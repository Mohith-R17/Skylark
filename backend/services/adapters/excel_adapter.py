"""
Excel/CSV adapter for development and testing.

Reads the hackathon Excel datasets and normalizes them into domain models.
This adapter is used during development; production uses the monday.com adapter.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from models.deal import DataQualityIssue, Deal
from models.work_order import WorkOrder
from services.adapters.base import DataAdapter
from services.normalization.date_normalizer import normalize_date
from services.normalization.numeric_normalizer import normalize_currency, normalize_numeric
from services.normalization.text_normalizer import normalize_text


# ---------------------------------------------------------------------------
# Column mappings: Excel column name → normalized field name
# ---------------------------------------------------------------------------

DEAL_COLUMN_MAP: Dict[str, str] = {
    "Deal Name": "name",
    "Owner code": "owner",
    "Client Code": "client",
    "Deal Status": "status",
    "Close Date (A)": "close_date",
    "Closure Probability": "closure_probability",
    "Masked Deal value": "deal_value",
    "Tentative Close Date": "tentative_close_date",
    "Deal Stage": "stage",
    "Product deal": "product",
    "Sector/service": "sector",
    "Created Date": "created_date",
}

WORK_ORDER_COLUMN_MAP: Dict[str, str] = {
    "Deal name masked": "deal_reference",
    "Customer Name Code": "customer",
    "Serial #": "serial_number",
    "Nature of Work": "nature_of_work",
    "Execution Status": "execution_status",
    "Data Delivery Date": "delivery_date",
    "Date of PO/LOI": "po_loi_date",
    "Document Type": "document_type",
    "Probable Start Date": "probable_start_date",
    "Probable End Date": "probable_end_date",
    "BD/KAM Personnel code": "owner",
    "Sector": "sector",
    "Type of Work": "work_type",
    "Last invoice date": "last_invoice_date",
    "latest invoice no.": "po_latest_invoice_no",
    "Amount in Rupees (Excl of GST) (Masked)": "amount_excl_gst",
    "Amount in Rupees (Incl of GST) (Masked)": "amount_incl_gst",
    "Billed Value in Rupees (Excl of GST.) (Masked)": "billed_value_excl_gst",
    "Billed Value in Rupees (Incl of GST.) (Masked)": "billed_value_incl_gst",
    "Collected Amount in Rupees (Incl of GST.) (Masked)": "collected_amount_incl_gst",
    "Amount to be billed in Rs. (Exl. of GST) (Masked)": "amount_to_be_billed_excl_gst",
    "Amount to be billed in Rs. (Incl. of GST) (Masked)": "amount_to_be_billed_incl_gst",
    "Amount Receivable (Masked)": "amount_receivable",
    "AR Priority account": "ar_priority_account",
    "Quantity by Ops": "quantity_by_ops",
    "Quantities as per PO": "quantities_as_per_po",
    "Quantity billed (till date)": "quantity_billed_till_date",
    "Balance in quantity": "balance_in_quantity",
    "WO Status (billed)": "wo_status",
    "Collection status": "collection_status",
    "Billing Status": "billing_status",
}

# Date fields that need date parsing
DEAL_DATE_FIELDS = {"close_date", "tentative_close_date", "created_date"}
DEAL_NUMERIC_FIELDS = {"deal_value"}

WO_DATE_FIELDS = {"delivery_date", "po_loi_date", "probable_start_date", "probable_end_date", "last_invoice_date"}
WO_CURRENCY_FIELDS = {
    "amount_excl_gst", "amount_incl_gst",
    "billed_value_excl_gst", "billed_value_incl_gst",
    "collected_amount_incl_gst",
    "amount_to_be_billed_excl_gst", "amount_to_be_billed_incl_gst",
    "amount_receivable",
}
WO_INT_FIELDS = {"quantity_by_ops", "quantities_as_per_po", "quantity_billed_till_date", "balance_in_quantity"}


def _is_nan(val: Any) -> bool:
    """Check if a value is NaN (float)."""
    return isinstance(val, float) and val != val


def _normalize_row(row: Dict[str, Any], col_map: Dict[str, str],
                   date_fields: set, currency_fields: set, int_fields: set) -> Dict[str, Any]:
    """Map raw column names to normalized field names, applying type normalization."""
    normalized: Dict[str, Any] = {}
    for raw_col, norm_field in col_map.items():
        val = row.get(raw_col)
        if val is None or _is_nan(val):
            normalized[norm_field] = None
            continue
        if norm_field in date_fields:
            normalized[norm_field] = normalize_date(val)
        elif norm_field in currency_fields:
            normalized[norm_field] = normalize_currency(val)
        elif norm_field in int_fields:
            n = normalize_numeric(val)
            normalized[norm_field] = int(n) if n is not None else None
        else:
            normalized[norm_field] = normalize_text(str(val)) if val is not None else None
    return normalized


class ExcelAdapter(DataAdapter):
    """
    Load data from Excel files for development/testing.
    Requires openpyxl (already used by analyze_datasets.py).
    """

    def __init__(self, deals_path: Optional[str] = None, work_orders_path: Optional[str] = None) -> None:
        self.deals_path = deals_path
        self.work_orders_path = work_orders_path

    def source_name(self) -> str:
        return "Excel (development)"

    async def load_deals(self) -> Tuple[List[Deal], List[DataQualityIssue]]:
        if not self.deals_path or not Path(self.deals_path).exists():
            return [], [DataQualityIssue(
                field="__source__", message=f"Deal file not found: {self.deals_path}",
                raw_value=self.deals_path, severity="error",
            )]
        rows = _read_excel(self.deals_path)
        deals: List[Deal] = []
        issues: List[DataQualityIssue] = []
        for i, row in enumerate(rows):
            norm = _normalize_row(row, DEAL_COLUMN_MAP, DEAL_DATE_FIELDS, DEAL_NUMERIC_FIELDS, set())
            norm["id"] = norm.get("name") or f"deal-{i}"
            try:
                deal = Deal(**norm)
                deals.append(deal)
            except Exception as e:
                issues.append(DataQualityIssue(
                    field="__parse__", message=f"Row {i}: {e}",
                    raw_value=str(row)[:200], severity="error",
                ))
        return deals, issues

    async def load_work_orders(self) -> Tuple[List[WorkOrder], List[DataQualityIssue]]:
        if not self.work_orders_path or not Path(self.work_orders_path).exists():
            return [], [DataQualityIssue(
                field="__source__", message=f"WO file not found: {self.work_orders_path}",
                raw_value=self.work_orders_path, severity="error",
            )]
        rows = _read_excel(self.work_orders_path)
        wos: List[WorkOrder] = []
        issues: List[DataQualityIssue] = []
        for i, row in enumerate(rows):
            norm = _normalize_row(row, WORK_ORDER_COLUMN_MAP, WO_DATE_FIELDS, WO_CURRENCY_FIELDS, WO_INT_FIELDS)
            norm["id"] = norm.get("deal_reference") or f"wo-{i}"
            try:
                wo = WorkOrder(**norm)
                wos.append(wo)
            except Exception as e:
                issues.append(DataQualityIssue(
                    field="__parse__", message=f"Row {i}: {e}",
                    raw_value=str(row)[:200], severity="error",
                ))
        return wos, issues


class InMemoryAdapter(DataAdapter):
    """
    In-memory adapter for testing — accepts pre-built model lists directly.
    """

    def __init__(self, deals: Optional[List[Deal]] = None,
                 work_orders: Optional[List[WorkOrder]] = None) -> None:
        self._deals = deals or []
        self._work_orders = work_orders or []

    def source_name(self) -> str:
        return "In-Memory (test)"

    async def load_deals(self) -> Tuple[List[Deal], List[DataQualityIssue]]:
        return self._deals, []

    async def load_work_orders(self) -> Tuple[List[WorkOrder], List[DataQualityIssue]]:
        return self._work_orders, []


def _read_excel(path: str) -> List[Dict[str, Any]]:
    """Read an Excel file and return list of dicts (header → value)."""
    try:
        import openpyxl
    except ImportError:
        raise ImportError("openpyxl is required for Excel adapter. Install with: pip install openpyxl")

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    if ws is None:
        return []

    rows_iter = ws.iter_rows(values_only=False)
    
    header_row = None
    for row in rows_iter:
        if any(cell.value is not None and str(cell.value).strip() != '' for cell in row):
            header_row = row
            break
            
    if header_row is None:
        return []

    headers = [cell.value for cell in header_row]
    data: List[Dict[str, Any]] = []
    for row in rows_iter:
        row_dict: Dict[str, Any] = {}
        for header, cell in zip(headers, row):
            if header is not None:
                row_dict[str(header)] = cell.value
        data.append(row_dict)
    return data
