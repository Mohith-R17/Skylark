# data-resilience/SKILL.md

## Robust Data Handling Standards

### Null/Undefined Handling
- Never render undefined directly - default to null or empty state
- All components must handle null/undefined prop gracefully
- Default values at the API layer, not just frontend

### Date Normalization
- All dates ISO 8601 format from API: YYYY-MM-DD or ISO string
- Client-side: convert to consistent format for display
- Flag: dates older than 2 years get "last updated" badge
- Reject dates outside reasonable range (1900-2100)

### Naming Conventions
- snake_case for API fields, camelCase for React state/props
- Consistent prefix/suffix for status fields: `status_` prefix
- Enum values standardized at source, not scattered

### Status Normalization
- Standard statuses: `active`, `inactive`, `pending`, `archived`, `error`
- Map non-standard Monday.com statuses to canonical set
- Never display raw status codes - always human-readable

### Numeric Value Normalization
- Round to 2 decimal places for currency, 1 for percentages
- Null → 0 with explicit flag, or null with warning badge
- Prevent NaN propagation: guard all math operations
- Large numbers: format with abbreviations K/M/B, consistent precision

### Data-Quality Warnings
- Schema validation on ingest: required fields, type checks
- Warnings collection: attach to records, don't block display
- Visible indicators: yellow banner for warnings, red for critical
- Summary count at top of tables: "3 records have warnings"

### Monday.com Integration Specifics
- Item IDs: store as strings, parse to int only when needed
- Column values: map Monday column types to internal types
- Timestamps: Monday sends mixed formats, normalize on receipt
- Failure gracefully: if Monday API changes format, degrade gracefully, don't crash

### Error Shapes
```
{
  field: string,
  message: string,
  value: any, // raw problematic value
  severity: "warning" | "critical"
}
```