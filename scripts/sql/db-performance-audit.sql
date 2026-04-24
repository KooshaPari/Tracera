-- Database Performance Audit Script
-- Run this script to identify performance issues and optimization opportunities
--
-- Prerequisites:
-- - PostgreSQL 12+
-- - pg_stat_statements extension enabled
--
-- Usage:
--   psql -d tracertm -f scripts/db-performance-audit.sql > audit-report.txt

\echo '========================================='
\echo 'DATABASE PERFORMANCE AUDIT REPORT'
\echo 'Generated:' `date`
\echo '========================================='
\echo ''

-- =========================================================================
-- 1. DATABASE SIZE AND TABLE STATISTICS
-- =========================================================================
\echo '1. DATABASE SIZE AND TABLE STATISTICS'
\echo '-------------------------------------'

SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_row_percentage
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

\echo ''

-- =========================================================================
-- 2. TABLE BLOAT DETECTION
-- =========================================================================
\echo '2. TABLE BLOAT DETECTION (Tables with >20% bloat)'
\echo '-------------------------------------------------'

SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS bloat_percentage,
    last_vacuum,
    last_autovacuum,
    CASE
        WHEN last_vacuum IS NULL AND last_autovacuum IS NULL THEN 'NEVER VACUUMED'
        WHEN last_vacuum > last_autovacuum OR last_autovacuum IS NULL THEN 'Manual vacuum: ' || last_vacuum::text
        ELSE 'Auto vacuum: ' || last_autovacuum::text
    END AS last_cleanup
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
    AND ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) > 20
ORDER BY bloat_percentage DESC;

\echo ''

-- =========================================================================
-- 3. SLOW QUERIES (Top 20 by mean execution time)
-- =========================================================================
\echo '3. SLOW QUERIES (Top 20 by mean execution time)'
\echo '-----------------------------------------------'

SELECT
    SUBSTRING(query, 1, 100) AS query_preview,
    calls,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms,
    ROUND(mean_exec_time::numeric, 2) AS mean_time_ms,
    ROUND(max_exec_time::numeric, 2) AS max_time_ms,
    ROUND(stddev_exec_time::numeric, 2) AS stddev_ms,
    rows AS rows_returned
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
    AND query NOT LIKE '%pg_catalog%'
ORDER BY mean_exec_time DESC
LIMIT 20;

\echo ''

-- =========================================================================
-- 4. MOST FREQUENTLY CALLED QUERIES
-- =========================================================================
\echo '4. MOST FREQUENTLY CALLED QUERIES'
\echo '----------------------------------'

SELECT
    SUBSTRING(query, 1, 100) AS query_preview,
    calls,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms,
    ROUND(mean_exec_time::numeric, 2) AS mean_time_ms,
    ROUND((100 * total_exec_time / SUM(total_exec_time) OVER ())::numeric, 2) AS pct_total_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY calls DESC
LIMIT 20;

\echo ''

-- =========================================================================
-- 5. MISSING INDEXES (High seq_scan, low idx_scan)
-- =========================================================================
\echo '5. MISSING INDEXES (Tables with high sequential scans)'
\echo '------------------------------------------------------'

SELECT
    schemaname,
    tablename,
    seq_scan,
    idx_scan,
    CASE
        WHEN seq_scan > 0 THEN ROUND(100.0 * idx_scan / NULLIF(seq_scan + idx_scan, 0), 2)
        ELSE 0
    END AS index_usage_percentage,
    n_live_tup AS rows,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
WHERE seq_scan > 1000
    AND (idx_scan < seq_scan / 10 OR idx_scan = 0)
    AND pg_total_relation_size(schemaname||'.'||tablename) > 100000 -- > 100KB
ORDER BY seq_scan DESC, pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

\echo ''

-- =========================================================================
-- 6. UNUSED INDEXES
-- =========================================================================
\echo '6. UNUSED INDEXES (Candidates for removal)'
\echo '-------------------------------------------'

SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey'
    AND pg_relation_size(indexrelid) > 100000 -- > 100KB
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;

\echo ''

-- =========================================================================
-- 7. INDEX USAGE STATISTICS
-- =========================================================================
\echo '7. INDEX USAGE STATISTICS (Most used indexes)'
\echo '---------------------------------------------'

SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan > 0
ORDER BY idx_scan DESC
LIMIT 20;

\echo ''

-- =========================================================================
-- 8. CONNECTION POOL STATISTICS
-- =========================================================================
\echo '8. CONNECTION POOL STATISTICS'
\echo '-----------------------------'

SELECT
    datname AS database,
    numbackends AS active_connections,
    xact_commit AS committed_transactions,
    xact_rollback AS rolled_back_transactions,
    blks_read AS disk_blocks_read,
    blks_hit AS cache_blocks_hit,
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS cache_hit_ratio,
    tup_returned AS tuples_returned,
    tup_fetched AS tuples_fetched,
    tup_inserted AS tuples_inserted,
    tup_updated AS tuples_updated,
    tup_deleted AS tuples_deleted
FROM pg_stat_database
WHERE datname = current_database();

\echo ''

-- =========================================================================
-- 9. LOCK CONTENTION
-- =========================================================================
\echo '9. LOCK CONTENTION (Current locks)'
\echo '----------------------------------'

SELECT
    locktype,
    relation::regclass AS relation,
    mode,
    COUNT(*) AS lock_count
FROM pg_locks
WHERE granted = true
GROUP BY locktype, relation, mode
HAVING COUNT(*) > 1
ORDER BY lock_count DESC;

\echo ''

-- =========================================================================
-- 10. SUGGESTED OPTIMIZATIONS
-- =========================================================================
\echo '10. SUGGESTED OPTIMIZATIONS'
\echo '---------------------------'

\echo 'A. Tables needing VACUUM:'
SELECT
    schemaname || '.' || tablename AS table_name,
    'VACUUM ANALYZE ' || schemaname || '.' || tablename || ';' AS suggested_command
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
    OR (last_autovacuum IS NULL AND n_live_tup > 1000)
ORDER BY n_dead_tup DESC
LIMIT 10;

\echo ''
\echo 'B. Potential indexes to create (based on query patterns):'
SELECT DISTINCT
    'CREATE INDEX CONCURRENTLY idx_' || t.relname || '_' || a.attname ||
    ' ON ' || t.relname || '(' || a.attname || ');' AS suggested_index
FROM pg_stat_user_tables t
JOIN pg_attribute a ON a.attrelid = t.relid
LEFT JOIN pg_index i ON i.indrelid = t.relid AND a.attnum = ANY(i.indkey)
WHERE i.indrelid IS NULL
    AND a.attnum > 0
    AND NOT a.attisdropped
    AND t.seq_scan > 1000
    AND t.idx_scan < t.seq_scan / 10
LIMIT 10;

\echo ''
\echo 'C. Maintenance tasks:'
\echo 'ANALYZE;  -- Update query planner statistics'
\echo 'REINDEX DATABASE CONCURRENTLY tracertm;  -- Rebuild fragmented indexes'
\echo 'SELECT maintain_partitions();  -- Ensure future partitions exist'
\echo 'SELECT scheduled_refresh_materialized_views();  -- Refresh dashboard views'

\echo ''
\echo '========================================='
\echo 'END OF AUDIT REPORT'
\echo '========================================='
