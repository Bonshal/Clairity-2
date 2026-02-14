# Implementation Plan — Market Research + SEO Intelligence Platform

## Goal

Build a production-grade, agent-based Market Research + SEO Intelligence Platform that continuously collects social media data, detects trends, performs sentiment/emotion/topic analysis, identifies content gaps, and generates SEO/GEO-optimized content recommendations.

---

## Architecture Reference

| Doc | Link |
|---|---|
| System Overview | [01_system_overview.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/01_system_overview.md) |
| Agent Architecture | [02_agent_architecture.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/02_agent_architecture.md) |
| Data Pipeline | [03_data_pipeline.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/03_data_pipeline.md) |
| ML/NLP Pipeline | [04_ml_nlp_pipeline.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/04_ml_nlp_pipeline.md) |
| Database Strategy | [05_database_strategy.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/05_database_strategy.md) |
| Recommendation Engine | [06_recommendation_engine.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/06_recommendation_engine.md) |
| Frontend/Backend | [07_frontend_backend.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/07_frontend_backend.md) |
| Scalability/Cost | [08_scalability_cost.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/08_scalability_cost.md) |
| State Schema | [09_state_schema.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/09_state_schema.md) |

---

## Prerequisites (User Action Required)

> [!IMPORTANT]
> Complete these before Phase 1 begins.

### Accounts & API Keys
| Service | Action | Key to Obtain |
|---|---|---|
| [Neon](https://neon.tech) | Create free project | `DATABASE_URL` |
| [MongoDB Atlas](https://mongodb.com/atlas) | Create free M0 cluster | `MONGODB_URI` |
| [Upstash](https://upstash.com) | Create Redis database | `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN` |
| [Apify](https://apify.com) | Sign up, get token | `APIFY_TOKEN` |
| [GetXAPI](https://www.getxapi.com) | Sign up, get key | `GETXAPI_API_KEY` |
| [Google Cloud Console](https://console.cloud.google.com) | Enable YouTube Data API v3 | `YOUTUBE_API_KEY` |
| [Google AI Studio](https://aistudio.google.com) | Get Gemini API key | `GOOGLE_API_KEY` |
| [AWS](https://aws.amazon.com) | EC2 `t3.medium` instance + SSH key | Instance IP + SSH access |

### EC2 Instance Setup
```bash
# On EC2 (Ubuntu 22.04 recommended)
sudo apt update && sudo apt install -y docker.io docker-compose-v2 nginx certbot
sudo usermod -aG docker $USER
```

---

## Project Structure

```
market-research-platform/
├── docker-compose.yml            # Orchestrates all backend services
├── docker-compose.dev.yml        # Dev overrides (hot reload, debug)
├── .env.example                  # Template for env vars
├── .env                          # Secret env vars (gitignored)
├── nginx/
│   └── nginx.conf                # Reverse proxy config
│
├── api/                          # Node.js API Gateway
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── prisma/
│   │   └── schema.prisma         # Neon PostgreSQL schema
│   └── src/
│       ├── index.ts              # Express app entry
│       ├── routes/
│       │   ├── dashboard.ts
│       │   ├── trends.ts
│       │   ├── recommendations.ts
│       │   ├── seo.ts
│       │   ├── geo.ts
│       │   ├── content.ts
│       │   ├── niches.ts
│       │   └── pipeline.ts
│       ├── middleware/
│       │   ├── auth.ts
│       │   └── validation.ts
│       ├── services/
│       │   ├── neon.ts            # Prisma client
│       │   ├── redis.ts           # Upstash client
│       │   └── websocket.ts       # Socket.io server
│       └── types/
│           └── index.ts
│
├── analysis/                     # Python Analysis Service
│   ├── Dockerfile
│   ├── pyproject.toml            # Dependencies (Poetry)
│   ├── alembic/
│   │   └── versions/             # DB migrations
│   └── src/
│       ├── main.py               # FastAPI entry
│       ├── config.py             # Settings (Pydantic BaseSettings)
│       ├── state.py              # LangGraph PlatformState
│       ├── ingestion/
│       │   ├── reddit.py         # Apify Reddit fetcher
│       │   ├── twitter.py        # GetXAPI fetcher
│       │   └── youtube.py        # YouTube Data API fetcher
│       ├── processing/
│       │   ├── cleaner.py        # Text cleaning + normalization
│       │   ├── dedup.py          # Content hash deduplication
│       │   └── embeddings.py     # Sentence transformer embeddings
│       ├── ml/
│       │   ├── sentiment.py      # twitter-roberta pipeline
│       │   ├── emotions.py       # go_emotions pipeline
│       │   ├── topics.py         # BERTopic pipeline
│       │   ├── trends.py         # Statistical trend detection
│       │   └── anomaly.py        # Isolation Forest virality
│       ├── agents/
│       │   ├── graph.py          # LangGraph StateGraph definition
│       │   ├── ingestion_agent.py
│       │   ├── preprocessing_agent.py
│       │   ├── trend_agent.py
│       │   ├── sentiment_agent.py
│       │   ├── topic_agent.py
│       │   ├── insight_agent.py
│       │   ├── recommendation_agent.py
│       │   └── evaluator_agent.py
│       ├── db/
│       │   ├── neon.py           # SQLAlchemy + pgvector
│       │   └── mongo.py          # Motor async MongoDB
│       └── api/
│           └── routes.py         # FastAPI endpoints
│
├── frontend/                     # Next.js Frontend
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── app/
│       ├── layout.tsx
│       ├── page.tsx
│       ├── dashboard/page.tsx
│       ├── trends/
│       │   ├── page.tsx
│       │   └── [keyword]/page.tsx
│       ├── recommendations/
│       │   ├── page.tsx
│       │   └── [id]/page.tsx
│       ├── seo/page.tsx
│       ├── geo/page.tsx
│       └── settings/page.tsx
│
└── scripts/
    ├── setup.sh                  # One-command local setup
    ├── deploy.sh                 # EC2 deploy script
    └── seed.py                   # Seed DB with sample data
```

---

## Phase 1: Foundation (Week 1–2)

### 1.1 Project Scaffold
| Task | Files | Details |
|---|---|---|
| Init monorepo root | `docker-compose.yml`, `.env.example`, `.gitignore` | Docker Compose orchestrating `api`, `analysis`, `nginx` containers |
| Init Node.js API | `api/package.json`, `api/tsconfig.json`, `api/Dockerfile` | Express + TypeScript + Prisma + Socket.io + BullMQ |
| Init Python Analysis | `analysis/pyproject.toml`, `analysis/Dockerfile` | FastAPI + LangGraph + LangChain + Transformers + BERTopic |
| Init Next.js Frontend | `frontend/` | `npx create-next-app@latest` with App Router + TypeScript + Tailwind |
| Nginx config | `nginx/nginx.conf` | Reverse proxy: `/api/*` → Node.js:3001, `/analysis/*` → Python:8000 |

**Commands:**
```bash
# Root
mkdir market-research-platform && cd market-research-platform
git init

# Node.js API
mkdir -p api/src/{routes,middleware,services,types}
cd api && npm init -y && npm i express cors helmet zod socket.io bullmq @prisma/client
npm i -D typescript @types/express @types/cors prisma ts-node nodemon
npx tsc --init

# Python Analysis
mkdir -p analysis/src/{ingestion,processing,ml,agents,db,api}
cd analysis && poetry init && poetry add fastapi uvicorn langchain langchain-google-genai langgraph transformers sentence-transformers bertopic sqlalchemy asyncpg motor pydantic apify-client httpx

# Frontend
npx -y create-next-app@latest frontend --typescript --tailwind --app --eslint --src-dir=false --import-alias="@/*" --use-npm
```

### 1.2 Database Schemas

| Task | Files | Details |
|---|---|---|
| Prisma schema | `api/prisma/schema.prisma` | All tables from [03_data_pipeline.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/03_data_pipeline.md) |
| SQLAlchemy models | `analysis/src/db/neon.py` | Mirror Prisma schema for Python read/write |
| Neon migration | `npx prisma migrate dev` | Apply schema to Neon PostgreSQL |
| Enable pgvector | SQL: `CREATE EXTENSION vector;` | Run on Neon before migration |
| MongoDB collections | `analysis/src/db/mongo.py` | `raw_reddit_posts`, `raw_twitter_tweets`, `raw_youtube_videos` |

### 1.3 Configuration & Environment

| Task | Files | Details |
|---|---|---|
| Env template | `.env.example` | All keys listed in Prerequisites |
| Python config | `analysis/src/config.py` | Pydantic `BaseSettings` loading from `.env` |
| Node.js config | `api/src/services/neon.ts`, `api/src/services/redis.ts` | Prisma + Upstash clients |
| Docker Compose | `docker-compose.yml` + `docker-compose.dev.yml` | Dev: hot reload, mounted volumes |

**Acceptance criteria:** `docker compose up` starts all 3 services; health endpoints respond on `/health`

---

## Phase 2: Data Ingestion (Week 3–4)

### 2.1 Platform Fetchers

| Task | Files | Reference |
|---|---|---|
| Reddit fetcher (Apify) | `analysis/src/ingestion/reddit.py` | [03_data_pipeline.md § Reddit Integration](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/03_data_pipeline.md) |
| Twitter fetcher (GetXAPI) | `analysis/src/ingestion/twitter.py` | [03_data_pipeline.md § X/Twitter Integration](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/03_data_pipeline.md) |
| YouTube fetcher (Data API v3) | `analysis/src/ingestion/youtube.py` | [03_data_pipeline.md § YouTube Integration](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/03_data_pipeline.md) |

### 2.2 Raw Data Storage

| Task | Files | Details |
|---|---|---|
| MongoDB raw insert | `analysis/src/db/mongo.py` | Store raw API responses with `batch_id`, `fetch_timestamp`, `api_source` |
| Batch ID generation | `analysis/src/ingestion/` | UUID-based batch tracking |

### 2.3 Preprocessing Pipeline

| Task | Files | Details |
|---|---|---|
| Text cleaner | `analysis/src/processing/cleaner.py` | HTML strip, unicode normalize, URL/mention extraction, language detection |
| Deduplication | `analysis/src/processing/dedup.py` | Content hash fingerprinting (SHA-256) |
| Embedding generator | `analysis/src/processing/embeddings.py` | `all-MiniLM-L6-v2` batch embeddings → pgvector |
| Write to Neon | `analysis/src/db/neon.py` | `INSERT ... ON CONFLICT` for dedup |

### 2.4 Scheduling

| Task | Files | Details |
|---|---|---|
| Node.js scheduler | `api/src/services/scheduler.ts` | `node-cron`: Reddit every 4h, Twitter every 2h, YouTube every 6h |
| BullMQ job queue | `api/src/services/queue.ts` | Push jobs to Upstash Redis; Python worker consumes |
| Python worker | `analysis/src/main.py` | BullMQ-compatible consumer processing ingestion jobs |

**Acceptance criteria:** Scheduled run fetches real data from all 3 platforms, stores raw in MongoDB, processes into Neon with embeddings. Dedup prevents duplicates on re-run.

---

## Phase 3: ML/NLP Pipelines (Week 5–6)

### 3.1 Sentiment Analysis

| Task | Files | Reference |
|---|---|---|
| Sentiment pipeline | `analysis/src/ml/sentiment.py` | [04_ml_nlp_pipeline.md § Pipeline 1](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/04_ml_nlp_pipeline.md) |
| Batch processing (64 at a time) | Same file | `transformers.pipeline("sentiment-analysis")` with `twitter-roberta` |
| Write results | `analysis/src/db/neon.py` | Insert into `sentiment_results` table |

### 3.2 Emotion Detection

| Task | Files | Reference |
|---|---|---|
| Emotion pipeline | `analysis/src/ml/emotions.py` | [04_ml_nlp_pipeline.md § Pipeline 2](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/04_ml_nlp_pipeline.md) |
| Weighted aggregation per topic | Same file | Engagement-weighted emotion averaging |
| Results → `sentiment_results.emotions` JSONB | `analysis/src/db/neon.py` | Merged into sentiment results |

### 3.3 Topic Modeling

| Task | Files | Reference |
|---|---|---|
| BERTopic pipeline | `analysis/src/ml/topics.py` | [04_ml_nlp_pipeline.md § Pipeline 3](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/04_ml_nlp_pipeline.md) |
| Pre-computed embeddings input | Same file | Reuse pgvector embeddings from Phase 2 |
| Results → `topic_clusters` table | `analysis/src/db/neon.py` | Cluster labels, keywords, doc counts |

### 3.4 Trend Detection

| Task | Files | Reference |
|---|---|---|
| Statistical trend detector | `analysis/src/ml/trends.py` | [04_ml_nlp_pipeline.md § Pipeline 4](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/04_ml_nlp_pipeline.md) |
| Momentum (7d + 30d), Z-score | Same file | EMA + scipy Z-score |
| Direction classification | Same file | emerging / declining / stable / viral |
| Results → `trend_signals` table | `analysis/src/db/neon.py` | |

### 3.5 Anomaly / Virality Detection

| Task | Files | Reference |
|---|---|---|
| Isolation Forest detector | `analysis/src/ml/anomaly.py` | [04_ml_nlp_pipeline.md § Pipeline 5](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/04_ml_nlp_pipeline.md) |
| Features: engagement rate, velocity, ratios | Same file | Contamination = 5% threshold |

**Acceptance criteria:** Each pipeline runs independently on stored content_items. Results written to corresponding Neon tables. Verified with sample data set of 500+ items.

---

## Phase 4: Agent Orchestration (Week 7–8)

### 4.1 LangGraph State & Graph Definition

| Task | Files | Reference |
|---|---|---|
| PlatformState (Pydantic) | `analysis/src/state.py` | [09_state_schema.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/09_state_schema.md) |
| StateGraph definition | `analysis/src/agents/graph.py` | [02_agent_architecture.md](file:///C:/Users/bonsh/.gemini/antigravity/brain/5614d7e4-3238-4571-9305-bec38f564d91/02_agent_architecture.md) |
| Conditional routing | Same file | Evaluator routes to `end`, `insight_agent`, or `recommendation_agent` |
| Max refinement cap | Same file | 2 iterations max |

### 4.2 Eight Specialized Agents

| Agent | File | Input Reads | Output Writes |
|---|---|---|---|
| 1. Ingestion Coordinator | `ingestion_agent.py` | `active_platforms`, `niche_id` | `ingestion_metadata` |
| 2. Preprocessing | `preprocessing_agent.py` | `ingestion_metadata` | `cleaned_data_refs`, `total_items_processed` |
| 3. Trend Detection | `trend_agent.py` | `cleaned_data_refs` | `trend_signals`, `emerging_count` |
| 4. Sentiment & Emotion | `sentiment_agent.py` | `cleaned_data_refs` | `sentiment_summaries`, `emotion_summaries` |
| 5. Topic Clustering | `topic_agent.py` | `cleaned_data_refs` | `topic_clusters` |
| 6. Insight Synthesis | `insight_agent.py` | Trends + sentiment + topics | `insights`, `content_gaps`, `viral_outliers` |
| 7. Recommendation + SEO/GEO | `recommendation_agent.py` | `insights`, `content_gaps` | `recommendations` |
| 8. Evaluator / Critic | `evaluator_agent.py` | `recommendations`, `insights` | `evaluation`, routing decision |

### 4.3 LLM Integration (Gemini)

| Task | Files | Details |
|---|---|---|
| Gemini 2.5 Pro (insights) | `insight_agent.py` | `langchain_google_genai.ChatGoogleGenerativeAI` |
| Gemini 2.5 Flash (SEO/GEO) | `recommendation_agent.py` | Structured JSON output |
| Gemini 2.5 Flash-Lite (eval) | `evaluator_agent.py` | Pass/fail + feedback + routing |
| Prompt templates | Each agent file | Structured prompts with JSON output schemas |

**Acceptance criteria:** Full pipeline runs end-to-end: ingestion → preprocessing → parallel ML → insight synthesis → recommendation → evaluation → conditional re-run or finish. State passes correctly between all 8 agents.

---

## Phase 5: Frontend & API (Week 9–10)

### 5.1 Node.js API Gateway

| Task | Files | Details |
|---|---|---|
| Express app setup | `api/src/index.ts` | CORS, Helmet, Zod validation, error handling |
| Auth middleware | `api/src/middleware/auth.ts` | JWT verification |
| Dashboard routes | `api/src/routes/dashboard.ts` | `GET /kpis`, `GET /alerts` |
| Trend routes | `api/src/routes/trends.ts` | `GET /top`, `GET /:keyword`, `GET /timeline` |
| Recommendation routes | `api/src/routes/recommendations.ts` | `GET /`, `GET /:id`, `POST /generate` |
| SEO/GEO routes | `api/src/routes/seo.ts`, `api/src/routes/geo.ts` | Analysis endpoints |
| Content routes | `api/src/routes/content.ts` | Browse, semantic search, outliers |
| Pipeline routes | `api/src/routes/pipeline.ts` | Trigger, status, history |
| WebSocket server | `api/src/services/websocket.ts` | Socket.io real-time pushes |

### 5.2 Next.js Dashboard

| Task | Files | Details |
|---|---|---|
| Layout + nav | `frontend/app/layout.tsx` | Sidebar nav, dark mode, auth wrapper |
| Dashboard page | `frontend/app/dashboard/page.tsx` | KPI cards, sparklines, alert feed |
| Trend explorer | `frontend/app/trends/page.tsx` | Timeline charts, heatmaps (Recharts/Nivo) |
| Keyword detail | `frontend/app/trends/[keyword]/page.tsx` | Deep-dive: sentiment, volume, related topics |
| Recommendations list | `frontend/app/recommendations/page.tsx` | Ranked cards with confidence scores |
| Recommendation detail | `frontend/app/recommendations/[id]/page.tsx` | SEO + GEO breakdown |
| Settings | `frontend/app/settings/page.tsx` | Niche config, platform connections |

### 5.3 Deployment

| Task | Details |
|---|---|
| EC2 deploy script | `scripts/deploy.sh` — SSH + docker compose pull/up |
| Vercel frontend deploy | Connect GitHub repo → auto-deploy on push |
| Nginx SSL | Certbot Let's Encrypt cert for API domain |
| GitHub Actions CI | Lint + test on PR; deploy on merge to `main` |

**Acceptance criteria:** Dashboard loads with real data. User can view trends, click into keywords, see recommendations with SEO/GEO scores. Pipeline can be triggered manually from the UI. WebSocket pushes real-time alerts.

---

## Verification Plan

### Per-Phase Tests
| Phase | Test Type | Tool |
|---|---|---|
| Phase 1 | Health check endpoints | `curl`, Docker compose logs |
| Phase 2 | Ingestion + dedup integration | `pytest` with mocked APIs |
| Phase 3 | ML pipeline output validation | `pytest` with sample data (500 items) |
| Phase 4 | End-to-end LangGraph pipeline | `pytest` with state assertions |
| Phase 5 | API endpoint testing | `supertest` (Node.js), browser testing |

### Smoke Test (Post Phase 5)
```bash
# 1. Trigger full pipeline
curl -X POST https://api.yourdomain.com/api/pipeline/trigger

# 2. Check status
curl https://api.yourdomain.com/api/pipeline/status/{run_id}

# 3. Verify dashboard loads
# Open https://yourdomain.com/dashboard in browser

# 4. Verify recommendations generated
curl https://api.yourdomain.com/api/recommendations?limit=5
```
