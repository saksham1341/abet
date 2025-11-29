# KMMLU Benchmark

**Evaluates Korean-language knowledge and reasoning across multiple categories.**

Live at Streamlit [here](https://sxm-abet.streamlit.app/KMMLU%20Benchmark)

---

## Purpose

KMMLU is a Korean adaptation of the MMLU benchmark.
This module measures:

* Korean reading comprehension
* Domain-specific multiple-choice knowledge
* Category-specific accuracy
* Cultural and linguistic grounding

---

## Pipeline Summary

```
KMMLUDatasetLoader → AgentBuilder → AgentRunner → KMMLUTranslator → KMMLUEvaluator → Dashboard
```

---

# 1. Dataset Loading

File: `utils.py` 
Class: `KMMLUDatasetLoader`

### Data Source

Data is pulled directly from Hugging Face:

```
hf://datasets/HAERAE-HUB/KMMLU/data/{subset}-test.csv
```

### For each configured category:

1. Read the CSV for that category
2. For each row:

   * Construct input prompt:

     ```
     질문: {question}
     선택지:
     (1) A
     (2) B
     (3) C
     (4) D
     ```
   * Target contains:

     * `correct_option`
     * `human_accuracy` (metadata)
     * `category`

### Output Dataset

A `ListDataset` containing:

* `inputs`: formatted Korean MCQ prompts
* `targets`: dict with answer + metadata

---

# 2. Agent Construction

The benchmark uses the same:

```
LangGraphAgentBuilder
```

But you provide a KMMLU-specific system prompt instructing:

* Output must be a number (1–4)
* No explanation or extra text

No tools are used here — this is pure QA.

---

# 3. Running the Agent

Runner: `AsyncConcurrentAgentRunner`

For each prompt:

```
raw = agent(input)
translated = translator(raw)
dataset.set_output(key, translated)
```

Execution is fully parallelized.

---

# 4. Translating Outputs

File: `utils.py`
Class: `KMMLUTranslator` 

Process:

1. Call `LangGraphTranslator` → get structured messages
2. Extract model’s final answer:

   * Look at `messages[-1].content`
   * Attempt: `selected_option = int(content)`
   * Fallback: `None`

Output dataclass:

```
KMMLUAgentOutput(
    selected_option=...
)
```

---

# 5. Evaluation

Class: `KMMLUEvaluator` 

For each sample:

1. Compare predicted option vs `correct_option`
2. Maintain per-category counters
3. Collect failed examples into `samples`:

```
{
  "question": ...,
  "selected_option": ...,
  "correct_option": ...
}
```

Final `KMMLUEvaluation` contains:

* `accuracies`: dict mapping `{category → accuracy}`
* `samples`: all incorrect attempts

---

# 6. Dashboard Integration

Class: `KMMLUEvaluationSaver` 

Stores each category’s accuracy as top-level metrics so the dashboard can:

* Display radar charts
* Compare categories
* Generate leaderboards

---

# Summary

KMMLU Benchmark evaluates:

* Korean comprehension
* Expert-level factual knowledge
* Multi-domain generalization
* Answer grounding with precise option selection

It is a strong benchmark when applying to Korean-focused LLM evaluation roles.
