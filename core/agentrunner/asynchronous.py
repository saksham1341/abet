"""
Asynchronous Agent Runners
"""

from .base import BaseAgentRunner
import asyncio
import traceback
import logging

logger = logging.getLogger(__name__)

class AsyncConcurrentAgentRunner(BaseAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.max_tries_for_an_input = self.config.get("max_tries_for_an_input", 3)
        self.worker_count = self.config.get("worker_count", 1)

        self.iq = None 
        self.oq = None

    async def _worker(self, name: str) -> None:
        while True:
            item = await self.iq.get()
            
            key, inp, tries = item

            logger.info(f"INP[{key}] >> WORKER[{name}]")
            
            try:
                agent_out = await asyncio.to_thread(self.agent, inp)
                
                out = self.translator(agent_out)
                await self.oq.put((key, out))
                
            except Exception as e:
                logger.error(f"Error while running input with KEY[{key}]: {e}")
                logger.debug(f"Error Details:\nINP: {inp}\nERR: {traceback.format_exc()}")

                if tries < self.max_tries_for_an_input:
                    logger.info(f"KEY[{key}] returned to queue.")
                    await self.iq.put((key, inp, tries + 1))
                else:
                    logger.info(f"Maximum retries for KEY[{key}] raeched, dropped.")
            finally:
                self.iq.task_done()

                logger.info(f"WORKER[{name}] >> OUT[{key}]")

    async def _async_run(self) -> None:
        self.iq = asyncio.Queue()
        self.oq = asyncio.Queue()

        logger.info("Populating input queue.")
        keys = self.dataset.get_keys()
        for key in keys:
            self.iq.put_nowait((key, self.dataset.get_input(key), 0))

        # Create Workers
        logger.info(f"Launching {self.worker_count} workers.")
        workers = [
            asyncio.create_task(self._worker(f"AsyncConcurrentAgentRunner#{i}"))
            for i in range(self.worker_count)
        ]

        await self.iq.join()

        # Cancel workers
        for worker in workers:
            worker.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)

        logger.info("Draining output queue.")
        while not self.oq.empty():
            key, out = await self.oq.get()
            self.dataset.set_output(key, out)
            logger.debug(f"Set OUT[{out}] to KEY[{key}]")
        logger.info("Run completed.")

    def _run(self) -> None:
        return asyncio.run(self._async_run())


class AsyncSequentialAgentRunner(AsyncConcurrentAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Sequential is just concurrent with 1 worker
        self.worker_count = 1
