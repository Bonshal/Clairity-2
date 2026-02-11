"""Statistical trend detection pipeline."""

import logging
from dataclasses import dataclass
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class TrendResult:
    """Detected trend signal."""
    keyword: str
    direction: str        # 'emerging', 'declining', 'stable', 'viral'
    momentum_7d: float    # 7-day momentum (EMA ratio)
    momentum_30d: float   # 30-day momentum (EMA ratio)
    volume_current: int   # Current period mention count
    volume_previous: int  # Previous period mention count
    z_score: float        # Statistical significance
    confidence: float     # 0-1 confidence score


def calculate_ema(values: list[float], span: int) -> list[float]:
    """Calculate Exponential Moving Average."""
    if not values:
        return []

    alpha = 2 / (span + 1)
    ema = [values[0]]
    for v in values[1:]:
        ema.append(alpha * v + (1 - alpha) * ema[-1])
    return ema


def detect_trends(
    items: list[dict],
    text_field: str = "text",
    time_field: str = "created_at",
    keywords: list[str] | None = None,
    min_mentions: int = 3,
) -> list[TrendResult]:
    """
    Detect trending keywords from content items using statistical methods.

    Args:
        items: List of content dicts with text and timestamp
        text_field: Key for text content
        time_field: Key for timestamp
        keywords: Optional list of keywords to track (if None, auto-extract)
        min_mentions: Minimum mentions to qualify as a trend

    Returns:
        List of TrendResult objects sorted by momentum
    """
    if not items:
        return []

    logger.info(f"Detecting trends in {len(items)} items")

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    # Extract keywords from texts if not provided
    if keywords is None:
        keywords = _auto_extract_keywords(items, text_field, min_count=min_mentions)

    # Count keyword mentions by time period
    results: list[TrendResult] = []

    for keyword in keywords:
        keyword_lower = keyword.lower()

        current_7d = 0
        previous_7d = 0
        current_30d = 0
        previous_30d = 0
        daily_counts: dict[str, int] = defaultdict(int)

        for item in items:
            text = (item.get(text_field) or "").lower()
            if keyword_lower not in text:
                continue

            # Parse timestamp
            ts_raw = item.get(time_field)
            if ts_raw is None:
                continue

            if isinstance(ts_raw, str):
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).replace(tzinfo=None)
                except (ValueError, TypeError):
                    continue
            elif isinstance(ts_raw, datetime):
                ts = ts_raw.replace(tzinfo=None)
            else:
                continue

            day_key = ts.strftime("%Y-%m-%d")
            daily_counts[day_key] += 1

            if ts >= week_ago:
                current_7d += 1
            elif ts >= week_ago - timedelta(days=7):
                previous_7d += 1

            if ts >= month_ago:
                current_30d += 1
            elif ts >= two_months_ago:
                previous_30d += 1

        if current_7d < min_mentions:
            continue

        # Calculate momentum
        momentum_7d = (current_7d / max(previous_7d, 1)) - 1.0
        momentum_30d = (current_30d / max(previous_30d, 1)) - 1.0

        # Calculate Z-score for current 7d volume
        daily_values = list(daily_counts.values())
        if len(daily_values) >= 3:
            z_score = float(stats.zscore(daily_values)[-1]) if len(daily_values) > 1 else 0.0
        else:
            z_score = 0.0

        # Classify direction
        if z_score > 3.0 or momentum_7d > 5.0:
            direction = "viral"
        elif momentum_7d > 0.5:
            direction = "emerging"
        elif momentum_7d < -0.3:
            direction = "declining"
        else:
            direction = "stable"

        # Confidence: combination of volume and statistical significance
        volume_score = min(current_7d / 50, 1.0)
        z_score_normalized = min(abs(z_score) / 3.0, 1.0)
        confidence = 0.6 * volume_score + 0.4 * z_score_normalized

        results.append(TrendResult(
            keyword=keyword,
            direction=direction,
            momentum_7d=round(momentum_7d, 3),
            momentum_30d=round(momentum_30d, 3),
            volume_current=current_7d,
            volume_previous=previous_7d,
            z_score=round(z_score, 3),
            confidence=round(confidence, 3),
        ))

    # Sort by momentum (descending)
    results.sort(key=lambda r: r.momentum_7d, reverse=True)

    viral = sum(1 for r in results if r.direction == "viral")
    emerging = sum(1 for r in results if r.direction == "emerging")
    declining = sum(1 for r in results if r.direction == "declining")
    logger.info(f"Trends: {viral} viral, {emerging} emerging, {declining} declining, {len(results)} total")

    return results


def _auto_extract_keywords(
    items: list[dict],
    text_field: str,
    min_count: int = 3,
    max_keywords: int = 100,
) -> list[str]:
    """Extract most common multi-word phrases from texts."""
    from collections import Counter
    import re

    word_counter: Counter = Counter()
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "out", "off", "over",
        "under", "again", "further", "then", "once", "here", "there", "when",
        "where", "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "just", "don", "now", "and",
        "but", "or", "if", "this", "that", "it", "its", "i", "me", "my",
        "we", "our", "you", "your", "he", "she", "they", "them", "what",
        "which", "who", "whom", "these", "those", "am",
    }

    for item in items:
        text = (item.get(text_field) or "").lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        meaningful = [w for w in words if w not in stop_words]
        word_counter.update(meaningful)

    # Return words that appear at least min_count times
    keywords = [
        word for word, count in word_counter.most_common(max_keywords)
        if count >= min_count
    ]

    logger.info(f"Auto-extracted {len(keywords)} keywords (min_count={min_count})")
    return keywords
