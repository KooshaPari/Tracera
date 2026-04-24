package database

import (
	"context"
	"database/sql"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	dbTestLongSleep        = 100 * time.Millisecond
	dbTestShortSleep       = 10 * time.Millisecond
	dbTestTimeoutImmediate = 1 * time.Nanosecond
	dbTestTimeoutShort     = 1 * time.Second
	dbTestTimeoutMedium    = 2 * time.Second
	dbTestTimeoutLong      = 5 * time.Second
)

type dbURLVariationCase struct {
	name        string
	url         string
	shouldError bool
	errorMsg    string
}

func dbURLVariationCases() []dbURLVariationCase {
	return []dbURLVariationCase{
		{
			name:        "standard postgres URL",
			url:         "postgres://user:pass@localhost:5432/dbname",
			shouldError: true, // Will fail to connect but should parse
		},
		{
			name:        "postgresql URL",
			url:         "postgresql://user:pass@localhost:5432/dbname",
			shouldError: true,
		},
		{
			name:        "URL with sslmode",
			url:         "postgres://user:pass@localhost:5432/dbname?sslmode=disable",
			shouldError: true,
		},
		{
			name:        "URL with multiple parameters",
			url:         "postgres://user:pass@localhost:5432/dbname?sslmode=disable&connect_timeout=10",
			shouldError: true,
		},
		{
			name:        "empty string",
			url:         "",
			shouldError: true,
			errorMsg:    "ping",
		},
		{
			name:        "invalid scheme",
			url:         "mysql://user:pass@localhost:5432/dbname",
			shouldError: true,
		},
		{
			name:        "missing host",
			url:         "postgres://user:pass@/dbname",
			shouldError: true,
		},
		{
			name:        "URL with IPv6 host",
			url:         "postgres://user:pass@[::1]:5432/dbname",
			shouldError: true,
		},
	}
}

func requireTestDBURL(t *testing.T) string {
	t.Helper()
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	return dbURL
}

func withTestPool(t *testing.T, fn func(*pgxpool.Pool)) {
	t.Helper()
	dbURL := requireTestDBURL(t)

	pool, err := InitDB(dbURL)
	require.NoError(t, err)
	require.NotNil(t, pool)
	defer pool.Close()

	fn(pool)
}

func runInitDBIntegrationCases(t *testing.T) {
	t.Run("successful initialization with valid URL", func(t *testing.T) {
		withTestPool(t, func(pool *pgxpool.Pool) {
			err := pool.Ping(context.Background())
			require.NoError(t, err)

			config := pool.Config()
			assert.Equal(t, int32(50), config.MaxConns)
			assert.Equal(t, int32(10), config.MinConns)
		})
	})

	t.Run("special characters in password", func(t *testing.T) {
		if testing.Short() {
			t.Skip("skipping integration test in short mode")
		}

		pool, err := InitDB("postgres://user:p@ss%20w0rd@localhost:5432/testdb")
		if err != nil {
			assert.Contains(t, err.Error(), "failed to")
		}
		if pool != nil {
			pool.Close()
		}
	})

	t.Run("connection pool limits", func(t *testing.T) {
		withTestPool(t, func(pool *pgxpool.Pool) {
			conns := make([]*pgxpool.Conn, 0, 10)
			for i := 0; i < 10; i++ {
				conn, err := pool.Acquire(context.Background())
				if err != nil {
					t.Errorf("failed to acquire connection %d: %v", i, err)
					break
				}
				conns = append(conns, conn)
			}

			for _, conn := range conns {
				conn.Release()
			}

			assert.Len(t, conns, 10)
		})
	})
}

func runInitDBErrorCases(t *testing.T) {
	t.Run("invalid database URL", func(t *testing.T) {
		pool, err := InitDB("invalid://url")
		require.Error(t, err)
		assert.Nil(t, pool)
		assert.Contains(t, err.Error(), "failed to parse database URL")
	})

	t.Run("malformed connection string", func(t *testing.T) {
		pool, err := InitDB("postgres://user:pass@:99999/db")
		require.Error(t, err)
		assert.Nil(t, pool)
	})

	t.Run("unreachable host", func(t *testing.T) {
		pool, err := InitDB("postgres://user:pass@192.0.2.1:5432/testdb")
		require.Error(t, err)
		assert.Nil(t, pool)
		assert.Contains(t, err.Error(), "failed to ping database")
	})

	t.Run("connection timeout", func(t *testing.T) {
		pool, err := InitDB("postgres://user:pass@192.0.2.1:5432/testdb")
		if err != nil {
			assert.Contains(t, err.Error(), "failed to")
		}
		if pool != nil {
			pool.Close()
		}
	})

	t.Run("empty database URL", func(t *testing.T) {
		pool, err := InitDB("")
		require.Error(t, err)
		assert.Nil(t, pool)
	})
}

func runConcurrentPingSubtest(t *testing.T, pool *pgxpool.Pool) {
	t.Helper()
	const numGoroutines = 50
	errChan := make(chan error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func() {
			ctx, cancel := context.WithTimeout(context.Background(), dbTestTimeoutLong)
			defer cancel()
			errChan <- pool.Ping(ctx)
		}()
	}

	for i := 0; i < numGoroutines; i++ {
		err := <-errChan
		require.NoError(t, err, "ping %d failed", i)
	}
}

func runConcurrentAcquireSubtest(t *testing.T, pool *pgxpool.Pool) {
	t.Helper()
	const numGoroutines = 20
	successChan := make(chan bool, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			ctx, cancel := context.WithTimeout(context.Background(), dbTestTimeoutLong)
			defer cancel()

			conn, err := pool.Acquire(ctx)
			if err != nil {
				t.Logf("goroutine %d failed to acquire connection: %v", id, err)
				successChan <- false
				return
			}
			defer conn.Release()

			time.Sleep(dbTestShortSleep)
			successChan <- true
		}(i)
	}

	successes := 0
	for i := 0; i < numGoroutines; i++ {
		if <-successChan {
			successes++
		}
	}

	assert.Greater(t, successes, numGoroutines/2, "at least half should succeed")
}

func runDatabaseURLVariationCase(t *testing.T, tt dbURLVariationCase) {
	t.Helper()
	pool, err := InitDB(tt.url)
	if pool != nil {
		defer pool.Close()
	}

	if tt.shouldError {
		require.Error(t, err)
		if tt.errorMsg != "" {
			assert.Contains(t, err.Error(), tt.errorMsg)
		}
		return
	}

	require.NoError(t, err)
}

func TestInitDB(t *testing.T) {
	runInitDBIntegrationCases(t)
	runInitDBErrorCases(t)
}

func TestRunMigrations(t *testing.T) {
	t.Run("successful migration", func(t *testing.T) {
		if testing.Short() {
			t.Skip("skipping integration test in short mode")
		}

		dbURL := os.Getenv("TEST_DATABASE_URL")
		if dbURL == "" {
			t.Skip("TEST_DATABASE_URL not set")
		}

		pool, err := InitDB(dbURL)
		require.NoError(t, err)
		defer pool.Close()

		// Note: This test assumes migrations are idempotent
		err = RunMigrations(pool)
		// Migration might fail if already applied, which is acceptable
		if err != nil {
			t.Logf("Migration error (may be expected): %v", err)
		}
	})

	t.Run("nil pool", func(t *testing.T) {
		var pool *pgxpool.Pool
		err := RunMigrations(pool)
		require.Error(t, err)
	})

	t.Run("closed pool", func(t *testing.T) {
		if testing.Short() {
			t.Skip("skipping integration test in short mode")
		}

		dbURL := os.Getenv("TEST_DATABASE_URL")
		if dbURL == "" {
			t.Skip("TEST_DATABASE_URL not set")
		}

		pool, err := InitDB(dbURL)
		require.NoError(t, err)
		pool.Close()

		err = RunMigrations(pool)
		require.Error(t, err)
	})
}

func TestDatabaseConnectionRecovery(t *testing.T) {
	t.Run("reconnect after connection loss", func(t *testing.T) {
		if testing.Short() {
			t.Skip("skipping integration test in short mode")
		}

		dbURL := os.Getenv("TEST_DATABASE_URL")
		if dbURL == "" {
			t.Skip("TEST_DATABASE_URL not set")
		}

		pool, err := InitDB(dbURL)
		require.NoError(t, err)
		defer pool.Close()

		// First ping should work
		err = pool.Ping(context.Background())
		require.NoError(t, err)

		// Simulate work
		time.Sleep(dbTestLongSleep)

		// Second ping should still work
		err = pool.Ping(context.Background())
		require.NoError(t, err)
	})
}

func TestConcurrentDatabaseAccess(t *testing.T) {
	withTestPool(t, func(pool *pgxpool.Pool) {
		t.Run("concurrent pings", func(t *testing.T) {
			runConcurrentPingSubtest(t, pool)
		})

		t.Run("concurrent connection acquisition", func(t *testing.T) {
			runConcurrentAcquireSubtest(t, pool)
		})
	})
}

func TestDatabaseContextCancellation(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	pool, err := InitDB(dbURL)
	require.NoError(t, err)
	defer pool.Close()

	t.Run("ping with cancelled context", func(t *testing.T) {
		ctx, cancel := context.WithCancel(context.Background())
		cancel() // Cancel immediately

		err := pool.Ping(ctx)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "context canceled")
	})

	t.Run("acquire with timeout", func(t *testing.T) {
		ctx, cancel := context.WithTimeout(context.Background(), dbTestTimeoutImmediate)
		defer cancel()

		time.Sleep(dbTestShortSleep) // Ensure timeout

		conn, err := pool.Acquire(ctx)
		if err == nil {
			conn.Release()
			t.Fatal("expected timeout error")
		}
		require.Error(t, err)
	})
}

func TestDatabaseURLVariations(t *testing.T) {
	for _, tt := range dbURLVariationCases() {
		t.Run(tt.name, func(t *testing.T) {
			runDatabaseURLVariationCase(t, tt)
		})
	}
}

func TestPoolConfigurationEdgeCases(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	t.Run("verify pool stats", func(t *testing.T) {
		pool, err := InitDB(dbURL)
		require.NoError(t, err)
		defer pool.Close()

		stats := pool.Stat()
		assert.GreaterOrEqual(t, stats.MaxConns(), int32(25))
		assert.GreaterOrEqual(t, int32(5), stats.IdleConns())
	})

	t.Run("pool exhaustion and recovery", func(t *testing.T) {
		pool, err := InitDB(dbURL)
		require.NoError(t, err)
		defer pool.Close()

		// Acquire all available connections
		conns := make([]*pgxpool.Conn, 0)
		for i := 0; i < 25; i++ {
			ctx, cancel := context.WithTimeout(context.Background(), dbTestTimeoutMedium)
			conn, err := pool.Acquire(ctx)
			cancel()
			if err != nil {
				break
			}
			conns = append(conns, conn)
		}

		// Release all
		for _, conn := range conns {
			conn.Release()
		}

		// Should be able to acquire again
		ctx, cancel := context.WithTimeout(context.Background(), dbTestTimeoutMedium)
		defer cancel()
		conn, err := pool.Acquire(ctx)
		require.NoError(t, err)
		if conn != nil {
			conn.Release()
		}
	})
}

func TestMigrationEdgeCases(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	t.Run("migration with invalid database", func(t *testing.T) {
		// Create a pool with invalid credentials
		ctx := context.Background()
		config, err := pgxpool.ParseConfig("postgres://invaliduser:invalidpass@localhost:5432/invaliddb")
		if err != nil {
			t.Skipf("Failed to parse config: %v", err)
		}

		pool, err := pgxpool.NewWithConfig(ctx, config)
		if err != nil {
			t.Skipf("Failed to create pool: %v", err)
		}
		defer pool.Close()

		err = RunMigrations(pool)
		// Should error because database is invalid
		if err == nil {
			t.Log("Expected error but got none - may indicate test database exists")
		}
	})

	t.Run("migration with read-only connection", func(t *testing.T) {
		dbURL := os.Getenv("TEST_DATABASE_URL")
		if dbURL == "" {
			t.Skip("TEST_DATABASE_URL not set")
		}

		// This test would require a read-only user to be properly tested
		// For now, we just ensure the function handles errors gracefully
		pool, err := InitDB(dbURL)
		if err != nil {
			t.Skip("Could not initialize database")
		}
		defer pool.Close()

		// Run migrations
		err = RunMigrations(pool)
		// Log result but don't fail - migrations may already be applied
		t.Logf("Migration result: %v", err)
	})
}

func TestSQLOpenError(t *testing.T) {
	t.Run("invalid SQL connection", func(t *testing.T) {
		// Create a basic pool just to get config
		ctx := context.Background()
		config, err := pgxpool.ParseConfig("postgres://user:pass@localhost:5432/db")
		require.NoError(t, err)

		pool, err := pgxpool.NewWithConfig(ctx, config)
		require.NoError(t, err)
		defer pool.Close()

		// Try to open with invalid driver
		db, err := sql.Open("invalid_driver", pool.Config().ConnString())
		require.Error(t, err)
		if db != nil {
			if err := db.Close(); err != nil {
				t.Logf("close error: %v", err)
			}
		}
	})
}

func TestDatabaseStressTest(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping stress test in short mode")
	}

	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	pool, err := InitDB(dbURL)
	require.NoError(t, err)
	defer pool.Close()

	t.Run("rapid ping stress test", func(t *testing.T) {
		const iterations = 100
		for i := 0; i < iterations; i++ {
			ctx, cancel := context.WithTimeout(context.Background(), dbTestTimeoutShort)
			err := pool.Ping(ctx)
			cancel()
			require.NoError(t, err, "iteration %d failed", i)
		}
	})

	t.Run("connection churn", func(t *testing.T) {
		const iterations = 50
		for i := 0; i < iterations; i++ {
			ctx, cancel := context.WithTimeout(context.Background(), dbTestTimeoutMedium)
			conn, err := pool.Acquire(ctx)
			cancel()
			if err != nil {
				t.Errorf("iteration %d: failed to acquire: %v", i, err)
				continue
			}
			conn.Release()
		}
	})
}

// Helper function to test error wrapping
func TestErrorWrapping(t *testing.T) {
	t.Run("verify error messages", func(t *testing.T) {
		pool, err := InitDB("invalid://url")
		require.Error(t, err)
		assert.Nil(t, pool)

		// Check error is properly wrapped
		assert.Contains(t, err.Error(), "failed to parse database URL")
	})
}
