"""
Tools for Tool Call Benchmark
"""

def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a (int): First integer.
        b (int): Second integer.
    
    Returns:
        int: Sum of both integers.
    """

    return a + b

def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a (int): First integer.
        b (int): Second integer.
    
    Returns:
        int: Sum of both integers.
    """
    
    return a * b

tools = [
    add, 
    multiply
]
