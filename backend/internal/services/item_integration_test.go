//go:build integration
// +build integration

package services

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// TestPhase7ItemRepositoryCreate tests creating items through the repository
func TestPhase7ItemRepositoryCreate(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create a project first
	project := &models.Project{
		Name:        "Test Project",
		Description: "A test project for Phase 7",
	}

	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)
	require.NotEmpty(t, project.ID)

	// Create an item
	item := &models.Item{
		ProjectID:   project.ID,
		Title:       "Test Item",
		Description: "A test item",
		Type:        "task",
		Status:      "open",
		Priority:    models.PriorityHigh,
	}

	err = helper.ItemRepo.Create(ctx, item)
	require.NoError(t, err)
	require.NotEmpty(t, item.ID)
	assert.Equal(t, project.ID, item.ProjectID)
	assert.Equal(t, "Test Item", item.Title)
}

// TestPhase7ItemRepositoryGetByID tests retrieving items by ID
func TestPhase7ItemRepositoryGetByID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project and item
	project := &models.Project{Name: "Test Project"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	originalItem := &models.Item{
		ProjectID: project.ID,
		Title:     "Original Item",
		Type:      "feature",
		Status:    "in-progress",
	}
	err = helper.ItemRepo.Create(ctx, originalItem)
	require.NoError(t, err)

	// Test: Retrieve the item
	retrievedItem, err := helper.ItemRepo.GetByID(ctx, originalItem.ID)
	require.NoError(t, err)
	require.NotNil(t, retrievedItem)
	assert.Equal(t, originalItem.ID, retrievedItem.ID)
	assert.Equal(t, originalItem.Title, retrievedItem.Title)
	assert.Equal(t, originalItem.ProjectID, retrievedItem.ProjectID)
}

// TestPhase7ItemRepositoryGetByProjectID tests retrieving items by project
func TestPhase7ItemRepositoryGetByProjectID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project and multiple items
	project := &models.Project{Name: "Multi-Item Project"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	items := []*models.Item{
		{ProjectID: project.ID, Title: "Item 1", Type: "task"},
		{ProjectID: project.ID, Title: "Item 2", Type: "bug"},
		{ProjectID: project.ID, Title: "Item 3", Type: "feature"},
	}

	for _, item := range items {
		err := helper.ItemRepo.Create(ctx, item)
		require.NoError(t, err)
	}

	// Test: Retrieve all items for project
	projectItems, err := helper.ItemRepo.GetByProjectID(ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, 3, len(projectItems))

	// Verify all items belong to the project
	for _, item := range projectItems {
		assert.Equal(t, project.ID, item.ProjectID)
	}
}

// TestPhase7ItemRepositoryUpdate tests updating items
func TestPhase7ItemRepositoryUpdate(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Update Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	item := &models.Item{
		ProjectID: project.ID,
		Title:     "Original Title",
		Status:    "open",
	}
	err = helper.ItemRepo.Create(ctx, item)
	require.NoError(t, err)

	originalID := item.ID
	originalCreatedAt := item.CreatedAt

	// Modify and update
	item.Title = "Updated Title"
	item.Status = "closed"

	err = helper.ItemRepo.Update(ctx, item)
	require.NoError(t, err)

	// Verify
	updated, err := helper.ItemRepo.GetByID(ctx, originalID)
	require.NoError(t, err)
	assert.Equal(t, "Updated Title", updated.Title)
	assert.Equal(t, "closed", updated.Status)
	assert.Equal(t, originalCreatedAt, updated.CreatedAt)
	assert.True(t, updated.UpdatedAt.After(originalCreatedAt))
}

// TestPhase7ItemRepositoryDelete tests soft deleting items
func TestPhase7ItemRepositoryDelete(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Delete Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	item := &models.Item{
		ProjectID: project.ID,
		Title:     "To Delete",
	}
	err = helper.ItemRepo.Create(ctx, item)
	require.NoError(t, err)

	itemID := item.ID

	// Delete
	err = helper.ItemRepo.Delete(ctx, itemID)
	require.NoError(t, err)

	// Verify item is not returned
	deleted, err := helper.ItemRepo.GetByID(ctx, itemID)
	assert.Error(t, err)
	assert.Nil(t, deleted)
}

// TestPhase7ItemRepositoryCount tests counting items
func TestPhase7ItemRepositoryCount(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Count Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create items
	for i := 0; i < 5; i++ {
		item := &models.Item{
			ProjectID: project.ID,
			Title:     "Item " + string(rune(i)),
			Type:      "task",
		}
		err := helper.ItemRepo.Create(ctx, item)
		require.NoError(t, err)
	}

	// Test: Count with filter
	count, err := helper.ItemRepo.Count(ctx, NewItemFilter(project.ID, nil, nil, nil))
	require.NoError(t, err)
	assert.Equal(t, int64(5), count)
}

// Helper to create ItemFilter
func NewItemFilter(projectID string, itemType, status, priority *string) ItemFilter {
	filter := ItemFilter{
		ProjectID: &projectID,
		Limit:     100,
		Offset:    0,
	}
	if itemType != nil {
		filter.Type = itemType
	}
	if status != nil {
		filter.Status = status
	}
	if priority != nil {
		filter.Priority = priority
	}
	return filter
}

// TestPhase7ItemServiceWithRepository tests the service using the repository
func TestPhase7ItemServiceWithRepository(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create a mock Redis client (nil for now, graceful degradation)
	var redisClient interface{} = nil

	// Create service with real repository
	service := NewItemService(helper.ItemRepo, redisClient)

	// Setup
	project := &models.Project{Name: "Service Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Test: Service creation
	item := &models.Item{
		ProjectID: project.ID,
		Title:     "Service Item",
		Type:      "feature",
		Status:    "open",
	}

	err = service.Create(ctx, item)
	require.NoError(t, err)
	require.NotEmpty(t, item.ID)

	// Test: Service retrieval
	retrieved, err := service.GetItem(ctx, item.ID)
	require.NoError(t, err)
	assert.NotNil(t, retrieved)
	assert.Equal(t, item.Title, retrieved.Title)
}

// TestPhase7ItemRepositoryTransactionBehavior tests repository behavior with multiple operations
func TestPhase7ItemRepositoryTransactionBehavior(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create two projects
	project1 := &models.Project{Name: "Project 1"}
	project2 := &models.Project{Name: "Project 2"}

	err := helper.ProjectRepo.Create(ctx, project1)
	require.NoError(t, err)
	err = helper.ProjectRepo.Create(ctx, project2)
	require.NoError(t, err)

	// Create items in both projects
	item1 := &models.Item{ProjectID: project1.ID, Title: "P1 Item"}
	item2 := &models.Item{ProjectID: project2.ID, Title: "P2 Item"}

	err = helper.ItemRepo.Create(ctx, item1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, item2)
	require.NoError(t, err)

	// Verify items are in correct projects
	p1Items, err := helper.ItemRepo.GetByProjectID(ctx, project1.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(p1Items))
	assert.Equal(t, item1.ID, p1Items[0].ID)

	p2Items, err := helper.ItemRepo.GetByProjectID(ctx, project2.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(p2Items))
	assert.Equal(t, item2.ID, p2Items[0].ID)
}

// TestPhase7ItemRepositoryTimestampHandling tests timestamp handling
func TestPhase7ItemRepositoryTimestampHandling(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Timestamp Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	beforeCreate := time.Now().UTC()

	// Create
	item := &models.Item{
		ProjectID: project.ID,
		Title:     "Timestamp Item",
	}
	err = helper.ItemRepo.Create(ctx, item)
	require.NoError(t, err)

	afterCreate := time.Now().UTC()

	// Verify timestamps
	assert.True(t, item.CreatedAt.After(beforeCreate.Add(-time.Second)))
	assert.True(t, item.CreatedAt.Before(afterCreate.Add(time.Second)))
	assert.Equal(t, item.CreatedAt, item.UpdatedAt)
	assert.Nil(t, item.DeletedAt)
}
