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

def create_tool_response(success: bool, content: str) -> dict:
    return {
        "success": success,
        "content": content
    }

def run_code(code: str, input_key: int) -> str:
    """
    Run a python code and compare against it's correct output (using the given input_key).
    Returns the traceback if some exception occures during execution of the code,
    and also when code output does not match the correct output.
    Also returns an error if maimum tries reached.

    Args:
        code (str): The code to run.
        input_key (int): The input_key provided in your prompt.
    Returns:
        dict: {
            success (bool): Indicates if the code is correct, i.e., gives the desired output,
            content (str): If the code is correct, this is the output of the code, otherwise this is the error in the code.
        }
    """

    # check if input key is valid if not return error
    if input_key is not None:
        try:
            input_key = int(input_key)
            correct_output = dataset[input_key]["correct_output"]
        except:
            return create_tool_response(False, "Error: Invalid input key passed, make sure you pass the same input key as given in the prompt")

    # check quota
    if input_key is not None:
        if input_key not in tries:
            tries[input_key] = 1
        elif tries[input_key] == 5:
            return create_tool_response(False, "Error: Maximum attempts made. You can not run any code now. Terminate.")
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
        
        # Cleanup the file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Combine stdout and stderr for the agent
        if result.returncode == 0:
            output = result.stdout.rstrip()
            if input_key is not None:    
                if output != correct_output:
                    return create_tool_response(False, "Error: Wrong output.")
            return create_tool_response(True, result.stdout if result.stdout else "")
        else:
            return create_tool_response(False, f"Error:\n{result.stderr}\n{result.stdout}")

    except subprocess.TimeoutExpired:
        # Cleanup the file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return create_tool_response(False, "Timeout: Code execution took longer than 10 seconds.")
    except Exception as e:
        # Cleanup the file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return create_tool_response(False, f"System Execution Error: {str(e)}")
    finally:
        # Cleanup the file
        if os.path.exists(temp_path):
            os.remove(temp_path)

tools = [
    run_code
]
