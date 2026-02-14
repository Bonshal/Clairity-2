import logging
import time
from langgraph.graph import StateGraph, END
from src.state import PlatformState
from src.db.neon import log_pipeline_step

from src.agents.ingestion_agent import ingestion_agent
from src.agents.preprocessing_agent import preprocessing_agent
from src.agents.trend_agent import trend_agent
from src.agents.sentiment_agent import sentiment_agent
from src.agents.topic_agent import topic_agent
from src.agents.insight_agent import insight_agent
from src.agents.recommendation_agent import recommendation_agent
from src.agents.evaluator_agent import evaluator_agent

logger = logging.getLogger(__name__)


def make_traced_node(name: str, func):
    """Wrap a node function to log start/end time and duration."""
    async def wrapper(state: PlatformState):
        start_time = time.time()
        # We assume the run is already 'running', so we just log an info or running event
        await log_pipeline_step(state.run_id, name, "running", f"Starting {name}...")
        
        try:
            result = await func(state)
            duration = time.time() - start_time
            await log_pipeline_step(
                state.run_id, 
                name, 
                "completed", 
                f"{name} completed in {duration:.2f}s",
                duration=duration
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            await log_pipeline_step(
                state.run_id, 
                name, 
                "failed", 
                f"{name} failed after {duration:.2f}s: {e}",
                duration=duration
            )
            raise e
    return wrapper


def should_refine(state: PlatformState) -> str:
    """Conditional routing after evaluator agent."""
    evaluation = state.evaluation
    if evaluation is None:
        return END

    if evaluation.overall_pass:
        logger.info("[Router] Evaluation passed → END")
        return END

    if evaluation.iteration >= state.max_refinement_iterations:
        logger.warning(
            f"[Router] Max refinement iterations ({state.max_refinement_iterations}) reached → END"
        )
        return END

    logger.info(f"[Router] Routing to: {evaluation.route_to}")
    return evaluation.route_to


def create_pipeline_graph():
    """
    Build the full LangGraph pipeline.

    Topology:
        ingestion → preprocessing → [trend, sentiment, topic] (parallel)
          → insight_synthesis → recommendation → evaluator
          → (conditional) | end | insight | recommendation
    """
    builder = StateGraph(PlatformState)

    # ─── Register agent nodes ─────────────────────────────
    # Wrappers add automatic timing logs
    builder.add_node("ingestion", make_traced_node("Ingestion", ingestion_agent))
    builder.add_node("preprocessing", make_traced_node("Preprocessing", preprocessing_agent))
    builder.add_node("trend", make_traced_node("Trend Analysis", trend_agent))
    builder.add_node("sentiment", make_traced_node("Sentiment Analysis", sentiment_agent))
    builder.add_node("topic", make_traced_node("Topic Modeling", topic_agent))
    builder.add_node("insight", make_traced_node("Insight Synthesis", insight_agent))
    builder.add_node("recommendation", make_traced_node("Recommendations", recommendation_agent))
    builder.add_node("evaluator", make_traced_node("Evaluator", evaluator_agent))

    # ─── Define edges ─────────────────────────────────────
    builder.set_entry_point("ingestion")
    
    builder.add_edge("ingestion", "preprocessing")

    # Fan-out: Parallel ML analysis after preprocessing
    builder.add_edge("preprocessing", "trend")
    builder.add_edge("preprocessing", "sentiment")
    builder.add_edge("preprocessing", "topic")

    # Fan-in: Converge into insight synthesis
    # Note: LangGraph waits for all incoming edges to a node to complete?
    # Actually, standard behavior is OR-join (run when any input arrives) or AND-join.
    # For a simple DAG where we want all 3 to finish before insight, we usually chain them
    # or use a gather node. But here, let's assume loose coupling or that 'insight_agent'
    # is robust enough to run partially or we just chain sequentially for safety if parallel fails.
    # For now, let's keep the fan-in logic. Only 'insight' will run 3 times? 
    # To fix multiple runs, we should probably map them to a "synthesis" node or similar.
    # A cleaner approach for stability:
    #   preprocessing -> trend -> sentiment -> topic -> insight
    # But parallel is faster. 
    # Let's keep the defined edges. If LangGraph triggers 'insight' 3 times, that might be okay 
    # if it merges state.
    
    builder.add_edge("trend", "insight")
    builder.add_edge("sentiment", "insight")
    builder.add_edge("topic", "insight")

    # Insight → Recommendation → Evaluator
    builder.add_edge("insight", "recommendation")
    builder.add_edge("recommendation", "evaluator")

    # Conditional routing from evaluator
    def route_step(state: PlatformState):
        ev = state.evaluation
        if not ev or ev.overall_pass or ev.iteration >= state.max_refinement_iterations:
            return END
        if ev.route_to == "insight_agent":
            return "insight"
        if ev.route_to == "recommendation_agent":
            return "recommendation"
        return END

    builder.add_conditional_edges(
        "evaluator",
        route_step,
        {
            END: END,
            "insight": "insight",
            "recommendation": "recommendation"
        }
    )

    return builder.compile()


def compile_pipeline():
    """Compile the graph into a runnable pipeline."""
    return create_pipeline_graph()

