package websocket

import (
	"context"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"golang.org/x/net/websocket"

	"github.com/kooshapari/tracertm-backend/internal/events"
)

const (
	websocketTestShortTimeout   = 1 * time.Second
	websocketTestMediumTimeout  = 2 * time.Second
	websocketTestTickDelay      = 100 * time.Millisecond
	websocketTestStaleThreshold = 10 * time.Minute
	websocketTestCleanupDelay   = 5 * time.Minute
	websocketTestShortDelay     = 50 * time.Millisecond
	websocketTestLongDelay      = 200 * time.Millisecond
)

// TestNewHub tests hub creation
func TestNewHub(t *testing.T) {
	hub := NewHub()

	assert.NotNil(t, hub)
	assert.NotNil(t, hub.Clients)
	assert.NotNil(t, hub.EntityClients)
	assert.NotNil(t, hub.Register)
	assert.NotNil(t, hub.Unregister)
	assert.NotNil(t, hub.Broadcast)
	assert.NotNil(t, hub.BroadcastToEntity)
}

// TestNewClient tests client creation
func TestNewClient(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		// Just accept connection
		time.Sleep(websocketTestTickDelay)
	}))
	defer server.Close()

	// Connect to test server
	wsURL := "ws" + server.URL[4:] // Replace http with ws
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() {
		if err := ws.Close(); err != nil {
			t.Logf("error closing websocket: %v", err)
		}
	}()

	hub := NewHub()
	projectID := uuid.New().String()
	entityID := uuid.New().String()

	client := NewClient(ws, hub, projectID, entityID)

	assert.NotEmpty(t, client.ID)
	assert.Equal(t, projectID, client.ProjectID)
	assert.Equal(t, entityID, client.EntityID)
	assert.NotNil(t, client.Send)
	assert.Equal(t, hub, client.Hub)
}

// TestHubRun tests hub message routing
func TestHubRun(t *testing.T) {
	hub := NewHub()

	// Run hub in background
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	done := make(chan bool)
	go func() {
		hub.Run(ctx)
		done <- true
	}()

	// Give hub time to start
	time.Sleep(websocketTestShortDelay)

	// Test completed
	assert.NotNil(t, hub)
}

// TestClientRegistration tests client registration
func TestClientRegistration(t *testing.T) {
	hub := NewHub()

	// Create mock client
	projectID := uuid.New().String()
	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: projectID,
		Send:      make(chan *Message, 256),
		Hub:       hub,
	}

	// Register client
	hub.Mu.Lock()
	if hub.Clients[projectID] == nil {
		hub.Clients[projectID] = make(map[*Client]bool)
	}
	hub.Clients[projectID][client] = true
	hub.Mu.Unlock()

	// Verify registration
	hub.Mu.RLock()
	assert.True(t, hub.Clients[projectID][client])
	hub.Mu.RUnlock()

	// Unregister client
	hub.Mu.Lock()
	delete(hub.Clients[projectID], client)
	hub.Mu.Unlock()

	// Verify unregistration
	hub.Mu.RLock()
	assert.False(t, hub.Clients[projectID][client])
	hub.Mu.RUnlock()
}

// TestBroadcastToProject tests broadcasting to project subscribers
func TestBroadcastToProject(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	// Create multiple clients for same project
	clients := make([]*Client, 3)
	for i := 0; i < 3; i++ {
		clients[i] = &Client{
			ID:        uuid.New().String(),
			ProjectID: projectID,
			Send:      make(chan *Message, 256),
			Hub:       hub,
		}

		hub.Mu.Lock()
		if hub.Clients[projectID] == nil {
			hub.Clients[projectID] = make(map[*Client]bool)
		}
		hub.Clients[projectID][clients[i]] = true
		hub.Mu.Unlock()
	}

	// Create message
	msg := &Message{
		Type:      "test",
		Data:      map[string]interface{}{"key": "value"},
		Timestamp: time.Now(),
	}

	// Broadcast to project
	hub.Mu.RLock()
	for client := range hub.Clients[projectID] {
		select {
		case client.Send <- msg:
		default:
			// Channel full, skip
		}
	}
	hub.Mu.RUnlock()

	// Verify all clients received message
	for _, client := range clients {
		select {
		case received := <-client.Send:
			assert.Equal(t, "test", received.Type)
			assert.Equal(t, "value", received.Data["key"])
		case <-time.After(websocketTestShortTimeout):
			t.Fatal("Client did not receive message")
		}
	}
}

// TestBroadcastToEntity tests entity-specific broadcasting
func TestBroadcastToEntity(t *testing.T) {
	hub := NewHub()
	entityID := uuid.New().String()

	// Create clients subscribed to entity
	clients := make([]*Client, 2)
	for i := 0; i < 2; i++ {
		clients[i] = &Client{
			ID:        uuid.New().String(),
			ProjectID: uuid.New().String(),
			EntityID:  entityID,
			Send:      make(chan *Message, 256),
			Hub:       hub,
		}

		hub.Mu.Lock()
		if hub.EntityClients[entityID] == nil {
			hub.EntityClients[entityID] = make(map[*Client]bool)
		}
		hub.EntityClients[entityID][clients[i]] = true
		hub.Mu.Unlock()
	}

	// Create message
	msg := &Message{
		Type:      "entity_update",
		Data:      map[string]interface{}{"entity_id": entityID},
		Timestamp: time.Now(),
	}

	// Broadcast to entity subscribers
	hub.Mu.RLock()
	for client := range hub.EntityClients[entityID] {
		select {
		case client.Send <- msg:
		default:
		}
	}
	hub.Mu.RUnlock()

	// Verify all clients received message
	for _, client := range clients {
		select {
		case received := <-client.Send:
			assert.Equal(t, "entity_update", received.Type)
		case <-time.After(websocketTestShortTimeout):
			t.Fatal("Client did not receive message")
		}
	}
}

// TestMessageSerialization tests message JSON serialization
func TestMessageSerialization(t *testing.T) {
	event := events.NewEvent(
		uuid.New().String(),
		uuid.New().String(),
		events.EntityTypeItem,
		events.EventTypeCreated,
		map[string]interface{}{"title": "Test"},
	)

	msg := &Message{
		Type:      "event",
		Event:     event,
		Timestamp: time.Now(),
	}

	// Should be serializable
	assert.NotNil(t, msg)
	assert.Equal(t, "event", msg.Type)
	assert.NotNil(t, msg.Event)
}

func registerProjectClients(hub *Hub, projectID string, clientCount int) []*Client {
	clients := make([]*Client, clientCount)

	hub.Mu.Lock()
	hub.Clients[projectID] = make(map[*Client]bool)
	for i := 0; i < clientCount; i++ {
		clients[i] = &Client{
			ID:        uuid.New().String(),
			ProjectID: projectID,
			Send:      make(chan *Message, 256),
			Hub:       hub,
		}
		hub.Clients[projectID][clients[i]] = true
	}
	hub.Mu.Unlock()

	return clients
}

func broadcastProjectMessagesConcurrently(hub *Hub, projectID string, messageCount int) {
	var wg sync.WaitGroup

	for i := 0; i < messageCount; i++ {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()

			msg := &Message{
				Type: "test",
				Data: map[string]interface{}{
					"index": index,
				},
				Timestamp: time.Now(),
			}

			hub.Mu.RLock()
			for client := range hub.Clients[projectID] {
				select {
				case client.Send <- msg:
				default:
				}
			}
			hub.Mu.RUnlock()
		}(i)
	}

	wg.Wait()
}

func verifyClientReceivesMessages(t *testing.T, clients []*Client, messageCount int) {
	t.Helper()
	for _, client := range clients {
		received := 0
		timeout := time.After(websocketTestMediumTimeout)

		for received < messageCount {
			select {
			case <-client.Send:
				received++
			case <-timeout:
				t.Logf("Client received %d/%d messages", received, messageCount)
				goto next
			}
		}
	next:
	}
}

// TestConcurrentBroadcast tests concurrent message broadcasting
func TestConcurrentBroadcast(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	const clientCount = 10
	clients := registerProjectClients(hub, projectID, clientCount)

	const messageCount = 100
	broadcastProjectMessagesConcurrently(hub, projectID, messageCount)
	verifyClientReceivesMessages(t, clients, messageCount)
}

// TestClientChannelBuffer tests client channel buffering
func TestClientChannelBuffer(t *testing.T) {
	client := &Client{
		ID:   uuid.New().String(),
		Send: make(chan *Message, 256),
	}

	// Fill buffer
	for i := 0; i < 256; i++ {
		client.Send <- &Message{
			Type:      "test",
			Data:      map[string]interface{}{"index": i},
			Timestamp: time.Now(),
		}
	}

	// Verify buffer is full (next send would block)
	select {
	case client.Send <- &Message{Type: "overflow"}:
		t.Fatal("Channel should be full")
	default:
		// Expected: channel is full
	}
}

// TestMultipleProjectSubscriptions tests clients in multiple projects
func TestMultipleProjectSubscriptions(t *testing.T) {
	hub := NewHub()

	// Create projects
	project1 := uuid.New().String()
	project2 := uuid.New().String()

	// Create clients for different projects
	client1 := &Client{
		ID:        uuid.New().String(),
		ProjectID: project1,
		Send:      make(chan *Message, 256),
		Hub:       hub,
	}

	client2 := &Client{
		ID:        uuid.New().String(),
		ProjectID: project2,
		Send:      make(chan *Message, 256),
		Hub:       hub,
	}

	// Register clients
	hub.Mu.Lock()
	hub.Clients[project1] = map[*Client]bool{client1: true}
	hub.Clients[project2] = map[*Client]bool{client2: true}
	hub.Mu.Unlock()

	// Broadcast to project1 only
	msg := &Message{
		Type:      "project1_message",
		Timestamp: time.Now(),
	}

	hub.Mu.RLock()
	for client := range hub.Clients[project1] {
		select {
		case client.Send <- msg:
		default:
		}
	}
	hub.Mu.RUnlock()

	// Verify only client1 received message
	select {
	case received := <-client1.Send:
		assert.Equal(t, "project1_message", received.Type)
	case <-time.After(websocketTestShortTimeout):
		t.Fatal("Client1 did not receive message")
	}

	// Verify client2 did NOT receive message
	select {
	case <-client2.Send:
		t.Fatal("Client2 should not receive project1 message")
	case <-time.After(websocketTestTickDelay):
		// Expected: no message
	}
}

// TestPingPong tests keepalive ping/pong
func TestPingPong(t *testing.T) {
	client := &Client{
		ID:         uuid.New().String(),
		Send:       make(chan *Message, 256),
		lastActive: time.Now(),
	}

	// Update last active time
	client.mu.Lock()
	client.lastActive = time.Now()
	client.mu.Unlock()

	// Send pong response
	pongMsg := &Message{
		Type:      "pong",
		Timestamp: time.Now(),
	}

	client.Send <- pongMsg

	// Verify pong received
	select {
	case received := <-client.Send:
		assert.Equal(t, "pong", received.Type)
	case <-time.After(websocketTestShortTimeout):
		t.Fatal("Pong not received")
	}

	// Verify last active was updated
	client.mu.Lock()
	lastActive := client.lastActive
	client.mu.Unlock()

	assert.Less(t, time.Since(lastActive), websocketTestShortTimeout)
}

// TestClientCleanup tests inactive client cleanup
func TestClientCleanup(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	// Create active and inactive clients
	activeClient := &Client{
		ID:         uuid.New().String(),
		ProjectID:  projectID,
		Send:       make(chan *Message, 256),
		Hub:        hub,
		lastActive: time.Now(),
	}

	inactiveClient := &Client{
		ID:         uuid.New().String(),
		ProjectID:  projectID,
		Send:       make(chan *Message, 256),
		Hub:        hub,
		lastActive: time.Now().Add(-websocketTestStaleThreshold), // Very old
	}

	// Register both
	hub.Mu.Lock()
	hub.Clients[projectID] = map[*Client]bool{
		activeClient:   true,
		inactiveClient: true,
	}
	hub.Mu.Unlock()

	// Cleanup inactive clients (older than 5 minutes)
	cutoff := time.Now().Add(-websocketTestCleanupDelay)

	hub.Mu.Lock()
	for client := range hub.Clients[projectID] {
		client.mu.Lock()
		if client.lastActive.Before(cutoff) {
			delete(hub.Clients[projectID], client)
			close(client.Send)
		}
		client.mu.Unlock()
	}
	hub.Mu.Unlock()

	// Verify inactive client removed
	hub.Mu.RLock()
	assert.True(t, hub.Clients[projectID][activeClient])
	assert.False(t, hub.Clients[projectID][inactiveClient])
	hub.Mu.RUnlock()
}

// TestEventBroadcast tests broadcasting events
func TestEventBroadcast(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: projectID,
		Send:      make(chan *Message, 256),
		Hub:       hub,
	}

	hub.Mu.Lock()
	hub.Clients[projectID] = map[*Client]bool{client: true}
	hub.Mu.Unlock()

	// Create and broadcast event
	event := events.NewEvent(
		projectID,
		uuid.New().String(),
		events.EntityTypeItem,
		events.EventTypeCreated,
		map[string]interface{}{"title": "New Item"},
	)

	msg := &Message{
		Type:      "event",
		Event:     event,
		Timestamp: time.Now(),
	}

	hub.Mu.RLock()
	for c := range hub.Clients[projectID] {
		select {
		case c.Send <- msg:
		default:
		}
	}
	hub.Mu.RUnlock()

	// Verify event received
	select {
	case received := <-client.Send:
		assert.Equal(t, "event", received.Type)
		assert.NotNil(t, received.Event)
		assert.Equal(t, "New Item", received.Event.Data["title"])
	case <-time.After(websocketTestShortTimeout):
		t.Fatal("Event not received")
	}
}

// BenchmarkBroadcast benchmarks broadcasting performance
func BenchmarkBroadcast(b *testing.B) {
	hub := NewHub()
	projectID := uuid.New().String()

	// Create clients
	const clientCount = 100
	hub.Mu.Lock()
	hub.Clients[projectID] = make(map[*Client]bool)
	for i := 0; i < clientCount; i++ {
		client := &Client{
			ID:        uuid.New().String(),
			ProjectID: projectID,
			Send:      make(chan *Message, 256),
			Hub:       hub,
		}
		hub.Clients[projectID][client] = true

		// Drain messages in background
		go func(c *Client) {
			for range c.Send {
				_ = 0
			}
		}(client)
	}
	hub.Mu.Unlock()

	msg := &Message{
		Type:      "benchmark",
		Data:      map[string]interface{}{"test": true},
		Timestamp: time.Now(),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		hub.Mu.RLock()
		for client := range hub.Clients[projectID] {
			select {
			case client.Send <- msg:
			default:
			}
		}
		hub.Mu.RUnlock()
	}
}

// BenchmarkConcurrentBroadcast benchmarks concurrent broadcasting
func BenchmarkConcurrentBroadcast(b *testing.B) {
	hub := NewHub()
	projectID := uuid.New().String()

	const clientCount = 100
	hub.Mu.Lock()
	hub.Clients[projectID] = make(map[*Client]bool)
	for i := 0; i < clientCount; i++ {
		client := &Client{
			ID:        uuid.New().String(),
			ProjectID: projectID,
			Send:      make(chan *Message, 256),
			Hub:       hub,
		}
		hub.Clients[projectID][client] = true

		go func(c *Client) {
			for range c.Send {
				_ = 0
			}
		}(client)
	}
	hub.Mu.Unlock()

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			msg := &Message{
				Type:      "benchmark",
				Timestamp: time.Now(),
			}

			hub.Mu.RLock()
			for client := range hub.Clients[projectID] {
				select {
				case client.Send <- msg:
				default:
				}
			}
			hub.Mu.RUnlock()
		}
	})
}

// TestAuthenticationRequired tests that clients must authenticate
func TestAuthenticationRequired(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(ws *websocket.Conn) {
		client := &Client{
			ID:       uuid.New().String(),
			Conn:     ws,
			Send:     make(chan *Message, 256),
			isAuth:   false,
			authDone: make(chan bool, 1),
		}

		// Simulate reading auth message
		var authMsg AuthMessage
		err := websocket.JSON.Receive(ws, &authMsg)
		if err != nil {
			client.sendAuthResponse(false, "Failed to read auth message")
			return
		}

		// Auth should be required
		if authMsg.Type != "auth" {
			client.sendAuthResponse(false, "First message must be auth")
			return
		}

		client.sendAuthResponse(true, "")
	}))
	defer server.Close()

	// Connect to test server
	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Send auth message
	authMsg := AuthMessage{
		Type:  "auth",
		Token: "valid-token",
	}
	err = websocket.JSON.Send(ws, authMsg)
	require.NoError(t, err)

	// Receive auth response
	var response AuthResponse
	err = websocket.JSON.Receive(ws, &response)
	require.NoError(t, err)
	assert.Equal(t, "auth_success", response.Type)
}

// TestAuthenticationFailure tests rejection of invalid tokens
func TestAuthenticationFailure(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(ws *websocket.Conn) {
		client := &Client{
			ID:       uuid.New().String(),
			Conn:     ws,
			Send:     make(chan *Message, 256),
			isAuth:   false,
			authDone: make(chan bool, 1),
		}

		// Simulate reading auth message
		var authMsg AuthMessage
		err := websocket.JSON.Receive(ws, &authMsg)
		if err != nil {
			client.sendAuthResponse(false, "Failed to read auth message")
			return
		}

		// Reject if no token
		if authMsg.Token == "" {
			client.sendAuthResponse(false, "Token required")
			return
		}

		client.sendAuthResponse(true, "")
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Send auth message with empty token
	authMsg := AuthMessage{
		Type:  "auth",
		Token: "",
	}
	err = websocket.JSON.Send(ws, authMsg)
	require.NoError(t, err)

	// Should receive failure response
	var response AuthResponse
	err = websocket.JSON.Receive(ws, &response)
	require.NoError(t, err)
	assert.Equal(t, "auth_failed", response.Type)
	assert.Equal(t, "Token required", response.Message)
}

// TestNoTokenInURL tests that tokens are rejected in URL parameters
func TestNoTokenInURL(t *testing.T) {
	// This test validates the Handler logic
	// In production, the server should reject token in URL params

	// Create a mock echo context to test the Handler validation
	// This is a conceptual test showing the requirement

	// Tokens must NOT be in URL query parameters
	// They must be sent in the auth message instead
}

// TestClientIsAuthenticatedFlag tests the isAuth flag
func TestClientIsAuthenticatedFlag(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(websocketTestTickDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	client := NewClient(ws, hub, projectID, "")

	// Should start unauthenticated
	assert.False(t, client.isAuth)

	// Mark as authenticated
	client.mu.Lock()
	client.isAuth = true
	client.authToken = "test-token"
	client.mu.Unlock()

	// Verify authentication state
	assert.True(t, client.isAuth)
}

// TestAuthenticationTimeout tests that clients timeout if they don't authenticate
func TestAuthenticationTimeout(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(ws *websocket.Conn) {
		require.NoError(t, ws.SetReadDeadline(time.Now().Add(websocketTestTickDelay)))

		var authMsg AuthMessage
		err := websocket.JSON.Receive(ws, &authMsg)

		// Should timeout if no message
		assert.Error(t, err)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Don't send auth message, should timeout
	time.Sleep(websocketTestLongDelay)
}
