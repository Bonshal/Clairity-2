"""Sentence transformer embedding generation for pgvector."""

import logging
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import settings

logger = logging.getLogger(__name__)

# Lazy-load model to avoid slow import on startup
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Get or initialize the sentence transformer model."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
        logger.info(f"Model loaded. Embedding dimension: {settings.embedding_dim}")
    return _model


def generate_embeddings(
    texts: list[str],
    batch_size: int = 64,
    show_progress: bool = False,
) -> np.ndarray:
    """
    Generate embeddings for a batch of texts.

    Args:
        texts: List of text strings to embed
        batch_size: Processing batch size (for memory efficiency)
        show_progress: Show progress bar

    Returns:
        numpy array of shape (len(texts), embedding_dim)
    """
    model = get_model()

    logger.info(f"Generating embeddings for {len(texts)} texts (batch_size={batch_size})")

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,  # L2 normalize for cosine similarity
    )

    logger.info(f"Generated {len(embeddings)} embeddings, shape: {embeddings.shape}")
    return embeddings


def generate_single_embedding(text: str) -> list[float]:
    """Generate embedding for a single text. Returns list of floats for pgvector."""
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two normalized vectors."""
    return float(np.dot(a, b))
