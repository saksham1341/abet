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
    SystemMessage, 
    AIMessage, 
    HumanMessage, 
    ToolCall, 
    ToolMessage
) 
from typing import Dict, List


class LangGraphTranslator(BaseTranslator):
    def from_native_output(self, native_output: Dict) -> AgentOutput:
        messages = native_output["messages"]
        
        translated_messages = []
        for msg in messages:
            new_translated_messages = []
            if isinstance(msg, SystemMessage):
                continue
            elif isinstance(msg, AIMessage):
                new_translated_messages.append(_AIMessage(
                    content=msg.content
                ))

                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        new_translated_messages.append(_ToolCallMessage(
                            tool_name=tc["name"],
                            tool_kwargs=tc["args"],
                            tool_call_id=tc["id"]
                        ))
            elif isinstance(msg, HumanMessage):
                new_translated_messages.append(_UserMessage(
                    content=msg.content
                ))
            elif isinstance(msg, ToolMessage):
                new_translated_messages.append(_ToolResponseMessage(
                    tool_call_id=msg.tool_call_id,
                    content=msg.content
                ))
            else:
                new_translated_messages.append( _ErrorMessage(
                    content="Invalid type of message encountered during translation from native messages."
                ))
            
            if new_translated_messages:
                translated_messages.extend(new_translated_messages)

                if isinstance(translated_messages[-1], _ErrorMessage):
                    break

        return AgentOutput(
            messages=translated_messages
        )
