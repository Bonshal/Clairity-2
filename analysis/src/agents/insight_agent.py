"""Insight Synthesis Agent — uses Gemini 2.5 Pro for reasoning."""

import logging
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from src.state import PlatformState, Insight, ContentGap
from src.config import settings

logger = logging.getLogger(__name__)


def _get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.gemini_pro_model,
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )


INSIGHT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a market research analyst. Analyze the following data 
and generate actionable insights about content gaps, viral patterns, audience signals, 
and risk signals.

Return a JSON object with:
{{
  "insights": [
    {{
      "category": "content_gap|viral_pattern|audience_signal|risk_signal",
      "title": "short title",
      "description": "detailed description",
      "supporting_data": ["data point 1", "data point 2"],
      "confidence": 0.0-1.0,
      "actionability": "high|medium|low"
    }}
  ],
  "content_gaps": [
    {{
      "topic": "topic name",
      "demand_score": 0.0-1.0,
      "supply_count": 0,
      "opportunity_score": 0.0-1.0,
      "platforms": ["reddit", "twitter", "youtube"],
      "related_keywords": ["kw1", "kw2"]
    }}
  ],
  "opportunity_score": 0.0-1.0
}}"""),
    ("human", """## Trend Data
{trend_data}

## Sentiment Data
{sentiment_data}

## Topic Clusters
{topic_data}

## Overall Metrics
- Total items processed: {total_items}
- Emerging trends: {emerging_count}
- Viral trends: {viral_count}

Generate insights and identify content gaps from this data."""),
])


async def insight_agent(state: PlatformState) -> dict:
    """
    Agent 6: Synthesize insights using Gemini 2.5 Pro.

    Reads: trend_signals, sentiment_summaries, topic_clusters
    Writes: insights, content_gaps, opportunity_score
    """
    logger.info("[Insight Agent] Starting with Gemini 2.5 Pro...")

    llm = _get_llm()

    # Prepare input data
    trend_data = json.dumps([
        {"keyword": t.keyword, "direction": t.direction, "momentum": t.momentum_7d, "confidence": t.confidence}
        for t in state.trend_signals[:20]
    ], indent=2) if state.trend_signals else "No trend data available"

    sentiment_data = json.dumps([
        s.model_dump() for s in state.sentiment_summaries
    ], indent=2) if state.sentiment_summaries else "No sentiment data available"

    topic_data = json.dumps([
        {"label": t.label, "keywords": t.keywords[:5], "doc_count": t.doc_count}
        for t in state.topic_clusters[:15]
    ], indent=2) if state.topic_clusters else "No topic data available"

    # Invoke LLM
    try:
        chain = INSIGHT_PROMPT | llm
        response = await chain.ainvoke({
            "trend_data": trend_data,
            "sentiment_data": sentiment_data,
            "topic_data": topic_data,
            "total_items": state.total_items_processed,
            "emerging_count": state.emerging_count,
            "viral_count": state.viral_count,
        })

        # Parse response
        content = response.content
        if isinstance(content, str):
            # Strip markdown code fences if present
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("```", 1)[0]
            parsed = json.loads(content)
        else:
            parsed = {}

        insights = [
            Insight(**i) for i in parsed.get("insights", [])
        ]
        content_gaps = [
            ContentGap(**cg) for cg in parsed.get("content_gaps", [])
        ]
        opportunity_score = parsed.get("opportunity_score", 0.0)

        logger.info(f"[Insight Agent] Generated {len(insights)} insights, {len(content_gaps)} content gaps")

        return {
            "insights": insights,
            "content_gaps": content_gaps,
            "opportunity_score": opportunity_score,
        }

    except Exception as e:
        logger.error(f"[Insight Agent] LLM call failed: {e}")
        return {
            "insights": [],
            "content_gaps": [],
            "opportunity_score": 0.0,
            "errors": state.errors + [f"Insight agent LLM error: {str(e)}"],
        }
