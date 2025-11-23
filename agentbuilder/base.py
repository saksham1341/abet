"""
Tool Call Benchmark AbstractAgentBuilder Module
"""

from typing import Callable


class AbstractAgentBuilder:
    def build(self, *args, **kwargs) -> Callable:
        raise NotImplementedError()
