import streamlit as st
import yaml
from pathlib import Path
import utils
from typing import Callable

with st.spinner():
    CONFIG_FILE = Path(Path(__file__).parent, "config.yaml")
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)

    evaluations_folder = Path(config["evaluations_folder"])
    evaluations = utils.load_evaluations(evaluations_folder)
    compiled_evaluations = utils.compile_evaluations(evaluations, config)

pages = utils.generate_pages(compiled_evaluations)
nav = st.navigation(
    pages,
    position="top"
)

nav.run()
