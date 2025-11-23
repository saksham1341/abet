"""
Tool Call Benchmark Evaluator
"""

from core.dataset import ListDataset
from core.evaluationresult import AbstractEvaluationResult

def evaluate(dataset: ListDataset) -> AbstractEvaluationResult:
    return AbstractEvaluationResult()

def save_result(result: AbstractEvaluationResult) -> None:
    print(result)
