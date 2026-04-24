-- Database Connection Pool Stress Test
-- Tests database performance under high connection count and query load
--
-- This test suite should be run with pgbench or similar tool:
-- pgbench -c 1000 -j 100 -T 600 -f connection-pool-test.sql tracertm
--
-- Parameters:
-- -c 1000: 1000 concurrent connections
-- -j 100: 100 worker threads
-- -T 600: 10 minute duration
--
-- Requirements:
-- 1. PostgreSQL 13+ with connection pooling (PgBouncer recommended)
-- 2. Properly configured connection limits
-- 3. Monitoring enabled (pg_stat_statements, pg_stat_activity)

-- =============================================================================
-- Test 1: Connection Pool Saturation
-- =============================================================================
-- Description: Tests behavior when connection pool reaches capacity
-- Expected: Graceful queueing or rejection, no crashes

BEGIN;

-- Simulate holding a connection for varying durations
SELECT pg_sleep(random() * 0.5); -- 0-500ms hold time

-- Simple query to verify connection is alive
SELECT COUNT(*) FROM pg_stat_activity;

COMMIT;

-- =============================================================================
-- Test 2: High Write Throughput (1000 inserts/second target)
-- =============================================================================
-- Description: Tests database write performance under load
-- Expected: Consistent insert performance, no lock contention

BEGIN;

-- Insert into items table (high-traffic table)
INSERT INTO items (
    project_id,
    type,
    title,
    description,
    status,
    priority,
    created_at,
    updated_at
) VALUES (
    floor(random() * 100 + 1)::int, -- Random project 1-100
    (ARRAY['requirement', 'feature', 'task', 'bug'])[floor(random() * 4 + 1)::int],
    'Load Test Item ' || gen_random_uuid()::text,
    'Description for load testing - ' || md5(random()::text),
    (ARRAY['open', 'in_progress', 'done'])[floor(random() * 3 + 1)::int],
    (ARRAY['low', 'medium', 'high', 'critical'])[floor(random() * 4 + 1)::int],
    NOW(),
    NOW()
);

COMMIT;

-- =============================================================================
-- Test 3: Complex Query Performance Under Load
-- =============================================================================
-- Description: Tests complex queries with joins and aggregations
-- Expected: Consistent query performance, proper index usage

BEGIN;

-- Complex query with joins (simulates dashboard query)
SELECT
    p.id,
    p.name,
    COUNT(DISTINCT i.id) as item_count,
    COUNT(DISTINCT l.id) as link_count,
    COUNT(DISTINCT tc.id) as test_case_count,
    AVG(CASE WHEN i.status = 'done' THEN 1 ELSE 0 END) as completion_rate
FROM projects p
LEFT JOIN items i ON p.id = i.project_id
LEFT JOIN links l ON i.id = l.source_id OR i.id = l.target_id
LEFT JOIN test_cases tc ON p.id = tc.project_id
WHERE p.id = floor(random() * 100 + 1)::int
GROUP BY p.id, p.name;

COMMIT;

-- =============================================================================
-- Test 4: Read-Heavy Mixed Workload
-- =============================================================================
-- Description: Simulates typical application read patterns
-- Expected: Fast reads, proper cache utilization

BEGIN;

-- Get project details
SELECT * FROM projects WHERE id = floor(random() * 100 + 1)::int;

-- Get recent items
SELECT * FROM items
WHERE project_id = floor(random() * 100 + 1)::int
ORDER BY updated_at DESC
LIMIT 20;

-- Get item links
SELECT
    l.*,
    i_source.title as source_title,
    i_target.title as target_title
FROM links l
JOIN items i_source ON l.source_id = i_source.id
JOIN items i_target ON l.target_id = i_target.id
WHERE l.source_id = floor(random() * 10000 + 1)::int
LIMIT 10;

COMMIT;

-- =============================================================================
-- Test 5: Connection Churn (Rapid Connect/Disconnect)
-- =============================================================================
-- Description: Tests connection pool behavior with rapid turnover
-- Expected: Efficient connection reuse, no resource leaks

BEGIN;

-- Quick query then disconnect
SELECT COUNT(*) FROM items WHERE project_id = floor(random() * 100 + 1)::int;

COMMIT;

-- =============================================================================
-- Test 6: Search Query Performance
-- =============================================================================
-- Description: Tests full-text search under load
-- Expected: Consistent search performance, proper index usage

BEGIN;

-- Full-text search simulation
SELECT
    i.*,
    ts_rank(
        to_tsvector('english', i.title || ' ' || i.description),
        plainto_tsquery('english', 'performance optimization')
    ) as rank
FROM items i
WHERE
    to_tsvector('english', i.title || ' ' || i.description) @@
    plainto_tsquery('english', 'performance optimization')
ORDER BY rank DESC
LIMIT 20;

COMMIT;

-- =============================================================================
-- Test 7: Transaction Lock Contention
-- =============================================================================
-- Description: Tests behavior under high lock contention
-- Expected: Proper lock handling, no deadlocks

BEGIN;

-- Update random item (creates row lock)
UPDATE items
SET
    status = (ARRAY['open', 'in_progress', 'done'])[floor(random() * 3 + 1)::int],
    updated_at = NOW()
WHERE id = floor(random() * 10000 + 1)::int;

-- Small delay to increase lock contention probability
SELECT pg_sleep(random() * 0.1);

COMMIT;

-- =============================================================================
-- Test 8: Bulk Operations
-- =============================================================================
-- Description: Tests bulk insert/update performance
-- Expected: Efficient batch processing

BEGIN;

-- Bulk insert using VALUES
INSERT INTO links (source_id, target_id, link_type, created_at)
SELECT
    floor(random() * 10000 + 1)::int,
    floor(random() * 10000 + 1)::int,
    (ARRAY['depends_on', 'blocks', 'relates_to'])[floor(random() * 3 + 1)::int],
    NOW()
FROM generate_series(1, 10);

COMMIT;

-- =============================================================================
-- Monitoring Queries
-- Run these separately to monitor test progress
-- =============================================================================

-- Check active connections
-- SELECT
--     COUNT(*) as total_connections,
--     COUNT(*) FILTER (WHERE state = 'active') as active,
--     COUNT(*) FILTER (WHERE state = 'idle') as idle,
--     COUNT(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
-- FROM pg_stat_activity
-- WHERE datname = 'tracertm';

-- Check lock contention
-- SELECT
--     locktype,
--     relation::regclass,
--     mode,
--     COUNT(*) as lock_count
-- FROM pg_locks
-- WHERE NOT granted
-- GROUP BY locktype, relation, mode
-- ORDER BY lock_count DESC;

-- Check slow queries
-- SELECT
--     pid,
--     now() - pg_stat_activity.query_start AS duration,
--     query,
--     state
-- FROM pg_stat_activity
-- WHERE state != 'idle'
--     AND now() - pg_stat_activity.query_start > interval '1 second'
-- ORDER BY duration DESC;

-- Check table bloat and vacuum needs
-- SELECT
--     schemaname,
--     tablename,
--     n_live_tup,
--     n_dead_tup,
--     n_dead_tup::float / NULLIF(n_live_tup, 0) as dead_ratio,
--     last_vacuum,
--     last_autovacuum
-- FROM pg_stat_user_tables
-- WHERE n_dead_tup > 1000
-- ORDER BY n_dead_tup DESC;

-- Check index usage
-- SELECT
--     schemaname,
--     tablename,
--     indexname,
--     idx_scan,
--     idx_tup_read,
--     idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE idx_scan = 0
--     AND indexname NOT LIKE 'pg_%'
-- ORDER BY pg_relation_size(indexrelid) DESC;
