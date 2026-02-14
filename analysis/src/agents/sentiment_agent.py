"""Sentiment & Emotion Analysis Agent."""

import logging
import uuid
from datetime import datetime, timezone
from collections import Counter

from src.state import PlatformState, SentimentSummary, EmotionSummary
from src.db.neon import fetch_content_by_ids, SentimentResultModel, async_session
from src.ml.sentiment import analyze_sentiment_batch
from src.ml.emotions import detect_emotions_batch

logger = logging.getLogger(__name__)


async def sentiment_agent(state: PlatformState) -> dict:
    """
    Agent 4: Analyze sentiment and emotions of processed content.

    Reads: cleaned_data_refs
    Writes: sentiment_summaries, emotion_summaries
    """
    logger.info("[Sentiment Agent] Starting...")

    # 1. Gather all content IDs
    content_ids = []
    for ref in state.cleaned_data_refs:
        if ref.content_ids:
            content_ids.extend(ref.content_ids)

    if not content_ids:
        logger.warning("[Sentiment Agent] No content to analyze")
        return {
            "sentiment_summaries": [],
            "emotion_summaries": [],
        }

    # 2. Fetch content
    try:
        async with async_session() as session:
            items = await fetch_content_by_ids(session, content_ids)
    except Exception as e:
        logger.error(f"[Sentiment Agent] DB fetch failed: {e}")
        return {
            "sentiment_summaries": [],
            "emotion_summaries": [],
        }

    # Filter out items with no text
    valid_items = [
        item for item in items 
        if item.body or item.title
    ]
    texts = [
        (item.body or item.title or "") for item in valid_items
    ]
    ids = [item.id for item in valid_items]

    if not texts:
        logger.warning("[Sentiment Agent] No text found in items")
        return {
            "sentiment_summaries": [],
            "emotion_summaries": [],
        }

    # 3. Run Analysis
    logger.info(f"[Sentiment Agent] Analyzing {len(texts)} items")
    
    # Sentiment
    sentiments = analyze_sentiment_batch(texts, batch_size=32)
    
    # Emotions
    emotions = detect_emotions_batch(texts, batch_size=32)

    # 4. Save results to DB
    result_models = []
    timestamp = datetime.now(timezone.utc)
    
    for i, (sent, emo) in enumerate(zip(sentiments, emotions)):
        # Calculate max emotion
        
        result_models.append(SentimentResultModel(
            id=uuid.uuid4(),
            content_id=ids[i],
            sentiment=sent.label,
            sentiment_score=sent.score,
            emotions=emo.emotions,
            analyzed_at=timestamp,
        ))

    async with async_session() as session:
        session.add_all(result_models)
        await session.commit()
    
    logger.info(f"[Sentiment Agent] Saved {len(result_models)} results to DB")

    # 5. Aggregation for State
    # Overall Sentiment
    sent_counts = Counter(s.label for s in sentiments)
    total = len(sentiments)
    
    pos_ratio = sent_counts["positive"] / total
    neg_ratio = sent_counts["negative"] / total
    neu_ratio = sent_counts["neutral"] / total
    
    dominant_sent = sent_counts.most_common(1)[0][0]

    sent_summary = SentimentSummary(
        scope="overall",
        positive_ratio=round(pos_ratio, 3),
        negative_ratio=round(neg_ratio, 3),
        neutral_ratio=round(neu_ratio, 3),
        dominant_sentiment=dominant_sent, # type: ignore
        sample_size=total,
    )

    # Overall Emotions
    agg_emotions = {}
    for emo in emotions:
        for k, v in emo.emotions.items():
            agg_emotions[k] = agg_emotions.get(k, 0.0) + v
    
    # Average
    for k in agg_emotions:
        agg_emotions[k] = round(agg_emotions[k] / total, 4)
    
    dominant_emo = max(agg_emotions, key=agg_emotions.get) # type: ignore
    intensity = agg_emotions[dominant_emo]

    emo_summary = EmotionSummary(
        scope="overall",
        emotions=agg_emotions,
        dominant_emotion=dominant_emo,
        emotional_intensity=intensity,
        sample_size=total,
    )

    return {
        "sentiment_summaries": [sent_summary],
        "emotion_summaries": [emo_summary],
        "overall_sentiment": dominant_sent,
    }
