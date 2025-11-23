"""
Tool Call Benchmark dataset handling.
"""

from core.dataset import ListDataset
from core.message import AnyMessage
from typing import List
import json

def load_dataset(path: str) -> ListDataset:
    with open(path, "r") as f:
        raw_data = json.load(f)

    inputs = []
    targets = []
    for r in raw_data:
        inputs.append(r["input"])
        _ = list()

        for msg_kwargs in r["optimal_message_sequence"]:
            _.append(
                AnyMessage(**msg_kwargs)
            )
         
    return ListDataset(
        inputs=inputs,
        targets=targets
    )
