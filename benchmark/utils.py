"""
General benchmar utilities
"""

from core.agentbuilder import AbstractAgentBuilder
from core.translator import AbstractTranslator
from core.dataset import AbstractDataset
from core.evaluationresult import AbstractEvaluationResult
from typing import Any, Dict, TypeVar, Type, Callable
import importlib

AgentBuilder_T = TypeVar("AgentBuilder_T", bound=AbstractAgentBuilder)
Translator_T = TypeVar("Translator_T", bound=AbstractTranslator)

def get_agentbuilder_class_from_config(config: Dict) -> Type[AgentBuilder_T]:
    _ = config["agentbuilder_class"].split(".")
    module_name = ".".join(_[:-1])
    class_name = _[-1]

    return getattr(importlib.import_module(module_name), class_name)

def get_translator_class_from_config(config: Dict) -> Type[Translator_T]:
    _ = config["translator_class"].split(".")
    module_name = ".".join(_[:-1])
    class_name = _[-1]

    return getattr(importlib.import_module(module_name), class_name)

def create_agent_from_config(config: Dict) -> Callable:
    agentbuilder_class = get_agentbuilder_class_from_config(config)
    agentbuilder_obj = agentbuilder_class(
        config=config["agentbuilder_config"]
    )

    return agentbuilder_obj.build()

def create_translator_from_config(config: Dict) -> AbstractTranslator:
    translator_class = get_translator_class_from_config(config)
    translator_obj = translator_class(
        config=config["translator_config"]
    )

    return translator_obj

def get_datasetloader_callable_from_config(config: Dict) -> Callable:
    _ = config["datasetloader_callable"].split(".")
    module_name = ".".join(_[:-1])
    callable_name = _[-1]

    return getattr(importlib.import_module(module_name), callable_name)

def load_dataset_from_config(config: Dict) -> AbstractDataset:
    datasetloader_callable = get_datasetloader_callable_from_config(config)
    
    return datasetloader_callable(
        **config["datasetloader_kwargs"]
    )

def get_evaluator_callable_from_config(config: Dict) -> Callable[[AbstractDataset, ...], AbstractEvaluationResult]:
    _ = config["evaluator_callable"].split(".")
    module_name = ".".join(_[:-1])
    callable_name = _[-1]

    return getattr(importlib.import_module(module_name), callable_name)

def evaluate_from_config(dataset: AbstractDataset, config: Dict) -> AbstractEvaluationResult:
    evaluator_callable = get_evaluator_callable_from_config(config)
    
    return evaluator_callable(
        dataset=dataset,
        **config["evaluator_kwargs"]
    )

def run(config: Dict = None) -> None:
    # build agent
    agent = create_agent_from_config(config)

    # create translator
    translator = create_translator_from_config(config)
    
    # load dataset
    dataset = load_dataset_from_config(config)

    # run agent on the dataset and store translated outptus
    keys = dataset.get_keys()
    for key in keys:
        inp = dataset.get_input(key)
        output = agent(inp)

        dataset.set_output(key, translator.from_native_output(output))
    
    # evaluate
    results = evaluate_from_config(
        dataset=dataset,
        config=config
    )

    print(results)

    # TODO:
    # 1. Create a dataset
    # 2. Fetch it and input it to agent
    # 3. Translate agent's output to ABET Messages
    # 4. Write an evaluator function for this benchmark
    # 5. Properly format and save evaluation output
