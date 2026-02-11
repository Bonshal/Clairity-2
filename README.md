# Market Research + SEO Intelligence Platform

An agent-based platform that continuously collects social/video platform data, detects trends, performs sentiment/emotion analysis, and generates SEO + GEO-optimized content recommendations.

## Architecture

```
Frontend (Vercel)  →  Node.js API (EC2)  →  Python Analysis (EC2)
                           ↓                        ↓
                    Neon PostgreSQL           MongoDB Atlas
                    + pgvector               (raw data)
                    Upstash Redis
                    (cache + queue)
```

## Quick Start

```bash
# 1. Setup
cp .env.example .env   # Fill in API keys
./scripts/setup.sh     # Install deps

# 2. Run locally
cd api && npm run dev                                     # Node.js API on :3001
cd analysis && uvicorn src.main:app --reload --port 8000  # Python on :8000

# 3. Or use Docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Services

| Service | Port | Tech |
|---|---|---|
| Node.js API | 3001 | Express + TypeScript + Prisma |
| Python Analysis | 8000 | FastAPI + LangGraph + ML |
| Frontend | 3000 | Next.js (Vercel) |

## Data Sources

| Platform | API | Cost |
|---|---|---|
| Reddit | Apify | Free tier / $49/mo |
| X/Twitter | GetXAPI | $0.001/call |
| YouTube | Data API v3 | Free (10K quota/day) |

## LLM (Dev Phase)

| Task | Model |
|---|---|
| Insight Synthesis | Gemini 2.5 Pro (free tier) |
| SEO/GEO Analysis | Gemini 2.5 Flash (free tier) |
| Evaluation | Gemini 2.5 Flash-Lite (free tier) |
