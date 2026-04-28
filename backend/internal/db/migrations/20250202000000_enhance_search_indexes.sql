-- Migration: Enhanced Search Indexes and Optimizations
-- Purpose: Optimize search performance for advanced search service

-- =============================================================================
-- PART 1: Verify and Enhance Indexes
-- =============================================================================

-- Ensure search_vector index uses GIN (inverted index, fastest for full-text)
-- Use CREATE INDEX IF NOT EXISTS to avoid dropping if it already exists with correct type
-- Check if index exists and is GIN type, if not, recreate it
-- NOTE: Must drop dependent objects first (views, composite indexes)

-- Drop dependent objects first (if they exist)
DROP VIEW IF EXISTS search_performance CASCADE;
DROP INDEX IF EXISTS idx_items_project_search CASCADE;

-- Ensure search_vector index uses GIN (inverted index, fastest for full-text)
-- Skip if index already exists (idempotent)
-- Note: Index already created in previous migration, so we skip it here
-- Only recreate if it doesn't exist or is wrong type
DO $$
BEGIN
    -- Check if index exists and is GIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'idx_items_search_vector'
        AND schemaname = 'public'
        AND indexdef LIKE '%GIN%'
    ) THEN
        -- Index doesn't exist or is wrong type, create/recreate it
        DROP INDEX IF EXISTS idx_items_search_vector CASCADE;
        CREATE INDEX idx_items_search_vector ON items USING GIN (search_vector);
    ELSE
        RAISE NOTICE 'Index idx_items_search_vector already exists with correct type, skipping';
    END IF;
EXCEPTION WHEN duplicate_table THEN
    RAISE NOTICE 'Index idx_items_search_vector already exists, skipping';
WHEN OTHERS THEN
    RAISE NOTICE 'Could not create idx_items_search_vector: %', SQLERRM;
END $$;

-- Ensure trigram indexes exist for fuzzy search (idempotent - only create if not exists)
CREATE INDEX IF NOT EXISTS idx_items_title_trgm ON items USING GIN (title gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_items_description_trgm ON items USING GIN (description gin_trgm_ops);

-- Combined trigram index for cross-field fuzzy search
CREATE INDEX IF NOT EXISTS idx_items_title_desc_trgm
ON items USING GIN ((title || ' ' || coalesce(description, '')) gin_trgm_ops);

-- =============================================================================
-- PART 2: Optimize HNSW Index for Vector Search
-- =============================================================================

-- Drop old vector index if it exists
DROP INDEX IF EXISTS idx_items_embedding_hnsw;
DROP INDEX IF EXISTS idx_items_embedding_ivfflat;

-- Create optimized HNSW index (if pgvector is available)
-- HNSW is faster and more accurate than IVFFlat for approximate nearest neighbor
DO $$
BEGIN
    -- Check if pgvector extension exists
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        -- Check if index already exists
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_items_embedding_hnsw') THEN
            -- Create HNSW index with optimized parameters
            -- m=16: Good balance of accuracy and speed
            -- ef_construction=64: Build quality (higher = better quality, slower build)
            EXECUTE 'CREATE INDEX idx_items_embedding_hnsw
                     ON items USING hnsw (embedding vector_cosine_ops)
                     WITH (m = 16, ef_construction = 64)
                     WHERE embedding IS NOT NULL AND deleted_at IS NULL';
            RAISE NOTICE 'Created HNSW vector index';
        ELSE
            RAISE NOTICE 'HNSW index already exists, skipping';
        END IF;
    ELSE
        RAISE NOTICE 'pgvector extension not available, skipping vector index';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not create HNSW index: %', SQLERRM;
END $$;

-- =============================================================================
-- PART 3: Add Composite Indexes for Common Query Patterns
-- =============================================================================

-- Index for project + type filtering (common in search)
DROP INDEX IF EXISTS idx_items_project_type;
CREATE INDEX idx_items_project_type
ON items (project_id, type)
WHERE deleted_at IS NULL;

-- Index for project + status filtering
DROP INDEX IF EXISTS idx_items_project_status;
CREATE INDEX idx_items_project_status
ON items (project_id, status)
WHERE deleted_at IS NULL;

-- Index for full-text search with project filter
-- Note: This index depends on search_vector column, not the idx_items_search_vector index
-- So it's safe to create after the search_vector index exists
DROP INDEX IF EXISTS idx_items_project_search CASCADE;
CREATE INDEX idx_items_project_search
ON items (project_id, search_vector)
WHERE deleted_at IS NULL;

-- =============================================================================
-- PART 4: Create Statistics for Query Planner
-- =============================================================================

-- Create extended statistics for better query planning
DROP STATISTICS IF EXISTS items_search_stats;
CREATE STATISTICS items_search_stats (dependencies)
ON project_id, type, status, deleted_at
FROM items;

-- Analyze the table to update statistics
ANALYZE items;

-- =============================================================================
-- PART 5: Create Helper Functions for Search
-- =============================================================================

-- Function to get embedding dimension (useful for validation)
-- Only create if embedding column exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'items' AND column_name = 'embedding'
    ) THEN
        EXECUTE 'CREATE OR REPLACE FUNCTION get_embedding_dimension()
        RETURNS INTEGER AS $func$
        DECLARE
            dim INTEGER;
        BEGIN
            SELECT array_length(embedding::float[], 1)
            INTO dim
            FROM items
            WHERE embedding IS NOT NULL
            LIMIT 1;

            RETURN COALESCE(dim, 0);
        END;
        $func$ LANGUAGE plpgsql';
    ELSE
        RAISE NOTICE 'embedding column does not exist, skipping get_embedding_dimension() function';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not create get_embedding_dimension() function: %', SQLERRM;
END $$;

-- Function to check search readiness
CREATE OR REPLACE FUNCTION search_readiness_check()
RETURNS TABLE (
    check_name TEXT,
    status BOOLEAN,
    details TEXT
) AS $$
BEGIN
    -- Check 1: pg_trgm extension
    RETURN QUERY
    SELECT
        'pg_trgm_extension'::TEXT,
        EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'),
        CASE
            WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm')
            THEN 'Fuzzy search enabled'
            ELSE 'Fuzzy search disabled'
        END;

    -- Check 2: pgvector extension
    RETURN QUERY
    SELECT
        'vector_extension'::TEXT,
        EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector'),
        CASE
            WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')
            THEN 'Semantic search enabled'
            ELSE 'Semantic search disabled'
        END;

    -- Check 3: Search vectors indexed
    RETURN QUERY
    SELECT
        'search_vectors_indexed'::TEXT,
        (SELECT COUNT(*) FROM items WHERE search_vector IS NOT NULL) > 0,
        (SELECT COUNT(*)::TEXT || ' items indexed' FROM items WHERE search_vector IS NOT NULL);

    -- Check 4: Embeddings generated (only if embedding column exists)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'items' AND column_name = 'embedding'
    ) THEN
        RETURN QUERY
        SELECT
            'embeddings_generated'::TEXT,
            (SELECT COUNT(*) FROM items WHERE embedding IS NOT NULL) > 0,
            (SELECT COUNT(*)::TEXT || ' embeddings generated' FROM items WHERE embedding IS NOT NULL);
    ELSE
        RETURN QUERY
        SELECT
            'embeddings_generated'::TEXT,
            false,
            'embedding column not available (pgvector may not be installed)'::TEXT;
    END IF;

    -- Check 5: Index health
    RETURN QUERY
    SELECT
        'index_health'::TEXT,
        EXISTS(
            SELECT 1 FROM pg_stat_user_indexes
            WHERE indexrelname = 'idx_items_search_vector'
            AND idx_scan > 0
        ),
        'Search index ' ||
        CASE
            WHEN EXISTS(
                SELECT 1 FROM pg_stat_user_indexes
                WHERE indexrelname = 'idx_items_search_vector'
                AND idx_scan > 0
            )
            THEN 'is being used'
            ELSE 'has not been used yet'
        END;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- PART 6: Create View for Search Performance Monitoring
-- =============================================================================

-- Drop view first if it exists (will be recreated below)
-- This view doesn't actually depend on the index itself, just queries pg_stat_user_indexes
-- But we drop it here to ensure clean recreation
DROP VIEW IF EXISTS search_performance CASCADE;

CREATE OR REPLACE VIEW search_performance AS
SELECT
    schemaname,
    relname AS tablename,
    indexrelname AS indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE relname = 'items'
  AND (indexrelname LIKE '%search%' OR indexrelname LIKE '%trgm%' OR indexrelname LIKE '%embedding%')
ORDER BY idx_scan DESC;

-- =============================================================================
-- PART 7: Optimize Configuration for Search
-- =============================================================================

-- Set configuration for better full-text search
-- These are session-level settings, but good defaults for search-heavy workloads

-- Increase work_mem for sorting large result sets
-- ALTER SYSTEM SET work_mem = '256MB';

-- Increase shared_buffers for caching
-- ALTER SYSTEM SET shared_buffers = '512MB';

-- Enable parallel query for large searches
-- ALTER SYSTEM SET max_parallel_workers_per_gather = 4;

-- For better trigram performance
-- ALTER SYSTEM SET pg_trgm.similarity_threshold = 0.3;

-- Note: Uncomment above if you have permission to alter system settings
-- Otherwise, these should be set in postgresql.conf

-- =============================================================================
-- PART 8: Create Materialized View for Search Statistics (Optional)
-- =============================================================================

-- Create a materialized view that can be refreshed periodically
-- Useful for dashboards and monitoring
-- Only include embedding column if it exists
DO $$
DECLARE
    has_embedding BOOLEAN;
BEGIN
    -- Check if embedding column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'items' AND column_name = 'embedding'
    ) INTO has_embedding;

    -- Drop existing materialized view if it exists
    DROP MATERIALIZED VIEW IF EXISTS search_statistics;

    IF has_embedding THEN
        -- Create with embedding column
        EXECUTE 'CREATE MATERIALIZED VIEW search_statistics AS
        SELECT
            COUNT(*) FILTER (WHERE search_vector IS NOT NULL) AS items_with_search_vector,
            COUNT(*) FILTER (WHERE embedding IS NOT NULL) AS items_with_embeddings,
            COUNT(*) FILTER (WHERE deleted_at IS NULL) AS active_items,
            COUNT(DISTINCT project_id) AS total_projects,
            COUNT(DISTINCT type) AS total_types,
            pg_size_pretty(pg_total_relation_size(''items'')) AS table_size,
            NOW() AS last_updated
        FROM items';
    ELSE
        -- Create without embedding column
        EXECUTE 'CREATE MATERIALIZED VIEW search_statistics AS
        SELECT
            COUNT(*) FILTER (WHERE search_vector IS NOT NULL) AS items_with_search_vector,
            0::BIGINT AS items_with_embeddings,
            COUNT(*) FILTER (WHERE deleted_at IS NULL) AS active_items,
            COUNT(DISTINCT project_id) AS total_projects,
            COUNT(DISTINCT type) AS total_types,
            pg_size_pretty(pg_total_relation_size(''items'')) AS table_size,
            NOW() AS last_updated
        FROM items';
        RAISE NOTICE 'embedding column not available, search_statistics created without embeddings count';
    END IF;
END $$;

-- Create index on materialized view for faster refresh
CREATE UNIQUE INDEX IF NOT EXISTS search_statistics_idx
ON search_statistics (last_updated);

-- Function to refresh statistics (call this periodically)
CREATE OR REPLACE FUNCTION refresh_search_statistics()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY search_statistics;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- PART 9: Add Comments for Documentation
-- =============================================================================

COMMENT ON INDEX idx_items_search_vector IS
'GIN index for PostgreSQL full-text search. Enables fast keyword-based search.';

COMMENT ON INDEX idx_items_title_trgm IS
'Trigram index for fuzzy matching on item titles. Enables typo-tolerant search.';

COMMENT ON INDEX idx_items_description_trgm IS
'Trigram index for fuzzy matching on descriptions. Enables typo-tolerant search.';

-- Only add comment if HNSW index exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_items_embedding_hnsw') THEN
        EXECUTE 'COMMENT ON INDEX idx_items_embedding_hnsw IS
                ''HNSW index for approximate nearest neighbor vector search. Enables semantic search with pgvector.''';
    END IF;
END $$;

COMMENT ON INDEX idx_items_project_type IS
'Composite index for filtering by project and type. Speeds up common query patterns.';

COMMENT ON FUNCTION search_readiness_check IS
'Checks if search infrastructure is properly configured and operational.';

COMMENT ON MATERIALIZED VIEW search_statistics IS
'Cached statistics about search infrastructure. Refresh with refresh_search_statistics().';

-- =============================================================================
-- PART 10: Grant Permissions
-- =============================================================================

-- Grant execute permissions on helper functions
-- GRANT EXECUTE ON FUNCTION get_embedding_dimension() TO authenticated;
-- GRANT EXECUTE ON FUNCTION search_readiness_check() TO authenticated;
-- GRANT EXECUTE ON FUNCTION refresh_search_statistics() TO authenticated;

-- Grant select permissions on views
-- GRANT SELECT ON search_performance TO authenticated;
-- GRANT SELECT ON search_statistics TO authenticated;

-- Note: Uncomment above if using Supabase RLS or similar auth system

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Run readiness check
SELECT * FROM search_readiness_check();

-- Show search performance stats
SELECT * FROM search_performance;

-- Show current statistics
SELECT * FROM search_statistics;
