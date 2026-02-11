"""Reddit data fetcher via Apify."""

import os
import logging
from apify_client import ApifyClient

from src.config import settings

logger = logging.getLogger(__name__)
client = ApifyClient(token=settings.apify_token)


async def fetch_reddit_data(
    subreddits: list[str],
    limit: int = 500,
    sort: str = "hot",
) -> list[dict]:
    """
    Fetch Reddit posts via Apify's Reddit scraper.

    Args:
        subreddits: List of subreddit names (without r/)
        limit: Max items to fetch
        sort: Sort order ('hot', 'new', 'top')

    Returns:
        List of raw post dicts from Apify
    """
    logger.info(f"Fetching Reddit data: {subreddits}, limit={limit}, sort={sort}")

    try:
        run = client.actor("trudax/reddit-scraper").call(
            run_input={
                "startUrls": [
                    {"url": f"https://reddit.com/r/{sub}"} for sub in subreddits
                ],
                "maxItems": limit,
                "sort": sort,
                "proxy": {"useApifyProxy": True},
            },
            timeout_secs=300,
            memory_mbytes=512,
        )

        items = client.dataset(run["defaultDatasetId"]).list_items().items
        logger.info(f"Fetched {len(items)} Reddit items")
        return items

    except Exception as e:
        logger.error(f"Reddit fetch failed: {e}")
        raise
