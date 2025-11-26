"""
Self-Repair Benchmark Tools
"""

import sys
import subprocess
import tempfile
import os

def run_code(code: str) -> str:
    """
    Run a python code.

    Args:
        code (str): The code to run.
    Returns:
        str: The output of the code or traceback if any exception occures.
    """
    
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
