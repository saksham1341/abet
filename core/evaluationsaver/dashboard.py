"""
DashboardEvaluationSaver saves an evaluation for our dashboard to be able to visualize it
"""

from core.evaluation import AbstractEvaluation
from .base import BaseEvaluationSaver
import json


class DashboardEvaluationSaver(BaseEvaluationSaver):
    def _save_evaluation(self, evaluation: AbstractEvaluation) -> None:
        data = {
            "benchmark_name": self.config["benchmark_name"],
            "run_id": self.config["run_id"]
        }

        data["results"] = {}
        # only support integer and float values
        for k, v in evaluation.__dict__.items():
            if isinstance(v, (int , float)):
                data["results"][k] = v

        with open(self.config["output_path"], "w") as f:
            json.dump(data, f)
