"""FastAPI entry point for the Python Analysis Service."""

import sys
import asyncio
import logging
from contextlib import asynccontextmanager

# Fix for Windows asyncio loop policy with httpx/uvicorn
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routes import router as api_router
from src.scheduler import start_scheduler, shutdown_scheduler

logging.basicConfig(level=logging.INFO)


# ─── Lifespan ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the scheduler on startup, stop it cleanly on shutdown."""
    start_scheduler(interval_hours=12)
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Market Research Analysis Service",
    description="ML pipelines, LangGraph agent orchestration, and data analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# ─── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check ──────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "market-research-analysis",
        "environment": settings.environment,
    }


# ─── API Routes ───────────────────────────────────────────
app.include_router(api_router, prefix="")
