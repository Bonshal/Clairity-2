"""
Focused Twitter API (GetXAPI) Test Script
=========================================
Tests the Twitter ingestion module in isolation.

Usage:
    cd analysis
    uv run python -m tests.test_twitter_api
"""

import asyncio
import logging
import sys
import json
from datetime import datetime

# ─── Setup logging ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("twitter_test")

async def test_twitter():
    query = "AI agents 2026"
    max_pages = 1
    
    logger.info(f"🚀 Starting Twitter API test...")
    logger.info(f"   Query: {query}")
    logger.info(f"   Max Pages: {max_pages}")
    
    try:
        from src.ingestion.twitter import fetch_twitter_data
        
        start_time = datetime.now()
        tweets = await fetch_twitter_data(query=query, max_pages=max_pages)
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Test completed in {duration:.2f} seconds")
        logger.info(f"📊 Results: {len(tweets)} tweets fetched")
        
        if tweets:
            logger.info("📄 Sample Tweet Data:")
            sample = tweets[0]
            
            # Extract common fields for a clean preview
            tweet_id = sample.get("id_str") or sample.get("rest_id") or "N/A"
            text = sample.get("text") or sample.get("full_text") or "No text"
            author = "Unknown"
            
            # Handle nested user object if present
            user = sample.get("user") or sample.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
            if user:
                author = f"@{user.get('screen_name', 'unknown')}"
            
            print("\n" + "="*60)
            print(f"AUTHOR:  {author}")
            print(f"ID:      {tweet_id}")
            print(f"TEXT:    {text[:200]}..." if len(text) > 200 else f"TEXT:    {text}")
            print("="*60 + "\n")
            
            # Save raw sample to a file for manual inspection
            with open("twitter_sample.json", "w", encoding="utf-8") as f:
                json.dump(sample, f, indent=2)
            logger.info("💾 Full raw sample saved to 'twitter_sample.json'")
            
        else:
            logger.warning("❌ No tweets were returned. Check your query or API credits.")
            
    except Exception as e:
        logger.error(f"💥 Twitter test failed with error: {type(e).__name__}")
        logger.error(f"   {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_twitter())
