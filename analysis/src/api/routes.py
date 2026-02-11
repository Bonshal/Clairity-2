"""FastAPI routes for the Python Analysis Service."""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()


class PipelineRequest(BaseModel):
    niche_id: Optional[str] = None
    platforms: list[str] = ["reddit", "twitter", "youtube"]


class PipelineResponse(BaseModel):
    run_id: str
    status: str


# ─── Pipeline endpoints ───────────────────────────────────

@router.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Execute full LangGraph pipeline."""
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    # TODO: background_tasks.add_task(execute_pipeline, run_id, request)
    return PipelineResponse(run_id=run_id, status="queued")


@router.post("/pipeline/ingest", response_model=PipelineResponse)
async def run_ingestion(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Run ingestion only."""
    run_id = f"ingest_{uuid.uuid4().hex[:12]}"
    # TODO: background_tasks.add_task(execute_ingestion, run_id, request)
    return PipelineResponse(run_id=run_id, status="queued")


@router.post("/pipeline/analyze", response_model=PipelineResponse)
async def run_analysis(background_tasks: BackgroundTasks):
    """Run analysis only (assumes data already ingested)."""
    run_id = f"analyze_{uuid.uuid4().hex[:12]}"
    # TODO: background_tasks.add_task(execute_analysis, run_id)
    return PipelineResponse(run_id=run_id, status="queued")


@router.get("/pipeline/status/{run_id}")
async def pipeline_status(run_id: str):
    """Get pipeline run status."""
    # TODO: Query analysis_runs table
    return {"run_id": run_id, "status": "unknown"}


# ─── Search endpoint ──────────────────────────────────────

@router.post("/search/semantic")
async def semantic_search(query: str, limit: int = 10):
    """Semantic similarity search via pgvector."""
    # TODO: Generate embedding, query pgvector
    return {"query": query, "results": [], "limit": limit}
