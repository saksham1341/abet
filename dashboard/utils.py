"""
Dashboard utils
"""

from typing import List, Dict
from os import listdir
import json
from dataclasses import dataclass
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st
from typing import Callable


@dataclass
class Evaluation:
    benchmark_name: str
    run_id: str
    results: Dict

def load_evaluations(directory: str) -> List[Evaluation]:
    evaluations = []

    directory = Path(directory)
    items = listdir(directory)
    for item in items:
        try:
            with open(Path(directory, item), "r") as f:
                _ = json.load(f)
                is_valid = True
                for key in ["benchmark_name", "run_id", "results"]:
                    if key not in _:
                        is_valid = False
                        break
                
                if not is_valid:
                    print(f"File [{item}] is invalid, skipping.")
                
                evaluations.append(Evaluation(
                    benchmark_name=_["benchmark_name"],
                    run_id=_["run_id"],
                    results=_["results"]
                ))
        except Exception as e:
            print(f"Error [{e}] loading file [{item}], skipping.")
    
    return evaluations

@dataclass
class CompiledEvaluation:
    benchmark_name: str
    config: Dict
    df: pd.DataFrame

    def get_description(self) -> str:
        return self.config.get("description", "")

    def get_metrics(self) -> List[str]:
        return list(self.df.columns)

    def get_metric_config(self, metric: str) -> Dict[str, Dict]:
        m_config = self.config.get("metrics", {}).get(metric, {})
        
        m_config["alternate_name"] = m_config.get("alternate_name", "")
        m_config["description"] = m_config.get("description", "")
        m_config["scoring_weight"] = m_config.get("scoring_weight", 1)

        return m_config

def compile_evaluations(evaluations: List[Evaluation], config: Dict) -> List[CompiledEvaluation]:
    benchmark_wise_results = {}
    for e in evaluations:
        if e.benchmark_name not in benchmark_wise_results:
            benchmark_wise_results[e.benchmark_name] = []
        
        data = {
            "run_id": e.run_id
        }
        data.update(e.results)
        benchmark_wise_results[e.benchmark_name].append(data)
    
    benchmark_wise_dfs = {
        k: pd.DataFrame(v)
        for k, v in benchmark_wise_results.items()
    }

    # make run_id as the index
    for k, v in benchmark_wise_dfs.items():
        benchmark_wise_dfs[k] = v.set_index("run_id")

    return [
        CompiledEvaluation(
            benchmark_name=k,
            df=v,
            config=config.get("benchmark_configs", {}).get(k, {})
        ) for k, v in benchmark_wise_dfs.items()
    ]

def score_single_compiled_evaluation(ce: CompiledEvaluation) -> Dict:    
    df = ce.df.copy()
    for col in ce.get_metrics():
        m_config = ce.get_metric_config(col)

        # get weight
        w = m_config["scoring_weight"]
        
        # Move the values to positive
        if df[col].min() < 0:
            df[col] = df[col] + abs(df[col].min()) + 1
        
        # replace NAs
        df[col] = df[col].fillna(0)
        
        # Scale from 0 to 1
        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

        # apply weight direction
        if w < 0:
            df[col] = 1 - df[col]

        # apply weight
        df[col] = df[col] * abs(w)
    
    # final scores
    scores = df.sum(axis=1).to_dict()

    return scores

def get_compiled_evaluation_leaderboard(ce: CompiledEvaluation) -> pd.DataFrame:
    # Sort
    scores = score_single_compiled_evaluation(ce)
    scores = {
        _: scores[_]
        for _ in sorted(scores, key=scores.get, reverse=True)
    }

    res = []
    rank = 1
    for run_id, score in scores.items():
        res.append({
            "rank": rank,
            "run_id": run_id,
            "score": score
        })

        rank += 1
    
    return pd.DataFrame(res).set_index("rank")

def display_leaderboard(data, name_col="name", score_col="score"):
    # 1. Prepare Data
    df = pd.DataFrame(data)
    
    # Sort by score descending
    df = df.sort_values(by=score_col, ascending=False).reset_index(drop=True)
    
    # Get the maximum score for the progress bar calculation
    max_score = df[score_col].max()

    # 2. Header
    st.subheader("Leaderboard")
    
    # 3. Iterate and Display
    for index, row in df.iterrows():
        rank = index + 1
        name = row[name_col]
        score = row[score_col]
        
        # Determine Medal/Rank Emoji
        if rank == 1:
            emoji = "🥇"
            color = "gold" # Used for visual emphasis logic if needed
        elif rank == 2:
            emoji = "🥈"
            color = "silver"
        elif rank == 3:
            emoji = "🥉"
            color = "#cd7f32" # Bronze color
        else:
            emoji = f"#{rank}"
            color = "gray"

        # Create a container for each row
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 4, 1])
            
            # Column 1: Rank/Emoji
            with c1:
                st.markdown(f"### {emoji}")
            
            # Column 2: Name
            with c2:
                st.markdown(f"**{name}**")
            
            # Column 3: Numeric Score
            with c3:
                st.metric(label="Score", value=score)

def render_compiled_evaluation(ce: CompiledEvaluation):
    st.header(ce.benchmark_name)
    st.markdown(ce.get_description())
    
    with st.spinner():
        leaderboard_df = get_compiled_evaluation_leaderboard(ce)
    
    # st.subheader("Leaderboards")
    # st.dataframe(leaderboard_df)

    display_leaderboard(leaderboard_df, "run_id", "score")

    st.divider()

    for col in ce.get_metrics():
        m_config = ce.get_metric_config(col)

        altername_name = m_config["alternate_name"]
        sh = f"`{col}`" + (f' / {altername_name}' if altername_name else '')
        st.subheader(sh)
        st.markdown(m_config["description"])
        st.bar_chart(ce.df[col])
        st.divider()
    
    st.markdown("Made with <3 by [saksham1341](https://github.com/saksham1341/abet)")

def compiled_evaluation_page_generator(ce: CompiledEvaluation) -> Callable:
    def _():
        return render_compiled_evaluation(ce)

    return _

def render_home_page():
    """
    Renders the A.B.E.T. Project Home Page.
    Contains project description, structure, and usage info from README.md.
    """
    st.set_page_config(
        page_title="A.B.E.T. | Home",
        page_icon="🏠",
        layout="wide"
    )

    # --- Header Section ---
    st.title("🤖 A.B.E.T.")
    st.subheader("Agent Benchmark and Evaluation Toolkit")
    
    st.info("ℹ️ **Note:** This project is currently a work in progress.")

    st.markdown("""
    **A.B.E.T.** is a comprehensive package designed to provide tools to 
    **quickly and easily implement agent benchmarks and evaluate them**.
    """)

    st.divider()

    # --- Project Structure Section ---
    st.header("📂 Project Structure")
    st.markdown("The toolkit is organized into core components, benchmarks, and visualization tools.")
    
    st.code("""
|__ benchmark/                          # Benchmarks live here
|   |__ utils.py                        # The main run() function and other benchmarking utilities
|   |__ init/                           # benchmark.init command implementation
|   |__ tool_call/                      # Example: Tool calling benchmark
|__ core/                               # Core components
|   |__ agentoutput.py                  # Defines AbstractAgentOutput
|   |__ dataset.py                      # Defines AbstractDataset
|   |__ evaluation.py                   # Defines AbstractEvaluation
|   |__ message.py                      # Defines multiple message types
|   |__ agentbuilder/                   # AgentBuilder implementations
|   |__ agentrunner/                    # AgentRunner implementations
|   |__ datasetloader/                  # AbstractDatasetLoader
|   |__ evaluationsaver/                # AbstractEvaluationSaver
|   |__ translator/                     # AbstractTranslator
|__ dashboard/                          # Streamlit powered Dashboard
    """, language="text")

    st.divider()

    # --- Program Flow Section ---
    st.header("wm Program Flow")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        The system consists of several components that work together to evaluate an agent:

        1. **AgentBuilder**: Produces an Agent instance.
        2. **DatasetLoader**: Loads and produces a Dataset.
        3. **Translator**: Translates Agent's outputs to standardised Messages.
        4. **AgentRunner**: Processes the dataset, populating it with translated agent outputs.
        5. **Evaluator**: Generates an Evaluation object from the updated dataset.
        6. **EvaluationSaver**: Stores or exports the final evaluation results.
        """)
    
    with col2:
        # Placeholder for the flow image. 
        # In a real deployment, you would ensure 'flow.png' is accessible or hosted.
        st.caption("Flow Visualization")
        st.image("flow.png", caption="Program Flow Diagram", width='stretch')
        # Fallback text if image is missing in this context
        # st.warning("Ensure `flow.png` is in the running directory to view the diagram.")

    st.divider()

    # --- Usage Section ---
    st.header("🚀 How to Run")

    st.subheader("1. Setup")
    st.markdown("Clone the repository and install dependencies:")
    st.code("""
git clone https://github.com/saksham1341/abet
cd abet
python -m pip install -r requirements.txt
    """, language="bash")

    st.subheader("2. Running a Benchmark")
    st.markdown("Execute a benchmark as a python module:")
    st.code("python -m benchmark.tool_call", language="bash")
    
    st.subheader("3. Dashboard")
    st.markdown("To view the results (like the one you are seeing now), run:")
    st.code("streamlit run dashboard/app.py", language="bash")

def generate_pages(ces: List[CompiledEvaluation]) -> List[st.Page]:    
    return [
        st.Page(
            page=render_home_page,
            title="A.B.E.T.",
            url_path="home",
            default=True
        )
    ] + [
        st.Page(
            page=compiled_evaluation_page_generator(ce),
            title=ce.benchmark_name,
            url_path=ce.benchmark_name
        ) for ce in ces
    ]
