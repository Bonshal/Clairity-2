
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from src.db.neon import engine  # Reuse existing engine config

load_dotenv()

async def main():
    async with engine.begin() as conn:
        print("Truncating trend_signals table...")
        await conn.execute(text("TRUNCATE TABLE trend_signals CASCADE;"))
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
