"""
Self-Repair Benchmark Utilities
"""

from core.dataset import ListDataset
from core.datasetloader import BaseDatasetLoader
from core.translator import LangGraphTranslator
from core.agentoutput import AbstractAgentOutput
from core.agentrunner import SyncThreadPoolAgentRunner
from core.message import ToolCallMessage
from core.evaluation import AbstractEvaluation
from core.evaluator import BaseEvaluator
from core.evaluationsaver import BaseEvaluationSaver
from .tools import run_code
from dataclasses import dataclass
from typing import Dict
import json


class SRBDatasetLoader(BaseDatasetLoader):
    def _load_dataset(self) -> ListDataset:
        with open(self.config["path"], "r") as f:
            raw_data = json.load(f)
        
        inputs = []
        targets = []
        for row in raw_data:
            inputs.append(json.dumps({
                "desired_task": row["desired_task"],
                "incomplete_code": row["incomplete_code"]
            }))

            targets.append(row["correct_output"])
        
        return ListDataset(
            inputs=inputs,
            targets=targets
        )

@dataclass
class SRBAgentOutput(AbstractAgentOutput):
    code_output: bool
    tries: int

class SRBTranslator(LangGraphTranslator):
    def _translate(self, native_output: Dict) -> SRBAgentOutput:
        agentoutput = super()._translate(
            native_output=native_output
        )

        messages = agentoutput.messages
        tries = 0
        last_run_code = None
        for msg in messages:
            if isinstance(msg, ToolCallMessage) and msg.tool_name == "run_code":
                tries += 1
                last_run_code = msg.tool_kwargs["code"]
        
        if last_run_code:
            code_output = run_code(
                code=last_run_code
            )
        else:
            code_output = None

        return SRBAgentOutput(
            code_output=code_output,
            tries=tries
        )

@dataclass
class SRBEvaluation(AbstractEvaluation):
    sr: float     # Any try success rate
    ftsr: float   # First try success rate
    scr: float    # Self correcting rate

class SRBEvaluator(BaseEvaluator):
    def _evaluate(self, dataset: ListDataset) -> SRBEvaluation:
        keys = dataset.get_keys()
        
        total_items = len(keys)
        total_successes = 0
        first_try_successes = 0
        second_try_successes = 0

        for key in keys:
            out = dataset.get_output(key)
            tgt = dataset.get_target(key)

            if out.tries == 0 or out.code_output is None:
                continue  # Agent didn't run any code

            agent_code_output = out.code_output.rstrip()   # Removing unintended `\n` at the end
            target_code_output = tgt

            if agent_code_output == target_code_output:
                total_successes += 1

                if out.tries == 1:
                    first_try_successes += 1
                elif out.tries == 2:
                    second_try_successes += 1
                else:
                    total_successes -= 1  # In case the agent succeeded in more than 2 tries
        
        sr = total_successes / total_items
        ftsr = (first_try_successes / total_successes) if total_successes != 0 else 0
        second_tries = total_successes - first_try_successes
        scr =  second_try_successes / second_tries if second_tries != 0 else 0

        return SRBEvaluation(
            dataset=dataset,
            sr=sr,
            ftsr=ftsr,
            scr=scr
        )

class SRBEvaluationSaver(BaseEvaluationSaver):
    def _save_evaluation(self, evaluation: SRBEvaluation) -> bool:
        del evaluation.dataset

        with open(self.config["path"], "w") as f:
            json.dump(evaluation.__dict__, f)
