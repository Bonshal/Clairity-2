"""Trend Detection Agent — identifies emerging and viral trends."""

import logging
from src.state import PlatformState, TrendSignal as TrendSignalState, PlatformEnum
from src.ml.trends import detect_trends

logger = logging.getLogger(__name__)


async def trend_agent(state: PlatformState) -> dict:
    """
    Agent 3: Run statistical trend detection on processed content.

    Reads: cleaned_data_refs
    Writes: trend_signals, emerging_count, declining_count, viral_count
    """
    logger.info("[Trend Agent] Starting...")

    # TODO: Load content items from Neon based on cleaned_data_refs
    # For now, placeholder with empty items
    all_items: list[dict] = []

    if not all_items:
        logger.warning("[Trend Agent] No items available for trend detection")
        return {
            "trend_signals": [],
            "emerging_count": 0,
            "declining_count": 0,
            "viral_count": 0,
        }

    # Run trend detection
    results = detect_trends(all_items, text_field="cleaned_text", time_field="platform_created_at")

    # Convert to state schema
    signals = [
        TrendSignalState(
            keyword=r.keyword,
            platform=PlatformEnum.REDDIT,  # TODO: determine from item source
            direction=r.direction,
            momentum_7d=r.momentum_7d,
            momentum_30d=r.momentum_30d,
            volume_current=r.volume_current,
            volume_previous=r.volume_previous,
            z_score=r.z_score,
            confidence=r.confidence,
        )
        for r in results
    ]

    emerging = sum(1 for s in signals if s.direction == "emerging")
    declining = sum(1 for s in signals if s.direction == "declining")
    viral = sum(1 for s in signals if s.direction == "viral")

    logger.info(f"[Trend Agent] Complete. {len(signals)} signals: {viral} viral, {emerging} emerging")

    return {
        "trend_signals": signals,
        "emerging_count": emerging,
        "declining_count": declining,
        "viral_count": viral,
    }
