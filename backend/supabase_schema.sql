
-- RAGFlow Enhanced Backend - Supabase Database Schema
-- Complete schema for enterprise RAG system with category-specific storage

-- Documents table: stores document metadata and categorization
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    category TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.0,
    file_size INTEGER,
    namespace TEXT DEFAULT 'default',
    upload_time TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Query logs table: tracks query performance and routing
CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    category TEXT NOT NULL,
    response_time INTEGER NOT NULL, -- in milliseconds
    cache_hit BOOLEAN DEFAULT FALSE,
    namespace TEXT DEFAULT 'default',
    user_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Category statistics table: aggregated performance metrics
CREATE TABLE IF NOT EXISTS category_stats (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL UNIQUE,
    doc_count INTEGER DEFAULT 0,
    avg_response_time DECIMAL(8,2) DEFAULT 0.0,
    total_queries INTEGER DEFAULT 0,
    cache_hit_rate DECIMAL(5,2) DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Embedding metadata table: tracks embedding generation
CREATE TABLE IF NOT EXISTS embedding_metadata (
    id SERIAL PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_count INTEGER NOT NULL,
    embedding_model TEXT,
    processing_time INTEGER, -- in milliseconds
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_namespace ON documents(namespace);
CREATE INDEX IF NOT EXISTS idx_documents_upload_time ON documents(upload_time);
CREATE INDEX IF NOT EXISTS idx_documents_confidence ON documents(confidence);

CREATE INDEX IF NOT EXISTS idx_query_logs_category ON query_logs(category);
CREATE INDEX IF NOT EXISTS idx_query_logs_namespace ON query_logs(namespace);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_query_logs_cache_hit ON query_logs(cache_hit);

CREATE INDEX IF NOT EXISTS idx_category_stats_category ON category_stats(category);
CREATE INDEX IF NOT EXISTS idx_category_stats_last_updated ON category_stats(last_updated);

CREATE INDEX IF NOT EXISTS idx_embedding_metadata_document_id ON embedding_metadata(document_id);
CREATE INDEX IF NOT EXISTS idx_embedding_metadata_created_at ON embedding_metadata(created_at);

-- Create function to update category statistics
CREATE OR REPLACE FUNCTION update_category_stats()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO category_stats (category, doc_count, last_updated)
    VALUES (NEW.category, 1, NOW())
    ON CONFLICT (category) 
    DO UPDATE SET 
        doc_count = category_stats.doc_count + 1,
        last_updated = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update category stats
CREATE TRIGGER trigger_update_category_stats
    AFTER INSERT ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_category_stats();

-- Create function to update query statistics
CREATE OR REPLACE FUNCTION update_query_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE category_stats 
    SET 
        total_queries = total_queries + 1,
        avg_response_time = (avg_response_time * total_queries + NEW.response_time) / (total_queries + 1),
        cache_hit_rate = CASE 
            WHEN total_queries = 0 THEN 0
            ELSE (cache_hit_rate * total_queries + CASE WHEN NEW.cache_hit THEN 1 ELSE 0 END) / (total_queries + 1)
        END,
        last_updated = NOW()
    WHERE category = NEW.category;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update query stats
CREATE TRIGGER trigger_update_query_stats
    AFTER INSERT ON query_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_query_stats();
