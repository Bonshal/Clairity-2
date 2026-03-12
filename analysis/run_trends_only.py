
import asyncio
import logging
import uuid
import os
from src.state import PlatformState, CleanedDataRef
from src.agents.trend_agent import trend_agent
from src.db.neon import engine, async_session
from sqlalchemy import text
from dotenv import load_dotenv

# Setup logging first to file
logging.basicConfig(
    filename='debug_trends.log', 
    filemode='w',
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("manual_run")

# Load env from parent directory (project root)
# The current file is in analysis/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(project_root, ".env")
logger.info(f"Looking for .env at: {env_file}")
logger.info(f"File exists: {os.path.exists(env_file)}")

load_dotenv(env_file)

async def get_all_content_ids() -> list[str]:
    """Fetch all content IDs from the database."""
    async with async_session() as session:
        result = await session.execute(text("SELECT id FROM content_items"))
        return [str(row[0]) for row in result.fetchall()]

async def main():
    logger.info("Starting manual trend detection run...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    logger.info(f"GEMINI_API_KEY present: {bool(api_key)}")
    if api_key:
        logger.info(f"Key prefix: {api_key[:4]}...")
    else:
        logger.warning("GEMINI_API_KEY is MISSING!")
    
    # Check GOOGLE_API_KEY too
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        logger.info(f"GOOGLE_API_KEY found: {google_key[:4]}... (Note: wrapper looks for GEMINI_API_KEY)")

    # 1. Fetch all content IDs
    ids = await get_all_content_ids()
    if not ids:
        logger.error("No content found in DB. Make sure you have fetched data.")
        return
        
    logger.info(f"Found {len(ids)} content items in DB.")
    
    # 2. Construct mock state using CleanedDataRef
    mock_ref = CleanedDataRef(
        platform="twitter",  # Dummy platform
        item_count=len(ids),
        content_ids=ids,
        embedding_count=0
    )
    
    state = PlatformState(
        run_id=f"manual-run-{uuid.uuid4()}",
        cleaned_data_refs=[mock_ref],
        niche_id="default",
    )
    
    # 3. Run Trend Agent
    logger.info("Invoking trend_agent...")
    result = await trend_agent(state)
    
    # 4. Print Results
    signals = result.get("trend_signals", [])
    logger.info("=" * 60)
    logger.info(f"DETECTED {len(signals)} TRENDS (Hybrid Mode)")
    logger.info("=" * 60)
    
    for i, s in enumerate(signals[:20], 1):
        direction_icon = "🚀" if s.direction == "viral" else "📈" if s.direction == "emerging" else "📉"
        logger.info(f"{i:2d}. {direction_icon} {s.keyword:<30} (Dir: {s.direction}, Conf: {s.confidence:.2f}, Mom7d: {s.momentum_7d:.2f})")
        
    if len(signals) > 20:
        logger.info(f"... and {len(signals) - 20} more.")

if __name__ == "__main__":
    asyncio.run(main())
