"""Topic Clustering Agent — discovers topic clusters using BERTopic."""

import logging
import uuid
import numpy as np
from datetime import datetime, timezone

from src.state import PlatformState, TopicCluster as TopicClusterState
from src.ml.topics import run_topic_modeling
from src.db.neon import get_session, fetch_content_by_ids, TopicClusterModel, async_session

logger = logging.getLogger(__name__)


async def topic_agent(state: PlatformState) -> dict:
    """
    Agent 5: Run topic modeling on processed content.

    Reads: cleaned_data_refs
    Writes: topic_clusters, total_topics_discovered
    """
    logger.info("[Topic Agent] Starting...")

    # 1. Gather all content IDs
    content_ids = []
    for ref in state.cleaned_data_refs:
        if ref.content_ids:
            content_ids.extend(ref.content_ids)

    if not content_ids:
        logger.warning("[Topic Agent] No content to analyze")
        return {
            "topic_clusters": [],
            "total_topics_discovered": 0,
        }

    # 2. Fetch content with embeddings
    items = []
    try:
        async with async_session() as session:
            fetched = await fetch_content_by_ids(session, content_ids)
            # Filter items that have embeddings
            items = [item for item in fetched if item.embedding is not None and (item.body or item.title)]
    except Exception as e:
        logger.error(f"[Topic Agent] DB fetch failed: {e}")
        return {
            "topic_clusters": [],
            "total_topics_discovered": 0,
        }

    if not items:
        logger.warning("[Topic Agent] No items with embeddings found")
        return {
            "topic_clusters": [],
            "total_topics_discovered": 0,
        }

    texts = [(item.body or item.title or "") for item in items]
    # Convert list of vectors to numpy array
    embeddings = np.array([item.embedding for item in items])

    # 3. Run BERTopic
    logger.info(f"[Topic Agent] Running modeling on {len(texts)} docs with embeddings shape {embeddings.shape}")
    
    try:
        topic_results = run_topic_modeling(
            texts=texts,
            embeddings=embeddings,
            min_topic_size=min(10, len(texts) // 5 + 1), # Dynamic min_size for small batches
        )
    except Exception as e:
        logger.error(f"[Topic Agent] BERTopic failed: {e}")
        return {
            "topic_clusters": [],
            "total_topics_discovered": 0,
        }

    # 4. Save clusters to DB
    cluster_models = []
    timestamp = datetime.now(timezone.utc)
    
    clusters = []

    for r in topic_results:
        # Map generic result to TopicClusterState
        cluster_state = TopicClusterState(
            cluster_id=r.topic_id,
            label=r.label,
            keywords=r.keywords,
            doc_count=r.doc_count,
            representative_doc_ids=[str(items[i].id) for i in r.representative_doc_indices],
            avg_sentiment=0.0,  # Placeholder, computed later
            dominant_emotion="neutral",  # Placeholder
        )
        clusters.append(cluster_state)

        # Create DB model
        cluster_models.append(TopicClusterModel(
            id=uuid.uuid4(),
            cluster_label=r.label,
            keywords=r.keywords,
            representative_docs=[items[i].id for i in r.representative_doc_indices],
            doc_count=r.doc_count,
            avg_sentiment=None,
            created_at=timestamp,
            analysis_run_id=state.run_id,
        ))

    if cluster_models:
        async with async_session() as session:
            session.add_all(cluster_models)
            await session.commit()
        logger.info(f"[Topic Agent] Saved {len(cluster_models)} clusters to DB")

    logger.info(f"[Topic Agent] Complete. Discovered {len(clusters)} topics")

    return {
        "topic_clusters": clusters,
        "total_topics_discovered": len(clusters),
    }
