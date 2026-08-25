from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any


def _is_na_like(value: Any) -> bool:
    """Check if a value represents a missing/NA sentinel without requiring pandas."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip().lower() in {"", "nat", "nan", "none", "na", "n/a"}:
        return True
    return False


def normalize_date(value: Any) -> date | None:
    """
    Parse a date from various possible formats.
    Safe to call on already-normalized dates.
    Returns None if parsing fails.
    """
    if _is_na_like(value):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    if not s:
        return None
    # Try common formats
    for fmt in (
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%b %d, %Y",
        "%m-%d-%Y",
    ):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # Fallback: fromisoformat
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        return None


def date_to_iso(d: date | None) -> str | None:
    """Convert a date to ISO string representation."""
    if d is None:
        return None
    return d.isoformat()


def days_between(d1: date | None, d2: date | None) -> int | None:
    """Return the number of days between two dates, or None if either is None."""
    if d1 is None or d2 is None:
        return None
    return (d2 - d1).days