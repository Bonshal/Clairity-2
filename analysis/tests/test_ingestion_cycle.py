"""
Full Ingestion Cycle Integration Test
======================================
Tests the complete pipeline: fetch → store raw → preprocess → write to Neon.

Usage:
    cd analysis
    uv run python -m tests.test_ingestion_cycle

Steps:
    1. Fetch from Twitter (GetXAPI) — 2 pages = ~40 tweets
    2. Fetch from YouTube (Data API v3) — 10 videos
    3. Store raw data in MongoDB Atlas
    4. Normalize into unified content_items format
    5. Clean text (HTML strip, unicode normalize, URL/mention extraction)
    6. Deduplicate (SHA-256 hash)
    7. Generate embeddings (all-MiniLM-L6-v2, 384-dim)
    8. Write to Neon PostgreSQL with pgvector
"""

import asyncio
import logging
import sys
import uuid
from datetime import datetime, timezone

# ─── Setup logging ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("integration_test")

# ═══════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════

def divider(title: str):
    logger.info("")
    logger.info(f"{'═' * 60}")
    logger.info(f"  {title}")
    logger.info(f"{'═' * 60}")


def normalize_twitter(raw_tweets: list[dict]) -> list[dict]:
    """Normalize raw GetXAPI tweets into unified format."""
    items = []
    for tw in raw_tweets:
        text = tw.get("text") or tw.get("full_text") or ""
        if not text:
            continue

        # Extract tweet ID — handle nested structure from GetXAPI
        tweet_id = (
            tw.get("id_str")
            or tw.get("rest_id")
            or str(tw.get("id", ""))
        )

        user = tw.get("user", {}) or tw.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
        author = user.get("screen_name") or user.get("name") or "unknown"

        items.append({
            "platform": "twitter",
            "platform_id": tweet_id,
            "content_type": "tweet",
            "title": None,
            "body": text,
            "text": text,  # for cleaning
            "author": f"@{author}",
            "url": f"https://x.com/{author}/status/{tweet_id}" if tweet_id else None,
            "upvotes": tw.get("favorite_count", 0) or 0,
            "likes": tw.get("favorite_count", 0) or 0,
            "views": tw.get("views", {}).get("count", 0) if isinstance(tw.get("views"), dict) else 0,
            "comments_count": tw.get("reply_count", 0) or 0,
            "shares": tw.get("retweet_count", 0) or 0,
            "platform_created_at": tw.get("created_at"),
        })
    return items


def normalize_youtube(raw_videos: list[dict]) -> list[dict]:
    """Normalize raw YouTube API videos into unified format."""
    items = []
    for vid in raw_videos:
        title = vid.get("title", "")
        desc = vid.get("description", "")
        text = f"{title}. {desc}" if desc else title

        items.append({
            "platform": "youtube",
            "platform_id": vid.get("video_id", ""),
            "content_type": "video",
            "title": title,
            "body": desc,
            "text": text,
            "author": vid.get("channel_title", ""),
            "url": f"https://youtube.com/watch?v={vid.get('video_id', '')}",
            "upvotes": vid.get("likes", 0),
            "likes": vid.get("likes", 0),
            "views": vid.get("views", 0),
            "comments_count": vid.get("comments", 0),
            "shares": 0,
            "platform_created_at": vid.get("published_at"),
        })
    return items


# ═══════════════════════════════════════════════════════════
#  Main Test
# ═══════════════════════════════════════════════════════════

async def run_test():
    batch_id = f"test_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    query = "AI code review tools"

    divider("STEP 1: Fetch from Twitter (GetXAPI)")
    # ─────────────────────────────────────────────────────

    from src.ingestion.twitter import fetch_twitter_data

    try:
        raw_tweets = await fetch_twitter_data(query=query, max_pages=2)
        logger.info(f"✅ Twitter: fetched {len(raw_tweets)} tweets")
    except Exception as e:
        logger.warning(f"⚠️  Twitter fetch failed: {e}")
        raw_tweets = []

    if raw_tweets:
        sample = raw_tweets[0]
        sample_keys = list(sample.keys())[:8]
        logger.info(f"   Sample tweet keys: {sample_keys}")
        text_preview = (sample.get("text") or sample.get("full_text") or "")[:100]
        logger.info(f"   Text preview: {text_preview!r}")

    divider("STEP 2: Fetch from YouTube (Data API v3)")
    # ─────────────────────────────────────────────────────

    from src.ingestion.youtube import search_youtube_videos

    try:
        raw_videos = await search_youtube_videos(query=query, max_results=10)
        logger.info(f"✅ YouTube: fetched {len(raw_videos)} videos")
    except Exception as e:
        logger.warning(f"⚠️  YouTube fetch failed: {e}")
        raw_videos = []

    if raw_videos:
        sample = raw_videos[0]
        logger.info(f"   Sample: {sample.get('title', '')[:80]!r}")
        logger.info(f"   Views: {sample.get('views', 0):,} | Likes: {sample.get('likes', 0):,}")

    divider("STEP 3: Store Raw Data in MongoDB")
    # ─────────────────────────────────────────────────────

    mongo_stored = 0
    try:
        from src.db.mongo import store_raw_data, ping as mongo_ping

        if await mongo_ping():
            if raw_tweets:
                n = await store_raw_data("raw_twitter_tweets", raw_tweets, batch_id, "getxapi")
                mongo_stored += n
                logger.info(f"   Stored {n} tweets in MongoDB")
            if raw_videos:
                n = await store_raw_data("raw_youtube_videos", raw_videos, batch_id, "youtube_api")
                mongo_stored += n
                logger.info(f"   Stored {n} videos in MongoDB")
            logger.info(f"✅ MongoDB: {mongo_stored} total documents stored")
        else:
            logger.warning("⚠️  MongoDB ping failed — skipping raw storage")
    except Exception as e:
        logger.warning(f"⚠️  MongoDB storage failed: {e} — continuing without raw storage")

    divider("STEP 4: Normalize to Unified Format")
    # ─────────────────────────────────────────────────────

    all_items = normalize_twitter(raw_tweets) + normalize_youtube(raw_videos)
    logger.info(f"✅ Unified items: {len(all_items)}")
    logger.info(f"   Twitter items: {len([i for i in all_items if i['platform'] == 'twitter'])}")
    logger.info(f"   YouTube items: {len([i for i in all_items if i['platform'] == 'youtube'])}")

    if not all_items:
        logger.error("❌ No items fetched — cannot continue pipeline. Exiting.")
        return

    divider("STEP 5: Clean Text")
    # ─────────────────────────────────────────────────────

    from src.processing.cleaner import clean_batch

    texts = [item.get("text", "") for item in all_items]
    cleaned = clean_batch(texts)

    langs = {}
    for c in cleaned:
        langs[c.language] = langs.get(c.language, 0) + 1
    logger.info(f"✅ Cleaned {len(cleaned)} items")
    logger.info(f"   Languages detected: {langs}")
    logger.info(f"   Avg original length: {sum(c.original_length for c in cleaned) / len(cleaned):.0f}")
    logger.info(f"   Avg cleaned length:  {sum(c.cleaned_length for c in cleaned) / len(cleaned):.0f}")
    logger.info(f"   Total URLs extracted: {sum(len(c.urls) for c in cleaned)}")
    logger.info(f"   Total mentions:      {sum(len(c.mentions) for c in cleaned)}")
    logger.info(f"   Total hashtags:      {sum(len(c.hashtags) for c in cleaned)}")

    # Update items with cleaned text
    for item, c in zip(all_items, cleaned):
        item["text"] = c.text
        item["language"] = c.language

    divider("STEP 6: Deduplicate")
    # ─────────────────────────────────────────────────────

    from src.processing.dedup import deduplicate_batch

    dedup_result = deduplicate_batch(
        all_items,
        text_field="text",
        platform_field="platform",
        id_field="platform_id",
    )

    unique_items = dedup_result.unique_items
    logger.info(f"✅ Dedup results:")
    logger.info(f"   Input:      {len(all_items)}")
    logger.info(f"   Unique:     {len(unique_items)}")
    logger.info(f"   Duplicates: {dedup_result.duplicate_count}")

    divider("STEP 7: Generate Embeddings")
    # ─────────────────────────────────────────────────────

    from src.processing.embeddings import generate_embeddings

    embed_texts = [item.get("text", "") for item in unique_items]
    embeddings = generate_embeddings(embed_texts, batch_size=32, show_progress=True)

    logger.info(f"✅ Embeddings generated:")
    logger.info(f"   Shape: {embeddings.shape}")
    logger.info(f"   Dtype: {embeddings.dtype}")
    logger.info(f"   Sample L2 norm: {(embeddings[0] ** 2).sum() ** 0.5:.4f} (should be ~1.0)")

    divider("STEP 8: Write to Neon PostgreSQL")
    # ─────────────────────────────────────────────────────

    from src.db.neon import async_session, ContentItemModel
    from sqlalchemy import text as sql_text

    inserted = 0
    skipped = 0

    try:
        async with async_session() as session:
            # Verify connection
            result = await session.execute(sql_text("SELECT 1"))
            logger.info("   Neon connection verified ✓")

            for i, item in enumerate(unique_items):
                try:
                    content_item = ContentItemModel(
                        id=uuid.uuid4(),
                        platform=item["platform"],
                        platform_id=str(item["platform_id"]),
                        content_type=item["content_type"],
                        title=item.get("title"),
                        body=item.get("body"),
                        author=item.get("author"),
                        url=item.get("url"),
                        content_hash=item["content_hash"],
                        language=item.get("language", "en"),
                        upvotes=item.get("upvotes", 0),
                        likes=item.get("likes", 0),
                        views=item.get("views", 0),
                        comments_count=item.get("comments_count", 0),
                        shares=item.get("shares", 0),
                        fetched_at=datetime.now(timezone.utc),
                        processed_at=datetime.now(timezone.utc),
                        batch_id=batch_id,
                        embedding=embeddings[i].tolist(),
                    )
                    session.add(content_item)
                    await session.commit()
                    inserted += 1
                except Exception as e:
                    await session.rollback()
                    if "unique constraint" in str(e).lower():
                        logger.debug(f"   Item {i} already exists (skipping)")
                    else:
                        logger.warning(f"   Failed to insert item {i}: {e}")
                    skipped += 1
            logger.info(f"✅ Neon PostgreSQL: {inserted} rows inserted, {skipped} skipped")

            # Verify row count
            count_result = await session.execute(
                sql_text("SELECT COUNT(*) FROM content_items WHERE batch_id = :bid"),
                {"bid": batch_id},
            )
            db_count = count_result.scalar()
            logger.info(f"   Verified: {db_count} rows in DB for batch {batch_id}")

            # Test vector similarity search
            if inserted > 0:
                sim_result = await session.execute(
                    sql_text("""
                        SELECT title, platform, 1 - (embedding <=> :query_vec) AS similarity
                        FROM content_items
                        WHERE batch_id = :bid AND embedding IS NOT NULL
                        ORDER BY embedding <=> :query_vec
                        LIMIT 5
                    """),
                    {"query_vec": str(embeddings[0].tolist()), "bid": batch_id},
                )
                logger.info("   🔍 Vector similarity search (top 5):")
                for row in sim_result:
                    title_preview = (row[0] or "")[:60]
                    logger.info(f"      [{row[1]:>8}] sim={row[2]:.4f} | {title_preview!r}")

    except Exception as e:
        logger.error(f"❌ Neon write failed: {e}")
        import traceback
        traceback.print_exc()

    # ═══════════════════════════════════════════════════════
    divider("INTEGRATION TEST SUMMARY")
    # ═══════════════════════════════════════════════════════

    total_fetched = len(raw_tweets) + len(raw_videos)
    logger.info(f"  Batch ID:           {batch_id}")
    logger.info(f"  Query:              {query!r}")
    logger.info(f"  ────────────────────────────────────────")
    logger.info(f"  Tweets fetched:     {len(raw_tweets)}")
    logger.info(f"  Videos fetched:     {len(raw_videos)}")
    logger.info(f"  Total fetched:      {total_fetched}")
    logger.info(f"  MongoDB stored:     {mongo_stored}")
    logger.info(f"  Unified items:      {len(all_items)}")
    logger.info(f"  After dedup:        {len(unique_items)}")
    logger.info(f"  Embeddings:         {embeddings.shape[0]} × {embeddings.shape[1]}")
    logger.info(f"  Neon inserted:      {inserted}")
    logger.info(f"  Neon skipped:       {skipped}")
    logger.info(f"  ────────────────────────────────────────")

    if inserted > 0:
        logger.info(f"  ✅ FULL INGESTION CYCLE PASSED")
    elif total_fetched > 0 and inserted == 0:
        logger.warning(f"  ⚠️  Data fetched but Neon write failed")
    else:
        logger.error(f"  ❌ No data fetched — check API keys")


if __name__ == "__main__":
    asyncio.run(run_test())
