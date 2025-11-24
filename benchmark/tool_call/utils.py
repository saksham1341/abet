"""
Tool Call Benchmark Evaluator
"""

from core.datasetloader import AbstractDatasetLoader
from core.dataset import ListDataset
from core.evaluator import AbstractEvaluator
from core.evaluation import AbstractEvaluation
from core.evaluationsaver import AbstractEvaluationSaver
from core.message import ToolCallMessage, AnyMessage
from core.agentoutput import AgentOutputWithMessages
from core.translator import LangGraphTranslator
from dataclasses import dataclass
from typing import List, Dict
import json
import Levenshtein


@dataclass
class ToolCallBenchmarkAgentOutput(AgentOutputWithMessages):
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
            messages=o.messages,
            tool_call_names=tool_call_names,
            tool_call_args=tool_call_args
        )

class ToolCallBenchmarkDatasetLoader(AbstractDatasetLoader):
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.path = config["path"]
    
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
class ToolCallBenchmarkEvaluation(AbstractEvaluation):
    tsa: float     # Tool Selection Accuracy
    ahr: float     # Argument Hallucination Rate
    tp: float      # Trajectory Precision

class ToolCallBenchmarkEvaluator(AbstractEvaluator):
    def __init__(self, config: Dict) -> None:
        self.config = config

    def _evaluate(self, dataset: ListDataset) -> ToolCallBenchmarkEvaluation:
        keys = dataset.get_keys()
        total_correct_tool_calls = 0
        grand_total_tool_calls = 0
        total_correct_args = 0
        grand_total_args = 0
        total_tp = 0
        for key in keys:
            out = dataset.get_output(key)
            tgt = dataset.get_target(key)

            out_tool_call_names = out.tool_call_names
            tgt_tool_call_names = tgt["tool_call_names"]

            out_tool_call_args = out.tool_call_args
            tgt_tool_call_args = tgt["tool_call_args"]

            total_tool_calls = len(tgt_tool_call_names)
            correct_tool_calls = 0
            total_args = len(tgt_tool_call_args)
            correct_args = 0
            for i in range(total_tool_calls):
                ttc = tgt_tool_call_names[i]
                try:
                    otc = out_tool_call_names[i]
                except IndexError:
                    break

                if ttc != otc:
                    continue
            
                correct_tool_calls += 1

                out_args = out_tool_call_args[i]
                tgt_args = tgt_tool_call_args[i]

                for k in tgt_args.keys():
                    if k not in out_args or out_args[k] != tgt_args[k]:
                        continue

                    correct_args += 1

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
            tp=tp
        )

class ToolCallBenchmarkEvaluationSaver(AbstractEvaluationSaver):
    def __init__(self, config: Dict) -> None:
        self.config = config
    
    def _save_evaluation(self, evaluation: ToolCallBenchmarkEvaluation) -> bool:
        del evaluation.dataset

        with open(self.config["output_path"], "w") as f:
            json.dump(evaluation.__dict__, f)

        return True
