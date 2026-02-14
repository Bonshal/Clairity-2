
import asyncio
import os
from dotenv import load_dotenv
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd())))

from src.ingestion.reddit import fetch_reddit_data

async def main():
    load_dotenv()
    print("Testing Reddit ingestion (comchat)...")
    print("Testing Reddit ingestion (comchat) - Debugging Raw Data...")
    print("Testing Reddit ingestion (comchat) - Checking all item types...")
    try:
        keywords = ["AI tools"]
        # Use fetch_reddit_data which calls our search function
        items = await fetch_reddit_data(keywords=keywords, max_items=20)
        print(f"Fetched {len(items)} items total.")
        for i, item in enumerate(items[:10]):
            raw = item["raw_data"]
            dtype = raw.get("dataType", "N/A")
            is_comment = "commentId" in raw or "parentId" in raw
            print(f"Item {i}: dataType={dtype}, is_comment_infer={is_comment}, post_title={item.get('title')[:30] if item.get('title') else 'N/A'}")
    except Exception as e:
        print(f"Error during Reddit ingestion: {e}")

if __name__ == "__main__":
    asyncio.run(main())
