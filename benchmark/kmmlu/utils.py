"""
KMMLU Benchmark Utils
"""

from dataclasses import dataclass
from core.datasetloader import BaseDatasetLoader
from core.dataset import ListDataset
from core.agentoutput import BaseAgentOutput
from core.translator import LangGraphTranslator
from core.evaluation import DashboardEvaluation
from core.evaluator import BaseEvaluator
from core.evaluationsaver import DashboardEvaluationSaver
from typing import Dict
import pandas as pd


class KMMLUDatasetLoader(BaseDatasetLoader):
    def _load_category(self, subset: str) -> pd.DataFrame:
        df = pd.read_csv(f"hf://datasets/HAERAE-HUB/KMMLU/data/{subset}-test.csv")

        return df
    
    def _create_input(self, ques: str, a: str, b: str, c: str, d: str) -> str:
        return f"""
질문: {ques}
선택지:
(1) {a}
(2) {b}
(3) {c}
(4) {d}
"""

    def _load_dataset(self) -> ListDataset:
        inps = []
        tgts = []
        
        categories = self.config["categories"]
        for category in categories:
            df = self._load_category(category)
            for idx, r in df.iterrows():
                inps.append(
                    self._create_input(
                        r["question"],
                        r["A"],
                        r["B"],
                        r["C"],
                        r["D"]
                    )
                )

                tgts.append({
                    "correct_option": r["answer"],
                    "human_accuracy": r["Human Accuracy"],
                    "category": category
                })
        
        return ListDataset(
            inputs=inps,
            targets=tgts
        )

@dataclass
class KMMLUAgentOutput(BaseAgentOutput):
    selected_option: int

class KMMLUTranslator(LangGraphTranslator):
    def _translate(self, *args, **kwargs) -> KMMLUAgentOutput:
        o = super()._translate(*args, **kwargs)

        try:
            selected_option = int(o.messages[-1].content)
        except Exception:
            selected_option = None
        
        return KMMLUAgentOutput(
            selected_option=selected_option
        )

@dataclass
class KMMLUEvaluation(DashboardEvaluation):
    accuracies: Dict = None

class KMMLUEvaluator(BaseEvaluator):
    def _evaluate(self, dataset: ListDataset) -> KMMLUEvaluation:
        correct_counts = {}
        total_counts = {}

        samples = []

        keys = dataset.get_keys()
        for key in keys:
            tgt = dataset.get_target(key)
            tgt_category = tgt["category"]
            tgt_option = tgt["correct_option"]
            output = dataset.get_output(key)
            selected_option = output.selected_option

            if tgt_category not in total_counts:
                total_counts[tgt_category] = 0
                correct_counts[tgt_category] = 0
            
            if tgt_option == selected_option:
                correct_counts[tgt_category] += 1
            else:
                samples.append({
                    "question": dataset.get_input(key),
                    "selected_option": selected_option,
                    "correct_option": tgt_option
                })
            
            total_counts[tgt_category] += 1
        
        accuracies = {}
        for category in total_counts.keys():
            accuracies[category] = correct_counts[category] / total_counts[category]
        
        return KMMLUEvaluation(
            dataset=dataset,
            accuracies=accuracies,
            samples=samples
        )

class KMMLUEvaluationSaver(DashboardEvaluationSaver):
    def _save_evaluation(self, evaluation: KMMLUEvaluation) -> bool:
        # Take the accuracies dictionary inside the evaluation and set them as the evaluation's attributes

        accuracies = evaluation.accuracies
        for category, acc in accuracies.items():
            setattr(evaluation, category, acc)
        
        # now call the default saver
        return super()._save_evaluation(evaluation)
