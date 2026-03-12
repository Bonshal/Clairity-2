
import asyncio
import uuid
import logging
import os
from dotenv import load_dotenv

# Load env variables before importing app modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

from src.api.routes import execute_pipeline, PipelineRequest
from src.db.neon import async_session, AnalysisRunModel
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("manual_workflow_runner")

async def run():
    run_id = f"manual_{uuid.uuid4().hex[:8]}"
    
    print(f"🚀 Starting Manual Analysis Workflow (Run ID: {run_id})")
    print(f"Target Platforms: Twitter, YouTube, Reddit")
    print("-" * 50)

    # Create run record
    async with async_session() as session:
        run_record = AnalysisRunModel(
            id=run_id,
            started_at=datetime.now(timezone.utc),
            status="queued",
            platforms_processed=["twitter", "youtube", "reddit"],
            run_metadata={"trigger": "manual_script", "logs": []}
        )
        session.add(run_record)
        await session.commit()

    # Execute
    req = PipelineRequest(
        niche_id="manual_test",
        platforms=["twitter", "youtube", "reddit"]
    )
    
    try:
        await execute_pipeline(run_id, req)
        print(f"\n✅ Workflow Completed Successfully!")
        print(f"Check database or dashboard for results.")
    except Exception as e:
        print(f"\n❌ Workflow Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())
