"""
LangGraphTranslator module.
"""

from .base import BaseTranslator
from core.message import (
    AbstractMessage as _AbstractMessage, 
    AIMessage as _AIMessage, 
    UserMessage as _UserMessage, 
    ToolCallMessage as _ToolCallMessage, 
    ToolResponseMessage as _ToolResponseMessage,
    ErrorMessage as _ErrorMessage
)
from core.agentoutput import AgentOutput
from langchain_core.messages import (
    BaseMessage, 
    SystemMessage, 
    AIMessage, 
    HumanMessage, 
    ToolCall, 
    ToolMessage
) 
from typing import  List


class LangGraphTranslator(BaseTranslator):
    def front_native_output(self, native_output: dict) -> AgentOutput:
        messages = native_output["messages"]
        
        _ = []
        for msg in messages:
            translated_messages = []
            if isinstance(msg, SystemMessage):
                continue
            elif isinstance(msg, AIMessage):
                translated_messages.append(_AIMessage(
                    content=msg.content
                ))

                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        translated_messages.append(_ToolCallMessage(
                            tool_name=tc["name"],
                            tool_kwargs=tc["args"],
                            tool_call_id=tc["id"]
                        ))
            elif isinstance(msg, HumanMessage):
                translated_messages.append(_UserMessage(
                    content=msg.content
                ))
            elif isinstance(msg, ToolMessage):
                translated_messages.append(_ToolResponseMessage(
                    tool_call_id=msg.tool_call_id,
                    tool_response=msg.content
                ))
            else:
                translated_messages.append( _ErrorMessage(
                    content="Invalid type of message encountered during translation from native messages."
                ))
            
            if translated_messages:
                _.extend(translated_messages)

                if isinstance(translated_messages[-1], _ErrorMessage):
                    break

        return AgentOutput(
            messages=_
        )
