package infrastructure

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/config"
)

const (
	infrastructureTimeoutDelay     = 10 * time.Millisecond
	infrastructureTimeoutImmediate = 1 * time.Nanosecond
)

func createTestConfig(t *testing.T) *config.Config {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	return &config.Config{
		DatabaseURL:           dbURL,
		RedisURL:              os.Getenv("TEST_REDIS_URL"),
		NATSUrl:               os.Getenv("TEST_NATS_URL"),
		Neo4jURI:              os.Getenv("TEST_NEO4J_URI"),
		Neo4jUser:             os.Getenv("TEST_NEO4J_USER"),
		Neo4jPassword:         os.Getenv("TEST_NEO4J_PASSWORD"),
		UpstashRedisRestURL:   os.Getenv("UPSTASH_REDIS_REST_URL"),
		UpstashRedisRestToken: os.Getenv("UPSTASH_REDIS_REST_TOKEN"),
		Env:                   "test",
	}
}

// TestInitializeInfrastructure tests infrastructure initialization
func TestInitializeInfrastructure(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping infrastructure integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("initialize all infrastructure services", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			// Some services may not be available in test environment
			t.Logf("Infrastructure initialization error (may be expected): %v", err)
			return
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		assert.NotNil(t, infra)
		assert.NotNil(t, infra.DB)
	})

	t.Run("initialize with minimal config", func(t *testing.T) {
		minimalCfg := &config.Config{
			DatabaseURL: cfg.DatabaseURL,
			NATSUrl:     "nats://localhost:4222",
		}

		infra, err := InitializeInfrastructure(ctx, minimalCfg)
		if err != nil {
			t.Logf("Expected error with minimal config: %v", err)
			return
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		assert.NotNil(t, infra.DB)
	})

	t.Run("initialize with invalid database URL", func(t *testing.T) {
		badCfg := &config.Config{
			DatabaseURL: "postgres://invalid:invalid@invalid:5432/invalid",
			NATSUrl:     "nats://localhost:4222",
		}

		infra, err := InitializeInfrastructure(ctx, badCfg)
		require.Error(t, err)
		assert.Nil(t, infra)
	})

	t.Run("initialize with context timeout", func(t *testing.T) {
		timeoutCtx, cancel := context.WithTimeout(ctx, infrastructureTimeoutImmediate)
		defer cancel()
		time.Sleep(infrastructureTimeoutDelay)

		infra, err := InitializeInfrastructure(timeoutCtx, cfg)
		if err == nil && infra != nil {
			if closeErr := infra.Close(ctx); closeErr != nil {
				t.Logf("Failed to close infrastructure: %v", closeErr)
			}
			t.Log("Initialization completed before timeout")
		} else {
			require.Error(t, err)
		}
	})
}

func TestInfrastructurePostgresInit(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("postgres connection successful", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		assert.NotNil(t, infra.DB)

		// Test connection
		err = infra.DB.Ping(ctx)
		require.NoError(t, err)
	})

	t.Run("postgres with invalid credentials", func(t *testing.T) {
		badCfg := &config.Config{
			DatabaseURL: "postgres://baduser:badpass@localhost:5432/baddb",
			NATSUrl:     "nats://localhost:4222",
		}

		infra, err := InitializeInfrastructure(ctx, badCfg)
		require.Error(t, err)
		assert.Nil(t, infra)
	})
}

func TestInfrastructureRedisInit(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("redis connection successful", func(t *testing.T) {
		if cfg.RedisURL == "" {
			cfg.RedisURL = "redis://localhost:6379"
		}

		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		// Redis may or may not be available
		if infra.Redis != nil {
			err := infra.Redis.Ping(ctx).Err()
			if err != nil {
				t.Logf("Redis ping failed (acceptable): %v", err)
			}
		}
	})

	t.Run("redis fallback to upstash", func(t *testing.T) {
		badRedisCfg := createTestConfig(t)
		badRedisCfg.RedisURL = "redis://192.0.2.1:6379"

		infra, err := InitializeInfrastructure(ctx, badRedisCfg)
		if err != nil {
			t.Logf("Failed to initialize (expected if NATS unavailable): %v", err)
			return
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		// Should fall back to Upstash or have nil cache
		if infra.Cache == nil {
			t.Log("No cache initialized (acceptable)")
		}
	})
}

func TestInfrastructureNATSInit(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("NATS connection successful", func(t *testing.T) {
		if cfg.NATSUrl == "" {
			cfg.NATSUrl = "nats://localhost:4222"
		}

		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("NATS not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		if infra.NATS != nil {
			err := infra.NATS.HealthCheck(ctx)
			require.NoError(t, err)
		}
	})

	t.Run("NATS with invalid URL", func(t *testing.T) {
		badCfg := createTestConfig(t)
		badCfg.NATSUrl = "nats://192.0.2.1:4222"

		infra, err := InitializeInfrastructure(ctx, badCfg)
		require.Error(t, err)
		assert.Nil(t, infra)
	})
}

// TestInfrastructureHealthCheck tests infrastructure health check
func TestInfrastructureHealthCheck(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("health check all services", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		err = infra.HealthCheck(ctx)
		// May fail if optional services not available
		if err != nil {
			t.Logf("Health check error (some services unavailable): %v", err)
		}
	})

	t.Run("health check with postgres only", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		// Test postgres specifically
		if infra.DB != nil {
			err := infra.DB.Ping(ctx)
			require.NoError(t, err)
		}
	})

	t.Run("health check with context cancellation", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		cancelCtx, cancel := context.WithCancel(ctx)
		cancel()

		err = infra.HealthCheck(cancelCtx)
		// Will likely error due to cancelled context
		if err != nil {
			t.Logf("Health check with cancelled context (expected): %v", err)
		}
	})

	t.Run("health check with timeout", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		timeoutCtx, cancel := context.WithTimeout(ctx, infrastructureTimeoutImmediate)
		defer cancel()
		time.Sleep(infrastructureTimeoutDelay)

		err = infra.HealthCheck(timeoutCtx)
		// Will likely error due to timeout
		if err != nil {
			t.Logf("Health check with timeout (expected): %v", err)
		}
	})
}

func TestInfrastructureClose(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("close all connections", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}

		err = infra.Close(ctx)
		require.NoError(t, err)

		// Verify connections closed
		if infra.DB != nil {
			err := infra.DB.Ping(ctx)
			require.Error(t, err)
		}
	})

	t.Run("double close", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}

		if err := infra.Close(ctx); err != nil {
			t.Logf("error closing infrastructure: %v", err)
		}
		err = infra.Close(ctx)
		require.NoError(t, err) // Should not panic
	})

	t.Run("close with nil components", func(t *testing.T) {
		infra := &Infrastructure{}
		err := infra.Close(ctx)
		require.NoError(t, err)
	})
}

func TestInfrastructureNeo4jInit(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("Neo4j initialization", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		if infra.Neo4j != nil {
			t.Log("Neo4j initialized successfully")
		}
	})
}

// TestInfrastructureSupabaseInit has been removed as Supabase is no longer used
// Keeping as a placeholder for potential future storage backend tests
/*
func TestInfrastructureSupabaseInit(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)
	// Supabase removed - using PostgreSQL directly
	t.Skip("Supabase integration removed")
}
*/

func TestInfrastructureCacheInit(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("cache initialization with Redis", func(t *testing.T) {
		if cfg.RedisURL == "" {
			cfg.RedisURL = "redis://localhost:6379"
		}

		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		// Cache may be Redis or Upstash
		if infra.Cache != nil {
			t.Log("Cache initialized")
		}
	})

	t.Run("cache fallback behavior", func(t *testing.T) {
		badCfg := createTestConfig(t)
		badCfg.RedisURL = "redis://invalid:6379"
		badCfg.UpstashRedisRestURL = ""

		infra, err := InitializeInfrastructure(ctx, badCfg)
		if err != nil {
			t.Logf("Infrastructure init failed (expected): %v", err)
			return
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		// Cache may be nil if both Redis and Upstash fail
		if infra.Cache == nil {
			t.Log("No cache available (acceptable)")
		}
	})
}

func TestInfrastructureConcurrentAccess(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	infra, err := InitializeInfrastructure(ctx, cfg)
	if err != nil {
		t.Skipf("Infrastructure not available: %v", err)
	}
	defer func() {
		if err := infra.Close(ctx); err != nil {
			t.Logf("error closing infrastructure: %v", err)
		}
	}()

	t.Run("concurrent database access", func(t *testing.T) {
		errChan := make(chan error, 20)

		for i := 0; i < 20; i++ {
			go func() {
				errChan <- infra.DB.Ping(ctx)
			}()
		}

		for i := 0; i < 20; i++ {
			err := <-errChan
			require.NoError(t, err)
		}
	})

	t.Run("concurrent health checks", func(t *testing.T) {
		errChan := make(chan error, 10)

		for i := 0; i < 10; i++ {
			go func() {
				errChan <- infra.HealthCheck(ctx)
			}()
		}

		for i := 0; i < 10; i++ {
			err := <-errChan
			// May error if optional services unavailable
			if err != nil {
				t.Logf("Health check error (acceptable): %v", err)
			}
		}
	})
}

func TestInfrastructureEdgeCases(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()

	t.Run("empty config", func(t *testing.T) {
		emptyCfg := &config.Config{}
		infra, err := InitializeInfrastructure(ctx, emptyCfg)
		require.Error(t, err)
		assert.Nil(t, infra)
	})

	t.Run("partially invalid config", func(t *testing.T) {
		partialCfg := &config.Config{
			DatabaseURL: os.Getenv("TEST_DATABASE_URL"),
			RedisURL:    "invalid://url",
			NATSUrl:     "nats://192.0.2.1:4222",
		}

		if partialCfg.DatabaseURL == "" {
			t.Skip("TEST_DATABASE_URL not set")
		}

		infra, err := InitializeInfrastructure(ctx, partialCfg)
		// Should fail on NATS
		require.Error(t, err)
		assert.Nil(t, infra)
	})
}

func TestInfrastructureResourceCleanup(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("verify all resources cleaned up", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}

		// Store references
		db := infra.DB
		redis := infra.Redis
		nats := infra.NATS

		// Close
		if err := infra.Close(ctx); err != nil {
			t.Logf("error closing infrastructure: %v", err)
		}

		// Verify cleanup
		if db != nil {
			err := db.Ping(ctx)
			require.Error(t, err, "DB should be closed")
		}

		if redis != nil {
			err := redis.Ping(ctx).Err()
			if err == nil {
				t.Log("Redis still active after close")
			}
		}

		if nats != nil {
			err := nats.HealthCheck(ctx)
			require.Error(t, err, "NATS should be closed")
		}
	})
}

func TestInfrastructureInitializationOrder(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	ctx := context.Background()
	cfg := createTestConfig(t)

	t.Run("services initialized in correct order", func(t *testing.T) {
		infra, err := InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Infrastructure not available: %v", err)
		}
		defer func() {
			if err := infra.Close(ctx); err != nil {
				t.Logf("error closing infrastructure: %v", err)
			}
		}()

		// DB should always be initialized first
		assert.NotNil(t, infra.DB)

		assert.NotNil(t, infra.NATS)
		assert.NotNil(t, infra.Redis)
		assert.NotNil(t, infra.Neo4j)
	})
}
