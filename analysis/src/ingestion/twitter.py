"""X/Twitter data fetcher via GetXAPI."""

import logging
import httpx

from src.config import settings

logger = logging.getLogger(__name__)

GETXAPI_BASE = "https://api.getxapi.com"


async def fetch_twitter_data(
    query: str,
    max_pages: int = 50,
) -> list[dict]:
    """
    Fetch tweets via GetXAPI advanced search.

    Cost: $0.001 per API call (~20 tweets/call).
    50 pages = 50 calls = $0.05 = ~1000 tweets.

    Args:
        query: Twitter search query (supports advanced operators)
        max_pages: Max pages to paginate through

    Returns:
        List of raw tweet dicts
    """
    logger.info(f"Fetching Twitter data: query='{query}', max_pages={max_pages}")

    headers = {
        "Authorization": f"Bearer {settings.getxapi_api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    all_tweets: list[dict] = []
    cursor = None

    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        for page in range(max_pages):
            params: dict = {"q": query, "product": "Latest"}
            if cursor:
                params["cursor"] = cursor

            try:
                resp = await client.get(
                    f"{GETXAPI_BASE}/twitter/tweet/advanced_search",
                    headers=headers,
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()

                tweets = data.get("tweets", [])
                all_tweets.extend(tweets)

                logger.info(f"  Page {page + 1}: {len(tweets)} tweets (total: {len(all_tweets)})")

                if not data.get("has_more", False):
                    break
                cursor = data.get("next_cursor")

            except httpx.HTTPStatusError as e:
                logger.error(f"GetXAPI HTTP error on page {page + 1}: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
                break
            except Exception as e:
                logger.error(f"GetXAPI error on page {page + 1}: {e}")
                break

    logger.info(f"Fetched {len(all_tweets)} total tweets")
    return all_tweets
