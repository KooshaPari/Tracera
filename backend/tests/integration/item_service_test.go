//go:build integration

package integration

import (
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

func TestServiceIntegration_CreateItem_DatabasePersistence(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:          uuid.New().String(),
		Name:        "Test Project",
		Description: "Integration test project",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	err := f.projectRepo.Create(f.ctx, project)
	require.NoError(t, err)

	item := &models.Item{
		ID:          uuid.New().String(),
		ProjectID:   project.ID,
		Title:       "Test Item",
		Description: "Integration test item",
		Type:        "task",
		Status:      "todo",
		Priority:    models.PriorityMedium,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	err = f.itemService.CreateItem(f.ctx, item)
	assert.NoError(t, err, "Should create item successfully")

	retrieved, err := f.itemRepo.GetByID(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)
	assert.Equal(t, item.Title, retrieved.Title)
	assert.Equal(t, item.ProjectID, retrieved.ProjectID)
	assert.Equal(t, "task", retrieved.Type)
}

func TestServiceIntegration_UpdateItem_DatabaseValidation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Original Title",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	item.Title = "Updated Title"
	item.Status = "in_progress"
	item.UpdatedAt = time.Now()

	err := f.itemService.UpdateItem(f.ctx, item)
	assert.NoError(t, err)

	updated, err := f.itemRepo.GetByID(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.Equal(t, "Updated Title", updated.Title)
	assert.Equal(t, "in_progress", updated.Status)
}

func TestServiceIntegration_DeleteItem_CascadesToLinks(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item1))
	require.NoError(t, f.itemService.CreateItem(f.ctx, item2))

	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  item1.ID,
		TargetID:  item2.ID,
		Type:      "depends_on",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.linkService.CreateLink(f.ctx, link))

	err := f.itemService.DeleteItem(f.ctx, item1.ID)
	assert.NoError(t, err)

	_, err = f.itemRepo.GetByID(f.ctx, item1.ID)
	assert.Error(t, err)

	_, err = f.linkRepo.GetByID(f.ctx, link.ID)
	assert.Error(t, err)

	retrieved, err := f.itemRepo.GetByID(f.ctx, item2.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)
}

func TestServiceIntegration_ConcurrentOperations_DatabaseConsistency(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Concurrent Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	numItems := 10
	done := make(chan bool, numItems)
	errChan := make(chan error, numItems)

	for i := 0; i < numItems; i++ {
		go func(idx int) {
			item := &models.Item{
				ID:        uuid.New().String(),
				ProjectID: project.ID,
				Title:     fmt.Sprintf("Concurrent Item %d", idx),
				Type:      "task",
				Status:    "todo",
				CreatedAt: time.Now(),
				UpdatedAt: time.Now(),
			}
			if err := f.itemService.CreateItem(f.ctx, item); err != nil {
				errChan <- err
			}
			done <- true
		}(i)
	}

	for i := 0; i < numItems; i++ {
		<-done
	}
	close(errChan)

	for err := range errChan {
		assert.NoError(t, err)
	}

	filter := repository.ItemFilter{ProjectID: &project.ID}
	items, err := f.itemRepo.List(f.ctx, filter)
	assert.NoError(t, err)
	assert.Equal(t, numItems, len(items))
}

func TestServiceIntegration_Validation_BeforeDatabaseOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	invalidItem := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: "",
		Title:     "",
		Type:      "invalid_type",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemService.CreateItem(f.ctx, invalidItem)
	assert.Error(t, err, "Should reject invalid item")
	assert.Contains(t, err.Error(), "validation failed")

	_, err = f.itemRepo.GetByID(f.ctx, invalidItem.ID)
	assert.Error(t, err)
}

func TestServiceIntegration_CrossService_ItemToLink(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Test Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	itemWithLinks, err := f.itemService.GetWithLinks(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, itemWithLinks)
	assert.Equal(t, item.ID, itemWithLinks.Item.ID)
	assert.NotNil(t, itemWithLinks.SourceLinks)
	assert.NotNil(t, itemWithLinks.TargetLinks)
}
