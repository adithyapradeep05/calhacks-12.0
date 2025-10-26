-- Enterprise RAG System Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table - stores metadata about uploaded documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('legal', 'technical', 'financial', 'hr_docs', 'general')),
    storage_path TEXT NOT NULL,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Query logs table - tracks all queries for analytics
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    categories TEXT[] DEFAULT '{}',
    response_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Category statistics table - aggregated stats per category
CREATE TABLE category_stats (
    category TEXT PRIMARY KEY CHECK (category IN ('legal', 'technical', 'financial', 'hr_docs', 'general')),
    doc_count INTEGER DEFAULT 0,
    total_queries INTEGER DEFAULT 0,
    avg_response_time_ms INTEGER DEFAULT 0
);

-- Insert initial category stats
INSERT INTO category_stats (category) VALUES 
    ('legal'), ('technical'), ('financial'), ('hr_docs'), ('general');

-- Row Level Security (RLS) policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE category_stats ENABLE ROW LEVEL SECURITY;

-- Allow public read access to documents (for demo purposes)
CREATE POLICY "Allow public read access to documents" ON documents
    FOR SELECT USING (true);

-- Allow public insert access to documents (for demo purposes)
CREATE POLICY "Allow public insert access to documents" ON documents
    FOR INSERT WITH CHECK (true);

-- Allow public read access to query logs (for analytics)
CREATE POLICY "Allow public read access to query_logs" ON query_logs
    FOR SELECT USING (true);

-- Allow public insert access to query logs
CREATE POLICY "Allow public insert access to query_logs" ON query_logs
    FOR INSERT WITH CHECK (true);

-- Allow public read access to category stats
CREATE POLICY "Allow public read access to category_stats" ON category_stats
    FOR SELECT USING (true);

-- Allow public update access to category stats
CREATE POLICY "Allow public update access to category_stats" ON category_stats
    FOR UPDATE USING (true);
