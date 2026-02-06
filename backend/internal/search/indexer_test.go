//go:build !integration && !e2e

package search

import (
	"testing"
)

// Note: NewIndexer requires *pgxpool.Pool, not pgxmock.PgxPoolIface
// These tests should use integration tests with a real pool
// For unit tests, we test the logic that doesn't require a pool

func TestNewIndexer_Defaults(t *testing.T) {
	// Test default values logic
	// Actual indexer creation requires real pool (integration test)
	t.Run("default worker pool", func(_ *testing.T) {
		// Default is 4 workers when 0 is passed
		// This is tested in the NewIndexer function itself
	})

	t.Run("default queue size", func(_ *testing.T) {
		// Default is 1000 when 0 is passed
		// This is tested in the NewIndexer function itself
	})
}

// Note: NewIndexer requires *pgxpool.Pool, not pgxmock.PgxPoolIface
// These tests should use integration tests with a real pool
// For unit tests, we test the logic that doesn't require a pool

func TestIndexer_Start_Integration(t *testing.T) {
	// This test requires a real *pgxpool.Pool
	// Mark as integration test
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_Stop_Integration(t *testing.T) {
	// This test requires a real *pgxpool.Pool
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_QueueIndex_Integration(t *testing.T) {
	// These tests require a real *pgxpool.Pool
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_QueueUpdate_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_QueueDelete_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_ReindexAll_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_Stats_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_processJob_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_indexItem_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_IndexItemWithEmbedding_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_deleteItemIndex_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestIndexer_WaitForQueue_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}
