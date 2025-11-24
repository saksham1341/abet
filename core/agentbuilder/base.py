"""
Tool Call Benchmark AbstractAgentBuilder Module
"""

from typing import Callable


class AbstractAgentBuilder:
    def __init__(self, config: dict) -> None:
        raise NotImplementedError()

    def _build(self) -> Callable:
        raise NotImplementedError()
    
    def __call__(self) -> Callable:
        return self._build()

class BaseAgentBuilder(AbstractAgentBuilder):
    config: dict

    def __init__(self, config: dict) -> None:
        self.config = config
