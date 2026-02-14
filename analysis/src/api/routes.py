"""FastAPI routes for the Python Analysis Service."""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import logging
from datetime import datetime, timezone

from src.state import PlatformState, PlatformEnum
from src.agents.graph import compile_pipeline
from src.db.neon import async_session, AnalysisRunModel, log_pipeline_step

logger = logging.getLogger(__name__)
router = APIRouter()


class PipelineRequest(BaseModel):
    niche_id: Optional[str] = "default"
    platforms: list[str] = ["reddit", "twitter", "youtube"]


class PipelineResponse(BaseModel):
    run_id: str
    status: str


# ─── Worker Function ──────────────────────────────────────


# ─── Worker Function ──────────────────────────────────────

async def execute_pipeline(run_id: str, request: PipelineRequest):
    """Execute the LangGraph pipeline in background."""
    logger.info(f"Starting pipeline run {run_id} for niche {request.niche_id}")
    
    # 1. Initialize State
    platforms = []
    for p in request.platforms:
        try:
            platforms.append(PlatformEnum(p.lower()))
        except ValueError:
            logger.warning(f"Invalid platform: {p}")
    
    if not platforms:
        platforms = [PlatformEnum.TWITTER, PlatformEnum.YOUTUBE] # Default fallback

    initial_state = PlatformState(
        run_id=run_id,
        niche_id=request.niche_id or "default",
        active_platforms=platforms,
    )

    # 2. Update run status to running
    try:
        async with async_session() as session:
            run = await session.get(AnalysisRunModel, run_id)
            if run:
                run.status = "running"
                await session.commit()
        
        await log_pipeline_step(run_id, "Pipeline", "started", f"Starting analysis for {request.platforms}")
    except Exception as e:
        logger.error(f"Failed to update run status: {e}")
        return

    # 3. Run Graph
    try:
        pipeline = compile_pipeline()
        final_state = await pipeline.ainvoke(initial_state) # type: ignore
        
        # 4. Update run record on completion
        async with async_session() as session:
            run = await session.get(AnalysisRunModel, run_id)
            if run:
                run.completed_at = datetime.now(timezone.utc)
                run.status = "completed"
                
                if hasattr(final_state, "evaluation") and final_state.evaluation:
                    run.evaluation_score = final_state.evaluation.confidence_score
                elif isinstance(final_state, dict) and final_state.get("evaluation"):
                     run.evaluation_score = final_state["evaluation"].confidence_score
                
                processed = final_state.total_items_processed if hasattr(final_state, "total_items_processed") else final_state.get("total_items_processed", 0)
                run.items_processed = processed
                await session.commit()
        
        await log_pipeline_step(run_id, "Pipeline", "completed", f"Analysis complete. Items processed: {run.items_processed}")
        logger.info(f"Pipeline run {run_id} completed successfully")

    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {e}")
        await log_pipeline_step(run_id, "Pipeline", "error", str(e))
        
        # Update DB status
        async with async_session() as session:
            run = await session.get(AnalysisRunModel, run_id)
            if run:
                run.status = "failed"
                run.completed_at = datetime.now(timezone.utc)
                # run_metadata usually handled by log_pipeline_step but safe to keep error there?
                # Actually log_pipeline_step appends to metadata, so we shouldn't overwrite it here blindly
                # run.run_metadata = {"error": str(e)} 
                await session.commit()


# ─── Pipeline endpoints ───────────────────────────────────

@router.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Execute full LangGraph pipeline."""
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    # Create run record immediately to avoid race condition with status polling
    async with async_session() as session:
        run_record = AnalysisRunModel(
            id=run_id,
            started_at=datetime.now(timezone.utc),
            status="queued",
            platforms_processed=request.platforms,
            run_metadata={"trigger": "api", "logs": []}
        )
        session.add(run_record)
        await session.commit()

    background_tasks.add_task(execute_pipeline, run_id, request)
    return PipelineResponse(run_id=run_id, status="queued")


@router.get("/pipeline/status/{run_id}")
async def pipeline_status(run_id: str):
    """Get pipeline run status."""
    async with async_session() as session:
        run = await session.get(AnalysisRunModel, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        
        metadata = run.run_metadata or {}
        
        return {
            "run_id": run.id,
            "status": run.status,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "items_processed": run.items_processed,
            "score": run.evaluation_score,
            "logs": metadata.get("logs", [])
        }


@router.get("/pipeline/history")
async def pipeline_history(limit: int = 10):
    """Get recent pipeline runs."""
    from sqlalchemy import select
    
    async with async_session() as session:
        # Sort by started_at desc
        stmt = select(AnalysisRunModel).order_by(
            AnalysisRunModel.started_at.desc()
        ).limit(limit)
        
        result = await session.execute(stmt)
        runs = result.scalars().all()
        
        history = []
        for run in runs:
            # Calculate duration
            duration = "N/A"
            if run.completed_at and run.started_at:
                diff = (run.completed_at - run.started_at).total_seconds()
                duration = f"{diff:.1f}s"
            elif run.status == "running" and run.started_at:
                now = datetime.now(timezone.utc)
                if run.started_at.tzinfo is None:
                    now = datetime.utcnow()
                diff = (now - run.started_at).total_seconds()
                duration = f"{diff:.1f}s..."

            history.append({
                "runId": run.id,
                "status": run.status,
                "startedAt": run.started_at.isoformat() if run.started_at else None,
                "completedAt": run.completed_at.isoformat() if run.completed_at else None,
                "duration": duration,
                "itemsProcessed": run.items_processed,
                "evaluationScore": run.evaluation_score,
                "platforms": run.platforms_processed
            })
            
        return {"runs": history}


# ─── Search endpoint ──────────────────────────────────────

@router.post("/search/semantic")
async def semantic_search(query: str, limit: int = 10):
    """Semantic similarity search via pgvector."""
    from src.processing.embeddings import generate_embeddings
    from src.db.neon import ContentItemModel
    from sqlalchemy import select
    
    # Generate embedding for query
    embeddings = generate_embeddings([query])
    if not embeddings:
        return {"query": query, "results": []}
    
    query_vec = embeddings[0].tolist()
    
    # Query DB
    async with async_session() as session:
        stmt = select(ContentItemModel).order_by(
            ContentItemModel.embedding.cosine_distance(query_vec)
        ).limit(limit)
        
        result = await session.execute(stmt)
        items = result.scalars().all()
        
        results = []
        for item in items:
            results.append({
                "id": str(item.id),
                "title": item.title,
                "body": item.body[:200] + "..." if item.body else "",
                "score": 0.0, # distance not easily returned yet via simpleORM select, need explicit request
                "platform": item.platform,
                "url": item.url
            })
            
    return {"query": query, "results": results, "limit": limit}
