"""
Module to initialize a new benchmark
"""

from sys import argv
from shutil import copyfile
from pathlib import Path

this_root = Path(__file__).resolve().parent
benchmark_root = this_root.parent

# Create target directory
target_name = argv[1]
target_root = Path(benchmark_root, target_name)
target_root.mkdir(exist_ok=False)

# Create target config file
placeholder_config = Path(this_root, "placeholder_config.yaml")
target_config = Path(target_root, "config.yaml")
copyfile(placeholder_config, target_config)

# Create target __init__.py
placeholder_init = Path(this_root, "placeholder_init.py")
target_init = Path(target_root, "__init__.py")
copyfile(placeholder_init, target_init)

# Create target __main__.py
placeholder_main = Path(this_root, "placeholder_main.py")
target_main = Path(target_root, "__main__.py")
copyfile(placeholder_main, target_main)
