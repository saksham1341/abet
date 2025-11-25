"""
Self-Repair Benchmark Tools
"""

import io
import sys
import traceback


def run_code(code: str) -> str:
    """
    Run a python code.

    Args:
        code (str): The code to run.
    Returns:
        str: Output of the run or the traceback if an exception occured.
    """

    captured_output = io.StringIO()
    _, sys.stdout = sys.stdout, captured_output
    
    try:
        exec(
            code
        )
    except Exception as e:
        to_return = traceback.format_exc()
    else:
        to_return = captured_output.getvalue()
    
    sys.stdout = _

    return to_return

tools = [
    run_code
]
