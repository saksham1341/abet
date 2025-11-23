from pathlib import Path
from typing import Dict
import yaml

this_root: Path = Path(__file__).resolve().parent

DEFAULT_CONFIG_PATH: Path = Path(this_root, "config.yaml")
DEFAULT_CONFIG: Dict = {}
with open(DEFAULT_CONFIG_PATH) as f:
    DEFAULT_CONFIG = yaml.safe_load(f)
