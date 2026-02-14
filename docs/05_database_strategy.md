# 05 — Database & Storage Strategy

## Database Portfolio

```mermaid
graph LR
    subgraph "Primary Relational"
        Neon[(Neon PostgreSQL<br/>+ pgvector)]
    end
    
    subgraph "Document Store"
        Mongo[(MongoDB Atlas)]
    end
    
    subgraph "Cache & Queue"
        Redis[(Upstash Redis)]
    end
    
    App[Application] --> Neon
    App --> Mongo
    App --> Redis
    
    style Neon fill:#336791,stroke:#333,color:#fff
    style Mongo fill:#4DB33D,stroke:#333,color:#fff
    style Redis fill:#DC382D,stroke:#333,color:#fff
```

---

## Database 1: Neon PostgreSQL (+ pgvector)

| Property | Value |
|---|---|
| **Provider** | [Neon](https://neon.tech) |
| **Role** | Primary relational DB, vector store, analytics |
| **Why Neon** | Serverless PostgreSQL with autoscaling, branching, pgvector support |
| **Pricing Tier** | Free tier: 0.5 GiB storage, 1 project. Launch plan: $19/mo, 10 GiB |

### What Neon Stores
- `content_items` — Unified platform content with embeddings (pgvector)
- `sentiment_results` — Sentiment/emotion analysis outputs
- `topic_clusters` — BERTopic clustering results
- `trend_signals` — Trend detection signals
- `recommendations` — Generated content recommendations
- `analysis_runs` — Pipeline execution metadata
- `users`, `projects`, `niches` — Application data

### pgvector Configuration
```sql
-- Enable the extension
CREATE EXTENSION IF NOT EXISTS vector;

-- HNSW index for fast approximate nearest neighbor search
CREATE INDEX idx_content_embedding ON content_items 
    USING hnsw (embedding vector_cosine_ops) 
    WITH (m = 16, ef_construction = 64);
    
-- Similarity search example
SELECT id, title, 1 - (embedding <=> $1) AS similarity
FROM content_items
WHERE platform = 'reddit'
ORDER BY embedding <=> $1
LIMIT 20;
```

### Why pgvector Instead of Pinecone

| Factor | Neon pgvector | Pinecone |
|---|---|---|
| **Cost** | Included in Neon plan | $70/mo (Starter) |
| **Complexity** | Same DB, same queries | Separate service, separate SDK |
| **Performance** | Good for < 1M vectors | Better for > 5M vectors |
| **JOINs** | Yes (join embeddings with metadata) | No (metadata filtering only) |
| **Migration path** | Easy to add Pinecone later | — |

> [!IMPORTANT]
> **Recommendation**: Start with Neon pgvector. If/when vector volume exceeds 1M rows or query latency degrades, migrate to Pinecone for the vector-specific workload while keeping relational data in Neon.

### Time-Series Without a Separate DB

Instead of adding TimescaleDB, we use PostgreSQL materialized views and proper indexing:

```sql
-- Materialized view for daily engagement trends
CREATE MATERIALIZED VIEW daily_engagement AS
SELECT 
    DATE(platform_created_at) AS date,
    platform,
    COUNT(*) AS post_count,
    AVG(likes) AS avg_likes,
    AVG(views) AS avg_views,
    SUM(comments_count) AS total_comments
FROM content_items
GROUP BY DATE(platform_created_at), platform;

-- Refresh daily
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_engagement;

-- Index for fast time-range queries
CREATE INDEX idx_daily_engagement_date ON daily_engagement(date DESC, platform);
```

> [!NOTE]
> If trend query complexity grows (e.g. needing continuous aggregates, retention policies, compression), migrate time-series data to **Timescale Cloud** ($0.023/hr for smallest instance). This can be done without touching the rest of the stack.

---

## Database 2: MongoDB Atlas (Document Store)

| Property | Value |
|---|---|
| **Provider** | [MongoDB Atlas](https://www.mongodb.com/atlas) |
| **Role** | Raw data store, unstructured document storage |
| **Why MongoDB** | Schema-flexible for varied Apify responses; managed cloud; excellent for audit trails |
| **Pricing Tier** | Free tier (M0): 512 MB. Shared (M2): $9/mo, 2 GB |

### What MongoDB Stores
- `raw_reddit_posts` — Raw Apify Reddit scraper output
- `raw_twitter_tweets` — Raw Apify Twitter scraper output
- `raw_youtube_videos` — Raw Apify YouTube scraper output
- `ingestion_logs` — Detailed ingestion run logs
- `pipeline_artifacts` — Intermediate ML pipeline outputs (if large)

### Why MongoDB Instead of Just PostgreSQL for Raw Data

| Factor | MongoDB Atlas | PostgreSQL JSONB |
|---|---|---|
| **Schema flexibility** | Fully schemaless | JSONB works but querying is awkward |
| **Raw document size** | Handles large nested docs naturally | JSONB columns can bloat |
| **Write throughput** | Optimized for high-volume writes | Good but locks on hot tables |
| **Audit/replay** | Natural fit for event-sourced raw data | Possible but not idiomatic |
| **Cost** | Free tier available | Uses Neon storage quota |

### Setup Instructions

> [!CAUTION]
> **User Action Required**: Before implementation, create a MongoDB Atlas cluster:
> 1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
> 2. Create a free M0 cluster (or M2 for production)
> 3. Set up a database user with read/write permissions
> 4. Whitelist your application's IP range (or use 0.0.0.0/0 for dev)
> 5. Copy the connection string (e.g., `mongodb+srv://...`)
> 6. Set environment variable: `MONGODB_URI=mongodb+srv://...`

---

## Database 3: Upstash Redis (Cache + Queue)

| Property | Value |
|---|---|
| **Provider** | [Upstash](https://upstash.com) |
| **Role** | Caching, job queues, rate limiting, session store |
| **Why Upstash** | Serverless Redis, pay-per-request, REST API, multi-region, BullMQ compatible |
| **Pricing Tier** | Free: 10K commands/day. Pay-as-you-go: $0.2/100K commands |

### What Redis Handles

| Use Case | Key Pattern | TTL |
|---|---|---|
| **Job Queue** | `queue:ingestion:{platform}` | Until processed |
| **Dead Letter Queue** | `dlq:ingestion:{platform}` | 7 days |
| **Rate Limit Counters** | `ratelimit:apify:{actor_id}` | 60 seconds |
| **API Response Cache** | `cache:api:{endpoint}:{params_hash}` | 5 minutes |
| **Pipeline Lock** | `lock:pipeline:{run_id}` | 30 minutes |
| **Session Store** | `session:{user_id}` | 24 hours |

### Setup Instructions

> [!CAUTION]
> **User Action Required**: Before implementation, create an Upstash Redis database:
> 1. Go to [Upstash Console](https://console.upstash.com)
> 2. Click "Create Database"
> 3. Choose a region closest to your compute (e.g., `us-east-1`)
> 4. Enable TLS (recommended)
> 5. Copy the REST URL and token
> 6. Set environment variables:
>    - `UPSTASH_REDIS_REST_URL=https://...`
>    - `UPSTASH_REDIS_REST_TOKEN=...`

---

## Full Database Decision Matrix

| Requirement | Database | Justification |
|---|---|---|
| Structured content data | Neon PostgreSQL | Relational, ACID, complex queries |
| Vector embeddings | Neon pgvector | Avoids extra vendor; HNSW index |
| Semantic similarity search | Neon pgvector | `<=>` cosine distance operator |
| Time-series trends | Neon (materialized views) | Sufficient for initial scale |
| Raw scraped documents | MongoDB Atlas | Schema-flexible, audit trail |
| Job queues | Upstash Redis | BullMQ-compatible, serverless |
| Caching | Upstash Redis | Low-latency, pay-per-use |
| Rate limiting | Upstash Redis | Atomic counters, TTL support |
| User auth / sessions | Neon + Redis | Sessions cached, auth data in Neon |

---

## Environment Variables Summary

```env
# Neon PostgreSQL
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/market_research

# Upstash Redis
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXxx...

# Data Source APIs
APIFY_TOKEN=apify_api_xxx              # Reddit scraping
GETXAPI_API_KEY=xxx                    # X/Twitter data
YOUTUBE_API_KEY=AIzaSy...             # YouTube Data API v3

# LLM APIs (Dev Phase — Gemini)
GOOGLE_API_KEY=xxx                     # Gemini API

# LLM APIs (Production — add when needed)
# OPENAI_API_KEY=sk-xxx
# ANTHROPIC_API_KEY=sk-ant-xxx
```
