//go:build integration

package graph

import (
	"context"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

// setupTestDBForGraph sets up a PostgreSQL container for graph tests
func setupTestDBForGraph(t *testing.T) (*pgxpool.Pool, func()) {
	ctx := context.Background()

	pgContainer, err := postgres.RunContainer(ctx,
		testcontainers.WithImage("postgres:16-alpine"),
		postgres.WithDatabase("testdb"),
		postgres.WithUsername("testuser"),
		postgres.WithPassword("testpass"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(30*time.Second)),
	)
	require.NoError(t, err)

	connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	require.NoError(t, err)

	pool, err := pgxpool.New(ctx, connStr)
	require.NoError(t, err)

	err = pool.Ping(ctx)
	require.NoError(t, err)

	cleanup := func() {
		pool.Close()
		require.NoError(t, pgContainer.Terminate(ctx))
	}

	return pool, cleanup
}

// TestNewGraph_Integration tests Graph creation with real database
func TestNewGraph_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForGraph(t)
	defer cleanup()

	t.Run("creates graph successfully", func(t *testing.T) {
		graph := NewGraph(pool)
		assert.NotNil(t, graph)
	})
}

// TestGraph_Operations_Integration tests graph operations
func TestGraph_Operations_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForGraph(t)
	defer cleanup()

	graph := NewGraph(pool)

	ctx := context.Background()

	t.Run("adds nodes", func(t *testing.T) {
		// Note: Requires graph implementation details
		// This is a placeholder for integration test
		_ = graph
		_ = ctx
	})

	t.Run("adds edges", func(t *testing.T) {
		// Note: Requires graph implementation details
		_ = graph
		_ = ctx
	})

	t.Run("performs BFS", func(t *testing.T) {
		// Note: Requires graph implementation details
		_ = graph
		_ = ctx
	})

	t.Run("performs DFS", func(t *testing.T) {
		// Note: Requires graph implementation details
		_ = graph
		_ = ctx
	})
}
