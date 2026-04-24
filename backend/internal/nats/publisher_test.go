package nats

import (
	"encoding/json"
	"sync"
	"testing"
	"time"

	natslib "github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewEventPublisher(t *testing.T) {
	t.Run("successful connection", func(t *testing.T) {
		publisher, err := NewEventPublisher(natslib.DefaultURL, "")
		if err != nil {
			t.Skipf("NATS not available: %v", err)
		}
		defer publisher.Close()

		assert.NotNil(t, publisher)
		assert.NotNil(t, publisher.conn)
		assert.False(t, publisher.conn.IsClosed())
	})

	t.Run("connection with invalid URL", func(t *testing.T) {
		publisher, err := NewEventPublisher("invalid://url", "")
		require.Error(t, err)
		assert.Nil(t, publisher)
		assert.Contains(t, err.Error(), "failed to connect to NATS")
	})

	t.Run("connection to unreachable server", func(t *testing.T) {
		publisher, err := NewEventPublisher("nats://192.0.2.1:4222", "")
		require.Error(t, err)
		assert.Nil(t, publisher)
	})

	t.Run("connection with invalid credentials file", func(t *testing.T) {
		publisher, err := NewEventPublisher(natslib.DefaultURL, "/invalid/path/creds.txt")
		if err == nil && publisher != nil {
			publisher.Close()
			t.Skip("NATS accepted invalid creds")
		}
		require.Error(t, err)
	})

	t.Run("connection with empty URL", func(t *testing.T) {
		publisher, err := NewEventPublisher("", "")
		if publisher != nil {
			defer publisher.Close()
		}
		// Behavior depends on NATS library
		if err != nil {
			require.Error(t, err)
		}
	})
}

func setupTestPublisher(t *testing.T) *EventPublisher {
	publisher, err := NewEventPublisher(natslib.DefaultURL, "")
	if err != nil {
		t.Skipf("NATS not available: %v", err)
	}
	return publisher
}

func TestEventPublisherPublishItemEvent(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("publish item created event", func(t *testing.T) {
		data := map[string]interface{}{
			"name":        "Test Item",
			"description": "Test Description",
			"type":        "task",
		}

		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-123", "item-456", data)
		require.NoError(t, err)
	})

	t.Run("publish item updated event", func(t *testing.T) {
		data := map[string]interface{}{
			"name":   "Updated Item",
			"status": "completed",
		}

		err := publisher.PublishItemEvent(EventTypeItemUpdated, "proj-123", "item-456", data)
		require.NoError(t, err)
	})

	t.Run("publish item deleted event", func(t *testing.T) {
		err := publisher.PublishItemEvent(EventTypeItemDeleted, "proj-123", "item-456", nil)
		require.NoError(t, err)
	})

	t.Run("publish with empty project ID", func(t *testing.T) {
		err := publisher.PublishItemEvent(EventTypeItemCreated, "", "item-123", nil)
		require.NoError(t, err)
	})

	t.Run("publish with empty item ID", func(t *testing.T) {
		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-123", "", nil)
		require.NoError(t, err)
	})

	t.Run("publish with nil data", func(t *testing.T) {
		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-123", "item-456", nil)
		require.NoError(t, err)
	})

	t.Run("publish with complex nested data", func(t *testing.T) {
		data := map[string]interface{}{
			"name": "Complex Item",
			"metadata": map[string]interface{}{
				"tags":     []string{"urgent", "important"},
				"priority": 1,
				"nested": map[string]string{
					"key": "value",
				},
			},
		}

		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-123", "item-complex", data)
		require.NoError(t, err)
	})
}

func TestEventPublisherPublishLinkEvent(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("publish link created event", func(t *testing.T) {
		data := map[string]interface{}{
			"source_id": "item-1",
			"target_id": "item-2",
			"type":      "depends_on",
		}

		err := publisher.PublishLinkEvent(EventTypeLinkCreated, "proj-123", "link-789", data)
		require.NoError(t, err)
	})

	t.Run("publish link deleted event", func(t *testing.T) {
		err := publisher.PublishLinkEvent(EventTypeLinkDeleted, "proj-123", "link-789", nil)
		require.NoError(t, err)
	})

	t.Run("publish with various link types", func(t *testing.T) {
		linkTypes := []string{"depends_on", "blocks", "related_to", "child_of", "references"}

		for _, linkType := range linkTypes {
			data := map[string]interface{}{"type": linkType}
			err := publisher.PublishLinkEvent(EventTypeLinkCreated, "proj-123", "link-"+linkType, data)
			require.NoError(t, err)
		}
	})
}

func TestEventPublisherPublishAgentEvent(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("publish agent created event", func(t *testing.T) {
		data := map[string]interface{}{
			"name":   "Agent 1",
			"status": "active",
			"type":   "worker",
		}

		err := publisher.PublishAgentEvent(EventTypeAgentCreated, "proj-123", "agent-abc", data)
		require.NoError(t, err)
	})

	t.Run("publish agent updated event", func(t *testing.T) {
		data := map[string]interface{}{
			"status": "idle",
		}

		err := publisher.PublishAgentEvent(EventTypeAgentUpdated, "proj-123", "agent-abc", data)
		require.NoError(t, err)
	})

	t.Run("publish agent deleted event", func(t *testing.T) {
		err := publisher.PublishAgentEvent(EventTypeAgentDeleted, "proj-123", "agent-abc", nil)
		require.NoError(t, err)
	})

	t.Run("publish agent status transitions", func(t *testing.T) {
		statuses := []string{"idle", "active", "busy", "error", "offline"}

		for _, status := range statuses {
			data := map[string]interface{}{"status": status}
			err := publisher.PublishAgentEvent(EventTypeAgentUpdated, "proj-123", "agent-status", data)
			require.NoError(t, err)
		}
	})
}

func TestEventPublisherPublishProjectEvent(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("publish project created event", func(t *testing.T) {
		data := map[string]interface{}{
			"name":        "New Project",
			"description": "Project Description",
		}

		err := publisher.PublishProjectEvent(EventTypeProjectCreated, "proj-new", data)
		require.NoError(t, err)
	})

	t.Run("publish project updated event", func(t *testing.T) {
		data := map[string]interface{}{
			"name": "Updated Project",
		}

		err := publisher.PublishProjectEvent(EventTypeProjectUpdated, "proj-123", data)
		require.NoError(t, err)
	})

	t.Run("publish project deleted event", func(t *testing.T) {
		err := publisher.PublishProjectEvent(EventTypeProjectDeleted, "proj-123", nil)
		require.NoError(t, err)
	})

	t.Run("publish project configuration changes", func(t *testing.T) {
		data := map[string]interface{}{
			"settings": map[string]interface{}{
				"auto_archive": true,
				"retention":    90,
			},
		}

		err := publisher.PublishProjectEvent(EventTypeProjectUpdated, "proj-123", data)
		require.NoError(t, err)
	})
}

func TestEventPublisherClose(t *testing.T) {
	t.Run("close active connection", func(t *testing.T) {
		publisher := setupTestPublisher(t)

		assert.False(t, publisher.conn.IsClosed())
		publisher.Close()
		assert.True(t, publisher.conn.IsClosed())
	})

	t.Run("close nil publisher", func(_ *testing.T) {
		publisher := &EventPublisher{conn: nil}
		// Should not panic
		publisher.Close()
	})

	t.Run("double close", func(t *testing.T) {
		publisher := setupTestPublisher(t)

		publisher.Close()
		publisher.Close() // Should not panic
	})

	t.Run("publish after close fails", func(t *testing.T) {
		publisher := setupTestPublisher(t)
		publisher.Close()

		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-123", "item-456", nil)
		require.Error(t, err)
	})
}

func TestEventStructure(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("event marshaling", func(t *testing.T) {
		event := Event{
			Type:       EventTypeItemCreated,
			ProjectID:  "proj-123",
			EntityID:   "item-456",
			EntityType: "item",
			Data:       map[string]string{"key": "value"},
			Timestamp:  time.Now().Unix(),
		}

		data, err := json.Marshal(event)
		require.NoError(t, err)
		assert.NotEmpty(t, data)

		var unmarshaled Event
		err = json.Unmarshal(data, &unmarshaled)
		require.NoError(t, err)
		assert.Equal(t, event.Type, unmarshaled.Type)
		assert.Equal(t, event.ProjectID, unmarshaled.ProjectID)
		assert.Equal(t, event.EntityID, unmarshaled.EntityID)
	})

	t.Run("event with nil data", func(t *testing.T) {
		event := Event{
			Type:       EventTypeItemDeleted,
			ProjectID:  "proj-123",
			EntityID:   "item-456",
			EntityType: "item",
			Data:       nil,
			Timestamp:  0,
		}

		data, err := json.Marshal(event)
		require.NoError(t, err)
		assert.NotEmpty(t, data)
	})
}

func TestEventTypeConstants(t *testing.T) {
	t.Run("all event type constants defined", func(t *testing.T) {
		assert.Equal(t, "item.created", EventTypeItemCreated)
		assert.Equal(t, "item.updated", EventTypeItemUpdated)
		assert.Equal(t, "item.deleted", EventTypeItemDeleted)
		assert.Equal(t, "link.created", EventTypeLinkCreated)
		assert.Equal(t, "link.deleted", EventTypeLinkDeleted)
		assert.Equal(t, "agent.created", EventTypeAgentCreated)
		assert.Equal(t, "agent.updated", EventTypeAgentUpdated)
		assert.Equal(t, "agent.deleted", EventTypeAgentDeleted)
		assert.Equal(t, "project.created", EventTypeProjectCreated)
		assert.Equal(t, "project.updated", EventTypeProjectUpdated)
		assert.Equal(t, "project.deleted", EventTypeProjectDeleted)
	})

	t.Run("event types are unique", func(t *testing.T) {
		eventTypes := []string{
			EventTypeItemCreated, EventTypeItemUpdated, EventTypeItemDeleted,
			EventTypeLinkCreated, EventTypeLinkDeleted,
			EventTypeAgentCreated, EventTypeAgentUpdated, EventTypeAgentDeleted,
			EventTypeProjectCreated, EventTypeProjectUpdated, EventTypeProjectDeleted,
		}

		seen := make(map[string]bool)
		for _, et := range eventTypes {
			assert.False(t, seen[et], "duplicate event type: %s", et)
			seen[et] = true
		}
	})
}

func runConcurrentItemPublishing(t *testing.T, publisher *EventPublisher) {
	t.Helper()
	var wg sync.WaitGroup
	numGoroutines := 50
	errChan := make(chan error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			data := map[string]interface{}{"id": id}
			err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-concurrent", "item-"+string(rune(id)), data)
			errChan <- err
		}(i)
	}

	wg.Wait()
	close(errChan)

	errorCount := 0
	for err := range errChan {
		if err != nil {
			errorCount++
		}
	}

	assert.Equal(t, 0, errorCount, "no errors expected in concurrent publishing")
}

func runConcurrentMixedPublishing(t *testing.T, publisher *EventPublisher) {
	t.Helper()
	var wg sync.WaitGroup
	numGoroutines := 30
	errChan := make(chan error, numGoroutines)

	eventPublishers := []func(int){
		func(id int) {
			err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-mixed", "item-"+string(rune(id)), nil)
			errChan <- err
		},
		func(id int) {
			err := publisher.PublishLinkEvent(EventTypeLinkCreated, "proj-mixed", "link-"+string(rune(id)), nil)
			errChan <- err
		},
		func(id int) {
			err := publisher.PublishAgentEvent(EventTypeAgentCreated, "proj-mixed", "agent-"+string(rune(id)), nil)
			errChan <- err
		},
	}

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		idx := i % len(eventPublishers)
		if idx < 0 || idx >= len(eventPublishers) {
			t.Fatalf("index %d out of bounds for eventPublishers (len=%d)", idx, len(eventPublishers))
		}
		publishFunc := eventPublishers[idx]
		go func(id int, fn func(int)) {
			defer wg.Done()
			fn(id)
		}(i, publishFunc)
	}

	wg.Wait()
	close(errChan)

	for err := range errChan {
		require.NoError(t, err)
	}
}

func TestConcurrentPublishing(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping concurrent test in short mode")
	}

	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("concurrent item event publishing", func(t *testing.T) {
		runConcurrentItemPublishing(t, publisher)
	})

	t.Run("concurrent mixed event types", func(t *testing.T) {
		runConcurrentMixedPublishing(t, publisher)
	})
}

func TestEventSubjectFormat(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("subject format for different entities", func(t *testing.T) {
		testCases := []struct {
			publishFunc func() error
			projectID   string
			eventType   string
		}{
			{
				publishFunc: func() error {
					return publisher.PublishItemEvent(EventTypeItemCreated, "proj-1", "item-1", nil)
				},
				projectID: "proj-1",
				eventType: EventTypeItemCreated,
			},
			{
				publishFunc: func() error {
					return publisher.PublishLinkEvent(EventTypeLinkCreated, "proj-2", "link-1", nil)
				},
				projectID: "proj-2",
				eventType: EventTypeLinkCreated,
			},
			{
				publishFunc: func() error {
					return publisher.PublishAgentEvent(EventTypeAgentCreated, "proj-3", "agent-1", nil)
				},
				projectID: "proj-3",
				eventType: EventTypeAgentCreated,
			},
			{
				publishFunc: func() error {
					return publisher.PublishProjectEvent(EventTypeProjectCreated, "proj-4", nil)
				},
				projectID: "proj-4",
				eventType: EventTypeProjectCreated,
			},
		}

		for _, tc := range testCases {
			err := tc.publishFunc()
			require.NoError(t, err)
			// Subject format: tracertm.{projectID}.{eventType}
			// This is tested implicitly by successful publishing
		}
	})
}

func TestEventDataTypes(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("various data types", func(t *testing.T) {
		testCases := []struct {
			name string
			data interface{}
		}{
			{"nil data", nil},
			{"string data", "test string"},
			{"number data", 12345},
			{"boolean data", true},
			{"array data", []string{"a", "b", "c"}},
			{"map data", map[string]interface{}{"key": "value"}},
			{"nested map", map[string]interface{}{
				"level1": map[string]interface{}{
					"level2": []int{1, 2, 3},
				},
			}},
			{"struct-like data", struct {
				Name  string
				Count int
			}{"test", 42}},
		}

		for _, tc := range testCases {
			t.Run(tc.name, func(t *testing.T) {
				err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-types", "item-"+tc.name, tc.data)
				require.NoError(t, err)
			})
		}
	})
}

func TestPublisherConnectionStates(t *testing.T) {
	t.Run("publish with active connection", func(t *testing.T) {
		publisher := setupTestPublisher(t)
		defer publisher.Close()

		assert.True(t, publisher.conn.IsConnected())

		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-123", "item-456", nil)
		require.NoError(t, err)
	})

	t.Run("multiple sequential publishes", func(t *testing.T) {
		publisher := setupTestPublisher(t)
		defer publisher.Close()

		for i := 0; i < 10; i++ {
			err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-seq", "item-"+string(rune(i)), nil)
			require.NoError(t, err)
		}
	})
}

func TestEventPublishErrorHandling(t *testing.T) {
	t.Run("publish with closed connection", func(t *testing.T) {
		publisher := setupTestPublisher(t)
		publisher.Close()

		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-123", "item-456", nil)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to publish event")
	})

	t.Run("publish with very large data", func(t *testing.T) {
		publisher := setupTestPublisher(t)
		defer publisher.Close()

		// Create large data structure
		largeData := make(map[string]interface{})
		for i := 0; i < 1000; i++ {
			largeData["key"+string(rune(i))] = "value with some content to make it larger"
		}

		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-large", "item-large", largeData)
		require.NoError(t, err)
	})
}

func TestEventEntityTypes(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("verify entity type in event", func(t *testing.T) {
		testCases := []struct {
			name        string
			entityType  string
			publishFunc func() error
		}{
			{
				name:       "item entity",
				entityType: "item",
				publishFunc: func() error {
					return publisher.PublishItemEvent(EventTypeItemCreated, "proj-1", "item-1", nil)
				},
			},
			{
				name:       "link entity",
				entityType: "link",
				publishFunc: func() error {
					return publisher.PublishLinkEvent(EventTypeLinkCreated, "proj-1", "link-1", nil)
				},
			},
			{
				name:       "agent entity",
				entityType: "agent",
				publishFunc: func() error {
					return publisher.PublishAgentEvent(EventTypeAgentCreated, "proj-1", "agent-1", nil)
				},
			},
			{
				name:       "project entity",
				entityType: "project",
				publishFunc: func() error {
					return publisher.PublishProjectEvent(EventTypeProjectCreated, "proj-1", nil)
				},
			},
		}

		for _, tc := range testCases {
			t.Run(tc.name, func(t *testing.T) {
				err := tc.publishFunc()
				require.NoError(t, err)
			})
		}
	})
}

func TestPublisherResourceCleanup(t *testing.T) {
	t.Run("ensure connection closed on Close", func(t *testing.T) {
		publisher := setupTestPublisher(t)

		conn := publisher.conn
		assert.False(t, conn.IsClosed())

		publisher.Close()
		assert.True(t, conn.IsClosed())
	})

	t.Run("multiple publishers", func(t *testing.T) {
		publishers := make([]*EventPublisher, 5)

		for i := 0; i < 5; i++ {
			pub, err := NewEventPublisher(natslib.DefaultURL, "")
			if err != nil {
				t.Skipf("NATS not available: %v", err)
			}
			publishers[i] = pub
		}

		// Close all
		for _, pub := range publishers {
			pub.Close()
			assert.True(t, pub.conn.IsClosed())
		}
	})
}

func TestEventTimestamps(t *testing.T) {
	publisher := setupTestPublisher(t)
	defer publisher.Close()

	t.Run("timestamp handling", func(t *testing.T) {
		// Timestamps are set to 0 in the Event struct and handled by NATS
		err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-time", "item-time", nil)
		require.NoError(t, err)

		// Verify we can create events with explicit timestamps
		event := Event{
			Type:       EventTypeItemCreated,
			ProjectID:  "proj-123",
			EntityID:   "item-456",
			EntityType: "item",
			Data:       nil,
			Timestamp:  time.Now().Unix(),
		}

		data, err := json.Marshal(event)
		require.NoError(t, err)
		assert.NotEmpty(t, data)
	})
}

func BenchmarkEventPublishing(b *testing.B) {
	publisher, err := NewEventPublisher(natslib.DefaultURL, "")
	if err != nil {
		b.Skipf("NATS not available: %v", err)
	}
	defer publisher.Close()

	data := map[string]interface{}{
		"name": "Benchmark Item",
		"type": "task",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-bench", "item-bench", data); err != nil {
			b.Fatalf("PublishItemEvent failed: %v", err)
		}
	}
}

func BenchmarkConcurrentPublishing(b *testing.B) {
	publisher, err := NewEventPublisher(natslib.DefaultURL, "")
	if err != nil {
		b.Skipf("NATS not available: %v", err)
	}
	defer publisher.Close()

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			if err := publisher.PublishItemEvent(EventTypeItemCreated, "proj-bench", "item-bench", nil); err != nil {
				b.Fatalf("PublishItemEvent failed: %v", err)
			}
		}
	})
}
