from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Set

from services.normalization.date_normalizer import normalize_date
from services.normalization.numeric_normalizer import normalize_currency, normalize_numeric
from services.normalization.text_normalizer import normalize_text


class MissingValueDetector:
    """
    Detect and report missing/null/undefined values across different data types.
    Does NOT silently invent values. Returns detection results with flags.
    """

    @staticmethod
    def detect(field_name: str, value: Any) -> Dict[str, Any]:
        """
        Detect the state of a field value.
        Returns dict with keys: known, missing, invalid, normalized
        """
        result: Dict[str, Any] = {
            "field": field_name,
            "known": False,
            "missing": False,
            "invalid": False,
            "normalized": None,
        }

        if value is None:
            result["missing"] = True
            return result

        if isinstance(value, bool):
            # Booleans are not considered "missing" in our context,
            # but we flag them specially
            result["known"] = True
            result["normalized"] = value
            return result

        if isinstance(value, (int, float)):
            if isinstance(value, float) and value != value:  # NaN
                result["invalid"] = True
                return result
            result["known"] = True
            result["normalized"] = normalize_numeric(value)
            return result

        if isinstance(value, (date, datetime)):
            result["known"] = True
            result["normalized"] = value
            return result

        # String type
        if isinstance(value, str):
            s = value.strip()
            if not s:
                result["missing"] = True
                return result
            result["known"] = True
            result["normalized"] = normalize_text(value, strip=True, lower=False)
            return result

        # Fallback for other types
        s = str(value).strip()
        if not s:
            result["missing"] = True
            return result

        result["known"] = True
        result["normalized"] = s
        return result

    @classmethod
    def assess_series(
        cls, rows: List[Dict[str, Any]], fields: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Assess multiple rows for missing values across specified fields.
        Returns a dict mapping field name -> detection summary.
        """
        results: Dict[str, Dict[str, Any]] = {}
        for field in fields:
            results[field] = cls._assess_field(rows, field)
        return results

    @staticmethod
    def _assess_field(rows: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
        total = len(rows)
        missing = 0
        invalid = 0
        known = 0
        values: List[Any] = []

        for row in rows:
            val = row.get(field)
            if val is None:
                missing += 1
                continue
            if isinstance(val, bool):
                known += 1
                values.append(str(val))
                continue
            if isinstance(val, (int, float)):
                if isinstance(val, float) and val != val:  # NaN
                    invalid += 1
                else:
                    known += 1
                    values.append(val)
                continue
            s = str(val).strip()
            if not s:
                missing += 1
                continue
            known += 1
            values.append(s)

        return {
            "total": total,
            "missing": missing,
            "invalid": invalid,
            "known": known,
            "missing_pct": round(missing / total * 100, 1) if total > 0 else 0,
            "known_values": values[:10],  # first 10 for inspection
        }


class DuplicateDetector:
    """
    Basic duplicate detection across rows based on key fields.
    Does NOT assume a specific primary key; uses configurable key fields.
    """

    @staticmethod
    def find_duplicates(
        rows: List[Dict[str, Any]],
        key_fields: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Find rows that have duplicate values in the specified key fields.
        Returns list of dicts with 'key_values', 'count', 'indices'.
        """
        seen: Dict[str, List[int]] = {}
        for i, row in enumerate(rows):
            key_parts = []
            for kf in key_fields:
                val = row.get(kf)
                key_parts.append(str(val) if val is not None else "")
            key = "|".join(key_parts)
            if key not in seen:
                seen[key] = []
            seen[key].append(i)

        duplicates: List[Dict[str, Any]] = []
        for key, indices in seen.items():
            if len(indices) > 1:
                duplicates.append(
                    {
                        "key_values": key,
                        "count": len(indices),
                        "indices": indices,
                        "preview_rows": [rows[i] for i in indices[:3]],  # first 3
                    }
                )
        return duplicates


class InvalidValueDetector:
    """
    Detect values that are present but malformed/invalid for their type.
    """

    @staticmethod
    def detect(value: Any, expected_type: str = "auto") -> Dict[str, str]:
        """
        Detect if a value is invalid for the expected type.
        Returns dict with 'status' ('valid'|'invalid') and 'reason'.
        """
        result: Dict[str, str] = {"status": "valid", "reason": ""}

        if value is None:
            result["status"] = "missing"
            result["reason"] = "value is None"
            return result

        if isinstance(value, bool):
            result["status"] = "valid"
            result["reason"] = "boolean value"
            return result

        if expected_type == "auto":
            expected_type = "string"  # default assumption

        if expected_type == "date":
            parsed = normalize_date(value)
            if parsed is None:
                result["status"] = "invalid"
                result["reason"] = f"cannot parse as date: {value}"
            return result

        if expected_type in ("currency", "numeric"):
            parsed = normalize_currency(value)
            if parsed is None:
                result["status"] = "invalid"
                result["reason"] = f"cannot parse as currency: {value}"
            return result

        if expected_type == "text":
            if not isinstance(value, str) or not value.strip():
                result["status"] = "invalid"
                result["reason"] = "empty or non-string text"
            return result

        return result