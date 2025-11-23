"""
AgentOutput module for standardised agent outputs.
"""

from core.message import AbstractMessage
from dataclasses import dataclass
from typing import List

@dataclass
class AgentOutput:
    messages: List[AbstractMessage] = None
