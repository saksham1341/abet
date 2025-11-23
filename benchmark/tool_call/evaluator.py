"""
Tool Call Benchmark Evaluator
"""

from core.dataset import ListDataset
from core.evaluationresult import AbstractEvaluationResult


class EvaluationResult(AbstractEvaluationResult):
    total_outputs: int

def evaluate(dataset: ListDataset) -> AbstractEvaluationResult:
    total_outputs = len(dataset.outputs)

    valid_outputs = 0
    correct_outputs = 0
    total_absolute_error = 0
    for k in dataset.get_keys():
        inp = dataset.get_input(k)
        out = dataset.get_output(k)
        tgt = dataset.get_target(k)

        print("=" * 50)
        print("INP:", inp)
        print("TGT:", tgt[-1].content)
        print("OUT:", out.messages[-1].content)
        print("=" * 50)

        _tgt = float(tgt[-1].content)
        try:
            _out = float(out.messages[-1].content)
        except:
            continue
        
        valid_outputs += 1
        if _tgt == _out:
            correct_outputs += 1
        
        total_absolute_error += abs(_tgt - _out)
    mean_absolute_error = total_absolute_error / valid_outputs

    result = AbstractEvaluationResult()
    result.total_outputs = total_outputs
    result.valid_outputs = valid_outputs
    result.correct_outputs = correct_outputs
    result.mean_absolute_error = mean_absolute_error

    return result

def save_result(result: AbstractEvaluationResult) -> None:
    print("Total Outputs:", result.total_outputs)
    print("Valid Outputs:", result.valid_outputs)
    print("Correct Outputs:", result.correct_outputs)
    print("MAE of Incorrect Outputs:", result.mean_absolute_error)
