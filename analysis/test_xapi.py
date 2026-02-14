
import asyncio
import logging
import sys
import os

# Add src to path if needed
sys.path.append(os.path.join(os.getcwd()))

from src.ingestion.twitter import fetch_twitter_data
from src.config import settings

logging.basicConfig(level=logging.INFO)

async def test_x():
    print(f"Testing GetXAPI with key: {settings.getxapi_api_key[:10]}...")
    try:
        tweets = await fetch_twitter_data(query="artificial intelligence", max_pages=1)
        print(f"\nSUCCESS! Fetched {len(tweets)} tweets.")
        if tweets:
            print(f"Sample tweet: {tweets[0].get('text')}")
    except Exception as e:
        print(f"\nFAILED! Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_x())
