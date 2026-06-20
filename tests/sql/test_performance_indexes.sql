-- Performance Indexes Test Suite
-- Tests to verify all performance indexes are created and functional

-- Setup: Connect to your database first
-- psql -d trace_db -f tests/sql/test_performance_indexes.sql

-- ============================================================================
-- PART 1: VERIFY INDEX CREATION
-- ============================================================================

-- Check all expected indexes exist
SELECT
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename IN ('items', 'links', 'change_log')
AND schemaname = 'public'
ORDER BY tablename, indexname;

-- Expected output: 23 rows (22 + 1 FTS index)

-- ============================================================================
-- PART 2: VERIFY INDEX TYPES AND COLUMNS
-- ============================================================================

-- Links indexes
SELECT
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename = 'links'
AND schemaname = 'public'
ORDER BY indexname;

-- Expected:
-- ix_links_created_at       - single column (created_at)
-- ix_links_source_id        - single column (source_id)
-- ix_links_source_target    - composite (source_id, target_id)
-- ix_links_source_type      - composite (source_id, type)
-- ix_links_target_id        - single column (target_id)
-- ix_links_type             - single column (type)
-- ix_links_type_created     - composite (type, created_at)
-- ix_links_updated_at       - single column (updated_at)

-- Items indexes
SELECT
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename = 'items'
AND schemaname = 'public'
ORDER BY indexname;

-- Expected:
-- ix_items_created_at                - single column
-- ix_items_owner                     - single column
-- ix_items_parent_id                 - single column (with NULL filter)
-- ix_items_parent_status             - composite
-- ix_items_priority                  - single column
-- ix_items_project_id                - single column
-- ix_items_project_owner             - composite
-- ix_items_project_status            - composite
-- ix_items_project_status_priority   - composite (3 columns)
-- ix_items_project_updated           - composite
-- ix_items_search                    - full-text (GIN)
-- ix_items_status                    - single column
-- ix_items_type                      - single column
-- ix_items_updated_at                - single column

-- ============================================================================
-- PART 3: INDEX USAGE MONITORING
-- ============================================================================

-- Check current index usage statistics
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan as scans,
  idx_tup_read as tuples_read,
  idx_tup_fetch as tuples_fetched,
  pg_size_pretty(pg_relation_size(indexrelid)) as size,
  ROUND(100.0 * idx_scan / NULLIF(
    (SELECT idx_scan FROM pg_stat_user_indexes
     WHERE tablename IN ('items', 'links', 'change_log')
     AND schemaname = 'public' LIMIT 1), 0), 2) as usage_percent
FROM pg_stat_user_indexes
WHERE tablename IN ('items', 'links', 'change_log')
AND schemaname = 'public'
ORDER BY idx_scan DESC, tablename, indexname;

-- ============================================================================
-- PART 4: TEST QUERY PLANS (Requires sample data)
-- ============================================================================

-- NOTE: Run these after applying migration and with sample data

-- TEST 1: Links by source_id
-- Should use ix_links_source_id
EXPLAIN ANALYZE
SELECT * FROM links WHERE source_id = '550e8400-e29b-41d4-a716-446655440001'::uuid;

-- TEST 2: Links by target_id
-- Should use ix_links_target_id
EXPLAIN ANALYZE
SELECT * FROM links WHERE target_id = '550e8400-e29b-41d4-a716-446655440002'::uuid;

-- TEST 3: Links by source and type
-- Should use ix_links_source_type
EXPLAIN ANALYZE
SELECT * FROM links WHERE source_id = '550e8400-e29b-41d4-a716-446655440001'::uuid AND type = 'depends_on';

-- TEST 4: Items by project
-- Should use ix_items_project_id
EXPLAIN ANALYZE
SELECT * FROM items WHERE project_id = '550e8400-e29b-41d4-a716-446655440000'::uuid;

-- TEST 5: Items by project and status (covering index)
-- Should use ix_items_project_status
EXPLAIN ANALYZE
SELECT * FROM items WHERE project_id = '550e8400-e29b-41d4-a716-446655440000'::uuid AND status = 'active';

-- TEST 6: Items hierarchy
-- Should use ix_items_parent_id
EXPLAIN ANALYZE
SELECT * FROM items WHERE parent_id = '550e8400-e29b-41d4-a716-446655440003'::uuid;

-- TEST 7: Recent items
-- Should use ix_items_updated_at
EXPLAIN ANALYZE
SELECT * FROM items WHERE updated_at > now() - interval '7 days' ORDER BY updated_at DESC LIMIT 20;

-- TEST 8: Full-text search
-- Should use ix_items_search (GIN)
EXPLAIN ANALYZE
SELECT * FROM items WHERE to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, ''))
                       @@ plainto_tsquery('english', 'search term');

-- TEST 9: Dashboard query
-- Should use ix_items_project_status_priority
EXPLAIN ANALYZE
SELECT * FROM items
WHERE project_id = '550e8400-e29b-41d4-a716-446655440000'::uuid
AND status = 'active'
ORDER BY priority DESC;

-- ============================================================================
-- PART 5: INDEX SIZE ANALYSIS
-- ============================================================================

-- Overall index storage consumption
SELECT
  tablename,
  COUNT(*) as index_count,
  pg_size_pretty(SUM(pg_relation_size(indexrelid))) as total_size,
  ROUND(AVG(pg_relation_size(indexrelid))::numeric) as avg_size
FROM pg_stat_user_indexes
WHERE tablename IN ('items', 'links', 'change_log')
AND schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

-- Detailed breakdown
SELECT
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE tablename IN ('items', 'links', 'change_log')
AND schemaname = 'public'
ORDER BY tablename, pg_relation_size(indexrelid) DESC;

-- ============================================================================
-- PART 6: POTENTIAL ISSUES
-- ============================================================================

-- Find unused indexes (may indicate redundant indexes)
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND tablename IN ('items', 'links', 'change_log')
AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================================================
-- PART 7: MAINTENANCE
-- ============================================================================

-- Refresh table statistics (for accurate query planning)
-- Run after significant data changes
ANALYZE items;
ANALYZE links;
ANALYZE change_log;

-- Check bloated indexes (only needed if index is heavily modified)
-- SELECT * FROM pg_stat_user_indexes WHERE idx_scan > 10000000;

-- To rebuild a specific index if bloated:
-- REINDEX INDEX CONCURRENTLY ix_items_project_status;

-- ============================================================================
-- PART 8: PERFORMANCE BASELINE
-- ============================================================================

-- Create baseline statistics for comparison
CREATE TEMP TABLE IF NOT EXISTS index_baseline AS
SELECT
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch,
  pg_relation_size(indexrelid) as size,
  now()::timestamp as baseline_time
FROM pg_stat_user_indexes
WHERE tablename IN ('items', 'links', 'change_log')
AND schemaname = 'public';

-- Run queries and then check improvement:
-- SELECT * FROM index_baseline;
-- SELECT * FROM pg_stat_user_indexes WHERE tablename IN ('items', 'links', 'change_log');
-- Compare idx_scan and idx_tup_fetch between baseline and current stats
