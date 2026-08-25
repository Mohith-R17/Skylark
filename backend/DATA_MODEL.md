# Skylark Drones — Data Model

## 1. Source Datasets

The hackathon provides two datasets that will ultimately be imported into separate monday.com boards:

- Deal funnel Data.xlsx
- Work_Order_Tracker Data.xlsx

The Excel files are development/reference inputs only. The final application must query monday.com dynamically and must not hardcode these records.

---

## 2. Deals Dataset

Dataset size: 346 rows × 12 columns.

### Raw fields

| Field | Type | Missing |
|---|---|---:|
| Deal Name | Text | 2 |
| Owner code | Text | 17 |
| Client Code | Text | 2 |
| Deal Status | Text | 1 |
| Close Date (A) | Date | 318 |
| Closure Probability | Text | 258 |
| Masked Deal value | Numeric | 181 |
| Tentative Close Date | Date | 74 |
| Deal Stage | Text | 170 |
| Product deal | Text | 170 |
| Sector/service | Text | 8 |
| Created Date | Date | 1 |

### Normalized Deal

The application should internally represent a deal using normalized fields:

- id / deal name
- owner
- client
- status
- close_date
- tentative_close_date
- closure_probability
- deal_value
- stage
- product
- sector
- created_date

The exact mapping must remain configurable because monday.com column IDs/names may differ from the Excel representation.

---

## 3. Work Orders Dataset

Dataset size: 177 rows × 38 columns.

The source workbook contains generic/unnamed spreadsheet column labels in some parsing contexts, while the actual business headers are present in the worksheet.

### Raw business fields

- Deal name masked
- Customer Name Code
- Serial #
- Nature of Work
- Last executed month of recurring project
- Execution Status
- Data Delivery Date
- Date of PO/LOI
- Document Type
- Probable Start Date
- Probable End Date
- BD/KAM Personnel code
- Sector
- Type of Work
- Is any Skylark software platform part of the client deliverables in this deal?
- Last invoice date
- latest invoice no.
- Amount in Rupees (Excl of GST) (Masked)
- Amount in Rupees (Incl of GST) (Masked)
- Billed Value in Rupees (Excl of GST.) (Masked)
- Billed Value in Rupees (Incl of GST.) (Masked)
- Collected Amount in Rupees (Incl of GST.) (Masked)
- Amount to be billed in Rs. (Exl. of GST) (Masked)
- Amount to be billed in Rs. (Incl. of GST) (Masked)
- Amount Receivable (Masked)
- AR Priority account
- Quantity by Ops
- Quantities as per PO
- Quantity billed (till date)
- Balance in quantity
- Invoice Status
- Expected Billing Month
- Actual Billing Month
- Actual Collection Month
- WO Status (billed)
- Collection status
- Collection Date
- Billing Status

### Normalized WorkOrder

The internal model should support:

- id
- deal_reference
- customer
- serial_number
- nature_of_work
- execution_status
- data_delivery_date
- po_loi_date
- document_type
- probable_start_date
- probable_end_date
- owner
- sector
- work_type
- software_included
- last_invoice_date
- latest_invoice_number
- total_value_excl_gst
- total_value_incl_gst
- billed_value_excl_gst
- billed_value_incl_gst
- collected_amount
- amount_to_be_billed_excl_gst
- amount_to_be_billed_incl_gst
- amount_receivable
- ar_priority
- quantity_ops
- quantity_po
- quantity_billed
- balance_quantity
- invoice_status
- expected_billing_month
- actual_billing_month
- actual_collection_month
- wo_status
- collection_status
- collection_date
- billing_status

---

## 4. DataQualityIssue

Every detected data problem should be representable using:

- dataset
- record_id
- field
- issue_type
- original_value
- normalized_value
- severity
- description
- resolution

Possible issue types:

- missing
- invalid
- inconsistent
- duplicate
- normalized
- inferred

The system must not silently invent missing business values.

---

## 5. Normalization Rules

### Missing values

Missing values remain explicitly missing.

Do not replace missing business values with arbitrary defaults such as:

- 0
- Unknown
- current date

unless the metric specifically requires a documented treatment.

### Dates

Normalize valid date values to a consistent internal representation.

Invalid or unparseable dates should generate a data-quality issue.

### Numeric values

Currency and quantity fields should be converted to numeric values after removing formatting where appropriate.

Invalid numeric values should be reported rather than silently converted.

### Statuses

Statuses should be normalized into canonical internal values while preserving the original source value.

### Text

Text comparisons should normalize whitespace and casing where appropriate.

Original values should remain available for traceability.

### Duplicate detection

Potential duplicates should be detected using stable identifiers where available and combinations of business fields where necessary.

Potential duplicates should be reported rather than automatically deleted.

---

## 6. Cross-Board Relationship

The Deals and Work Orders datasets contain deal/customer-related identifiers.

The application must investigate the reliability of:

1. Deal name / masked deal identifier
2. Customer/company identifier
3. Other stable identifiers available from monday.com

No cross-board relationship should be assumed without validation.

The relationship strategy should support:

- primary relationship when a reliable identifier exists
- fallback matching when appropriate
- explicit "unmatched" state when no reliable relationship exists

Approximate/fuzzy matching must never silently create a business relationship.

---

## 7. Supported Business Metrics

Metrics should only be calculated when the underlying fields are available and sufficiently reliable.

### Pipeline

- Total pipeline value
- Weighted pipeline
- Pipeline by sector
- Pipeline by stage
- Pipeline by owner
- Pipeline by probability
- Deals missing close dates
- Deals missing probability

### Revenue / Billing

Where supported by Work Order fields:

- Total work order value
- Billed value
- Collected amount
- Amount to be billed
- Accounts receivable
- Billing status
- Collection status

### Operations

- Active work orders
- Work orders by execution status
- Work orders by sector
- Work orders by type
- Work orders by billing status
- Work orders by collection status
- Quantity planned versus billed where reliable

### Cross-board analysis

Potential examples:

- Pipeline compared with active work orders
- Pipeline by sector versus operational workload
- Customers with both pipeline and active work
- Deals with operational/billing risk

Every cross-board metric must clearly identify its relationship assumptions.

---

## 8. Data Quality Reporting

Data-quality warnings must be visible to the AI/business layer when they affect an answer.

Examples:

- "91% of deals are missing an actual close date."
- "Closure probability is missing for a large portion of deals."
- "Some work-order records cannot be reliably matched to deals."

The application should distinguish between:

- business insight
- data-quality warning
- assumption

---

## 9. Known Limitations

- The source data contains substantial missing values.
- Some fields are masked.
- Work Order spreadsheet headers require careful parsing.
- Cross-board relationships must be validated rather than assumed.
- Some business metrics may not be reliable when required fields are missing.
- monday.com column IDs and values may differ from the Excel representation.

---

## 10. Runtime Architecture

The final runtime data flow should be:

monday.com Deals Board
        |
        v
Deals Adapter
        |
        v
Normalization
        |
        +------------------+
                           |
monday.com Work Orders ----+
        |
        v
Work Order Adapter
        |
        v
Normalization
        |
        v
Analytics Engine
        |
        v
AI Business Intelligence Agent
        |
        v
Founder-facing answer

The Excel datasets are used for development and validation, but the production application must dynamically query monday.com.
