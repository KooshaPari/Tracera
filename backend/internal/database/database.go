package database

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kooshapari/tracertm-backend/internal/db"
	_ "github.com/lib/pq" // PostgreSQL driver
)

// InitDB initializes the database connection using pgxpool
func InitDB(databaseURL string) (*pgxpool.Pool, error) {
	// Use default optimized pool configuration
	poolConfig := DefaultPoolConfig()
	return InitPoolWithConfig(databaseURL, poolConfig)
}

// InitDBWithOptimizations initializes database with full optimizations
func InitDBWithOptimizations(databaseURL string, config *PoolConfig) (*pgxpool.Pool, error) {
	// Create pool with custom configuration
	pool, err := InitPoolWithConfig(databaseURL, config)
	if err != nil {
		return nil, err
	}

	// Apply optimizations
	ctx := context.Background()
	if err := ApplyOptimizations(ctx, pool, DefaultOptimizationConfig()); err != nil {
		// Log warning but don't fail
		fmt.Printf("Warning: Failed to apply some optimizations: %v\n", err)
	}

	// Warmup pool
	if err := WarmupPool(ctx, pool, int(config.MinConnections)); err != nil {
		fmt.Printf("Warning: Failed to warmup pool: %v\n", err)
	}

	return pool, nil
}

// RunMigrations runs SQL migrations from the migrations directory
func RunMigrations(pool *pgxpool.Pool) error {
	// Check for nil pool
	if pool == nil {
		return errors.New("database pool is nil")
	}

	// Test connection first
	ctx := context.Background()
	if err := pool.Ping(ctx); err != nil {
		return fmt.Errorf("failed to ping database - ensure PostgreSQL is running and DATABASE_URL is correct: %w", err)
	}

	// Get database URL from pool config
	dbURL := pool.Config().ConnString()

	// Open a standard sql.DB connection
	sqlDB, err := sql.Open("postgres", dbURL)
	if err != nil {
		return fmt.Errorf("failed to open database connection: %w", err)
	}
	defer func() {
		if closeErr := sqlDB.Close(); closeErr != nil {
			log.Printf("⚠️  Warning: failed to close sql.DB: %v", closeErr)
		}
	}()

	// Test the sql.DB connection
	if err := sqlDB.PingContext(ctx); err != nil {
		return fmt.Errorf("failed to ping database via sql.DB: %w", err)
	}

	// Run migrations using the Atlas-based migration system
	if err := db.RunMigrations(ctx, sqlDB); err != nil {
		return fmt.Errorf("failed to run migrations: %w", err)
	}

	return nil
}
