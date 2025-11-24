# A.B.E.T.

> [!NOTE] 
> This is a work in progress.

A.B.E.T. (Agent Benchmark and Evaluation Toolkit) is a package which provides tools to 
quickly and easily implement agent benchmarks and evaluate them.

## Project Structure

```py
|__ benchmark/                          # Benchmarks live here
|   |__ utils.py                        # The main run() function and other benchmarking utilities
|   |__ init/                           # Implementation of benchmark.init command which creates a template benchmark directory
|   |   |__ __main__.py
|   |   |__ placeholder_config.yaml     # Placeholder config file
|   |   |__ placeholder_init.py         # Placeholder __init__.py file
|   |   |__ placeholder_main.py         # Placeholder __main__.py file
|   |__ tool_call/                      # Implementation of a benchmark for tool calling abilities
|       |__ ...
|__ core/                               # Core components
|   |__ agentoutput.py                  # Defines AbstractAgentOutput
|   |__ dataset.py                      # Defines AbstractDataset
|   |__ evaluation.py                   # Defines AbstractEvaluation
|   |__ message.py                      # Defines multiple message types
|   |__ agentbuilder/                   # Some AgentBuilder implementations
|   |__ agentrunner/                    # Some AgentRunner implementations (Synchronous, Multithreaded, Multiprocessed, Asynchronous)
|   |__ datasetloader/                  # Defines AbstractDatasetLoader
|   |__ evaluationsaver/                # Defines AbstractEvaluationSaver
|   |__ translator/                     # Defines AbstractTranslator
|__ README.md                           # You are here
```

## Program Flow

![Program Flow Diagram](flow.png)

The system consists of several components that work together to evaluate an agent.
1. AgentBuilder produces an Agent.
2. DatasetLoader produces a Dataset.
3. Translator produces a Translator instance that translates Agent's outputs to standardised Messages.
4. The AgentRunner processes the dataset, populating it's outputs with translated agent outputs.
5. The Updated Dataset is passed into the Evaluator.
6. The Evaluator generates an Evaluation object.
7. The Evaluation is then passed to an EvaluationSaver, which stores or exports evaluation results.

## How to run

### Setting up

First clone the repository and install required dependencies.

```sh
git clone https://github.com/saksham1341/abet
cd abet
python -m pip install -r requirements.txt
```

### Running a benchmark

To run a benchmark, just execute it as a python module.

```sh
python -m benchmark.tool_call
```

A benchmark can be configured through the `config.yaml` file inside it's directory.
