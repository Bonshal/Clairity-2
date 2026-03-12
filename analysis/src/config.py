"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """All configuration via .env file or environment variables."""

    # ─── Neon PostgreSQL ──────────────────────────────────
    database_url: str

    # ─── MongoDB Atlas ────────────────────────────────────
    mongodb_uri: str

    # ─── Upstash Redis ────────────────────────────────────
    upstash_redis_rest_url: str
    upstash_redis_rest_token: str

    # ─── Data Source APIs ─────────────────────────────────
    apify_token: Optional[str] = None
    getxapi_api_key: str
    youtube_api_key: str

    # ─── LLM APIs ─────────────────────────────────────────
    gemini_api_keys: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # ─── App Config ───────────────────────────────────────
    environment: str = "development"
    analysis_port: int = 8000
    jwt_secret: str = "dev-secret-change-me"

    # ─── ML Config ────────────────────────────────────────
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    emotion_model: str = "SamLowe/roberta-base-go_emotions"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # ─── LLM Model Config ────────────────────────────────
    gemini_pro_model: str = "gemini-2.5-pro"
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_lite_model: str = "gemini-2.5-flash-lite"

    class Config:
        env_file = ("../.env", ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()  # type: ignore[call-arg]
