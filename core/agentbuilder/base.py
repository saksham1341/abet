"""
AbstractAgentBuilder Module
"""

from typing import Callable
import logging

logger = logging.getLogger(__name__)

class AbstractAgentBuilder:
    def __init__(self, config: dict) -> None:
        raise NotImplementedError()

    def _build(self) -> Callable:
        raise NotImplementedError()
    
    def __call__(self) -> Callable:
        logger.info(f"Running AgentBuilder[{self.__class__.__name__}]")
        return self._build()

class BaseAgentBuilder(AbstractAgentBuilder):
    config: dict

    def __init__(self, config: dict) -> None:
        self.config = config
