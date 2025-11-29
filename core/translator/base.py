"""
Module for AbstractTranslator
"""

from core.agentoutput import AbstractAgentOutput
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class AbstractTranslator:
    def __init__(self, config: Dict) -> None:
        raise NotImplementedError()

    def _translate(self, native_output: Any) -> AbstractAgentOutput:
        raise NotImplementedError()
    
    def __call__(self, native_output: Any) -> AbstractAgentOutput:
        logging.info("Translating native output.")
        resp = self._translate(
            native_output=native_output
        )
        logging.info("Native output translated succesfully.")
        logging.debug(f"Translation generated.\nNative Output: {native_output}\nTranslated Output: {resp}")

        return resp

class BaseTranslator(AbstractTranslator):
    config: Dict

    def __init__(self, config: Dict) -> None:
        self.config = config
