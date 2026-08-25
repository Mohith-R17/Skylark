from __future__ import annotations

import math
from typing import Any


def _is_na_like(value: Any) -> bool:
    """Check if a value represents a missing/NA sentinel without requiring pandas."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip().lower() in {"", "nan", "none", "na", "n/a"}:
        return True
    return False


def normalize_currency(value: Any) -> float | None:
    """
    Normalize a currency value from various formats.
    Handles:
    - float values
    - string representations with commas, currency symbols
    - None / empty / NaN -> None
    - Invalid strings -> None
    Preserves the actual business value; does NOT invent zeros for missing data.
    """
    if _is_na_like(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        # Remove currency symbols, commas, spaces
        cleaned = s.replace("$", "").replace("₹", "").replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def normalize_numeric(value: Any) -> int | float | None:
    """
    Normalize a numeric value.
    Returns int if the value is a whole number, otherwise float.
    Returns None if the value is missing or invalid.
    """
    if _is_na_like(value):
        return None
    if isinstance(value, bool):
        # Don't treat True/False as numbers
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        v = float(value)
        if v == int(v):
            return int(v)
        return v
    if isinstance(value, str):
        s = value.strip().replace(",", "")
        if not s:
            return None
        try:
            v = float(s)
            if v == int(v):
                return int(v)
            return v
        except ValueError:
            return None
    return None


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert to int, returning default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default