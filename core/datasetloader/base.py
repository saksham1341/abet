"""
AbstractDatasetLoader class
"""

from core.dataset import AbstractDataset
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class AbstractDatasetLoader:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()
    
    def _load_dataset(self, **kwargs) -> AbstractDataset:
        raise NotImplementedError()
    
    def __call__(self) -> AbstractDataset:
        logger.info("Loading dataset.")
        return self._load_dataset()

class BaseDatasetLoader(AbstractDatasetLoader):
    def __init__(self, config: Dict) -> None:
        self.config = config
