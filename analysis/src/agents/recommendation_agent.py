"""Recommendation + SEO/GEO Agent — uses Gemini 2.5 Flash."""

import logging
import json
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from src.state import (
    PlatformState, Recommendation, SEOAnalysis, GEOAnalysis,
)
from src.config import settings

logger = logging.getLogger(__name__)


def _get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.gemini_flash_model,
        google_api_key=settings.google_api_key,
        temperature=0.4,
    )


RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an SEO strategist and content advisor. Based on the market insights 
and content gaps provided, generate actionable content recommendations with SEO and GEO optimization.

Return a JSON object:
{{
  "recommendations": [
    {{
      "title": "Content piece title",
      "content_angle": "Specific angle/perspective",
      "target_audience": "Who this is for",
      "suggested_format": "blog|video|infographic|comparison|guide|tool",
      "estimated_effort": "low|medium|high",
      "confidence": 0.0-1.0,
      "reasoning": "Why this recommendation matters",
      "source_platforms": ["reddit", "twitter"],
      "seo": {{
        "primary_keyword": "main keyword",
        "long_tail_keywords": ["keyword 1", "keyword 2"],
        "keyword_intent": "informational|commercial|transactional|navigational",
        "title_variants": ["Title Option 1", "Title Option 2"],
        "meta_description": "150-char meta description",
        "estimated_competition": "low|medium|high",
        "seo_score": 0.0-1.0
      }},
      "geo": {{
        "key_entities": ["entity1", "entity2"],
        "citation_worthy_claims": 3,
        "recommended_structure": "How to structure for AI citation",
        "faq_suggestions": [{{"question": "Q1", "answer": "A1"}}],
        "schema_markup": ["FAQPage", "HowTo"],
        "geo_score": 0.0-1.0
      }}
    }}
  ]
}}

Generate 3-5 recommendations, prioritized by opportunity score."""),
    ("human", """## Insights
{insights}

## Content Gaps
{content_gaps}

## Trend Context
- Emerging trends: {emerging_count}
- Viral trends: {viral_count}
- Overall opportunity score: {opportunity_score}

Generate SEO + GEO optimized content recommendations."""),
])


async def recommendation_agent(state: PlatformState) -> dict:
    """
    Agent 7: Generate content recommendations with SEO/GEO optimization.

    Reads: insights, content_gaps, trend_signals
    Writes: recommendations
    """
    logger.info("[Recommendation Agent] Starting with Gemini 2.5 Flash...")

    llm = _get_llm()

    insights_data = json.dumps([
        i.model_dump() for i in state.insights[:10]
    ], indent=2) if state.insights else "No insights available"

    gaps_data = json.dumps([
        g.model_dump() for g in state.content_gaps[:10]
    ], indent=2) if state.content_gaps else "No content gaps identified"

    try:
        chain = RECOMMENDATION_PROMPT | llm
        response = await chain.ainvoke({
            "insights": insights_data,
            "content_gaps": gaps_data,
            "emerging_count": state.emerging_count,
            "viral_count": state.viral_count,
            "opportunity_score": state.opportunity_score,
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

        recommendations = []
        for rec in parsed.get("recommendations", []):
            try:
                seo = SEOAnalysis(**rec.pop("seo", {}))
                geo = GEOAnalysis(**rec.pop("geo", {}))
                recommendations.append(Recommendation(
                    id=uuid.uuid4().hex[:12],
                    seo=seo,
                    geo=geo,
                    source_trends=[t.keyword for t in state.trend_signals[:5]],
                    **rec,
                ))
            except Exception as e:
                logger.warning(f"Failed to parse recommendation: {e}")

        logger.info(f"[Recommendation Agent] Generated {len(recommendations)} recommendations")

        return {"recommendations": recommendations}

    except Exception as e:
        logger.error(f"[Recommendation Agent] LLM call failed: {e}")
        return {
            "recommendations": [],
            "errors": state.errors + [f"Recommendation agent LLM error: {str(e)}"],
        }
