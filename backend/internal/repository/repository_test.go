package repository

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func setupTestDB(t *testing.T) *gorm.DB {
	dsn := os.Getenv("TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		t.Skipf("Failed to connect to database: %v", err)
	}

	// Auto migrate models
	err = db.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{}, &models.Agent{})
	if err != nil {
		t.Fatalf("Failed to migrate: %v", err)
	}

	return db
}

func cleanupDB(db *gorm.DB) {
	db.Exec("DELETE FROM links")
	db.Exec("DELETE FROM items")
	db.Exec("DELETE FROM agents")
	db.Exec("DELETE FROM projects")
}

const (
	testProjectID1 = "proj-1"
	testItemType   = "task"
)

// Item Repository Tests

func TestItemRepositoryCreate(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewItemRepository(db)
	ctx := context.Background()

	t.Run("create item successfully", func(t *testing.T) {
		item := &models.Item{
			ID:          "item-1",
			ProjectID:   testProjectID1,
			Title:       "Test Item",
			Description: "Test Description",
			Type:        "task",
			Status:      "open",
			Priority:    models.PriorityHigh,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		err := repo.Create(ctx, item)
		require.NoError(t, err)
		assert.NotEmpty(t, item.ID)
	})

	t.Run("create duplicate item fails", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-dup",
			ProjectID: testProjectID1,
			Title:     "Duplicate",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, item)
		require.NoError(t, err)

		err = repo.Create(ctx, item)
		require.Error(t, err)
	})

	t.Run("create with minimal fields", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-minimal",
			ProjectID: testProjectID1,
			Title:     "Minimal",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, item)
		require.NoError(t, err)
	})
}

func TestItemRepositoryGetByID(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewItemRepository(db)
	ctx := context.Background()

	// Create test item
	testItem := &models.Item{
		ID:        "item-get-1",
		ProjectID: testProjectID1,
		Title:     "Get Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, repo.Create(ctx, testItem))

	t.Run("get existing item", func(t *testing.T) {
		item, err := repo.GetByID(ctx, "item-get-1")
		require.NoError(t, err)
		assert.NotNil(t, item)
		assert.Equal(t, "Get Test", item.Title)
	})

	t.Run("get non-existent item", func(t *testing.T) {
		item, err := repo.GetByID(ctx, "non-existent")
		require.Error(t, err)
		assert.Nil(t, item)
		assert.Contains(t, err.Error(), "not found")
	})

	t.Run("get deleted item returns error", func(t *testing.T) {
		deletedItem := &models.Item{
			ID:        "item-deleted",
			ProjectID: testProjectID1,
			Title:     "Deleted",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, repo.Create(ctx, deletedItem))
		require.NoError(t, repo.Delete(ctx, "item-deleted"))

		item, err := repo.GetByID(ctx, "item-deleted")
		require.Error(t, err)
		assert.Nil(t, item)
	})
}

func seedListItems(ctx context.Context, t *testing.T, repo ItemRepository) {
	t.Helper()
	items := []*models.Item{
		{
			ID:        "item-list-1",
			ProjectID: testProjectID1,
			Title:     "Item 1",
			Type:      testItemType,
			Status:    "open",
			Priority:  models.PriorityHigh,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
		{
			ID:        "item-list-2",
			ProjectID: testProjectID1,
			Title:     "Item 2",
			Type:      "bug",
			Status:    "closed",
			Priority:  models.PriorityLow,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
		{
			ID:        "item-list-3",
			ProjectID: "proj-2",
			Title:     "Item 3",
			Type:      testItemType,
			Status:    "open",
			Priority:  models.PriorityMedium,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
	}

	for _, item := range items {
		require.NoError(t, repo.Create(ctx, item))
	}
}

func runListCase(
	ctx context.Context,
	t *testing.T,
	name string,
	repo ItemRepository,
	filter ItemFilter,
	assertFn func(*testing.T, []*models.Item),
) {
	t.Helper()
	t.Run(name, func(t *testing.T) {
		result, err := repo.List(ctx, filter)
		require.NoError(t, err)
		assertFn(t, result)
	})
}

func filterByProjectID(projectID string) ItemFilter {
	return ItemFilter{ProjectID: &projectID}
}

func filterByType(itemType string) ItemFilter {
	return ItemFilter{Type: &itemType}
}

func filterByStatus(status string) ItemFilter {
	return ItemFilter{Status: &status}
}

func filterByPriority(priority models.Priority) ItemFilter {
	return ItemFilter{Priority: &priority}
}

func filterByProjectAndType(projectID string, itemType string) ItemFilter {
	return ItemFilter{ProjectID: &projectID, Type: &itemType}
}

func TestItemRepositoryList(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewItemRepository(db)
	ctx := context.Background()

	seedListItems(ctx, t, repo)

	runListCase(ctx, t, "list all items", repo, ItemFilter{}, func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 3)
	})
	runListCase(ctx, t, "filter by project ID", repo, filterByProjectID(testProjectID1), func(t *testing.T, result []*models.Item) {
		assert.Len(t, result, 2)
	})
	runListCase(ctx, t, "filter by type", repo, filterByType(testItemType), func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 2)
	})
	runListCase(ctx, t, "filter by status", repo, filterByStatus("open"), func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 2)
	})
	runListCase(ctx, t, "filter by priority", repo, filterByPriority(models.PriorityHigh), func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 1)
	})
	runListCase(ctx, t, "with limit", repo, ItemFilter{Limit: 2}, func(t *testing.T, result []*models.Item) {
		assert.LessOrEqual(t, len(result), 2)
	})
	runListCase(ctx, t, "with offset", repo, ItemFilter{Offset: 1}, func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 2)
	})
	combinedFilter := filterByProjectAndType(testProjectID1, testItemType)
	runListCase(ctx, t, "combined filters", repo, combinedFilter, func(t *testing.T, result []*models.Item) {
		assert.Len(t, result, 1)
	})
}

func TestItemRepositoryUpdate(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewItemRepository(db)
	ctx := context.Background()

	t.Run("update item successfully", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-update-1",
			ProjectID: testProjectID1,
			Title:     "Original",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, repo.Create(ctx, item))

		item.Title = "Updated"
		err := repo.Update(ctx, item)
		require.NoError(t, err)

		updated, err := repo.GetByID(ctx, "item-update-1")
		require.NoError(t, err)
		assert.Equal(t, "Updated", updated.Title)
	})

	t.Run("update non-existent item", func(t *testing.T) {
		item := &models.Item{
			ID:        "non-existent",
			Title:     "Should Fail",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Update(ctx, item)
		// GORM Save will insert if not exists
		require.NoError(t, err)
	})
}

func TestItemRepositoryDelete(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewItemRepository(db)
	ctx := context.Background()

	t.Run("soft delete item", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-del-1",
			ProjectID: testProjectID1,
			Title:     "To Delete",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, repo.Create(ctx, item))

		err := repo.Delete(ctx, "item-del-1")
		require.NoError(t, err)

		// Should not be found
		_, err = repo.GetByID(ctx, "item-del-1")
		require.Error(t, err)
	})

	t.Run("delete non-existent item", func(t *testing.T) {
		err := repo.Delete(ctx, "non-existent")
		require.NoError(t, err) // Soft delete succeeds even if not found
	})
}

func TestItemRepositoryCount(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewItemRepository(db)
	ctx := context.Background()

	// Create test items
	for i := 0; i < 5; i++ {
		item := &models.Item{
			ID:        "item-count-" + string(rune(i)),
			ProjectID: "proj-count",
			Title:     "Count Test",
			Type:      "task",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, repo.Create(ctx, item))
	}

	t.Run("count all items", func(t *testing.T) {
		filter := ItemFilter{}
		count, err := repo.Count(ctx, filter)
		require.NoError(t, err)
		assert.GreaterOrEqual(t, count, int64(5))
	})

	t.Run("count filtered items", func(t *testing.T) {
		projectID := "proj-count"
		filter := ItemFilter{ProjectID: &projectID}
		count, err := repo.Count(ctx, filter)
		require.NoError(t, err)
		assert.Equal(t, int64(5), count)
	})
}

// Link Repository Tests

func TestLinkRepositoryCreate(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewLinkRepository(db)
	ctx := context.Background()

	t.Run("create link successfully", func(t *testing.T) {
		link := &models.Link{
			ID:        "link-1",
			SourceID:  "item-1",
			TargetID:  "item-2",
			Type:      "depends_on",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, link)
		require.NoError(t, err)
	})

	t.Run("create duplicate link fails", func(t *testing.T) {
		link := &models.Link{
			ID:        "link-dup",
			SourceID:  "item-1",
			TargetID:  "item-2",
			Type:      "depends_on",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, link)
		require.NoError(t, err)

		err = repo.Create(ctx, link)
		require.Error(t, err)
	})
}

func TestLinkRepositoryGetByID(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewLinkRepository(db)
	ctx := context.Background()

	testLink := &models.Link{
		ID:        "link-get-1",
		SourceID:  "item-1",
		TargetID:  "item-2",
		Type:      "blocks",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, repo.Create(ctx, testLink))

	t.Run("get existing link", func(t *testing.T) {
		link, err := repo.GetByID(ctx, "link-get-1")
		require.NoError(t, err)
		assert.NotNil(t, link)
		assert.Equal(t, "blocks", link.Type)
	})

	t.Run("get non-existent link", func(t *testing.T) {
		link, err := repo.GetByID(ctx, "non-existent")
		require.Error(t, err)
		assert.Nil(t, link)
	})
}

func TestLinkRepositoryGetBySourceID(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-src-1", SourceID: "source-1", TargetID: "target-1", Type: "depends_on", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-src-2", SourceID: "source-1", TargetID: "target-2", Type: "blocks", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-src-3", SourceID: "source-2", TargetID: "target-3", Type: "related", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}

	for _, link := range links {
		require.NoError(t, repo.Create(ctx, link))
	}

	t.Run("get links by source ID", func(t *testing.T) {
		result, err := repo.GetBySourceID(ctx, "source-1")
		require.NoError(t, err)
		assert.Len(t, result, 2)
	})

	t.Run("get links for non-existent source", func(t *testing.T) {
		result, err := repo.GetBySourceID(ctx, "non-existent")
		require.NoError(t, err)
		assert.Empty(t, result)
	})
}

func TestLinkRepositoryGetByTargetID(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-tgt-1", SourceID: "source-1", TargetID: "target-1", Type: "depends_on", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-tgt-2", SourceID: "source-2", TargetID: "target-1", Type: "blocks", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}

	for _, link := range links {
		require.NoError(t, repo.Create(ctx, link))
	}

	t.Run("get links by target ID", func(t *testing.T) {
		result, err := repo.GetByTargetID(ctx, "target-1")
		require.NoError(t, err)
		assert.Len(t, result, 2)
	})
}

func TestLinkRepositoryList(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-list-1", SourceID: "s1", TargetID: "t1", Type: "depends_on", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-list-2", SourceID: "s2", TargetID: "t2", Type: "blocks", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}

	for _, link := range links {
		require.NoError(t, repo.Create(ctx, link))
	}

	t.Run("list all links", func(t *testing.T) {
		filter := LinkFilter{}
		result, err := repo.List(ctx, filter)
		require.NoError(t, err)
		assert.GreaterOrEqual(t, len(result), 2)
	})

	t.Run("filter by source ID", func(t *testing.T) {
		sourceID := "s1"
		filter := LinkFilter{SourceID: &sourceID}
		result, err := repo.List(ctx, filter)
		require.NoError(t, err)
		assert.Len(t, result, 1)
	})

	t.Run("filter by target ID", func(t *testing.T) {
		targetID := "t2"
		filter := LinkFilter{TargetID: &targetID}
		result, err := repo.List(ctx, filter)
		require.NoError(t, err)
		assert.Len(t, result, 1)
	})

	t.Run("filter by type", func(t *testing.T) {
		linkType := "depends_on"
		filter := LinkFilter{Type: &linkType}
		result, err := repo.List(ctx, filter)
		require.NoError(t, err)
		assert.GreaterOrEqual(t, len(result), 1)
	})

	t.Run("with limit and offset", func(t *testing.T) {
		filter := LinkFilter{Limit: 1, Offset: 1}
		result, err := repo.List(ctx, filter)
		require.NoError(t, err)
		assert.LessOrEqual(t, len(result), 1)
	})
}

func TestLinkRepositoryDeleteByItemID(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-del-1", SourceID: "item-del", TargetID: "other-1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-del-2", SourceID: "other-2", TargetID: "item-del", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-del-3", SourceID: "other-3", TargetID: "other-4", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}

	for _, link := range links {
		require.NoError(t, repo.Create(ctx, link))
	}

	t.Run("delete all links for item", func(t *testing.T) {
		err := repo.DeleteByItemID(ctx, "item-del")
		require.NoError(t, err)

		// Verify links are deleted
		result, err := repo.GetBySourceID(ctx, "item-del")
		require.NoError(t, err)
		assert.Empty(t, result)

		result, err = repo.GetByTargetID(ctx, "item-del")
		require.NoError(t, err)
		assert.Empty(t, result)

		// Other link should still exist
		link, err := repo.GetByID(ctx, "link-del-3")
		require.NoError(t, err)
		assert.NotNil(t, link)
	})
}

// Project Repository Tests

func TestProjectRepositoryCreate(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewProjectRepository(db)
	ctx := context.Background()

	t.Run("create project successfully", func(t *testing.T) {
		project := &models.Project{
			ID:          "proj-1",
			Name:        "Test Project",
			Description: "Test Description",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		err := repo.Create(ctx, project)
		require.NoError(t, err)
	})
}

func TestProjectRepositoryList(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewProjectRepository(db)
	ctx := context.Background()

	projects := []*models.Project{
		{ID: "proj-list-1", Name: "Project 1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "proj-list-2", Name: "Project 2", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}

	for _, proj := range projects {
		require.NoError(t, repo.Create(ctx, proj))
	}

	t.Run("list all projects", func(t *testing.T) {
		result, err := repo.List(ctx)
		require.NoError(t, err)
		assert.GreaterOrEqual(t, len(result), 2)
	})
}

// Agent Repository Tests

func TestAgentRepositoryCreate(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewAgentRepository(db)
	ctx := context.Background()

	t.Run("create agent successfully", func(t *testing.T) {
		agent := &models.Agent{
			ID:        "agent-1",
			ProjectID: testProjectID1,
			Name:      "Test Agent",
			Status:    "active",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, agent)
		require.NoError(t, err)
	})
}

func TestAgentRepositoryUpdateStatus(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewAgentRepository(db)
	ctx := context.Background()

	agent := &models.Agent{
		ID:        "agent-status",
		ProjectID: testProjectID1,
		Name:      "Status Agent",
		Status:    "idle",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, repo.Create(ctx, agent))

	t.Run("update agent status", func(t *testing.T) {
		err := repo.UpdateStatus(ctx, "agent-status", "active")
		require.NoError(t, err)

		updated, err := repo.GetByID(ctx, "agent-status")
		require.NoError(t, err)
		assert.Equal(t, "active", updated.Status)
	})
}

func TestAgentRepositoryGetByProjectID(t *testing.T) {
	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewAgentRepository(db)
	ctx := context.Background()

	agents := []*models.Agent{
		{ID: "agent-proj-1", ProjectID: "proj-x", Name: "Agent 1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "agent-proj-2", ProjectID: "proj-x", Name: "Agent 2", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "agent-proj-3", ProjectID: "proj-y", Name: "Agent 3", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}

	for _, agent := range agents {
		require.NoError(t, repo.Create(ctx, agent))
	}

	t.Run("get agents by project ID", func(t *testing.T) {
		result, err := repo.GetByProjectID(ctx, "proj-x")
		require.NoError(t, err)
		assert.Len(t, result, 2)
	})
}

// Concurrent Operations Tests

func TestConcurrentRepositoryOperations(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping concurrent test in short mode")
	}

	db := setupTestDB(t)
	defer cleanupDB(db)

	repo := NewItemRepository(db)
	ctx := context.Background()

	t.Run("concurrent creates", func(t *testing.T) {
		errChan := make(chan error, 10)

		for i := 0; i < 10; i++ {
			go func(id int) {
				item := &models.Item{
					ID:        "item-concurrent-" + string(rune(id)),
					ProjectID: "proj-concurrent",
					Title:     "Concurrent Test",
					CreatedAt: time.Now(),
					UpdatedAt: time.Now(),
				}
				errChan <- repo.Create(ctx, item)
			}(i)
		}

		for i := 0; i < 10; i++ {
			err := <-errChan
			require.NoError(t, err)
		}
	})
}
