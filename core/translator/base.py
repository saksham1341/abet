"""
Module for AbstractTranslator
"""

from core.message import AbstractMessage
from typing import Any, List


class AbstractTranslator:
    def __init__(self, config: dict) -> None:
        raise NotImplementedError()

    def front_native_output(self, native_output: Any) -> List[AbstractMessage]:
        raise NotImplementedError()

class BaseTranslator:
    config: dict

    def __init__(self, config: dict) -> None:
        self.config = config
