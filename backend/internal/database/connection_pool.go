// Package database provides database functionality.
package database

import (
	"context"
	"fmt"
	"strconv"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	defaultMaxConnections  = 50
	defaultMinConnections  = 10
	defaultMaxConnLifetime = 1 * time.Hour
	defaultMaxConnIdleTime = 30 * time.Minute
	defaultConnectTimeout  = 30 * time.Second
	defaultQueryTimeout    = 30 * time.Second
	defaultAcquireTimeout  = 5 * time.Second
	defaultHistorySize     = 100
	percentScale           = 100
)

// PoolConfig holds enhanced connection pool configuration
type PoolConfig struct {
	// Connection limits
	MaxConnections    int32
	MinConnections    int32
	MaxConnLifetime   time.Duration
	MaxConnIdleTime   time.Duration
	HealthCheckPeriod time.Duration

	// Timeout settings
	ConnectTimeout time.Duration
	QueryTimeout   time.Duration

	// Advanced settings
	AcquireTimeout       time.Duration
	LazyConnect          bool
	PreferSimpleProtocol bool
}

// DefaultPoolConfig returns production-ready pool configuration
func DefaultPoolConfig() *PoolConfig {
	return &PoolConfig{
		MaxConnections:       defaultMaxConnections, // Increased from 25
		MinConnections:       defaultMinConnections, // Increased from 5
		MaxConnLifetime:      defaultMaxConnLifetime,
		MaxConnIdleTime:      defaultMaxConnIdleTime,
		HealthCheckPeriod:    1 * time.Minute,
		ConnectTimeout:       defaultConnectTimeout,
		QueryTimeout:         defaultQueryTimeout,
		AcquireTimeout:       defaultAcquireTimeout,
		LazyConnect:          false,
		PreferSimpleProtocol: false,
	}
}

// PoolMetrics tracks connection pool utilization
type PoolMetrics struct {
	TotalConnections        int32
	IdleConnections         int32
	AcquiredConnections     int32
	ConstructingConnections int32
	AcquireCount            int64
	AcquireDuration         time.Duration
	CanceledAcquireCount    int64
	EmptyAcquireCount       int64
	MaxIdleDestroyCount     int64
	MaxLifetimeDestroyCount int64
}

// PoolMonitor provides real-time pool monitoring
type PoolMonitor struct {
	pool *pgxpool.Pool
	mu   sync.RWMutex

	// Historical metrics
	history    []PoolMetrics
	maxHistory int
}

// NewPoolMonitor creates a new pool monitor
func NewPoolMonitor(pool *pgxpool.Pool) *PoolMonitor {
	return &PoolMonitor{
		pool:       pool,
		history:    make([]PoolMetrics, 0, defaultHistorySize),
		maxHistory: defaultHistorySize,
	}
}

// GetCurrentMetrics returns current pool statistics
func (pm *PoolMonitor) GetCurrentMetrics() *PoolMetrics {
	stat := pm.pool.Stat()

	return &PoolMetrics{
		TotalConnections:        stat.TotalConns(),
		IdleConnections:         stat.IdleConns(),
		AcquiredConnections:     stat.AcquiredConns(),
		ConstructingConnections: stat.ConstructingConns(),
		AcquireCount:            stat.AcquireCount(),
		AcquireDuration:         stat.AcquireDuration(),
		CanceledAcquireCount:    stat.CanceledAcquireCount(),
		EmptyAcquireCount:       stat.EmptyAcquireCount(),
		MaxIdleDestroyCount:     stat.MaxIdleDestroyCount(),
		MaxLifetimeDestroyCount: stat.MaxLifetimeDestroyCount(),
	}
}

// RecordMetrics records current metrics to history
func (pm *PoolMonitor) RecordMetrics() {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	metrics := pm.GetCurrentMetrics()
	pm.history = append(pm.history, *metrics)

	// Keep only last maxHistory entries
	if len(pm.history) > pm.maxHistory {
		pm.history = pm.history[len(pm.history)-pm.maxHistory:]
	}
}

// GetMetricsHistory returns historical metrics
func (pm *PoolMonitor) GetMetricsHistory() []PoolMetrics {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	// Return a copy to avoid race conditions
	history := make([]PoolMetrics, len(pm.history))
	copy(history, pm.history)
	return history
}

// GetUtilizationPercentage returns pool utilization as percentage
func (pm *PoolMonitor) GetUtilizationPercentage() float64 {
	metrics := pm.GetCurrentMetrics()
	if metrics.TotalConnections == 0 {
		return 0
	}
	return float64(metrics.AcquiredConnections) / float64(metrics.TotalConnections) * percentScale
}

// HealthCheck validates pool health
func (pm *PoolMonitor) HealthCheck(ctx context.Context) error {
	// Get a connection from the pool
	conn, err := pm.pool.Acquire(ctx)
	if err != nil {
		return fmt.Errorf("failed to acquire connection: %w", err)
	}
	defer conn.Release()

	// Execute a simple query
	var result int
	if err := conn.QueryRow(ctx, "SELECT 1").Scan(&result); err != nil {
		return fmt.Errorf("failed to execute health check query: %w", err)
	}

	if result != 1 {
		return fmt.Errorf("unexpected health check result: %d", result)
	}

	return nil
}

// StartMonitoring begins periodic pool monitoring
func (pm *PoolMonitor) StartMonitoring(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			pm.RecordMetrics()
		}
	}
}

// InitPoolWithConfig initializes a connection pool with custom configuration
func InitPoolWithConfig(ctx context.Context, databaseURL string, config *PoolConfig) (*pgxpool.Pool, error) {
	// Parse connection string
	poolConfig, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse database URL: %w", err)
	}

	// Apply configuration
	poolConfig.MaxConns = config.MaxConnections
	poolConfig.MinConns = config.MinConnections
	poolConfig.MaxConnLifetime = config.MaxConnLifetime
	poolConfig.MaxConnIdleTime = config.MaxConnIdleTime
	poolConfig.HealthCheckPeriod = config.HealthCheckPeriod

	// Configure connection timeouts
	poolConfig.ConnConfig.ConnectTimeout = config.ConnectTimeout
	poolConfig.ConnConfig.RuntimeParams["statement_timeout"] = strconv.FormatInt(config.QueryTimeout.Milliseconds(), 10)

	// Create connection pool
	pool, err := pgxpool.NewWithConfig(ctx, poolConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create connection pool: %w", err)
	}

	// Test connection if not lazy
	if !config.LazyConnect {
		pingCtx, cancel := context.WithTimeout(ctx, config.ConnectTimeout)
		defer cancel()

		if err := pool.Ping(pingCtx); err != nil {
			pool.Close()
			return nil, fmt.Errorf("failed to ping database: %w", err)
		}
	}

	return pool, nil
}

// GetPoolStats returns comprehensive pool statistics
func GetPoolStats(pool *pgxpool.Pool) map[string]interface{} {
	stat := pool.Stat()

	return map[string]interface{}{
		"total_connections":          stat.TotalConns(),
		"idle_connections":           stat.IdleConns(),
		"acquired_connections":       stat.AcquiredConns(),
		"constructing_connections":   stat.ConstructingConns(),
		"acquire_count":              stat.AcquireCount(),
		"acquire_duration_ms":        stat.AcquireDuration().Milliseconds(),
		"canceled_acquire_count":     stat.CanceledAcquireCount(),
		"empty_acquire_count":        stat.EmptyAcquireCount(),
		"max_idle_destroy_count":     stat.MaxIdleDestroyCount(),
		"max_lifetime_destroy_count": stat.MaxLifetimeDestroyCount(),
	}
}

// WarmupPool pre-creates connections up to MinConns
func WarmupPool(ctx context.Context, pool *pgxpool.Pool, minConns int) error {
	conns := make([]*pgxpool.Conn, 0, minConns)
	defer func() {
		for _, conn := range conns {
			conn.Release()
		}
	}()

	// Acquire connections
	for i := 0; i < minConns; i++ {
		conn, err := pool.Acquire(ctx)
		if err != nil {
			return fmt.Errorf("failed to warmup connection %d: %w", i, err)
		}
		conns = append(conns, conn)
	}

	return nil
}
