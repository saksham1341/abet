"""
Self-Repair Benchmark Tools
"""

import sys
import subprocess
import tempfile
import os
import json
from pathlib import Path


dataset_path = Path(Path(__file__).parent, "dataset.json")
with open(dataset_path, "r") as f:
    dataset = json.load(f)

tries = {}
tries_limit = 5

def run_code(code: str, input_key: str) -> str:
    """
    Run a python code and compare against it's correct output (using the given input_key).
    Returns the traceback if some exception occures during execution of the code,
    and also when code output does not match the correct output.
    Also returns an error if maimum tries reached.

    Args:
        code (str): The code to run.
        input_key (str): The input_key provided in your prompt.
    Returns:
        str: The output of the code or traceback if any exception occures.
    """

    # check if input key is valid if not return error
    if input_key is not None:
        try:
            input_key = int(input_key)
            correct_output = dataset[input_key]["correct_output"]
        except:
            return "Error: Invalid input key passed, make sure you pass the same input key as given in the prompt"

    # check quota
    if input_key is not None:
        if input_key not in tries:
            tries[input_key] = 1
        elif tries[input_key] == 5:
            return "Error: Maximum attempts made. You can not run any code now. Terminate."
        else:
            tries[input_key] += 1

    # Create a temporary python file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp:
        temp.write(code)
        temp_path = temp.name

    try:
        # Run the file as a separate generic Python process
        result = subprocess.run(
            [sys.executable, temp_path], # Uses the same python interpreter path
            capture_output=True,
            text=True,
            timeout=10 # Built-in timeout handling
        )
        
        # Combine stdout and stderr for the agent
        if result.returncode == 0:
            output = result.stdout.rstrip()
            if input_key is not None:
                if output != correct_output:
                    return f"Error: Wrong Output\nOUTPUT: {output}\nEXPECTED: {correct_output}."
            return result.stdout if result.stdout else "Success (No Output)"
        else:
            return f"Error:\n{result.stderr}\n{result.stdout}"

    except subprocess.TimeoutExpired:
        return "Timeout: Code execution took longer than 10 seconds."
    except Exception as e:
        return f"System Execution Error: {str(e)}"
    finally:
        # Cleanup the file
        if os.path.exists(temp_path):
            os.remove(temp_path)

tools = [
    run_code
]
