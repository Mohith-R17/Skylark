"""
Pipeline analytics — computes metrics from normalized Deal data.

Every metric clearly reports data-quality limitations.
Missing values are never silently invented.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models.deal import Deal


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

@dataclass
class MetricResult:
    """A single metric value with data-quality context."""
    label: str
    value: Any
    unit: str = ""
    data_quality: str = "reliable"  # reliable | limited | insufficient
    caveat: str = ""
    available_count: int = 0
    missing_count: int = 0


@dataclass
class BreakdownItem:
    """One slice of a breakdown (e.g. one sector in 'pipeline by sector')."""
    key: str
    value: float
    count: int
    pct_of_total: float = 0.0


@dataclass
class BreakdownResult:
    """A breakdown metric with its slices."""
    label: str
    items: List[BreakdownItem] = field(default_factory=list)
    total: float = 0.0
    data_quality: str = "reliable"
    caveat: str = ""
    available_count: int = 0
    missing_count: int = 0


# ---------------------------------------------------------------------------
# Pipeline analytics
# ---------------------------------------------------------------------------

class PipelineAnalytics:
    """Compute pipeline metrics from a list of normalized Deals."""

    def __init__(self, deals: List[Deal]) -> None:
        self.deals = deals
        self._open_deals = [d for d in deals if d.status and d.status.lower() in ("open", "pending", "proposal", "negotiation")]

    # -- Aggregate metrics --------------------------------------------------

    def total_pipeline_value(self) -> MetricResult:
        """Sum of deal_value for open/active deals."""
        valued = [d for d in self._open_deals if d.deal_value is not None]
        missing = len(self._open_deals) - len(valued)
        total = sum(d.deal_value for d in valued)  # type: ignore[arg-type]
        quality = _quality_rating(len(valued), missing)
        caveat = f"{missing} open deals missing value" if missing else ""
        return MetricResult(
            label="Total Pipeline Value",
            value=round(total, 2),
            unit="currency",
            data_quality=quality,
            caveat=caveat,
            available_count=len(valued),
            missing_count=missing,
        )

    def weighted_pipeline(self) -> MetricResult:
        """
        Pipeline value weighted by closure probability.
        High = 0.75, Medium = 0.50, Low = 0.25.
        Deals missing probability are excluded (not silently weighted at 0).
        """
        weights = {"high": 0.75, "medium": 0.50, "low": 0.25}
        usable = []
        for d in self._open_deals:
            if d.deal_value is not None and d.closure_probability is not None:
                w = weights.get(d.closure_probability.lower())
                if w is not None:
                    usable.append(d.deal_value * w)
        missing = len(self._open_deals) - len(usable)
        total = sum(usable)
        quality = _quality_rating(len(usable), missing)
        caveat = f"{missing} deals excluded (missing value or probability)" if missing else ""
        return MetricResult(
            label="Weighted Pipeline",
            value=round(total, 2),
            unit="currency",
            data_quality=quality,
            caveat=caveat,
            available_count=len(usable),
            missing_count=missing,
        )

    def deals_missing_close_dates(self) -> MetricResult:
        """Count of deals with no close date."""
        missing = [d for d in self.deals if d.close_date is None]
        return MetricResult(
            label="Deals Missing Close Date",
            value=len(missing),
            unit="count",
            data_quality="reliable",
            caveat=f"{len(missing)}/{len(self.deals)} deals ({_pct(len(missing), len(self.deals))}%)",
            available_count=len(self.deals) - len(missing),
            missing_count=len(missing),
        )

    def deals_missing_probability(self) -> MetricResult:
        """Count of deals with no closure probability."""
        missing = [d for d in self.deals if d.closure_probability is None]
        return MetricResult(
            label="Deals Missing Probability",
            value=len(missing),
            unit="count",
            data_quality="reliable",
            caveat=f"{len(missing)}/{len(self.deals)} deals ({_pct(len(missing), len(self.deals))}%)",
            available_count=len(self.deals) - len(missing),
            missing_count=len(missing),
        )

    # -- Breakdowns ---------------------------------------------------------

    def pipeline_by_sector(self) -> BreakdownResult:
        """Pipeline value grouped by sector."""
        return self._breakdown_by(
            label="Pipeline by Sector",
            key_fn=lambda d: d.sector or "__missing__",
            value_fn=lambda d: d.deal_value,
        )

    def pipeline_by_stage(self) -> BreakdownResult:
        """Pipeline value grouped by deal stage."""
        return self._breakdown_by(
            label="Pipeline by Stage",
            key_fn=lambda d: d.stage or "__missing__",
            value_fn=lambda d: d.deal_value,
        )

    def pipeline_by_owner(self) -> BreakdownResult:
        """Pipeline value grouped by deal owner."""
        return self._breakdown_by(
            label="Pipeline by Owner",
            key_fn=lambda d: d.owner or "__missing__",
            value_fn=lambda d: d.deal_value,
        )

    def pipeline_by_probability(self) -> BreakdownResult:
        """Pipeline value grouped by closure probability."""
        return self._breakdown_by(
            label="Pipeline by Probability",
            key_fn=lambda d: d.closure_probability or "__missing__",
            value_fn=lambda d: d.deal_value,
        )

    def deal_status_distribution(self) -> BreakdownResult:
        """Count of deals by status."""
        counts: Dict[str, int] = Counter()
        for d in self.deals:
            key = d.status or "__missing__"
            counts[key] += 1
        items = [
            BreakdownItem(key=k, value=float(c), count=c, pct_of_total=_pct(c, len(self.deals)))
            for k, c in sorted(counts.items(), key=lambda x: -x[1])
        ]
        return BreakdownResult(
            label="Deal Status Distribution",
            items=items,
            total=float(len(self.deals)),
            data_quality="reliable",
            available_count=len(self.deals),
        )

    def pipeline_trend(self) -> BreakdownResult:
        """Pipeline generated over time based on created_date (YYYY-MM)."""
        def format_month(d: Deal) -> str:
            if not d.created_date:
                return "__missing__"
            return d.created_date.strftime("%Y-%m")

        return self._breakdown_by(
            label="Pipeline Trend (by Created Date)",
            key_fn=format_month,
            value_fn=lambda d: d.deal_value,
            sort_by_key=True,
        )

    # -- Helpers ------------------------------------------------------------

    def _breakdown_by(
        self,
        label: str,
        key_fn,
        value_fn,
        sort_by_key: bool = False,
    ) -> BreakdownResult:
        buckets: Dict[str, List[float]] = {}
        missing_value = 0
        for d in self._open_deals:
            val = value_fn(d)
            if val is None:
                missing_value += 1
                continue
            key = key_fn(d)
            buckets.setdefault(key, []).append(val)

        total = sum(sum(vs) for vs in buckets.values())
        items = []
        
        if sort_by_key:
            sorted_items = sorted(buckets.items(), key=lambda x: x[0])
        else:
            sorted_items = sorted(buckets.items(), key=lambda x: -sum(x[1]))
            
        for key, vs in sorted_items:
            s = sum(vs)
            items.append(BreakdownItem(
                key=key,
                value=round(s, 2),
                count=len(vs),
                pct_of_total=_pct(s, total) if total else 0.0,
            ))

        quality = _quality_rating(sum(len(v) for v in buckets.values()), missing_value)
        caveat = f"{missing_value} deals excluded (missing value)" if missing_value else ""
        return BreakdownResult(
            label=label,
            items=items,
            total=round(total, 2),
            data_quality=quality,
            caveat=caveat,
            available_count=sum(len(v) for v in buckets.values()),
            missing_count=missing_value,
        )

    # -- Summary for API consumption ----------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Full pipeline analytics summary."""
        return {
            "total_deals": len(self.deals),
            "open_deals": len(self._open_deals),
            "total_pipeline_value": _to_dict(self.total_pipeline_value()),
            "weighted_pipeline": _to_dict(self.weighted_pipeline()),
            "deals_missing_close_dates": _to_dict(self.deals_missing_close_dates()),
            "deals_missing_probability": _to_dict(self.deals_missing_probability()),
            "pipeline_by_sector": _breakdown_to_dict(self.pipeline_by_sector()),
            "pipeline_by_stage": _breakdown_to_dict(self.pipeline_by_stage()),
            "pipeline_by_owner": _breakdown_to_dict(self.pipeline_by_owner()),
            "pipeline_by_probability": _breakdown_to_dict(self.pipeline_by_probability()),
            "deal_status_distribution": _breakdown_to_dict(self.deal_status_distribution()),
            "pipeline_trend": _breakdown_to_dict(self.pipeline_trend()),
        }


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _pct(part: float, whole: float) -> float:
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 1)


def _quality_rating(available: int, missing: int) -> str:
    total = available + missing
    if total == 0:
        return "insufficient"
    ratio = available / total
    if ratio >= 0.7:
        return "reliable"
    if ratio >= 0.3:
        return "limited"
    return "insufficient"


def _to_dict(m: MetricResult) -> Dict[str, Any]:
    return {
        "label": m.label,
        "value": m.value,
        "unit": m.unit,
        "data_quality": m.data_quality,
        "caveat": m.caveat,
        "available_count": m.available_count,
        "missing_count": m.missing_count,
    }


def _breakdown_to_dict(b: BreakdownResult) -> Dict[str, Any]:
    return {
        "label": b.label,
        "total": b.total,
        "data_quality": b.data_quality,
        "caveat": b.caveat,
        "available_count": b.available_count,
        "missing_count": b.missing_count,
        "items": [
            {"key": i.key, "value": i.value, "count": i.count, "pct": i.pct_of_total}
            for i in b.items
        ],
    }
