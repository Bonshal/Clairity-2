# ─── Stage 1: Base ──────────────────────────────────────────
FROM python:3.11-slim AS base
WORKDIR /app

# System deps for ML/NLP libraries (torch etc. need gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (the package manager this project uses)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency manifest and install (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# ─── Stage 2: Production ────────────────────────────────────
FROM base AS production

# Copy source
COPY src/ ./src/

# Download spaCy model at build time so it's baked into the image
# (avoids the runtime "model not found" error)
RUN uv run python -m spacy download en_core_web_sm

# Run as non-root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]


# ─── Stage 3: Development ───────────────────────────────────
FROM base AS development
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
