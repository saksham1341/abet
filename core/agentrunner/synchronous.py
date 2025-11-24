"""
Synchronous Agent Runners
"""

from .base import BaseAgentRunner
from core.translator import AbstractTranslator
import threading
import multiprocessing
import queue
from typing import List, Any, Callable

class SyncSequentialAgentRunner(BaseAgentRunner):
    def _run(self) -> None:
        keys = self.dataset.get_keys()
        for key in keys:
            inp = self.dataset.get_input(key)
            native_out = self.agent(inp)
            out = self.translator(native_out)

            self.dataset.set_output(key, out)

def _split_keys(keys: List[Any], n: int) -> List[List[Any]]:
    K = len(keys)
    STEP = K // n
    
    _ = []
    for i in range(0, K, STEP):
        _.append(
            keys[i: i + STEP]
        )
    
    return _

class SyncThreadPoolAgentRunner(BaseAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.thread_count = self.config["thread_count"]
        self.q = queue.Queue()

        keys = self.dataset.get_keys()
        for key in keys:
            self.q.put(key)

    def _target(self, name: str) -> None:
        while not self.q.empty():
            try:
                key = self.q.get()
            except queue.Empty:
                break

            inp = self.dataset.get_input(key)
            native_out = self.agent(inp)
            out = self.translator(native_out)

            self.dataset.set_output(key, out)

    def _run(self) -> None:
        threads = [
            threading.Thread(
                target=self._target,
                name=f"SyncThreadPoolAgentRunner#{i}",
                kwargs={
                    "name": f"SyncThreadPoolAgentRunner#{i}"
                }
            ) for i in range(self.thread_count)
        ]

        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()

class SyncProcessPoolAgentRunner(BaseAgentRunner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.process_count = self.config["process_count"]
        self.iq = multiprocessing.Queue()
        self.oq = multiprocessing.Queue()

        keys = self.dataset.get_keys()
        for key in keys:
            self.iq.put({
                "key": key,
                "inp": self.dataset.get_input(key),
            })

    def _target(self, name: str, agent: Callable, translator: AbstractTranslator, iq: multiprocessing.Queue, oq: multiprocessing.Queue) -> None:
        while not iq.empty():
            try:
                msg = iq.get()
            except multiprocessing.queues.Empty:
                break

            key, inp = msg["key"], msg["inp"]
            native_out = agent(inp)
            out = translator(native_out)

            oq.put({
                "key": key,
                "out": out
            })

    def _run(self) -> None:
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
            ) for i in range(self.process_count)
        ]

        for process in processes:
            process.start()
        
        for process in processes:
            process.join()
        
        while not self.oq.empty():
            msg = self.oq.get()

            key, out = msg["key"], msg["out"]

            self.dataset.set_output(key, out)
