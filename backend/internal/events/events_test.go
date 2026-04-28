package events

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const eventTimestampDelay = 1 * time.Millisecond

// TestNewEvent tests event creation
func TestNewEvent(t *testing.T) {
	projectID := uuid.New().String()
	entityID := uuid.New().String()
	data := map[string]interface{}{
		"title":  "Test Item",
		"status": "open",
	}

	event := NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, data)

	assert.NotEmpty(t, event.ID)
	assert.Equal(t, projectID, event.ProjectID)
	assert.Equal(t, entityID, event.EntityID)
	assert.Equal(t, EntityTypeItem, event.EntityType)
	assert.Equal(t, EventTypeCreated, event.EventType)
	assert.Equal(t, data, event.Data)
	assert.NotNil(t, event.Metadata)
	assert.Equal(t, int64(1), event.Version)
	assert.False(t, event.CreatedAt.IsZero())
}

// TestEventMetadata tests adding metadata to events
func TestEventMetadata(t *testing.T) {
	event := NewEvent("proj-1", "entity-1", EntityTypeItem, EventTypeCreated, nil)

	event.WithMetadata("user_id", "user-123").
		WithMetadata("source", "api").
		WithMetadata("ip_address", "192.168.1.1")

	assert.Equal(t, "user-123", event.Metadata["user_id"])
	assert.Equal(t, "api", event.Metadata["source"])
	assert.Equal(t, "192.168.1.1", event.Metadata["ip_address"])
}

// TestEventSerialization tests event JSON serialization
func TestEventSerialization(t *testing.T) {
	event := NewEvent("proj-1", "entity-1", EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title": "Test",
		"count": 42,
	})

	// Serialize
	jsonData, err := event.ToJSON()
	require.NoError(t, err)
	assert.NotEmpty(t, jsonData)

	// Deserialize
	deserializedEvent, err := FromJSON(jsonData)
	require.NoError(t, err)

	assert.Equal(t, event.ID, deserializedEvent.ID)
	assert.Equal(t, event.ProjectID, deserializedEvent.ProjectID)
	assert.Equal(t, event.EntityID, deserializedEvent.EntityID)
	assert.Equal(t, event.EntityType, deserializedEvent.EntityType)
	assert.Equal(t, event.EventType, deserializedEvent.EventType)
	assert.Equal(t, "Test", deserializedEvent.Data["title"])

	// JSON number becomes float64
	count, ok := deserializedEvent.Data["count"].(float64)
	require.True(t, ok)
	assert.InEpsilon(t, 42.0, count, 1e-9)
}

// TestEventTypes tests all event type constants
func TestEventTypes(t *testing.T) {
	testCases := []struct {
		name       string
		entityType EntityType
		eventType  EventType
	}{
		{"Item Created", EntityTypeItem, EventTypeCreated},
		{"Item Updated", EntityTypeItem, EventTypeUpdated},
		{"Item Deleted", EntityTypeItem, EventTypeDeleted},
		{"Item Status Changed", EntityTypeItem, EventTypeItemStatusChanged},
		{"Item Priority Changed", EntityTypeItem, EventTypeItemPriorityChanged},
		{"Link Created", EntityTypeLink, EventTypeLinkCreated},
		{"Link Deleted", EntityTypeLink, EventTypeLinkDeleted},
		{"Agent Started", EntityTypeAgent, EventTypeAgentStarted},
		{"Agent Stopped", EntityTypeAgent, EventTypeAgentStopped},
		{"Agent Activity", EntityTypeAgent, EventTypeAgentActivity},
		{"Agent Error", EntityTypeAgent, EventTypeAgentError},
		{"Snapshot", EntityTypeItem, EventTypeSnapshot},
		{"Rollback", EntityTypeItem, EventTypeRollback},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			event := NewEvent("proj-1", "entity-1", tc.entityType, tc.eventType, nil)
			assert.Equal(t, tc.entityType, event.EntityType)
			assert.Equal(t, tc.eventType, event.EventType)
		})
	}
}

// TestSnapshot tests snapshot creation
func TestNewSnapshot(t *testing.T) {
	projectID := uuid.New().String()
	entityID := uuid.New().String()
	version := int64(10)
	state := map[string]interface{}{
		"title":   "Current Title",
		"status":  "in_progress",
		"version": version,
	}

	snapshot := NewSnapshot(projectID, entityID, EntityTypeItem, version, state)

	assert.NotEmpty(t, snapshot.ID)
	assert.Equal(t, projectID, snapshot.ProjectID)
	assert.Equal(t, entityID, snapshot.EntityID)
	assert.Equal(t, EntityTypeItem, snapshot.EntityType)
	assert.Equal(t, version, snapshot.Version)
	assert.Equal(t, state, snapshot.State)
	assert.False(t, snapshot.CreatedAt.IsZero())
}

// TestBaseAggregate tests aggregate functionality
func TestBaseAggregate(t *testing.T) {
	aggregateID := uuid.New().String()
	agg := NewBaseAggregate(aggregateID)

	assert.Equal(t, aggregateID, agg.GetID())
	assert.Equal(t, int64(0), agg.GetVersion())
	assert.Empty(t, agg.GetUncommittedEvents())

	// Add events
	event1 := NewEvent("proj-1", aggregateID, EntityTypeItem, EventTypeCreated, nil)
	event2 := NewEvent("proj-1", aggregateID, EntityTypeItem, EventTypeUpdated, nil)

	agg.AddUncommittedEvent(event1)
	agg.AddUncommittedEvent(event2)

	assert.Equal(t, int64(2), agg.GetVersion())
	assert.Len(t, agg.GetUncommittedEvents(), 2)
	assert.Equal(t, int64(1), agg.GetUncommittedEvents()[0].Version)
	assert.Equal(t, int64(2), agg.GetUncommittedEvents()[1].Version)

	// Mark as committed
	agg.MarkEventsAsCommitted()
	assert.Empty(t, agg.GetUncommittedEvents())
	assert.Equal(t, int64(2), agg.GetVersion()) // Version persists
}

// TestEventTimestampOrdering tests that events maintain chronological order
func TestEventTimestampOrdering(t *testing.T) {
	events := make([]*Event, 0, 100)

	for i := 0; i < 100; i++ {
		event := NewEvent("proj-1", "entity-1", EntityTypeItem, EventTypeCreated, nil)
		events = append(events, event)
		time.Sleep(eventTimestampDelay) // Ensure timestamp difference
	}

	// Verify timestamps are in ascending order
	for i := 1; i < len(events); i++ {
		assert.True(t, events[i].CreatedAt.After(events[i-1].CreatedAt) ||
			events[i].CreatedAt.Equal(events[i-1].CreatedAt))
	}
}

// TestEventDataMutation tests that event data can be modified
func TestEventDataMutation(t *testing.T) {
	data := map[string]interface{}{
		"title": "Original",
		"count": 1,
	}

	event := NewEvent("proj-1", "entity-1", EntityTypeItem, EventTypeCreated, data)

	// Modify data
	event.Data["title"] = "Modified"
	event.Data["count"] = 2
	event.Data["new_field"] = "added"

	assert.Equal(t, "Modified", event.Data["title"])
	assert.Equal(t, 2, event.Data["count"])
	assert.Equal(t, "added", event.Data["new_field"])
}

// TestConcurrentEventCreation tests thread-safety of event creation
func TestConcurrentEventCreation(t *testing.T) {
	const goroutines = 100
	events := make(chan *Event, goroutines)

	for i := 0; i < goroutines; i++ {
		go func(id int) {
			event := NewEvent("proj-1", "entity-1", EntityTypeItem, EventTypeCreated, map[string]interface{}{
				"id": id,
			})
			events <- event
		}(i)
	}

	// Collect all events
	created := make([]*Event, 0, goroutines)
	for i := 0; i < goroutines; i++ {
		created = append(created, <-events)
	}

	// Verify all events have unique IDs
	ids := make(map[string]bool)
	for _, event := range created {
		assert.False(t, ids[event.ID], "Duplicate event ID: %s", event.ID)
		ids[event.ID] = true
	}
	assert.Len(t, ids, goroutines)
}

// TestInvalidJSON tests handling of invalid JSON
func TestInvalidJSON(t *testing.T) {
	invalidJSON := []byte(`{"invalid": json}`)

	event, err := FromJSON(invalidJSON)
	require.Error(t, err)
	assert.Nil(t, event)
}

// TestEmptyEvent tests event with minimal data
func TestEmptyEvent(t *testing.T) {
	event := NewEvent("", "", EntityTypeItem, EventTypeCreated, nil)

	assert.NotEmpty(t, event.ID) // ID should still be generated
	assert.Empty(t, event.ProjectID)
	assert.Empty(t, event.EntityID)
	assert.Nil(t, event.Data)
	assert.NotNil(t, event.Metadata)
}

// TestEventVersionIncrement tests version incrementation
func TestEventVersionIncrement(t *testing.T) {
	agg := NewBaseAggregate(uuid.New().String())

	for i := 1; i <= 10; i++ {
		event := NewEvent("proj-1", agg.ID, EntityTypeItem, EventTypeUpdated, nil)
		agg.AddUncommittedEvent(event)
		assert.Equal(t, int64(i), event.Version)
		assert.Equal(t, int64(i), agg.GetVersion())
	}
}

// BenchmarkEventCreation benchmarks event creation performance
func BenchmarkEventCreation(b *testing.B) {
	projectID := uuid.New().String()
	entityID := uuid.New().String()
	data := map[string]interface{}{
		"title": "Benchmark",
		"count": 42,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = NewEvent(projectID, entityID, EntityTypeItem, EventTypeCreated, data)
	}
}

// BenchmarkEventSerialization benchmarks JSON serialization
func BenchmarkEventSerialization(b *testing.B) {
	event := NewEvent("proj-1", "entity-1", EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title":       "Benchmark",
		"description": "This is a benchmark event with some data",
		"count":       42,
		"active":      true,
	})

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := event.ToJSON()
		require.NoError(b, err)
	}
}

// BenchmarkEventDeserialization benchmarks JSON deserialization
func BenchmarkEventDeserialization(b *testing.B) {
	event := NewEvent("proj-1", "entity-1", EntityTypeItem, EventTypeCreated, map[string]interface{}{
		"title": "Benchmark",
		"count": 42,
	})
	jsonData, err := event.ToJSON()
	require.NoError(b, err)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := FromJSON(jsonData)
		require.NoError(b, err)
	}
}
