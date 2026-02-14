import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analysis")))

from src.state import PlatformState, CleanedDataRef, PlatformEnum
from src.agents.trend_agent import trend_agent
from src.agents.sentiment_agent import sentiment_agent
from src.agents.topic_agent import topic_agent
from src.db.neon import async_session, ContentItemModel
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_agents():
    # 1. Fetch existing content IDs from DB to construct a mock state
    logger.info("Fetching content IDs from DB...")
    async with async_session() as session:
        result = await session.execute(select(ContentItemModel.id))
        ids = [str(row[0]) for row in result.all()]
    
    if not ids:
        logger.error("No content found in DB. Run ingestion test first.")
        return

    logger.info(f"Found {len(ids)} items.")

    # Mock state
    mock_state = PlatformState(
        run_id="verify_test_run",
        niche_id="test_niche",
        active_platforms=[PlatformEnum.TWITTER, PlatformEnum.YOUTUBE],
        cleaned_data_refs=[
            CleanedDataRef(
                platform=PlatformEnum.TWITTER,
                item_count=len(ids),
                content_ids=ids,
                embedding_count=len(ids)
            )
        ]
    )

    # 2. Run Trend Agent
    logger.info("--- Testing Trend Agent ---")
    trend_result = await trend_agent(mock_state)
    print(f"Trends detected: {len(trend_result['trend_signals'])}")
    if trend_result['trend_signals']:
        print(f"Top trend: {trend_result['trend_signals'][0].keyword} ({trend_result['trend_signals'][0].direction})")

    # 3. Run Sentiment Agent
    logger.info("--- Testing Sentiment Agent ---")
    sent_result = await sentiment_agent(mock_state)
    print("Sentiment Summary:", sent_result['sentiment_summaries'][0])
    print("Emotion Summary:", sent_result['emotion_summaries'][0])

    # 4. Run Topic Agent
    logger.info("--- Testing Topic Agent ---")
    topic_result = await topic_agent(mock_state)
    print(f"Topics discovered: {topic_result['total_topics_discovered']}")
    if topic_result['topic_clusters']:
        print(f"Top Cluster: {topic_result['topic_clusters'][0].label}")

if __name__ == "__main__":
    asyncio.run(verify_agents())
