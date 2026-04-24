//go:build integration
// +build integration

package db

import (
	"context"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// setupTestDB creates a PostgreSQL container and returns a connection pool
func setupTestDB(t *testing.T) (*pgxpool.Pool, testcontainers.Container) {
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

	pool, err := pgxpool.New(ctx, connString)
	require.NoError(t, err)

	// Run migrations using pgxpool
	conn, err := pool.Acquire(ctx)
	require.NoError(t, err)
	defer conn.Release()

	// Execute migration SQL directly
	migrationSQL := `
		CREATE TABLE IF NOT EXISTS projects (
			id uuid NOT NULL DEFAULT gen_random_uuid(),
			name varchar(255) NOT NULL,
			description text,
			metadata jsonb DEFAULT '{}'::jsonb,
			created_at timestamp NOT NULL DEFAULT now(),
			updated_at timestamp NOT NULL DEFAULT now(),
			deleted_at timestamp,
			PRIMARY KEY (id)
		);
	`
	_, err = conn.Exec(ctx, migrationSQL)
	require.NoError(t, err)

	return pool, container
}

func TestNew(t *testing.T) {
	pool, container := setupTestDB(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	t.Run("creates new Queries instance", func(t *testing.T) {
		queries := New(pool)
		assert.NotNil(t, queries)
		assert.Equal(t, pool, queries.db)
	})

	t.Run("can execute queries", func(t *testing.T) {
		queries := New(pool)

		// Create a test project
		project, err := queries.CreateProject(ctx, CreateProjectParams{
			Name:        "Test Project",
			Description: pgtype.Text{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)
		assert.Equal(t, "Test Project", project.Name)
	})
}

func TestWithTx(t *testing.T) {
	pool, container := setupTestDB(t)
	defer container.Terminate(context.Background())
	defer func() {
		pool.Close()
		if false {
			// ignore error
		}
	}()

	ctx := context.Background()

	t.Run("creates queries with transaction", func(t *testing.T) {
		queries := New(pool)

		tx, err := pool.Begin(ctx)
		require.NoError(t, err)
		defer tx.Rollback(ctx)

		txQueries := queries.WithTx(tx)
		assert.NotNil(t, txQueries)
		assert.Equal(t, tx, txQueries.db)
	})

	t.Run("transaction isolation", func(t *testing.T) {
		queries := New(pool)

		// Start transaction
		tx, err := pool.Begin(ctx)
		require.NoError(t, err)

		txQueries := queries.WithTx(tx)

		// Create project in transaction
		project, err := txQueries.CreateProject(ctx, CreateProjectParams{
			Name:        "Tx Project",
			Description: pgtype.Text{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)
		assert.Equal(t, "Tx Project", project.Name)

		// Verify it's not visible outside transaction yet
		_, err = queries.GetProject(ctx, project.ID)
		assert.Error(t, err) // Should not be visible

		// Commit transaction
		err = tx.Commit(ctx)
		require.NoError(t, err)

		// Now it should be visible
		retrieved, err := queries.GetProject(ctx, project.ID)
		require.NoError(t, err)
		assert.Equal(t, "Tx Project", retrieved.Name)
	})

	t.Run("transaction rollback", func(t *testing.T) {
		queries := New(pool)

		// Start transaction
		tx, err := pool.Begin(ctx)
		require.NoError(t, err)

		txQueries := queries.WithTx(tx)

		// Create project in transaction
		project, err := txQueries.CreateProject(ctx, CreateProjectParams{
			Name:        "Rollback Project",
			Description: pgtype.Text{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)

		// Rollback transaction
		err = tx.Rollback(ctx)
		require.NoError(t, err)

		// Should not be visible
		_, err = queries.GetProject(ctx, project.ID)
		assert.Error(t, err)
	})
}
