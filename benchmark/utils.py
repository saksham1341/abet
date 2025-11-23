"""
General benchmar utilities
"""

from core.agentbuilder import AbstractAgentBuilder
from core.translator import AbstractTranslator
from core.dataset import AbstractDataset
from core.evaluationresult import AbstractEvaluationResult
from typing import Any, Dict, TypeVar, Type, Callable
import importlib
from tqdm import tqdm

AgentBuilder_T = TypeVar("AgentBuilder_T", bound=AbstractAgentBuilder)
Translator_T = TypeVar("Translator_T", bound=AbstractTranslator)

def import_item(s: str) -> Any:
    _ = s.split(".")
    module_name = ".".join(_[:-1])
    item_name = _[-1]

    return getattr(importlib.import_module(module_name), item_name)

def get_agentbuilder_class_from_config(config: Dict) -> Type[AgentBuilder_T]:
    return import_item(config["agentbuilder_class"])

def get_translator_class_from_config(config: Dict) -> Type[Translator_T]:
    return import_item(config["translator_class"])

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
    return import_item(config["datasetloader_callable"])

def load_dataset_from_config(config: Dict) -> AbstractDataset:
    datasetloader_callable = get_datasetloader_callable_from_config(config)
    
    return datasetloader_callable(
        **config["datasetloader_kwargs"]
    )

def get_evaluator_callable_from_config(config: Dict) -> Callable[[AbstractDataset, ...], AbstractEvaluationResult]:
    return import_item(config["evaluator_callable"])

def evaluate_from_config(dataset: AbstractDataset, config: Dict) -> AbstractEvaluationResult:
    evaluator_callable = get_evaluator_callable_from_config(config)
    
    return evaluator_callable(
        dataset=dataset,
        **config["evaluator_kwargs"]
    )

def get_evaluationresultsaver_callable_from_config(config: Dict) -> Callable:
    return import_item(config["evaluationresultsaver_callable"])

def save_evaluationresult_form_config(result: AbstractEvaluationResult, config: Dict) -> None:
    evaluationresultsaver_callable = get_evaluationresultsaver_callable_from_config(config)

    return evaluationresultsaver_callable(
        result=result,
        **config["evaluationresultsaver_kwargs"]
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
    for key in tqdm(keys, total=len(keys)):
        inp = dataset.get_input(key)
        output = agent(inp)

        dataset.set_output(key, translator.from_native_output(output))
    
    # evaluate
    result = evaluate_from_config(
        dataset=dataset,
        config=config
    )

    # save evaluation result
    save_evaluationresult_form_config(
        result=result,
        config=config
    )
