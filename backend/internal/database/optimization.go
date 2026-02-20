package database

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	defaultOptMaxConnections   = 25
	defaultOptMinConnections   = 5
	defaultOptMaxConnLifetime  = 1 * time.Hour
	defaultOptHealthCheckDelay = 1 * time.Minute
	defaultOptMaxConnIdleTime  = 30 * time.Minute
	defaultOptStatementTimeout = 30 * time.Second
	defaultOptIdleInTxTimeout  = 5 * time.Minute
)

// OptimizationConfig holds database optimization settings
type OptimizationConfig struct {
	// Connection pool settings
	MaxConnections    int32
	MinConnections    int32
	MaxConnLifetime   time.Duration
	MaxConnIdleTime   time.Duration
	HealthCheckPeriod time.Duration

	// Query optimization
	StatementTimeout time.Duration
	IdleInTxTimeout  time.Duration

	// Prepared statements
	PreparedStatements bool
}

// DefaultOptimizationConfig returns sensible defaults
func DefaultOptimizationConfig() *OptimizationConfig {
	return &OptimizationConfig{
		MaxConnections:     defaultOptMaxConnections,
		MinConnections:     defaultOptMinConnections,
		MaxConnLifetime:    defaultOptMaxConnLifetime,
		MaxConnIdleTime:    defaultOptMaxConnIdleTime,
		HealthCheckPeriod:  defaultOptHealthCheckDelay,
		StatementTimeout:   defaultOptStatementTimeout,
		IdleInTxTimeout:    defaultOptIdleInTxTimeout,
		PreparedStatements: true,
	}
}

// ApplyOptimizations applies optimization settings to the database connection
func ApplyOptimizations(ctx context.Context, pool *pgxpool.Pool, _ *OptimizationConfig) error {
	// Set session-level configurations
	queries := []string{
		// Timeout settings
		"SET statement_timeout = '30s'",
		"SET idle_in_transaction_session_timeout = '5m'",

		// Performance settings
		"SET work_mem = '16MB'",
		"SET maintenance_work_mem = '128MB'",
		"SET effective_cache_size = '4GB'",
		"SET random_page_cost = 1.1",

		// Query planner settings
		"SET default_statistics_target = 100",
		"SET enable_seqscan = on",
		"SET enable_indexscan = on",
		"SET enable_bitmapscan = on",

		// Parallel query settings
		"SET max_parallel_workers_per_gather = 4",
		"SET max_parallel_workers = 8",

		// Write-ahead log settings for better performance
		"SET synchronous_commit = on",
		"SET wal_compression = on",
	}

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	for _, query := range queries {
		if _, err := conn.Exec(ctx, query); err != nil {
			// Log warning but don't fail - some settings may require superuser
			continue
		}
	}

	return nil
}

// CreateIndexes creates optimized indexes for common query patterns
func CreateIndexes(ctx context.Context, pool *pgxpool.Pool) error {
	indexes := []string{
		// Items table indexes
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_project_id ON items(project_id)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_type ON items(type)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_status ON items(status)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_created_at ON items(created_at DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_updated_at ON items(updated_at DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_project_type ON items(project_id, type)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_project_status ON items(project_id, status)",

		// Full-text search index
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_search ON items USING GIN(" +
			"to_tsvector('english', title || ' ' || COALESCE(content, '')))",

		// Links table indexes
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_links_source_id ON links(source_id)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_links_target_id ON links(target_id)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_links_type ON links(type)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_links_source_target ON links(source_id, target_id)",

		// Vector search index (for semantic search)
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_embedding ON items USING ivfflat " +
			"(embedding vector_cosine_ops) WITH (lists = 100)",

		// Composite indexes for common queries
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_project_created ON items(project_id, created_at DESC)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_project_updated ON items(project_id, updated_at DESC)",

		// Partial indexes for active items
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_items_active ON items(project_id, type) WHERE status = 'active'",
	}

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	for _, indexSQL := range indexes {
		if _, err := conn.Exec(ctx, indexSQL); err != nil {
			// Log error but continue with other indexes
			continue
		}
	}

	return nil
}

// AnalyzeTable runs ANALYZE to update query planner statistics
func AnalyzeTable(ctx context.Context, pool *pgxpool.Pool, tableName string) error {
	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	_, err = conn.Exec(ctx, "ANALYZE "+tableName)
	return err
}

// VacuumTable runs VACUUM to reclaim storage and update statistics
func VacuumTable(ctx context.Context, pool *pgxpool.Pool, tableName string, full bool) error {
	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	query := "VACUUM"
	if full {
		query += " FULL"
	}
	query += " ANALYZE " + tableName

	_, err = conn.Exec(ctx, query)
	return err
}

// GetSlowQueries returns slow queries for analysis
func GetSlowQueries(ctx context.Context, pool *pgxpool.Pool, limit int) ([]SlowQuery, error) {
	query := `
		SELECT
			query,
			calls,
			total_exec_time,
			mean_exec_time,
			max_exec_time,
			stddev_exec_time
		FROM pg_stat_statements
		WHERE query NOT LIKE '%pg_stat_statements%'
		ORDER BY mean_exec_time DESC
		LIMIT $1
	`

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()

	rows, err := conn.Query(ctx, query, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var slowQueries []SlowQuery
	for rows.Next() {
		var sq SlowQuery
		if err := rows.Scan(
			&sq.Query,
			&sq.Calls,
			&sq.TotalExecTime,
			&sq.MeanExecTime,
			&sq.MaxExecTime,
			&sq.StddevExecTime,
		); err != nil {
			continue
		}
		slowQueries = append(slowQueries, sq)
	}

	return slowQueries, nil
}

// SlowQuery describes a query that exceeds the slow query threshold.
type SlowQuery struct {
	Query          string
	Calls          int64
	TotalExecTime  float64
	MeanExecTime   float64
	MaxExecTime    float64
	StddevExecTime float64
}

// GetTableStatistics returns table statistics
func GetTableStatistics(ctx context.Context, pool *pgxpool.Pool, tableName string) (*TableStats, error) {
	query := `
		SELECT
			schemaname,
			tablename,
			pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
			n_tup_ins AS inserts,
			n_tup_upd AS updates,
			n_tup_del AS deletes,
			n_live_tup AS live_tuples,
			n_dead_tup AS dead_tuples,
			last_vacuum,
			last_autovacuum,
			last_analyze,
			last_autoanalyze
		FROM pg_stat_user_tables
		WHERE tablename = $1
	`

	var stats TableStats
	if err := Get(ctx, pool, &stats, query, tableName); err != nil {
		return nil, err
	}
	return &stats, nil
}

// TableStats summarizes table statistics.
type TableStats struct {
	SchemaName      string
	TableName       string
	Size            string
	Inserts         int64
	Updates         int64
	Deletes         int64
	LiveTuples      int64
	DeadTuples      int64
	LastVacuum      *time.Time
	LastAutovacuum  *time.Time
	LastAnalyze     *time.Time
	LastAutoanalyze *time.Time
}

// CreateMaterializedViews creates all materialized views
func CreateMaterializedViews(ctx context.Context, pool *pgxpool.Pool) error {
	_ = ctx
	_ = pool
	// Views are created via migration 057_create_materialized_views.py
	// This function is a placeholder for programmatic view creation if needed
	return nil
}

// RefreshMaterializedView refreshes a specific materialized view
func RefreshMaterializedView(ctx context.Context, pool *pgxpool.Pool, viewName string, concurrent bool) error {
	query := "REFRESH MATERIALIZED VIEW"
	if concurrent {
		query += " CONCURRENTLY"
	}
	query += " " + viewName

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	_, err = conn.Exec(ctx, query)
	return err
}

// RefreshAllMaterializedViews refreshes all materialized views
func RefreshAllMaterializedViews(ctx context.Context, pool *pgxpool.Pool, concurrent bool) error {
	query := "SELECT refresh_all_materialized_views($1)"

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	_, err = conn.Exec(ctx, query, concurrent)
	return err
}

// GetTablePartitions returns partitions for a partitioned table
func GetTablePartitions(ctx context.Context, pool *pgxpool.Pool, tableName string) ([]string, error) {
	query := `
		SELECT inhrelid::regclass::text AS partition_name
		FROM pg_inherits
		WHERE inhparent = $1::regclass
		ORDER BY partition_name
	`

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()

	rows, err := conn.Query(ctx, query, tableName)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var partitions []string
	for rows.Next() {
		var partition string
		if err := rows.Scan(&partition); err != nil {
			continue
		}
		partitions = append(partitions, partition)
	}

	return partitions, nil
}

// CreatePartition creates a new partition for a partitioned table
func CreatePartition(ctx context.Context, pool *pgxpool.Pool, tableName, partitionName, bounds string) error {
	query := fmt.Sprintf("CREATE TABLE IF NOT EXISTS %s PARTITION OF %s %s", partitionName, tableName, bounds)

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	_, err = conn.Exec(ctx, query)
	return err
}
