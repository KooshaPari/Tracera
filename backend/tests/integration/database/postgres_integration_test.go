//go:build integration

package database_test

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var (
	testPool     *pgxpool.Pool
	testDBURL    = "postgresql://postgres:postgres@localhost:5432/tracertm_test?sslmode=disable"
	setupOnce    sync.Once
	teardownOnce sync.Once
)

func setupTestDB(t *testing.T) *pgxpool.Pool {
	setupOnce.Do(func() {
		ctx := context.Background()
		config, err := pgxpool.ParseConfig(testDBURL)
		require.NoError(t, err)

		// Configure connection pool for testing
		config.MaxConns = 10
		config.MinConns = 2

		pool, err := pgxpool.NewWithConfig(ctx, config)
		require.NoError(t, err)

		err = pool.Ping(ctx)
		require.NoError(t, err)

		// Create test schema
		_, err = pool.Exec(ctx, `
			CREATE TABLE IF NOT EXISTS test_items (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				title TEXT NOT NULL,
				content TEXT,
				version INTEGER DEFAULT 1,
				created_at TIMESTAMP DEFAULT NOW(),
				updated_at TIMESTAMP DEFAULT NOW()
			);

			CREATE INDEX IF NOT EXISTS idx_test_items_title ON test_items(title);
			CREATE INDEX IF NOT EXISTS idx_test_items_created_at ON test_items(created_at);
		`)
		require.NoError(t, err)

		testPool = pool
		t.Logf("✅ Test database initialized successfully")
	})

	return testPool
}

func teardownTestDB(t *testing.T) {
	teardownOnce.Do(func() {
		if testPool != nil {
			ctx := context.Background()
			_, err := testPool.Exec(ctx, "DROP TABLE IF EXISTS test_items CASCADE")
			if err != nil {
				t.Logf("⚠️ Warning: Failed to drop test tables: %v", err)
			}
			_ = testPool.Close()
			t.Logf("✅ Test database cleaned up")
		}
	})
}

// TestPostgres_ConnectionPool_Healthy verifies connection pool health and configuration
func TestPostgres_ConnectionPool_Healthy(t *testing.T) {
	pool := setupTestDB(t)
	defer teardownTestDB(t)

	ctx := context.Background()

	// Test basic connectivity
	err := pool.Ping(ctx)
	assert.NoError(t, err, "Pool should be pingable")

	// Verify pool stats
	stats := pool.Stat()
	assert.GreaterOrEqual(t, stats.MaxConns(), int32(2), "Max connections should be configured")
	assert.GreaterOrEqual(t, stats.TotalConns(), int32(1), "Should have at least one connection")

	// Test connection acquisition
	conn, err := pool.Acquire(ctx)
	require.NoError(t, err)
	assert.NotNil(t, conn)
	conn.Release()

	// Test multiple concurrent acquisitions
	var wg sync.WaitGroup
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			conn, err := pool.Acquire(ctx)
			if err != nil {
				t.Errorf("Failed to acquire connection: %v", err)
				return
			}
			defer conn.Release()

			var result int
			err = conn.QueryRow(ctx, "SELECT 1").Scan(&result)
			assert.NoError(t, err)
			assert.Equal(t, 1, result)
		}()
	}
	wg.Wait()
}

// TestPostgres_Transactions_CommitRollback tests transaction behavior
func TestPostgres_Transactions_CommitRollback(t *testing.T) {
	pool := setupTestDB(t)
	defer teardownTestDB(t)

	ctx := context.Background()

	t.Run("Commit_Transaction", func(t *testing.T) {
		tx, err := pool.Begin(ctx)
		require.NoError(t, err)
		defer tx.Rollback(ctx) // Safe to call even after commit

		// Insert test data
		itemID := uuid.New()
		_, err = tx.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID, "Transaction Test", "Commit test content")
		require.NoError(t, err)

		// Commit transaction
		err = tx.Commit(ctx)
		require.NoError(t, err)

		// Verify data persisted
		var title string
		err = pool.QueryRow(ctx, "SELECT title FROM test_items WHERE id = $1", itemID).Scan(&title)
		require.NoError(t, err)
		assert.Equal(t, "Transaction Test", title)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID)
	})

	t.Run("Rollback_Transaction", func(t *testing.T) {
		tx, err := pool.Begin(ctx)
		require.NoError(t, err)

		// Insert test data
		itemID := uuid.New()
		_, err = tx.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID, "Rollback Test", "Rollback test content")
		require.NoError(t, err)

		// Rollback transaction
		err = tx.Rollback(ctx)
		require.NoError(t, err)

		// Verify data not persisted
		var title string
		err = pool.QueryRow(ctx, "SELECT title FROM test_items WHERE id = $1", itemID).Scan(&title)
		assert.Error(t, err)
		assert.Equal(t, pgx.ErrNoRows, err)
	})

	t.Run("Nested_SavePoint", func(t *testing.T) {
		tx, err := pool.Begin(ctx)
		require.NoError(t, err)
		defer tx.Rollback(ctx)

		// Insert first item
		itemID1 := uuid.New()
		_, err = tx.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID1, "Item 1", "Content 1")
		require.NoError(t, err)

		// Create savepoint
		_, err = tx.Exec(ctx, "SAVEPOINT sp1")
		require.NoError(t, err)

		// Insert second item
		itemID2 := uuid.New()
		_, err = tx.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID2, "Item 2", "Content 2")
		require.NoError(t, err)

		// Rollback to savepoint
		_, err = tx.Exec(ctx, "ROLLBACK TO SAVEPOINT sp1")
		require.NoError(t, err)

		// Commit transaction
		err = tx.Commit(ctx)
		require.NoError(t, err)

		// Verify first item exists
		var title1 string
		err = pool.QueryRow(ctx, "SELECT title FROM test_items WHERE id = $1", itemID1).Scan(&title1)
		require.NoError(t, err)
		assert.Equal(t, "Item 1", title1)

		// Verify second item doesn't exist
		var title2 string
		err = pool.QueryRow(ctx, "SELECT title FROM test_items WHERE id = $1", itemID2).Scan(&title2)
		assert.Error(t, err)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID1)
	})
}

// TestPostgres_ConcurrentAccess_NoDeadlock tests concurrent access patterns
func TestPostgres_ConcurrentAccess_NoDeadlock(t *testing.T) {
	pool := setupTestDB(t)
	defer teardownTestDB(t)

	ctx := context.Background()

	// Create test items
	itemIDs := make([]uuid.UUID, 10)
	for i := 0; i < 10; i++ {
		itemID := uuid.New()
		itemIDs[i] = itemID
		_, err := pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content, version)
			VALUES ($1, $2, $3, $4)
		`, itemID, fmt.Sprintf("Item %d", i), fmt.Sprintf("Content %d", i), 1)
		require.NoError(t, err)
	}

	// Concurrent reads and writes
	var wg sync.WaitGroup
	errors := make(chan error, 50)

	// 25 concurrent readers
	for i := 0; i < 25; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			itemID := itemIDs[idx%10]

			var title string
			err := pool.QueryRow(ctx, "SELECT title FROM test_items WHERE id = $1", itemID).Scan(&title)
			if err != nil {
				errors <- fmt.Errorf("read error: %w", err)
			}
		}(i)
	}

	// 25 concurrent writers
	for i := 0; i < 25; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			itemID := itemIDs[idx%10]

			_, err := pool.Exec(ctx, `
				UPDATE test_items
				SET version = version + 1, updated_at = NOW()
				WHERE id = $1
			`, itemID)
			if err != nil {
				errors <- fmt.Errorf("write error: %w", err)
			}
		}(i)
	}

	wg.Wait()
	close(errors)

	// Check for errors
	for err := range errors {
		t.Errorf("Concurrent access error: %v", err)
	}

	// Cleanup
	_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = ANY($1)", itemIDs)
}

// TestPostgres_CRUD_Operations tests basic CRUD operations
func TestPostgres_CRUD_Operations(t *testing.T) {
	pool := setupTestDB(t)
	defer teardownTestDB(t)

	ctx := context.Background()

	t.Run("Create", func(t *testing.T) {
		itemID := uuid.New()
		var createdID uuid.UUID

		err := pool.QueryRow(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
			RETURNING id
		`, itemID, "Created Item", "Created content").Scan(&createdID)

		require.NoError(t, err)
		assert.Equal(t, itemID, createdID)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID)
	})

	t.Run("Read", func(t *testing.T) {
		// Insert test data
		itemID := uuid.New()
		_, err := pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID, "Read Item", "Read content")
		require.NoError(t, err)

		// Read data
		var title, content string
		err = pool.QueryRow(ctx, `
			SELECT title, content FROM test_items WHERE id = $1
		`, itemID).Scan(&title, &content)

		require.NoError(t, err)
		assert.Equal(t, "Read Item", title)
		assert.Equal(t, "Read content", content)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID)
	})

	t.Run("Update", func(t *testing.T) {
		// Insert test data
		itemID := uuid.New()
		_, err := pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content, version)
			VALUES ($1, $2, $3, $4)
		`, itemID, "Original Title", "Original content", 1)
		require.NoError(t, err)

		// Update data
		result, err := pool.Exec(ctx, `
			UPDATE test_items
			SET title = $2, content = $3, version = version + 1
			WHERE id = $1
		`, itemID, "Updated Title", "Updated content")
		require.NoError(t, err)
		assert.Equal(t, int64(1), result.RowsAffected())

		// Verify update
		var title, content string
		var version int
		err = pool.QueryRow(ctx, `
			SELECT title, content, version FROM test_items WHERE id = $1
		`, itemID).Scan(&title, &content, &version)
		require.NoError(t, err)
		assert.Equal(t, "Updated Title", title)
		assert.Equal(t, "Updated content", content)
		assert.Equal(t, 2, version)

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID)
	})

	t.Run("Delete", func(t *testing.T) {
		// Insert test data
		itemID := uuid.New()
		_, err := pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID, "Delete Item", "Delete content")
		require.NoError(t, err)

		// Delete data
		result, err := pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID)
		require.NoError(t, err)
		assert.Equal(t, int64(1), result.RowsAffected())

		// Verify deletion
		var title string
		err = pool.QueryRow(ctx, "SELECT title FROM test_items WHERE id = $1", itemID).Scan(&title)
		assert.Error(t, err)
		assert.Equal(t, pgx.ErrNoRows, err)
	})
}

// TestPostgres_ConstraintViolations tests constraint enforcement
func TestPostgres_ConstraintViolations(t *testing.T) {
	pool := setupTestDB(t)
	defer teardownTestDB(t)

	ctx := context.Background()

	t.Run("PrimaryKey_Duplicate", func(t *testing.T) {
		itemID := uuid.New()

		// Insert first item
		_, err := pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID, "Item 1", "Content 1")
		require.NoError(t, err)

		// Try to insert duplicate ID
		_, err = pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID, "Item 2", "Content 2")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "duplicate key")

		// Cleanup
		_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID)
	})

	t.Run("NotNull_Violation", func(t *testing.T) {
		itemID := uuid.New()

		// Try to insert with null title
		_, err := pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, NULL, $2)
		`, itemID, "Content")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "null value")
	})
}

// TestPostgres_IndexPerformance benchmarks index performance
func TestPostgres_IndexPerformance(t *testing.T) {
	pool := setupTestDB(t)
	defer teardownTestDB(t)

	ctx := context.Background()

	// Insert test data
	numItems := 1000
	itemIDs := make([]uuid.UUID, numItems)

	startInsert := time.Now()
	for i := 0; i < numItems; i++ {
		itemID := uuid.New()
		itemIDs[i] = itemID
		_, err := pool.Exec(ctx, `
			INSERT INTO test_items (id, title, content)
			VALUES ($1, $2, $3)
		`, itemID, fmt.Sprintf("Item %d", i), fmt.Sprintf("Content %d", i))
		require.NoError(t, err)
	}
	insertDuration := time.Since(startInsert)
	t.Logf("Inserted %d items in %v (%.2f items/sec)", numItems, insertDuration, float64(numItems)/insertDuration.Seconds())

	// Test indexed query performance
	startQuery := time.Now()
	for i := 0; i < 100; i++ {
		title := fmt.Sprintf("Item %d", i)
		var id uuid.UUID
		err := pool.QueryRow(ctx, "SELECT id FROM test_items WHERE title = $1", title).Scan(&id)
		require.NoError(t, err)
	}
	queryDuration := time.Since(startQuery)
	t.Logf("Executed 100 indexed queries in %v (%.2f queries/sec)", queryDuration, 100.0/queryDuration.Seconds())

	// Each query should be fast with index
	avgQueryTime := queryDuration / 100
	assert.Less(t, avgQueryTime, 10*time.Millisecond, "Average query time should be under 10ms with index")

	// Cleanup
	_, _ = pool.Exec(ctx, "DELETE FROM test_items WHERE id = ANY($1)", itemIDs)
}
