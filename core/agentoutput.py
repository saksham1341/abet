"""
AgentOutput module for standardised agent outputs.
"""

from core.message import AbstractMessage
from dataclasses import dataclass
from typing import List

@dataclass
class AbstractAgentOutput:
    pass

@dataclass
class AgentOutput(AbstractAgentOutput):
    messages: List[AbstractMessage] = None
