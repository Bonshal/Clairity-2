"""Normalization functions for raw platform data."""

from datetime import datetime
from typing import Optional
import logging
from src.ingestion.reddit import _normalize_item

logger = logging.getLogger(__name__)

def normalize_twitter_data(raw_items: list[dict]) -> list[dict]:
    """Normalize raw Twitter/GetXAPI data."""
    items = []
    for tw in raw_items:
        text = tw.get("text") or tw.get("full_text") or ""
        if not text:
            continue

        # Extract tweet ID
        tweet_id = (
            tw.get("id_str")
            or tw.get("rest_id")
            or str(tw.get("id", ""))
        )

        user = tw.get("user", {}) or tw.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
        author = user.get("screen_name") or user.get("name") or "unknown"
        
        # Parse timestamp if available
        created_at: Optional[datetime] = None
        # TODO: parse specific format if needed

        items.append({
            "platform": "twitter",
            "platform_id": tweet_id,
            "content_type": "tweet",
            "title": None,
            "body": text,
            "text": text,  # used for cleaning
            "author": f"@{author}",
            "url": f"https://x.com/{author}/status/{tweet_id}" if tweet_id else None,
            "upvotes": tw.get("favorite_count", 0) or 0,
            "likes": tw.get("favorite_count", 0) or 0,
            "views": tw.get("views", {}).get("count", 0) if isinstance(tw.get("views"), dict) else 0,
            "comments_count": tw.get("reply_count", 0) or 0,
            "shares": tw.get("retweet_count", 0) or 0,
            "platform_created_at": created_at,
        })
    return items

def normalize_youtube_data(raw_items: list[dict]) -> list[dict]:
    """Normalize raw YouTube API data."""
    items = []
    for vid in raw_items:
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
            "platform_created_at": None, # complex parsing needed
        })
    return items

def normalize_reddit_data(raw_items: list[dict]) -> list[dict]:
    """Normalize raw Reddit Apify data."""
    items = []
    for raw in raw_items:
        try:
            norm = _normalize_item(raw)
            if not norm:
                continue

            items.append({
                "platform": "reddit",
                "platform_id": norm.get("external_id"),
                "content_type": norm.get("data_type", "post"),
                "title": norm.get("title"),
                "body": norm.get("body"),
                "text": norm.get("text_content"),  # used for cleaning
                "author": norm.get("author"),
                "url": norm.get("url"),
                "upvotes": norm.get("upvotes", 0),
                "likes": norm.get("upvotes", 0),
                "views": 0,
                "comments_count": norm.get("comment_count", 0),
                "shares": 0,
                "platform_created_at": norm.get("created_at"), # datetime or string? _normalize_post_fast returns isoformat string.
            })
        except Exception as e:
            logger.error(f"Failed to normalize reddit item: {e}")
            continue
            
    return items
