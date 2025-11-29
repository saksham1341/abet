"""
DashboardEvaluationSaver saves an evaluation for our dashboard to be able to visualize it
"""

from core.evaluation import AbstractEvaluation
from .base import BaseEvaluationSaver
from pathlib import Path
from typing import List,Dict
import json
import logging

logger = logging.getLogger(__name__)


class DashboardEvaluationSaver(BaseEvaluationSaver):
    def _save_evaluation(self, evaluation: AbstractEvaluation) -> None:
        data = {
            "benchmark_name": self.config["benchmark_name"],
            "run_id": self.config["run_id"]
        }

        data["results"] = {}
        # only support integer and float values
        for k in self.config["metrics"]:
            v = getattr(evaluation, k, None)
            if isinstance(v, (int , float)):
                data["results"][k] = v
            else:
                logging.error(f"Metric {k} invalid or not found in the evaluation, skipping.")
            
        data["samples"] = getattr(evaluation, "samples", None)

        logger.debug(f"Saving evaluation with data: {data}")

        with open(Path(self.config["output_dir"], f"{data['benchmark_name']}_{data['run_id']}.json"), "w") as f:
            json.dump(data, f)
