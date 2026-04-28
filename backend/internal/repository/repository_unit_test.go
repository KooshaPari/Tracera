//go:build !integration && !e2e

package repository

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// setupTestDBUnit creates an in-memory SQLite database for unit testing
func setupTestDBUnit(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	require.NoError(t, err)

	// Auto migrate models
	err = db.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{}, &models.Agent{})
	require.NoError(t, err)

	return db
}

func TestItemRepository_Create(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewItemRepository(db)
	ctx := context.Background()

	t.Run("success", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-1",
			ProjectID: "proj-1",
			Title:     "Test Item",
			Type:      "task",
			Status:    "open",
			Priority:  models.PriorityHigh,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, item)
		require.NoError(t, err)
		assert.NotEmpty(t, item.ID)
	})

	t.Run("duplicate ID fails", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-dup",
			ProjectID: "proj-1",
			Title:     "Duplicate",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, item)
		require.NoError(t, err)

		// Try to create again
		err = repo.Create(ctx, item)
		require.Error(t, err)
	})
}

func TestItemRepository_GetByID(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewItemRepository(db)
	ctx := context.Background()

	// Create test item
	testItem := &models.Item{
		ID:        "item-get",
		ProjectID: "proj-1",
		Title:     "Get Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, repo.Create(ctx, testItem))

	t.Run("get existing item", func(t *testing.T) {
		item, err := repo.GetByID(ctx, "item-get")
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

	t.Run("get deleted item", func(t *testing.T) {
		deletedItem := &models.Item{
			ID:        "item-deleted",
			ProjectID: "proj-1",
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

func seedUnitListItems(ctx context.Context, t *testing.T, repo ItemRepository) {
	t.Helper()
	items := []*models.Item{
		{
			ID:        "item-1",
			ProjectID: "proj-1",
			Title:     "Item 1",
			Type:      "task",
			Status:    "open",
			Priority:  models.PriorityHigh,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
		{
			ID:        "item-2",
			ProjectID: "proj-1",
			Title:     "Item 2",
			Type:      "bug",
			Status:    "closed",
			Priority:  models.PriorityLow,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
		{
			ID:        "item-3",
			ProjectID: "proj-2",
			Title:     "Item 3",
			Type:      "task",
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

func runUnitListCase(
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

func unitFilterByProjectID(projectID string) ItemFilter {
	return ItemFilter{ProjectID: &projectID}
}

func unitFilterByType(itemType string) ItemFilter {
	return ItemFilter{Type: &itemType}
}

func unitFilterByStatus(status string) ItemFilter {
	return ItemFilter{Status: &status}
}

func unitFilterByPriority(priority models.Priority) ItemFilter {
	return ItemFilter{Priority: &priority}
}

func unitFilterByProjectAndType(projectID string, itemType string) ItemFilter {
	return ItemFilter{ProjectID: &projectID, Type: &itemType}
}

func TestItemRepository_List(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewItemRepository(db)
	ctx := context.Background()

	seedUnitListItems(ctx, t, repo)

	runUnitListCase(ctx, t, "list all items", repo, ItemFilter{}, func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 3)
	})
	runUnitListCase(ctx, t, "filter by project ID", repo, unitFilterByProjectID("proj-1"), func(t *testing.T, result []*models.Item) {
		assert.Len(t, result, 2)
	})
	runUnitListCase(ctx, t, "filter by type", repo, unitFilterByType("task"), func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 2)
	})
	runUnitListCase(ctx, t, "filter by status", repo, unitFilterByStatus("open"), func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 2)
	})
	highPrioFilter := unitFilterByPriority(models.PriorityHigh)
	runUnitListCase(ctx, t, "filter by priority", repo, highPrioFilter, func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 1)
	})
	runUnitListCase(ctx, t, "with limit", repo, ItemFilter{Limit: 2}, func(t *testing.T, result []*models.Item) {
		assert.LessOrEqual(t, len(result), 2)
	})
	runUnitListCase(ctx, t, "with offset", repo, ItemFilter{Offset: 1}, func(t *testing.T, result []*models.Item) {
		assert.GreaterOrEqual(t, len(result), 2)
	})
	combinedFilter := unitFilterByProjectAndType("proj-1", "task")
	runUnitListCase(ctx, t, "combined filters", repo, combinedFilter, func(t *testing.T, result []*models.Item) {
		assert.Len(t, result, 1)
	})
}

func TestItemRepository_Update(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewItemRepository(db)
	ctx := context.Background()

	t.Run("update item successfully", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-update",
			ProjectID: "proj-1",
			Title:     "Original",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, repo.Create(ctx, item))

		item.Title = "Updated"
		err := repo.Update(ctx, item)
		require.NoError(t, err)

		updated, err := repo.GetByID(ctx, "item-update")
		require.NoError(t, err)
		assert.Equal(t, "Updated", updated.Title)
	})
}

func TestItemRepository_Delete(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewItemRepository(db)
	ctx := context.Background()

	t.Run("soft delete item", func(t *testing.T) {
		item := &models.Item{
			ID:        "item-del",
			ProjectID: "proj-1",
			Title:     "To Delete",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, repo.Create(ctx, item))

		err := repo.Delete(ctx, "item-del")
		require.NoError(t, err)

		// Should not be found
		_, err = repo.GetByID(ctx, "item-del")
		require.Error(t, err)
	})
}

func TestItemRepository_Count(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewItemRepository(db)
	ctx := context.Background()

	// Create test items
	for i := 0; i < 5; i++ {
		item := &models.Item{
			ID:        "item-count-" + string(rune(i+48)),
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

func TestLinkRepository_Create(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewLinkRepository(db)
	ctx := context.Background()

	t.Run("success", func(t *testing.T) {
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
}

func TestLinkRepository_GetByID(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewLinkRepository(db)
	ctx := context.Background()

	testLink := &models.Link{
		ID:        "link-get",
		SourceID:  "item-1",
		TargetID:  "item-2",
		Type:      "blocks",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, repo.Create(ctx, testLink))

	t.Run("get existing link", func(t *testing.T) {
		link, err := repo.GetByID(ctx, "link-get")
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

func TestLinkRepository_GetBySourceID(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-1", SourceID: "source-1", TargetID: "target-1", Type: "depends_on", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-2", SourceID: "source-1", TargetID: "target-2", Type: "blocks", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-3", SourceID: "source-2", TargetID: "target-3", Type: "related", CreatedAt: time.Now(), UpdatedAt: time.Now()},
	}

	for _, link := range links {
		require.NoError(t, repo.Create(ctx, link))
	}

	t.Run("get links by source ID", func(t *testing.T) {
		result, err := repo.GetBySourceID(ctx, "source-1")
		require.NoError(t, err)
		assert.Len(t, result, 2)
	})
}

func TestLinkRepository_GetByTargetID(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-1", SourceID: "source-1", TargetID: "target-1", Type: "depends_on", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-2", SourceID: "source-2", TargetID: "target-1", Type: "blocks", CreatedAt: time.Now(), UpdatedAt: time.Now()},
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

func TestLinkRepository_List(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-1", SourceID: "s1", TargetID: "t1", Type: "depends_on", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-2", SourceID: "s2", TargetID: "t2", Type: "blocks", CreatedAt: time.Now(), UpdatedAt: time.Now()},
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
}

func TestLinkRepository_DeleteByItemID(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewLinkRepository(db)
	ctx := context.Background()

	links := []*models.Link{
		{ID: "link-1", SourceID: "item-del", TargetID: "other-1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-2", SourceID: "other-2", TargetID: "item-del", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "link-3", SourceID: "other-3", TargetID: "other-4", CreatedAt: time.Now(), UpdatedAt: time.Now()},
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
		link, err := repo.GetByID(ctx, "link-3")
		require.NoError(t, err)
		assert.NotNil(t, link)
	})
}

func TestProjectRepository_Create(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewProjectRepository(db)
	ctx := context.Background()

	t.Run("success", func(t *testing.T) {
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

func TestProjectRepository_List(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewProjectRepository(db)
	ctx := context.Background()

	projects := []*models.Project{
		{ID: "proj-1", Name: "Project 1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "proj-2", Name: "Project 2", CreatedAt: time.Now(), UpdatedAt: time.Now()},
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

func TestAgentRepository_Create(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewAgentRepository(db)
	ctx := context.Background()

	t.Run("success", func(t *testing.T) {
		agent := &models.Agent{
			ID:        "agent-1",
			ProjectID: "proj-1",
			Name:      "Test Agent",
			Status:    "active",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		err := repo.Create(ctx, agent)
		require.NoError(t, err)
	})
}

func TestAgentRepository_UpdateStatus(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewAgentRepository(db)
	ctx := context.Background()

	agent := &models.Agent{
		ID:        "agent-status",
		ProjectID: "proj-1",
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

func TestAgentRepository_GetByProjectID(t *testing.T) {
	db := setupTestDBUnit(t)
	repo := NewAgentRepository(db)
	ctx := context.Background()

	agents := []*models.Agent{
		{ID: "agent-1", ProjectID: "proj-x", Name: "Agent 1", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "agent-2", ProjectID: "proj-x", Name: "Agent 2", CreatedAt: time.Now(), UpdatedAt: time.Now()},
		{ID: "agent-3", ProjectID: "proj-y", Name: "Agent 3", CreatedAt: time.Now(), UpdatedAt: time.Now()},
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
