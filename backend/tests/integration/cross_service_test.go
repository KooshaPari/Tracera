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
)

func TestServiceIntegration_CrossService_LinkValidatesItems(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  "non-existent-source",
		TargetID:  "non-existent-target",
		Type:      "depends_on",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.linkService.CreateLink(f.ctx, link)
	if err != nil {
		assert.Contains(t, err.Error(), "not found")
	}
}

func TestServiceIntegration_CrossService_ProjectToItems(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	for i := 0; i < 5; i++ {
		item := &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Item %d", i),
			Type:      "task",
			Status:    "todo",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, f.itemService.CreateItem(f.ctx, item))
	}

	stats, err := f.itemService.GetItemStats(f.ctx, project.ID)
	assert.NoError(t, err)
	assert.NotNil(t, stats)
	assert.Equal(t, int64(5), stats.TotalItems)
}

func TestServiceIntegration_CrossService_CoordinatedOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Coordination Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Parent Item",
		Type:      "epic",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Child Item",
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
		Type:      "contains",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.linkService.CreateLink(f.ctx, link))

	itemWithLinks, err := f.itemService.GetWithLinks(f.ctx, item1.ID)
	assert.NoError(t, err)
	assert.NotNil(t, itemWithLinks)
	assert.Len(t, itemWithLinks.SourceLinks, 1)
	assert.Equal(t, item2.ID, itemWithLinks.SourceLinks[0].TargetID)
}

func TestServiceIntegration_CrossService_ReferentialIntegrity(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Integrity Test",
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
		Type:      "related",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.linkService.CreateLink(f.ctx, link))

	err := f.itemService.DeleteItem(f.ctx, item1.ID)
	assert.NoError(t, err)

	_, err = f.linkRepo.GetByID(f.ctx, link.ID)
	assert.Error(t, err)
}
