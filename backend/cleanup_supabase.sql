-- Cleanup script to remove existing RAGFlow objects
-- Run this first if you get "already exists" errors

-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_category_stats ON documents;
DROP TRIGGER IF EXISTS trigger_update_query_stats ON query_logs;

-- Drop functions
DROP FUNCTION IF EXISTS update_category_stats();
DROP FUNCTION IF EXISTS update_query_stats();

-- Drop tables (in reverse order due to foreign key constraints)
DROP TABLE IF EXISTS embedding_metadata CASCADE;
DROP TABLE IF EXISTS query_logs CASCADE;
DROP TABLE IF EXISTS category_stats CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- Note: This will delete all existing data!
-- Only run this if you want to start fresh
