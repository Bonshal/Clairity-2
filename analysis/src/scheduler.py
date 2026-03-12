"""Background scheduler — runs the analysis pipeline on a fixed interval."""

import logging
import uuid
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.api.routes import execute_pipeline, PipelineRequest
from src.db.neon import async_session, AnalysisRunModel

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def run_scheduled_pipeline():
    """Scheduled job: create a run record and fire the pipeline."""
    run_id = f"sched_{uuid.uuid4().hex[:12]}"
    logger.info(f"[Scheduler] Starting scheduled pipeline run: {run_id}")

    request = PipelineRequest(
        niche_id="default",
        platforms=["reddit", "twitter", "youtube"],
    )

    # Create the DB run record first
    try:
        async with async_session() as session:
            run_record = AnalysisRunModel(
                id=run_id,
                started_at=datetime.now(timezone.utc),
                status="queued",
                platforms_processed=request.platforms,
                run_metadata={"trigger": "scheduler", "logs": []},
            )
            session.add(run_record)
            await session.commit()
    except Exception as e:
        logger.error(f"[Scheduler] Failed to create run record: {e}")
        return

    # Hand off to the same worker the HTTP endpoint uses
    await execute_pipeline(run_id, request)
    logger.info(f"[Scheduler] Run {run_id} complete.")


def start_scheduler(interval_hours: int = 12):
    """Create and start the APScheduler instance inside FastAPI's event loop."""
    global _scheduler

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        run_scheduled_pipeline,
        trigger=IntervalTrigger(hours=interval_hours),
        id="pipeline_job",
        name="Scheduled Analysis Pipeline",
        next_run_time=datetime.now(timezone.utc),  # fire immediately on startup
        max_instances=1,   # never overlap two runs
        coalesce=True,     # if the server was down and missed runs, just run once
    )
    _scheduler.start()
    logger.info(f"[Scheduler] Started — pipeline runs every {interval_hours}h.")


def shutdown_scheduler():
    """Stop the scheduler cleanly when FastAPI shuts down."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped.")
