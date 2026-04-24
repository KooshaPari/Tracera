package websocket

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/events"
)

const (
	integrationShortTimeout     = 1 * time.Second
	integrationMediumTimeout    = 5 * time.Second
	integrationLongTimeout      = 10 * time.Second
	integrationTickDelay        = 100 * time.Millisecond
	integrationShortSleep       = 100 * time.Millisecond
	integrationMediumSleep      = 500 * time.Millisecond
	integrationClientBuffer     = 256
	integrationLargeBuffer      = 1024
	integrationBenchmarkClients = 100
	integrationMaxClients       = 1000
	integrationDropBufferSize   = 10
	integrationDropThreshold    = 0.8
	integrationMessageCount     = 10000
)

func startHub(t *testing.T) (*Hub, context.Context, context.CancelFunc) {
	t.Helper()
	hub := NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	go hub.Run(ctx)
	return hub, ctx, cancel
}

func buildTestClients(hub *Hub) (*Client, *Client) {
	client1 := &Client{
		ID:        "client-1",
		ProjectID: "project-1",
		Send:      make(chan *Message, integrationClientBuffer),
		Hub:       hub,
	}
	client2 := &Client{
		ID:        "client-2",
		ProjectID: "project-1",
		Send:      make(chan *Message, integrationClientBuffer),
		Hub:       hub,
	}
	return client1, client2
}

func registerClients(hub *Hub, clients ...*Client) {
	for _, client := range clients {
		hub.Register <- client
	}
	time.Sleep(integrationShortSleep)
}

func unregisterClients(hub *Hub, clients ...*Client) {
	for _, client := range clients {
		hub.Unregister <- client
	}
	time.Sleep(integrationShortSleep)
}

func subscribeIntegrationClients(t *testing.T, sm *SubscriptionManager, client1 *Client, client2 *Client) {
	_, err := sm.Subscribe(client1, SubscribeToProject, "project-1", nil)
	require.NoError(t, err)
	_, err = sm.Subscribe(client2, SubscribeToEntity, "entity-1", nil)
	require.NoError(t, err)
}

func trackIntegrationPresence(pt *PresenceTracker) {
	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")
	pt.StartViewing("client-1", "entity-1", "item")
}

func broadcastIntegrationEvent(hub *Hub) {
	event := events.NewEvent(
		"project-1",
		"entity-1",
		events.EntityTypeItem,
		events.EventTypeCreated,
		map[string]interface{}{"title": "Test"},
	)

	hub.BroadcastEvent(event)
}

func assertClientReceivedEvent(t *testing.T, client *Client, timeoutMessage string) {
	t.Helper()
	timeout := time.After(integrationShortTimeout)
	select {
	case msg := <-client.Send:
		assert.Equal(t, "event", msg.Type)
		assert.NotNil(t, msg.Event)
	case <-timeout:
		t.Fatal(timeoutMessage)
	}
}

func assertIntegrationPresence(t *testing.T, pt *PresenceTracker) {
	t.Helper()
	viewers := pt.GetEntityViewers("entity-1")
	assert.Len(t, viewers, 1)
	assert.Equal(t, "user-1", viewers[0].UserID)
}

func waitForHubClients(hub *Hub, expected int) error {
	timeout := time.After(integrationMediumTimeout)
	ticker := time.NewTicker(integrationTickDelay)
	defer ticker.Stop()

	for {
		select {
		case <-timeout:
			stats := hub.GetStats()
			return fmt.Errorf("timed out waiting for %d clients, got %v", expected, stats["total_clients"])
		case <-ticker.C:
			stats := hub.GetStats()
			if stats["total_clients"] == expected {
				return nil
			}
		}
	}
}

func registerConcurrentClients(hub *Hub, numClients int) []*Client {
	clients := make([]*Client, numClients)
	var wg sync.WaitGroup

	for i := 0; i < numClients; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			client := &Client{
				ID:        string(rune('a' + idx)),
				ProjectID: "project-1",
				Send:      make(chan *Message, integrationClientBuffer),
				Hub:       hub,
			}
			clients[idx] = client
			hub.Register <- client
		}(i)
	}

	wg.Wait()
	return clients
}

func broadcastProjectMessage(hub *Hub, projectID string) {
	msg := &Message{
		Type:      "test",
		Timestamp: time.Now(),
	}
	hub.BroadcastToProject(projectID, msg)
}

func countClientMessages(clients []*Client, timeout time.Duration) int64 {
	var wg sync.WaitGroup
	var received atomic.Int64
	deadline := time.After(timeout)

	for _, client := range clients {
		wg.Add(1)
		go func(c *Client) {
			defer wg.Done()
			select {
			case <-c.Send:
				received.Add(1)
			case <-deadline:
			}
		}(client)
	}

	wg.Wait()
	return received.Load()
}

func unregisterAll(hub *Hub, clients []*Client) {
	for _, client := range clients {
		hub.Unregister <- client
	}
}

// TestFullIntegration tests the complete real-time system
func TestFullIntegration(t *testing.T) {
	hub, _, cancel := startHub(t)
	defer cancel()

	sm := NewSubscriptionManager()
	pt := NewPresenceTracker()

	client1, client2 := buildTestClients(hub)

	registerClients(hub, client1, client2)
	subscribeIntegrationClients(t, sm, client1, client2)
	trackIntegrationPresence(pt)
	broadcastIntegrationEvent(hub)

	assertClientReceivedEvent(t, client1, "Client 1 didn't receive event")
	assertClientReceivedEvent(t, client2, "Client 2 didn't receive event")
	assertIntegrationPresence(t, pt)

	unregisterClients(hub, client1, client2)
	require.NoError(t, waitForHubClients(hub, 0))
}

// TestConcurrentConnections tests handling of many concurrent connections
func TestConcurrentConnections(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping concurrent connections test in short mode")
	}

	hub, ctx, cancel := startHub(t)
	defer cancel()

	numClients := integrationMaxClients
	clients := registerConcurrentClients(hub, numClients)
	require.NoError(t, waitForHubClients(hub, numClients))

	broadcastProjectMessage(hub, "project-1")
	received := countClientMessages(clients, integrationMediumTimeout)

	assert.Greater(t, int(received), numClients-10)

	unregisterAll(hub, clients)
	_ = ctx
}

// TestHighFrequencyUpdates tests handling of high-frequency message broadcasts
func TestHighFrequencyUpdates(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping high frequency test in short mode")
	}

	hub := NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go hub.Run(ctx)

	client := &Client{
		ID:        "client-1",
		ProjectID: "project-1",
		Send:      make(chan *Message, integrationLargeBuffer), // Larger buffer
		Hub:       hub,
	}

	hub.Register <- client
	time.Sleep(integrationShortSleep)

	// Send many messages quickly
	numMessages := integrationMessageCount
	var wg sync.WaitGroup

	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < numMessages; i++ {
			msg := &Message{
				Type:      "update",
				Timestamp: time.Now(),
				Data: map[string]interface{}{
					"index": i,
				},
			}
			hub.BroadcastToProject("project-1", msg)
		}
	}()

	// Count received messages
	var received atomic.Int64
	wg.Add(1)
	go func() {
		defer wg.Done()
		timeout := time.After(integrationLongTimeout)
		for {
			select {
			case <-client.Send:
				received.Add(1)
			case <-timeout:
				return
			}
		}
	}()

	wg.Wait()

	// Should have received most messages
	t.Logf("Sent: %d, Received: %d", numMessages, received.Load())
	assert.Greater(t, int(received.Load()), numMessages/2)
}

// TestBackpressureHandling tests backpressure mechanisms
func TestBackpressureHandling(t *testing.T) {
	config := &BackpressureConfig{
		Strategy:      StrategyDrop,
		BufferSize:    integrationDropBufferSize,
		DropThreshold: integrationDropThreshold,
	}

	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, integrationDropBufferSize),
	}

	bp := NewBackpressureHandler(client, config)

	// Fill buffer
	for i := 0; i < integrationDropBufferSize; i++ {
		msg := &Message{Type: "test", Timestamp: time.Now()}
		bp.Send(msg)
	}

	// Next message should be dropped (buffer full)
	msg := &Message{Type: "test", Timestamp: time.Now()}
	sent := bp.Send(msg)
	assert.False(t, sent)

	// Check stats
	stats := bp.GetStats()
	typed329, ok := stats["messages_dropped"].(int64)
	require.True(t, ok)
	assert.Positive(t, typed329)
}

// TestSubscriptionFiltering tests message filtering based on subscriptions
func TestSubscriptionFiltering(t *testing.T) {
	hub := NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go hub.Run(ctx)

	sm := NewSubscriptionManager()

	client := &Client{
		ID:        "client-1",
		ProjectID: "project-1",
		Send:      make(chan *Message, integrationClientBuffer),
		Hub:       hub,
	}

	hub.Register <- client
	time.Sleep(integrationShortSleep)

	// Subscribe with filters
	filters := map[string]interface{}{
		"event_types": []string{"created"},
	}
	_, err := sm.Subscribe(client, SubscribeToProject, "project-1", filters)
	require.NoError(t, err)

	// Test matching message
	matchingMsg := &Message{
		Type: "event",
		Event: &events.Event{
			EventType: events.EventTypeCreated,
		},
	}

	subs := sm.GetClientSubscriptions("client-1")
	matches := sm.MatchesFilter(subs[0], matchingMsg)
	assert.True(t, matches)

	// Test non-matching message
	nonMatchingMsg := &Message{
		Type: "event",
		Event: &events.Event{
			EventType: events.EventTypeUpdated,
		},
	}

	matches = sm.MatchesFilter(subs[0], nonMatchingMsg)
	assert.False(t, matches)
}

// TestPresenceCollaboration tests presence tracking for collaboration
func TestPresenceCollaboration(t *testing.T) {
	pt := NewPresenceTracker()

	// Multiple users join
	pt.Join("client-1", "user-1", "project-1")
	pt.Join("client-2", "user-2", "project-1")
	pt.Join("client-3", "user-3", "project-1")

	// Users start viewing/editing same entity
	pt.StartViewing("client-1", "entity-1", "item")
	pt.StartEditing("client-2", "entity-1", "item")
	pt.StartViewing("client-3", "entity-1", "item")

	// Check collaboration state
	viewers := pt.GetEntityViewers("entity-1")
	editors := pt.GetEntityEditors("entity-1")

	assert.Len(t, viewers, 3) // All 3 are viewing
	assert.Len(t, editors, 1) // Only 1 is editing

	// Check editor is user-2
	assert.Equal(t, "user-2", editors[0].UserID)
}

// TestReconnectionHandling tests client reconnection scenarios
func TestReconnectionHandling(t *testing.T) {
	hub := NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go hub.Run(ctx)

	// Initial connection
	client1 := &Client{
		ID:        "client-1",
		ProjectID: "project-1",
		Send:      make(chan *Message, integrationClientBuffer),
		Hub:       hub,
	}

	hub.Register <- client1
	time.Sleep(integrationShortSleep)

	// Disconnect
	hub.Unregister <- client1
	time.Sleep(integrationShortSleep)

	stats := hub.GetStats()
	assert.Equal(t, 0, stats["total_clients"])

	// Reconnect
	client2 := &Client{
		ID:        "client-2",
		ProjectID: "project-1",
		Send:      make(chan *Message, integrationClientBuffer),
		Hub:       hub,
	}

	hub.Register <- client2
	time.Sleep(integrationShortSleep)

	stats = hub.GetStats()
	assert.Equal(t, 1, stats["total_clients"])
}

// TestMultiProjectIsolation tests message isolation between projects
func TestMultiProjectIsolation(t *testing.T) {
	hub := NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go hub.Run(ctx)

	// Clients in different projects
	client1 := &Client{
		ID:        "client-1",
		ProjectID: "project-1",
		Send:      make(chan *Message, integrationClientBuffer),
		Hub:       hub,
	}

	client2 := &Client{
		ID:        "client-2",
		ProjectID: "project-2",
		Send:      make(chan *Message, integrationClientBuffer),
		Hub:       hub,
	}

	hub.Register <- client1
	hub.Register <- client2
	time.Sleep(integrationShortSleep)

	// Broadcast to project-1 only
	msg := &Message{
		Type:      "test",
		Timestamp: time.Now(),
	}
	hub.BroadcastToProject("project-1", msg)

	// Client 1 should receive
	select {
	case <-client1.Send:
		// Success
	case <-time.After(integrationShortTimeout):
		t.Fatal("Client 1 didn't receive message")
	}

	// Client 2 should NOT receive
	select {
	case <-client2.Send:
		t.Fatal("Client 2 should not have received message")
	case <-time.After(integrationTickDelay):
		// Expected timeout
	}
}

// BenchmarkFullSystem benchmarks the entire integrated system
func BenchmarkFullSystem(b *testing.B) {
	hub := NewHub()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go hub.Run(ctx)

	sm := NewSubscriptionManager()
	pt := NewPresenceTracker()

	// Create 100 clients
	clients := make([]*Client, integrationBenchmarkClients)
	for i := 0; i < integrationBenchmarkClients; i++ {
		client := &Client{
			ID:        string(rune('a' + i)),
			ProjectID: "project-1",
			Send:      make(chan *Message, integrationClientBuffer),
			Hub:       hub,
		}
		clients[i] = client
		hub.Register <- client
		_, err := sm.Subscribe(client, SubscribeToProject, "project-1", nil)
		require.NoError(b, err)
		pt.Join(client.ID, "user-"+string(rune('a'+i)), "project-1")
	}

	time.Sleep(integrationMediumSleep)

	event := events.NewEvent(
		"project-1",
		"item-1",
		events.EntityTypeItem,
		events.EventTypeCreated,
		map[string]interface{}{"title": "Test"},
	)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		hub.BroadcastEvent(event)
	}
}
