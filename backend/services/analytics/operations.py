"""
Operations analytics — work order operational metrics.
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


class OperationsAnalytics:
    """Compute operational metrics from WorkOrder list."""

    def __init__(self, work_orders: List[WorkOrder]) -> None:
        self.wos = work_orders

    def active_work_orders(self) -> MetricResult:
        """Count WOs with status indicating activity (not completed/closed)."""
        inactive = {"completed", "closed"}
        active = [w for w in self.wos if w.wo_status and w.wo_status.lower() not in inactive]
        no_status = [w for w in self.wos if w.wo_status is None]
        return MetricResult(
            label="Active Work Orders",
            value=len(active),
            unit="count",
            data_quality=_quality_rating(len(self.wos) - len(no_status), len(no_status)),
            caveat=f"{len(no_status)} WOs missing status" if no_status else "",
            available_count=len(self.wos) - len(no_status),
            missing_count=len(no_status),
        )

    def by_execution_status(self) -> BreakdownResult:
        return self._count_by("WOs by Execution Status", lambda w: w.execution_status)

    def by_sector(self) -> BreakdownResult:
        return self._count_by("WOs by Sector", lambda w: w.sector)

    def by_work_type(self) -> BreakdownResult:
        return self._count_by("WOs by Work Type", lambda w: w.work_type)

    def by_wo_status(self) -> BreakdownResult:
        return self._count_by("WOs by Status", lambda w: w.wo_status)

    def by_billing_status(self) -> BreakdownResult:
        return self._count_by("WOs by Billing Status", lambda w: w.billing_status)

    def by_collection_status(self) -> BreakdownResult:
        return self._count_by("WOs by Collection Status", lambda w: w.collection_status)

    def quantity_planned_vs_billed(self) -> Dict[str, Any]:
        """Compare quantity planned (as per PO) vs quantity billed, where both are available."""
        usable = [
            w for w in self.wos
            if w.quantities_as_per_po is not None and w.quantity_billed_till_date is not None
        ]
        missing = len(self.wos) - len(usable)
        total_planned = sum(w.quantities_as_per_po for w in usable)  # type: ignore
        total_billed = sum(w.quantity_billed_till_date for w in usable)  # type: ignore
        return {
            "label": "Quantity Planned vs Billed",
            "planned": total_planned,
            "billed": total_billed,
            "gap": total_planned - total_billed,
            "data_quality": _quality_rating(len(usable), missing),
            "caveat": f"{missing} WOs excluded (missing quantity data)" if missing else "",
            "available_count": len(usable),
            "missing_count": missing,
        }

    # -- Helpers ------------------------------------------------------------

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

    def summary(self) -> Dict[str, Any]:
        return {
            "total_work_orders": len(self.wos),
            "active_work_orders": _to_dict(self.active_work_orders()),
            "by_execution_status": _breakdown_to_dict(self.by_execution_status()),
            "by_sector": _breakdown_to_dict(self.by_sector()),
            "by_work_type": _breakdown_to_dict(self.by_work_type()),
            "by_wo_status": _breakdown_to_dict(self.by_wo_status()),
            "by_billing_status": _breakdown_to_dict(self.by_billing_status()),
            "by_collection_status": _breakdown_to_dict(self.by_collection_status()),
            "quantity_planned_vs_billed": self.quantity_planned_vs_billed(),
        }
