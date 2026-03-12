
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import pandas as pd

# Load env
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

if DATABASE_URL and "?sslmode=" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

async def view_trends():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not set")
        return

    try:
        # asyncpg requires ssl="require" in connect_args, not sslmode in URL
        engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"ssl": "require"})
        async with engine.connect() as conn:
            # Fetch all strong signals
            result = await conn.execute(text("SELECT keyword, direction, confidence, momentum_7d FROM trend_signals WHERE confidence > 0.05 ORDER BY confidence DESC"))
            rows = result.fetchall()
            
            # Filter for Title Case (LLM Refined) in Python
            polished_rows = [r for r in rows if r[0][0].isupper()]
            
            print(f"\n{'='*60}")
            print(f"POLISHED (LLM) TRENDS ({len(polished_rows)} found)")
            print(f"{'='*60}")
            print(f"{'Keyword':<30} | {'Dir':<10} | {'Conf':<5} | {'Mom7d'}")
            print("-" * 60)
            
            seen = set()
            for row in polished_rows[:20]:
                kw, direction, conf, mom = row
                if kw in seen: continue
                seen.add(kw)
                print(f"{kw:<30} | {direction:<10} | {conf:<5.2f} | {mom:.1f}")
            
            print("-" * 60)
            
            # Check for junk
            junk_indicators = ["http", "www", "video", "youtube", "twitter"]
            junk_count = sum(1 for r in rows if any(j in r[0].lower() for j in junk_indicators) and len(r[0].split()) < 2)
            print(f"\nQuality Check:")
            print(f"- Total Trends: {len(rows)}")
            print(f"- Single-word generic (potential junk): {junk_count}")
            print(f"- Title Cased: {sum(1 for r in rows if r[0][0].isupper())}/{len(rows)}")

        await engine.dispose()

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    asyncio.run(view_trends())
