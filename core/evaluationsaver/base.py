"""
AbstractEvaluationSaver class
"""

from core.evaluation import AbstractEvaluation
from typing import Dict


class AbstractEvaluationSaver:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()

    def _save_evaluation(self, evaluation: AbstractEvaluation) -> bool:
        raise NotImplementedError()
    
    def __call__(self, evaluation: AbstractEvaluation) -> bool:
        return self._save_evaluation(
            evaluation=evaluation
        )
