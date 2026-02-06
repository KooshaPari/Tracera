package websocket

import (
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestNewConnectedMessage tests connected message creation
func TestNewConnectedMessage(t *testing.T) {
	clientID := "client-123"
	msg := NewConnectedMessage(clientID)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeConnected), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, clientID, msg.Data["client_id"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewDisconnectedMessage tests disconnected message creation
func TestNewDisconnectedMessage(t *testing.T) {
	clientID := "client-456"
	reason := "connection_timeout"
	msg := NewDisconnectedMessage(clientID, reason)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeDisconnected), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, clientID, msg.Data["client_id"])
	assert.Equal(t, reason, msg.Data["reason"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewErrorMessage tests error message creation
func TestNewErrorMessage(t *testing.T) {
	code := "ERR_AUTH_FAILED"
	message := "Authentication failed"
	details := map[string]interface{}{
		"attempt": 3,
		"max":     5,
	}
	msg := NewErrorMessage(code, message, details)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeError), msg.Type)
	assert.NotNil(t, msg.Data)

	errorData := msg.Data["error"].(map[string]interface{})
	assert.Equal(t, code, errorData["code"])
	assert.Equal(t, message, errorData["message"])
	assert.NotNil(t, errorData["details"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewSubscribedMessage tests subscribed message creation
func TestNewSubscribedMessage(t *testing.T) {
	subscriptionID := "sub-789"
	resourceType := SubscriptionTypeItem
	resourceID := "item-123"

	msg := NewSubscribedMessage(subscriptionID, resourceType, resourceID)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeSubscribed), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, subscriptionID, msg.Data["subscription_id"])
	assert.Equal(t, string(resourceType), msg.Data["resource_type"])
	assert.Equal(t, resourceID, msg.Data["resource_id"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewUnsubscribedMessage tests unsubscribed message creation
func TestNewUnsubscribedMessage(t *testing.T) {
	subscriptionID := "sub-456"
	success := true

	msg := NewUnsubscribedMessage(subscriptionID, success)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeUnsubscribed), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, subscriptionID, msg.Data["subscription_id"])
	assert.Equal(t, success, msg.Data["success"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewEventMessage tests event message creation
func TestNewEventMessage(t *testing.T) {
	event := &events.Event{
		Type:     "item.created",
		EntityID: "item-789",
		Data: map[string]interface{}{
			"title": "New Item",
		},
	}

	msg := NewEventMessage(event)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeEvent), msg.Type)
	assert.Equal(t, event, msg.Event)
	assert.NotZero(t, msg.Timestamp)
}

// TestNewPresenceJoinMessage tests presence join message creation
func TestNewPresenceJoinMessage(t *testing.T) {
	userID := "user-123"
	projectID := "proj-456"
	entityID := "item-789"

	msg := NewPresenceJoinMessage(userID, projectID, entityID)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypePresenceJoin), msg.Type)
	assert.NotNil(t, msg.Data)

	presence := msg.Data["presence"].(map[string]interface{})
	assert.Equal(t, userID, presence["user_id"])
	assert.Equal(t, projectID, presence["project_id"])
	assert.Equal(t, entityID, presence["entity_id"])
	assert.Equal(t, "join", presence["action"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewPresenceLeaveMessage tests presence leave message creation
func TestNewPresenceLeaveMessage(t *testing.T) {
	userID := "user-456"
	projectID := "proj-789"
	entityID := "item-123"

	msg := NewPresenceLeaveMessage(userID, projectID, entityID)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypePresenceLeave), msg.Type)
	assert.NotNil(t, msg.Data)

	presence := msg.Data["presence"].(map[string]interface{})
	assert.Equal(t, userID, presence["user_id"])
	assert.Equal(t, projectID, presence["project_id"])
	assert.Equal(t, entityID, presence["entity_id"])
	assert.Equal(t, "leave", presence["action"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewPresenceUpdateMessage tests presence update message creation
func TestNewPresenceUpdateMessage(t *testing.T) {
	userID := "user-789"
	projectID := "proj-123"
	status := PresenceStatusActive
	metadata := map[string]interface{}{
		"cursor_position": "line:42",
	}

	msg := NewPresenceUpdateMessage(userID, projectID, status, metadata)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypePresenceUpdate), msg.Type)
	assert.NotNil(t, msg.Data)

	presence := msg.Data["presence"].(map[string]interface{})
	assert.Equal(t, userID, presence["user_id"])
	assert.Equal(t, projectID, presence["project_id"])
	assert.Equal(t, string(status), presence["status"])
	assert.Equal(t, metadata, presence["metadata"])
	assert.Equal(t, "update", presence["action"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewPresenceViewingMessage tests presence viewing message creation
func TestNewPresenceViewingMessage(t *testing.T) {
	userID := "user-123"
	projectID := "proj-456"
	entityID := "item-789"
	entityType := "item"

	msg := NewPresenceViewingMessage(userID, projectID, entityID, entityType)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypePresenceViewing), msg.Type)
	assert.NotNil(t, msg.Data)

	presence := msg.Data["presence"].(map[string]interface{})
	assert.Equal(t, userID, presence["user_id"])
	assert.Equal(t, projectID, presence["project_id"])
	assert.Equal(t, entityID, presence["entity_id"])
	assert.Equal(t, entityType, presence["entity_type"])
	assert.Equal(t, "viewing", presence["action"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewPresenceEditingMessage tests presence editing message creation
func TestNewPresenceEditingMessage(t *testing.T) {
	userID := "user-456"
	projectID := "proj-789"
	entityID := "item-123"
	entityType := "requirement"

	msg := NewPresenceEditingMessage(userID, projectID, entityID, entityType)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypePresenceEditing), msg.Type)
	assert.NotNil(t, msg.Data)

	presence := msg.Data["presence"].(map[string]interface{})
	assert.Equal(t, userID, presence["user_id"])
	assert.Equal(t, projectID, presence["project_id"])
	assert.Equal(t, entityID, presence["entity_id"])
	assert.Equal(t, entityType, presence["entity_type"])
	assert.Equal(t, "editing", presence["action"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewStatsMessage tests stats message creation
func TestNewStatsMessage(t *testing.T) {
	clients := 42
	projects := 10
	subscriptions := 150
	presence := 25

	msg := NewStatsMessage(clients, projects, subscriptions, presence)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeStats), msg.Type)
	assert.NotNil(t, msg.Data)

	stats := msg.Data["stats"].(map[string]interface{})
	assert.Equal(t, clients, stats["clients"])
	assert.Equal(t, projects, stats["projects"])
	assert.Equal(t, subscriptions, stats["subscriptions"])
	assert.Equal(t, presence, stats["presence"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewAckMessage tests acknowledgment message creation
func TestNewAckMessage(t *testing.T) {
	messageID := "msg-789"
	success := true

	msg := NewAckMessage(messageID, success)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeAck), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, messageID, msg.Data["message_id"])
	assert.Equal(t, success, msg.Data["success"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewMessageRouter tests message router creation
func TestNewMessageRouter(t *testing.T) {
	router := NewMessageRouter()

	require.NotNil(t, router)
	assert.NotNil(t, router.handlers)
	assert.Equal(t, 0, len(router.handlers))
}

// TestMessageRouter_Register tests handler registration
func TestMessageRouter_Register(t *testing.T) {
	router := NewMessageRouter()

	called := false
	handler := func(c *Client, m *Message) error {
		called = true
		return nil
	}

	router.Register(MessageTypeConnected, handler)
	assert.Equal(t, 1, len(router.handlers))

	// Verify handler is registered
	registeredHandler, exists := router.handlers[MessageTypeConnected]
	assert.True(t, exists)
	assert.NotNil(t, registeredHandler)

	// Call handler to verify it works
	err := registeredHandler(nil, nil)
	assert.NoError(t, err)
	assert.True(t, called)
}

// TestMessageRouter_Route tests message routing
func TestMessageRouter_Route(t *testing.T) {
	router := NewMessageRouter()

	receivedMsg := (*Message)(nil)
	receivedClient := (*Client)(nil)

	handler := func(c *Client, m *Message) error {
		receivedClient = c
		receivedMsg = m
		return nil
	}

	router.Register(MessageTypeConnected, handler)

	client := &Client{
		ID:        "client-123",
		ProjectID: "proj-456",
	}
	msg := &Message{
		Type:      string(MessageTypeConnected),
		Timestamp: time.Now(),
	}

	err := router.Route(client, msg)
	assert.NoError(t, err)
	assert.Equal(t, client, receivedClient)
	assert.Equal(t, msg, receivedMsg)
}

// TestMessageRouter_Route_UnhandledMessage tests routing unhandled message
func TestMessageRouter_Route_UnhandledMessage(t *testing.T) {
	router := NewMessageRouter()

	client := &Client{
		ID:        "client-123",
		ProjectID: "proj-456",
	}
	msg := &Message{
		Type:      string(MessageTypeConnected),
		Timestamp: time.Now(),
	}

	// No handler registered, should return error
	err := router.Route(client, msg)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "no handler")
}
