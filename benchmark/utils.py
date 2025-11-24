"""
General benchmar utilities
"""

from core.agentbuilder import AbstractAgentBuilder
from core.translator import AbstractTranslator
from core.datasetloader import AbstractDatasetLoader
from core.dataset import AbstractDataset
from core.evaluator import AbstractEvaluator
from core.evaluation import AbstractEvaluation
from core.evaluationsaver import AbstractEvaluationSaver
from typing import Any, Dict, TypeVar, Type, Callable
import importlib
from tqdm import tqdm

AgentBuilder_T = TypeVar("AgentBuilder_T", bound=AbstractAgentBuilder)
Translator_T = TypeVar("Translator_T", bound=AbstractTranslator)
DatasetLoader_T = TypeVar("DatasetLoader_T", bound=AbstractDatasetLoader)
Evaluator_T = TypeVar("Evaluator_T", bound=AbstractEvaluator)
EvaluationSaver_T = TypeVar("EvaluationSaver_T", bound=AbstractEvaluationSaver)

def import_item(s: str) -> Any:
    _ = s.split(".")
    module_name = ".".join(_[:-1])
    item_name = _[-1]

    return getattr(importlib.import_module(module_name), item_name)

def get_agentbuilder_class_from_config(config: Dict) -> Type[AgentBuilder_T]:
    return import_item(config["agentbuilder_class"])

def create_agent_from_config(config: Dict) -> Callable:
    agentbuilder_class = get_agentbuilder_class_from_config(config)
    agentbuilder_obj = agentbuilder_class(
        config=config["agentbuilder_config"]
    )

    return agentbuilder_obj.build()

def get_translator_class_from_config(config: Dict) -> Type[Translator_T]:
    return import_item(config["translator_class"])

def create_translator_from_config(config: Dict) -> AbstractTranslator:
    translator_class = get_translator_class_from_config(config)
    translator_obj = translator_class(
        config=config["translator_config"]
    )

    return translator_obj

def get_datasetloader_class_from_config(config: Dict) -> Type[DatasetLoader_T]:
    return import_item(config["datasetloader_class"])

def create_datasetloader_from_config(config: Dict) -> AbstractDatasetLoader:
    datasetloader_class = get_datasetloader_class_from_config(config)
    datasetloader_obj = datasetloader_class(
        config=config["datasetloader_config"]
    )

    return datasetloader_obj

def load_dataset_from_config(config: Dict) -> AbstractDataset:
    datasetloader_obj = create_datasetloader_from_config(config)
    dataset = datasetloader_obj()
    
    return dataset

def get_evaluator_class_from_config(config: Dict) -> Type[Evaluator_T]:
    return import_item(config["evaluator_class"])

def create_evaluator_from_config(config: Dict) -> AbstractEvaluator:
    evaluator_class = get_evaluator_class_from_config(config)
    evaluator_obj = evaluator_class(
        config=config["evaluator_config"]
    )

    return evaluator_obj

def evaluate_from_config(config: Dict, dataset: AbstractDataset) -> AbstractEvaluation:
    evaluator_obj = create_evaluator_from_config(config)
    evaluation = evaluator_obj(
        dataset=dataset
    )

    return evaluation

def get_evaluationsaver_class_from_config(config: Dict) -> EvaluationSaver_T:
    return import_item(config["evaluationsaver_class"])

def create_evaluationsaver_from_config(config: Dict) -> AbstractEvaluationSaver:
    evaluationsaver_class = get_evaluationsaver_class_from_config(config)
    evaluationsaver_obj = evaluationsaver_class(
        config=config["evaluationsaver_config"]
    )

    return evaluationsaver_obj

def save_evaluation_from_config(config: Dict, evaluation: AbstractEvaluation) -> bool:
    evaluationsaver_obj = create_evaluationsaver_from_config(config)
    result = evaluationsaver_obj(
        evaluation=evaluation
    )

    return result

def run(config: Dict = None) -> None:
    # build agent
    agent = create_agent_from_config(config)

    # create translator
    translator = create_translator_from_config(config)
    
    # load dataset
    dataset = load_dataset_from_config(config)

    # create evaluator
    evaluator = create_evaluator_from_config(config)

    # create evaluation saver
    evaluation_saver = create_evaluationsaver_from_config(config)

    # run agent on the dataset and store translated outptus
    keys = dataset.get_keys()
    for key in tqdm(keys, total=len(keys)):
        inp = dataset.get_input(key)
        native_output = agent(inp)
        agent_output = translator(native_output)

        dataset.set_output(key, agent_output)
    
    # evaluate
    evaluation = evaluator(
        dataset=dataset
    )

    # save evaluation
    result = evaluation_saver(
        evaluation=evaluation
    )
