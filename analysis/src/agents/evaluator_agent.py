"""Evaluator / Critic Agent — uses Gemini 2.5 Flash-Lite for pass/fail evaluation."""

import logging
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from src.state import PlatformState, EvaluationResult
from src.config import settings

logger = logging.getLogger(__name__)


def _get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.gemini_lite_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,  # Low temp for evaluation consistency
    )


EVALUATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a quality evaluator for content recommendations. 
Evaluate the pipeline output and determine if it meets quality standards.

Score each dimension 0.0-1.0:
- **insight_quality**: Are insights specific, actionable, and data-backed?
- **recommendation_actionability**: Can a content creator immediately act on these?
- **hallucination_risk**: How likely is the output to contain fabricated data? (0 = no risk, 1 = high risk)

Return JSON:
{{
  "overall_pass": true/false,
  "confidence_score": 0.0-1.0,
  "insight_quality": 0.0-1.0,
  "recommendation_actionability": 0.0-1.0,
  "hallucination_risk": 0.0-1.0,
  "feedback": "Specific feedback for improvement",
  "route_to": "end|insight_agent|recommendation_agent"
}}

Rules:
- Pass if confidence_score >= 0.6 AND hallucination_risk < 0.4
- Route to "insight_agent" if insights are weak
- Route to "recommendation_agent" if recommendations need improvement
- Route to "end" if quality is acceptable"""),
    ("human", """## Insights ({insight_count})
{insights}

## Recommendations ({rec_count})
{recommendations}

## Pipeline Context
- Items processed: {total_items}
- Trends detected: {trend_count}
- Iteration: {iteration}
- Max iterations: {max_iterations}

Evaluate this pipeline output."""),
])


async def evaluator_agent(state: PlatformState) -> dict:
    """
    Agent 8: Evaluate pipeline quality and decide routing.

    Reads: insights, recommendations, overall state
    Writes: evaluation, evaluation_history
    """
    current_iteration = len(state.evaluation_history)
    logger.info(f"[Evaluator Agent] Starting (iteration {current_iteration + 1}/{state.max_refinement_iterations})...")

    llm = _get_llm()

    insights_str = json.dumps([
        {"title": i.title, "category": i.category, "confidence": i.confidence, "actionability": i.actionability}
        for i in state.insights[:10]
    ], indent=2) if state.insights else "No insights generated"

    recs_str = json.dumps([
        {"title": r.title, "format": r.suggested_format, "confidence": r.confidence, "seo_score": r.seo.seo_score}
        for r in state.recommendations[:10]
    ], indent=2) if state.recommendations else "No recommendations generated"

    try:
        chain = EVALUATOR_PROMPT | llm
        response = await chain.ainvoke({
            "insights": insights_str,
            "recommendations": recs_str,
            "insight_count": len(state.insights),
            "rec_count": len(state.recommendations),
            "total_items": state.total_items_processed,
            "trend_count": len(state.trend_signals),
            "iteration": current_iteration + 1,
            "max_iterations": state.max_refinement_iterations,
        })

        content = response.content
        if isinstance(content, str):
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            parsed = json.loads(content)
        else:
            parsed = {}

        evaluation = EvaluationResult(
            overall_pass=parsed.get("overall_pass", True),
            confidence_score=parsed.get("confidence_score", 0.5),
            insight_quality=parsed.get("insight_quality", 0.5),
            recommendation_actionability=parsed.get("recommendation_actionability", 0.5),
            hallucination_risk=parsed.get("hallucination_risk", 0.5),
            feedback=parsed.get("feedback", "No feedback"),
            route_to=parsed.get("route_to", "end"),
            iteration=current_iteration + 1,
        )

        logger.info(
            f"[Evaluator] Pass: {evaluation.overall_pass}, "
            f"Confidence: {evaluation.confidence_score:.2f}, "
            f"Route: {evaluation.route_to}"
        )

        return {
            "evaluation": evaluation,
            "evaluation_history": state.evaluation_history + [evaluation],
        }

    except Exception as e:
        logger.error(f"[Evaluator Agent] LLM call failed: {e}")
        # Default to pass on error to avoid infinite loops
        fallback = EvaluationResult(
            overall_pass=True,
            confidence_score=0.5,
            insight_quality=0.5,
            recommendation_actionability=0.5,
            hallucination_risk=0.5,
            feedback=f"Evaluation failed: {str(e)}",
            route_to="end",
            iteration=current_iteration + 1,
        )
        return {
            "evaluation": fallback,
            "evaluation_history": state.evaluation_history + [fallback],
        }
