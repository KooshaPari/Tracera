package nats

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

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

const (
	notificationStreamName = "TRACERTM_NOTIFICATIONS"
	notificationSubject    = "tracertm.notifications"
	notificationMaxAge     = 24 * time.Hour
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

// PublishNotification publishes a user notification event through JetStream.
func (ep *EventPublisher) PublishNotification(userID string, data interface{}) error {
	if userID == "" {
		return fmt.Errorf("notification user ID is required")
	}
	if ep == nil || ep.conn == nil {
		return fmt.Errorf("NATS event publisher is not configured")
	}

	js, err := ep.notificationJetStream()
	if err != nil {
		return err
	}

	payload, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal notification event: %w", err)
	}

	subject := fmt.Sprintf("%s.%s", notificationSubject, sanitizeSubjectToken(userID))
	if _, err := js.Publish(subject, payload); err != nil {
		return fmt.Errorf("failed to publish notification event: %w", err)
	}

	return nil
}

// SubscribeNotifications subscribes to all notification events for this process.
func (ep *EventPublisher) SubscribeNotifications(handler func(userID string, data []byte)) (func() error, error) {
	if ep == nil || ep.conn == nil {
		return nil, fmt.Errorf("NATS event publisher is not configured")
	}
	if handler == nil {
		return nil, fmt.Errorf("notification handler is required")
	}

	js, err := ep.notificationJetStream()
	if err != nil {
		return nil, err
	}

	subject := notificationSubject + ".>"
	durable := notificationDurableName()
	sub, err := js.Subscribe(subject, func(msg *natslib.Msg) {
		userID := notificationUserID(msg.Subject)
		handler(userID, msg.Data)
		if err := msg.Ack(); err != nil {
			// Ack failures are surfaced through NATS redelivery; keep handler non-blocking.
			return
		}
	}, natslib.Durable(durable), natslib.ManualAck())
	if err != nil {
		return nil, fmt.Errorf("failed to subscribe to notification events: %w", err)
	}

	return sub.Unsubscribe, nil
}

func (ep *EventPublisher) notificationJetStream() (natslib.JetStreamContext, error) {
	js, err := ep.conn.JetStream()
	if err != nil {
		return nil, fmt.Errorf("failed to create JetStream context: %w", err)
	}

	cfg := &natslib.StreamConfig{
		Name:      notificationStreamName,
		Subjects:  []string{notificationSubject + ".>"},
		Retention: natslib.InterestPolicy,
		Storage:   natslib.FileStorage,
		MaxAge:    notificationMaxAge,
		Replicas:  1,
	}
	if _, err := js.AddStream(cfg); err != nil {
		if _, updateErr := js.UpdateStream(cfg); updateErr != nil {
			return nil, fmt.Errorf("failed to ensure notification stream: %w", updateErr)
		}
	}

	return js, nil
}

func notificationDurableName() string {
	host, err := os.Hostname()
	if err != nil || host == "" {
		host = "local"
	}
	return sanitizeSubjectToken(fmt.Sprintf("notification-service-%s-%d", host, os.Getpid()))
}

func notificationUserID(subject string) string {
	prefix := notificationSubject + "."
	return strings.TrimPrefix(subject, prefix)
}

func sanitizeSubjectToken(value string) string {
	replacer := strings.NewReplacer(".", "_", ">", "_", "*", "_", " ", "_")
	return replacer.Replace(value)
}

// Close closes the NATS connection
func (ep *EventPublisher) Close() {
	if ep.conn != nil {
		ep.conn.Close()
	}
}
