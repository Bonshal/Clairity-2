import asyncio
import logging
from src.db.neon import async_session
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flush")

async def flush():
    async with async_session() as s:
        # Must delete in correct FK order
        await s.execute(text("DELETE FROM sentiment_results"))
        await s.execute(text("DELETE FROM trend_signals"))
        await s.execute(text("DELETE FROM topic_clusters"))
        await s.execute(text("DELETE FROM recommendations"))
        await s.execute(text("DELETE FROM content_items WHERE platform = 'reddit'"))
        await s.commit()
        
        r = await s.execute(text("SELECT platform, COUNT(*) FROM content_items GROUP BY platform"))
        for row in r.fetchall():
            print(f"  {row[0]}: {row[1]}")
    print("Done! Analysis tables + Reddit content cleared. Re-run the pipeline.")

asyncio.run(flush())
