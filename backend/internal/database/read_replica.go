package database

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	defaultReplicaLagThresholdMs  = 1000
	defaultReplicaHealthInterval  = 10 * time.Second
	defaultReplicaMaxConns        = 50
	defaultReplicaMinConns        = 10
	defaultReplicaMaxConnLifetime = 1 * time.Hour
	defaultReplicaMaxConnIdleTime = 30 * time.Minute
	defaultReplicaPingTimeout     = 10 * time.Second
	defaultReplicaHealthTimeout   = 5 * time.Second
)

// ReadReplicaConfig holds read replica configuration
type ReadReplicaConfig struct {
	ReplicaDSN          string
	LagThresholdMs      int64 // Maximum acceptable replication lag in milliseconds
	HealthCheckInterval time.Duration
	FallbackToPrimary   bool // Fallback to primary if replica is unhealthy
}

// DefaultReplicaConfig returns default replica configuration
func DefaultReplicaConfig(replicaDSN string) *ReadReplicaConfig {
	return &ReadReplicaConfig{
		ReplicaDSN:          replicaDSN,
		LagThresholdMs:      defaultReplicaLagThresholdMs, // 1 second
		HealthCheckInterval: defaultReplicaHealthInterval,
		FallbackToPrimary:   true,
	}
}

// ReplicaManager manages read replica connections
type ReplicaManager struct {
	primaryPool *pgxpool.Pool
	replicaPool *pgxpool.Pool
	config      *ReadReplicaConfig

	// Replica health tracking
	replicaHealthy atomic.Bool
	replicaLag     atomic.Int64

	mu             sync.RWMutex
	stopMonitoring chan struct{}
}

// NewReplicaManager creates a new replica manager
func NewReplicaManager(primaryPool *pgxpool.Pool, config *ReadReplicaConfig) (*ReplicaManager, error) {
	if config == nil {
		return nil, errors.New("replica config is required")
	}

	rm := &ReplicaManager{
		primaryPool:    primaryPool,
		config:         config,
		stopMonitoring: make(chan struct{}),
	}

	// Initialize replica pool
	if err := rm.initReplicaPool(); err != nil {
		return nil, fmt.Errorf("failed to initialize replica pool: %w", err)
	}

	// Start health monitoring
	go rm.monitorReplicaHealth()

	return rm, nil
}

// initReplicaPool initializes the replica connection pool
func (rm *ReplicaManager) initReplicaPool() error {
	poolConfig, err := pgxpool.ParseConfig(rm.config.ReplicaDSN)
	if err != nil {
		return fmt.Errorf("failed to parse replica DSN: %w", err)
	}

	// Configure pool for read workloads
	poolConfig.MaxConns = defaultReplicaMaxConns
	poolConfig.MinConns = defaultReplicaMinConns
	poolConfig.MaxConnLifetime = defaultReplicaMaxConnLifetime
	poolConfig.MaxConnIdleTime = defaultReplicaMaxConnIdleTime

	// Create pool
	pool, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
	if err != nil {
		return fmt.Errorf("failed to create replica pool: %w", err)
	}

	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), defaultReplicaPingTimeout)
	defer cancel()

	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return fmt.Errorf("failed to ping replica: %w", err)
	}

	rm.mu.Lock()
	rm.replicaPool = pool
	rm.mu.Unlock()
	rm.replicaHealthy.Store(true)

	return nil
}

// monitorReplicaHealth continuously monitors replica health and lag
func (rm *ReplicaManager) monitorReplicaHealth() {
	ticker := time.NewTicker(rm.config.HealthCheckInterval)
	defer ticker.Stop()

	for {
		select {
		case <-rm.stopMonitoring:
			return
		case <-ticker.C:
			rm.checkReplicaHealth()
		}
	}
}

// checkReplicaHealth checks replica health and replication lag
func (rm *ReplicaManager) checkReplicaHealth() {
	ctx, cancel := context.WithTimeout(context.Background(), defaultReplicaHealthTimeout)
	defer cancel()

	// Check basic connectivity
	pool := rm.getReplicaPool()
	if pool == nil {
		rm.replicaHealthy.Store(false)
		return
	}
	if err := pool.Ping(ctx); err != nil {
		rm.replicaHealthy.Store(false)
		return
	}

	// Check replication lag
	lag, err := rm.getReplicationLag(ctx)
	if err != nil {
		rm.replicaHealthy.Store(false)
		return
	}

	rm.replicaLag.Store(lag)

	// Mark unhealthy if lag exceeds threshold
	if lag > rm.config.LagThresholdMs {
		rm.replicaHealthy.Store(false)
	} else {
		rm.replicaHealthy.Store(true)
	}
}

// getReplicationLag returns replication lag in milliseconds
func (rm *ReplicaManager) getReplicationLag(ctx context.Context) (int64, error) {
	var lagMs int64

	// Query replication status
	query := `
		SELECT EXTRACT(MILLISECONDS FROM (NOW() - pg_last_xact_replay_timestamp()))::BIGINT
		FROM pg_stat_replication
		LIMIT 1
	`

	pool := rm.getReplicaPool()
	if pool == nil {
		return 0, errors.New("replica pool not initialized")
	}
	conn, err := pool.Acquire(ctx)
	if err != nil {
		return 0, err
	}
	defer conn.Release()

	err = conn.QueryRow(ctx, query).Scan(&lagMs)
	if err != nil {
		// If query fails, replica might not be in recovery mode
		// Try alternative query
		query = `SELECT 0`
		if err := conn.QueryRow(ctx, query).Scan(&lagMs); err != nil {
			return 0, err
		}
	}

	return lagMs, nil
}

// GetReadConnection returns a connection for read queries
func (rm *ReplicaManager) GetReadConnection(ctx context.Context) (*pgxpool.Conn, bool, error) {
	// Check if replica is healthy
	if rm.replicaHealthy.Load() {
		pool := rm.getReplicaPool()
		if pool == nil {
			return nil, false, errors.New("replica pool not initialized")
		}
		conn, err := pool.Acquire(ctx)
		if err == nil {
			return conn, true, nil // true = from replica
		}
		// If acquire fails, fall through to primary
	}

	// Fallback to primary if configured
	if rm.config.FallbackToPrimary {
		conn, err := rm.primaryPool.Acquire(ctx)
		if err != nil {
			return nil, false, fmt.Errorf("failed to acquire connection from primary: %w", err)
		}
		return conn, false, nil // false = from primary
	}

	return nil, false, errors.New("replica unavailable and fallback disabled")
}

// RouteQuery routes a query to replica or primary based on query type
func (rm *ReplicaManager) RouteQuery(ctx context.Context, query string, forceWrite bool) (*pgxpool.Conn, bool, error) {
	// Write queries always go to primary
	if forceWrite || isWriteQuery(query) {
		conn, err := rm.primaryPool.Acquire(ctx)
		return conn, false, err
	}

	// Read queries go to replica (with fallback)
	return rm.GetReadConnection(ctx)
}

// isWriteQuery determines if a query is a write operation
func isWriteQuery(query string) bool {
	// Simple heuristic - check for write keywords
	// In production, use a proper SQL parser
	writeKeywords := []string{
		"INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP",
		"TRUNCATE", "GRANT", "REVOKE",
	}

	queryUpper := query
	for _, keyword := range writeKeywords {
		if len(queryUpper) >= len(keyword) {
			prefix := queryUpper[:len(keyword)]
			if prefix == keyword {
				return true
			}
		}
	}

	return false
}

// GetReplicaLag returns current replication lag in milliseconds
func (rm *ReplicaManager) GetReplicaLag() int64 {
	return rm.replicaLag.Load()
}

// IsReplicaHealthy returns replica health status
func (rm *ReplicaManager) IsReplicaHealthy() bool {
	return rm.replicaHealthy.Load()
}

// GetReplicaStats returns replica statistics
func (rm *ReplicaManager) GetReplicaStats() map[string]interface{} {
	return map[string]interface{}{
		"healthy":          rm.IsReplicaHealthy(),
		"lag_ms":           rm.GetReplicaLag(),
		"threshold_ms":     rm.config.LagThresholdMs,
		"fallback_enabled": rm.config.FallbackToPrimary,
		"pool_stats":       GetPoolStats(rm.getReplicaPool()),
	}
}

// Close closes both primary and replica pools
func (rm *ReplicaManager) Close() {
	close(rm.stopMonitoring)

	pool := rm.getReplicaPool()
	if pool != nil {
		pool.Close()
	}
}

// SwitchToReplica temporarily forces all reads to replica (for testing)
func (rm *ReplicaManager) SwitchToReplica(force bool) {
	rm.replicaHealthy.Store(force)
}

// RefreshReplicaHealth forces an immediate health check
func (rm *ReplicaManager) RefreshReplicaHealth() {
	rm.checkReplicaHealth()
}

func (rm *ReplicaManager) getReplicaPool() *pgxpool.Pool {
	rm.mu.RLock()
	defer rm.mu.RUnlock()
	return rm.replicaPool
}
