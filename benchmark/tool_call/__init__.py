"""
Tool Call Benchmark main module
"""

from pathlib import Path
import yaml
from core.message import UserMessage, ToolCallMessage, ToolResponseMessage, AIMessage
from benchmark.utils import get_agentbuilder_class, get_translator_class

CONFIG_PATH: Path = Path(Path(__file__).resolve().parent, "config.yaml")
DEFAULT_CONFIG: dict = {}
with open(CONFIG_PATH, "r") as CONFIG_FILE:
    DEFAULT_CONFIG = yaml.safe_load(CONFIG_FILE)

def run(custom_config: dict = None) -> None:
    global DEFAULT_CONFIG

    if custom_config is None:
        custom_config = {}

    config = DEFAULT_CONFIG.copy()
    config.update(config)

    framework = config["framework"]

    # AgentBuilder
    agbr_class = get_agentbuilder_class(config)
    agbr_config = config["agentbuilder_config"]
    agbr = agbr_class(
        config=agbr_config
    )
    agent = agbr.build()

    # Translator
    tltr_class = get_translator_class(config)
    tltr_config = config["translator_config"]
    tltr = tltr_class(
        config=tltr_config
    )
    
    dataset = [
        {
            "idx": 0,
            "input": "Value of 2 + 2?",
            "optmial_message_sequence": [
                UserMessage("Value of 2 + 2?"),
                ToolCallMessage("add", {"a": 2, "b": 2}, "0"),
                ToolResponseMessage("0", "4"),
                AIMessage("4")
            ]
        }
    ]

    out = agent(dataset[0]["input"])
    print(out)
    print(tltr.front_native_output(out))

    # TODO:
    # 1. Create a dataset
    # 2. Fetch it and input it to agent
    # 3. Translate agent's output to ABET Messages
    # 4. Write an evaluator function for this benchmark
    # 5. Properly format and save evaluation output
