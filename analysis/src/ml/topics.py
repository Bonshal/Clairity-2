"""Topic modeling pipeline using BERTopic."""

import logging
from dataclasses import dataclass
from bertopic import BERTopic
import numpy as np

logger = logging.getLogger(__name__)

_model: BERTopic | None = None


@dataclass
class TopicResult:
    """Topic modeling result."""
    topic_id: int
    label: str
    keywords: list[str]
    doc_count: int
    representative_doc_indices: list[int]


def get_model(
    nr_topics: str | int = "auto",
    min_topic_size: int = 10,
) -> BERTopic:
    """
    Get or create a BERTopic model.

    Uses pre-computed embeddings to avoid re-encoding with sentence-transformers.
    """
    global _model
    if _model is None:
        logger.info("Initializing BERTopic model")
        _model = BERTopic(
            nr_topics=nr_topics,
            min_topic_size=min_topic_size,
            calculate_probabilities=True,
            verbose=True,
        )
    return _model


def run_topic_modeling(
    texts: list[str],
    embeddings: np.ndarray | None = None,
    min_topic_size: int = 10,
) -> list[TopicResult]:
    """
    Run topic modeling on a collection of texts.

    Args:
        texts: List of document texts
        embeddings: Pre-computed embeddings (from processing/embeddings.py)
        min_topic_size: Minimum docs per topic cluster

    Returns:
        List of TopicResult objects
    """
    logger.info(f"Running BERTopic on {len(texts)} documents")

    model = get_model(min_topic_size=min_topic_size)

    # Fit the model (use pre-computed embeddings if available)
    topics, probs = model.fit_transform(texts, embeddings=embeddings)

    # Extract topic info
    topic_info = model.get_topic_info()
    results: list[TopicResult] = []

    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        if topic_id == -1:
            continue  # Skip outlier cluster

        # Get top keywords for this topic
        topic_words = model.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:10]] if topic_words else []

        # Get representative document indices
        rep_docs = []
        try:
            rep_docs_data = model.get_representative_docs(topic_id)
            if rep_docs_data:
                rep_docs = [texts.index(doc) for doc in rep_docs_data[:5] if doc in texts]
        except Exception:
            pass

        # Generate a readable label
        label = " | ".join(keywords[:3]) if keywords else f"Topic {topic_id}"

        results.append(TopicResult(
            topic_id=topic_id,
            label=label,
            keywords=keywords,
            doc_count=int(row.get("Count", 0)),
            representative_doc_indices=rep_docs,
        ))

    logger.info(f"Discovered {len(results)} topics (excluded outliers)")

    return results


def get_topic_for_text(text: str, model: BERTopic | None = None) -> int:
    """Get the topic assignment for a single text."""
    m = model or get_model()
    topics, _ = m.transform([text])
    return topics[0]
