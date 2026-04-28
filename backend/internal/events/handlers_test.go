package events

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// MockEventStore for testing
type MockEventStore struct {
	events    map[string][]*Event
	snapshots map[string]*Snapshot
}

func NewMockEventStore() *MockEventStore {
	return &MockEventStore{
		events:    make(map[string][]*Event),
		snapshots: make(map[string]*Snapshot),
	}
}

func (m *MockEventStore) Store(event *Event) error {
	if m.events[event.EntityID] == nil {
		m.events[event.EntityID] = make([]*Event, 0)
	}
	m.events[event.EntityID] = append(m.events[event.EntityID], event)
	return nil
}

func (m *MockEventStore) StoreMany(events []*Event) error {
	for _, event := range events {
		if err := m.Store(event); err != nil {
			return err
		}
	}
	return nil
}

func (m *MockEventStore) GetByEntityID(entityID string) ([]*Event, error) {
	if events, ok := m.events[entityID]; ok {
		return events, nil
	}
	return []*Event{}, nil
}

func (m *MockEventStore) GetByEntityIDAfterVersion(entityID string, version int64) ([]*Event, error) {
	allEvents, err := m.GetByEntityID(entityID)
	if err != nil {
		return nil, err
	}
	filtered := make([]*Event, 0)
	for _, e := range allEvents {
		if e.Version > version {
			filtered = append(filtered, e)
		}
	}
	return filtered, nil
}

func (m *MockEventStore) GetByProjectID(projectID string, _ int, _ int) ([]*Event, error) {
	result := make([]*Event, 0)
	for _, events := range m.events {
		for _, e := range events {
			if e.ProjectID == projectID {
				result = append(result, e)
			}
		}
	}
	return result, nil
}

func (m *MockEventStore) GetByProjectIDAndType(projectID string, entityType EntityType, _ int, _ int) ([]*Event, error) {
	result := make([]*Event, 0)
	for _, events := range m.events {
		for _, e := range events {
			if e.ProjectID == projectID && e.EntityType == entityType {
				result = append(result, e)
			}
		}
	}
	return result, nil
}

func (m *MockEventStore) GetByTimeRange(projectID string, start, end time.Time) ([]*Event, error) {
	result := make([]*Event, 0)
	for _, events := range m.events {
		for _, e := range events {
			if e.ProjectID == projectID && e.CreatedAt.After(start) && e.CreatedAt.Before(end) {
				result = append(result, e)
			}
		}
	}
	return result, nil
}

func (m *MockEventStore) SaveSnapshot(snapshot *Snapshot) error {
	m.snapshots[snapshot.EntityID] = snapshot
	return nil
}

func (m *MockEventStore) GetLatestSnapshot(entityID string) (*Snapshot, error) {
	if snapshot, ok := m.snapshots[entityID]; ok {
		return snapshot, nil
	}
	return nil, nil
}

func (m *MockEventStore) GetSnapshotAtVersion(entityID string, _ int64) (*Snapshot, error) {
	return m.GetLatestSnapshot(entityID)
}

func (m *MockEventStore) Replay(entityID string) (map[string]interface{}, error) {
	events, err := m.GetByEntityID(entityID)
	if err != nil {
		return nil, err
	}
	state := make(map[string]interface{})
	for _, e := range events {
		for k, v := range e.Data {
			state[k] = v
		}
	}
	return state, nil
}

func (m *MockEventStore) ReplayFromSnapshot(entityID string, _ int64) (map[string]interface{}, error) {
	return m.Replay(entityID)
}

func TestItemEventHandler_HandleCreate(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	item := &models.Item{
		ID:          uuid.New().String(),
		ProjectID:   uuid.New().String(),
		Title:       "Test Item",
		Description: "Test Description",
		Type:        "feature",
		Status:      "todo",
		Priority:    models.PriorityHigh,
	}

	correlationID := GenerateCorrelationID()
	event, err := handler.HandleCreate(context.Background(), item, "user-123", &correlationID)

	require.NoError(t, err)
	require.NotNil(t, event)
	assert.Equal(t, item.ID, event.EntityID)
	assert.Equal(t, item.ProjectID, event.ProjectID)
	assert.Equal(t, EntityTypeItem, event.EntityType)
	assert.Equal(t, EventTypeCreated, event.EventType)
	assert.Equal(t, item.Title, event.Data["title"])
	assert.Equal(t, "user-123", event.Metadata["user_id"])
	assert.NotNil(t, event.CorrelationID)
	assert.Equal(t, correlationID, *event.CorrelationID)
}

func TestItemEventHandler_HandleUpdate(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Title:     "Updated Title",
		Status:    "in_progress",
	}

	// Create initial event
	_, err := handler.HandleCreate(context.Background(), item, "user-123", nil)
	require.NoError(t, err)

	// Update
	item.Title = "New Title"
	correlationID := GenerateCorrelationID()
	event, err := handler.HandleUpdate(context.Background(), item, "user-456", &correlationID, nil)

	require.NoError(t, err)
	assert.Equal(t, EventTypeUpdated, event.EventType)
	assert.Equal(t, "New Title", event.Data["title"])
	assert.Equal(t, int64(2), event.Version) // Second event
	assert.Equal(t, "user-456", event.Metadata["user_id"])
}

func TestItemEventHandler_HandleStatusChange(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	itemID := uuid.New().String()
	projectID := uuid.New().String()

	event, err := handler.HandleStatusChange(context.Background(), itemID, projectID, "todo", "in_progress", "user-123", nil)

	require.NoError(t, err)
	assert.Equal(t, EventTypeItemStatusChanged, event.EventType)
	assert.Equal(t, "todo", event.Data["old_status"])
	assert.Equal(t, "in_progress", event.Data["new_status"])
}

func TestItemEventHandler_HandlePriorityChange(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	itemID := uuid.New().String()
	projectID := uuid.New().String()

	event, err := handler.HandlePriorityChange(context.Background(), itemID, projectID, int32(1), int32(3), "user-123", nil)

	require.NoError(t, err)
	assert.Equal(t, EventTypeItemPriorityChanged, event.EventType)
	assert.Equal(t, int32(1), event.Data["old_priority"])
	assert.Equal(t, int32(3), event.Data["new_priority"])
}

func TestItemEventHandler_HandleDelete(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	itemID := uuid.New().String()
	projectID := uuid.New().String()

	event, err := handler.HandleDelete(context.Background(), itemID, projectID, "user-123", nil)

	require.NoError(t, err)
	assert.Equal(t, EventTypeDeleted, event.EventType)
	assert.Equal(t, true, event.Data["deleted"])
}

func TestLinkEventHandler_HandleCreate(t *testing.T) {
	store := NewMockEventStore()
	handler := NewLinkEventHandler(store)

	link := &models.Link{
		ID:       uuid.New().String(),
		SourceID: uuid.New().String(),
		TargetID: uuid.New().String(),
		Type:     "depends_on",
	}

	projectID := uuid.New().String()
	event, err := handler.HandleCreate(context.Background(), link, projectID, "user-123", nil)

	require.NoError(t, err)
	assert.Equal(t, EntityTypeLink, event.EntityType)
	assert.Equal(t, EventTypeLinkCreated, event.EventType)
	assert.Equal(t, link.SourceID, event.Data["source_id"])
	assert.Equal(t, link.TargetID, event.Data["target_id"])
}

func TestLinkEventHandler_HandleDelete(t *testing.T) {
	store := NewMockEventStore()
	handler := NewLinkEventHandler(store)

	linkID := uuid.New().String()
	projectID := uuid.New().String()

	event, err := handler.HandleDelete(context.Background(), linkID, projectID, "user-123", nil)

	require.NoError(t, err)
	assert.Equal(t, EventTypeLinkDeleted, event.EventType)
}

func TestProjectEventHandler(t *testing.T) {
	store := NewMockEventStore()
	handler := NewProjectEventHandler(store)

	project := &models.Project{
		ID:          uuid.New().String(),
		Name:        "Test Project",
		Description: "Test Description",
	}

	// Test Create
	event, err := handler.HandleCreate(context.Background(), project, "user-123", nil)
	require.NoError(t, err)
	assert.Equal(t, EntityTypeProject, event.EntityType)
	assert.Equal(t, EventTypeCreated, event.EventType)

	// Test Update
	project.Name = "Updated Project"
	event, err = handler.HandleUpdate(context.Background(), project, "user-123", nil)
	require.NoError(t, err)
	assert.Equal(t, EventTypeUpdated, event.EventType)
	assert.Equal(t, int64(2), event.Version)

	// Test Delete
	event, err = handler.HandleDelete(context.Background(), project.ID, "user-123", nil)
	require.NoError(t, err)
	assert.Equal(t, EventTypeDeleted, event.EventType)
}

func TestAgentEventHandler(t *testing.T) {
	store := NewMockEventStore()
	handler := NewAgentEventHandler(store)

	agent := &models.Agent{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Name:      "Test Agent",
		Status:    "active",
	}

	// Test Create
	event, err := handler.HandleCreate(context.Background(), agent, "user-123", nil)
	require.NoError(t, err)
	assert.Equal(t, EntityTypeAgent, event.EntityType)
	assert.Equal(t, EventTypeCreated, event.EventType)

	// Test Start
	event, err = handler.HandleStart(context.Background(), agent.ID, agent.ProjectID, "user-123", nil)
	require.NoError(t, err)
	assert.Equal(t, EventTypeAgentStarted, event.EventType)

	// Test Activity
	metadata := map[string]interface{}{"task": "processing"}
	event, err = handler.HandleActivity(context.Background(), agent.ID, agent.ProjectID, "working", "user-123", metadata, nil)
	require.NoError(t, err)
	assert.Equal(t, EventTypeAgentActivity, event.EventType)
	assert.Equal(t, "working", event.Data["activity"])

	// Test Error
	event, err = handler.HandleError(context.Background(), agent.ID, agent.ProjectID, "connection failed", "user-123", nil)
	require.NoError(t, err)
	assert.Equal(t, EventTypeAgentError, event.EventType)
	assert.Equal(t, "connection failed", event.Data["error"])

	// Test Stop
	event, err = handler.HandleStop(context.Background(), agent.ID, agent.ProjectID, "user-123", nil)
	require.NoError(t, err)
	assert.Equal(t, EventTypeAgentStopped, event.EventType)
}

func TestReconstructItemFromEvents(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	item := &models.Item{
		ID:          uuid.New().String(),
		ProjectID:   uuid.New().String(),
		Title:       "Initial Title",
		Description: "Initial Description",
		Type:        "feature",
		Status:      "todo",
		Priority:    models.PriorityLow,
	}

	// Create initial item
	_, err := handler.HandleCreate(context.Background(), item, "user-123", nil)
	require.NoError(t, err)

	// Update item
	item.Title = "Updated Title"
	item.Status = "in_progress"
	_, err = handler.HandleUpdate(context.Background(), item, "user-123", nil, nil)
	require.NoError(t, err)

	// Change status
	_, err = handler.HandleStatusChange(context.Background(), item.ID, item.ProjectID, "in_progress", "done", "user-123", nil)
	require.NoError(t, err)

	// Reconstruct
	reconstructed, err := ReconstructItemFromEvents(item.ID, store)
	require.NoError(t, err)
	assert.Equal(t, "Updated Title", reconstructed.Title)
	assert.Equal(t, "done", reconstructed.Status)
	assert.Equal(t, item.ProjectID, reconstructed.ProjectID)
}

func TestGenerateCorrelationID(t *testing.T) {
	id1 := GenerateCorrelationID()
	id2 := GenerateCorrelationID()

	assert.NotEmpty(t, id1)
	assert.NotEmpty(t, id2)
	assert.NotEqual(t, id1, id2)
}

func TestEventVersioning(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Title:     "Test",
	}

	// Create multiple events
	_, err := handler.HandleCreate(context.Background(), item, "user-123", nil)
	require.NoError(t, err)
	_, err = handler.HandleUpdate(context.Background(), item, "user-123", nil, nil)
	require.NoError(t, err)
	_, err = handler.HandleUpdate(context.Background(), item, "user-123", nil, nil)
	require.NoError(t, err)

	events, err := store.GetByEntityID(item.ID)
	require.NoError(t, err)
	require.Len(t, events, 3)
	assert.Equal(t, int64(1), events[0].Version)
	assert.Equal(t, int64(2), events[1].Version)
	assert.Equal(t, int64(3), events[2].Version)
}

func TestEventCausation(t *testing.T) {
	store := NewMockEventStore()
	handler := NewItemEventHandler(store)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Title:     "Test",
	}

	// Create event
	createEvent, err := handler.HandleCreate(context.Background(), item, "user-123", nil)
	require.NoError(t, err)

	// Update with causation
	causationID := createEvent.ID
	updateEvent, err := handler.HandleUpdate(context.Background(), item, "user-123", nil, &causationID)
	require.NoError(t, err)

	assert.NotNil(t, updateEvent.CausationID)
	assert.Equal(t, createEvent.ID, *updateEvent.CausationID)
}

func TestEventCorrelation(t *testing.T) {
	store := NewMockEventStore()
	itemHandler := NewItemEventHandler(store)
	linkHandler := NewLinkEventHandler(store)

	correlationID := GenerateCorrelationID()

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Title:     "Test",
	}

	link := &models.Link{
		ID:       uuid.New().String(),
		SourceID: item.ID,
		TargetID: uuid.New().String(),
		Type:     "depends_on",
	}

	// Create item and link with same correlation ID
	itemEvent, err := itemHandler.HandleCreate(context.Background(), item, "user-123", &correlationID)
	require.NoError(t, err)
	linkEvent, err := linkHandler.HandleCreate(context.Background(), link, item.ProjectID, "user-123", &correlationID)
	require.NoError(t, err)

	assert.Equal(t, *itemEvent.CorrelationID, *linkEvent.CorrelationID)
	assert.Equal(t, correlationID, *itemEvent.CorrelationID)
}
