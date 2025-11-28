"""
AbstractEvaluator class.
"""

from core.dataset import AbstractDataset
from core.evaluation import AbstractEvaluation
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class AbstractEvaluator:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()

    def _evaluate(self, dataset: AbstractDataset) -> AbstractEvaluation:
        raise NotImplementedError()

    def __call__(self, dataset: AbstractDataset) -> AbstractEvaluation:
        logger.info("Evaluating dataset.")
        return self._evaluate(dataset)

class BaseEvaluator(AbstractEvaluator):
    def __init__(self, config: Dict) -> None:
        self.config = config
