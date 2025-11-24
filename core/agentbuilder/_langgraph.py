"""
Tool Call Benchmark LangGraphAgentBuilder module
"""

from .base import BaseAgentBuilder
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool, tool
from typing import List, Callable
import importlib


class LangGraphAgentBuilder(BaseAgentBuilder):
    tools: List[BaseTool]
    model: str
    system_prompt: str
    
    def __init__(self, config: dict) -> None:
        super().__init__(config)

        _ = config["tools"].split(".")
        tools_module_name = ".".join(_[:-1])
        tools_object_name = _[-1]
        tools = getattr(importlib.import_module(tools_module_name), tools_object_name)
        self.tools = [tool(_) for _ in tools]

        self.model = config["model"]
        
        self.system_prompt = open(config["system_prompt_path"], "r").read()

    def _build(self) -> Callable:
        # Need to just use create_agent with self.model
        # But it is breaking for now since I don't have a GCP project for gemini
        # so this is a temporary solution exclusively supporing a gemini model

        x = ChatGoogleGenerativeAI(model=self.model)
        agent = create_agent(
            model=x,
            tools=self.tools,
            system_prompt=self.system_prompt
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

            return resp
        
        return _
