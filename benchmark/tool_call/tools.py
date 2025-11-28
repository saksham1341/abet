"""
tools.py

Very simple deterministic tool universe for benchmarking.

Static data:
- A small catalog of items with fixed prices.

Tools (all pure and deterministic):
1. list_items()        -> list all items
2. get_item(item_id)   -> fetch a single item
3. add_numbers(a, b)   -> return a + b
4. multiply_numbers(a, b) -> return a * b
5. string_template(template, values) -> simple {{name}} substitution
"""

from __future__ import annotations

from typing import Any, Dict, List
import re

# ============================================================================
# Static data
# ============================================================================

ITEMS: List[Dict[str, Any]] = [
    {"item_id": 1, "name": "Notebook", "price": 2.50},
    {"item_id": 2, "name": "Pen", "price": 1.20},
    {"item_id": 3, "name": "Backpack", "price": 25.00},
    {"item_id": 4, "name": "Bottle", "price": 8.00},
    {"item_id": 5, "name": "Headphones", "price": 45.00},
]

# Precompiled regex for string_template
_TEMPLATE_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


# ============================================================================
# Tools
# ============================================================================

def list_items() -> Dict[str, Any]:
    """
    Return the full list of items with ids, names, and prices.

    :return: {"items": [ { "item_id": int, "name": str, "price": float }, ... ]}
    """
    return {"items": [dict(item) for item in ITEMS]}


def add_numbers(a: float, b: float) -> Dict[str, Any]:
    """
    Add two numbers. Argument a must be the larger number.

    :param a: Larger addend.
    :param b: Smaller addend.
    :return: {"result": a + b}
    """
    return {"result": a + b}


def multiply_numbers(a: float, b: float) -> Dict[str, Any]:
    """
    Multiply two numbers. Argument a must be the larger number.

    :param a: Larger factor.
    :param b: Smaller factor.
    :return: {"result": a * b}
    """
    return {"result": a * b}

tools = [
    list_items,
    add_numbers,
    multiply_numbers
]
