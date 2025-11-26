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

def compile_evaluations(evaluations: List[Evaluation], config: Dict) -> List[CompiledEvaluation]:
    benchmark_wise_results = {}
    for e in evaluations:
        if e.benchmark_name  not in benchmark_wise_results:
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
    weights = ce.config.get("scoring_weights", {})
    
    df = ce.df.copy()
    for col in df.columns:
        # get weight, default is 1
        w = weights.get(col, 1)
        
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

def plot_compiled_evaluation(ce: CompiledEvaluation) -> List[plt.Figure]:
    resp = {}
    
    df = ce.df
    run_ids = df.index.values
    for col in df.columns:
        fig = plt.figure()
        ax = fig.subplots()
        bars = ax.bar(run_ids, df[col].values)
        ax.bar_label(bars, padding=3)
        ax.margins(y=0.2)

        resp[col] = fig
    
    return resp

def render_compiled_evaluation(ce: CompiledEvaluation):
    st.header(ce.benchmark_name)
    
    with st.spinner():
        leaderboard_df = get_compiled_evaluation_leaderboard(ce)
    
    st.subheader("Leaderboards")
    st.dataframe(leaderboard_df)

    with st.spinner():
        plots = plot_compiled_evaluation(ce)

    for col, fig in plots.items():
        st.subheader(f"Comparing `{col}`")
        st.pyplot(fig)
        st.divider()
    
    st.markdown("Made with <3 by [saksham1341](https://github.com/saksham1341/abet)")

def compiled_evaluation_page_generator(ce: CompiledEvaluation) -> Callable:
    def _():
        return render_compiled_evaluation(ce)

    return _

def generate_pages(ces: List[CompiledEvaluation]) -> List[st.Page]:    
    return [
        st.Page(
            page=compiled_evaluation_page_generator(ce),
            title=ce.benchmark_name,
            url_path=ce.benchmark_name
        ) for ce in ces
    ]
