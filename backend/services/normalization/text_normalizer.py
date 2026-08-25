from __future__ import annotations

import re
from typing import Any


def normalize_text(value: Any, *, strip: bool = True, lower: bool = False) -> str | None:
    """
    Normalize a text string.
    - strip: remove leading/trailing whitespace
    - lower: convert to lowercase
    Returns None if value is None/empty after stripping.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    v = value
    if strip:
        v = v.strip()
    if not v:
        return None
    if lower:
        v = v.lower()
    return v


def normalize_case(value: Any, *, upper: bool = False, title: bool = False) -> str | None:
    """
    Normalize case of a text string.
    - upper: convert to uppercase
    - title: convert to title case
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    v = str(value).strip()
    if not v:
        return None
    if upper:
        v = v.upper()
    if title:
        v = v.title()
    return v


def normalize_whitespace(value: Any) -> str | None:
    """
    Collapse multiple whitespace characters to a single space.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    v = str(value).strip()
    if not v:
        return None
    v = re.sub(r"\s+", " ", v)
    return v


def extract_primary_name(value: Any) -> str | None:
    """
    Extract what appears to be the primary/first name from a name string.
    Useful for owner/author names.
    """
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None
    # Take the first token
    parts = v.split()
    if parts:
        return parts[0]
    return v


def remove_prefix_suffix(value: Any, prefix: str | None = None, suffix: str | None = None) -> str | None:
    """
    Remove a known prefix and/or suffix from a string.
    Useful for cleaning deal names, serial numbers, etc.
    """
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None
    if prefix and v.lower().startswith(prefix.lower()):
        v = v[len(prefix):].strip()
    if suffix and v.lower().endswith(suffix.lower()):
        v = v[:-len(suffix)].strip()
    return v