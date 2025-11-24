"""
AbstractDatasetLoader class
"""

from core.dataset import AbstractDataset
from typing import Dict


class AbstractDatasetLoader:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()
    
    def _load_dataset(self, **kwargs) -> AbstractDataset:
        raise NotImplementedError()
    
    def __call__(self) -> AbstractDataset:
        return self._load_dataset()
