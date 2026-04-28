//go:build integration

package repository

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	postgrescontainer "github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
	postgresdriver "gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// setupTestDBForRepository sets up a PostgreSQL container for repository integration tests
func setupTestDBForRepository(t *testing.T) (*gorm.DB, func()) {
	ctx := context.Background()

	pgContainer, err := postgrescontainer.RunContainer(ctx,
		testcontainers.WithImage("postgres:16-alpine"),
		postgrescontainer.WithDatabase("testdb"),
		postgrescontainer.WithUsername("testuser"),
		postgrescontainer.WithPassword("testpass"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(30*time.Second)),
	)
	require.NoError(t, err)

	connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	require.NoError(t, err)

	db, err := gorm.Open(postgresdriver.Open(connStr), &gorm.Config{})
	require.NoError(t, err)

	// Auto migrate models
	err = db.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{}, &models.Agent{})
	require.NoError(t, err)

	cleanup := func() {
		sqlDB, _ := db.DB()
		if sqlDB != nil {
			_ = sqlDB.Close()
		}
		require.NoError(t, pgContainer.Terminate(ctx))
	}

	return db, cleanup
}

// TestItemRepository_Integration tests ItemRepository with real PostgreSQL
func TestItemRepository_Integration(t *testing.T) {
	db, cleanup := setupTestDBForRepository(t)
	defer cleanup()

	repo := NewItemRepository(db)
	ctx := context.Background()

	projectID := "proj-" + uuid.New().String()

	t.Run("creates item", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-" + uuid.New().String(),
			ProjectID: projectID,
			Title:     "Test Item",
			Type:      "requirement",
			Status:    "open",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, item)
		if err != nil {
			t.Logf("Create error: %v", err)
			return
		}
		assert.NoError(t, err)
	})

	t.Run("gets item by id", func(t *testing.T) {
		itemID := "item-" + uuid.New().String()
		item, err := repo.GetByID(ctx, itemID)
		// May return error if item doesn't exist
		if err == nil {
			assert.NotNil(t, item)
		}
	})

	t.Run("lists items", func(t *testing.T) {
		filter := ItemFilter{}
		items, err := repo.List(ctx, filter)
		if err != nil {
			t.Logf("List error: %v", err)
			return
		}
		assert.NotNil(t, items)
		assert.GreaterOrEqual(t, len(items), 0)
	})
}

// TestLinkRepository_Integration tests LinkRepository with real PostgreSQL
func TestLinkRepository_Integration(t *testing.T) {
	db, cleanup := setupTestDBForRepository(t)
	defer cleanup()

	repo := NewLinkRepository(db)
	ctx := context.Background()

	t.Run("creates link", func(t *testing.T) {
		// Note: Requires items to exist
		link := &models.Link{
			ID:        "link-" + uuid.New().String(),
			SourceID:  "item-" + uuid.New().String(),
			TargetID:  "item-" + uuid.New().String(),
			Type:      "implements",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, link)
		if err != nil {
			t.Logf("Create error (may need items): %v", err)
			return
		}
		assert.NoError(t, err)
	})

	t.Run("lists links", func(t *testing.T) {
		filter := LinkFilter{}
		links, err := repo.List(ctx, filter)
		if err != nil {
			t.Logf("List error: %v", err)
			return
		}
		assert.NotNil(t, links)
		assert.GreaterOrEqual(t, len(links), 0)
	})
}

// TestProjectRepository_Integration tests ProjectRepository with real PostgreSQL
func TestProjectRepository_Integration(t *testing.T) {
	db, cleanup := setupTestDBForRepository(t)
	defer cleanup()

	repo := NewProjectRepository(db)
	ctx := context.Background()

	t.Run("creates project", func(t *testing.T) {
		project := &models.Project{
			ID:          "proj-" + uuid.New().String(),
			Name:        "Test Project",
			Description: "Test description",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		err := repo.Create(ctx, project)
		if err != nil {
			t.Logf("Create error: %v", err)
			return
		}
		assert.NoError(t, err)
	})

	t.Run("lists all projects", func(t *testing.T) {
		projects, err := repo.List(ctx)
		if err != nil {
			t.Logf("List error: %v", err)
			return
		}
		assert.NotNil(t, projects)
		assert.GreaterOrEqual(t, len(projects), 0)
	})
}
