"""Sentiment & Emotion Agent — analyzes content sentiment and emotions."""

import logging
from src.state import PlatformState, SentimentSummary, EmotionSummary
from src.ml.sentiment import analyze_sentiment_batch
from src.ml.emotions import detect_emotions_batch, aggregate_emotions

logger = logging.getLogger(__name__)


async def sentiment_agent(state: PlatformState) -> dict:
    """
    Agent 4: Run sentiment and emotion analysis.

    Reads: cleaned_data_refs
    Writes: sentiment_summaries, emotion_summaries, overall_sentiment
    """
    logger.info("[Sentiment Agent] Starting...")

    # TODO: Load content items from Neon based on cleaned_data_refs
    all_texts: list[str] = []

    if not all_texts:
        logger.warning("[Sentiment Agent] No texts available for analysis")
        return {
            "sentiment_summaries": [],
            "emotion_summaries": [],
            "overall_sentiment": "neutral",
        }

    # Run sentiment analysis
    sentiment_results = analyze_sentiment_batch(all_texts, batch_size=64)

    # Aggregate sentiment
    pos = sum(1 for r in sentiment_results if r.label == "positive")
    neg = sum(1 for r in sentiment_results if r.label == "negative")
    neu = sum(1 for r in sentiment_results if r.label == "neutral")
    total = len(sentiment_results)

    overall = "neutral"
    if pos / max(total, 1) > 0.5:
        overall = "positive"
    elif neg / max(total, 1) > 0.5:
        overall = "negative"

    sentiment_summary = SentimentSummary(
        scope="overall",
        positive_ratio=round(pos / max(total, 1), 3),
        negative_ratio=round(neg / max(total, 1), 3),
        neutral_ratio=round(neu / max(total, 1), 3),
        dominant_sentiment=overall,
        sample_size=total,
    )

    # Run emotion detection
    emotion_results = detect_emotions_batch(all_texts, batch_size=64)
    aggregated = aggregate_emotions(emotion_results)
    dominant_emotion = max(aggregated, key=aggregated.get) if aggregated else "neutral"

    emotion_summary = EmotionSummary(
        scope="overall",
        emotions=aggregated,
        dominant_emotion=dominant_emotion,
        emotional_intensity=aggregated.get(dominant_emotion, 0),
        sample_size=total,
    )

    logger.info(
        f"[Sentiment Agent] Complete. {total} texts analyzed. "
        f"Overall: {overall}, Dominant emotion: {dominant_emotion}"
    )

    return {
        "sentiment_summaries": [sentiment_summary],
        "emotion_summaries": [emotion_summary],
        "overall_sentiment": overall,
    }
