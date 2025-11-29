"""
Self-Repair Benchmark Utilities
"""

from core.dataset import ListDataset
from core.datasetloader import BaseDatasetLoader
from core.translator import LangGraphTranslator
from core.agentoutput import AbstractAgentOutput
from core.agentrunner import SyncThreadPoolAgentRunner
from core.message import ToolCallMessage
from core.evaluation import DashboardEvaluation
from core.evaluator import BaseEvaluator
from .tools import run_code
from dataclasses import dataclass
from typing import Dict
import json
from pprint import pprint


class SRBDatasetLoader(BaseDatasetLoader):
    def _load_dataset(self) -> ListDataset:
        with open(self.config["path"], "r") as f:
            raw_data = json.load(f)
        
        inputs = []
        targets = []
        for idx, row in enumerate(raw_data):
            inputs.append(json.dumps({
                "input_key": idx,
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
        
        code_output = None
        if last_run_code:
            code_run_result = run_code(
                code=last_run_code,
                input_key=None  # The tool does not check against input_key if it is None
            )

            code_output = code_run_result["content"].rstrip()

        return SRBAgentOutput(
            code_output=code_output,
            tries=tries
        )

@dataclass
class SRBEvaluation(DashboardEvaluation):
    sr: float = None     # Any try success rate
    ftsr: float = None   # First try success rate
    scr: float = None    # Self correcting rate
    ats: float = None    # Averate Tries for Sucess

class SRBEvaluator(BaseEvaluator):
    def _evaluate(self, dataset: ListDataset) -> SRBEvaluation:
        keys = dataset.get_keys()
        
        total_items = len(keys)
        total_successes = 0
        total_tries = 0
        first_try_successes = 0
        other_try_successes = 0
        samples = []

        for key in keys:
            inp = dataset.get_input(key)
            out = dataset.get_output(key)
            tgt = dataset.get_target(key)
            sample = {
                "input": json.loads(inp),
                "output": out.__dict__,
                "target": tgt
            }
            
            if out.tries == 0 or out.code_output is None:
                samples.append(sample)

                continue  # Agent didn't run any code
            total_tries += out.tries

            agent_code_output = out.code_output.rstrip()   # Removing unintended `\n` at the end
            target_code_output = tgt

            if agent_code_output == target_code_output:
                total_successes += 1

                if out.tries == 1:
                    first_try_successes += 1
                else:
                    other_try_successes += 1
            else:
                samples.append(sample)
        
        sr = total_successes / total_items
        ftsr = first_try_successes / total_tries
        other_tries = total_successes - first_try_successes
        scr =  other_try_successes / other_tries if other_tries != 0 else 1
        ats = total_tries / total_items

        return SRBEvaluation(
            dataset=dataset,
            sr=sr,
            ftsr=ftsr,
            scr=scr,
            ats=ats,
            samples=samples
        )
