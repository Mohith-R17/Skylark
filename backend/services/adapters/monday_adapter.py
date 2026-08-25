"""
monday.com adapter stub — production data source.

This adapter connects to the monday.com GraphQL API to dynamically
fetch Deals and Work Order data. Column ID mappings are configurable
via environment variables.

NOT YET IMPLEMENTED — requires monday.com API token and board IDs.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from models.deal import DataQualityIssue, Deal
from models.work_order import WorkOrder
from services.adapters.base import DataAdapter


# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN", "")
MONDAY_DEALS_BOARD_ID = os.getenv("MONDAY_DEALS_BOARD_ID", "")
MONDAY_WO_BOARD_ID = os.getenv("MONDAY_WO_BOARD_ID", "")
MONDAY_API_URL = os.getenv("MONDAY_API_URL", "https://api.monday.com/v2")

# Column ID → normalized field name mappings (configurable per board)
# These MUST be configured based on the actual monday.com board structure.
# Do not assume column IDs without evidence.
MONDAY_DEAL_COLUMN_MAP: Dict[str, str] = {
    # "column_id_here": "name",
    # "column_id_here": "owner",
    # ... to be configured when monday.com access is available
}

MONDAY_WO_COLUMN_MAP: Dict[str, str] = {
    # "column_id_here": "deal_reference",
    # "column_id_here": "customer",
    # ... to be configured when monday.com access is available
}


class MondayAdapter(DataAdapter):
    """
    Production adapter for monday.com.

    Requires:
    - MONDAY_API_TOKEN environment variable
    - MONDAY_DEALS_BOARD_ID and MONDAY_WO_BOARD_ID environment variables
    - Column ID mappings configured in MONDAY_DEAL_COLUMN_MAP / MONDAY_WO_COLUMN_MAP

    Until configured, this adapter returns empty data with a clear error.
    """

    def source_name(self) -> str:
        return "monday.com (production)"

    def _is_configured(self) -> bool:
        return bool(MONDAY_API_TOKEN and MONDAY_DEALS_BOARD_ID and MONDAY_WO_BOARD_ID)

    async def load_deals(self) -> Tuple[List[Deal], List[DataQualityIssue]]:
        if not self._is_configured():
            return [], [DataQualityIssue(
                field="__source__",
                message="monday.com adapter not configured. Set MONDAY_API_TOKEN, MONDAY_DEALS_BOARD_ID, MONDAY_WO_BOARD_ID environment variables.",
                raw_value=None,
                severity="error",
            )]
        # TODO: Implement monday.com GraphQL query
        # query = '''
        # {
        #   boards(ids: [BOARD_ID]) {
        #     items_page(limit: 500) {
        #       items {
        #         id
        #         name
        #         column_values {
        #           id
        #           text
        #           value
        #         }
        #       }
        #     }
        #   }
        # }
        # '''
        return [], [DataQualityIssue(
            field="__source__",
            message="monday.com deal loading not yet implemented",
            raw_value=None,
            severity="info",
        )]

    async def load_work_orders(self) -> Tuple[List[WorkOrder], List[DataQualityIssue]]:
        if not self._is_configured():
            return [], [DataQualityIssue(
                field="__source__",
                message="monday.com adapter not configured. Set MONDAY_API_TOKEN, MONDAY_DEALS_BOARD_ID, MONDAY_WO_BOARD_ID environment variables.",
                raw_value=None,
                severity="error",
            )]
        # TODO: Implement monday.com GraphQL query
        return [], [DataQualityIssue(
            field="__source__",
            message="monday.com WO loading not yet implemented",
            raw_value=None,
            severity="info",
        )]
