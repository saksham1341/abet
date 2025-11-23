"""
Tool Call Benchmark AbstractAgentBuilder Module
"""

from typing import Callable


class AbstractAgentBuilder:
    def __init__(self, config: dict) -> None:
        raise NotImplementedError()

    def build(self) -> Callable:
        raise NotImplementedError()

class BaseAgentBuilder(AbstractAgentBuilder):
    config: dict

    def __init__(self, config: dict) -> None:
        self.config = config
