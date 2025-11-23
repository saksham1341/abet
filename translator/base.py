"""
Module for AbstractTranslator
"""

from message import AbstractMessage
from typing import Any, List


class AbstractTranslator:
    def from_framework(self, messages: List[Any]) -> List[AbstractMessage]:
        raise NotImplementedError()
