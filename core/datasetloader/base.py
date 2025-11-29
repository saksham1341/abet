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
        resp = self._load_dataset()
        
        keys = resp.get_keys()
        samples = []
        for key in keys[:10]:
            samples.append({
                "key": key,
                "inp": resp.get_input(key),
                "tgt": resp.get_target(key)
            })
        logger.debug(f"Dataset loaded with {len(keys)} keys. Sample: {samples}")

        return resp

class BaseDatasetLoader(AbstractDatasetLoader):
    def __init__(self, config: Dict) -> None:
        self.config = config
