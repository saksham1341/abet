"""
AbstractEvaluator class.
"""

from core.dataset import AbstractDataset
from core.evaluation import AbstractEvaluation
from typing import Dict


class AbstractEvaluator:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()

    def _evaluate(self, dataset: AbstractDataset) -> AbstractEvaluation:
        raise NotImplementedError()

    def __call__(self, dataset: AbstractDataset) -> AbstractEvaluation:
        return self._evaluate(dataset)
