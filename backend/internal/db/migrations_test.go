//go:build integration
// +build integration

package db

import (
	"context"
	"database/sql"
	"testing"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// setupTestDBForMigrations creates a PostgreSQL container and returns a *sql.DB
func setupTestDBForMigrations(t *testing.T) (*sql.DB, testcontainers.Container) {
	ctx := context.Background()

	req := testcontainers.ContainerRequest{
		Image:        "postgres:16-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_USER":     "testuser",
			"POSTGRES_PASSWORD": "testpass",
			"POSTGRES_DB":       "testdb",
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithOccurrence(2).
			WithStartupTimeout(30 * time.Second),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	require.NoError(t, err)

	host, err := container.Host(ctx)
	require.NoError(t, err)

	port, err := container.MappedPort(ctx, "5432")
	require.NoError(t, err)

	connString := "postgres://testuser:testpass@" + host + ":" + port.Port() + "/testdb?sslmode=disable"

	db, err := sql.Open("pgx", connString)
	require.NoError(t, err)

	return db, container
}

func TestRunMigrations(t *testing.T) {
	db, container := setupTestDBForMigrations(t)
	defer container.Terminate(context.Background())
	defer func() {
		if err := db.Close(); err != nil {
			// ignore error
		}
	}()

	ctx := context.Background()

	t.Run("creates migrations table", func(t *testing.T) {
		err := RunMigrations(ctx, db)
		require.NoError(t, err)

		// Verify migrations table exists
		var count int
		err = db.QueryRowContext(ctx, `
			SELECT COUNT(*) 
			FROM information_schema.tables 
			WHERE table_schema = 'public' AND table_name = 'schema_migrations'
		`).Scan(&count)
		require.NoError(t, err)
		assert.Equal(t, 1, count)
	})

	t.Run("applies available migrations", func(t *testing.T) {
		err := RunMigrations(ctx, db)
		require.NoError(t, err)

		// Verify migrations were recorded
		var migrationCount int
		err = db.QueryRowContext(ctx, "SELECT COUNT(*) FROM schema_migrations").Scan(&migrationCount)
		require.NoError(t, err)
		assert.Greater(t, migrationCount, 0)
	})

	t.Run("idempotent - can run multiple times", func(t *testing.T) {
		// Run migrations first time
		err := RunMigrations(ctx, db)
		require.NoError(t, err)

		var count1 int
		err = db.QueryRowContext(ctx, "SELECT COUNT(*) FROM schema_migrations").Scan(&count1)
		require.NoError(t, err)

		// Run migrations second time
		err = RunMigrations(ctx, db)
		require.NoError(t, err)

		var count2 int
		err = db.QueryRowContext(ctx, "SELECT COUNT(*) FROM schema_migrations").Scan(&count2)
		require.NoError(t, err)

		// Should have same count (no duplicates)
		assert.Equal(t, count1, count2)
	})
}

func TestCreateMigrationsTable(t *testing.T) {
	db, container := setupTestDBForMigrations(t)
	defer container.Terminate(context.Background())
	defer func() {
		if err := db.Close(); err != nil {
			// ignore error
		}
	}()

	ctx := context.Background()

	t.Run("creates table if not exists", func(t *testing.T) {
		err := createMigrationsTable(ctx, db)
		require.NoError(t, err)

		// Verify table exists
		var exists bool
		err = db.QueryRowContext(ctx, `
			SELECT EXISTS (
				SELECT FROM information_schema.tables 
				WHERE table_schema = 'public' AND table_name = 'schema_migrations'
			)
		`).Scan(&exists)
		require.NoError(t, err)
		assert.True(t, exists)
	})

	t.Run("idempotent - can create multiple times", func(t *testing.T) {
		err := createMigrationsTable(ctx, db)
		require.NoError(t, err)

		// Create again should not error
		err = createMigrationsTable(ctx, db)
		require.NoError(t, err)
	})
}

func TestGetAppliedMigrations(t *testing.T) {
	db, container := setupTestDBForMigrations(t)
	defer container.Terminate(context.Background())
	defer func() {
		if err := db.Close(); err != nil {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Setup migrations table
	err := createMigrationsTable(ctx, db)
	require.NoError(t, err)

	t.Run("returns empty map when no migrations applied", func(t *testing.T) {
		applied, err := getAppliedMigrations(ctx, db)
		require.NoError(t, err)
		assert.Empty(t, applied)
	})

	t.Run("returns applied migrations", func(t *testing.T) {
		// Record a test migration
		_, err = db.ExecContext(ctx, `
			INSERT INTO schema_migrations (version, name)
			VALUES ('20250101000000', 'test_migration')
		`)
		require.NoError(t, err)

		applied, err := getAppliedMigrations(ctx, db)
		require.NoError(t, err)
		assert.True(t, applied["20250101000000"])
		assert.Len(t, applied, 1)
	})
}

func TestGetAvailableMigrations(t *testing.T) {
	t.Run("returns available migrations", func(t *testing.T) {
		available, err := getAvailableMigrations()
		require.NoError(t, err)
		assert.Greater(t, len(available), 0)

		// Verify migrations are sorted
		for i := 1; i < len(available); i++ {
			assert.True(t, available[i-1].Version <= available[i].Version,
				"Migrations should be sorted by version")
		}
	})

	t.Run("parses migration filenames correctly", func(t *testing.T) {
		available, err := getAvailableMigrations()
		require.NoError(t, err)

		for _, migration := range available {
			assert.NotEmpty(t, migration.Version)
			assert.NotEmpty(t, migration.Name)
		}
	})
}

func TestRecordMigration(t *testing.T) {
	db, container := setupTestDBForMigrations(t)
	defer container.Terminate(context.Background())
	defer func() {
		if err := db.Close(); err != nil {
			// ignore error
		}
	}()

	ctx := context.Background()

	// Setup migrations table
	err := createMigrationsTable(ctx, db)
	require.NoError(t, err)

	t.Run("records migration", func(t *testing.T) {
		migration := MigrationRecord{
			Version: "20250101000000",
			Name:    "test_migration",
		}

		err := recordMigration(ctx, db, migration)
		require.NoError(t, err)

		// Verify it was recorded
		var count int
		err = db.QueryRowContext(ctx, `
			SELECT COUNT(*) FROM schema_migrations WHERE version = $1
		`, migration.Version).Scan(&count)
		require.NoError(t, err)
		assert.Equal(t, 1, count)
	})
}
