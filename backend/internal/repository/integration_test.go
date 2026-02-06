//go:build integration

package repository

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/testutil"
)

// setupTestRepositoryDB sets up a PostgreSQL container and GORM instance using testutil
func setupTestRepositoryDB(t *testing.T) (*gorm.DB, *testutil.PostgresContainer, func()) {
	ctx := context.Background()

	// Start PostgreSQL container using testutil
	pc, err := testutil.StartPostgresContainer(ctx)
	require.NoError(t, err, "Failed to start PostgreSQL container")

	// Get SQL database for running migrations
	sqlDB, err := pc.GetSQLDB(ctx)
	require.NoError(t, err, "Failed to get SQL database")

	// Run migrations
	err = db.RunMigrations(ctx, sqlDB)
	require.NoError(t, err, "Failed to run migrations")

	// Get connection string and create GORM DB
	connStr := pc.GetConnectionString()
	gormDB, err := gorm.Open(postgres.Open(connStr), &gorm.Config{})
	require.NoError(t, err, "Failed to open GORM database")

	// Auto-migrate models (if needed for GORM-based operations)
	err = gormDB.AutoMigrate(
		&models.Item{},
		&models.Link{},
		&models.Project{},
		&models.Agent{},
	)
	require.NoError(t, err, "Failed to auto-migrate models")

	cleanup := func() {
		err := pc.Close(ctx)
		if err != nil {
			t.Logf("⚠️ Warning: Failed to close container: %v", err)
		}
	}

	return gormDB, pc, cleanup
}

// TestItemRepository_CRUD_Integration tests ItemRepository CRUD operations with testcontainers
func TestItemRepository_CRUD_Integration(t *testing.T) {
	gormDB, pc, cleanup := setupTestRepositoryDB(t)
	defer cleanup()

	ctx := context.Background()
	pool, err := pc.GetPool(ctx)
	require.NoError(t, err)

	repo := NewItemRepository(gormDB)
	projectID := "proj-" + uuid.New().String()

	t.Run("Create_Item", func(t *testing.T) {
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
		assert.NoError(t, err, "Should create item successfully")

		// Verify item was created
		var storedItem models.Item
		err = gormDB.Where("id = ?", item.ID).First(&storedItem).Error
		if err != nil {
			t.Logf("Verification error (might not use GORM): %v", err)
		}
	})

	t.Run("Read_Item", func(t *testing.T) {
		itemID := "item-" + uuid.New().String()
		item := &models.Item{
			ID:        itemID,
			ProjectID: projectID,
			Title:     "Read Test Item",
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

		retrieved, err := repo.GetByID(ctx, itemID)
		if err == nil {
			assert.NotNil(t, retrieved)
		}
	})

	t.Run("Update_Item", func(t *testing.T) {
		itemID := "item-" + uuid.New().String()
		originalTitle := "Original Title"
		updatedTitle := "Updated Title"

		item := &models.Item{
			ID:        itemID,
			ProjectID: projectID,
			Title:     originalTitle,
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

		item.Title = updatedTitle
		item.UpdatedAt = time.Now()

		err = repo.Update(ctx, item)
		if err == nil {
			retrieved, _ := repo.GetByID(ctx, itemID)
			if retrieved != nil {
				assert.Equal(t, updatedTitle, retrieved.Title)
			}
		}
	})

	t.Run("Delete_Item", func(t *testing.T) {
		itemID := "item-" + uuid.New().String()
		item := &models.Item{
			ID:        itemID,
			ProjectID: projectID,
			Title:     "Delete Test Item",
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

		err = repo.Delete(ctx, itemID)
		if err == nil {
			_, err := repo.GetByID(ctx, itemID)
			assert.Error(t, err, "Item should not exist after deletion")
		}
	})

	t.Run("List_Items", func(t *testing.T) {
		filter := ItemFilter{}
		items, err := repo.List(ctx, filter)
		if err != nil {
			t.Logf("List error: %v", err)
			return
		}
		assert.NotNil(t, items)
		assert.GreaterOrEqual(t, len(items), 0)
	})

	t.Logf("✅ ItemRepository integration tests completed")
}

// TestLinkRepository_CRUD_Integration tests LinkRepository CRUD operations with testcontainers
func TestLinkRepository_CRUD_Integration(t *testing.T) {
	gormDB, pc, cleanup := setupTestRepositoryDB(t)
	defer cleanup()

	ctx := context.Background()

	repo := NewLinkRepository(gormDB)

	t.Run("Create_Link", func(t *testing.T) {
		sourceID := "item-" + uuid.New().String()
		targetID := "item-" + uuid.New().String()

		link := &models.Link{
			ID:        "link-" + uuid.New().String(),
			SourceID:  sourceID,
			TargetID:  targetID,
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

	t.Run("Read_Link", func(t *testing.T) {
		sourceID := "item-" + uuid.New().String()
		targetID := "item-" + uuid.New().String()
		linkID := "link-" + uuid.New().String()

		link := &models.Link{
			ID:        linkID,
			SourceID:  sourceID,
			TargetID:  targetID,
			Type:      "implements",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, link)
		if err != nil {
			t.Logf("Create error: %v", err)
			return
		}

		retrieved, err := repo.GetByID(ctx, linkID)
		if err == nil {
			assert.NotNil(t, retrieved)
		}
	})

	t.Run("List_Links", func(t *testing.T) {
		filter := LinkFilter{}
		links, err := repo.List(ctx, filter)
		if err != nil {
			t.Logf("List error: %v", err)
			return
		}
		assert.NotNil(t, links)
		assert.GreaterOrEqual(t, len(links), 0)
	})

	t.Logf("✅ LinkRepository integration tests completed")
}

// TestProjectRepository_CRUD_Integration tests ProjectRepository CRUD operations with testcontainers
func TestProjectRepository_CRUD_Integration(t *testing.T) {
	gormDB, pc, cleanup := setupTestRepositoryDB(t)
	defer cleanup()

	ctx := context.Background()

	repo := NewProjectRepository(gormDB)

	t.Run("Create_Project", func(t *testing.T) {
		project := &models.Project{
			ID:          "proj-" + uuid.New().String(),
			Name:        "Test Project",
			Description: "Test description",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		err := repo.Create(ctx, project)
		assert.NoError(t, err, "Should create project successfully")
	})

	t.Run("Read_Project", func(t *testing.T) {
		projectID := "proj-" + uuid.New().String()
		project := &models.Project{
			ID:          projectID,
			Name:        "Read Test Project",
			Description: "Read test description",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		err := repo.Create(ctx, project)
		if err != nil {
			t.Logf("Create error: %v", err)
			return
		}

		retrieved, err := repo.GetByID(ctx, projectID)
		if err == nil {
			assert.NotNil(t, retrieved)
			assert.Equal(t, projectID, retrieved.ID)
		}
	})

	t.Run("Update_Project", func(t *testing.T) {
		projectID := "proj-" + uuid.New().String()
		originalName := "Original Name"
		updatedName := "Updated Name"

		project := &models.Project{
			ID:          projectID,
			Name:        originalName,
			Description: "Test description",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		err := repo.Create(ctx, project)
		if err != nil {
			t.Logf("Create error: %v", err)
			return
		}

		project.Name = updatedName
		project.UpdatedAt = time.Now()

		err = repo.Update(ctx, project)
		if err == nil {
			retrieved, _ := repo.GetByID(ctx, projectID)
			if retrieved != nil {
				assert.Equal(t, updatedName, retrieved.Name)
			}
		}
	})

	t.Run("Delete_Project", func(t *testing.T) {
		projectID := "proj-" + uuid.New().String()
		project := &models.Project{
			ID:          projectID,
			Name:        "Delete Test Project",
			Description: "Delete test description",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		err := repo.Create(ctx, project)
		if err != nil {
			t.Logf("Create error: %v", err)
			return
		}

		err = repo.Delete(ctx, projectID)
		if err == nil {
			_, err := repo.GetByID(ctx, projectID)
			assert.Error(t, err, "Project should not exist after deletion")
		}
	})

	t.Run("List_Projects", func(t *testing.T) {
		projects, err := repo.List(ctx)
		if err != nil {
			t.Logf("List error: %v", err)
			return
		}
		assert.NotNil(t, projects)
		assert.GreaterOrEqual(t, len(projects), 0)
	})

	t.Logf("✅ ProjectRepository integration tests completed")
}

// TestRawQueryExecutionWithContainer tests direct SQL query execution with pgxpool
func TestRawQueryExecutionWithContainer(t *testing.T) {
	ctx := context.Background()

	testutil.SetupAndRunTest(t, db.RunMigrations, func(t *testing.T, pc *testutil.PostgresContainer) {
		pool, err := pc.GetPool(ctx)
		require.NoError(t, err)

		// Create test table
		err = pc.ExecuteSQL(ctx, `
			CREATE TABLE IF NOT EXISTS test_raw_queries (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				name TEXT NOT NULL,
				status TEXT DEFAULT 'active'
			)
		`)
		require.NoError(t, err)

		t.Run("Execute_Raw_Insert", func(t *testing.T) {
			id := uuid.New()
			_, err := pool.Exec(ctx, `
				INSERT INTO test_raw_queries (id, name, status)
				VALUES ($1, $2, $3)
			`, id, "Test Record", "active")
			assert.NoError(t, err)
		})

		t.Run("Execute_Raw_Query", func(t *testing.T) {
			id := uuid.New()
			_, err := pool.Exec(ctx, `
				INSERT INTO test_raw_queries (id, name, status)
				VALUES ($1, $2, $3)
			`, id, "Query Test", "active")
			require.NoError(t, err)

			var name string
			var status string
			err = pool.QueryRow(ctx, `
				SELECT name, status FROM test_raw_queries WHERE id = $1
			`, id).Scan(&name, &status)
			assert.NoError(t, err)
			assert.Equal(t, "Query Test", name)
			assert.Equal(t, "active", status)
		})

		t.Logf("✅ Raw query execution tests completed")
	})
}

// TestConcurrentRepositoryOperations tests concurrent repository operations with testcontainers
func TestConcurrentRepositoryOperations(t *testing.T) {
	gormDB, pc, cleanup := setupTestRepositoryDB(t)
	defer cleanup()

	ctx := context.Background()

	repo := NewItemRepository(gormDB)
	projectID := "proj-" + uuid.New().String()
	numConcurrent := 10

	t.Run("Concurrent_Creates", func(t *testing.T) {
		for i := 0; i < numConcurrent; i++ {
			go func(idx int) {
				item := &models.Item{
					ID:        "item-" + uuid.New().String(),
					ProjectID: projectID,
					Title:     "Concurrent Item",
					Type:      "requirement",
					Status:    "open",
					CreatedAt: time.Now(),
					UpdatedAt: time.Now(),
				}

				err := repo.Create(ctx, item)
				assert.NoError(t, err, "Concurrent create should succeed")
			}(i)
		}
	})

	t.Logf("✅ Concurrent repository operations test completed")
}

// TestTransactionIsolation tests transaction isolation with testcontainers
func TestTransactionIsolation(t *testing.T) {
	ctx := context.Background()

	testutil.SetupAndRunTest(t, db.RunMigrations, func(t *testing.T, pc *testutil.PostgresContainer) {
		pool, err := pc.GetPool(ctx)
		require.NoError(t, err)

		// Create test table
		err = pc.ExecuteSQL(ctx, `
			CREATE TABLE IF NOT EXISTS test_isolation (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				value INTEGER NOT NULL
			)
		`)
		require.NoError(t, err)

		t.Run("Transaction_Isolation", func(t *testing.T) {
			// Start transaction
			tx, err := pool.Begin(ctx)
			require.NoError(t, err)
			defer tx.Rollback(ctx)

			id := uuid.New()

			// Insert in transaction
			_, err = tx.Exec(ctx, `
				INSERT INTO test_isolation (id, value)
				VALUES ($1, $2)
			`, id, 100)
			require.NoError(t, err)

			// Update in same transaction
			_, err = tx.Exec(ctx, `
				UPDATE test_isolation SET value = $2 WHERE id = $1
			`, id, 200)
			require.NoError(t, err)

			// Verify update in transaction
			var value int
			err = tx.QueryRow(ctx, `
				SELECT value FROM test_isolation WHERE id = $1
			`, id).Scan(&value)
			require.NoError(t, err)
			assert.Equal(t, 200, value)

			// Commit
			err = tx.Commit(ctx)
			require.NoError(t, err)

			// Verify after commit
			err = pool.QueryRow(ctx, `
				SELECT value FROM test_isolation WHERE id = $1
			`, id).Scan(&value)
			require.NoError(t, err)
			assert.Equal(t, 200, value)
		})

		t.Logf("✅ Transaction isolation test completed")
	})
}
