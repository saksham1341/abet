"""
Asynchronous Agent Runners
"""

from .base import BaseAgentRunner
import asyncio
import traceback

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

            print(f"KEY[{key}] >> WORKER[{name}]")
            
            try:
                agent_out = await asyncio.to_thread(self.agent, (inp,))
                
                out = self.translator(agent_out)
                await self.oq.put((key, out))
                
            except Exception as e:
                if tries < self.max_tries_for_an_input:
                    await self.iq.put((key, inp, tries + 1))
            finally:
                self.iq.task_done()

                print(f"WORKER[{name}] >> OUT[{key}]")

    async def _async_run(self) -> None:
        self.iq = asyncio.Queue()
        self.oq = asyncio.Queue()

        keys = self.dataset.get_keys()
        for key in keys:
            self.iq.put_nowait((key, self.dataset.get_input(key), 0))

        # Create Workers
        workers = [
            asyncio.create_task(self._worker(f"AsyncRunner#{i}"))
            for i in range(self.worker_count)
        ]

        await self.iq.join()

        # Cancel workers
        for worker in workers:
            worker.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)

        while not self.oq.empty():
            key, out = await self.oq.get()
            self.dataset.set_output(key, out)

    def _run(self) -> None:
        return asyncio.run(self._async_run())


class AsyncSequentialAgentRunner(AsyncConcurrentAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Sequential is just concurrent with 1 worker
        self.worker_count = 1
