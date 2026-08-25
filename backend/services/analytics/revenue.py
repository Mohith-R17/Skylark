"""
Revenue, billing, and collection analytics from normalized WorkOrder data.

Every metric reports data-quality limitations.
Missing values are never silently invented.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from models.work_order import WorkOrder
from services.analytics.pipeline import (
    BreakdownItem,
    BreakdownResult,
    MetricResult,
    _breakdown_to_dict,
    _pct,
    _quality_rating,
    _to_dict,
)


class RevenueAnalytics:
    """Compute revenue/billing/collection metrics from WorkOrder list."""

    def __init__(self, work_orders: List[WorkOrder]) -> None:
        self.wos = work_orders

    # -- Aggregate value metrics --------------------------------------------

    def total_wo_value(self) -> MetricResult:
        return self._sum_metric("Total WO Value (excl GST)", lambda w: w.amount_excl_gst)

    def total_billed_value(self) -> MetricResult:
        return self._sum_metric("Total Billed (excl GST)", lambda w: w.billed_value_excl_gst)

    def total_collected(self) -> MetricResult:
        return self._sum_metric("Total Collected (incl GST)", lambda w: w.collected_amount_incl_gst)

    def total_to_be_billed(self) -> MetricResult:
        return self._sum_metric("Amount To Be Billed (excl GST)", lambda w: w.amount_to_be_billed_excl_gst)

    def total_receivable(self) -> MetricResult:
        return self._sum_metric("Accounts Receivable", lambda w: w.amount_receivable)

    # -- Status distributions -----------------------------------------------

    def billing_status_distribution(self) -> BreakdownResult:
        return self._count_by("Billing Status Distribution", lambda w: w.billing_status)

    def collection_status_distribution(self) -> BreakdownResult:
        return self._count_by("Collection Status Distribution", lambda w: w.collection_status)

    # -- Helpers ------------------------------------------------------------

    def _sum_metric(self, label: str, accessor) -> MetricResult:
        valued = [accessor(w) for w in self.wos if accessor(w) is not None]
        missing = len(self.wos) - len(valued)
        total = sum(valued)
        quality = _quality_rating(len(valued), missing)
        caveat = f"{missing} WOs missing this field" if missing else ""
        return MetricResult(
            label=label,
            value=round(total, 2),
            unit="currency",
            data_quality=quality,
            caveat=caveat,
            available_count=len(valued),
            missing_count=missing,
        )

    def _count_by(self, label: str, key_fn) -> BreakdownResult:
        counts: Dict[str, int] = Counter()
        for w in self.wos:
            key = key_fn(w) or "__missing__"
            counts[key] += 1
        items = [
            BreakdownItem(key=k, value=float(c), count=c, pct_of_total=_pct(c, len(self.wos)))
            for k, c in sorted(counts.items(), key=lambda x: -x[1])
        ]
        missing_count = counts.get("__missing__", 0)
        return BreakdownResult(
            label=label,
            items=items,
            total=float(len(self.wos)),
            data_quality=_quality_rating(len(self.wos) - missing_count, missing_count),
            available_count=len(self.wos) - missing_count,
            missing_count=missing_count,
        )

    # -- Summary for API consumption ----------------------------------------

    def summary(self) -> Dict[str, Any]:
        return {
            "total_work_orders": len(self.wos),
            "total_wo_value": _to_dict(self.total_wo_value()),
            "total_billed_value": _to_dict(self.total_billed_value()),
            "total_collected": _to_dict(self.total_collected()),
            "total_to_be_billed": _to_dict(self.total_to_be_billed()),
            "total_receivable": _to_dict(self.total_receivable()),
            "billing_status": _breakdown_to_dict(self.billing_status_distribution()),
            "collection_status": _breakdown_to_dict(self.collection_status_distribution()),
        }
