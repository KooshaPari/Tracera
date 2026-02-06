package nats

import (
	"encoding/json"
	"fmt"

	natslib "github.com/nats-io/nats.go"
)

// EventPublisher publishes events to NATS
type EventPublisher struct {
	conn *natslib.Conn
}

// NewEventPublisher creates a new event publisher
func NewEventPublisher(natsURL string, credsFile string) (*EventPublisher, error) {
	conn, err := connectWithAuth(natsURL, credsFile, "", "")
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %w", err)
	}

	return &EventPublisher{conn: conn}, nil
}

// NewEventPublisherWithAuth creates a new event publisher with JWT or file-based authentication
func NewEventPublisherWithAuth(natsURL string, credsFile string, userJWT string, userNkeySeed string) (*EventPublisher, error) {
	conn, err := connectWithAuth(natsURL, credsFile, userJWT, userNkeySeed)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %w", err)
	}

	return &EventPublisher{conn: conn}, nil
}

// Event types
const (
	EventTypeItemCreated    = "item.created"
	EventTypeItemUpdated    = "item.updated"
	EventTypeItemDeleted    = "item.deleted"
	EventTypeLinkCreated    = "link.created"
	EventTypeLinkDeleted    = "link.deleted"
	EventTypeAgentCreated   = "agent.created"
	EventTypeAgentUpdated   = "agent.updated"
	EventTypeAgentDeleted   = "agent.deleted"
	EventTypeProjectCreated = "project.created"
	EventTypeProjectUpdated = "project.updated"
	EventTypeProjectDeleted = "project.deleted"
)

// Event represents a domain event
type Event struct {
	Type       string      `json:"type"`
	ProjectID  string      `json:"project_id"`
	EntityID   string      `json:"entity_id"`
	EntityType string      `json:"entity_type"`
	Data       interface{} `json:"data"`
	Timestamp  int64       `json:"timestamp"`
}

// PublishItemEvent publishes an item event
func (ep *EventPublisher) PublishItemEvent(eventType string, projectID string, itemID string, data interface{}) error {
	event := Event{
		Type:       eventType,
		ProjectID:  projectID,
		EntityID:   itemID,
		EntityType: "item",
		Data:       data,
		Timestamp:  int64(0), // Will be set by NATS
	}

	return ep.publishEvent(event)
}

// PublishLinkEvent publishes a link event
func (ep *EventPublisher) PublishLinkEvent(eventType string, projectID string, linkID string, data interface{}) error {
	event := Event{
		Type:       eventType,
		ProjectID:  projectID,
		EntityID:   linkID,
		EntityType: "link",
		Data:       data,
		Timestamp:  int64(0),
	}

	return ep.publishEvent(event)
}

// PublishAgentEvent publishes an agent event
func (ep *EventPublisher) PublishAgentEvent(eventType string, projectID string, agentID string, data interface{}) error {
	event := Event{
		Type:       eventType,
		ProjectID:  projectID,
		EntityID:   agentID,
		EntityType: "agent",
		Data:       data,
		Timestamp:  int64(0),
	}

	return ep.publishEvent(event)
}

// PublishProjectEvent publishes a project event
func (ep *EventPublisher) PublishProjectEvent(eventType string, projectID string, data interface{}) error {
	event := Event{
		Type:       eventType,
		ProjectID:  projectID,
		EntityID:   projectID,
		EntityType: "project",
		Data:       data,
		Timestamp:  int64(0),
	}

	return ep.publishEvent(event)
}

// publishEvent publishes an event to NATS
func (ep *EventPublisher) publishEvent(event Event) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	subject := fmt.Sprintf("tracertm.%s.%s", event.ProjectID, event.Type)
	if err := ep.conn.Publish(subject, data); err != nil {
		return fmt.Errorf("failed to publish event: %w", err)
	}

	return nil
}

// Close closes the NATS connection
func (ep *EventPublisher) Close() {
	if ep.conn != nil {
		ep.conn.Close()
	}
}
