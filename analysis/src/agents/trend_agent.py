"""Trend Detection Agent — identifies emerging and viral trends.

CHANGELOG (2026-02-14):
- Now resolves niche keywords from the database and passes them to detect_trends()
  so trends are filtered/boosted by the user's niche configuration.
- Passes engagement data per item for engagement-weighted trend detection.
"""

import logging
import uuid
from datetime import datetime, timezone

from src.state import PlatformState, TrendSignal as TrendSignalState, PlatformEnum
from src.ml.trends import detect_trends, clean_text, extract_candidates_semantic
from src.llm.wrapper import refine_trend_labels
from src.db.neon import async_session, fetch_content_by_ids, TrendSignalModel, NicheModel, log_pipeline_step

logger = logging.getLogger(__name__)


async def trend_agent(state: PlatformState) -> dict:
    """
    Agent 3: Run statistical trend detection on processed content.

    Reads: cleaned_data_refs, niche_id
    Writes: trend_signals, emerging_count, declining_count, viral_count
    
    IMPORTANT: This agent persists detected trends to the `trend_signals`
    database table so the dashboard can display them.
    """
    logger.info("[Trend Agent] Starting...")
    await log_pipeline_step(state.run_id, "Trend Analysis", "running", "Detecting emerging & viral trends...")

    all_items: list[dict] = []
    
    # 1. Gather all content IDs from the preprocessing step
    content_ids = []
    for ref in state.cleaned_data_refs:
        if ref.content_ids:
            content_ids.extend(ref.content_ids)
    
    if not content_ids:
        logger.warning("[Trend Agent] No content IDs to process")
        await log_pipeline_step(state.run_id, "Trend Analysis", "warning", "No content to analyze.")
        return {
            "trend_signals": [],
            "emerging_count": 0,
            "declining_count": 0,
            "viral_count": 0,
        }

    # 2. Resolve niche keywords from the database
    niche_keywords: list[str] | None = None
    if state.niche_id and state.niche_id != "default":
        try:
            niche_uuid = uuid.UUID(state.niche_id)
            async with async_session() as session:
                niche = await session.get(NicheModel, niche_uuid)
                if niche and niche.keywords:
                    # Filter out empty strings
                    niche_keywords = [k for k in niche.keywords if k.strip()]
                    logger.info(f"[Trend Agent] Using niche keywords: {niche_keywords}")
        except (ValueError, Exception) as e:
            logger.warning(f"[Trend Agent] Could not resolve niche: {e}")

    # 3. Fetch content items from Neon
    try:
        async with async_session() as session:
            items = await fetch_content_by_ids(session, content_ids)
            for item in items:
                all_items.append({
                    "id": str(item.id),
                    "platform": item.platform,
                    "cleaned_text": item.body or item.title or "",
                    # Use the actual post date for trend momentum calculations.
                    # Falls back to fetched_at only if platform_created_at is NULL.
                    "platform_created_at": item.platform_created_at or item.fetched_at,
                    "engagement": (item.likes or 0) + (item.shares or 0) + (item.comments_count or 0)
                })
                
    except Exception as e:
        logger.error(f"[Trend Agent] Failed to fetch items: {e}")
        await log_pipeline_step(state.run_id, "Trend Analysis", "error", f"DB fetch failed: {e}")
        return {
            "trend_signals": [],
            "emerging_count": 0,
            "declining_count": 0,
            "viral_count": 0,
        }

    if not all_items:
        logger.warning("[Trend Agent] No items found in DB (despite IDs existing)")
        return { "trend_signals": [], "emerging_count": 0, "declining_count": 0, "viral_count": 0 }

    # 4. Hybrid Trend Extraction Pipeline
    # A. Clean texts for ML processing
    cleaned_texts = []
    for item in all_items:
        raw = item.get("cleaned_text", "")
        if len(raw) > 15:
            cleaned_texts.append(clean_text(raw))
    
    # B. Extract statistical candidates (The "Grounding" Layer)
    candidates = extract_candidates_semantic(cleaned_texts, top_n=60)
    logger.info(f"[Trend Agent] Extracted {len(candidates)} Semantic candidates: {candidates[:5]}...")
    await log_pipeline_step(
        state.run_id, "Trend Analysis", "running", 
        f"Step 1: Extracted {len(candidates)} candidates via KeyBERT/SpaCy (e.g., {', '.join(candidates[:3])})"
    )

    # C. Refine via LLM (The "Polish" Layer)
    refined_keywords = await refine_trend_labels(candidates)
    if refined_keywords != candidates:
        logger.info(f"[Trend Agent] LLM refined keywords: {refined_keywords[:5]}...")
        await log_pipeline_step(
            state.run_id, "Trend Analysis", "running", 
            f"Step 2: Refined {len(refined_keywords)} trends via LLM"
        )
    
    # D. Compute Trend Metrics (Momentum, Z-Score) on refined keywords
    results = detect_trends(
        all_items, 
        text_field="cleaned_text", 
        time_field="platform_created_at",
        keywords=refined_keywords,
        niche_keywords=niche_keywords,
    )

    # 4. Convert to state schema AND persist to database
    signals = []
    db_models = []
    timestamp = datetime.now(timezone.utc)

    for r in results:
        # Determine platform from data or default
        platform = _determine_platform(all_items, r.keyword)

        # State object for LangGraph
        signal = TrendSignalState(
            keyword=r.keyword,
            platform=platform,
            direction=r.direction,
            momentum_7d=r.momentum_7d,
            momentum_30d=r.momentum_30d,
            volume_current=r.volume_current,
            volume_previous=r.volume_previous,
            z_score=r.z_score,
            confidence=r.confidence,
        )
        signals.append(signal)

        # DB model for persistence
        db_models.append(TrendSignalModel(
            id=uuid.uuid4(),
            keyword=r.keyword,
            platform=platform.value if isinstance(platform, PlatformEnum) else str(platform),
            direction=r.direction,
            momentum_7d=r.momentum_7d,
            momentum_30d=r.momentum_30d,
            volume_current=r.volume_current,
            volume_previous=r.volume_previous,
            confidence=r.confidence,
            detected_at=timestamp,
        ))

    # 5. Persist trends to database
    if db_models:
        try:
            async with async_session() as session:
                session.add_all(db_models)
                await session.commit()
            logger.info(f"[Trend Agent] Persisted {len(db_models)} trends to database")
        except Exception as e:
            logger.error(f"[Trend Agent] Failed to persist trends: {e}", exc_info=True)
            # Don't fail the pipeline even if DB write fails —
            # the trends are still in LangGraph state for downstream agents
            await log_pipeline_step(
                state.run_id, "Trend Analysis", "warning",
                f"Trends detected but DB persist failed: {e}"
            )

    emerging = sum(1 for s in signals if s.direction == "emerging")
    declining = sum(1 for s in signals if s.direction == "declining")
    viral = sum(1 for s in signals if s.direction == "viral")

    logger.info(f"[Trend Agent] Complete. {len(signals)} signals: {viral} viral, {emerging} emerging")
    await log_pipeline_step(
        state.run_id, "Trend Analysis", "completed",
        f"Found {len(signals)} trends ({viral} viral, {emerging} emerging) — saved to DB"
    )

    return {
        "trend_signals": signals,
        "emerging_count": emerging,
        "declining_count": declining,
        "viral_count": viral,
    }


def _determine_platform(items: list[dict], keyword: str) -> PlatformEnum:
    """
    Determine the most relevant platform for a trend keyword
    by checking which platform's content mentions it most.

    Falls back to TWITTER if no match found.
    """
    from collections import Counter

    keyword_lower = keyword.lower()
    platform_counts: Counter = Counter()

    for item in items:
        text = item.get("cleaned_text", "").lower()
        if keyword_lower in text:
            platform_counts[item.get("platform", "twitter")] += 1

    if not platform_counts:
        return PlatformEnum.TWITTER

    most_common = platform_counts.most_common(1)[0][0]

    try:
        return PlatformEnum(most_common.lower())
    except ValueError:
        return PlatformEnum.TWITTER
