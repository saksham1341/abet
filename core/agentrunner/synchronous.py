"""
Synchronous Agent Runners
"""

from .base import BaseAgentRunner
from core.translator import AbstractTranslator
import threading
import multiprocessing
import queue
from typing import List, Any, Callable
from time import sleep
import logging

logger = logging.getLogger(__name__)

class SyncSequentialAgentRunner(BaseAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        self.max_tries_for_an_input = self.config.get("max_tries_for_an_input", 3)
        self.q = None

    def _run(self) -> None:
        self.q = queue.Queue()

        keys = self.dataset.get_keys()
        for key in keys:
            self.q.put((key, 0))
    
        while not self.q.empty():
            key, tries = self.q.get()

            logger.info(f"KEY[{key}] >> WORKER[0]")

            inp = self.dataset.get_input(key)
            try:
                agent_out = self.agent(inp)
            except Exception as e:
                logger.error(f"Error running input KEY[{key}]: {e}")
                logger.debug(f"Error Details:\nINP: {inp}\nERR: {traceback.format_exc()}")

                if tries < self.max_tries_for_an_input:
                    logger.info(f"KEY[{key}] returned to queue.")
                    self.q.put((key, tries + 1))
                else:
                    logger.info(f"Maximum retries for KEY[{key}] raeched, dropped.")

                continue
            
            out = self.translator(agent_out)

            logger.info(f"WORKER[0] >> OUT[{key}]")

            self.dataset.set_output(key, out)
            logger.debug(f"Set OUT[{out}] to KEY[{key}]")

class SyncThreadPoolAgentRunner(BaseAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.worker_count = self.config.get("worker_count", 1)
        self.max_tries_for_an_input = self.config.get("max_tries_for_an_input", 3)
        self.iq = queue.Queue()
        self.oq = queue.Queue()

    def _target(self, name: str) -> None:
        while True:
            try:
                item = self.iq.get()
            except queue.Empty:
                break

            key, inp, tries = item

            logger.info(f"INP[{key}] >> WORKER[{name}]")

            inp = self.dataset.get_input(key)
            try:
                native_out = self.agent(inp)
            except Exception as e:
                logger.error(f"Error while running KEY[{key}] through the agent: {e}")
                logger.debug(f"Error Details:\nINP: {inp}\nERR: {traceback.format_exc()}")

                if tries < self.max_tries_for_an_input:
                    logger.info(f"KEY[{key}] returned to queue.")
                    self.iq.put((key, tries + 1))
                else:
                    logger.info(f"Maximum retries for KEY[{key}] raeched, dropped.")
                
                continue

            out = self.translator(native_out)

            self.oq.put((key, out))

            logger.info(f"WORKER[{name}] >> KEY[{key}]")

    def _run(self) -> None:
        logger.info(f"Populating input queue.")
        keys = self.dataset.get_keys()
        for key in keys:
            self.iq.put((key, self.dataset.get_input(key), 0))
        
        logger.info(f"Launching {self.worker_count} workers.")
        threads = [
            threading.Thread(
                target=self._target,
                name=f"SyncThreadPoolAgentRunner#{i}",
                kwargs={
                    "name": f"SyncThreadPoolAgentRunner#{i}"
                }
            ) for i in range(self.worker_count)
        ]

        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        logger.info(f"Draining output queue.")
        while not self.oq.empty():
            item = self.oq.get()
            key, out = item

            self.dataset.set_output(key, out)
        
        logger.info(f"Run completed.")

class SyncProcessPoolAgentRunner(BaseAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.worker_count = self.config.get("worker_count", 1)
        self.max_tries_for_an_input = self.config.get("max_tries_for_an_input", 3)
        self.iq = multiprocessing.Queue()
        self.oq = multiprocessing.Queue()

    def _target(self, name: str, agent: Callable, translator: AbstractTranslator, iq: multiprocessing.Queue, oq: multiprocessing.Queue) -> None:
        while not iq.empty():
            try:
                msg = iq.get()
            except multiprocessing.queues.Empty:
                break

            key, inp, tries = msg["key"], msg["inp"], msg["tries"]
            
            logger.info(f"INP[{key}] >> WORKER[{name}]")

            try:
                native_out = agent(inp)
            except Exception:
                if tries < self.max_tries_for_an_input:
                    iq.put({
                        "key": key,
                        "inp": inp,
                        "tries": tries + 1
                    })
                
                continue
            
            out = translator(native_out)

            oq.put({
                "key": key,
                "out": out
            })

            logging.info(f"WORKER[{name}] >> OUT[{key}]")

    def _run(self) -> None:
        logger.info("Populating input queue.")
        keys = self.dataset.get_keys()
        for key in keys:
            self.iq.put({
                "key": key,
                "inp": self.dataset.get_input(key),
                "tries": 0
            })
        
        logger.info(f"Launching {self.worker_count} workers.")
        processes = [
            multiprocessing.Process(
                target=self._target,
                name=f"SyncProcessPoolAgentRunner#{i}",
                kwargs={
                    "name": f"SyncProcessPoolAgentRunner#{i}",
                    "agent": self.agent,
                    "translator": self.translator,
                    "iq": self.iq,
                    "oq": self.oq
                }
            ) for i in range(self.worker_count)
        ]

        for process in processes:
            process.start()
        
        for process in processes:
            process.join()
        
        logger.info("Draining output queue.")
        while not self.oq.empty():
            msg = self.oq.get()

            key, out = msg["key"], msg["out"]

            self.dataset.set_output(key, out)
        
        logger.info("Run completed.")
