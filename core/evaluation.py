"""
Evaluation module for standardised evaluation results
"""

from core.dataset import AbstractDataset
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AbstractEvaluation:
    dataset: AbstractDataset

@dataclass
class BaseEvaluation(AbstractEvaluation):
    dataset: AbstractDataset = None

@dataclass
class DashboardEvaluation(BaseEvaluation):
    samples: List[Dict] = None
