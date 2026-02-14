# Project Tasks: Market Research + SEO Intelligence Platform

## Phase 1: Foundation
- [ ] Initialize monorepo structure (root `docker-compose.yml`, `nginx/`)
- [ ] Initialize Node.js API (`api/` with Express, TypeScript, Prisma)
- [ ] Initialize Python Analysis Service (`analysis/` with FastAPI, LangGraph)
- [ ] Initialize Next.js Frontend (`frontend/` with App Router, Tailwind)
- [ ] Set up Neon PostgreSQL database
  - [ ] Create `schema.prisma` with `content_items`, `trend_signals`, etc.
  - [ ] Enable `pgvector` extension in Neon
  - [ ] Run initial migration
- [ ] Set up MongoDB Atlas cluster (raw data store)
- [ ] Set up Upstash Redis (queue, cache)
- [ ] Configure environment variables (`.env`, `config.py`, `.env.example`)
- [ ] Verify local dev environment (`docker compose up`)

## Phase 2: Data Ingestion
- [ ] Implement Reddit Fetcher (Apify `reddit-scraper`)
- [ ] Implement Twitter Fetcher (GetXAPI `advanced_search`)
- [ ] Implement YouTube Fetcher (Google Data API v3 `search` + `videos`)
- [ ] Implement Raw Data Storage (MongoDB `raw_data` collections)
- [ ] Implement Preprocessing Pipeline
  - [ ] Text cleaning & normalization
  - [ ] Deduplication (SHA-256 content hash)
- [ ] Implement Embedding Generator (`all-MiniLM-L6-v2` -> `pgvector`)
- [ ] Set up Ingestion Scheduler (`node-cron` + BullMQ)
- [ ] Verify end-to-end ingestion flow

## Phase 3: ML/NLP Pipelines
- [ ] Implement Sentiment Analysis Pipeline (`twitter-roberta`)
- [ ] Implement Emotion Detection Pipeline (`go_emotions`)
- [ ] Implement Topic Modeling Pipeline (BERTopic)
- [ ] Implement Trend Detection Pipeline (Momentum + Z-score)
- [ ] Implement Anomaly/Virality Detection (Isolation Forest)
- [ ] Validate ML pipeline outputs with sample data

## Phase 4: Agent Orchestration (LangGraph)
- [ ] Define `PlatformState` Pydantic schema
- [ ] Implement Ingestion Agent
- [ ] Implement Preprocessing Agent
- [ ] Implement Trend Detection Agent
- [ ] Implement Sentiment & Emotion Agent
- [ ] Implement Topic Clustering Agent
- [ ] Implement Insight Synthesis Agent (Gemini Pro)
- [ ] Implement Recommendation Agent (Gemini Flash)
- [ ] Implement Evaluator Agent (Gemini Flash-Lite)
- [ ] Construct LangGraph Topology (DAG with conditional edges)
- [ ] Implement Retry & Error Handling logic
- [ ] Verify full agentic workflow execution

## Phase 5: Frontend & API
- [ ] Implement Node.js API Endpoints
  - [ ] Dashboard KPIs & Alerts
  - [ ] Trend Explorer & Detail
  - [ ] Recommendations & SEO/GEO Analysis
  - [ ] Search & Content Browser
  - [ ] Pipeline Trigger & Status
- [ ] Implement WebSocket Server (Real-time updates)
- [ ] Implement Next.js Dashboard UI
  - [ ] Main Dashboard (Charts, KPIs)
  - [ ] Trend Visualization (Timeline, Heatmaps)
  - [ ] Recommendation Cards & Detail View
  - [ ] Settings & Niche Configuration
- [ ] Implement Authentication (NextAuth.js)
- [ ] Integrate Frontend with API

## Phase 6: Deployment & Polish
- [ ] Create production `docker-compose.yml`
- [ ] Configure Nginx / SSL (Certbot)
- [ ] Deploy Backend to AWS EC2
- [ ] Deploy Frontend to Vercel
- [ ] Set up Monitoring (LangSmith, Sentry)
- [ ] Conduct final End-to-End Smoke Tests
- [ ] Write User Documentation / README

---

## Current Status
- [x] System Architecture Design
- [x] Database Schema Design
- [x] Agent Topology Design
- [x] Tech Stack Selection
- [ ] **Next Step:** Phase 1 Initialization
