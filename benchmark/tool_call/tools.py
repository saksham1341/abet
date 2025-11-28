"""
tools.py

Deterministic tool universe for agentic benchmarking.

This module defines:
1. Static, closed-world data for cities, roads, attractions, products, and currency rates.
2. Deterministic implementations of all tools described in the spec.

Each tool is a pure function with:
- clear docstrings
- no randomness or external I/O
- structured return values (dicts / lists) as if they were tool call results
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Tuple
import ast
import hashlib
import re


# =============================================================================
# 0. STATIC DATA
# =============================================================================

# 0.1 Cities
CITIES: List[Dict[str, Any]] = [
    {"city_id": 1, "name": "Alpha", "country": "A-Land", "timezone": "UTC+01:00"},
    {"city_id": 2, "name": "Beta", "country": "A-Land", "timezone": "UTC+01:00"},
    {"city_id": 3, "name": "Gamma", "country": "B-Land", "timezone": "UTC+02:00"},
    {"city_id": 4, "name": "Delta", "country": "B-Land", "timezone": "UTC+02:00"},
    {"city_id": 5, "name": "Epsilon", "country": "C-Land", "timezone": "UTC+03:00"},
]

# Road distances in km (undirected)
# keys are frozenset({from_city_id, to_city_id})
CITY_DISTANCES: Dict[frozenset, float] = {
    frozenset({1, 2}): 100.0,
    frozenset({2, 3}): 200.0,
    frozenset({3, 4}): 150.0,
    frozenset({2, 4}): 400.0,
    frozenset({1, 3}): 250.0,
    frozenset({4, 5}): 300.0,
}

TRAVEL_SPEEDS_KMH: Dict[str, float] = {
    "car": 100.0,
    "train": 150.0,
}

# 0.2 Attractions
ATTRACTIONS: List[Dict[str, Any]] = [
    {
        "attraction_id": 1,
        "name": "Alpha History Museum",
        "city_id": 1,
        "category": "museum",
        "open_time": "09:00",
        "close_time": "17:00",
        "base_price_eur": 12.50,
    },
    {
        "attraction_id": 2,
        "name": "Beta Art Gallery",
        "city_id": 2,
        "category": "museum",
        "open_time": "10:00",
        "close_time": "18:00",
        "base_price_eur": 15.00,
    },
    {
        "attraction_id": 3,
        "name": "Gamma Theme Park",
        "city_id": 3,
        "category": "park",
        "open_time": "08:00",
        "close_time": "20:00",
        "base_price_eur": 35.00,
    },
    {
        "attraction_id": 4,
        "name": "Delta Opera House",
        "city_id": 4,
        "category": "concert",
        "open_time": "18:00",
        "close_time": "23:00",
        "base_price_eur": 50.00,
    },
    {
        "attraction_id": 5,
        "name": "Epsilon Tech Center",
        "city_id": 5,
        "category": "exhibition",
        "open_time": "09:00",
        "close_time": "19:00",
        "base_price_eur": 20.00,
    },
]

# 0.3 Products
PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": 1,
        "name": "Travel Backpack 30L",
        "category": "gear",
        "price_eur": 60.00,
        "rating": 4.5,
        "stock": 12,
    },
    {
        "product_id": 2,
        "name": "Noise-Cancelling Headset",
        "category": "electronics",
        "price_eur": 120.00,
        "rating": 4.8,
        "stock": 5,
    },
    {
        "product_id": 3,
        "name": "Compact Travel Umbrella",
        "category": "gear",
        "price_eur": 15.00,
        "rating": 4.1,
        "stock": 0,
    },
    {
        "product_id": 4,
        "name": "Power Bank 20,000mAh",
        "category": "electronics",
        "price_eur": 40.00,
        "rating": 4.6,
        "stock": 20,
    },
    {
        "product_id": 5,
        "name": "City Guidebook Bundle",
        "category": "books",
        "price_eur": 25.00,
        "rating": 4.0,
        "stock": 50,
    },
]

# 0.4 Currency rates (base: EUR)
# Interpretation: amount_in_eur = amount_in_currency * rate_to_eur[currency]
CURRENCY_RATES: Dict[str, float] = {
    "EUR": 1.0,
    "USD": 0.9,
    "GBP": 1.1,
}


# =============================================================================
# Helper utilities (internal, deterministic)
# =============================================================================


def _round_half_away_from_zero(value: float, ndigits: int = 2) -> float:
    """
    Deterministic rounding: "round half away from zero" using Decimal.

    :param value: Float to round.
    :param ndigits: Number of decimal places.
    :return: Rounded float.
    """
    quantize_str = "1." + "0" * ndigits
    d = Decimal(str(value))
    return float(d.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP))


def _parse_time_hhmm(t: str) -> int:
    """
    Parse 'HH:MM' into minutes since midnight.

    :param t: Time string 'HH:MM'.
    :return: Minutes since midnight.
    """
    hh, mm = t.split(":")
    return int(hh) * 60 + int(mm)


def _format_time_hhmm(minutes: int) -> str:
    """
    Format minutes since midnight into 'HH:MM'.

    :param minutes: Minutes since midnight.
    :return: Time string 'HH:MM'.
    """
    hh = minutes // 60
    mm = minutes % 60
    return f"{hh:02d}:{mm:02d}"


# =============================================================================
# 1. math_calculator
# =============================================================================

class _SafeEvalVisitor(ast.NodeVisitor):
    """
    AST visitor to safely evaluate simple arithmetic expressions.

    Supported:
    - Binary ops: +, -, *, /
    - Unary ops: +, -
    - Parentheses (handled by AST structure)
    - Numeric literals (int/float)

    No variables, function calls, attributes, etc.
    """

    allowed_binops = {
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
    }

    allowed_unaryops = {
        ast.UAdd,
        ast.USub,
    }

    def visit(self, node):  # type: ignore[override]
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self.allowed_binops:
                raise ValueError("Unsupported binary operator")
            left = self.visit(node.left)
            right = self.visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.allowed_unaryops:
                raise ValueError("Unsupported unary operator")
            operand = self.visit(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
        elif isinstance(node, ast.Num):  # py < 3.8
            return node.n
        elif isinstance(node, ast.Constant):  # py >= 3.8
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Only numeric literals are allowed")
        else:
            raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def math_calculator(expression: str) -> Dict[str, Any]:
    """
    Evaluate an arithmetic expression safely (no variables, no functions).

    Supported operators: +, -, *, / and parentheses.

    :param expression: A math expression using +, -, *, /, parentheses, and decimal numbers.
                       Example: '3.5 * (2 + 4) - 1'
    :return: dict with key 'result' containing the numeric result (float).
    :raises ValueError: On invalid or unsafe expressions.
    """
    parsed = ast.parse(expression, mode="eval")
    visitor = _SafeEvalVisitor()
    result = visitor.visit(parsed)
    return {"result": float(result)}


# =============================================================================
# 2. string_template
# =============================================================================

_TEMPLATE_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


def string_template(template: str, values: Dict[str, str]) -> Dict[str, Any]:
    """
    Fill a template using named placeholders `{{name}}` style.

    Placeholders that have no matching key in values are left unchanged.

    :param template: Template string with `{{placeholder}}` tokens.
    :param values: Mapping of placeholder names to replacement string values.
    :return: dict with key 'result' containing the formatted string.
    """

    def repl(match: re.Match) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    result = _TEMPLATE_PATTERN.sub(repl, template)
    return {"result": result}


# =============================================================================
# 3. list_cities
# =============================================================================

def list_cities() -> Dict[str, Any]:
    """
    Return the full list of known cities with IDs, names, country, and timezone.

    :return: dict with key 'cities' containing a list of city dicts.
    """
    # Return a shallow copy to avoid accidental mutation by callers.
    return {"cities": [dict(city) for city in CITIES]}


# =============================================================================
# 4. get_city_connections
# =============================================================================

def get_city_connections(from_city_id: int, to_city_id: int) -> Dict[str, Any]:
    """
    Return direct road distance and travel durations between two cities.

    If there is no direct road in the static graph, return {"exists": False}.

    :param from_city_id: ID of origin city.
    :param to_city_id: ID of destination city.
    :return: dict:
        - exists: bool
        - distance_km: float (if exists)
        - travel_time_hours: {"car": float, "train": float} (if exists)
    """
    key = frozenset({from_city_id, to_city_id})
    if key not in CITY_DISTANCES:
        return {"exists": False}

    distance = CITY_DISTANCES[key]
    travel_time_hours = {
        method: distance / speed for method, speed in TRAVEL_SPEEDS_KMH.items()
    }
    return {
        "exists": True,
        "distance_km": distance,
        "travel_time_hours": travel_time_hours,
    }


# =============================================================================
# 5. shortest_route
# =============================================================================

def shortest_route(from_city_id: int, to_city_id: int) -> Dict[str, Any]:
    """
    Compute the shortest path between two cities by road, minimizing total distance.

    Uses Dijkstra's algorithm over the static CITY_DISTANCES graph.

    :param from_city_id: Origin city ID.
    :param to_city_id: Destination city ID.
    :return: dict with keys:
        - path: list of city IDs in order (empty if no path)
        - total_distance_km: float or None
        - per_leg: list of {from_city_id, to_city_id, distance_km} (one per edge)
    """

    # Build adjacency list
    adj: Dict[int, List[Tuple[int, float]]] = {}
    for key, dist in CITY_DISTANCES.items():
        a, b = tuple(key)
        adj.setdefault(a, []).append((b, dist))
        adj.setdefault(b, []).append((a, dist))

    # Dijkstra
    import heapq

    INF = float("inf")
    dist_to: Dict[int, float] = {city["city_id"]: INF for city in CITIES}
    prev: Dict[int, Optional[int]] = {city["city_id"]: None for city in CITIES}

    if from_city_id not in dist_to or to_city_id not in dist_to:
        # Unknown city IDs
        return {"path": [], "total_distance_km": None, "per_leg": []}

    dist_to[from_city_id] = 0.0
    heap: List[Tuple[float, int]] = [(0.0, from_city_id)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist_to[node]:
            continue
        if node == to_city_id:
            break
        for neighbor, w in adj.get(node, []):
            nd = d + w
            if nd < dist_to[neighbor]:
                dist_to[neighbor] = nd
                prev[neighbor] = node
                heapq.heappush(heap, (nd, neighbor))

    if dist_to[to_city_id] == INF:
        return {"path": [], "total_distance_km": None, "per_leg": []}

    # Reconstruct path
    path: List[int] = []
    cur: Optional[int] = to_city_id
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    # Build per_leg info
    per_leg: List[Dict[str, Any]] = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        distance = CITY_DISTANCES[frozenset({a, b})]
        per_leg.append(
            {
                "from_city_id": a,
                "to_city_id": b,
                "distance_km": distance,
            }
        )

    return {
        "path": path,
        "total_distance_km": dist_to[to_city_id],
        "per_leg": per_leg,
    }


# =============================================================================
# 6. list_attractions
# =============================================================================

def list_attractions() -> Dict[str, Any]:
    """
    Return the full list of attractions with IDs, city_id, category, hours, and base price in EUR.

    :return: dict with key 'attractions' containing a list of attraction dicts.
    """
    return {"attractions": [dict(a) for a in ATTRACTIONS]}


# =============================================================================
# 7. filter_and_sort_items
# =============================================================================

@dataclass
class FilterCondition:
    field: str
    op: str  # "eq", "neq", "lt", "lte", "gt", "gte", "in", "not_in"
    value: Any


def _apply_filter(item: Dict[str, Any], cond: FilterCondition) -> bool:
    """
    Apply a single filter condition to an item.

    Missing fields are treated as None.
    """
    val = item.get(cond.field, None)
    op = cond.op
    cmp_val = cond.value

    if op == "eq":
        return val == cmp_val
    if op == "neq":
        return val != cmp_val
    if op == "lt":
        return val < cmp_val
    if op == "lte":
        return val <= cmp_val
    if op == "gt":
        return val > cmp_val
    if op == "gte":
        return val >= cmp_val
    if op == "in":
        return val in (cmp_val or [])
    if op == "not_in":
        return val not in (cmp_val or [])
    raise ValueError(f"Unsupported filter op: {op}")


def filter_and_sort_items(
    items: List[Dict[str, Any]],
    filters: Optional[List[Dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> Dict[str, Any]:
    """
    Filter a list of objects and sort the result using simple conditions.

    Filters are combined with logical AND.

    :param items: List of JSON-like dict objects to filter and sort.
    :param filters: List of filter dicts, each with:
        - field: str
        - op: "eq" | "neq" | "lt" | "lte" | "gt" | "gte" | "in" | "not_in"
        - value: Any
    :param sort_by: Field name to sort by (optional). If None, keep original order.
    :param sort_order: "asc" or "desc"; default "asc".
    :return: dict with key 'items' containing the filtered and sorted list.
    """
    filters = filters or []
    conds = [
        FilterCondition(
            field=f["field"],
            op=f["op"],
            value=f.get("value"),
        )
        for f in filters
    ]

    # Filter
    filtered: List[Tuple[int, Dict[str, Any]]] = []
    for idx, item in enumerate(items):
        if all(_apply_filter(item, cond) for cond in conds):
            filtered.append((idx, item))

    # Sort
    if sort_by is not None:
        reverse = sort_order == "desc"

        def sort_key(t: Tuple[int, Dict[str, Any]]):
            idx, itm = t
            return itm.get(sort_by, None), idx  # tie-breaker by original index

        filtered.sort(key=sort_key, reverse=reverse)

    result_items = [itm for _, itm in filtered]
    return {"items": result_items}


# =============================================================================
# 8. currency_convert
# =============================================================================

def currency_convert(amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
    """
    Convert an amount from one currency to another using fixed deterministic rates.

    Rates are defined by the CURRENCY_RATES table.
    Conversion goes via EUR:
        amount_eur = amount * rate_to_eur[from_currency]
        result = amount_eur / rate_to_eur[to_currency]

    Rounding uses "round half away from zero" to 2 decimal places.

    :param amount: Amount in from_currency.
    :param from_currency: "EUR", "USD", or "GBP".
    :param to_currency: "EUR", "USD", or "GBP".
    :return: dict with key 'converted_amount' containing the converted float.
    :raises KeyError: If an unknown currency code is provided.
    """
    if from_currency not in CURRENCY_RATES:
        raise KeyError(f"Unknown from_currency: {from_currency}")
    if to_currency not in CURRENCY_RATES:
        raise KeyError(f"Unknown to_currency: {to_currency}")

    amount_eur = amount * CURRENCY_RATES[from_currency]
    result = amount_eur / CURRENCY_RATES[to_currency]
    result = _round_half_away_from_zero(result, ndigits=2)
    return {"converted_amount": result}


# =============================================================================
# 9. lookup_product
# =============================================================================

def lookup_product(product_id: int) -> Dict[str, Any]:
    """
    Get details for a single product by product_id.

    :param product_id: Product ID to look up.
    :return: dict:
        - found: bool
        - product: product dict (if found)
    """
    for p in PRODUCTS:
        if p["product_id"] == product_id:
            return {"found": True, "product": dict(p)}
    return {"found": False}


# =============================================================================
# 10. list_products
# =============================================================================

def list_products() -> Dict[str, Any]:
    """
    Return the full list of products with prices, ratings, and stock.

    :return: dict with key 'products' containing a list of product dicts.
    """
    return {"products": [dict(p) for p in PRODUCTS]}


# =============================================================================
# 11. booking_simulator
# =============================================================================

def booking_simulator(
    attraction_id: int,
    city_id: int,
    start_time_local: str,
    duration_hours: float,
    tickets: int,
    currency: str,
) -> Dict[str, Any]:
    """
    Validate and simulate a booking for an attraction visit, returning a deterministic confirmation.

    Validation:
    - attraction_id must exist.
    - attraction.city_id must match given city_id.
    - start_time_local must be within [open_time, close_time].
    - (start_time_local + duration_hours) must be <= close_time.
    - tickets must be >= 1.
    - currency must be a supported code for conversion.

    Price calculation:
    - total_price_eur = base_price_eur * tickets
    - total_price_currency = currency_convert(total_price_eur, "EUR", currency)
    - The converted amount is rounded with round-half-away-from-zero.

    Booking ID:
    - Deterministic SHA-256 hash of input parameters, hex-encoded and truncated to 8 chars.

    :param attraction_id: ID of the attraction.
    :param city_id: ID of the city where the attraction is located.
    :param start_time_local: Visit start time in 'HH:MM', local to city.
    :param duration_hours: Visit duration in hours (may be fractional).
    :param tickets: Number of tickets (>= 1).
    :param currency: Desired currency code ("EUR", "USD", "GBP").
    :return: dict:
        - success: bool
        - booking_id: str (if success)
        - total_price: {"amount": float, "currency": str} (if success)
        - details: dict (if success)
        - error: str (if not success)
    """
    # Validate tickets
    if tickets < 1:
        return {"success": False, "error": "Tickets must be at least 1."}

    # Find attraction
    attraction = None
    for a in ATTRACTIONS:
        if a["attraction_id"] == attraction_id:
            attraction = a
            break

    if attraction is None:
        return {"success": False, "error": "Unknown attraction_id."}

    if attraction["city_id"] != city_id:
        return {
            "success": False,
            "error": "city_id does not match attraction.city_id.",
        }

    # Validate currency
    if currency not in CURRENCY_RATES:
        return {"success": False, "error": "Unsupported currency."}

    # Validate times
    open_min = _parse_time_hhmm(attraction["open_time"])
    close_min = _parse_time_hhmm(attraction["close_time"])
    try:
        start_min = _parse_time_hhmm(start_time_local)
    except Exception:
        return {"success": False, "error": "Invalid start_time_local format."}

    duration_min = int(round(duration_hours * 60))
    end_min = start_min + duration_min

    if start_min < open_min or end_min > close_min:
        return {
            "success": False,
            "error": "Visit times are outside opening hours.",
        }

    # Price calculation
    base_price_eur = float(attraction["base_price_eur"])
    total_price_eur = base_price_eur * tickets
    converted = currency_convert(total_price_eur, "EUR", currency)
    total_price_amount = converted["converted_amount"]

    # Deterministic booking ID
    payload = f"{attraction_id}|{city_id}|{start_time_local}|{duration_hours}|{tickets}|{currency}"
    booking_id_full = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    booking_id = booking_id_full[:8]

    return {
        "success": True,
        "booking_id": booking_id,
        "total_price": {"amount": total_price_amount, "currency": currency},
        "details": {
            "attraction_id": attraction_id,
            "city_id": city_id,
            "start_time_local": start_time_local,
            "duration_hours": duration_hours,
            "tickets": tickets,
        },
    }


# =============================================================================
# Optional: simple tool registry
# =============================================================================

TOOL_REGISTRY: Dict[str, Any] = {
    "math_calculator": math_calculator,
    "string_template": string_template,
    "list_cities": list_cities,
    "get_city_connections": get_city_connections,
    "shortest_route": shortest_route,
    "list_attractions": list_attractions,
    "filter_and_sort_items": filter_and_sort_items,
    "currency_convert": currency_convert,
    "lookup_product": lookup_product,
    "list_products": list_products,
    "booking_simulator": booking_simulator,
}

tools = [v for v in TOOL_REGISTRY.values()]
