"""
Tool Call Benchmark LangGraphAgentBuilder module
"""

from .base import BaseAgentBuilder
from langchain.agents import create_agent
from langchain.tools import BaseTool, tool
from typing import List, Callable, Union, Any
import importlib
import logging

logger = logging.getLogger(__name__)


class LangGraphAgentBuilder(BaseAgentBuilder):
    tools: List[BaseTool]
    model: Union[str, Any]
    system_prompt: str
    
    def __init__(self, config: dict) -> None:
        super().__init__(config)

        if config.get("tools", None):
            _ = config["tools"].split(".")
            tools_module_name = ".".join(_[:-1])
            tools_object_name = _[-1]
            tools = getattr(importlib.import_module(tools_module_name), tools_object_name)
            self.tools = [tool(_) for _ in tools]
        else:
            self.tools = []

        self.model = config["model_name"]
        if config.get("model_class", None):
            _ = config["model_class"].split(".")
            model_module_name = ".".join(_[:-1])
            model_class_name = _[-1]
            model_class = getattr(importlib.import_module(model_module_name), model_class_name)

            model_class_kwargs = config.get("model_class_kwargs", dict())
            self.model = model_class(
                model=self.model,
                **model_class_kwargs
            )
        
        self.system_prompt = open(config["system_prompt_path"], "r").read()

    def _build(self) -> Callable:
        kwargs = {
            "model": self.model,
            "tools": self.tools,
            "system_prompt": self.system_prompt
        }
    
        logger.debug(f"Calling langgraph.create_agent with args: {kwargs}")
        
        agent = create_agent(**kwargs)

        def _(inp: str):
            logger.debug(f"Sending INP[{inp}] to agent.")
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

            logger.debug(f"Agentic call finished.\nINP: {inp}\nOUT: {resp}")

            return resp
        
        return _
