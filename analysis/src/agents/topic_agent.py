"""Topic Clustering Agent — discovers topic clusters using BERTopic."""

import logging
from src.state import PlatformState, TopicCluster as TopicClusterState
from src.ml.topics import run_topic_modeling

logger = logging.getLogger(__name__)


async def topic_agent(state: PlatformState) -> dict:
    """
    Agent 5: Run topic modeling on processed content.

    Reads: cleaned_data_refs
    Writes: topic_clusters, total_topics_discovered
    """
    logger.info("[Topic Agent] Starting...")

    # TODO: Load content texts + embeddings from Neon
    all_texts: list[str] = []
    all_embeddings = None  # numpy array from pgvector

    if not all_texts:
        logger.warning("[Topic Agent] No texts available for topic modeling")
        return {
            "topic_clusters": [],
            "total_topics_discovered": 0,
        }

    # Run BERTopic
    topic_results = run_topic_modeling(
        texts=all_texts,
        embeddings=all_embeddings,
        min_topic_size=10,
    )

    # Convert to state schema
    clusters = [
        TopicClusterState(
            cluster_id=r.topic_id,
            label=r.label,
            keywords=r.keywords,
            doc_count=r.doc_count,
            representative_doc_ids=[str(i) for i in r.representative_doc_indices],
            avg_sentiment=0.0,  # TODO: cross-reference with sentiment results
            dominant_emotion="neutral",  # TODO: cross-reference with emotion results
        )
        for r in topic_results
    ]

    logger.info(f"[Topic Agent] Complete. Discovered {len(clusters)} topics")

    return {
        "topic_clusters": clusters,
        "total_topics_discovered": len(clusters),
    }
