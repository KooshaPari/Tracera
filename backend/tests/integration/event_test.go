//go:build integration

package integration

import (
	"encoding/json"
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestServiceIntegration_Events_ItemCreated(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)
	mockNATS.ClearEvents()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Event Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err := f.itemService.CreateItem(f.ctx, item)
	assert.NoError(t, err)

	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	var createdEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.created" {
			createdEvent = e
			break
		}
	}
	assert.NotNil(t, createdEvent)
}

func TestServiceIntegration_Events_ItemUpdated(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Update Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Original",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	mockNATS.ClearEvents()

	item.Title = "Updated"
	err := f.itemService.UpdateItem(f.ctx, item)
	assert.NoError(t, err)

	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	var updatedEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.updated" {
			updatedEvent = e
			break
		}
	}
	assert.NotNil(t, updatedEvent)
}

func TestServiceIntegration_Events_ItemDeleted(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Delete Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "To Delete",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	mockNATS.ClearEvents()

	err := f.itemService.DeleteItem(f.ctx, item.ID)
	assert.NoError(t, err)

	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	var deletedEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.deleted" {
			deletedEvent = e
			break
		}
	}
	assert.NotNil(t, deletedEvent)
}

func TestServiceIntegration_Events_BatchOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)
	mockNATS.ClearEvents()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Batch Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	items := make([]*models.Item, 3)
	for i := 0; i < 3; i++ {
		items[i] = &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Batch Item %d", i),
			Type:      "task",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
	}

	err := f.itemService.CreateBatch(f.ctx, items)
	assert.NoError(t, err)

	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	var batchEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.batch_created" {
			batchEvent = e
			break
		}
	}
	assert.NotNil(t, batchEvent)

	var eventData map[string]interface{}
	err = json.Unmarshal(batchEvent.Data, &eventData)
	assert.NoError(t, err)

	data, ok := eventData["data"].(map[string]interface{})
	assert.True(t, ok)
	count, ok := data["count"].(float64)
	assert.True(t, ok)
	assert.Equal(t, float64(3), count)
}

func TestServiceIntegration_Events_Metadata(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)
	mockNATS.ClearEvents()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Metadata Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Metadata Item",
		Type:      "task",
		Status:    "todo",
		Priority:  models.PriorityHigh,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err := f.itemService.CreateItem(f.ctx, item)
	assert.NoError(t, err)

	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	event := events[len(events)-1]
	var eventData map[string]interface{}
	err = json.Unmarshal(event.Data, &eventData)
	assert.NoError(t, err)

	assert.Contains(t, eventData, "type")
	assert.Contains(t, eventData, "data")
	assert.Contains(t, eventData, "timestamp")
}
