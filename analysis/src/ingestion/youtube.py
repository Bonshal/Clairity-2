"""YouTube data fetcher via official YouTube Data API v3."""

import logging
from googleapiclient.discovery import build

from src.config import settings

logger = logging.getLogger(__name__)

youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)


async def search_youtube_videos(
    query: str,
    max_results: int = 50,
    published_after: str = "2025-01-01T00:00:00Z",
) -> list[dict]:
    """
    Search YouTube videos. Quota cost: 100 units per search.list call.
    With 10K units/day: ~100 search calls/day.

    Args:
        query: Search query string
        max_results: Max results (capped at 50 per API call)
        published_after: ISO 8601 date filter

    Returns:
        List of video detail dicts with stats
    """
    logger.info(f"Searching YouTube: query='{query}', max_results={max_results}")

    try:
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=min(max_results, 50),
            order="relevance",
            publishedAfter=published_after,
        )
        response = request.execute()

        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        logger.info(f"Found {len(video_ids)} videos")

        if not video_ids:
            return []

        return await get_video_details(video_ids)

    except Exception as e:
        logger.error(f"YouTube search failed: {e}")
        raise


async def get_video_details(video_ids: list[str]) -> list[dict]:
    """
    Get detailed video stats. Quota cost: 1 unit per video.

    Args:
        video_ids: List of YouTube video IDs

    Returns:
        List of video detail dicts with engagement stats
    """
    logger.info(f"Fetching details for {len(video_ids)} videos")

    try:
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids),
        )
        response = request.execute()

        videos = [
            {
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "channel_id": item["snippet"]["channelId"],
                "channel_title": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "tags": item["snippet"].get("tags", []),
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comments": int(item["statistics"].get("commentCount", 0)),
                "duration": item["contentDetails"].get("duration"),
            }
            for item in response.get("items", [])
        ]

        logger.info(f"Got details for {len(videos)} videos")
        return videos

    except Exception as e:
        logger.error(f"YouTube video details failed: {e}")
        raise
