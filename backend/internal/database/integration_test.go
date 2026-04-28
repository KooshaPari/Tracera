//go:build integration

package database_test

import (
	"context"
	"fmt"
	"testing"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/database"
	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/testutil"
)

// TestInitDB_WithContainer tests InitDB with a real PostgreSQL container
func TestInitDB_WithContainer(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
	pc, err := testutil.StartPostgresContainer(ctx)
	require.NoError(t, err)
	defer func() {
		err := pc.Close(ctx)
		require.NoError(t, err)
	}()

	// Test InitDB with container connection string
	pool, err := database.InitDB(pc.GetConnectionString())
	require.NoError(t, err)
	defer pool.Close()

	// Verify pool is healthy
	err = pool.Ping(ctx)
	assert.NoError(t, err)

	stats := pool.Stat()
	assert.Greater(t, stats.TotalConns(), int32(0))
	t.Logf("✅ InitDB created healthy pool: %d connections", stats.TotalConns())
}

// TestMigrations_WithContainer tests running migrations on a real database
func TestMigrations_WithContainer(t *testing.T) {
	ctx := context.Background()

	// Start PostgreSQL container
	pc, err := testutil.StartPostgresContainer(ctx)
	require.NoError(t, err)
	defer func() {
		err := pc.Close(ctx)
		require.NoError(t, err)
	}()

	// Get SQL database connection for migrations
	sqlDB, err := pc.GetSQLDB(ctx)
	require.NoError(t, err)

	// Run migrations
	err = db.RunMigrations(ctx, sqlDB)
	require.NoError(t, err)

	// Verify migrations table exists
	var count int
	err = sqlDB.QueryRowContext(ctx, "SELECT COUNT(*) FROM schema_migrations").Scan(&count)
	require.NoError(t, err)
	assert.Greater(t, count, 0, "Should have applied migrations")

	t.Logf("✅ Applied %d migrations successfully", count)
}

// TestConnectionPool_WithContainer tests connection pool behavior with a real database
func TestConnectionPool_WithContainer(t *testing.T) {
	ctx := context.Background()

	testutil.SetupAndRunTest(t, db.RunMigrations, func(t *testing.T, pc *testutil.PostgresContainer) {
		pool, err := pc.GetPool(ctx)
		require.NoError(t, err)

		// Test basic connectivity
		err = pool.Ping(ctx)
		assert.NoError(t, err)

		// Test connection acquisition
		conn, err := pool.Acquire(ctx)
		require.NoError(t, err)
		defer conn.Release()

		var result int
		err = conn.QueryRow(ctx, "SELECT 1").Scan(&result)
		require.NoError(t, err)
		assert.Equal(t, 1, result)

		t.Logf("✅ Connection pool health verified")
	})
}

// TestCRUD_Operations_WithContainer tests CRUD operations with a real database
func TestCRUD_Operations_WithContainer(t *testing.T) {
	ctx := context.Background()

	testutil.SetupAndRunTest(t, db.RunMigrations, func(t *testing.T, pc *testutil.PostgresContainer) {
		pool, err := pc.GetPool(ctx)
		require.NoError(t, err)

		// Create test table
		err = pc.ExecuteSQL(ctx, `
			CREATE TABLE IF NOT EXISTS test_items (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				title TEXT NOT NULL,
				content TEXT,
				version INTEGER DEFAULT 1,
				created_at TIMESTAMP DEFAULT NOW(),
				updated_at TIMESTAMP DEFAULT NOW()
			)
		`)
		require.NoError(t, err)

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
		})

		t.Run("Read", func(t *testing.T) {
			itemID := uuid.New()
			_, err := pool.Exec(ctx, `
				INSERT INTO test_items (id, title, content)
				VALUES ($1, $2, $3)
			`, itemID, "Read Item", "Read content")
			require.NoError(t, err)

			var title, content string
			err = pool.QueryRow(ctx, `
				SELECT title, content FROM test_items WHERE id = $1
			`, itemID).Scan(&title, &content)

			require.NoError(t, err)
			assert.Equal(t, "Read Item", title)
			assert.Equal(t, "Read content", content)
		})

		t.Run("Update", func(t *testing.T) {
			itemID := uuid.New()
			_, err := pool.Exec(ctx, `
				INSERT INTO test_items (id, title, content, version)
				VALUES ($1, $2, $3, $4)
			`, itemID, "Original Title", "Original content", 1)
			require.NoError(t, err)

			result, err := pool.Exec(ctx, `
				UPDATE test_items
				SET title = $2, content = $3, version = version + 1
				WHERE id = $1
			`, itemID, "Updated Title", "Updated content")
			require.NoError(t, err)
			assert.Equal(t, int64(1), result.RowsAffected())

			var title, content string
			var version int
			err = pool.QueryRow(ctx, `
				SELECT title, content, version FROM test_items WHERE id = $1
			`, itemID).Scan(&title, &content, &version)
			require.NoError(t, err)
			assert.Equal(t, "Updated Title", title)
			assert.Equal(t, "Updated content", content)
			assert.Equal(t, 2, version)
		})

		t.Run("Delete", func(t *testing.T) {
			itemID := uuid.New()
			_, err := pool.Exec(ctx, `
				INSERT INTO test_items (id, title, content)
				VALUES ($1, $2, $3)
			`, itemID, "Delete Item", "Delete content")
			require.NoError(t, err)

			result, err := pool.Exec(ctx, "DELETE FROM test_items WHERE id = $1", itemID)
			require.NoError(t, err)
			assert.Equal(t, int64(1), result.RowsAffected())

			var title string
			err = pool.QueryRow(ctx, "SELECT title FROM test_items WHERE id = $1", itemID).Scan(&title)
			assert.Error(t, err)
			assert.Equal(t, pgx.ErrNoRows, err)
		})

		t.Logf("✅ All CRUD operations passed")
	})
}

// TestTransactions_WithContainer tests transaction behavior with a real database
func TestTransactions_WithContainer(t *testing.T) {
	ctx := context.Background()

	testutil.SetupAndRunTest(t, db.RunMigrations, func(t *testing.T, pc *testutil.PostgresContainer) {
		pool, err := pc.GetPool(ctx)
		require.NoError(t, err)

		// Create test table
		err = pc.ExecuteSQL(ctx, `
			CREATE TABLE IF NOT EXISTS test_transactions (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				title TEXT NOT NULL,
				version INTEGER DEFAULT 1
			)
		`)
		require.NoError(t, err)

		t.Run("Commit", func(t *testing.T) {
			tx, err := pool.Begin(ctx)
			require.NoError(t, err)
			defer tx.Rollback(ctx)

			itemID := uuid.New()
			_, err = tx.Exec(ctx, `
				INSERT INTO test_transactions (id, title)
				VALUES ($1, $2)
			`, itemID, "Transaction Test")
			require.NoError(t, err)

			err = tx.Commit(ctx)
			require.NoError(t, err)

			var title string
			err = pool.QueryRow(ctx, "SELECT title FROM test_transactions WHERE id = $1", itemID).Scan(&title)
			require.NoError(t, err)
			assert.Equal(t, "Transaction Test", title)
		})

		t.Run("Rollback", func(t *testing.T) {
			tx, err := pool.Begin(ctx)
			require.NoError(t, err)

			itemID := uuid.New()
			_, err = tx.Exec(ctx, `
				INSERT INTO test_transactions (id, title)
				VALUES ($1, $2)
			`, itemID, "Rollback Test")
			require.NoError(t, err)

			err = tx.Rollback(ctx)
			require.NoError(t, err)

			var title string
			err = pool.QueryRow(ctx, "SELECT title FROM test_transactions WHERE id = $1", itemID).Scan(&title)
			assert.Error(t, err)
			assert.Equal(t, pgx.ErrNoRows, err)
		})

		t.Logf("✅ All transaction tests passed")
	})
}

// TestConstraintEnforcement_WithContainer tests constraint violations with a real database
func TestConstraintEnforcement_WithContainer(t *testing.T) {
	ctx := context.Background()

	testutil.SetupAndRunTest(t, db.RunMigrations, func(t *testing.T, pc *testutil.PostgresContainer) {
		pool, err := pc.GetPool(ctx)
		require.NoError(t, err)

		// Create test table with constraints
		err = pc.ExecuteSQL(ctx, `
			CREATE TABLE IF NOT EXISTS test_constraints (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				title TEXT NOT NULL,
				email TEXT UNIQUE,
				version INTEGER DEFAULT 1
			)
		`)
		require.NoError(t, err)

		t.Run("PrimaryKey_Duplicate", func(t *testing.T) {
			itemID := uuid.New()

			_, err := pool.Exec(ctx, `
				INSERT INTO test_constraints (id, title)
				VALUES ($1, $2)
			`, itemID, "Item 1")
			require.NoError(t, err)

			_, err = pool.Exec(ctx, `
				INSERT INTO test_constraints (id, title)
				VALUES ($1, $2)
			`, itemID, "Item 2")
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "duplicate key")
		})

		t.Run("NotNull_Violation", func(t *testing.T) {
			_, err := pool.Exec(ctx, `
				INSERT INTO test_constraints (id, title)
				VALUES ($1, NULL)
			`, uuid.New())
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "null value")
		})

		t.Run("Unique_Violation", func(t *testing.T) {
			email := "test@example.com"

			_, err := pool.Exec(ctx, `
				INSERT INTO test_constraints (id, title, email)
				VALUES ($1, $2, $3)
			`, uuid.New(), "Item 1", email)
			require.NoError(t, err)

			_, err = pool.Exec(ctx, `
				INSERT INTO test_constraints (id, title, email)
				VALUES ($1, $2, $3)
			`, uuid.New(), "Item 2", email)
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "unique")
		})

		t.Logf("✅ All constraint tests passed")
	})
}

// TestConcurrentAccess_WithContainer tests concurrent operations with a real database
func TestConcurrentAccess_WithContainer(t *testing.T) {
	ctx := context.Background()

	testutil.SetupAndRunTest(t, db.RunMigrations, func(t *testing.T, pc *testutil.PostgresContainer) {
		pool, err := pc.GetPool(ctx)
		require.NoError(t, err)

		// Create test table
		err = pc.ExecuteSQL(ctx, `
			CREATE TABLE IF NOT EXISTS test_concurrent (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				title TEXT NOT NULL,
				version INTEGER DEFAULT 1
			)
		`)
		require.NoError(t, err)

		// Insert test data
		itemIDs := make([]uuid.UUID, 10)
		for i := 0; i < 10; i++ {
			itemID := uuid.New()
			itemIDs[i] = itemID
			_, err := pool.Exec(ctx, `
				INSERT INTO test_concurrent (id, title, version)
				VALUES ($1, $2, $3)
			`, itemID, fmt.Sprintf("Item %d", i), 1)
			require.NoError(t, err)
		}

		// Run concurrent operations
		t.Run("ConcurrentReads", func(t *testing.T) {
			t.Parallel()
			for i := 0; i < 10; i++ {
				go func(idx int) {
					var title string
					err := pool.QueryRow(ctx, "SELECT title FROM test_concurrent WHERE id = $1", itemIDs[idx]).Scan(&title)
					assert.NoError(t, err)
				}(i)
			}
		})

		t.Run("ConcurrentWrites", func(t *testing.T) {
			t.Parallel()
			for i := 0; i < 10; i++ {
				go func(idx int) {
					_, err := pool.Exec(ctx, `
						UPDATE test_concurrent
						SET version = version + 1
						WHERE id = $1
					`, itemIDs[idx])
					assert.NoError(t, err)
				}(i)
			}
		})

		t.Logf("✅ Concurrent access tests passed")
	})
}
