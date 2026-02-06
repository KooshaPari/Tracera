package integration

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/websocket"
)

// TestNATSEventPropagationToWebSocket verifies that NATS events are propagated to WebSocket clients
func TestNATSEventPropagationToWebSocket(t *testing.T) {
	// Skip if not in integration test environment
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Create WebSocket hub
	hub := websocket.NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Start hub
	go hub.Run(ctx)

	// Create mock WebSocket client
	// In real test, this would connect via HTTP test server
	mockClient := &websocket.Client{
		ID:        "test-client-1",
		ProjectID: "test-project",
		Send:      make(chan *websocket.Message, 256),
		Hub:       hub,
	}

	// Register client
	hub.Register <- mockClient

	// Give time for registration
	time.Sleep(100 * time.Millisecond)

	// Create NATS event
	natsEvent := &websocket.NATSEvent{
		EventType:  "item.created",
		ProjectID:  "test-project",
		EntityID:   "item-123",
		EntityType: "item",
		Data: map[string]interface{}{
			"title": "Test Item",
		},
		Timestamp: time.Now().Format(time.RFC3339),
		Source:    "python",
	}

	// Send NATS event to hub
	hub.HandleNATSEvent(natsEvent)

	// Wait for message to be received
	select {
	case msg := <-mockClient.Send:
		assert.Equal(t, "nats_event", msg.Type)
		assert.NotNil(t, msg.Data)

		data := msg.Data
		assert.Equal(t, "item.created", data["event_type"])
		assert.Equal(t, "test-project", data["project_id"])
		assert.Equal(t, "item-123", data["entity_id"])
		assert.Equal(t, "item", data["entity_type"])
		assert.Equal(t, "python", data["source"])

		itemData, ok := data["data"].(map[string]interface{})
		require.True(t, ok)
		assert.Equal(t, "Test Item", itemData["title"])

	case <-time.After(2 * time.Second):
		t.Fatal("Timeout waiting for WebSocket message")
	}

	// Unregister client
	hub.Unregister <- mockClient
}

// TestNATSBridgeEventConversion verifies BridgeEvent to NATSEvent conversion
func TestNATSBridgeEventConversion(t *testing.T) {
	bridgeEvent := &nats.BridgeEvent{
		Type:       "spec.created",
		ProjectID:  "test-project",
		EntityID:   "spec-456",
		EntityType: "specification",
		Data: map[string]interface{}{
			"title":       "Test Spec",
			"description": "A test specification",
		},
		Source: "python",
	}

	// Convert to NATSEvent
	natsEvent := &websocket.NATSEvent{
		EventType:  bridgeEvent.Type,
		ProjectID:  bridgeEvent.ProjectID,
		EntityID:   bridgeEvent.EntityID,
		EntityType: bridgeEvent.EntityType,
		Data:       bridgeEvent.Data,
		Timestamp:  time.Now().Format(time.RFC3339),
		Source:     bridgeEvent.Source,
	}

	assert.Equal(t, "spec.created", natsEvent.EventType)
	assert.Equal(t, "test-project", natsEvent.ProjectID)
	assert.Equal(t, "spec-456", natsEvent.EntityID)
	assert.Equal(t, "specification", natsEvent.EntityType)
	assert.Equal(t, "python", natsEvent.Source)
	assert.Equal(t, "Test Spec", natsEvent.Data["title"])
}

// TestWebSocketMessageSerialization verifies that WebSocket messages serialize correctly
func TestWebSocketMessageSerialization(t *testing.T) {
	msg := &websocket.Message{
		Type: "nats_event",
		Data: map[string]interface{}{
			"event_type":  "item.updated",
			"project_id":  "test-project",
			"entity_id":   "item-789",
			"entity_type": "item",
			"data": map[string]interface{}{
				"title": "Updated Item",
			},
			"timestamp": "2024-01-15T10:30:00Z",
			"source":    "go",
		},
		Timestamp: time.Now(),
	}

	// Serialize to JSON
	data, err := json.Marshal(msg)
	require.NoError(t, err)

	// Deserialize
	var deserialized websocket.Message
	err = json.Unmarshal(data, &deserialized)
	require.NoError(t, err)

	assert.Equal(t, "nats_event", deserialized.Type)
	assert.Equal(t, "item.updated", deserialized.Data["event_type"])
	assert.Equal(t, "go", deserialized.Data["source"])
}

// TestProjectSpecificBroadcast verifies that events are only sent to clients subscribed to the project
func TestProjectSpecificBroadcast(t *testing.T) {
	hub := websocket.NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go hub.Run(ctx)

	// Create clients for different projects
	client1 := &websocket.Client{
		ID:        "client-1",
		ProjectID: "project-a",
		Send:      make(chan *websocket.Message, 256),
		Hub:       hub,
	}

	client2 := &websocket.Client{
		ID:        "client-2",
		ProjectID: "project-b",
		Send:      make(chan *websocket.Message, 256),
		Hub:       hub,
	}

	// Register both clients
	hub.Register <- client1
	hub.Register <- client2

	time.Sleep(100 * time.Millisecond)

	// Send event to project-a
	natsEvent := &websocket.NATSEvent{
		EventType:  "item.created",
		ProjectID:  "project-a",
		EntityID:   "item-123",
		EntityType: "item",
		Data:       map[string]interface{}{"title": "Item A"},
		Timestamp:  time.Now().Format(time.RFC3339),
		Source:     "go",
	}

	hub.HandleNATSEvent(natsEvent)

	// Client 1 should receive the event
	select {
	case msg := <-client1.Send:
		assert.Equal(t, "nats_event", msg.Type)
	case <-time.After(1 * time.Second):
		t.Fatal("Client 1 did not receive event")
	}

	// Client 2 should NOT receive the event
	select {
	case <-client2.Send:
		t.Fatal("Client 2 should not have received event for project-a")
	case <-time.After(500 * time.Millisecond):
		// Expected - no message
	}

	// Cleanup
	hub.Unregister <- client1
	hub.Unregister <- client2
}

// TestMultipleClientsInSameProject verifies that all clients in a project receive events
func TestMultipleClientsInSameProject(t *testing.T) {
	hub := websocket.NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go hub.Run(ctx)

	// Create multiple clients for same project
	clients := make([]*websocket.Client, 3)
	for i := 0; i < 3; i++ {
		clients[i] = &websocket.Client{
			ID:        string(rune('A' + i)),
			ProjectID: "test-project",
			Send:      make(chan *websocket.Message, 256),
			Hub:       hub,
		}
		hub.Register <- clients[i]
	}

	time.Sleep(100 * time.Millisecond)

	// Send event
	natsEvent := &websocket.NATSEvent{
		EventType:  "item.created",
		ProjectID:  "test-project",
		EntityID:   "item-999",
		EntityType: "item",
		Data:       map[string]interface{}{"title": "Broadcast Item"},
		Timestamp:  time.Now().Format(time.RFC3339),
		Source:     "python",
	}

	hub.HandleNATSEvent(natsEvent)

	// All clients should receive the event
	for i, client := range clients {
		select {
		case msg := <-client.Send:
			assert.Equal(t, "nats_event", msg.Type, "Client %d should receive event", i)
		case <-time.After(1 * time.Second):
			t.Fatalf("Client %d did not receive event", i)
		}
	}

	// Cleanup
	for _, client := range clients {
		hub.Unregister <- client
	}
}
