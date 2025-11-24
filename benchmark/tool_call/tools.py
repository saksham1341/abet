"""
Tools for Tool Call Benchmark
"""

def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a (float): First number.
        b (float): Second number.
    
    Returns:
        float: Sum of both integers.
    """

    return a + b

def subtract(a: float, b: float) -> float:
    """
    Subtract `b` from `a`.

    Args:
        a (float): First number.
        b (float): Second number.
    
    Returns:
        float: Result of (a - b).
    """

    return a - b

def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a (float): First number.
        b (float): Second number.
    
    Returns:
        float: Product of both numbers.
    """
    
    return a * b

def divide(a: float, b: float) -> float:
    """
    Divide `a` by `b`.

    Args:
        a (float): First number.
        b (float): Second number.

    Returns:
        float: Result of (a / b)
    """

    return a / b

def modulo(a: float, b: float) -> float:
    """
    Result of `a` % `b`

    Args:
        a (float): First number.
        b (float): Second number.
    
    Returns:
        float: Resunt of (a % b)
    """

    return a % b

tools = [
    add, 
    subtract,
    multiply,
    divide,
    modulo
]
