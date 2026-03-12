"""LangGraph shared state schema — Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class PlatformEnum(str, Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"
    YOUTUBE = "youtube"


class IngestionMetadata(BaseModel):
    platform: PlatformEnum
    items_fetched: int = 0
    items_new: int = 0
    items_failed: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["success", "partial", "failed"] = "success"
    error_message: Optional[str] = None
    batch_id: str


class CleanedDataRef(BaseModel):
    platform: PlatformEnum
    item_count: int
    content_ids: list[str]
    embedding_count: int


class TrendSignal(BaseModel):
    keyword: str
    platform: PlatformEnum
    direction: Literal["emerging", "declining", "stable", "viral"]
    momentum_7d: float
    momentum_30d: float
    volume_current: int
    volume_previous: int
    z_score: float
    confidence: float
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class SentimentSummary(BaseModel):
    scope: str
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    dominant_sentiment: Literal["positive", "negative", "neutral"]
    sample_size: int


class EmotionSummary(BaseModel):
    scope: str
    emotions: dict[str, float]
    dominant_emotion: str
    emotional_intensity: float
    sample_size: int


class TopicCluster(BaseModel):
    cluster_id: int
    label: str
    keywords: list[str]
    doc_count: int
    representative_doc_ids: list[str]
    avg_sentiment: float
    dominant_emotion: str


class ContentGap(BaseModel):
    topic: str
    demand_score: float
    supply_count: int
    opportunity_score: float
    platforms: list[PlatformEnum]
    related_keywords: list[str]


class Insight(BaseModel):
    category: Literal["content_gap", "viral_pattern", "audience_signal", "risk_signal"]
    title: str
    description: str
    supporting_data: list[str]
    confidence: float
    actionability: Literal["high", "medium", "low"]


class SEOAnalysis(BaseModel):
    primary_keyword: str
    long_tail_keywords: list[str]
    keyword_intent: str  # informational|commercial|transactional|navigational
    title_variants: list[str]
    meta_description: str
    estimated_competition: str  # low|medium|high
    seo_score: float


class GEOAnalysis(BaseModel):
    key_entities: list[str]
    citation_worthy_claims: int
    recommended_structure: str
    faq_suggestions: list[dict]
    schema_markup: list[str]
    geo_score: float


class Recommendation(BaseModel):
    id: str
    title: str
    content_angle: str
    target_audience: str
    suggested_format: str  # blog|video|infographic|comparison|guide|tool
    estimated_effort: Literal["low", "medium", "high"]
    seo: SEOAnalysis
    geo: GEOAnalysis
    confidence: float
    reasoning: str
    source_trends: list[str]
    source_platforms: list[str]


class EvaluationResult(BaseModel):
    overall_pass: bool
    confidence_score: float
    insight_quality: float
    recommendation_actionability: float
    hallucination_risk: float
    feedback: str
    route_to: Literal["end", "insight_agent", "recommendation_agent"]
    iteration: int = 0


class PlatformState(BaseModel):
    """Shared state for the LangGraph pipeline."""

    # Run metadata
    run_id: str
    niche_id: str
    active_platforms: list[PlatformEnum] = [
        PlatformEnum.REDDIT, PlatformEnum.TWITTER, PlatformEnum.YOUTUBE
    ]

    # Agent outputs
    ingestion_metadata: list[IngestionMetadata] = []
    cleaned_data_refs: list[CleanedDataRef] = []
    total_items_processed: int = 0
    total_embeddings_generated: int = 0

    trend_signals: list[TrendSignal] = []
    emerging_count: int = 0
    declining_count: int = 0
    viral_count: int = 0

    sentiment_summaries: list[SentimentSummary] = []
    emotion_summaries: list[EmotionSummary] = []
    overall_sentiment: Optional[str] = None

    topic_clusters: list[TopicCluster] = []
    total_topics_discovered: int = 0

    content_gaps: list[ContentGap] = []
    insights: list[Insight] = []
    opportunity_score: float = 0.0
    recommendations: list[Recommendation] = []

    evaluation: Optional[EvaluationResult] = None
    evaluation_history: list[EvaluationResult] = []
    max_refinement_iterations: int = 0

    # Pipeline metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    errors: list[str] = []
    warnings: list[str] = []
