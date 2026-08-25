from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.deal import DataQualityIssue


class WorkOrder(BaseModel):
    """Normalized WorkOrder model - independent of Excel column names."""

    id: Optional[str] = None
    deal_reference: Optional[str] = None  # e.g. SDPLDEAL-075
    customer: Optional[str] = None
    serial_number: Optional[str] = None
    nature_of_work: Optional[str] = None
    execution_status: Optional[str] = None
    delivery_date: Optional[date] = None
    po_loi_date: Optional[date] = None
    document_type: Optional[str] = None
    probable_start_date: Optional[date] = None
    probable_end_date: Optional[date] = None
    owner: Optional[str] = None
    sector: Optional[str] = None
    work_type: Optional[str] = None
    billing_status: Optional[str] = None
    collection_status: Optional[str] = None
    wo_status: Optional[str] = None
    quantity_by_ops: Optional[int] = None
    quantities_as_per_po: Optional[int] = None
    quantity_billed_till_date: Optional[int] = None
    balance_in_quantity: Optional[int] = None
    receivable: Optional[float] = None
    ar_priority_account: Optional[str] = None
    po_latest_invoice_no: Optional[str] = None
    last_invoice_date: Optional[date] = None

    # Billing / collection money values (masked/raw)
    amount_excl_gst: Optional[float] = None
    amount_incl_gst: Optional[float] = None
    billed_value_excl_gst: Optional[float] = None
    billed_value_incl_gst: Optional[float] = None
    collected_amount_incl_gst: Optional[float] = None
    amount_to_be_billed_excl_gst: Optional[float] = None
    amount_to_be_billed_incl_gst: Optional[float] = None
    amount_receivable: Optional[float] = None

    # Quality flags
    normalization_flags: dict = Field(default_factory=dict)

    @field_validator("execution_status", mode="before")
    @classmethod
    def validate_execution_status(cls, v: Any) -> Any:
        if v is None:
            return None
        v = str(v).strip()
        # Normalize month names
        month_map = {
            "jan": "January", "feb": "February", "mar": "March", "apr": "April",
            "may": "May", "jun": "June", "jul": "July", "aug": "August",
            "sep": "September", "oct": "October", "nov": "November", "dec": "December",
        }
        v_lower = v.lower()
        if v_lower in month_map and len(v_lower) <= 3:
            v = month_map[v_lower]
        return v

    @field_validator("wo_status", mode="before")
    @classmethod
    def validate_wo_status(cls, v: Any) -> Any:
        if v is None:
            return None
        v = str(v).strip().lower()
        if v in {"completed", "c"}:
            return "Completed"
        if v in {"not started", "ns"}:
            return "Not Started"
        if v in {"executed", "e"}:
            return "Executed"
        if v in {"open", "o"}:
            return "Open"
        return v

    @field_validator("billing_status", mode="before")
    @classmethod
    def validate_billing_status(cls, v: Any) -> Any:
        if v is None:
            return None
        v = str(v).strip().lower()
        if v in {"fully billed", "fb"}:
            return "Fully Billed"
        if v in {"partially billed", "pb"}:
            return "Partially Billed"
        if v in {"not billed", "nb"}:
            return "Not Billed"
        return v

    @field_validator("collection_status", mode="before")
    @classmethod
    def validate_collection_status(cls, v: Any) -> Any:
        if v is None:
            return None
        v = str(v).strip().lower()
        if v in {"collected", "c"}:
            return "Collected"
        if v in {"partially collected", "pc"}:
            return "Partially Collected"
        if v in {"not collected", "nc"}:
            return "Not Collected"
        if v in {"update required", "ur"}:
            return "Update Required"
        return v

    def is_missing_required(self) -> bool:
        """Check if essential fields are missing."""
        return (
            self.deal_reference is None
            and self.customer is None
            and self.nature_of_work is None
        )

    def has_delivery_date(self) -> bool:
        return self.delivery_date is not None

    def has_po_loi_date(self) -> bool:
        return self.po_loi_date is not None


class NormalizedWorkOrder(BaseModel):
    """Fully normalized WorkOrder ready for analytics."""

    id: Optional[str] = None
    deal_reference: Optional[str] = None
    customer: Optional[str] = None
    serial_number: Optional[str] = None
    nature_of_work: Optional[str] = None
    execution_status: Optional[str] = None
    delivery_date: Optional[date] = None
    po_loi_date: Optional[date] = None
    document_type: Optional[str] = None
    probable_start_date: Optional[date] = None
    probable_end_date: Optional[date] = None
    owner: Optional[str] = None
    sector: Optional[str] = None
    work_type: Optional[str] = None
    wo_status: Optional[str] = None
    billing_status: Optional[str] = None
    collection_status: Optional[str] = None
    quantity_by_ops: Optional[int] = None
    quantities_as_per_po: Optional[int] = None
    quantity_billed_till_date: Optional[int] = None
    balance_in_quantity: Optional[int] = None
    receivable: Optional[float] = None
    ar_priority_account: Optional[str] = None
    po_latest_invoice_no: Optional[str] = None
    last_invoice_date: Optional[date] = None
    amount_excl_gst: Optional[float] = None
    amount_incl_gst: Optional[float] = None
    billed_value_excl_gst: Optional[float] = None
    billed_value_incl_gst: Optional[float] = None
    collected_amount_incl_gst: Optional[float] = None
    amount_to_be_billed_excl_gst: Optional[float] = None
    amount_to_be_billed_incl_gst: Optional[float] = None
    amount_receivable: Optional[float] = None

    # Quality flags
    missing_deal_ref: bool = False
    missing_customer: bool = False
    missing_nature_of_work: bool = False
    missing_delivery_date: bool = False
    missing_po_loi_date: bool = False
    missing_receivable: bool = False
    statuses_normalized: bool = False

    def has_critical_missing(self) -> bool:
        return self.missing_deal_ref or self.missing_customer or self.missing_nature_of_work

    def is_fully_qualified(self) -> bool:
        """Check if WO has all essential data for reporting."""
        return (
            self.deal_reference is not None
            and self.customer is not None
            and self.nature_of_work is not None
            and self.delivery_date is not None
            and self.po_loi_date is not None
        )


def normalize_work_order(raw: dict) -> tuple[NormalizedWorkOrder, list[DataQualityIssue]]:
    """
    Convert raw dict (from Excel/monday) into NormalizedWorkOrder
    with DataQualityIssue tracking.
    """
    issues: list[DataQualityIssue] = []

    # Deal reference
    deal_ref = raw.get("deal_reference") or raw.get("Deal name masked") or raw.get("SDPLDEAL")
    if deal_ref is not None:
        deal_ref = str(deal_ref).strip()
    else:
        deal_ref = None
        issues.append(
            DataQualityIssue(
                field="deal_reference",
                message="Deal reference is missing",
                raw_value=raw.get("deal_reference"),
                severity="warning",
            )
        )

    # Customer
    customer = raw.get("customer") or raw.get("Customer Name Code")
    if customer is not None:
        customer = str(customer).strip()
    else:
        customer = None
        issues.append(
            DataQualityIssue(field="customer", message="Customer is missing", raw_value=raw.get("customer"), severity="warning")
        )

    # Serial number
    serial = raw.get("serial_number") or raw.get("Serial #")
    if serial is not None:
        serial = str(serial).strip()
    else:
        serial = None

    # Nature of work
    nature = raw.get("nature_of_work") or raw.get("Nature of Work")
    if nature is not None:
        nature = str(nature).strip()
    else:
        nature = None
        issues.append(
            DataQualityIssue(field="nature_of_work", message="Nature of work is missing", raw_value=raw.get("nature_of_work"), severity="warning")
        )

    # Execution status
    exec_status = raw.get("execution_status") or raw.get("Execution Status")
    if exec_status is not None:
        exec_status = str(exec_status).strip()
    else:
        exec_status = None

    # Delivery date
    delivery_date = None
    delivery_raw = raw.get("delivery_date") or raw.get("Data Delivery Date")
    if delivery_raw is not None:
        try:
            delivery_date = parse_date(delivery_raw)
        except (ValueError, TypeError):
            delivery_date = None

    # PO/LOI date
    poi_date = None
    poi_raw = raw.get("po_loi_date") or raw.get("Date of PO/LOI")
    if poi_raw is not None:
        try:
            poi_date = parse_date(poi_raw)
        except (ValueError, TypeError):
            poi_date = None

    # Document type
    doc_type = raw.get("document_type") or raw.get("Document Type")
    if doc_type is not None:
        doc_type = str(doc_type).strip()
    else:
        doc_type = None

    # Probable start/end dates
    start_date = None
    end_date = None
    start_raw = raw.get("probable_start_date") or raw.get("Probable Start Date")
    end_raw = raw.get("probable_end_date") or raw.get("Probable End Date")
    if start_raw is not None:
        try:
            start_date = parse_date(start_raw)
        except (ValueError, TypeError):
            start_date = None
    if end_raw is not None:
        try:
            end_date = parse_date(end_raw)
        except (ValueError, TypeError):
            end_date = None

    # Owner
    owner = raw.get("owner") or raw.get("BD/KAM Personnel code")
    if owner is not None:
        owner = str(owner).strip()
    else:
        owner = None

    # Sector
    sector = raw.get("sector") or raw.get("Sector")
    if sector is not None:
        sector = str(sector).strip()
    else:
        sector = None

    # Work type
    work_type = raw.get("work_type") or raw.get("Type of Work")
    if work_type is not None:
        work_type = str(work_type).strip()
    else:
        work_type = None

    # WO Status (billed)
    wo_status = raw.get("wo_status") or raw.get("WO Status (billed)")
    if wo_status is not None:
        wo_status = str(wo_status).strip().lower()
        if wo_status in {"completed", "c"}:
            wo_status = "Completed"
        elif wo_status in {"not started", "ns"}:
            wo_status = "Not Started"
        elif wo_status in {"executed", "e"}:
            wo_status = "Executed"
        elif wo_status in {"open", "o"}:
            wo_status = "Open"
    else:
        wo_status = None

    # Billing status
    billing_status = raw.get("billing_status") or raw.get("Billing Status")
    if billing_status is not None:
        billing_status = str(billing_status).strip().lower()
        if billing_status in {"fully billed", "fb"}:
            billing_status = "Fully Billed"
        elif billing_status in {"partially billed", "pb"}:
            billing_status = "Partially Billed"
        elif billing_status in {"not billed", "nb"}:
            billing_status = "Not Billed"
    else:
        billing_status = None

    # Collection status
    collection_status = raw.get("collection_status") or raw.get("Collection status")
    if collection_status is not None:
        collection_status = str(collection_status).strip().lower()
        if collection_status in {"collected", "c"}:
            collection_status = "Collected"
        elif collection_status in {"partially collected", "pc"}:
            collection_status = "Partially Collected"
        elif collection_status in {"not collected", "nc"}:
            collection_status = "Not Collected"
        elif collection_status in {"update required", "ur"}:
            collection_status = "Update Required"
    else:
        collection_status = None

    # Quantities
    qty_by_ops = raw.get("quantity_by_ops") or raw.get("Quantity by Ops")
    qty_by_ops_int = None
    if qty_by_ops is not None:
        try:
            qty_by_ops_int = int(qty_by_ops)
        except (ValueError, TypeError):
            qty_by_ops_int = None

    qty_po = raw.get("quantities_as_per_po") or raw.get("Quantities as per PO")
    qty_po_int = None
    if qty_po is not None:
        try:
            qty_po_int = int(qty_po)
        except (ValueError, TypeError):
            qty_po_int = None

    qty_billed = raw.get("quantity_billed_till_date") or raw.get("Quantity billed (till date)")
    qty_billed_int = None
    if qty_billed is not None:
        try:
            qty_billed_int = int(qty_billed)
        except (ValueError, TypeError):
            qty_billed_int = None

    balance = raw.get("balance_in_quantity") or raw.get("Balance in quantity")
    balance_int = None
    if balance is not None:
        try:
            balance_int = int(balance)
        except (ValueError, TypeError):
            balance_int = None

    # Money values (masked)
    amount_excl = raw.get("amount_excl_gst") or raw.get("Amount in Rupees (Excl of GST) (Masked)")
    amount_excl_float = None
    if amount_excl is not None:
        try:
            amount_excl_float = float(amount_excl)
        except (ValueError, TypeError):
            amount_excl_float = None

    amount_incl = raw.get("amount_incl_gst") or raw.get("Amount in Rupees (Incl of GST) (Masked)")
    amount_incl_float = None
    if amount_incl is not None:
        try:
            amount_incl_float = float(amount_incl)
        except (ValueError, TypeError):
            amount_incl_float = None

    billed_excl = raw.get("billed_value_excl_gst") or raw.get("Billed Value in Rupees (Excl of GST.) (Masked)")
    billed_excl_float = None
    if billed_excl is not None:
        try:
            billed_excl_float = float(billed_excl)
        except (ValueError, TypeError):
            billed_excl_float = None

    billed_incl = raw.get("billed_value_incl_gst") or raw.get("Billed Value in Rupees (Incl of GST.) (Masked)")
    billed_incl_float = None
    if billed_incl is not None:
        try:
            billed_incl_float = float(billed_incl)
        except (ValueError, TypeError):
            billed_incl_float = None

    collected = raw.get("collected_amount_incl_gst") or raw.get("Collected Amount in Rupees (Incl of GST.) (Masked)")
    collected_float = None
    if collected is not None:
        try:
            collected_float = float(collected)
        except (ValueError, TypeError):
            collected_float = None

    amount_to_billed_excl = raw.get("amount_to_be_billed_excl_gst") or raw.get("Amount to be billed in Rs. (Exl. of GST) (Masked)")
    amount_to_billed_excl_float = None
    if amount_to_billed_excl is not None:
        try:
            amount_to_billed_excl_float = float(amount_to_billed_excl)
        except (ValueError, TypeError):
            amount_to_billed_excl_float = None

    amount_to_billed_incl = raw.get("amount_to_be_billed_incl_gst") or raw.get("Amount to be billed in Rs. (Incl of GST) (Masked)")
    amount_to_billed_incl_float = None
    if amount_to_billed_incl is not None:
        try:
            amount_to_billed_incl_float = float(amount_to_billed_incl)
        except (ValueError, TypeError):
            amount_to_billed_incl_float = None

    amount_receivable_raw = raw.get("amount_receivable") or raw.get("Amount Receivable (Masked)")
    amount_receivable_float = None
    if amount_receivable_raw is not None:
        try:
            amount_receivable_float = float(amount_receivable_raw)
        except (ValueError, TypeError):
            amount_receivable_float = None

    ar_priority = raw.get("ar_priority_account") or raw.get("AR Priority account")
    if ar_priority is not None:
        ar_priority = str(ar_priority).strip()
    else:
        ar_priority = None

    po_latest_invoice = raw.get("po_latest_invoice_no") or raw.get("Latest invoice no.")
    if po_latest_invoice is not None:
        po_latest_invoice = str(po_latest_invoice).strip()
    else:
        po_latest_invoice = None

    last_inv_date = None
    last_inv_raw = raw.get("last_invoice_date") or raw.get("Last invoice date")
    if last_inv_raw is not None:
        try:
            last_inv_date = parse_date(last_inv_raw)
        except (ValueError, TypeError):
            last_inv_date = None

    # Build NormalizedWorkOrder
    normalized = NormalizedWorkOrder(
        id=raw.get("id"),
        deal_reference=deal_ref,
        customer=customer,
        serial_number=serial,
        nature_of_work=nature,
        execution_status=exec_status,
        delivery_date=delivery_date,
        po_loi_date=poi_date,
        document_type=doc_type,
        probable_start_date=start_date,
        probable_end_date=end_date,
        owner=owner,
        sector=sector,
        work_type=work_type,
        wo_status=wo_status,
        billing_status=billing_status,
        collection_status=collection_status,
        quantity_by_ops=qty_by_ops_int,
        quantities_as_per_po=qty_po_int,
        quantity_billed_till_date=qty_billed_int,
        balance_in_quantity=balance_int,
        receivable=amount_receivable_float,
        ar_priority_account=ar_priority,
        po_latest_invoice_no=po_latest_invoice,
        last_invoice_date=last_inv_date,
        amount_excl_gst=amount_excl_float,
        amount_incl_gst=amount_incl_float,
        billed_value_excl_gst=billed_excl_float,
        billed_value_incl_gst=billed_incl_float,
        collected_amount_incl_gst=collected_float,
        amount_to_be_billed_excl_gst=amount_to_billed_excl_float,
        amount_to_be_billed_incl_gst=amount_to_billed_incl_float,
        amount_receivable=amount_receivable_float,
        # Quality flags
        missing_deal_ref=deal_ref is None,
        missing_customer=customer is None,
        missing_nature_of_work=nature is None,
        missing_delivery_date=delivery_date is None,
        missing_po_loi_date=poi_date is None,
        missing_receivable=amount_receivable_float is None,
        statuses_normalized=bool(
            wo_status is not None or billing_status is not None or collection_status is not None
        ),
    )

    return normalized, issues


def parse_date(value: object) -> date:
    """Parse a date from various possible formats."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        raise ValueError(f"Cannot parse date from: {s}")