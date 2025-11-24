"""
AbstractAgentRunner class for standardized agent runner interfaces.
"""

from core.translator import AbstractTranslator
from core.dataset import AbstractDataset
from typing import Callable, Dict


class AbstractAgentRunner:
    def __init__(
        self,
        agent: Callable,
        translator: AbstractTranslator,
        dataset: AbstractDataset,
        config: Dict
    ) -> None:
        raise NotImplementedError()

    def _run(self) -> None:
        raise NotImplementedError()
    
    def __call__(self) -> None:
        self._run()

class BaseAgentRunner(AbstractAgentRunner):
    agent: Callable
    translator: AbstractTranslator
    dataset = AbstractDataset
    config: Dict

    def __init__(
        self,
        agent: Callable,
        translator: AbstractTranslator,
        dataset: AbstractDataset,
        config: Dict
    ) -> None:
        self.agent = agent
        self.translator = translator
        self.dataset = dataset
        self.config = config
