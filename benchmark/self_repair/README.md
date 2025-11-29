# Self-Repair Benchmark

**Evaluates an LLM agent’s ability to debug code by iteratively using a `run_code` tool.**

Live at Streamlit [here](https://sxm-abet.streamlit.app/Self%20Repair%20Benchmark)

---

## 🎯 Purpose

This benchmark measures:

* First-Try Success Rate (**FTSR**)
* Any-Try Success Rate (**SR**)
* Self-Correction Rate (**SCR**)
* Average Tries per Sample (**ATS**)

The benchmark simulates a real-world coding environment where agents iteratively refine failing code.

---

## Pipeline Summary

```
SRBDatasetLoader → LangGraphAgentBuilder → AsyncConcurrentAgentRunner → SRBTranslator → SRBEvaluator → DashboardEvaluationSaver
```

---

# 1. Dataset Loading

DatasetLoader: `SRBDatasetLoader`

Loads from `dataset.json`, containing:

* A buggy code snippet
* Hidden test cases
* Expected output

The loader creates a `ListDataset` where:

* `inputs[i]`: problem description + failing code
* `targets[i]`: gold behavior + metadata

---

# 2. Agent Construction

The agent is built via:

```
LangGraphAgentBuilder
```

It:

* Loads the `run_code` tool from `benchmark/self_repair/tools.py`
* Loads system prompt guiding iterative repair
* Creates a LangGraph agent with tool-calling capability

Tools include:

* `run_code` → executes Python in a sandbox
* Auxiliary mathematical tools (optional)

---

# 3. Running the Agent

Runner: `AsyncConcurrentAgentRunner`

For each dataset item:

1. LLM attempts to fix code
2. Calls `run_code({"code": "...", "input_key": ...})`
3. Gets execution output
4. If incorrect, tries again (within quota)

The runner records:

* Messages
* Tool calls
* Code attempts

---

# 4. 🔄 Translating Outputs

Translator: `SRBTranslator`

Translation steps:

1. Use `LangGraphTranslator` to parse all agent messages
2. Detect all `ToolCallMessage` with `tool_name="run_code"`
3. Count number of tries
4. Extract last attempted code
5. Execute the final code again locally (`input_key=None`) to verify correctness
6. Build:

```
SRBAgentOutput(
    code_output="...",
    tries=3
)
```

---

# 5. Evaluation

Evaluator: `SRBEvaluator`

Calculates:

### **`sr` — Any-Try Success Rate**

Whether any attempt matches expected behavior.

### **`ftsr` — First-Try Success Rate**

Whether first attempt was already correct.

### **`scr` — Self-Correction Rate**

Cases where initial attempt failed but later attempts succeeded.

### **`ats` — Average Tries for Success**

Per-sample inspection includes:

* Code attempts
* Outputs

---

# 6. Dashboard Integration

Saves evaluation results using:

```
DashboardEvaluationSaver
```

Outputs metrics + sample failures for easy debugging.

---

# Summary

The Self-Repair Benchmark evaluates:

* Iterative reasoning
* Error analysis
* Debugging instincts
* Tool-use over multiple interactions

A powerful indicator of the model’s autonomous problem-solving ability.
