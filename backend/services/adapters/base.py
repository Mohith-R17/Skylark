"""
Abstract data adapter interface.

All data sources (Excel dev files, monday.com production) implement this
interface so the analytics engine is source-agnostic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from models.deal import DataQualityIssue, Deal
from models.work_order import WorkOrder


class DataAdapter(ABC):
    """Abstract base for loading raw board data and returning normalized models."""

    @abstractmethod
    async def load_deals(self) -> Tuple[List[Deal], List[DataQualityIssue]]:
        """Load and normalize deal data. Returns (deals, issues)."""
        ...

    @abstractmethod
    async def load_work_orders(self) -> Tuple[List[WorkOrder], List[DataQualityIssue]]:
        """Load and normalize work-order data. Returns (work_orders, issues)."""
        ...

    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name of this data source."""
        ...
