package middleware

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

const (
	slowQueryDefaultThreshold = 100 * time.Millisecond
	slowQueryMetricsThreshold = 100 * time.Millisecond
	slowQueryMaxSQLLength     = 200
)

// SlowQueryConfig configures slow query logging
type SlowQueryConfig struct {
	Threshold      time.Duration // Queries slower than this will be logged
	LogStackTrace  bool          // Include stack trace for slow queries
	LogQueryParams bool          // Include query parameters (be careful with sensitive data)
	EnableMetrics  bool          // Collect metrics for analysis
}

// DefaultSlowQueryConfig returns sensible defaults
func DefaultSlowQueryConfig() SlowQueryConfig {
	return SlowQueryConfig{
		Threshold:      slowQueryDefaultThreshold,
		LogStackTrace:  false,
		LogQueryParams: true,
		EnableMetrics:  true,
	}
}

// SlowQueryLogger implements GORM's logger interface with slow query detection
type SlowQueryLogger struct {
	config       SlowQueryConfig
	baseLogger   logger.Interface
	metricsStore *QueryMetricsStore
}

// NewSlowQueryLogger creates a new slow query logger
func NewSlowQueryLogger(config SlowQueryConfig) *SlowQueryLogger {
	var metricsStore *QueryMetricsStore
	if config.EnableMetrics {
		metricsStore = NewQueryMetricsStore()
	}

	return &SlowQueryLogger{
		config:       config,
		baseLogger:   logger.Default,
		metricsStore: metricsStore,
	}
}

// LogMode sets the log mode
func (l *SlowQueryLogger) LogMode(level logger.LogLevel) logger.Interface {
	newLogger := *l
	newLogger.baseLogger = l.baseLogger.LogMode(level)
	return &newLogger
}

// Info logs info messages
func (l *SlowQueryLogger) Info(ctx context.Context, msg string, data ...interface{}) {
	l.baseLogger.Info(ctx, msg, data...)
}

// Warn logs warning messages
func (l *SlowQueryLogger) Warn(ctx context.Context, msg string, data ...interface{}) {
	l.baseLogger.Warn(ctx, msg, data...)
}

// Error logs error messages
func (l *SlowQueryLogger) Error(ctx context.Context, msg string, data ...interface{}) {
	l.baseLogger.Error(ctx, msg, data...)
}

// Trace logs SQL queries with slow query detection
func (l *SlowQueryLogger) Trace(ctx context.Context, begin time.Time, fc func() (sql string, rowsAffected int64), err error) {
	elapsed := time.Since(begin)
	sql, rows := fc()

	// Always record metrics if enabled
	if l.metricsStore != nil {
		l.metricsStore.RecordQuery(sql, elapsed, rows, err)
	}

	// Check if query is slow
	if elapsed >= l.config.Threshold {
		// Log slow query with detailed information
		l.logSlowQuery(ctx, sql, elapsed, rows, err)
	}

	// Still pass through to base logger for standard logging
	l.baseLogger.Trace(ctx, begin, fc, err)
}

// logSlowQuery logs detailed information about slow queries
func (l *SlowQueryLogger) logSlowQuery(_ context.Context, sql string, elapsed time.Duration, rows int64, err error) {
	logMsg := fmt.Sprintf("🐌 SLOW QUERY [%v] rows=%d sql=%s",
		elapsed.Round(time.Millisecond),
		rows,
		sql,
	)

	if err != nil {
		logMsg += fmt.Sprintf(" error=%v", err)
	}

	// Log to standard logger
	slog.Info("message", "detail", logMsg)

	// Note: Monitoring system integration (Prometheus, DataDog) not yet implemented
	// if l.config.EnableMetrics {
	//     metrics.RecordSlowQuery(sql, elapsed)
	// }
}

// GetMetrics returns query metrics (if enabled)
func (l *SlowQueryLogger) GetMetrics() *QueryMetricsStore {
	return l.metricsStore
}

// QueryMetrics represents metrics for a single query pattern
type QueryMetrics struct {
	QueryPattern      string
	Count             int64
	TotalDuration     time.Duration
	MinDuration       time.Duration
	MaxDuration       time.Duration
	AvgDuration       time.Duration
	SlowCount         int64 // Queries over threshold
	ErrorCount        int64
	LastSeen          time.Time
	TotalRowsAffected int64
}

// QueryMetricsStore stores query performance metrics
type QueryMetricsStore struct {
	metrics   map[string]*QueryMetrics
	threshold time.Duration
}

// NewQueryMetricsStore creates a new metrics store
func NewQueryMetricsStore() *QueryMetricsStore {
	return &QueryMetricsStore{
		metrics:   make(map[string]*QueryMetrics),
		threshold: slowQueryMetricsThreshold,
	}
}

// RecordQuery records metrics for a query
func (s *QueryMetricsStore) RecordQuery(sql string, duration time.Duration, rows int64, err error) {
	// Normalize query to pattern (remove specific values)
	pattern := normalizeQuery(sql)

	metric, exists := s.metrics[pattern]
	if !exists {
		metric = &QueryMetrics{
			QueryPattern: pattern,
			MinDuration:  duration,
			MaxDuration:  duration,
		}
		s.metrics[pattern] = metric
	}

	// Update metrics
	metric.Count++
	metric.TotalDuration += duration
	metric.TotalRowsAffected += rows
	metric.LastSeen = time.Now()

	if duration > metric.MaxDuration {
		metric.MaxDuration = duration
	}
	if duration < metric.MinDuration {
		metric.MinDuration = duration
	}

	metric.AvgDuration = metric.TotalDuration / time.Duration(metric.Count)

	if duration >= s.threshold {
		metric.SlowCount++
	}

	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		metric.ErrorCount++
	}
}

// GetTopSlowQueries returns the N slowest query patterns
func (s *QueryMetricsStore) GetTopSlowQueries(n int) []*QueryMetrics {
	// Convert map to slice
	metrics := make([]*QueryMetrics, 0, len(s.metrics))
	for _, m := range s.metrics {
		metrics = append(metrics, m)
	}

	// Sort by avg duration (descending)
	for i := 0; i < len(metrics); i++ {
		for j := i + 1; j < len(metrics); j++ {
			if metrics[j].AvgDuration > metrics[i].AvgDuration {
				metrics[i], metrics[j] = metrics[j], metrics[i]
			}
		}
	}

	// Return top N
	if n > len(metrics) {
		n = len(metrics)
	}
	return metrics[:n]
}

// GetAllMetrics returns all collected metrics
func (s *QueryMetricsStore) GetAllMetrics() []*QueryMetrics {
	metrics := make([]*QueryMetrics, 0, len(s.metrics))
	for _, m := range s.metrics {
		metrics = append(metrics, m)
	}
	return metrics
}

// normalizeQuery simplifies a query to its pattern
// This is a simple implementation - a more sophisticated one could be added later
func normalizeQuery(sql string) string {
	// Note: Advanced query normalization not yet implemented
	// For now, just truncate very long queries
	if len(sql) > slowQueryMaxSQLLength {
		return sql[:slowQueryMaxSQLLength] + "..."
	}
	return sql
}

// RegisterGormPlugin registers the slow query logger as a GORM plugin
func RegisterGormPlugin(db *gorm.DB, config SlowQueryConfig) error {
	slowLogger := NewSlowQueryLogger(config)
	db.Logger = slowLogger
	return nil
}
