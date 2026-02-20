package database

import (
	"context"
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	slowExecTimeThreshold      = 100
	varianceRatioThreshold     = 0.5
	highCallCountThreshold     = 1000
	highCallExecTimeThreshold  = 10
	costPerRowThreshold        = 1
	maxPreparedTransactions    = 100
	optimizationSlowQueryLimit = 20
	queryStatsDistinctMin      = 10
	queryStatsCorrelationMax   = 0.9
	indexSuggestionDistinctMin = 100
	indexSuggestionCorrMax     = 0.5
	missingIndexSeqScanMin     = 1000
	missingIndexLimit          = 20
	missingIndexScanDivisor    = 10
)

// QueryPlan represents an EXPLAIN ANALYZE result
type QueryPlan struct {
	Query         string
	Plan          string
	ExecutionTime float64 // milliseconds
	PlanningTime  float64 // milliseconds
	TotalCost     float64
	Warnings      []string
	Suggestions   []string
}

// ExplainQuery runs EXPLAIN ANALYZE on a query
func ExplainQuery(ctx context.Context, pool *pgxpool.Pool, query string, args ...interface{}) (*QueryPlan, error) {
	explainQuery := "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + query

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to acquire connection: %w", err)
	}
	defer conn.Release()

	var planJSON string
	err = conn.QueryRow(ctx, explainQuery, args...).Scan(&planJSON)
	if err != nil {
		return nil, fmt.Errorf("failed to execute EXPLAIN: %w", err)
	}

	plan := &QueryPlan{
		Query: query,
		Plan:  planJSON,
	}

	// Parse execution time and warnings from plan
	plan.parseExecutionMetrics()
	plan.generateSuggestions()

	return plan, nil
}

// parseExecutionMetrics extracts metrics from the execution plan
func (qp *QueryPlan) parseExecutionMetrics() {
	// This is a simplified version - in production, parse the JSON properly
	qp.ExecutionTime = extractPlanMetricMS(qp.Plan, "Execution Time")
	qp.PlanningTime = extractPlanMetricMS(qp.Plan, "Planning Time")
}

func extractPlanMetricMS(plan, key string) float64 {
	if !strings.Contains(plan, key) {
		return 0
	}

	re := regexp.MustCompile(`"` + regexp.QuoteMeta(key) + `": ([0-9.]+)`)
	matches := re.FindStringSubmatch(plan)
	if len(matches) <= 1 {
		return 0
	}

	var value float64
	if _, err := fmt.Sscanf(matches[1], "%f", &value); err != nil {
		return 0
	}

	return value
}

// generateSuggestions analyzes the plan and generates optimization suggestions
func (qp *QueryPlan) generateSuggestions() {
	planLower := strings.ToLower(qp.Plan)

	// Check for sequential scans
	if strings.Contains(planLower, "seq scan") {
		qp.Warnings = append(qp.Warnings, "Sequential scan detected - consider adding an index")
		qp.Suggestions = append(qp.Suggestions, "Add index on frequently queried columns")
	}

	// Check for high execution time
	if qp.ExecutionTime > slowExecTimeThreshold {
		qp.Warnings = append(qp.Warnings, fmt.Sprintf("High execution time: %.2fms", qp.ExecutionTime))
		qp.Suggestions = append(qp.Suggestions, "Consider query optimization or caching")
	}

	// Check for nested loops on large tables
	if strings.Contains(planLower, "nested loop") && strings.Contains(planLower, "rows=") {
		qp.Warnings = append(qp.Warnings, "Nested loop join detected")
		qp.Suggestions = append(qp.Suggestions, "Consider hash join or merge join for large datasets")
	}

	// Check for missing indexes
	if strings.Contains(planLower, "filter:") {
		qp.Suggestions = append(qp.Suggestions, "Filter condition may benefit from an index")
	}
}

// OptimizeQuery suggests optimizations for a query
func OptimizeQuery(ctx context.Context, pool *pgxpool.Pool, query string) ([]string, error) {
	plan, err := ExplainQuery(ctx, pool, query)
	if err != nil {
		return nil, err
	}

	return plan.Suggestions, nil
}

// QueryPerformanceReport generates a report of the slowest queries
func QueryPerformanceReport(ctx context.Context, pool *pgxpool.Pool, limit int) ([]SlowQueryReport, error) {
	query := `
		SELECT
			query,
			calls,
			total_exec_time,
			mean_exec_time,
			max_exec_time,
			stddev_exec_time,
			rows
		FROM pg_stat_statements
		WHERE query NOT LIKE '%pg_stat_statements%'
			AND query NOT LIKE '%pg_catalog%'
		ORDER BY mean_exec_time DESC
		LIMIT $1
	`

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to acquire connection: %w", err)
	}
	defer conn.Release()

	rows, err := conn.Query(ctx, query, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to query slow queries: %w", err)
	}
	defer rows.Close()

	var reports []SlowQueryReport
	for rows.Next() {
		var report SlowQueryReport
		err := rows.Scan(
			&report.Query,
			&report.Calls,
			&report.TotalExecTime,
			&report.MeanExecTime,
			&report.MaxExecTime,
			&report.StddevExecTime,
			&report.Rows,
		)
		if err != nil {
			continue
		}

		// Classify query type
		report.QueryType = classifyQuery(report.Query)

		// Generate suggestions
		report.Suggestions = generateQuerySuggestions(report)

		reports = append(reports, report)
	}

	return reports, nil
}

// SlowQueryReport represents a slow query analysis
type SlowQueryReport struct {
	Query          string
	QueryType      string
	Calls          int64
	TotalExecTime  float64
	MeanExecTime   float64
	MaxExecTime    float64
	StddevExecTime float64
	Rows           int64
	Suggestions    []string
}

// classifyQuery determines the query type
func classifyQuery(query string) string {
	queryUpper := strings.ToUpper(strings.TrimSpace(query))

	switch {
	case strings.HasPrefix(queryUpper, "SELECT"):
		return "SELECT"
	case strings.HasPrefix(queryUpper, "INSERT"):
		return "INSERT"
	case strings.HasPrefix(queryUpper, "UPDATE"):
		return "UPDATE"
	case strings.HasPrefix(queryUpper, "DELETE"):
		return "DELETE"
	}

	return "OTHER"
}

// generateQuerySuggestions generates optimization suggestions for a slow query
func generateQuerySuggestions(report SlowQueryReport) []string {
	var suggestions []string

	// High execution time
	if report.MeanExecTime > slowExecTimeThreshold {
		suggestions = append(suggestions, fmt.Sprintf(
			"Query is slow (%.2fms avg) - run EXPLAIN ANALYZE to identify bottlenecks",
			report.MeanExecTime,
		))
	}

	// High variance
	if report.StddevExecTime > report.MeanExecTime*varianceRatioThreshold {
		suggestions = append(suggestions, "High execution time variance - consider query stability")
	}

	// High call count with slow execution
	if report.Calls > highCallCountThreshold && report.MeanExecTime > highCallExecTimeThreshold {
		suggestions = append(suggestions, "Frequently called slow query - prime candidate for optimization")
	}

	// Few rows returned despite high cost
	if report.Rows > 0 && report.TotalExecTime/float64(report.Rows) > costPerRowThreshold {
		suggestions = append(suggestions, "High cost per row - check for inefficient joins or filters")
	}

	return suggestions
}

// EnableQueryPlanCache enables query plan caching
func EnableQueryPlanCache(ctx context.Context, pool *pgxpool.Pool) error {
	queries := []string{
		"SET plan_cache_mode = 'force_generic_plan'",
		fmt.Sprintf("SET max_prepared_transactions = %d", maxPreparedTransactions),
	}

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	for _, query := range queries {
		if _, err := conn.Exec(ctx, query); err != nil {
			// Log warning but don't fail
			continue
		}
	}

	return nil
}

// AnalyzeQueryPatterns analyzes query patterns and suggests indexes
func AnalyzeQueryPatterns(ctx context.Context, pool *pgxpool.Pool) ([]IndexSuggestion, error) {
	query := fmt.Sprintf(`
		SELECT
			schemaname,
			tablename,
			attname,
			n_distinct,
			correlation
		FROM pg_stats
		WHERE schemaname = 'public'
			AND n_distinct > %d
			AND correlation < %g
		ORDER BY tablename, attname
	`, queryStatsDistinctMin, queryStatsCorrelationMax)

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()

	rows, err := conn.Query(ctx, query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var suggestions []IndexSuggestion
	for rows.Next() {
		var suggestion IndexSuggestion
		var correlation float64
		var nDistinct float64

		err := rows.Scan(
			&suggestion.SchemaName,
			&suggestion.TableName,
			&suggestion.ColumnName,
			&nDistinct,
			&correlation,
		)
		if err != nil {
			continue
		}

		// Suggest index based on statistics
		if nDistinct > indexSuggestionDistinctMin && correlation < indexSuggestionCorrMax {
			suggestion.IndexType = "btree"
			suggestion.Reason = fmt.Sprintf(
				"High cardinality (%.0f distinct values) with low correlation (%.2f)",
				nDistinct, correlation,
			)
			suggestion.CreateSQL = fmt.Sprintf(
				"CREATE INDEX CONCURRENTLY idx_%s_%s ON %s(%s)",
				suggestion.TableName, suggestion.ColumnName,
				suggestion.TableName, suggestion.ColumnName,
			)
			suggestions = append(suggestions, suggestion)
		}
	}

	return suggestions, nil
}

// IndexSuggestion represents an index creation suggestion
type IndexSuggestion struct {
	SchemaName string
	TableName  string
	ColumnName string
	IndexType  string
	Reason     string
	CreateSQL  string
}

// GetMissingIndexes identifies missing indexes based on query patterns
func GetMissingIndexes(ctx context.Context, pool *pgxpool.Pool) ([]string, error) {
	query := fmt.Sprintf(`
			SELECT DISTINCT
				format('CREATE INDEX CONCURRENTLY idx_%%s_%%s ON %%s(%%s)',
				t.relname,
				a.attname,
				t.relname,
				a.attname
			) AS create_index_sql
		FROM pg_stat_user_tables t
		JOIN pg_attribute a ON a.attrelid = t.relid
		LEFT JOIN pg_index i ON i.indrelid = t.relid
			AND a.attnum = ANY(i.indkey)
		WHERE i.indrelid IS NULL
			AND a.attnum > 0
			AND NOT a.attisdropped
			AND t.seq_scan > %d
			AND t.idx_scan < t.seq_scan / %d
		LIMIT %d
	`, missingIndexSeqScanMin, missingIndexScanDivisor, missingIndexLimit)

	conn, err := pool.Acquire(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()

	rows, err := conn.Query(ctx, query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var indexes []string
	for rows.Next() {
		var indexSQL string
		if err := rows.Scan(&indexSQL); err != nil {
			continue
		}
		indexes = append(indexes, indexSQL)
	}

	return indexes, nil
}

// OptimizationReport generates a comprehensive optimization report
type OptimizationReport struct {
	Timestamp        time.Time
	SlowQueries      []SlowQueryReport
	IndexSuggestions []IndexSuggestion
	MissingIndexes   []string
	DatabaseStats    map[string]interface{}
}

// GenerateOptimizationReport creates a comprehensive optimization report
func GenerateOptimizationReport(ctx context.Context, pool *pgxpool.Pool) (*OptimizationReport, error) {
	report := &OptimizationReport{
		Timestamp: time.Now(),
	}

	// Get slow queries
	slowQueries, err := QueryPerformanceReport(ctx, pool, optimizationSlowQueryLimit)
	if err != nil {
		return nil, fmt.Errorf("failed to get slow queries: %w", err)
	}
	report.SlowQueries = slowQueries

	// Get index suggestions
	indexSuggestions, err := AnalyzeQueryPatterns(ctx, pool)
	if err != nil {
		return nil, fmt.Errorf("failed to analyze query patterns: %w", err)
	}
	report.IndexSuggestions = indexSuggestions

	// Get missing indexes
	missingIndexes, err := GetMissingIndexes(ctx, pool)
	if err != nil {
		return nil, fmt.Errorf("failed to get missing indexes: %w", err)
	}
	report.MissingIndexes = missingIndexes

	// Get database stats
	report.DatabaseStats = GetPoolStats(pool)

	return report, nil
}
