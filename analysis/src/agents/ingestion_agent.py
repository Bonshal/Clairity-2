"""Ingestion Coordinator Agent — orchestrates data fetching from all platforms."""

import logging
import uuid
from datetime import datetime, timezone

from src.state import PlatformState, IngestionMetadata, PlatformEnum
from src.ingestion.twitter import fetch_twitter_data
from src.ingestion.youtube import search_youtube_videos
from src.db.mongo import store_raw_data

logger = logging.getLogger(__name__)


async def ingestion_agent(state: PlatformState) -> dict:
    """
    Agent 1: Orchestrate data ingestion from all active platforms.

    Reads: active_platforms, niche_id
    Writes: ingestion_metadata
    """
    logger.info(f"[Ingestion Agent] Starting for platforms: {state.active_platforms}")

    ingestion_results: list[IngestionMetadata] = []

    for platform in state.active_platforms:
        batch_id = f"{state.run_id}_{platform.value}_{uuid.uuid4().hex[:8]}"

        try:
            if platform == PlatformEnum.TWITTER:
                items = await _ingest_twitter(batch_id)
            elif platform == PlatformEnum.YOUTUBE:
                items = await _ingest_youtube(batch_id)
            elif platform == PlatformEnum.REDDIT:
                # Reddit/Apify deferred — skip gracefully
                logger.info("[Ingestion] Reddit/Apify not configured yet — skipping")
                ingestion_results.append(IngestionMetadata(
                    platform=platform,
                    items_fetched=0,
                    items_new=0,
                    status="partial",
                    error_message="Apify not configured",
                    batch_id=batch_id,
                ))
                continue
            else:
                logger.warning(f"Unknown platform: {platform}")
                continue

            ingestion_results.append(IngestionMetadata(
                platform=platform,
                items_fetched=len(items),
                items_new=len(items),
                status="success",
                batch_id=batch_id,
            ))

        except Exception as e:
            logger.error(f"[Ingestion] {platform.value} failed: {e}")
            ingestion_results.append(IngestionMetadata(
                platform=platform,
                items_fetched=0,
                items_failed=1,
                status="failed",
                error_message=str(e),
                batch_id=batch_id,
            ))

    total = sum(m.items_fetched for m in ingestion_results)
    logger.info(f"[Ingestion Agent] Complete. Total items fetched: {total}")

    return {"ingestion_metadata": ingestion_results}


async def _ingest_twitter(batch_id: str) -> list[dict]:
    """Fetch and store Twitter data."""
    # TODO: Pull query from niche config
    query = "AI tools"
    tweets = await fetch_twitter_data(query=query, max_pages=5)

    if tweets:
        stored = await store_raw_data(
            collection_name="raw_twitter_tweets",
            items=tweets,
            batch_id=batch_id,
            api_source="getxapi",
        )
        logger.info(f"[Twitter] Stored {stored} raw tweets in MongoDB")

    return tweets


async def _ingest_youtube(batch_id: str) -> list[dict]:
    """Fetch and store YouTube data."""
    # TODO: Pull query from niche config
    query = "AI tools"
    videos = await search_youtube_videos(query=query, max_results=25)

    if videos:
        stored = await store_raw_data(
            collection_name="raw_youtube_videos",
            items=videos,
            batch_id=batch_id,
            api_source="youtube_data_api",
        )
        logger.info(f"[YouTube] Stored {stored} raw videos in MongoDB")

    return videos
