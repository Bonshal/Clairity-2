-- Enable pgvector extension for embedding support
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column (384-dim from all-MiniLM-L6-v2)
ALTER TABLE content_items ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Create HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_content_embedding
ON content_items USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
