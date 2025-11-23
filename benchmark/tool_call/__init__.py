"""
Tool Call Benchmark main module
"""

from pathlib import Path
from typing import Dict
import yaml

CONFIG_PATH: Path = Path(Path(__file__).resolve().parent, "config.yaml")
DEFAULT_CONFIG: Dict = {}
with open(CONFIG_PATH, "r") as CONFIG_FILE:
    DEFAULT_CONFIG = yaml.safe_load(CONFIG_FILE)
