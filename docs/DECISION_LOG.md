# Skylark: Decision Log

This document details the key assumptions, architectural decisions, trade-offs, and design strategies implemented in the Skylark project.

## Key Assumptions
- **Provider Agnostic Core:** We assumed that while Monday.com is the eventual production system, the underlying data models and application logic must remain provider-agnostic. This ensures that the system is resilient and adaptable to different data sources.
- **Offline/Demo Reliability:** We assumed that depending solely on a live external API for demo and development purposes introduces unnecessary risk and latency. Therefore, a local Excel-based fallback is essential for consistent demonstrations.
- **Data Integrity Over Interpolation:** We assumed that missing or malformed data should be tracked and reported transparently rather than silently discarded or extrapolated. If a deal is missing a close date or value, it is explicitly flagged.

## Architecture / Design Decisions
- **Adapter Pattern for Data Ingestion:**
  We implemented the Adapter pattern (`DataAdapter` interface) to decouple data ingestion from business logic. The `ExcelAdapter` reads from local datasets, while the `MondayAdapter` interacts with Monday.com via GraphQL. Both adapters output standardized `Deal` and `WorkOrder` domain models.
- **Centralized Data Service:**
  The `DataService` acts as the single source of truth for the application. It aggregates data from the adapters, performs normalization, validates relationships (e.g., cross-board linking), and exposes aggregated summaries to the API.
- **Decoupled Analytics Modules:**
  Analytics logic is broken down into domain-specific modules (`pipeline.py`, `operations.py`, `cross_board.py`, `data_quality.py`). This separation of concerns makes the codebase highly testable and extensible.
- **React/Vite + FastAPI Stack:**
  We chose a modern React frontend with Vite for fast client-side performance, paired with a Python FastAPI backend for robust data processing and asynchronous API endpoints.

## Important Trade-offs and Why
- **Local Data vs. Live Monday.com Data for Demo:**
  *Trade-off:* Developing the demo around static Excel files instead of a live Monday.com board.
  *Why:* This ensures the application works offline, is immediately verifiable by judges, and does not fail due to rate limits, changing API credentials, or transient network issues. The Monday.com integration is built and ready for production, controlled simply via environment variables.
- **Aggregated Responses vs. Granular Deal Lookups in AI:**
  *Trade-off:* The Ask Skylark AI primarily returns aggregate data and top-level summaries rather than full individual deal profiles.
  *Why:* Returning large arrays of deals is visually overwhelming and can exceed typical LLM token limits or UI bounds. We group missing deals by name when stable unique IDs are not present (e.g., in the mock Excel data) to keep the UI legible.

## Data Quality / Missing Data Handling
- **Non-Destructive Normalization:** When data is ingested, it is normalized to standard formats (e.g., lowercase statuses, parsed dates). If a value is missing or invalid, the record is *not* dropped. Instead, it is flagged with a `DataQualityIssue`.
- **Transparent Reporting:** The backend tracks all normalization warnings and surfaces them via the `/api/data-quality` endpoint. The frontend explicitly displays these issues (e.g., "320 deals missing close dates", "177 missing work order statuses"), ensuring leadership is aware of CRM hygiene issues rather than presenting an artificially clean dashboard.

## AI / Ask Skylark Design
- **Deterministic Keyword Routing:**
  Instead of relying purely on an LLM to generate data or execute complex arbitrary queries against a database (which risks hallucination), Ask Skylark uses deterministic intent routing.
- **Data-Backed Responses:**
  Once an intent (e.g., "pipeline", "operations", "data quality", "cross-metric compare") is detected, the AI service injects *real, computed metrics* from the `DataService` into the response template.
- **No Hallucinations:**
  The AI will never invent business metrics. If the data is unavailable, it gracefully informs the user rather than guessing.

## How "Leadership Updates" Was Interpreted
- "Leadership Updates" are typically high-level, synthesized briefings that executives consume to understand the current state of the business instantly.
- We interpreted this feature as an AI-generated executive summary that pulls together the most critical metrics across all domains: Pipeline Health, Operational Status, Data Quality risks, and Cross-Board alignment.
- The output is structured as a clear, scannable briefing, avoiding deep technical jargon and focusing on actionable insights and immediate risks.

## What I Would Do Differently With More Time
- **Implement a Real Database Cache:** Currently, data is loaded into memory by the `DataService`. For production scale, I would implement a Redis cache or a PostgreSQL database to sync data from Monday.com periodically, enabling faster queries and persistent historical trending.
- **Advanced NLP Routing:** Upgrade the deterministic keyword routing in Ask Skylark to a semantic search or lightweight classification model (e.g., embedding-based routing) for better intent recognition on complex user queries.
- **Authentication & Authorization:** Add JWT-based user authentication and role-based access control (RBAC) so different leaders see dashboards tailored to their specific departments.

## Current Limitations
- **In-Memory Data Store:** The backend currently holds the dataset in memory. This works perfectly for the demo dataset sizes (hundreds of records) but will not scale to millions of records without a database backing.
- **Historical Data:** The `pipeline_trend` chart relies on available snapshot data. Without a persistent database tracking changes over time, deep historical trending is limited to what is explicitly provided in the datasets.
- **Stable Identifiers in Demo Data:** The provided demo Excel data uses the Deal Name as the ID, meaning IDs are not globally unique. The application handles this gracefully by grouping records, but production data from Monday.com will provide proper unique item IDs.
