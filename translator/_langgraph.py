"""
LangGraphTranslator module.
"""

from .base import AbstractTranslator
from message import (
    AbstractMessage as _AbstractMessage, 
    AIMessage as _AIMessage, 
    UserMessage as _UserMessage, 
    ToolCallMessage as _ToolCallMessage, 
    ToolResponseMessage as _ToolResponseMessage,
    ErrorMessage as _ErrorMessage
)
from langchain_core.messages import (
    BaseMessage, 
    AIMessage, 
    HumanMessage,
    ToolCall,
    ToolMessage
) 
from typing import  List


class LangGraphTranslator(AbstractTranslator):
    def from_framework(self, messages: List[BaseMessage]) -> List[_AbstractMessage]:
        _ = []
        for msg in messages:
            translated_message = None
            if isinstance(msg, AIMessage):
                translated_message = _AIMessage(
                    content=msg.content
                )
            elif isinstance(msg, HumanMessage):
                translated_message = _UserMessage(
                    content=msg.content
                )
            elif isinstance(msg, ToolCall):
                translated_message = _ToolCallMessage(
                    tool_name=msg.name,
                    tool_kwargs=msg.args,
                    tool_call_id=msg.id
                )
            elif isinstance(msg, ToolMessage):
                translated_message = _ToolResponseMessage(
                    tool_call_id=msg.tool_call_id,
                    tool_response=msg.content
                )
            else:
                translated_message = _ErrorMessage(
                    content="Invalid type of message encountered during translation from native messages."
                )
            
            if translated_message is not None:
                _.append(translated_message)

                if isinstance(translated_message, _ErrorMessage):
                    break

        return _
