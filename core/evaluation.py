"""
Evaluation module for standardised evaluation results
"""

from core.dataset import AbstractDataset
from dataclasses import dataclass


@dataclass
class AbstractEvaluation:
    dataset: AbstractDataset

@dataclass
class BaseEvaluation(AbstractEvaluation):
    dataset: AbstractDataset = None
