package events

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	eventReplayShortDelay   = 10 * time.Millisecond
	eventReplayLongOffset   = 1 * time.Hour
	eventReplayMediumOffset = 30 * time.Minute
)

func TestEventReplayService_ReplayToTimestamp(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	now := time.Now()

	// Create events at different times
	event1 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title": "Version 1",
		"count": 1,
	})
	event1.CreatedAt = now.Add(-eventReplayLongOffset)
	event1.Version = 1
	require.NoError(t, store.Store(event1))

	event2 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
		"title": "Version 2",
		"count": 2,
	})
	event2.CreatedAt = now.Add(-eventReplayMediumOffset)
	event2.Version = 2
	require.NoError(t, store.Store(event2))

	event3 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
		"count": 3,
	})
	event3.CreatedAt = now.Add(-10 * time.Minute)
	event3.Version = 3
	require.NoError(t, store.Store(event3))

	// Replay to a point between event2 and event3
	result, err := service.ReplayToTimestamp(context.Background(), entityID, now.Add(-20*time.Minute))

	require.NoError(t, err)
	assert.Equal(t, entityID, result.EntityID)
	assert.Equal(t, "Version 2", result.State["title"])
	assert.Equal(t, 2, result.State["count"])
	assert.Equal(t, int64(2), result.Version)
	assert.Len(t, result.EventIDs, 2)
}

func TestEventReplayService_ReplayToVersion(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	// Create multiple events
	for i := 1; i <= 5; i++ {
		event := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
			"version": i,
			"title":   "Version " + string(rune('0'+i)),
		})
		event.Version = int64(i)
		require.NoError(t, store.Store(event))
	}

	// Replay to version 3
	result, err := service.ReplayToVersion(context.Background(), entityID, 3)

	require.NoError(t, err)
	assert.Equal(t, int64(3), result.Version)
	assert.Equal(t, 3, result.State["version"])
	assert.Len(t, result.EventIDs, 3)
}

func TestEventReplayService_GetCurrentState(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	// Create events
	event1 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title": "Initial",
	})
	event1.Version = 1
	require.NoError(t, store.Store(event1))

	event2 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
		"title": "Final",
		"done":  true,
	})
	event2.Version = 2
	require.NoError(t, store.Store(event2))

	result, err := service.GetCurrentState(context.Background(), entityID)

	require.NoError(t, err)
	assert.Equal(t, "Final", result.State["title"])
	assert.Equal(t, true, result.State["done"])
	assert.Equal(t, int64(2), result.Version)
	assert.Len(t, result.EventIDs, 2)
}

func TestEventReplayService_GetStateAtMultiplePoints(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	now := time.Now()

	// Create events at hourly intervals
	for i := 0; i < 5; i++ {
		event := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
			"hour": i,
		})
		event.CreatedAt = now.Add(time.Duration(-4+i) * time.Hour)
		event.Version = int64(i + 1)
		require.NoError(t, store.Store(event))
	}

	// Query at multiple points
	timestamps := []time.Time{
		now.Add(-3*time.Hour - 30*time.Minute),
		now.Add(-2*time.Hour - 30*time.Minute),
		now.Add(-1*time.Hour - 30*time.Minute),
	}

	results, err := service.GetStateAtMultiplePoints(context.Background(), entityID, timestamps)

	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
}

func TestEventReplayService_CompareVersions(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	// Version 1: Create with initial data
	event1 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title":       "Initial",
		"description": "Test",
		"count":       1,
	})
	event1.Version = 1
	require.NoError(t, store.Store(event1))

	// Version 2: Update some fields
	event2 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
		"title":    "Updated",
		"count":    2,
		"newfield": "added",
	})
	event2.Version = 2
	require.NoError(t, store.Store(event2))

	comparison, err := service.CompareVersions(context.Background(), entityID, 1, 2)

	require.NoError(t, err)
	assert.Equal(t, int64(1), comparison.FromVersion)
	assert.Equal(t, int64(2), comparison.ToVersion)

	// Check modified fields
	assert.Contains(t, comparison.ModifiedFields, "title")
	assert.Contains(t, comparison.ModifiedFields, "count")

	// Check added fields
	assert.Contains(t, comparison.AddedFields, "newfield")

	// Description should be unchanged
	assert.Equal(t, 1, comparison.UnchangedCount)
}

func TestEventReplayService_GetEventChain(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	projectID := uuid.New().String()

	// Create a chain of events
	event1 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
	event1.Version = 1
	require.NoError(t, store.Store(event1))

	event2 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeUpdated, nil)
	event2.Version = 1
	event2.WithCausation(event1.ID)
	require.NoError(t, store.Store(event2))

	event3 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeUpdated, nil)
	event3.Version = 1
	event3.WithCausation(event2.ID)
	require.NoError(t, store.Store(event3))

	// Get the chain starting from event3
	chain, err := service.GetEventChain(context.Background(), event3.ID, projectID)

	require.NoError(t, err)
	assert.Len(t, chain, 3)
	assert.Equal(t, event1.ID, chain[0].ID) // Oldest first
	assert.Equal(t, event2.ID, chain[1].ID)
	assert.Equal(t, event3.ID, chain[2].ID)
}

func TestEventReplayService_GetCorrelatedEvents(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	projectID := uuid.New().String()
	correlationID := GenerateCorrelationID()

	// Create events with same correlation ID
	event1 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeCreated, nil)
	event1.WithCorrelation(correlationID)
	require.NoError(t, store.Store(event1))

	event2 := NewEvent(projectID, uuid.New().String(), EntityTypeLink, EventTypeLinkCreated, nil)
	event2.WithCorrelation(correlationID)
	require.NoError(t, store.Store(event2))

	// Create event with different correlation ID
	event3 := NewEvent(projectID, uuid.New().String(), EntityTypeItem, EventTypeUpdated, nil)
	event3.WithCorrelation(GenerateCorrelationID())
	require.NoError(t, store.Store(event3))

	// Get correlated events
	correlated, err := service.GetCorrelatedEvents(context.Background(), correlationID, projectID)

	require.NoError(t, err)
	assert.Len(t, correlated, 2)
}

func TestEventReplayService_GetAuditTrail(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	// Create a series of events
	event1 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title": "Initial",
	})
	event1.Version = 1
	event1.WithMetadata("user_id", "user-123")
	event1.WithMetadata("source", "api")
	require.NoError(t, store.Store(event1))

	time.Sleep(eventReplayShortDelay)

	event2 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
		"title": "Updated",
	})
	event2.Version = 2
	event2.WithMetadata("user_id", "user-456")
	event2.WithMetadata("source", "api")
	require.NoError(t, store.Store(event2))

	time.Sleep(eventReplayShortDelay)

	event3 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeDeleted, map[string]interface{}{
		"deleted": true,
	})
	event3.Version = 3
	event3.WithMetadata("user_id", "user-789")
	require.NoError(t, store.Store(event3))

	// Get audit trail
	trail, err := service.GetAuditTrail(context.Background(), entityID)

	require.NoError(t, err)
	assert.Equal(t, entityID, trail.EntityID)
	assert.Equal(t, EntityTypeItem, trail.EntityType)
	assert.Equal(t, 3, trail.TotalEvents)
	assert.Len(t, trail.Events, 3)

	// Check first event
	assert.Equal(t, event1.ID, trail.Events[0].EventID)
	assert.Equal(t, "user-123", trail.Events[0].UserID)
	assert.Equal(t, "api", trail.Events[0].Source)

	// Check last event
	assert.Equal(t, event3.ID, trail.Events[2].EventID)
	assert.Equal(t, "user-789", trail.Events[2].UserID)

	// Check current state
	assert.Equal(t, "Updated", trail.CurrentState["title"])
	assert.Equal(t, true, trail.CurrentState["deleted"])
}

func TestEventReplayService_GetProjectStats(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	projectID := uuid.New().String()

	// Create various events
	entities := []string{uuid.New().String(), uuid.New().String(), uuid.New().String()}

	for i, entityID := range entities {
		// Create event
		event1 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, nil)
		event1.Version = 1
		require.NoError(t, store.Store(event1))

		// Update event
		event2 := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, nil)
		event2.Version = 2
		require.NoError(t, store.Store(event2))

		// Add a link for first entity
		if i == 0 {
			linkEvent := NewEvent(projectID, uuid.New().String(), EntityTypeLink, EventTypeLinkCreated, nil)
			linkEvent.Version = 1
			require.NoError(t, store.Store(linkEvent))
		}
	}

	stats, err := service.GetProjectStats(context.Background(), projectID)

	require.NoError(t, err)
	assert.Equal(t, projectID, stats.ProjectID)
	assert.Equal(t, 7, stats.TotalEvents) // 3 creates + 3 updates + 1 link
	assert.Equal(t, 3, stats.EventsByType[EventTypeCreated])
	assert.Equal(t, 3, stats.EventsByType[EventTypeUpdated])
	assert.Equal(t, 1, stats.EventsByType[EventTypeLinkCreated])
	assert.Equal(t, 6, stats.EventsByEntity[EntityTypeItem])
	assert.Equal(t, 1, stats.EventsByEntity[EntityTypeLink])
	assert.Equal(t, 4, stats.UniqueEntities)
	assert.Greater(t, stats.AvgEventsPerEntity, 0.0)
}

func TestEventReplayService_EmptyEntity(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()

	// Try to get current state for non-existent entity
	_, err := service.GetCurrentState(context.Background(), entityID)
	require.Error(t, err)

	// Try to get audit trail
	_, err = service.GetAuditTrail(context.Background(), entityID)
	require.Error(t, err)
}

func TestEventReplayService_CompareVersions_InvalidVersions(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()

	// Try to compare versions for non-existent entity
	_, err := service.CompareVersions(context.Background(), entityID, 1, 2)
	require.Error(t, err)
}

func TestEventReplayService_ProjectStatsEmpty(t *testing.T) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	projectID := uuid.New().String()

	stats, err := service.GetProjectStats(context.Background(), projectID)

	require.NoError(t, err)
	assert.Equal(t, 0, stats.TotalEvents)
	assert.Equal(t, 0, stats.UniqueEntities)
	assert.InDelta(t, 0.0, stats.AvgEventsPerEntity, 1e-9)
}

func BenchmarkReplayToVersion(b *testing.B) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	// Create 100 events
	for i := 1; i <= 100; i++ {
		event := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
			"version": i,
		})
		event.Version = int64(i)
		require.NoError(b, store.Store(event))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := service.ReplayToVersion(context.Background(), entityID, 50)
		require.NoError(b, err)
	}
}

func BenchmarkGetAuditTrail(b *testing.B) {
	store := NewMockEventStore()
	service := NewEventReplayService(store)

	entityID := uuid.New().String()
	projectID := uuid.New().String()

	// Create 100 events
	for i := 1; i <= 100; i++ {
		event := NewEvent(projectID, entityID, EntityTypeItem, EventTypeUpdated, map[string]interface{}{
			"version": i,
		})
		event.Version = int64(i)
		event.WithMetadata("user_id", "user-123")
		require.NoError(b, store.Store(event))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := service.GetAuditTrail(context.Background(), entityID)
		require.NoError(b, err)
	}
}
