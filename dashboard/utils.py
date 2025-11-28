"""
Dashboard utils
"""

from typing import List, Dict, Callable
from os import listdir
import json
from dataclasses import dataclass
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st


@dataclass
class Evaluation:
    benchmark_name: str
    run_id: str
    results: Dict
    samples: List

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
                    results=_["results"],
                    samples=_["samples"]
                ))
        except Exception as e:
            print(f"Error [{e}] loading file [{item}], skipping.")
    
    return evaluations

@dataclass
class CompiledEvaluation:
    benchmark_name: str
    config: Dict
    df: pd.DataFrame
    samples: Dict

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
    benchmark_wise_samples = {}
    for e in evaluations:
        if e.benchmark_name not in benchmark_wise_results:
            benchmark_wise_results[e.benchmark_name] = []
        
        if e.benchmark_name not in benchmark_wise_samples:
            benchmark_wise_samples[e.benchmark_name] = {}
        
        data = {
            "run_id": e.run_id
        }
        data.update(e.results)
        benchmark_wise_results[e.benchmark_name].append(data)

        benchmark_wise_samples[e.benchmark_name].update({
            e.run_id: e.samples
        })
    
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
            samples=benchmark_wise_samples.get(k, {}),
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
    st.header("Leaderboard")
    
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
        with st.container(border=True, vertical_alignment="center"):
            c1, c2, c3 = st.columns([1, 10, 1])
            
            # Column 1: Rank/Emoji
            with c1:
                st.markdown(f"{emoji}")
            
            # Column 2: Name
            with c2:
                st.markdown(f"{name}")
            
            # Column 3: Numeric Score
            with c3:
                st.markdown(f"{score}")

def render_compiled_evaluation(ce: CompiledEvaluation):
    st.set_page_config(
        page_title=f"{ce.benchmark_name} | A.B.E.T.",
        layout="wide"
    )

    st.title(ce.benchmark_name)
    st.markdown(ce.get_description())
    
    with st.spinner():
        leaderboard_df = get_compiled_evaluation_leaderboard(ce)

    st.divider()

    display_leaderboard(leaderboard_df, "run_id", "score")

    st.divider()

    st.header("Evaluation Details")

    def _render_metric_in_container(m, col):
        with col:
            m_config = ce.get_metric_config(m)

            altername_name = m_config["alternate_name"]
            sh = f"`{m}`" + (f' / {altername_name}' if altername_name else '')
            st.subheader(sh)
            st.markdown(m_config["description"])
            st.bar_chart(ce.df[m], x_label="Run", y_label="Metric Value", horizontal=True)
    
    metrics = ce.get_metrics()
    for idx in range(0, len(metrics), 2):
        if idx < len(metrics) - 1:
            _ = zip(metrics[idx: idx + 2], st.columns([1, 1], border=True))
            for m, col in _:
                _render_metric_in_container(m, col)
        else:
            m = metrics[idx]
            col = st.container(border=True)
            _render_metric_in_container(m, col)
    
    st.divider()
    st.subheader("Samples")
    container_height = 300 if ce.samples else "content"
    with st.container(border=True, height=container_height):
        if ce.samples:
            st.write(ce.samples)
        else:
            st.write("No samples generated.")

    st.divider()
    st.markdown("Made with <3 by [saksham1341](https://github.com/saksham1341/abet)")

def compiled_evaluation_page_generator(ce: CompiledEvaluation) -> Callable:
    def _():
        return render_compiled_evaluation(ce)

    return _

def render_home_page():
    st.set_page_config(
        page_title="Home | A.B.E.T.",
        layout="wide"
    )

    # --- Header Section ---
    st.title("A.B.E.T.")
    st.subheader("Agent Benchmark and Evaluation Toolkit")
    
    st.info("**Note:** This project is currently a work in progress.")

    st.markdown("""
    A.B.E.T. (Agent Benchmark & Evaluation Toolkit) is a lightweight, modular framework for **building, running, and analyzing LLM agent benchmarks**. It provides a complete pipeline—from dataset loading to agent execution, evaluation, and visualization—making it easy to design custom benchmarks or plug in prebuilt ones.

The goal is to offer a flexible, extensible environment for evaluating **agentic behavior**, **tool-call reliability**, **self-repair**, and other emerging LLM capabilities.
    """)

    st.divider()

    # --- Project Structure Section ---
    st.header("Project Structure")
    st.markdown("The toolkit is organized into core components, benchmarks, and visualization tools.")
    
    st.code("""
|__ benchmark/                          # Benchmarks live here
|   |__ utils.py                        # run() + shared benchmark utilities
|   |__ init/                           # Template generator: benchmark.init
|   |   |__ __main__.py
|   |   |__ placeholder_config.yaml
|   |   |__ placeholder_init.py
|   |   |__ placeholder_main.py
|   |__ tool_call/                      # Tool-call evaluation benchmark
|   |__ self_repair/                    # (Optional) Self-repair benchmark
|
|__ core/                               # Core abstractions and runtime
|   |__ agentoutput.py                  # AbstractAgentOutput
|   |__ dataset.py                      # AbstractDataset
|   |__ evaluation.py                   # AbstractEvaluation
|   |__ message.py                      # Standard message types
|   |__ agentbuilder/                   # AgentBuilder implementations
|   |__ agentrunner/                    # Runners: sync + async
|   |   |__ synchronous.py              # Sequential, multithreaded, multiprocessing
|   |   |__ asynchronous.py             # Async sequential & concurrent runners
|   |__ datasetloader/                  # DatasetLoader base
|   |__ evaluationsaver/                # EvaluationSaver base
|   |   |__ dashboard.py                # DashboardEvaluationSaver
|   |__ translator/                     # Output→Message translators
|
|__ dashboard/                          # Streamlit-powered dashboard
|   |__ app.py                          # Main UI
|   |__ utils.py                        # Dashboard utilities
|   |__ config.yaml                     # Dashboard configuration
|
|__ evaluations/                        # Stored evaluation results
|
|__ README.md                           # You are here""", language="text")

    st.divider()

    # --- Program Flow Section ---
    st.header("Program Flow")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        The system consists of several components that work together to evaluate an agent:

        1. **AgentBuilder** constructs an agent from configuration.
        2. **DatasetLoader** loads a dataset into a standardized Dataset object.
        3. **Translator** converts raw agent outputs into normalized Message objects.
        4. **AgentRunner** executes the agent across the dataset (sync, threaded, multiprocess, or async).
        5. The dataset is populated with outputs and passed to an **Evaluator**.
        6. The **Evaluator** produces an Evaluation object.
        7. **EvaluationSaver** exports or stores the evaluation (JSON, dashboard results, etc.).

        This architecture allows *any* benchmark to be defined through simple config files and modular Python components.
        """)
    
    with col2:
        st.caption("Program Flow Diagram")
        st.image("flow.png", width='stretch')

    st.divider()

    # --- Usage Section ---
    st.header("How to Run")

    st.subheader("1. Setup")
    st.markdown("Clone the repository and install dependencies:")
    st.code("""
git clone https://github.com/saksham1341/abet
cd abet
python -m pip install -r requirements.txt""", language="bash")

    st.subheader("2. Running a Benchmark")
    st.markdown("Execute a benchmark as a python module:")
    st.code("python -m benchmark.tool_call", language="bash")
    st.markdown("""
    Benchmarks are configured via the `config.yaml` file inside their directory.
    This includes:

    * agent builder class
    * runner type (sync/async/threaded/process)
    * evaluator class
    * evaluation saver configuration
    * dataset path
    * translator class
    """)

    st.subheader("3. Dashboard")
    st.markdown("""
        If a benchmark uses
    `core.evaluationsaver.DashboardEvaluationSaver`
    and saves results under `evaluations/`, the Streamlit dashboard can visualize:

    * model comparisons
    * per-metric analysis
    * leaderboard-style views

    Minimal example snippet:
    """)
    st.code("""
evaluationsaver_class: core.evaluationsaver.DashboardEvaluationSaver
evaluationsaver_config:
    benchmark_name: *benchmark_name
    run_id: *model_name
    output_path: "evaluations/my_run.json" """, language="yaml")
    st.markdown("Launch the dashboard:")
    st.code("streamlit run dashboard_app.py", language="bash")

    st.divider()
    st.markdown("Made with <3 by [saksham1341](https://github.com/saksham1341/abet)")

def generate_pages(ces: List[CompiledEvaluation]) -> List[st.Page]:    
    return [
        st.Page(
            page=render_home_page,
            title="Home",
            url_path="index",
            default=True
        )] + [
        st.Page(
            page=compiled_evaluation_page_generator(ce),
            title=ce.benchmark_name,
            url_path=f"{ce.benchmark_name}"
        ) for ce in ces
    ]
