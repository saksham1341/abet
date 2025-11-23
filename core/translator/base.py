"""
Module for AbstractTranslator
"""

from core.message import AbstractMessage
from typing import Any, Dict, List


class AbstractTranslator:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()

    def from_native_output(self, native_output: Any) -> List[AbstractMessage]:
        raise NotImplementedError()

class BaseTranslator:
    config: Dict

    def __init__(self, config: Dict) -> None:
        self.config = config
