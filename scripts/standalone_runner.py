
import asyncio
import logging
import sys
import os

# Add project root to path (mimic server setup)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analysis")))

from src.state import PlatformState, PlatformEnum
from src.agents.graph import compile_pipeline
from src.db.neon import async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting standalone pipeline verification...")
    
    # 1. Pipeline Request Setup
    run_id = "standalone_verify_001"
    initial_state = PlatformState(
        run_id=run_id,
        niche_id="test_niche",
        active_platforms=[PlatformEnum.TWITTER, PlatformEnum.YOUTUBE],
        max_refinement_iterations=1, # faster check
    )

    # 2. Compile Graph
    logger.info("Compiling graph...")
    try:
        pipeline = compile_pipeline()
    except Exception as e:
        logger.error(f"Graph compilation failed: {e}")
        return

    # 3. Execute
    logger.info(f"Invoking pipeline run {run_id}...")
    try:
        final_state = await pipeline.ainvoke(initial_state)
        
        # 4. Results
        print("\n--- Pipeline Execution Complete ---")
        if isinstance(final_state, dict):
             # LangGraph returns dict usually
             print(f"Total Items Processed: {final_state.get('total_items_processed', 0)}")
             print(f"Emerging Trends: {final_state.get('emerging_count', 0)}")
             print(f"Insights Generated: {len(final_state.get('insights', []))}")
             if final_state.get('evaluation'):
                 print(f"Evaluation Score: {final_state['evaluation'].confidence_score}")
                 print(f"Evaluation Pass: {final_state['evaluation'].overall_pass}")
        else:
             # If Pydantic model returned (unlikely given typical LangGraph setup)
             print(f"Total Items Processed: {final_state.total_items_processed}")
             
    except Exception as e:
        logger.error(f"Pipeline execution crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Fix for Windows asyncio loop policy if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
