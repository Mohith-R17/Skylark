# Skylark

## Project Overview
Skylark is a modern executive dashboard and data-intelligence platform designed to aggregate, normalize, and analyze disparate business metrics across sales pipelines and operational workflows. It bridges the gap between CRM data and service delivery, giving leadership a holistic view of the organization's health.

## Problem Being Solved
Many organizations struggle with fragmented data. Sales teams track opportunities in a CRM, while delivery teams track active projects in separate operational tools. This siloing leads to:
- Misalignment between incoming revenue and operational capacity.
- Poor data hygiene where critical metrics (like close dates or probabilities) are missing.
- Leadership lacking a single pane of glass to ask questions and receive deterministic, data-backed answers.

Skylark solves this by acting as a central analytics hub, normalizing data from different sources and presenting it through a beautiful UI and an AI-driven executive assistant.

## Key Features
- **Executive Dashboard:** High-level metrics showing total pipeline, active work orders, and revenue realization.
- **Cross-Board Alignment:** Automatic reconciliation between CRM deals and operational work orders.
- **Data Health Monitoring:** Transparent reporting of missing or malformed data in source systems.
- **Ask Skylark (AI):** A natural-language interface that provides deterministic, computed metrics and "Leadership Updates" without inventing numbers.

## Architecture
Skylark follows a provider-agnostic, adapter-based architecture. 
- **Adapters (`DataAdapter`):** Ingest raw data from external systems (Excel or Monday.com) and convert it into standardized domain models (`Deal`, `WorkOrder`).
- **Data Service:** Acts as the centralized memory and source of truth, validating relationships and caching normalized data.
- **Analytics Modules:** Domain-specific services (`pipeline.py`, `operations.py`, `cross_board.py`) perform the business logic and computations.
- **API Layer:** FastAPI serves REST endpoints for the frontend.

## Tech Stack
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Recharts.
- **Backend:** Python 3.10+, FastAPI, Pydantic, Pytest.

## Data Flow
1. **Ingestion:** Raw data is pulled via `ExcelAdapter` (for the demo) or `MondayAdapter` (for production).
2. **Normalization:** Pydantic validators parse dates, standardize statuses, and flag missing required fields.
3. **Aggregation:** The `DataService` runs analytics modules to compute metrics (e.g., total pipeline value, active revenue).
4. **Presentation:** The React frontend fetches these JSON summaries and visualizes them. The Ask Skylark AI uses the same computed summaries to formulate natural-language responses.

## Ask Skylark Explanation
Ask Skylark is a deterministic AI assistant designed for leadership. Instead of allowing an LLM to hallucinate database queries, it uses robust keyword-intent routing. When a user asks about the "pipeline" or requests a "leadership update," the backend intercepts the intent, pulls the *exact computed metrics* from the Data Service, and generates a factual, data-backed response. 

## Analytics Explanation
The analytics engine is completely decoupled from the data source. It computes:
- **Pipeline:** Total value, open opportunities, and stage distributions.
- **Operations:** Active work orders, statuses, and delivery risks.
- **Cross-Board:** Identifying which work orders lack a corresponding CRM deal, highlighting rogue or untracked operational work.

## Data-Quality Handling
Data integrity is prioritized over interpolation. If a deal is missing a close date or a probability, it is not dropped or guessed. Instead, the backend flags it with a `DataQualityIssue`. The Data Health dashboard transparently presents these gaps to leadership (e.g., "320 deals missing close dates") so that CRM hygiene can be addressed.

## Demo Dataset / Offline Mode
**Important:** The current demo is configured to run in Offline Mode using the provided `Data.xlsx` datasets via the `ExcelAdapter`. 
This guarantees a reliable, fast, and verifiable demonstration without dependency on live external API rate limits or network issues. The `MondayAdapter` is fully built and ready for future production integration.

## Verified Results
The application is running against the actual provided datasets and yields the following verifiable metrics:
- **346** total deals
- **177** total work orders
- **$688.2M** open pipeline
- **$211.6M** work-order revenue
- **24** active work orders
- **35** backend tests passing successfully.
- **npm run build** completed successfully without errors.

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### How to Run Backend
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the FastAPI server: `uvicorn app:app --reload`
6. The backend will be available at `http://localhost:8000`.

### How to Run Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the Vite development server: `npm run dev`
4. The frontend will be available at `http://localhost:5173`.

### Environment Variables
Copy `backend/.env.example` to `backend/.env`. 
By default, the application uses the `ExcelAdapter` for the demo.

```ini
# .env
USE_MOCK_DATA=true
```

### Monday.com Configuration Instructions (Production)
To switch from the offline demo to a live Monday.com integration:
1. Open `backend/.env`
2. Set `USE_MOCK_DATA=false`
3. Provide your Monday.com API credentials and Board IDs:
```ini
MONDAY_API_TOKEN=your_token_here
MONDAY_CRM_BOARD_ID=your_crm_board_id
MONDAY_OPS_BOARD_ID=your_ops_board_id
```

### Testing Instructions
To run the complete backend test suite:
1. Ensure your virtual environment is active.
2. Navigate to `backend/`.
3. Run: `python -m pytest tests/`

### Demo Instructions
1. Start both the backend and frontend servers as described above.
2. Open `http://localhost:5173` in your browser.
3. Navigate the Overview dashboard to see the $688.2M pipeline.
4. Visit "Data Health" to view the 320 missing close dates transparently reported.
5. Visit "Ask Skylark" and ask: "Compare pipeline with active work orders" or "What data quality issues should leadership know about?".

### Production Limitations
- **In-Memory Data Store:** The current demo architecture aggregates data in-memory. For production deployments with millions of records, a persistent database (e.g., PostgreSQL) or caching layer (e.g., Redis) is required.
- **Historical Trending:** The pipeline trend graph relies on snapshots. A database is needed for robust historical time-series analytics.
