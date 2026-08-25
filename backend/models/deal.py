from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataQualityIssue(BaseModel):
    """Represents a single data-quality problem detected during normalization."""

    field: str
    message: str
    raw_value: object
    severity: str = "warning"
    normalized_value: Optional[object] = None

    model_config = ConfigDict(
        json_encoders={date: lambda d: d.isoformat()},
    )


class Deal(BaseModel):
    """Normalized Deal model - independent of Excel/Monday column names."""

    id: Optional[str] = None
    name: Optional[str] = None
    owner: Optional[str] = None
    client: Optional[str] = None
    status: Optional[str] = None
    close_date: Optional[date] = None
    tentative_close_date: Optional[date] = None
    closure_probability: Optional[str] = None  # "High", "Medium", "Low", or percentage
    deal_value: Optional[float] = None  # in currency units (masked/raw as-is)
    stage: Optional[str] = None
    product: Optional[str] = None
    sector: Optional[str] = None
    created_date: Optional[date] = None

    # Normalization tracking
    normalization_flags: dict = Field(default_factory=dict)

    @field_validator("closure_probability", mode="before")
    @classmethod
    def validate_probability(cls, v: Any) -> Any:
        if v is None:
            return None
        v = str(v).strip().lower()
        if v in {"high", "h"}:
            return "High"
        if v in {"medium", "m"}:
            return "Medium"
        if v in {"low", "l"}:
            return "Low"
        return v

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Any) -> Any:
        if v is None:
            return None
        v = str(v).strip().lower()
        if v in {"open", "o"}:
            return "Open"
        if v in {"won", "w"}:
            return "Won"
        if v in {"lost", "l"}:
            return "Lost"
        return v.capitalize()

    def is_missing_required(self) -> bool:
        """Check if required fields are missing."""
        return (
            self.name is None
            and self.owner is None
            and self.status is None
        )

    def has_valid_close_date(self) -> bool:
        """Check if deal has a valid close date."""
        return self.close_date is not None

    def has_valid_value(self) -> bool:
        """Check if deal has a valid value."""
        return self.deal_value is not None and self.deal_value > 0