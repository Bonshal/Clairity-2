"""Emotion detection pipeline using GoEmotions model."""

import logging
from dataclasses import dataclass
from transformers import pipeline as hf_pipeline

from src.config import settings

logger = logging.getLogger(__name__)

_pipeline = None

# Top emotions to track (GoEmotions has 28 labels)
PRIMARY_EMOTIONS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness",
    "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise", "neutral",
]


@dataclass
class EmotionResult:
    """Emotion detection result for a single text."""
    emotions: dict[str, float]   # emotion → confidence score
    dominant: str                 # highest-scoring emotion
    intensity: float             # score of dominant emotion


def get_pipeline():
    """Lazy-load the emotion detection pipeline."""
    global _pipeline
    if _pipeline is None:
        logger.info(f"Loading emotion model: {settings.emotion_model}")
        _pipeline = hf_pipeline(
            "text-classification",
            model=settings.emotion_model,
            tokenizer=settings.emotion_model,
            max_length=512,
            truncation=True,
            top_k=None,  # Return all emotion scores
        )
        logger.info("Emotion model loaded")
    return _pipeline


def detect_emotions(text: str) -> EmotionResult:
    """Detect emotions in a single text."""
    pipe = get_pipeline()
    results = pipe(text[:512])[0]

    # Build emotion dict, sort by score
    emotions = {r["label"]: round(r["score"], 4) for r in results}
    dominant = max(emotions, key=emotions.get)  # type: ignore

    return EmotionResult(
        emotions=emotions,
        dominant=dominant,
        intensity=emotions[dominant],
    )


def detect_emotions_batch(
    texts: list[str],
    batch_size: int = 64,
) -> list[EmotionResult]:
    """
    Detect emotions for a batch of texts.

    Args:
        texts: List of text strings
        batch_size: Processing batch size

    Returns:
        List of EmotionResult objects
    """
    pipe = get_pipeline()
    truncated = [t[:512] for t in texts]

    logger.info(f"Running emotion detection on {len(truncated)} texts (batch_size={batch_size})")

    results: list[EmotionResult] = []
    for i in range(0, len(truncated), batch_size):
        batch = truncated[i:i + batch_size]
        batch_results = pipe(batch)

        for raw_list in batch_results:
            emotions = {r["label"]: round(r["score"], 4) for r in raw_list}
            dominant = max(emotions, key=emotions.get)  # type: ignore
            results.append(EmotionResult(
                emotions=emotions,
                dominant=dominant,
                intensity=emotions[dominant],
            ))

        logger.info(f"  Processed batch {i // batch_size + 1}/{(len(truncated) - 1) // batch_size + 1}")

    # Log dominant emotion distribution
    from collections import Counter
    dist = Counter(r.dominant for r in results)
    top_3 = dist.most_common(3)
    logger.info(f"Top emotions: {top_3}")

    return results


def aggregate_emotions(
    results: list[EmotionResult],
    weights: list[float] | None = None,
) -> dict[str, float]:
    """
    Aggregate emotions across multiple texts, optionally weighted.

    Args:
        results: List of EmotionResult objects
        weights: Optional engagement weights per result

    Returns:
        Dict of averaged emotion scores
    """
    if not results:
        return {}

    if weights is None:
        weights = [1.0] * len(results)

    total_weight = sum(weights)
    aggregated: dict[str, float] = {}

    for result, weight in zip(results, weights):
        for emotion, score in result.emotions.items():
            aggregated[emotion] = aggregated.get(emotion, 0) + score * weight

    # Normalize
    return {k: round(v / total_weight, 4) for k, v in aggregated.items()}
