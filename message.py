"""
ABET messages module
"""

import json
from typing import Callable


class AbstractMessage:
    pass

class BaseMessage(AbstractMessage):
    _message_type: str
    _content: str

    def __init__(self, content: str, message_type: str = None) -> None:
        self._content = content
        if message_type is None:
            message_type = "BaseMessage"
        self._message_type = message_type
    
    @property
    def content(self) -> str:
        return self._content
    
    @property
    def message_type(self) -> str:
        return self._message_type

    def __repr__(self) -> str:
        return json.dumps({
            "type": self.message_type,
            "content": self.content
        })

class ErrorMessage(BaseMessage):
    def __init__(self, content: str) -> None:
        super().__init__(
            content=content,
            message_type="ErrorMessage"
        )

class UserMessage(BaseMessage):
    def __init__(self, content: str) -> None:
        super().__init__(
            content=content,
            message_type="UserMessage"
        )

class AIMessage(BaseMessage):
    def __init__(self, content: str) -> None:
        super().__init__(
            content=content,
            message_type="AIMessage"
        )

class ToolCallMessage(BaseMessage):
    _tool_name: str
    _tool_kwargs: dict
    _tool_call_id: str

    def __init__(self, tool_name: str, tool_kwargs: dict, tool_call_id: str) -> None:
        self._tool_name = tool_name
        self._tool_kwargs = tool_kwargs
        self._tool_call_id = tool_call_id

        _ = json.dumps({
            "tool_name": tool_name,
            "tool_kwargs": tool_kwargs,
            "tool_call_id": tool_call_id
        })

        super().__init__(
            content=_,
            message_type="ToolCallMessage"
        )
    
    @property
    def tool_name(self) -> str:
        return self._tool_name
    
    @property
    def tool_kwargs(self) -> dict:
        return self._tool_kwargs.copy()

    @property
    def tool_call_id(self) -> str:
        return self._tool_call_id

class ToolResponseMessage(BaseMessage):
    _tool_call_id: str
    _tool_response: str

    def __init__(self, tool_call_id: str, tool_response: str) -> None:
        self._tool_call_id = tool_call_id
        self._tool_response = tool_response

        _ = json.dumps({
            "tool_call_id": tool_call_id,
            "tool_response": tool_response
        })

        super().__init__(
            content=_,
            message_type="ToolResponseMessage"
        )
    
    @property
    def tool_call_id(self) -> str:
        return self._tool_call_id
    
    @property
    def tool_response(self) -> str:
        return self._tool_response
