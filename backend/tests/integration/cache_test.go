//go:build integration

package integration

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestServiceIntegration_Cache_ItemRetrieval(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Cache Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Cached Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	retrieved1, err := f.itemService.GetItem(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved1)

	retrieved2, err := f.itemService.GetItem(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved2)
	assert.Equal(t, retrieved1.Title, retrieved2.Title)

	mockCache := f.cache.(*mockCache)
	cacheKey := "item:" + item.ID
	assert.True(t, mockCache.HasKey(cacheKey))
}

func TestServiceIntegration_Cache_InvalidateOnUpdate(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Cache Invalidation Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Original Title",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	_, err := f.itemService.GetItem(f.ctx, item.ID)
	require.NoError(t, err)

	mockCache := f.cache.(*mockCache)
	cacheKey := "item:" + item.ID
	assert.True(t, mockCache.HasKey(cacheKey))

	item.Title = "Updated Title"
	err = f.itemService.UpdateItem(f.ctx, item)
	assert.NoError(t, err)

	assert.False(t, mockCache.HasKey(cacheKey))
}

func TestServiceIntegration_Cache_InvalidateRelated(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Related Cache Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Test Item",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	stats, err := f.itemService.GetItemStats(f.ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, int64(1), stats.TotalItems)

	mockCache := f.cache.(*mockCache)
	statsKey := "project:" + project.ID + ":stats"
	assert.True(t, mockCache.HasKey(statsKey))

	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Second Item",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err = f.itemService.CreateItem(f.ctx, item2)
	assert.NoError(t, err)

	assert.False(t, mockCache.HasKey(statsKey))
}

func TestServiceIntegration_Cache_ConcurrentAccess(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Concurrent Cache Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Concurrent Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	numReads := 20
	done := make(chan bool, numReads)
	errChan := make(chan error, numReads)

	for i := 0; i < numReads; i++ {
		go func() {
			_, err := f.itemService.GetItem(f.ctx, item.ID)
			if err != nil {
				errChan <- err
			}
			done <- true
		}()
	}

	for i := 0; i < numReads; i++ {
		<-done
	}
	close(errChan)

	for err := range errChan {
		assert.NoError(t, err)
	}
}

func TestServiceIntegration_Cache_TTL(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "TTL Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "TTL Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	_, err := f.itemService.GetItem(f.ctx, item.ID)
	assert.NoError(t, err)

	mockCache := f.cache.(*mockCache)
	cacheKey := "item:" + item.ID
	assert.True(t, mockCache.HasKey(cacheKey))
}
