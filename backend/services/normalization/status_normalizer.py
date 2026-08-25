from __future__ import annotations

from typing import Any, Dict, List, Optional


# Status taxonomies normalizations

DEAL_STATUSES: Dict[str, str] = {
    "open": "Open",
    "o": "Open",
    "won": "Won",
    "w": "Won",
    "lost": "Lost",
    "l": "Lost",
    "closed": "Closed",
    "c": "Closed",
    "pending": "Pending",
    "pending-quote": "Pending",
    "proposal": "Proposal",
    "negotiation": "Negotiation",
}

WORKORDER_STATUSES: Dict[str, str] = {
    "completed": "Completed",
    "c": "Completed",
    "not started": "Not Started",
    "ns": "Not Started",
    "executed": "Executed",
    "e": "Executed",
    "open": "Open",
    "o": "Open",
    "partially billed": "Partially Billed",
    "pb": "Partially Billed",
    "not billed": "Not Billed",
    "nb": "Not Billed",
    "update required": "Update Required",
    "ur": "Update Required",
}

BILLING_STATUSES: Dict[str, str] = {
    "fully billed": "Fully Billed",
    "fb": "Fully Billed",
    "partially billed": "Partially Billed",
    "pb": "Partially Billed",
    "not billed": "Not Billed",
    "nb": "Not Billed",
}

COLLECTION_STATUSES: Dict[str, str] = {
    "collected": "Collected",
    "c": "Collected",
    "partially collected": "Partially Collected",
    "pc": "Partially Collected",
    "not collected": "Not Collected",
    "nc": "Not Collected",
    "update required": "Update Required",
    "ur": "Update Required",
}


def normalize_deal_status(raw: Any) -> Optional[str]:
    """
    Normalize a deal status field.
    Accepts various raw forms and maps to canonical values.
    Returns None if input is None/empty.
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    raw_str = str(raw).strip().lower()
    return DEAL_STATUSES.get(raw_str)


def normalize_wo_status(raw: Any) -> Optional[str]:
    """
    Normalize a work order status field.
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    raw_str = str(raw).strip().lower()
    return WORKORDER_STATUSES.get(raw_str)


def normalize_billing_status(raw: Any) -> Optional[str]:
    """
    Normalize a billing status field.
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    raw_str = str(raw).strip().lower()
    return BILLING_STATUSES.get(raw_str)


def normalize_collection_status(raw: Any) -> Optional[str]:
    """
    Normalize a collection status field.
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    raw_str = str(raw).strip().lower()
    return COLLECTION_STATUSES.get(raw_str)


def is_valid_deal_status(raw: Any) -> bool:
    """Check if a raw deal status is recognized."""
    if raw is None:
        return False
    return normalize_deal_status(raw) is not None


def is_valid_wo_status(raw: Any) -> bool:
    """Check if a raw WO status is recognized."""
    if raw is None:
        return False
    return normalize_wo_status(raw) is not None


# ---------------------------------------------------------------------------
# Generic status normalizer — tries all taxonomies
# ---------------------------------------------------------------------------

# Combined lookup across all status categories
_ALL_STATUSES: Dict[str, str] = {
    **DEAL_STATUSES,
    **WORKORDER_STATUSES,
    **BILLING_STATUSES,
    **COLLECTION_STATUSES,
}


def normalize_status(raw: Any) -> Optional[str]:
    """
    Generic status normalizer that searches across all known status
    taxonomies (deal, work-order, billing, collection).

    Returns the canonical form if recognized, or the stripped/title-cased
    original if the input is a non-empty string that simply doesn't match
    any known taxonomy.  Returns None only for None/empty input.
    """
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    raw_str = str(raw).strip().lower()
    canonical = _ALL_STATUSES.get(raw_str)
    if canonical is not None:
        return canonical
    # Non-empty but unrecognized — return title-cased original so callers
    # can still distinguish "present but unknown" from "missing".
    return str(raw).strip().title()