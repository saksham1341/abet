"""
AbstractEvaluationSaver class
"""

from core.evaluation import AbstractEvaluation
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class AbstractEvaluationSaver:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()

    def _save_evaluation(self, evaluation: AbstractEvaluation) -> bool:
        raise NotImplementedError()
    
    def __call__(self, evaluation: AbstractEvaluation) -> bool:
        logger.info(f"Saving Evaluation.")
        return self._save_evaluation(
            evaluation=evaluation
        )

class BaseEvaluationSaver(AbstractEvaluationSaver):
    def __init__(self, config: Dict) -> None:
        self.config = config
