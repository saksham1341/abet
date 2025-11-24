"""
Tool Call Benchmark Evaluator
"""

from core.datasetloader import AbstractDatasetLoader
from core.dataset import ListDataset
from core.evaluator import AbstractEvaluator
from core.evaluation import AbstractEvaluation
from core.evaluationsaver import AbstractEvaluationSaver
from core.message import AnyMessage
from dataclasses import dataclass
from pprint import pprint
from typing import Dict
import json


class ToolCallBenchmarkDatasetLoader(AbstractDatasetLoader):
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.path = config["path"]
    
    def _load_dataset(self) -> ListDataset:
        with open(self.path, "r") as f:
            raw_data = json.load(f)

        inputs = []
        targets = []
        for r in raw_data[:2]:
            inputs.append(r["input"])
            
            messages = list()
            tcc = 0
            for msg_kwargs in r["optimal_message_sequence"]:
                if msg_kwargs["message_type"] == "ToolCallMessage":
                    tcc += 1
                
                messages.append(
                    AnyMessage(**msg_kwargs)
                )
            
            target = {
                "messages": messages,
                "tool_call_count": tcc
            }

            targets.append(target)
        
        return ListDataset(
            inputs=inputs,
            targets=targets
        )

@dataclass
class ToolCallBenchmarkEvaluation(AbstractEvaluation):
    total_outputs: int
    valid_outputs: int
    correct_outputs: int
    mean_absolute_error: float
    mean_delta_tcc_perc: float

class ToolCallBenchmarkEvaluator(AbstractEvaluator):
    def __init__(self, config: Dict) -> None:
        self.config = config

    def _evaluate(self, dataset: ListDataset) -> ToolCallBenchmarkEvaluation:
        total_outputs = len(dataset.outputs)

        valid_outputs = 0
        correct_outputs = 0
        total_absolute_error = 0
        total_delta_tcc_perc = 0
        for k in dataset.get_keys():
            inp = dataset.get_input(k)
            out = dataset.get_output(k)
            tgt = dataset.get_target(k)

            out_messages = out.messages
            tgt_messages = tgt["messages"]

            # print("=" * 50)
            # print("INP:", inp)
            # print("TGT:", tgt_messages[-1].content)
            # print("OUT:", out_messages[-1].content)
            # print("=" * 50)

            # Evaluate final output
            _tgt = float(tgt_messages[-1].content)
            try:
                _out = float(out_messages[-1].content)
            except:
                continue
            
            valid_outputs += 1
            if _tgt == _out:
                correct_outputs += 1

                # Evaluate tool_calls
                tcc = 0
                for msg in out_messages:
                    if msg.message_type == "ToolCallMessage":
                        tcc += 1
                
                tgt_tcc = tgt["tool_call_count"]
                delta_tcc = abs(tcc - tgt_tcc)
                delta_tcc_perc = delta_tcc / tgt_tcc
                total_delta_tcc_perc += delta_tcc_perc
            
            total_absolute_error += abs(_tgt - _out)
        
        incorrect_outputs = valid_outputs - correct_outputs
        mean_absolute_error = 0 if incorrect_outputs == 0 else total_absolute_error / incorrect_outputs
        mean_delta_tcc_perc = total_delta_tcc_perc / correct_outputs

        result = ToolCallBenchmarkEvaluation(
            dataset=dataset,
            total_outputs = total_outputs,
            valid_outputs = valid_outputs,
            correct_outputs = correct_outputs,
            mean_absolute_error = mean_absolute_error,
            mean_delta_tcc_perc = mean_delta_tcc_perc
        )
        return result

class ToolCallBenchmarkEvaluationSaver(AbstractEvaluationSaver):
    def __init__(self, config: Dict) -> None:
        self.config = config
    
    def _save_evaluation(self, evaluation: ToolCallBenchmarkEvaluation) -> bool:
        pprint(evaluation.__dict__)

        return True
