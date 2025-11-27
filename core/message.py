"""
ABET messages module
"""

import json
from typing import Dict, ClassVar
from dataclasses import dataclass, field


@dataclass
class AbstractMessage:
    content: str
    token_counts: Dict

@dataclass
class BaseMessage(AbstractMessage):
    content: str = None
    token_counts: Dict = field(default_factory=dict)
    message_type: str = "BaseMessage"

@dataclass
class ErrorMessage(BaseMessage):
    message_type: str = "ErrorMessage"

@dataclass
class UserMessage(BaseMessage):
    message_type: str = "UserMessage"

@dataclass
class AIMessage(BaseMessage):
    message_type: str = "AIMessage"

@dataclass
class ToolCallMessage(BaseMessage):
    message_type: str = "ToolCallMessage"

    tool_name: str = None
    tool_call_id: str = None
    tool_kwargs: Dict = None

@dataclass
class ToolResponseMessage(BaseMessage):
    message_type: str = "ToolResponseMessage"

    tool_call_id: str = None

@dataclass
class AnyMessage(
    ErrorMessage,
    UserMessage,
    AIMessage,
    ToolCallMessage,
    ToolResponseMessage
):
    pass
