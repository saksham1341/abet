"""
General benchmar utilities
"""

from core.agentbuilder import AbstractAgentBuilder
from core.translator import AbstractTranslator
from core.agentoutput import AbstractAgentOutput
from core.datasetloader import AbstractDatasetLoader
from core.dataset import AbstractDataset
from core.agentrunner import AbstractAgentRunner
from core.evaluator import AbstractEvaluator
from core.evaluation import AbstractEvaluation
from core.evaluationsaver import AbstractEvaluationSaver
from typing import Any, Dict, TypeVar, Type, Callable
from pathlib import Path
import datetime
import importlib
import logging

fmt = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    format=fmt
)

logger = logging.getLogger(__name__)

AgentBuilder_T = TypeVar("AgentBuilder_T", bound=AbstractAgentBuilder)
Translator_T = TypeVar("Translator_T", bound=AbstractTranslator)
DatasetLoader_T = TypeVar("DatasetLoader_T", bound=AbstractDatasetLoader)
AgentRunner_T = TypeVar("AgentRunner_T", bound=AbstractAgentRunner)
Evaluator_T = TypeVar("Evaluator_T", bound=AbstractEvaluator)
EvaluationSaver_T = TypeVar("EvaluationSaver_T", bound=AbstractEvaluationSaver)

def import_item(s: str) -> Any:
    _ = s.split(".")
    module_name = ".".join(_[:-1])
    item_name = _[-1]

    return getattr(importlib.import_module(module_name), item_name)

def get_agentbuilder_class_from_config(config: Dict) -> Type[AgentBuilder_T]:
    logger.info(f"Importing agent builder class {config['agentbuilder_class']}.")
    return import_item(config["agentbuilder_class"])

def create_agentbuilder_from_config(config: Dict) -> AbstractAgentBuilder:
    agentbuilder_class = get_agentbuilder_class_from_config(config)
    logger.info("Initializing agent object.")
    agentbuilder_obj = agentbuilder_class(
        config=config["agentbuilder_config"]
    )

    return agentbuilder_obj

def create_agent_from_config(config: Dict) -> Callable:
    agentbuilder_obj = create_agentbuilder_from_config(config)
    agent = agentbuilder_obj()

    return agent

def get_translator_class_from_config(config: Dict) -> Type[Translator_T]:
    logger.info(f"Importing translator class {config['translator_class']}.")
    return import_item(config["translator_class"])

def create_translator_from_config(config: Dict) -> AbstractTranslator:
    translator_class = get_translator_class_from_config(config)
    logger.info("Initializing translator object.")
    translator_obj = translator_class(
        config=config["translator_config"]
    )

    return translator_obj

def translate_from_config(config: Dict, native_output: Any) -> AbstractAgentOutput:
    translator_obj = create_translator_from_config(config)
    agent_output = translator_obj(
        native_output=native_output
    )

    return agent_output

def get_datasetloader_class_from_config(config: Dict) -> Type[DatasetLoader_T]:
    logger.info(f"Importing dataset loader class {config['datasetloader_class']}.")
    return import_item(config["datasetloader_class"])

def create_datasetloader_from_config(config: Dict) -> AbstractDatasetLoader:
    datasetloader_class = get_datasetloader_class_from_config(config)
    logger.info("Initializing dataset loader object.")
    datasetloader_obj = datasetloader_class(
        config=config["datasetloader_config"]
    )

    return datasetloader_obj

def load_dataset_from_config(config: Dict) -> AbstractDataset:
    datasetloader_obj = create_datasetloader_from_config(config)
    dataset = datasetloader_obj()
    
    return dataset

def get_agentrunner_class_from_config(config: Dict) -> Type[AgentRunner_T]:
    logger.info(f"Importing agent runner class {config['agentrunner_class']}.")
    return import_item(config["agentrunner_class"])

def create_agentrunner_from_config(config: Dict, agent: Callable, translator: AbstractTranslator, dataset: AbstractDataset) -> AbstractAgentRunner:
    agentrunner_class = get_agentrunner_class_from_config(config)
    logger.info("Initializing agent runner object.")
    agentrunner_obj = agentrunner_class(
        agent=agent,
        translator=translator,
        dataset=dataset,
        config=config["agentrunner_config"]
    )

    return agentrunner_obj

def run_agent_from_config(config: Dict, agent: Callable, translator: AbstractTranslator, dataset: AbstractDataset) -> None:
    agentrunner_obj = create_agentrunner_from_config(
        agent=agent,
        translator=translator,
        dataset=dataset,
        config=config
    )
    agentrunner_obj()

def get_evaluator_class_from_config(config: Dict) -> Type[Evaluator_T]:
    logger.info(f"Importing evaluator class {config['evaluator_class']}.")
    return import_item(config["evaluator_class"])

def create_evaluator_from_config(config: Dict) -> AbstractEvaluator:
    evaluator_class = get_evaluator_class_from_config(config)
    logger.info("Initializing evaluator object.")
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
    logger.info(f"Importing evaluation saver class {config['evaluationsaver_class']}.")
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
    # save logs 
    if config.get("logs_dir", None):
        logger_file_path = Path(config["logs_dir"], f"{datetime.datetime.now()}_{config['benchmark_name']}.log")
        logger.info(f"Saving logs to {logger_file_path.absolute()}")
        handler = logging.FileHandler(
            filename=logger_file_path,
        )
        formatter = logging.Formatter(
            fmt=fmt
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

    logger.info("Preparing Evaluation")
    preparing_since = datetime.datetime.now()

    # build agent
    logger.info("Creating agent.")
    agent = create_agent_from_config(
        config=config
    )

    # create translator
    logger.info("Creating translator.")
    translator = create_translator_from_config(
        config=config
    )
    
    # load dataset
    logger.info("Loading dataset.")
    dataset = load_dataset_from_config(
        config=config
    )

    # create agentrunner
    logger.info("Creating agent runner.")
    agent_runner = create_agentrunner_from_config(
        config=config,
        agent=agent,
        translator=translator,
        dataset=dataset
    )

    # create evaluator
    logger.info("Creating evaluator.")
    evaluator = create_evaluator_from_config(
        config=config
    )

    # create evaluation saver
    logger.info("Creating evaluation saver.")
    evaluation_saver = create_evaluationsaver_from_config(
        config=config
    )

    # run agent
    logger.info("Starting agent runner.")
    agent_runner()
    
    # evaluate
    logger.info("Starting evaluator.")
    evaluation = evaluator(
        dataset=dataset
    )

    # save evaluation
    logger.info("Starting evaluation saver.")
    result = evaluation_saver(
        evaluation=evaluation
    )

    _ = datetime.datetime.now()
    total_run_time = _ - preparing_since
    logger.info(f"Evaluation complete. Total Time: {total_run_time.total_seconds()}s")
