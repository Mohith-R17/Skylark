"""
Data loading service — orchestrates adapter → normalization → analytics.

Selects the appropriate adapter based on configuration and provides
a unified interface for the API layer.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from models.deal import DataQualityIssue, Deal
from models.work_order import WorkOrder
from services.adapters.base import DataAdapter
from services.adapters.excel_adapter import ExcelAdapter, InMemoryAdapter
from services.adapters.monday_adapter import MondayAdapter
from services.analytics.pipeline import PipelineAnalytics
from services.analytics.revenue import RevenueAnalytics
from services.analytics.operations import OperationsAnalytics
from services.analytics.cross_board import CrossBoardAnalytics


class DataService:
    """
    Central data service — loads data through the configured adapter
    and runs analytics.
    """

    def __init__(self, adapter: Optional[DataAdapter] = None) -> None:
        self.adapter = adapter or _auto_select_adapter()
        self._deals: Optional[List[Deal]] = None
        self._work_orders: Optional[List[WorkOrder]] = None
        self._deal_issues: List[DataQualityIssue] = []
        self._wo_issues: List[DataQualityIssue] = []

    async def load(self) -> None:
        """Load data from the adapter. Call once at startup or on refresh."""
        self._deals, self._deal_issues = await self.adapter.load_deals()
        self._work_orders, self._wo_issues = await self.adapter.load_work_orders()

    @property
    def deals(self) -> List[Deal]:
        return self._deals or []

    @property
    def work_orders(self) -> List[WorkOrder]:
        return self._work_orders or []

    @property
    def all_issues(self) -> List[DataQualityIssue]:
        return self._deal_issues + self._wo_issues

    def pipeline_analytics(self) -> PipelineAnalytics:
        return PipelineAnalytics(self.deals)

    def revenue_analytics(self) -> RevenueAnalytics:
        return RevenueAnalytics(self.work_orders)

    def operations_analytics(self) -> OperationsAnalytics:
        return OperationsAnalytics(self.work_orders)

    def cross_board_analytics(self) -> CrossBoardAnalytics:
        return CrossBoardAnalytics(self.deals, self.work_orders)

    def full_summary(self) -> Dict[str, Any]:
        """Complete analytics summary across all domains."""
        return {
            "source": self.adapter.source_name(),
            "data": {
                "total_deals": len(self.deals),
                "total_work_orders": len(self.work_orders),
                "data_quality_issues": len(self.all_issues),
            },
            "pipeline": self.pipeline_analytics().summary(),
            "revenue": self.revenue_analytics().summary(),
            "operations": self.operations_analytics().summary(),
            "cross_board": self.cross_board_analytics().summary(),
        }

    def data_quality_summary(self) -> Dict[str, Any]:
        """Data quality report."""
        deal_issues = [{"field": i.field, "message": i.message, "severity": i.severity}
                       for i in self._deal_issues]
        wo_issues = [{"field": i.field, "message": i.message, "severity": i.severity}
                     for i in self._wo_issues]
        return {
            "total_issues": len(self.all_issues),
            "deal_issues": deal_issues,
            "wo_issues": wo_issues,
            "deal_count": len(self.deals),
            "wo_count": len(self.work_orders),
        }


def _auto_select_adapter() -> DataAdapter:
    """
    Select adapter based on environment:
    - If MONDAY_API_TOKEN is set → MondayAdapter
    - If SKYLARK_DEALS_PATH / SKYLARK_WO_PATH are set → ExcelAdapter
    - Otherwise → InMemoryAdapter (empty, for dev)
    """
    if os.getenv("MONDAY_API_TOKEN"):
        return MondayAdapter()

    deals_path = os.getenv("SKYLARK_DEALS_PATH")
    wo_path = os.getenv("SKYLARK_WO_PATH")
    if deals_path or wo_path:
        return ExcelAdapter(deals_path=deals_path, work_orders_path=wo_path)

    return InMemoryAdapter()
