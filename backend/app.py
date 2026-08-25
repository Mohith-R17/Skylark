"""
Skylark BI API — FastAPI application.

Provides REST endpoints for pipeline, revenue, operations, cross-board
analytics and data quality.  Data source is selected automatically via
environment variables (monday.com → Excel → InMemory).
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.data_service import DataService
from services.ai_service import AIService


from dotenv import load_dotenv
load_dotenv()

data_service = DataService()
ai_service = AIService(data_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data on startup."""
    await data_service.load()
    yield


app = FastAPI(
    title="Skylark BI API",
    version="0.2.0",
    description="Founder-facing AI Business Intelligence for Skylark Drones",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health & config
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "source": data_service.adapter.source_name(),
        "deals_loaded": len(data_service.deals),
        "work_orders_loaded": len(data_service.work_orders),
    }


@app.post("/api/reload")
async def reload_data():
    """Re-fetch data from the configured source."""
    await data_service.load()
    return {
        "status": "reloaded",
        "deals": len(data_service.deals),
        "work_orders": len(data_service.work_orders),
        "issues": len(data_service.all_issues),
    }


# ---------------------------------------------------------------------------
# Full summary
# ---------------------------------------------------------------------------

@app.get("/api/summary")
async def full_summary():
    """Complete analytics summary across all domains."""
    return data_service.full_summary()


# ---------------------------------------------------------------------------
# Pipeline analytics
# ---------------------------------------------------------------------------

@app.get("/api/pipeline")
async def pipeline_analytics():
    """Full pipeline analytics."""
    return data_service.pipeline_analytics().summary()


@app.get("/api/pipeline/value")
async def pipeline_value():
    pa = data_service.pipeline_analytics()
    return {
        "total": _metric(pa.total_pipeline_value()),
        "weighted": _metric(pa.weighted_pipeline()),
    }


@app.get("/api/pipeline/breakdown/{dimension}")
async def pipeline_breakdown(dimension: str):
    """Pipeline breakdown by: sector, stage, owner, probability."""
    pa = data_service.pipeline_analytics()
    methods = {
        "sector": pa.pipeline_by_sector,
        "stage": pa.pipeline_by_stage,
        "owner": pa.pipeline_by_owner,
        "probability": pa.pipeline_by_probability,
    }
    fn = methods.get(dimension)
    if fn is None:
        raise HTTPException(400, f"Unknown dimension: {dimension}. Use: {', '.join(methods)}")
    return _breakdown(fn())


# ---------------------------------------------------------------------------
# Revenue / Billing
# ---------------------------------------------------------------------------

@app.get("/api/revenue")
async def revenue_analytics():
    """Full revenue/billing analytics."""
    return data_service.revenue_analytics().summary()


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

@app.get("/api/operations")
async def operations_analytics():
    """Full operations analytics."""
    return data_service.operations_analytics().summary()


# ---------------------------------------------------------------------------
# Cross-board
# ---------------------------------------------------------------------------

@app.get("/api/cross-board")
async def cross_board_analytics():
    """Full cross-board analytics."""
    return data_service.cross_board_analytics().summary()


# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------

@app.get("/api/data-quality")
async def data_quality():
    """Data quality summary."""
    return data_service.data_quality_summary()


# ---------------------------------------------------------------------------
# AI / BI Layer
# ---------------------------------------------------------------------------

class AskQuery(BaseModel):
    query: str

@app.post("/api/ai/ask")
async def ai_ask(payload: AskQuery):
    """Answers a founder business question using computed metrics."""
    return ai_service.ask_skylark(payload.query)


@app.get("/api/ai/leadership-update")
async def ai_leadership_update():
    """Generates the weekly leadership update."""
    sections = ai_service.generate_leadership_update()
    return {"sections": sections}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _metric(m) -> Dict[str, Any]:
    from services.analytics.pipeline import _to_dict
    return _to_dict(m)


def _breakdown(b) -> Dict[str, Any]:
    from services.analytics.pipeline import _breakdown_to_dict
    return _breakdown_to_dict(b)