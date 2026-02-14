"""
Reddit data fetcher via Apify (trudax/reddit-scraper).

Actor: https://apify.com/trudax/reddit-scraper
Actor ID: tW0tdmu7XAIoNezk2

Supports two ingestion modes:
  1. Search-based: Fetches posts/comments matching niche keywords.
  2. URL-based:    Fetches posts from specific subreddit URLs.
"""

import logging
import hashlib
from datetime import datetime, timezone
from typing import Optional
import asyncio
from apify_client import ApifyClient

from src.config import settings

logger = logging.getLogger(__name__)

ACTOR_ID = "fatihtahta/reddit-scraper-search-fast"
DEFAULT_MAX_ITEMS = 500
DEFAULT_MAX_POST_COUNT = 100
DEFAULT_MAX_COMMENTS = 50
DEFAULT_SCROLL_TIMEOUT = 40
DEFAULT_TIMEOUT_SECS = 600
DEFAULT_MEMORY_MBYTES = 1024


def _get_client() -> ApifyClient:
    """Create an Apify client with the configured token."""
    if not settings.apify_token or settings.apify_token == "apify_api_xxx":
        raise ValueError(
            "APIFY_TOKEN is not set. Please add a valid Apify API token "
            "to your .env file."
        )
    return ApifyClient(token=settings.apify_token)


def _content_hash(text: str) -> str:
    """Generate SHA-256 hash for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_post_fast(raw: dict) -> dict:
    """Normalize a raw post from fatihtahta/reddit-scraper-search-fast."""
    # This actor outputs field 'selftext' for body, 'title' for title
    body = raw.get("selftext", "") or ""
    title = raw.get("title", "") or ""
    text_content = f"{title}\n\n{body}".strip()

    # Handle timestamp safely
    created_utc = raw.get("created_utc", 0)
    try:
        if created_utc:
            created_at = datetime.fromtimestamp(float(created_utc), timezone.utc).isoformat()
        else:
            created_at = ""
    except (ValueError, OSError, TypeError):
        created_at = datetime.now(timezone.utc).isoformat()

    return {
        "external_id": str(raw.get("id", "")),
        "platform": "reddit",
        "data_type": "post",
        "url": raw.get("url", ""),
        "author": raw.get("author", ""),
        "title": title,
        "body": body,
        "text_content": text_content,
        "content_hash": _content_hash(text_content),
        "subreddit": raw.get("subreddit", ""),
        # This actor puts 'subreddit_name_prefixed' e.g. "r/AI"
        "community_name": raw.get("subreddit_name_prefixed", "").replace("r/", ""),
        "upvotes": int(raw.get("score", 0)),
        "comment_count": int(raw.get("num_comments", 0)),
        "engagement_score": float(raw.get("score", 0) + (raw.get("num_comments", 0) * 2)),
        "is_video": raw.get("is_video", False),
        "is_ad": False, 
        "is_nsfw": raw.get("over_18", False),
        "created_at": created_at,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_data": raw,
    }

def _normalize_comment_fast(raw: dict) -> dict:
    """Normalize a raw comment from fatihtahta/reddit-scraper-search-fast."""
    body = raw.get("body", "") or ""
    
    # Handle timestamp safely
    created_utc = raw.get("created_utc", 0)
    try:
        if created_utc:
            created_at = datetime.fromtimestamp(float(created_utc), timezone.utc).isoformat()
        else:
            created_at = ""
    except (ValueError, OSError, TypeError):
        created_at = datetime.now(timezone.utc).isoformat()
    
    return {
        "external_id": str(raw.get("id", "")),
        "platform": "reddit",
        "data_type": "comment",
        "url": f"https://www.reddit.com{raw.get('permalink', '')}", 
        "author": raw.get("author", ""),
        "title": "",
        "body": body,
        "text_content": body,
        "content_hash": _content_hash(body),
        "subreddit": raw.get("subreddit", ""),
        "community_name": raw.get("subreddit_name_prefixed", "").replace("r/", ""),
        "parent_id": raw.get("parent_id", ""),
        "upvotes": int(raw.get("score", 0)),
        "reply_count": 0,
        "engagement_score": float(raw.get("score", 0)),
        "is_nsfw": False,
        "created_at": created_at,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_data": raw,
    }

def _normalize_item(raw: dict) -> dict:
    """Route to the correct normalizer based on 'kind' or inferred type."""
    # fatihtahta actor returns 'kind': 't3' (post) or 't1' (comment)
    kind = raw.get("kind", "")
    if kind == "t1":
        return _normalize_comment_fast(raw)
    elif kind == "t3":
        return _normalize_post_fast(raw)
        
    # Infer if kind is missing
    if "body" in raw and "title" not in raw:
         return _normalize_comment_fast(raw)
    return _normalize_post_fast(raw)

def _calculate_engagement(raw: dict) -> float:
    # Kept primarily for backward comp or logic if needed
    return float(raw.get("score", 0) + (raw.get("num_comments", 0) * 2))


async def fetch_reddit_by_search(
    keywords: list[str],
    max_items: int = DEFAULT_MAX_ITEMS,
    max_post_count: int = DEFAULT_MAX_POST_COUNT,
    max_comments: int = DEFAULT_MAX_COMMENTS,
    sort: str = "new",
    time_filter: str = "week",
    search_posts: bool = True,
    search_comments: bool = True,
    search_communities: bool = False,
    community_name: Optional[str] = None,
) -> list[dict]:
    """
    Fetch Reddit data by searching for keywords.
    """
    client = _get_client()

    # Clean keywords (remove type:comment hacks if present)
    clean_keywords = [k.replace(" type:comment", "") for k in keywords]

    run_input = {
        "queries": clean_keywords,
        "maxPosts": max_items,  # Caps total posts
        "scrapeComments": True,
        "maxComments": max_comments, 
        "sort": sort,
        "timeframe": time_filter,
        "includeNsfw": False,
    }
    
    if community_name:
         run_input["subreddit"] = community_name

    logger.info(
        f"[Reddit Search] queries={clean_keywords}, sort={sort}, "
        f"max_items={max_items} (using fatihtahta/reddit-scraper-search-fast)"
    )

    try:
        actor = client.actor(ACTOR_ID)
        run = await asyncio.to_thread(
            actor.call,
            run_input=run_input,
            timeout_secs=DEFAULT_TIMEOUT_SECS,
            memory_mbytes=DEFAULT_MEMORY_MBYTES,
        )

        dataset = client.dataset(run["defaultDatasetId"])
        dataset_list = await asyncio.to_thread(dataset.list_items)
        raw_items = dataset_list.items
        logger.info(f"[Reddit Search] Fetched {len(raw_items)} raw items")

        normalized = _deduplicate([_normalize_item(item) for item in raw_items])
        logger.info(
            f"[Reddit Search] After normalization & dedup: {len(normalized)} items "
            f"({_count_by_type(normalized)})"
        )
        return normalized

    except Exception as e:
        logger.error(f"[Reddit Search] Failed: {e}", exc_info=True)
        raise


async def fetch_reddit_by_urls(
    subreddits: list[str],
    max_items: int = DEFAULT_MAX_ITEMS,
    max_post_count: int = DEFAULT_MAX_POST_COUNT,
    max_comments: int = DEFAULT_MAX_COMMENTS,
    sort: str = "hot",
) -> list[dict]:
    """
    Fetch Reddit data from specific subreddit URLs.
    """
    client = _get_client()

    start_urls = [
        {"url": f"https://www.reddit.com/r/{sub}/{sort}"}
        for sub in subreddits
    ]

    run_input = {
        "startUrls": start_urls,
        "maxItems": max_items,
        "maxPostCount": max_post_count,
        "maxComments": max_comments,
        "scrollTimeout": DEFAULT_SCROLL_TIMEOUT,
        "skipComments": False,
        "includeNSFW": False,
        "proxy": {"useApifyProxy": True},
    }

    logger.info(
        f"[Reddit URLs] subreddits={subreddits}, sort={sort}, "
        f"max_items={max_items}"
    )

    try:
        actor = client.actor(ACTOR_ID)
        run = await asyncio.to_thread(
            actor.call,
            run_input=run_input,
            timeout_secs=DEFAULT_TIMEOUT_SECS,
            memory_mbytes=DEFAULT_MEMORY_MBYTES,
        )

        dataset = client.dataset(run["defaultDatasetId"])
        dataset_list = await asyncio.to_thread(dataset.list_items)
        raw_items = dataset_list.items
        logger.info(f"[Reddit URLs] Fetched {len(raw_items)} raw items")

        normalized = _deduplicate([_normalize_item(item) for item in raw_items])
        logger.info(
            f"[Reddit URLs] After normalization & dedup: {len(normalized)} items "
            f"({_count_by_type(normalized)})"
        )
        return normalized

    except Exception as e:
        logger.error(f"[Reddit URLs] Failed: {e}", exc_info=True)
        raise


async def fetch_reddit_data(
    keywords: list[str],
    subreddits: Optional[list[str]] = None,
    max_items: int = DEFAULT_MAX_ITEMS,
    max_post_count: int = DEFAULT_MAX_POST_COUNT,
    max_comments: int = DEFAULT_MAX_COMMENTS,
    sort: str = "new",
    time_filter: str = "week",
) -> list[dict]:
    """
    Main entry point for the Ingestion Agent.

    Combines both search-based and URL-based fetching strategies.
    """
    all_items: list[dict] = []

    # Strategy 1: Search by keywords (always runs)
    logger.info(f"[Reddit Pipeline] Starting keyword search: {keywords}")
    search_results = await fetch_reddit_by_search(
        keywords=keywords,
        max_items=max_items,
        max_post_count=max_post_count,
        max_comments=max_comments,
        sort=sort,
        time_filter=time_filter,
    )
    all_items.extend(search_results)

    # Strategy 2: Fetch from specific subreddits (optional)
    if subreddits:
        logger.info(f"[Reddit Pipeline] Starting subreddit fetch: {subreddits}")
        url_results = await fetch_reddit_by_urls(
            subreddits=subreddits,
            max_items=max_items,
            max_post_count=max_post_count,
            max_comments=max_comments,
            sort=sort if sort in ("hot", "new", "top") else "hot",
        )
        all_items.extend(url_results)

    # Final deduplication across both strategies
    final = _deduplicate(all_items)

    posts = sum(1 for i in final if i["data_type"] == "post")
    comments = sum(1 for i in final if i["data_type"] == "comment")

    logger.info(
        f"[Reddit Pipeline] Complete — {len(final)} unique items "
        f"({posts} posts, {comments} comments)"
    )
    return final


def _deduplicate(items: list[dict]) -> list[dict]:
    """Deduplicate items by content_hash."""
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        h = item.get("content_hash", "")
        if h and h not in seen:
            seen.add(h)
            unique.append(item)
    return unique


def _count_by_type(items: list[dict]) -> str:
    """Return a human-readable count by data type."""
    posts = sum(1 for i in items if i.get("data_type") == "post")
    comments = sum(1 for i in items if i.get("data_type") == "comment")
    return f"{posts} posts, {comments} comments"
