"""LangGraph StateGraph definition — 8-agent pipeline with real implementations."""

import logging
from langgraph.graph import StateGraph, END
from src.state import PlatformState

from src.agents.ingestion_agent import ingestion_agent
from src.agents.preprocessing_agent import preprocessing_agent
from src.agents.trend_agent import trend_agent
from src.agents.sentiment_agent import sentiment_agent
from src.agents.topic_agent import topic_agent
from src.agents.insight_agent import insight_agent
from src.agents.recommendation_agent import recommendation_agent
from src.agents.evaluator_agent import evaluator_agent

logger = logging.getLogger(__name__)


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


def create_pipeline_graph() -> StateGraph:
    """
    Build the full LangGraph pipeline.

    Topology:
        ingestion → preprocessing → [trend, sentiment, topic] (parallel)
          → insight_synthesis → recommendation → evaluator
          → (conditional) → end | insight | recommendation
    """
    graph = StateGraph(PlatformState)

    # ─── Register agent nodes ─────────────────────────────
    graph.add_node("ingestion_agent", ingestion_agent)
    graph.add_node("preprocessing_agent", preprocessing_agent)
    graph.add_node("trend_agent", trend_agent)
    graph.add_node("sentiment_agent", sentiment_agent)
    graph.add_node("topic_agent", topic_agent)
    graph.add_node("insight_agent", insight_agent)
    graph.add_node("recommendation_agent", recommendation_agent)
    graph.add_node("evaluator_agent", evaluator_agent)

    # ─── Define edges ─────────────────────────────────────
    graph.set_entry_point("ingestion_agent")
    graph.add_edge("ingestion_agent", "preprocessing_agent")

    # Parallel ML analysis after preprocessing
    graph.add_edge("preprocessing_agent", "trend_agent")
    graph.add_edge("preprocessing_agent", "sentiment_agent")
    graph.add_edge("preprocessing_agent", "topic_agent")

    # Converge into insight synthesis
    graph.add_edge("trend_agent", "insight_agent")
    graph.add_edge("sentiment_agent", "insight_agent")
    graph.add_edge("topic_agent", "insight_agent")

    # Insight → Recommendation → Evaluator
    graph.add_edge("insight_agent", "recommendation_agent")
    graph.add_edge("recommendation_agent", "evaluator_agent")

    # Conditional routing from evaluator
    graph.add_conditional_edges(
        "evaluator_agent",
        should_refine,
        {
            END: END,
            "insight_agent": "insight_agent",
            "recommendation_agent": "recommendation_agent",
        },
    )

    return graph


def compile_pipeline():
    """Compile the graph into a runnable pipeline."""
    graph = create_pipeline_graph()
    return graph.compile()
