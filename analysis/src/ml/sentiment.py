"""Sentiment analysis pipeline using twitter-roberta-base."""

import logging
from dataclasses import dataclass
from transformers import pipeline as hf_pipeline

from src.config import settings

logger = logging.getLogger(__name__)

# Lazy-load pipeline
_pipeline = None

LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}


@dataclass
class SentimentResult:
    """Sentiment analysis result for a single text."""
    label: str          # 'positive', 'negative', 'neutral'
    score: float        # confidence score (0-1)
    raw_label: str      # original model label


def get_pipeline():
    """Lazy-load the sentiment analysis pipeline."""
    global _pipeline
    if _pipeline is None:
        logger.info(f"Loading sentiment model: {settings.sentiment_model}")
        _pipeline = hf_pipeline(
            "sentiment-analysis",
            model=settings.sentiment_model,
            tokenizer=settings.sentiment_model,
            max_length=512,
            truncation=True,
        )
        logger.info("Sentiment model loaded")
    return _pipeline


def analyze_sentiment(text: str) -> SentimentResult:
    """Analyze sentiment of a single text."""
    pipe = get_pipeline()
    result = pipe(text[:512])[0]

    label = LABEL_MAP.get(result["label"], result["label"])
    return SentimentResult(
        label=label,
        score=result["score"],
        raw_label=result["label"],
    )


def analyze_sentiment_batch(
    texts: list[str],
    batch_size: int = 64,
) -> list[SentimentResult]:
    """
    Analyze sentiment for a batch of texts.

    Args:
        texts: List of text strings
        batch_size: Processing batch size

    Returns:
        List of SentimentResult objects
    """
    pipe = get_pipeline()

    # Truncate texts to max model length
    truncated = [t[:512] for t in texts]

    logger.info(f"Running sentiment analysis on {len(truncated)} texts (batch_size={batch_size})")

    results = []
    for i in range(0, len(truncated), batch_size):
        batch = truncated[i:i + batch_size]
        batch_results = pipe(batch)

        for raw in batch_results:
            label = LABEL_MAP.get(raw["label"], raw["label"])
            results.append(SentimentResult(
                label=label,
                score=raw["score"],
                raw_label=raw["label"],
            ))

        logger.info(f"  Processed batch {i // batch_size + 1}/{(len(truncated) - 1) // batch_size + 1}")

    # Log distribution
    pos = sum(1 for r in results if r.label == "positive")
    neg = sum(1 for r in results if r.label == "negative")
    neu = sum(1 for r in results if r.label == "neutral")
    logger.info(f"Sentiment results: {pos} positive, {neg} negative, {neu} neutral")

    return results
