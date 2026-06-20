package websocket

import (
	"time"

	"github.com/kooshapari/tracertm-backend/internal/events"
)

// MessageType represents the type of WebSocket message
type MessageType string

const (
	// MessageTypeConnected is sent when client connects.
	MessageTypeConnected MessageType = "connected"
	// MessageTypeDisconnected is sent when client disconnects.
	MessageTypeDisconnected MessageType = "disconnected"
	// MessageTypePing is a ping frame.
	MessageTypePing MessageType = "ping"
	// MessageTypePong is a pong frame.
	MessageTypePong MessageType = "pong"
	// MessageTypeError reports an error to the client.
	MessageTypeError MessageType = "error"

	// MessageTypeSubscribe is a subscription request.
	MessageTypeSubscribe MessageType = "subscribe"
	// MessageTypeUnsubscribe cancels a subscription.
	MessageTypeUnsubscribe MessageType = "unsubscribe"
	// MessageTypeSubscribed acknowledges a subscription.
	MessageTypeSubscribed MessageType = "subscribed"
	// MessageTypeUnsubscribed acknowledges an unsubscribe.
	MessageTypeUnsubscribed MessageType = "unsubscribed"
	// MessageTypeSubscriptionError reports a subscription failure.
	MessageTypeSubscriptionError MessageType = "subscription_error"

	// MessageTypeEvent carries a generic event payload.
	MessageTypeEvent MessageType = "event"
	// MessageTypeItemCreated notifies item creation.
	MessageTypeItemCreated MessageType = "item.created"
	// MessageTypeItemUpdated notifies item updates.
	MessageTypeItemUpdated MessageType = "item.updated"
	// MessageTypeItemDeleted notifies item deletion.
	MessageTypeItemDeleted MessageType = "item.deleted"
	// MessageTypeItemStatusChanged notifies status changes.
	MessageTypeItemStatusChanged MessageType = "item.status_changed"
	// MessageTypeItemPriorityChanged notifies priority changes.
	MessageTypeItemPriorityChanged MessageType = "item.priority_changed"

	// MessageTypeLinkCreated is sent when a link is created.
	MessageTypeLinkCreated MessageType = "link.created"
	// MessageTypeLinkUpdated notifies link updates.
	MessageTypeLinkUpdated MessageType = "link.updated"
	// MessageTypeLinkDeleted notifies link deletion.
	MessageTypeLinkDeleted MessageType = "link.deleted"

	// MessageTypeProjectCreated is sent when a project is created.
	MessageTypeProjectCreated MessageType = "project.created"
	// MessageTypeProjectUpdated notifies project updates.
	MessageTypeProjectUpdated MessageType = "project.updated"
	// MessageTypeProjectDeleted notifies project deletion.
	MessageTypeProjectDeleted MessageType = "project.deleted"

	// MessageTypeAgentStarted is sent when an agent starts.
	MessageTypeAgentStarted MessageType = "agent.started"
	// MessageTypeAgentStopped is sent when an agent stops.
	MessageTypeAgentStopped MessageType = "agent.stopped"
	// MessageTypeAgentActivity carries agent activity.
	MessageTypeAgentActivity MessageType = "agent.activity"
	// MessageTypeAgentError reports agent errors.
	MessageTypeAgentError MessageType = "agent.error"

	// MessageTypePresenceJoin is sent when user joins presence.
	MessageTypePresenceJoin MessageType = "presence.join"
	// MessageTypePresenceLeave is sent when user leaves presence.
	MessageTypePresenceLeave MessageType = "presence.leave"
	// MessageTypePresenceUpdate updates presence data.
	MessageTypePresenceUpdate MessageType = "presence.update"
	// MessageTypePresenceViewing indicates viewing state.
	MessageTypePresenceViewing MessageType = "presence.viewing"
	// MessageTypePresenceEditing indicates editing state.
	MessageTypePresenceEditing MessageType = "presence.editing"

	// MessageTypeSnapshot carries full state snapshot.
	MessageTypeSnapshot MessageType = "snapshot"
	// MessageTypeRollback indicates a rollback event.
	MessageTypeRollback MessageType = "rollback"
	// MessageTypeSync synchronizes client state.
	MessageTypeSync MessageType = "sync"

	// MessageTypeHeartbeat is a keepalive ping.
	MessageTypeHeartbeat MessageType = "heartbeat"
	// MessageTypeStats reports runtime stats.
	MessageTypeStats MessageType = "stats"
	// MessageTypeAck acknowledges a message.
	MessageTypeAck MessageType = "ack"
)

// SubscribeRequest represents a subscription request from a client
type SubscribeRequest struct {
	Type        SubscriptionType       `json:"type"`
	ResourceID  string                 `json:"resource_id,omitempty"`
	ResourceIDs []string               `json:"resource_ids,omitempty"`
	Filters     map[string]interface{} `json:"filters,omitempty"`
}

// SubscribeResponse represents a subscription response to a client
type SubscribeResponse struct {
	SubscriptionID string                 `json:"subscription_id"`
	Type           SubscriptionType       `json:"type"`
	ResourceID     string                 `json:"resource_id,omitempty"`
	ResourceIDs    []string               `json:"resource_ids,omitempty"`
	Filters        map[string]interface{} `json:"filters,omitempty"`
	Success        bool                   `json:"success"`
	Error          string                 `json:"error,omitempty"`
}

// UnsubscribeRequest represents an unsubscribe request
type UnsubscribeRequest struct {
	SubscriptionID string `json:"subscription_id"`
}

// UnsubscribeResponse represents an unsubscribe response
type UnsubscribeResponse struct {
	SubscriptionID string `json:"subscription_id"`
	Success        bool   `json:"success"`
	Error          string `json:"error,omitempty"`
}

// PresenceMessage represents a presence-related message
type PresenceMessage struct {
	Action     string                 `json:"action"` // join, leave, update, viewing, editing
	UserID     string                 `json:"user_id"`
	ProjectID  string                 `json:"project_id"`
	EntityID   string                 `json:"entity_id,omitempty"`
	EntityType string                 `json:"entity_type,omitempty"`
	Status     PresenceStatus         `json:"status,omitempty"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
}

// ErrorMessage represents an error message
type ErrorMessage struct {
	Code    string                 `json:"code"`
	Message string                 `json:"message"`
	Details map[string]interface{} `json:"details,omitempty"`
}

// StatsMessage represents system statistics
type StatsMessage struct {
	Clients       int                    `json:"clients"`
	Projects      int                    `json:"projects"`
	Subscriptions int                    `json:"subscriptions"`
	Presence      int                    `json:"presence"`
	Details       map[string]interface{} `json:"details,omitempty"`
}

// AckMessage represents an acknowledgment message
type AckMessage struct {
	MessageID string `json:"message_id"`
	Success   bool   `json:"success"`
	Error     string `json:"error,omitempty"`
}

// NewConnectedMessage creates a connected message
func NewConnectedMessage(clientID, projectID string) *Message {
	return &Message{
		Type: string(MessageTypeConnected),
		Data: map[string]interface{}{
			"client_id":  clientID,
			"project_id": projectID,
			"timestamp":  time.Now().UTC(),
		},
		Timestamp: time.Now(),
	}
}

// NewDisconnectedMessage creates a disconnected message
func NewDisconnectedMessage(clientID string) *Message {
	return &Message{
		Type: string(MessageTypeDisconnected),
		Data: map[string]interface{}{
			"client_id": clientID,
			"timestamp": time.Now().UTC(),
		},
		Timestamp: time.Now(),
	}
}

// NewErrorMessage creates an error message
func NewErrorMessage(code, message string, details map[string]interface{}) *Message {
	return &Message{
		Type: string(MessageTypeError),
		Data: map[string]interface{}{
			"code":    code,
			"message": message,
			"details": details,
		},
		Timestamp: time.Now(),
	}
}

// NewSubscribedMessage creates a subscribed confirmation message
func NewSubscribedMessage(response *SubscribeResponse) *Message {
	return &Message{
		Type: string(MessageTypeSubscribed),
		Data: map[string]interface{}{
			"subscription_id": response.SubscriptionID,
			"type":            response.Type,
			"resource_id":     response.ResourceID,
			"resource_ids":    response.ResourceIDs,
			"filters":         response.Filters,
			"success":         response.Success,
		},
		Timestamp: time.Now(),
	}
}

// NewUnsubscribedMessage creates an unsubscribed confirmation message
func NewUnsubscribedMessage(response *UnsubscribeResponse) *Message {
	return &Message{
		Type: string(MessageTypeUnsubscribed),
		Data: map[string]interface{}{
			"subscription_id": response.SubscriptionID,
			"success":         response.Success,
		},
		Timestamp: time.Now(),
	}
}

// NewEventMessage creates an event message from an event
func NewEventMessage(event *events.Event) *Message {
	return &Message{
		Type:      string(MessageTypeEvent),
		Event:     event,
		Timestamp: time.Now(),
	}
}

// NewPresenceJoinMessage creates a presence join message
func NewPresenceJoinMessage(presence *PresenceActivity) *Message {
	return &Message{
		Type: string(MessageTypePresenceJoin),
		Data: map[string]interface{}{
			"user_id":    presence.UserID,
			"client_id":  presence.ClientID,
			"project_id": presence.ProjectID,
			"status":     presence.Status,
			"timestamp":  presence.ConnectedAt,
		},
		Timestamp: time.Now(),
	}
}

// NewPresenceLeaveMessage creates a presence leave message
func NewPresenceLeaveMessage(userID, clientID, projectID string) *Message {
	return &Message{
		Type: string(MessageTypePresenceLeave),
		Data: map[string]interface{}{
			"user_id":    userID,
			"client_id":  clientID,
			"project_id": projectID,
			"timestamp":  time.Now().UTC(),
		},
		Timestamp: time.Now(),
	}
}

// NewPresenceUpdateMessage creates a presence update message
func NewPresenceUpdateMessage(presence *PresenceActivity) *Message {
	return &Message{
		Type: string(MessageTypePresenceUpdate),
		Data: map[string]interface{}{
			"user_id":     presence.UserID,
			"client_id":   presence.ClientID,
			"status":      presence.Status,
			"entity_id":   presence.EntityID,
			"entity_type": presence.EntityType,
			"timestamp":   presence.LastActivity,
		},
		Timestamp: time.Now(),
	}
}

// NewPresenceViewingMessage creates a presence viewing message
func NewPresenceViewingMessage(presence *PresenceActivity) *Message {
	return &Message{
		Type: string(MessageTypePresenceViewing),
		Data: map[string]interface{}{
			"user_id":     presence.UserID,
			"client_id":   presence.ClientID,
			"entity_id":   presence.EntityID,
			"entity_type": presence.EntityType,
			"timestamp":   presence.LastActivity,
		},
		Timestamp: time.Now(),
	}
}

// NewPresenceEditingMessage creates a presence editing message
func NewPresenceEditingMessage(presence *PresenceActivity) *Message {
	return &Message{
		Type: string(MessageTypePresenceEditing),
		Data: map[string]interface{}{
			"user_id":     presence.UserID,
			"client_id":   presence.ClientID,
			"entity_id":   presence.EntityID,
			"entity_type": presence.EntityType,
			"timestamp":   presence.LastActivity,
		},
		Timestamp: time.Now(),
	}
}

// NewStatsMessage creates a stats message
func NewStatsMessage(stats map[string]interface{}) *Message {
	return &Message{
		Type:      string(MessageTypeStats),
		Data:      stats,
		Timestamp: time.Now(),
	}
}

// NewAckMessage creates an acknowledgment message
func NewAckMessage(messageID string, success bool, err string) *Message {
	return &Message{
		Type: string(MessageTypeAck),
		Data: map[string]interface{}{
			"message_id": messageID,
			"success":    success,
			"error":      err,
		},
		Timestamp: time.Now(),
	}
}

// MessageRouter routes messages to appropriate handlers
type MessageRouter struct {
	handlers map[MessageType]MessageHandler
}

// MessageHandler handles a specific message type
type MessageHandler func(*Client, *Message) error

// NewMessageRouter creates a new message router
func NewMessageRouter() *MessageRouter {
	return &MessageRouter{
		handlers: make(map[MessageType]MessageHandler),
	}
}

// Register registers a handler for a message type
func (mr *MessageRouter) Register(msgType MessageType, handler MessageHandler) {
	mr.handlers[msgType] = handler
}

// Route routes a message to the appropriate handler
func (mr *MessageRouter) Route(client *Client, msg *Message) error {
	handler, ok := mr.handlers[MessageType(msg.Type)]
	if !ok {
		return nil // No handler, ignore
	}

	return handler(client, msg)
}
