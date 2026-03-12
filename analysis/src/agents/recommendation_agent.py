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
from src.llm.wrapper import get_random_api_key
from src.db.neon import async_session, RecommendationModel, log_pipeline_step

logger = logging.getLogger(__name__)


def _get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.gemini_flash_model,
        google_api_key=get_random_api_key() or settings.google_api_key,
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
        await log_pipeline_step(
            state.run_id, "Recommendations", "running",
            f"Generated {len(recommendations)} recommendations — persisting to DB..."
        )

        # ─── Persist to database ───────────────────────────────────────
        if recommendations:
            db_models = []
            for rec in recommendations:
                db_models.append(RecommendationModel(
                    id=uuid.uuid4(),
                    title=rec.title,
                    content_angle=rec.content_angle,
                    target_keywords=rec.seo.long_tail_keywords + [rec.seo.primary_keyword],
                    keyword_intent=rec.seo.keyword_intent,
                    seo_score=rec.seo.seo_score,
                    geo_optimization={
                        "key_entities": rec.geo.key_entities,
                        "citation_worthy_claims": rec.geo.citation_worthy_claims,
                        "recommended_structure": rec.geo.recommended_structure,
                        "faq_suggestions": rec.geo.faq_suggestions,
                        "schema_markup": rec.geo.schema_markup,
                        "geo_score": rec.geo.geo_score,
                    },
                    confidence=rec.confidence,
                    reasoning=rec.reasoning,
                    source_trends=rec.source_trends,  # keyword strings
                    source_insights={
                        "target_audience": rec.target_audience,
                        "suggested_format": rec.suggested_format,
                        "estimated_effort": rec.estimated_effort,
                        "source_platforms": rec.source_platforms,
                        "title_variants": rec.seo.title_variants,
                        "meta_description": rec.seo.meta_description,
                        "estimated_competition": rec.seo.estimated_competition,
                    },
                    analysis_run_id=state.run_id,
                ))

            try:
                async with async_session() as session:
                    session.add_all(db_models)
                    await session.commit()
                logger.info(f"[Recommendation Agent] Persisted {len(db_models)} recommendations to DB")
                await log_pipeline_step(
                    state.run_id, "Recommendations", "completed",
                    f"Saved {len(db_models)} recommendations to database"
                )
            except Exception as e:
                logger.error(f"[Recommendation Agent] DB persist failed: {e}", exc_info=True)
                await log_pipeline_step(
                    state.run_id, "Recommendations", "warning",
                    f"Recommendations generated but DB write failed: {e}"
                )

        return {"recommendations": recommendations}

    except Exception as e:
        logger.error(f"[Recommendation Agent] LLM call failed: {e}")
        return {
            "recommendations": [],
            "errors": state.errors + [f"Recommendation agent LLM error: {str(e)}"],
        }
