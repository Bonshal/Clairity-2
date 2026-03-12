"""Normalization functions for raw platform data."""

from datetime import datetime
from typing import Optional
import logging

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
    """Normalize Reddit data from MongoDB.
    
    IMPORTANT: The data in MongoDB is ALREADY normalized by fetch_reddit_data()
    (which calls _normalize_item internally). The items have keys like:
      external_id, text_content, data_type, body, title, upvotes, etc.
    
    We just need to map those keys to our preprocessing schema.
    We do NOT call _normalize_item again (that expects raw Apify keys).
    """
    items = []
    for raw in raw_items:
        try:
            # The data is already normalized — just map to preprocessing schema
            text_content = raw.get("text_content", "") or ""
            title = raw.get("title", "") or ""
            body = raw.get("body", "") or ""
            external_id = raw.get("external_id", "") or ""
            
            # Skip items with no text at all
            if not text_content and not title and not body:
                continue

            items.append({
                "platform": "reddit",
                "platform_id": external_id,
                "content_type": raw.get("data_type", "post"),
                "title": title,
                "body": body,
                "text": text_content or f"{title}\n\n{body}".strip(),
                "author": raw.get("author", ""),
                "url": raw.get("url", ""),
                "upvotes": raw.get("upvotes", 0) or 0,
                "likes": raw.get("upvotes", 0) or 0,
                "views": 0,
                "comments_count": raw.get("comment_count", 0) or 0,
                "shares": 0,
                "platform_created_at": raw.get("created_at"),
            })
        except Exception as e:
            logger.error(f"Failed to normalize reddit item: {e}")
            continue
            
    return items
