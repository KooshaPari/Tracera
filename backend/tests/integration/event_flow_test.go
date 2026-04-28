package integration

import (
	"encoding/json"
	"testing"
	"time"

	natslib "github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/nats"
)

// setupPythonBridge creates a PythonBridge for testing
func setupPythonBridge(t *testing.T) *nats.PythonBridge {
	conn, err := natslib.Connect(natslib.DefaultURL)
	require.NoError(t, err)
	t.Cleanup(func() { conn.Close() })

	bridge, err := nats.NewPythonBridge(conn)
	require.NoError(t, err)

	return bridge
}

func TestItemCreatedEventPublished(t *testing.T) {
	bridge := setupPythonBridge(t)

	// Setup event collector
	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToEventType("item.created", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	// Give subscriber time to register
	time.Sleep(500 * time.Millisecond)

	// Publish item.created event
	eventData := map[string]interface{}{
		"id":     "test-item-123",
		"title":  "Test Item",
		"type":   "requirement",
		"status": "active",
	}

	err = bridge.PublishItemEvent(
		"item.created",
		"test-project-id",
		"test-item-123",
		eventData,
	)
	require.NoError(t, err)

	// Wait for event
	select {
	case event := <-eventChan:
		assert.Equal(t, "item.created", event.Type)
		assert.Equal(t, "test-project-id", event.ProjectID)
		assert.Equal(t, "test-item-123", event.EntityID)
		assert.Equal(t, "item", event.EntityType)
		assert.Equal(t, "go", event.Source)
		assert.Equal(t, "Test Item", event.Data["title"])
	case <-time.After(5 * time.Second):
		t.Fatal("Event not received within timeout")
	}
}

func TestItemUpdatedEventPublished(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToEventType("item.updated", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	eventData := map[string]interface{}{
		"id":     "test-item-456",
		"title":  "Updated Item",
		"status": "completed",
	}

	err = bridge.PublishItemEvent(
		"item.updated",
		"test-project-id",
		"test-item-456",
		eventData,
	)
	require.NoError(t, err)

	select {
	case event := <-eventChan:
		assert.Equal(t, "item.updated", event.Type)
		assert.Equal(t, "test-item-456", event.EntityID)
		assert.Equal(t, "Updated Item", event.Data["title"])
	case <-time.After(5 * time.Second):
		t.Fatal("Event not received within timeout")
	}
}

func TestItemDeletedEventPublished(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToEventType("item.deleted", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	eventData := map[string]interface{}{
		"id": "test-item-789",
	}

	err = bridge.PublishItemEvent(
		"item.deleted",
		"test-project-id",
		"test-item-789",
		eventData,
	)
	require.NoError(t, err)

	select {
	case event := <-eventChan:
		assert.Equal(t, "item.deleted", event.Type)
		assert.Equal(t, "test-item-789", event.EntityID)
	case <-time.After(5 * time.Second):
		t.Fatal("Event not received within timeout")
	}
}

func TestLinkCreatedEventPublished(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToEventType("link.created", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	eventData := map[string]interface{}{
		"id":        "test-link-123",
		"source_id": "item-1",
		"target_id": "item-2",
		"type":      "depends_on",
	}

	err = bridge.PublishLinkEvent(
		"link.created",
		"test-project-id",
		"test-link-123",
		eventData,
	)
	require.NoError(t, err)

	select {
	case event := <-eventChan:
		assert.Equal(t, "link.created", event.Type)
		assert.Equal(t, "link", event.EntityType)
		assert.Equal(t, "depends_on", event.Data["type"])
	case <-time.After(5 * time.Second):
		t.Fatal("Event not received within timeout")
	}
}

func TestProjectCreatedEventPublished(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToEventType("project.created", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	eventData := map[string]interface{}{
		"id":   "test-project-456",
		"name": "Test Project",
	}

	err = bridge.PublishProjectEvent(
		"project.created",
		"test-project-456",
		eventData,
	)
	require.NoError(t, err)

	select {
	case event := <-eventChan:
		assert.Equal(t, "project.created", event.Type)
		assert.Equal(t, "project", event.EntityType)
		assert.Equal(t, "test-project-456", event.ProjectID)
		assert.Equal(t, "Test Project", event.Data["name"])
	case <-time.After(5 * time.Second):
		t.Fatal("Event not received within timeout")
	}
}

func TestPythonBackendEventsReceived(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToPythonEvents(func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	// Simulate Python backend publishing a spec.created event
	conn, err := natslib.Connect(natslib.DefaultURL)
	require.NoError(t, err)
	defer conn.Close()

	js, err := conn.JetStream()
	require.NoError(t, err)

	pythonEvent := map[string]interface{}{
		"type":        "spec.created",
		"project_id":  "test-project",
		"entity_id":   "spec-123",
		"entity_type": "adr",
		"data": map[string]interface{}{
			"id":     "spec-123",
			"title":  "Test ADR",
			"status": "proposed",
		},
		"source": "python",
	}

	payload, err := json.Marshal(pythonEvent)
	require.NoError(t, err)

	_, err = js.Publish("tracertm.bridge.python.test-project.spec.created", payload)
	require.NoError(t, err)

	select {
	case event := <-eventChan:
		assert.Equal(t, "python", event.Source)
		assert.Equal(t, "spec.created", event.Type)
		assert.Equal(t, "adr", event.EntityType)
		assert.Equal(t, "Test ADR", event.Data["title"])
	case <-time.After(5 * time.Second):
		t.Fatal("Python event not received within timeout")
	}
}

func TestPublisherUtilsSafePublish(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToEventType("item.created", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	// Test SafePublish (fire-and-forget)
	eventData := map[string]interface{}{
		"id":    "safe-publish-test",
		"title": "Safe Publish Test",
	}

	nats.SafePublish(
		bridge,
		"item.created",
		"test-project",
		"safe-publish-test",
		"item",
		eventData,
	)

	// Give async publish time to complete
	time.Sleep(1 * time.Second)

	select {
	case event := <-eventChan:
		assert.Equal(t, "safe-publish-test", event.EntityID)
		assert.Equal(t, "Safe Publish Test", event.Data["title"])
	case <-time.After(5 * time.Second):
		t.Fatal("SafePublish event not received within timeout")
	}
}

func TestPublisherUtilsSafePublishWithRetry(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 10)
	err := bridge.SubscribeToEventType("item.updated", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	// Test SafePublishWithRetry
	eventData := map[string]interface{}{
		"id":    "retry-test",
		"title": "Retry Test",
	}

	nats.SafePublishWithRetry(
		bridge,
		"item.updated",
		"test-project",
		"retry-test",
		"item",
		eventData,
		3, // max retries
	)

	time.Sleep(1 * time.Second)

	select {
	case event := <-eventChan:
		assert.Equal(t, "retry-test", event.EntityID)
	case <-time.After(5 * time.Second):
		t.Fatal("SafePublishWithRetry event not received within timeout")
	}
}

func TestMultipleEventsInSequence(t *testing.T) {
	bridge := setupPythonBridge(t)

	eventChan := make(chan *nats.BridgeEvent, 20)
	err := bridge.SubscribeToEventType("item.created", func(event *nats.BridgeEvent) {
		eventChan <- event
	})
	require.NoError(t, err)

	time.Sleep(500 * time.Millisecond)

	// Publish multiple events
	for i := 0; i < 5; i++ {
		eventData := map[string]interface{}{
			"id":    "item-" + string(rune(i)),
			"title": "Item " + string(rune(i)),
		}

		err := bridge.PublishItemEvent(
			"item.created",
			"test-project",
			"item-"+string(rune(i)),
			eventData,
		)
		require.NoError(t, err)
	}

	// Collect all events
	receivedCount := 0
	timeout := time.After(10 * time.Second)

	for receivedCount < 5 {
		select {
		case <-eventChan:
			receivedCount++
		case <-timeout:
			t.Fatalf("Only received %d/5 events within timeout", receivedCount)
		}
	}

	assert.Equal(t, 5, receivedCount)
}

func TestProjectSpecificSubscription(t *testing.T) {
	conn, err := natslib.Connect(natslib.DefaultURL)
	require.NoError(t, err)
	defer conn.Close()

	bridge, err := nats.NewPythonBridge(conn)
	require.NoError(t, err)

	eventChan := make(chan *nats.BridgeEvent, 10)

	// Subscribe to events only for project-alpha
	js, err := conn.JetStream()
	require.NoError(t, err)

	sub, err := js.Subscribe(
		"tracertm.bridge.go.project-alpha.>",
		func(msg *natslib.Msg) {
			var event nats.BridgeEvent
			if err := json.Unmarshal(msg.Data, &event); err == nil {
				eventChan <- &event
			}
			msg.Ack()
		},
		natslib.Durable("test-project-alpha"),
		natslib.ManualAck(),
	)
	require.NoError(t, err)
	defer sub.Unsubscribe()

	time.Sleep(500 * time.Millisecond)

	// Publish to project-alpha (should receive)
	err = bridge.PublishItemEvent(
		"item.created",
		"project-alpha",
		"item-alpha-1",
		map[string]interface{}{"title": "Alpha Item"},
	)
	require.NoError(t, err)

	// Publish to project-beta (should not receive)
	err = bridge.PublishItemEvent(
		"item.created",
		"project-beta",
		"item-beta-1",
		map[string]interface{}{"title": "Beta Item"},
	)
	require.NoError(t, err)

	time.Sleep(1 * time.Second)

	// Should only receive event from project-alpha
	receivedCount := 0
	timeout := time.After(2 * time.Second)

loop:
	for {
		select {
		case event := <-eventChan:
			assert.Equal(t, "project-alpha", event.ProjectID)
			receivedCount++
		case <-timeout:
			break loop
		}
	}

	assert.Equal(t, 1, receivedCount, "Should only receive event from project-alpha")
}
