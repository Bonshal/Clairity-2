"""MongoDB Atlas async client using Motor."""

from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

client = AsyncIOMotorClient(settings.mongodb_uri)
db = client.market_research

# ─── Collections ──────────────────────────────────────────
raw_reddit = db.raw_reddit_posts
raw_twitter = db.raw_twitter_tweets
raw_youtube = db.raw_youtube_videos


async def store_raw_data(
    collection_name: str,
    items: list[dict],
    batch_id: str,
    api_source: str,
) -> int:
    """Store raw API responses in MongoDB."""
    from datetime import datetime, timezone

    collection = db[collection_name]
    documents = [
        {
            "raw_data": item,
            "batch_id": batch_id,
            "api_source": api_source,
            "fetch_timestamp": datetime.now(timezone.utc),
            "processed": False,
        }
        for item in items
    ]

    if documents:
        result = await collection.insert_many(documents)
        return len(result.inserted_ids)
    return 0


async def ping() -> bool:
    """Check MongoDB connection."""
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
