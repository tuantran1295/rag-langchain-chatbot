-- ============================================
-- Supabase PostgreSQL + pgvector Setup Script
-- ============================================
-- This script sets up the vector database for the RAG chatbot.
-- Run this in the Supabase SQL Editor after creating your project.
-- ============================================

-- Step 1: Enable the pgvector extension
-- This extension provides vector data type and similarity search functions
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create the documents table
-- This table stores document chunks with their vector embeddings
-- Column names match langchain_postgres.PGVector expectations:
-- - uuid: primary key (PGVector expects this name)
-- - document: text content (PGVector expects this name)
-- - embedding: vector embedding
-- - cmetadata: JSONB metadata (PGVector expects this name)
-- Additional columns for our use case:
-- - source: original filename
-- - created_at: timestamp
CREATE TABLE IF NOT EXISTS documents (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document TEXT NOT NULL,
    embedding vector(1536),  -- Dimension matches text-embedding-3-small (configurable)
    cmetadata JSONB DEFAULT '{}',
    source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create index for vector similarity search
-- Using HNSW (Hierarchical Navigable Small World) for fast approximate nearest neighbor search
-- This is optimized for free-tier constraints (m=16, ef_construction=64)
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Step 4: Create index on source for filtering by document
CREATE INDEX IF NOT EXISTS documents_source_idx ON documents(source);

-- Step 5: Create index on cmetadata for JSONB queries
CREATE INDEX IF NOT EXISTS documents_metadata_idx ON documents USING GIN (cmetadata);

-- Step 6: Add comment for documentation
COMMENT ON TABLE documents IS 'Stores document chunks with vector embeddings for RAG retrieval';
COMMENT ON COLUMN documents.embedding IS 'Vector embedding with dimension 1536 (text-embedding-3-small)';
COMMENT ON COLUMN documents.cmetadata IS 'JSONB metadata including document hash, chunk_index, source, etc.';
COMMENT ON COLUMN documents.document IS 'Document chunk text content';
COMMENT ON COLUMN documents.uuid IS 'Primary key UUID';

-- ============================================
-- Notes:
-- - The embedding dimension (1536) matches OpenAI text-embedding-3-small
-- - To change dimension, update both the vector(1536) type and EMBEDDING_DIMENSION env var
-- - HNSW index parameters are tuned for free-tier performance
-- - The table uses UUID primary keys for distributed-friendly IDs
-- ============================================
