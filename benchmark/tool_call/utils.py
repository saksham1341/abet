"""
Tool Call Benchmark Evaluator
"""

from core.datasetloader import BaseDatasetLoader
from core.dataset import ListDataset
from core.evaluator import BaseEvaluator
from core.evaluation import DashboardEvaluation
from core.message import ToolCallMessage, AnyMessage
from core.agentoutput import AbstractAgentOutput
from core.translator import LangGraphTranslator
from dataclasses import dataclass
from typing import List, Dict
import json
import Levenshtein


@dataclass
class ToolCallBenchmarkAgentOutput(AbstractAgentOutput):
    tool_call_names: List = None
    tool_call_args: List = None

class ToolCallBenchmarkTranslator(LangGraphTranslator):
    def _translate(self, native_output: Dict) -> ToolCallBenchmarkAgentOutput:
        o = super()._translate(native_output)

        tool_call_names = list()
        tool_call_args = list()
        for msg in o.messages:
            if not isinstance(msg, ToolCallMessage):
                continue

            tool_call_names.append(msg.tool_name)
            tool_call_args.append(msg.tool_kwargs)
        
        return ToolCallBenchmarkAgentOutput(
            tool_call_names=tool_call_names,
            tool_call_args=tool_call_args
        )

class ToolCallBenchmarkDatasetLoader(BaseDatasetLoader):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.path = self.config["path"]
    
    def _load_dataset(self) -> ListDataset:
        with open(self.path, "r") as f:
            raw_data = json.load(f)

        inputs = []
        targets = []
        for r in raw_data:
            inputs.append(r["input"])
            targets.append({
                "tool_call_names": r["tool_call_names"],
                "tool_call_args": r["tool_call_args"]
            })
        
        return ListDataset(
            inputs=inputs,
            targets=targets
        )

@dataclass
class ToolCallBenchmarkEvaluation(DashboardEvaluation):
    tsa: float = None     # Tool Selection Accuracy
    ahr: float = None     # Argument Hallucination Rate
    tp: float = None      # Trajectory Precision

class ToolCallBenchmarkEvaluator(BaseEvaluator):
    def _evaluate(self, dataset: ListDataset) -> DashboardEvaluation:
        keys = dataset.get_keys()
        total_correct_tool_calls = 0
        grand_total_tool_calls = 0
        total_correct_args = 0
        grand_total_args = 0
        total_tp = 0
        samples = []

        for key in keys:
            inp = dataset.get_input(key)
            out = dataset.get_output(key)
            tgt = dataset.get_target(key)
            sample = {
                "input": inp,
                "output": out.__dict__,
                "target": tgt
            }

            out_tool_call_names = out.tool_call_names
            tgt_tool_call_names = tgt["tool_call_names"]

            out_tool_call_args = out.tool_call_args
            tgt_tool_call_args = tgt["tool_call_args"]

            total_tool_calls = len(tgt_tool_call_names)
            correct_tool_calls = 0
            total_args = len(tgt_tool_call_args)
            correct_args = 0
            add_to_samples = False
            for i in range(total_tool_calls):
                ttc = tgt_tool_call_names[i]
                try:
                    otc = out_tool_call_names[i]
                except IndexError:
                    add_to_samples = True

                    break

                if ttc != otc:
                    add_to_samples = True

                    continue
            
                correct_tool_calls += 1

                out_args = out_tool_call_args[i]
                tgt_args = tgt_tool_call_args[i]

                for k in tgt_args.keys():
                    if k not in out_args or out_args[k] != tgt_args[k]:
                        add_to_samples = True
                        continue

                    correct_args += 1
                
            if add_to_samples:
                samples.append(sample)

            total_correct_tool_calls += correct_tool_calls
            grand_total_tool_calls += total_tool_calls

            total_correct_args += correct_args
            grand_total_args += total_args
        
            distance = Levenshtein.distance(tgt_tool_call_names, out_tool_call_names)
            max_distance = max(len(tgt_tool_call_names), len(out_tool_call_names))
            tp = 1.0 if max_distance == 0 else (1 - distance / max_distance)
            total_tp += tp
        
        tsa = total_correct_tool_calls / grand_total_tool_calls
        ahr = (grand_total_args - total_correct_args) / grand_total_args
        tp = total_tp / len(keys)

        return ToolCallBenchmarkEvaluation(
            dataset=dataset,
            tsa=tsa,
            ahr=ahr,
            tp=tp,
            samples=samples
        )
