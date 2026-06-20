package websocket

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/events"
)

// TestNewConnectedMessage tests connected message creation
func TestNewConnectedMessage(t *testing.T) {
	clientID := "client-123"
	projectID := "project-456"
	msg := NewConnectedMessage(clientID, projectID)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeConnected), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, clientID, msg.Data["client_id"])
	assert.Equal(t, projectID, msg.Data["project_id"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewDisconnectedMessage tests disconnected message creation
func TestNewDisconnectedMessage(t *testing.T) {
	clientID := "client-456"
	msg := NewDisconnectedMessage(clientID)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeDisconnected), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, clientID, msg.Data["client_id"])
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
	assert.Equal(t, code, msg.Data["code"])
	assert.Equal(t, message, msg.Data["message"])
	assert.NotNil(t, msg.Data["details"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewSubscribedMessage tests subscribed message creation
func TestNewSubscribedMessage(t *testing.T) {
	resp := &SubscribeResponse{
		SubscriptionID: "sub-789",
		Type:           SubscribeToEntity,
		ResourceID:     "item-123",
		Success:        true,
	}

	msg := NewSubscribedMessage(resp)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeSubscribed), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, resp.SubscriptionID, msg.Data["subscription_id"])
	assert.Equal(t, resp.Type, msg.Data["type"])
	assert.Equal(t, resp.ResourceID, msg.Data["resource_id"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewUnsubscribedMessage tests unsubscribed message creation
func TestNewUnsubscribedMessage(t *testing.T) {
	resp := &UnsubscribeResponse{
		SubscriptionID: "sub-456",
		Success:        true,
	}

	msg := NewUnsubscribedMessage(resp)

	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeUnsubscribed), msg.Type)
	assert.NotNil(t, msg.Data)
	assert.Equal(t, resp.SubscriptionID, msg.Data["subscription_id"])
	assert.Equal(t, resp.Success, msg.Data["success"])
	assert.NotZero(t, msg.Timestamp)
}

// TestNewEventMessage tests event message creation
func TestNewEventMessage(t *testing.T) {
	event := &events.Event{
		EventType: "item.created",
		EntityID:  "item-789",
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

// TestPresenceMessages tests presence-related message creation
func TestPresenceMessages(t *testing.T) {
	presence := &PresenceActivity{
		UserID:       "user-1",
		ClientID:     "client-1",
		ProjectID:    "project-1",
		Status:       PresenceOnline,
		ConnectedAt:  time.Now(),
		LastActivity: time.Now(),
	}

	// Join message
	joinMsg := NewPresenceJoinMessage(presence)
	require.NotNil(t, joinMsg)
	assert.Equal(t, string(MessageTypePresenceJoin), joinMsg.Type)
	assert.Equal(t, presence.UserID, joinMsg.Data["user_id"])

	// Update message
	updateMsg := NewPresenceUpdateMessage(presence)
	require.NotNil(t, updateMsg)
	assert.Equal(t, string(MessageTypePresenceUpdate), updateMsg.Type)
	assert.Equal(t, presence.Status, updateMsg.Data["status"])

	// Viewing message
	viewingMsg := NewPresenceViewingMessage(presence)
	require.NotNil(t, viewingMsg)
	assert.Equal(t, string(MessageTypePresenceViewing), viewingMsg.Type)

	// Leave message
	leaveMsg := NewPresenceLeaveMessage("user-1", "client-1", "project-1")
	require.NotNil(t, leaveMsg)
	assert.Equal(t, string(MessageTypePresenceLeave), leaveMsg.Type)
	assert.Equal(t, "user-1", leaveMsg.Data["user_id"])
}
