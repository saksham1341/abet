import streamlit as st
import yaml
from pathlib import Path
from dashboard import utils
from typing import Callable

def main():
    with st.spinner():
        st.set_page_config(
            menu_items={
                'Get Help': 'mailto:saksham1341@gmail.com',
                'Report a bug': 'https://github.com/saksham1341/abet/issues',
                'About': """
        A.B.E.T. is a simple highly modular and customizable agent benchmark and evaluation toolkit.  
        Source code hosted [here](https://github.com/saksham1341/abet)
        """
            }
        )

        CONFIG_FILE = Path(Path(__file__).parent, "config.yaml")
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)

        evaluations_folder = Path(config["evaluations_folder"])
        evaluations = utils.load_evaluations(evaluations_folder)
        compiled_evaluations = utils.compile_evaluations(evaluations, config)

        pages = utils.generate_pages(compiled_evaluations)
        nav = st.navigation(
            pages,
            position="top",
        )

    nav.run()
