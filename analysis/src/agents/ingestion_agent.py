import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone

from src.state import PlatformState, IngestionMetadata, PlatformEnum
from src.ingestion.twitter import fetch_twitter_data
from src.ingestion.youtube import search_youtube_videos
from src.ingestion.reddit import fetch_reddit_data
from src.db.mongo import store_raw_data
from src.db.neon import async_session, log_pipeline_step, NicheModel

logger = logging.getLogger(__name__)

# ── Ingestion volume presets ──────────────────────────────────────────
# Set INGESTION_MODE=prod in .env for real analysis runs.
# Default is "dev" to avoid burning API credits during testing.

INGESTION_PRESETS = {
    "dev": {
        "twitter_pages": 3,          # ~60 tweets, cost ~$0.003
        "twitter_keywords": 1,
        "youtube_results": 15,       # 15 videos, ~200 quota units
        "youtube_keywords": 1,
        "reddit_max_items": 50,      # ~50 items, cost ~$0.10
        "reddit_max_posts": 10,
    },
    "prod": {
        "twitter_pages": 15,         # ~300 tweets, cost ~$0.045
        "twitter_keywords": 3,
        "youtube_results": 50,       # ~150 videos, ~450 quota units
        "youtube_keywords": 3,
        "reddit_max_items": 200,     # ~200 items, cost ~$0.49
        "reddit_max_posts": 50,
    },
}

_mode = os.getenv("INGESTION_MODE", "dev").lower()
PRESET = INGESTION_PRESETS.get(_mode, INGESTION_PRESETS["dev"])
logger.info(f"Ingestion mode: {_mode} → {PRESET}")

async def ingestion_agent(state: PlatformState) -> dict:
    """
    Agent 1: Orchestrate data ingestion from all active platforms in parallel.

    Reads: active_platforms, niche_id
    Writes: ingestion_metadata
    """
    logger.info(f"[Ingestion Agent] Starting for platforms: {state.active_platforms}")
    await log_pipeline_step(state.run_id, "Ingestion", "running", f"Fetching data from {len(state.active_platforms)} platforms in parallel...")

    # 1. Resolve keywords from Niche
    keywords = ["AI tools"] # Fallback
    subreddits = []
    
    if state.niche_id and state.niche_id != "default":
        try:
            async with async_session() as session:
                # Try to parse uuid if it looks like one, otherwise skip
                try:
                    niche_uuid = uuid.UUID(state.niche_id)
                    niche = await session.get(NicheModel, niche_uuid)
                    if niche:
                        keywords = niche.keywords or keywords
                        subreddits = niche.subreddits or []
                        logger.info(f"[Ingestion] Using niche keywords: {keywords}")
                except ValueError:
                    logger.warning(f"[Ingestion] niche_id {state.niche_id} is not a valid UUID, using defaults")
        except Exception as e:
            logger.error(f"[Ingestion] Failed to fetch niche data: {e}")

    # 2. Prepare tasks for asycnio.gather
    tasks = []
    for platform in state.active_platforms:
        batch_id = f"{state.run_id}_{platform.value}_{uuid.uuid4().hex[:8]}"
        
        if platform == PlatformEnum.TWITTER:
            tasks.append(_ingest_twitter(batch_id, keywords, state.run_id))
        elif platform == PlatformEnum.YOUTUBE:
            tasks.append(_ingest_youtube(batch_id, keywords, state.run_id))
        elif platform == PlatformEnum.REDDIT:
            tasks.append(_ingest_reddit(batch_id, keywords, subreddits, state.run_id))
        else:
            logger.warning(f"Unknown platform: {platform}")

    # 3. Execute in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    ingestion_results: list[IngestionMetadata] = []
    for res in results:
        if isinstance(res, Exception):
            logger.error(f"[Ingestion] Task failed: {res}")
            continue
        if res:
            ingestion_results.append(res)

    total = sum(m.items_fetched for m in ingestion_results)
    logger.info(f"[Ingestion Agent] Complete. Total items fetched: {total}")
    await log_pipeline_step(state.run_id, "Ingestion", "completed", f"Ingestion complete. Total items: {total}")

    return {"ingestion_metadata": ingestion_results}


async def _ingest_twitter(batch_id: str, keywords: list[str], run_id: str) -> IngestionMetadata:
    """Fetch and store Twitter data.
    
    Searches up to 3 keywords, 15 pages each (~20 tweets/page).
    Expected yield: ~300-900 tweets.
    Cost: ~$0.045/run (45 API calls × $0.001).
    """
    try:
        all_tweets: list[dict] = []
        max_kw = PRESET["twitter_keywords"]
        total_pages = PRESET["twitter_pages"]
        search_terms = keywords[:max_kw] if keywords else ["AI tools"]
        pages_per_keyword = max(3, total_pages // len(search_terms))

        for term in search_terms:
            tweets = await fetch_twitter_data(query=term, max_pages=pages_per_keyword)
            all_tweets.extend(tweets)
            logger.info(f"[Twitter] '{term}': {len(tweets)} tweets")

        if all_tweets:
            stored = await store_raw_data(
                collection_name="raw_twitter_tweets",
                items=all_tweets,
                batch_id=batch_id,
                api_source="getxapi",
            )
            logger.info(f"[Twitter] Stored {stored} raw tweets in MongoDB")

        await log_pipeline_step(run_id, "Ingestion", "info", f"Fetched {len(all_tweets)} items from twitter ({len(search_terms)} queries)")
        return IngestionMetadata(
            platform=PlatformEnum.TWITTER,
            items_fetched=len(all_tweets),
            items_new=len(all_tweets),
            status="success",
            batch_id=batch_id,
        )
    except Exception as e:
        logger.error(f"[Twitter] failed: {e}")
        return IngestionMetadata(platform=PlatformEnum.TWITTER, status="failed", error_message=str(e), batch_id=batch_id)


async def _ingest_youtube(batch_id: str, keywords: list[str], run_id: str) -> IngestionMetadata:
    """Fetch and store YouTube data.
    
    Searches up to 3 keywords, 50 results each (API max per call).
    Expected yield: ~50-150 videos.
    Quota cost: ~450 units/run (3 searches × 100 + ~150 detail calls × 1).
    Daily budget: 10K units → ~22 runs/day.
    """
    try:
        all_videos: list[dict] = []
        max_kw = PRESET["youtube_keywords"]
        max_results = PRESET["youtube_results"]
        search_terms = keywords[:max_kw] if keywords else ["AI tools"]

        for term in search_terms:
            videos = await search_youtube_videos(query=term, max_results=max_results)
            all_videos.extend(videos)
            logger.info(f"[YouTube] '{term}': {len(videos)} videos")

        if all_videos:
            stored = await store_raw_data(
                collection_name="raw_youtube_videos",
                items=all_videos,
                batch_id=batch_id,
                api_source="youtube_data_api",
            )
            logger.info(f"[YouTube] Stored {stored} raw videos in MongoDB")

        await log_pipeline_step(run_id, "Ingestion", "info", f"Fetched {len(all_videos)} items from youtube ({len(search_terms)} queries)")
        return IngestionMetadata(
            platform=PlatformEnum.YOUTUBE,
            items_fetched=len(all_videos),
            items_new=len(all_videos),
            status="success",
            batch_id=batch_id,
        )
    except Exception as e:
        logger.error(f"[YouTube] failed: {e}")
        return IngestionMetadata(platform=PlatformEnum.YOUTUBE, status="failed", error_message=str(e), batch_id=batch_id)


async def _ingest_reddit(batch_id: str, keywords: list[str], subreddits: list[str], run_id: str) -> IngestionMetadata:
    """Fetch and store Reddit data.
    
    Searches up to 3 keywords across specified subreddits.
    Expected yield: ~200 items (posts + comments).
    Cost: ~$0.49/run (Apify actor).
    """
    try:
        search_terms = keywords[:3] if keywords else ["AI tools"]
        items = await fetch_reddit_data(
            keywords=search_terms,
            subreddits=subreddits if subreddits else None,
            max_items=PRESET["reddit_max_items"],
            max_post_count=PRESET["reddit_max_posts"],
        )

        if items:
            stored = await store_raw_data(
                collection_name="raw_reddit_posts",
                items=items,
                batch_id=batch_id,
                api_source="apify_reddit",
            )
            logger.info(f"[Reddit] Stored {stored} raw items in MongoDB")

        await log_pipeline_step(run_id, "Ingestion", "info", f"Fetched {len(items)} items from reddit")
        return IngestionMetadata(
            platform=PlatformEnum.REDDIT,
            items_fetched=len(items),
            items_new=len(items),
            status="success",
            batch_id=batch_id,
        )
    except Exception as e:
        logger.error(f"[Reddit] failed: {e}")
        return IngestionMetadata(platform=PlatformEnum.REDDIT, status="failed", error_message=str(e), batch_id=batch_id)
