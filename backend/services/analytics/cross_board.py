"""
Cross-board analytics — correlating Deals with Work Orders.

Cross-board relationships are validated, not assumed.
Matching is based on explicit identifiers, never fuzzy-created silently.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from models.deal import Deal
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


@dataclass
class CrossBoardMatch:
    """A matched pair of Deal and Work Order(s)."""
    deal: Deal
    work_orders: List[WorkOrder]
    match_type: str  # "exact_deal_ref" | "client_code"


class CrossBoardAnalytics:
    """
    Analyze relationships between Deals and Work Orders.

    Matching strategy:
    1. Primary: match Deal.name with WorkOrder.deal_reference
    2. Fallback: match Deal.client with WorkOrder.customer
    3. Unmatched records are explicitly reported, never silently discarded.
    """

    def __init__(self, deals: List[Deal], work_orders: List[WorkOrder]) -> None:
        self.deals = deals
        self.wos = work_orders
        self._matches: Optional[Dict[str, CrossBoardMatch]] = None
        self._unmatched_deals: Optional[List[Deal]] = None
        self._unmatched_wos: Optional[List[WorkOrder]] = None

    def _compute_matches(self) -> None:
        if self._matches is not None:
            return

        self._matches = {}
        self._unmatched_deals = []
        self._unmatched_wos = []

        # Build WO lookup by deal_reference
        wo_by_deal_ref: Dict[str, List[WorkOrder]] = {}
        wo_by_customer: Dict[str, List[WorkOrder]] = {}
        matched_wo_indices: Set[int] = set()

        for i, w in enumerate(self.wos):
            if w.deal_reference:
                wo_by_deal_ref.setdefault(w.deal_reference.strip().lower(), []).append(w)
            if w.customer:
                wo_by_customer.setdefault(w.customer.strip().lower(), []).append(w)

        # Match deals
        for d in self.deals:
            matched = False
            deal_key = d.name.strip().lower() if d.name else None

            # Primary: exact deal name/reference match
            if deal_key and deal_key in wo_by_deal_ref:
                self._matches[deal_key] = CrossBoardMatch(
                    deal=d,
                    work_orders=wo_by_deal_ref[deal_key],
                    match_type="exact_deal_ref",
                )
                for w in wo_by_deal_ref[deal_key]:
                    idx = self.wos.index(w)
                    matched_wo_indices.add(idx)
                matched = True

            # Fallback: client code match (only if primary didn't match)
            if not matched and d.client:
                client_key = d.client.strip().lower()
                if client_key in wo_by_customer:
                    match_key = f"client:{client_key}:{d.name or 'unknown'}"
                    self._matches[match_key] = CrossBoardMatch(
                        deal=d,
                        work_orders=wo_by_customer[client_key],
                        match_type="client_code",
                    )
                    for w in wo_by_customer[client_key]:
                        idx = self.wos.index(w)
                        matched_wo_indices.add(idx)
                    matched = True

            if not matched:
                self._unmatched_deals.append(d)

        # Find unmatched WOs
        for i, w in enumerate(self.wos):
            if i not in matched_wo_indices:
                self._unmatched_wos.append(w)

    # -- Metrics ------------------------------------------------------------

    def match_summary(self) -> Dict[str, Any]:
        """Summary of cross-board matching results."""
        self._compute_matches()
        assert self._matches is not None
        assert self._unmatched_deals is not None
        assert self._unmatched_wos is not None

        exact_matches = sum(1 for m in self._matches.values() if m.match_type == "exact_deal_ref")
        client_matches = sum(1 for m in self._matches.values() if m.match_type == "client_code")

        return {
            "total_deals": len(self.deals),
            "total_work_orders": len(self.wos),
            "matched_pairs": len(self._matches),
            "exact_deal_ref_matches": exact_matches,
            "client_code_matches": client_matches,
            "unmatched_deals": len(self._unmatched_deals),
            "unmatched_work_orders": len(self._unmatched_wos),
            "data_quality": _quality_rating(
                len(self._matches),
                len(self._unmatched_deals) + len(self._unmatched_wos),
            ),
            "caveat": (
                f"{len(self._unmatched_deals)} deals and {len(self._unmatched_wos)} WOs "
                "could not be matched to each other"
                if self._unmatched_deals or self._unmatched_wos else ""
            ),
        }

    def pipeline_vs_active_wos(self) -> Dict[str, Any]:
        """Compare open pipeline deals against active work orders."""
        open_deals = [d for d in self.deals if d.status and d.status.lower() in ("open", "pending", "proposal", "negotiation")]
        inactive = {"completed", "closed"}
        active_wos = [w for w in self.wos if w.wo_status and w.wo_status.lower() not in inactive]
        return {
            "label": "Pipeline vs Active Work Orders",
            "open_deals": len(open_deals),
            "active_work_orders": len(active_wos),
            "ratio": round(len(active_wos) / len(open_deals), 2) if open_deals else None,
            "data_quality": "reliable",
        }

    def sector_overlap(self) -> Dict[str, Any]:
        """Compare sectors between deals and work orders."""
        deal_sectors = Counter(d.sector for d in self.deals if d.sector)
        wo_sectors = Counter(w.sector for w in self.wos if w.sector)
        all_sectors = sorted(set(deal_sectors.keys()) | set(wo_sectors.keys()))
        overlap = []
        for s in all_sectors:
            overlap.append({
                "sector": s,
                "deal_count": deal_sectors.get(s, 0),
                "wo_count": wo_sectors.get(s, 0),
            })
        return {
            "label": "Sector Overlap: Pipeline vs Operations",
            "sectors": overlap,
            "data_quality": "reliable",
        }

    def customers_with_both(self) -> Dict[str, Any]:
        """Find customers that appear in both pipeline and active work."""
        deal_clients = {d.client.strip().lower() for d in self.deals if d.client}
        wo_clients = {w.customer.strip().lower() for w in self.wos if w.customer}
        both = deal_clients & wo_clients
        return {
            "label": "Customers with Pipeline & Active Work",
            "count": len(both),
            "customers": sorted(both)[:20],  # cap preview
            "deal_only": len(deal_clients - wo_clients),
            "wo_only": len(wo_clients - deal_clients),
            "data_quality": "reliable",
        }

    def summary(self) -> Dict[str, Any]:
        return {
            "match_summary": self.match_summary(),
            "pipeline_vs_active_wos": self.pipeline_vs_active_wos(),
            "sector_overlap": self.sector_overlap(),
            "customers_with_both": self.customers_with_both(),
        }
