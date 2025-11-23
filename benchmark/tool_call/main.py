"""
Tool Call Benchmark main module
"""

from pathlib import Path
import yaml
from translator import translators
from agentbuilder import agentbuilders


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

    agbr_config = config["agentbuilder_config"]
    agbr = agentbuilders[framework](
        config=agbr_config
    )
    agent = agbr.build()

    tltr_config = config["translator_config"]
    tltr = translators[framework](
        config=tltr_config
    )
    

    # TODO:
    # 1. Create a dataset
    # 2. Fetch it and input it to agent
    # 3. Translate agent's output to ABET Messages
    # 4. Write an evaluator function for this benchmark
    # 5. Properly format and save evaluation output
