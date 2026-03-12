"""Neon PostgreSQL client using SQLAlchemy + pgvector."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Integer, BigInteger, Float, DateTime, Boolean, JSON, select
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
from datetime import datetime
from typing import Optional, Sequence
import uuid

from src.config import settings

# Convert DATABASE_URL from postgres:// to postgresql+asyncpg://
db_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
# Strip query params (sslmode, channel_binding) that are Prisma-specific
if "?" in db_url:
    db_url = db_url.split("?")[0]

engine = create_async_engine(db_url, echo=False, connect_args={"ssl": "require"})
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class ContentItemModel(Base):
    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String(20))
    platform_id: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True)
    language: Mapped[str] = mapped_column(String(10), default="en")

    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    downvotes: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)

    platform_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    batch_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    embedding = mapped_column(Vector(384), nullable=True)


class SentimentResultModel(Base):
    __tablename__ = "sentiment_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(UUID)
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    emotions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class TopicClusterModel(Base):
    __tablename__ = "topic_clusters"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    cluster_label: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    representative_docs: Mapped[list] = mapped_column(ARRAY(UUID), default=[])
    doc_count: Mapped[int] = mapped_column(Integer)
    avg_sentiment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    analysis_run_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class TrendSignalModel(Base):
    __tablename__ = "trend_signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    topic_cluster_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, nullable=True)
    keyword: Mapped[str] = mapped_column(Text)
    platform: Mapped[str] = mapped_column(String(20))
    direction: Mapped[str] = mapped_column(String(20))
    momentum_7d: Mapped[float] = mapped_column(Float)
    momentum_30d: Mapped[float] = mapped_column(Float)
    volume_current: Mapped[int] = mapped_column(Integer)
    volume_previous: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RecommendationModel(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text)
    content_angle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_keywords: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    keyword_intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geo_optimization: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_trends: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    source_insights: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evaluation_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    analysis_run_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class AnalysisRunModel(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    platforms_processed: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    items_processed: Mapped[int] = mapped_column(Integer, default=0)
    evaluation_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    run_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)


class NicheModel(Base):
    __tablename__ = "niches"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    keywords: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    subreddits: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    twitter_queries: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    youtube_queries: Mapped[list] = mapped_column(ARRAY(Text), default=[])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


async def get_session() -> AsyncSession:
    """Get an async database session."""
    async with async_session() as session:
        yield session


async def fetch_content_by_ids(session: AsyncSession, content_ids: list[str]) -> Sequence[ContentItemModel]:
    """Fetch multiple content items by their UUIDs."""
    if not content_ids:
        return []
    
    # Convert string IDs to UUID objects
    uuids = [uuid.UUID(uid) for uid in content_ids]
    
    stmt = select(ContentItemModel).where(ContentItemModel.id.in_(uuids))
    result = await session.execute(stmt)
    return result.scalars().all()


async def log_pipeline_step(run_id: str, step: str, status: str = "info", message: str = "", duration: Optional[float] = None):
    """Log a pipeline step to the run metadata."""
    async with async_session() as session:
        try:
            # Use with_for_update to lock the row and prevent race conditions on JSON updates
            stmt = select(AnalysisRunModel).where(AnalysisRunModel.id == run_id).with_for_update()
            result = await session.execute(stmt)
            run = result.scalar_one_or_none()
            
            if run:
                metadata = dict(run.run_metadata or {})
                logs = list(metadata.get("logs", []))
                logs.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "step": step,
                    "status": status,
                    "message": message,
                    "duration": duration
                })
                metadata["logs"] = logs
                run.run_metadata = metadata
                # Force update since JSON dict mutation might not be detected
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(run, "run_metadata")
                await session.commit()
        except Exception as e:
            # Don't let logging fail the pipeline
            print(f"Failed to log pipeline step: {e}")

