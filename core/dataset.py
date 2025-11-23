"""
AbstractDataset Class
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from core.agentoutput import AbstractAgentOutput


@dataclass
class AbstractDataset:
    metadata: Dict

    def get_keys(self) -> List[Any]:
        raise NotImplementedError()

    def get_input(self, key: Any) -> Any:
        raise NotImplementedError()

    def get_target(self, key: Any) -> Any:
        raise NotImplementedError()

    def set_output(self, key: Any, output: AbstractAgentOutput) -> None:
        raise NotImplementedError()

    def get_output(self, key: Any) -> AbstractAgentOutput:
        raise NotImplementedError()

@dataclass
class ListDataset(AbstractDataset):
    inputs: List[Any] = field(default_factory=list)
    targets: List[Any] = field(default_factory=list)
    outputs: List[AbstractAgentOutput] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def get_keys(self) -> List[int]:
        return list(range(len(self.inputs)))

    def get_input(self, idx: int) -> Any:
        return self.inputs[idx]
    
    def get_target(self, idx: int) -> Any:
        return self.targets[idx]
    
    def set_output(self, idx: int, output: AbstractAgentOutput) -> None:
        if len(self.outputs) == 0:
            self.outputs = [None] * len(self.inputs)
        
        self.outputs[idx] = output

    def get_output(self, idx: int) -> AbstractAgentOutput:
        return self.outputs[idx]
