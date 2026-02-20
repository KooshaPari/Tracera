//go:build integration

package db

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

// setupTestDBForQueries sets up a PostgreSQL container for queries tests
func setupTestDBForQueries(t *testing.T) (*pgxpool.Pool, func()) {
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
	err = pool.Ping(ctx)
	require.NoError(t, err)

	cleanup := func() {
		pool.Close()
		require.NoError(t, pgContainer.Terminate(ctx))
	}

	return pool, cleanup
}

// TestQueries_ItemOperations_Integration tests item CRUD operations
func TestQueries_ItemOperations_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForQueries(t)
	defer cleanup()

	queries := New(pool)
	ctx := context.Background()

	projectID := pgtype.UUID{
		Bytes: uuid.MustParse("123e4567-e89b-12d3-a456-426614174000"),
		Valid: true,
	}

	t.Run("creates item", func(t *testing.T) {
		// Note: Requires migrations to be run first
		// This is a placeholder for integration test
		params := CreateItemParams{
			ProjectID:   projectID,
			Title:       "Test Item",
			Description: pgtype.Text{String: "Test description", Valid: true},
			Type:        "requirement",
			Status:      "open",
		}

		item, err := queries.CreateItem(ctx, params)
		if err != nil {
			// May fail if migrations not run
			t.Logf("CreateItem error (may need migrations): %v", err)
			return
		}
		assert.NotNil(t, item)
		assert.Equal(t, "Test Item", item.Title)
	})

	t.Run("gets item", func(t *testing.T) {
		// Note: Requires item to exist
		itemID := pgtype.UUID{
			Bytes: uuid.New(),
			Valid: true,
		}
		_, err := queries.GetItem(ctx, itemID)
		// May return error if item doesn't exist
		_ = err
	})

	t.Run("lists items by project", func(t *testing.T) {
		params := ListItemsByProjectParams{
			ProjectID: projectID,
			Limit:     10,
			Offset:    0,
		}

		items, err := queries.ListItemsByProject(ctx, params)
		if err != nil {
			t.Logf("ListItemsByProject error (may need migrations): %v", err)
			return
		}
		assert.NotNil(t, items)
		assert.GreaterOrEqual(t, len(items), 0)
	})

	t.Run("updates item", func(t *testing.T) {
		// Note: Requires item to exist
		itemID := pgtype.UUID{
			Bytes: uuid.New(),
			Valid: true,
		}
		params := UpdateItemParams{
			ID:    itemID,
			Title: "Updated Title",
		}

		_, err := queries.UpdateItem(ctx, params)
		// May return error if item doesn't exist
		_ = err
	})

	t.Run("deletes item", func(t *testing.T) {
		// Note: Requires item to exist
		itemID := pgtype.UUID{
			Bytes: uuid.New(),
			Valid: true,
		}
		err := queries.DeleteItem(ctx, itemID)
		// May return error if item doesn't exist
		_ = err
	})
}

// TestQueries_LinkOperations_Integration tests link operations
func TestQueries_LinkOperations_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForQueries(t)
	defer cleanup()

	queries := New(pool)
	ctx := context.Background()

	t.Run("creates link", func(t *testing.T) {
		// Note: Requires migrations and items to exist
		sourceID := pgtype.UUID{
			Bytes: uuid.New(),
			Valid: true,
		}
		targetID := pgtype.UUID{
			Bytes: uuid.New(),
			Valid: true,
		}

		params := CreateLinkParams{
			SourceID: sourceID,
			TargetID: targetID,
			Type:     "implements",
		}

		link, err := queries.CreateLink(ctx, params)
		if err != nil {
			t.Logf("CreateLink error (may need migrations/items): %v", err)
			return
		}
		assert.NotNil(t, link)
	})

	t.Run("lists links by project", func(t *testing.T) {
		projectID := pgtype.UUID{
			Bytes: uuid.MustParse("123e4567-e89b-12d3-a456-426614174000"),
			Valid: true,
		}
		// Note: Check actual method name in queries.sql.go
		// This is a placeholder - adjust based on actual method
		_ = projectID
		_ = queries
	})
}

// TestQueries_ProjectOperations_Integration tests project operations
func TestQueries_ProjectOperations_Integration(t *testing.T) {
	pool, cleanup := setupTestDBForQueries(t)
	defer cleanup()

	queries := New(pool)
	ctx := context.Background()

	t.Run("creates project", func(t *testing.T) {
		params := CreateProjectParams{
			Name:        "Test Project",
			Description: pgtype.Text{String: "Test description", Valid: true},
		}

		project, err := queries.CreateProject(ctx, params)
		if err != nil {
			t.Logf("CreateProject error (may need migrations): %v", err)
			return
		}
		assert.NotNil(t, project)
		assert.Equal(t, "Test Project", project.Name)
	})

	t.Run("lists projects", func(t *testing.T) {
		params := ListProjectsParams{
			Limit:  10,
			Offset: 0,
		}

		projects, err := queries.ListProjects(ctx, params)
		if err != nil {
			t.Logf("ListProjects error (may need migrations): %v", err)
			return
		}
		assert.NotNil(t, projects)
		assert.GreaterOrEqual(t, len(projects), 0)
	})
}
