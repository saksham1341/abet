"""
General benchmar utilities
"""

from core.agentbuilder import AbstractAgentBuilder
from core.translator import AbstractTranslator
from typing import TypeVar, Type
import importlib

AgentBuilder_T = TypeVar("AgentBuilder_T", bound=AbstractAgentBuilder)
Translator_T = TypeVar("Translator_T", bound=AbstractTranslator)

def get_agentbuilder_class(config: dict) -> Type[AgentBuilder_T]:
    _ = config["agentbuilder"].split(".")
    module_name = ".".join(_[:-1])
    class_name = _[-1]

    return getattr(importlib.import_module(module_name), class_name)

def get_translator_class(config: dict) -> Type[Translator_T]:
    _ = config["translator"].split(".")
    module_name = ".".join(_[:-1])
    class_name = _[-1]

    return getattr(importlib.import_module(module_name), class_name)
