"""
Tool Call Benchmark LangGraphAgentBuilder module
"""

from .base import AbstractAgentBuilder
from langchain.agents import create_agent
from langchain.tools import BaseTool
import yaml
from typing import Callable


class LangGraphAgentBuilder(AbstractAgentBuilder):
    def build(self, model: str, tools: List[BaseTool], system_prompt: str) -> Callable:
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt
        )

        def _(inp: str):
            resp = agent.invoke(
                input={
                    "messages": [
                        {
                            "role": "user",
                            "content": inp
                        }
                    ]
                },
                stream_mode="values"
            )

            return resp["content"]
