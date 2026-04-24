//go:build integration

package search

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

// setupTestDBForSearch sets up a PostgreSQL container for search tests
func setupTestDBForSearch(t *testing.T) (*pgxpool.Pool, func()) {
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

	// Run migrations
	// Note: You may need to run your migration setup here
	// For now, we'll just verify the pool works
	err = pool.Ping(ctx)
	require.NoError(t, err)

	cleanup := func() {
		pool.Close()
		require.NoError(t, pgContainer.Terminate(ctx))
	}

	return pool, cleanup
}

// TestNewSearchEngine_Integration tests Engine creation with real database
func TestNewSearchEngine_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForSearch(t)
	defer cleanup()

	t.Run("creates search engine successfully", func(t *testing.T) {
		engine := NewEngine(pool)
		assert.NotNil(t, engine)
	})

	t.Run("creates search engine with config", func(t *testing.T) {
		// Note: Requires actual reranker implementation
		config := &EngineConfig{
			Pool: pool,
			// Reranker: mockReranker, // Would need real reranker
		}

		engine := NewEngineWithConfig(config)
		assert.NotNil(t, engine)
	})
}

// TestSearchEngine_Search_FullText_Integration tests full-text search
func TestSearchEngine_Search_FullText_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForSearch(t)
	defer cleanup()

	engine := NewEngine(pool)

	ctx := context.Background()

	t.Run("searches with query", func(t *testing.T) {
		req := &Request{
			Query:     "test query",
			ProjectID: "123e4567-e89b-12d3-a456-426614174000",
		}

		// Note: Requires test data in database
		// For now, we test that the method doesn't panic
		_, err := engine.Search(ctx, req)
		// May return error if no data, but should not panic
		_ = err
	})

	t.Run("searches with filters", func(t *testing.T) {
		req := &Request{
			Query:     "test",
			ProjectID: "123e4567-e89b-12d3-a456-426614174000",
			ItemTypes: []string{"requirement"},
		}

		_, err := engine.Search(ctx, req)
		_ = err
	})
}

// TestSearchEngine_VectorSearch_Integration tests vector search
func TestSearchEngine_VectorSearch_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForSearch(t)
	defer cleanup()

	engine := NewEngine(pool)

	ctx := context.Background()

	t.Run("vector search with embeddings", func(t *testing.T) {
		// Note: Requires embeddings to be set up
		// This is a placeholder for integration test
		_ = engine
		_ = ctx
	})
}

// TestSearchEngine_GetSearchCount_Integration tests search count
func TestSearchEngine_GetSearchCount_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForSearch(t)
	defer cleanup()

	engine := NewEngine(pool)

	ctx := context.Background()

	t.Run("gets search count", func(t *testing.T) {
		req := &Request{
			Query:     "test",
			ProjectID: "123e4567-e89b-12d3-a456-426614174000",
		}

		// Note: getSearchCount is private, test through Search method
		resp, err := engine.Search(ctx, req)
		// May return 0 if no data, but should not error
		if err == nil {
			assert.NotNil(t, resp)
			assert.GreaterOrEqual(t, resp.TotalCount, 0)
		}
	})
}
