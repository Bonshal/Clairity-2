import asyncio
import sys
import os
from sqlalchemy import text

# Adjust path to find src
# Adjust path to find src
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
# Load .env file from two levels up (project root)
env_path = os.path.join(os.path.dirname(__file__), "../../.env")
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Import from the file we just viewed
# Import from src
from src.db.neon import async_session

async def flush_trends():
    print("Connecting to database...")
    async with async_session() as session:
        print("Deleting all trend signals...")
        try:
            # We can use a direct SQL execution for truncation or standard delete
            await session.execute(text("TRUNCATE TABLE trend_signals"))
            await session.commit()
            print("Successfully flushed 'trend_signals' table.")
        except Exception as e:
            print(f"Error flushing trends: {e}")
            await session.rollback()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(flush_trends())
