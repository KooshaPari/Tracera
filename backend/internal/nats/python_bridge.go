package nats

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	natslib "github.com/nats-io/nats.go"

	"github.com/kooshapari/tracertm-backend/internal/events"
)

const pythonBridgeStreamMaxAge = 7 * 24 * time.Hour

// PythonBridge handles bidirectional event communication between Go and Python backends
type PythonBridge struct {
	js            natslib.JetStreamContext
	conn          *natslib.Conn
	subscriptions map[string]*natslib.Subscription
	streamName    string
	subjectPrefix string
}

// Subject hierarchy constants
const (
	// Go-originated events (published by Go, consumed by Python)
	SubjectItemCreated    = "item.created"
	SubjectItemUpdated    = "item.updated"
	SubjectItemDeleted    = "item.deleted"
	SubjectLinkCreated    = "link.created"
	SubjectLinkDeleted    = "link.deleted"
	SubjectProjectCreated = "project.created"
	SubjectProjectUpdated = "project.updated"
	SubjectProjectDeleted = "project.deleted"

	// Python-originated events (published by Python, consumed by Go)
	SubjectSpecCreated        = "spec.created"
	SubjectSpecUpdated        = "spec.updated"
	SubjectSpecDeleted        = "spec.deleted"
	SubjectAIAnalysisComplete = "ai.analysis.complete"
	SubjectExecutionCompleted = "execution.completed"
	SubjectExecutionFailed    = "execution.failed"
	SubjectWorkflowCompleted  = "workflow.completed"
)

// BridgeEvent represents a cross-backend event
type BridgeEvent struct {
	Type       string                 `json:"type"`
	ProjectID  string                 `json:"project_id"`
	EntityID   string                 `json:"entity_id"`
	EntityType string                 `json:"entity_type"`
	Data       map[string]interface{} `json:"data"`
	Source     string                 `json:"source"` // "go" or "python"
}

// NewPythonBridge creates a new Python bridge for cross-backend communication
func NewPythonBridge(conn *natslib.Conn) (*PythonBridge, error) {
	// Create JetStream context
	js, err := conn.JetStream()
	if err != nil {
		return nil, fmt.Errorf("failed to create JetStream context: %w", err)
	}

	bridge := &PythonBridge{
		js:            js,
		conn:          conn,
		subscriptions: make(map[string]*natslib.Subscription),
		streamName:    "TRACERTM_BRIDGE",
		subjectPrefix: "tracertm.bridge",
	}

	// Ensure the stream exists
	if err := bridge.ensureStream(); err != nil {
		return nil, fmt.Errorf("failed to ensure stream: %w", err)
	}

	return bridge, nil
}

// ensureStream creates or updates the JetStream stream for bridge events
func (pb *PythonBridge) ensureStream() error {
	streamConfig := &natslib.StreamConfig{
		Name:      pb.streamName,
		Subjects:  []string{pb.subjectPrefix + ".>"},
		Retention: natslib.InterestPolicy,
		Storage:   natslib.FileStorage,
		MaxAge:    pythonBridgeStreamMaxAge,
		Replicas:  1,
	}

	// Try to add the stream, update if it already exists
	_, err := pb.js.AddStream(streamConfig)
	if err != nil {
		// Try to update if it exists
		_, err = pb.js.UpdateStream(streamConfig)
		if err != nil {
			return fmt.Errorf("failed to add/update stream: %w", err)
		}
	}

	return nil
}

// buildSubject constructs the subject pattern for an event
// Format: tracertm.bridge.{source}.{project_id}.{event_type}
func (pb *PythonBridge) buildSubject(source, projectID, eventType string) string {
	return pb.subjectPrefix + "." + source + "." + projectID + "." + eventType
}

// PublishPythonEvent publishes an event to Python backend
func (pb *PythonBridge) PublishPythonEvent(eventType, projectID, entityID, entityType string, data map[string]interface{}) error {
	subject := pb.buildSubject("go", projectID, eventType)

	event := BridgeEvent{
		Type:       eventType,
		ProjectID:  projectID,
		EntityID:   entityID,
		EntityType: entityType,
		Data:       data,
		Source:     "go",
	}

	payload, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	// Publish to JetStream
	ack, err := pb.js.Publish(subject, payload)
	if err != nil {
		return fmt.Errorf("failed to publish to JetStream: %w", err)
	}

	slog.Info("Published event to (stream= , seq= )", "detail", eventType, "detail", subject, "detail", ack.Stream, "value", ack.Sequence)
	return nil
}

// SubscribeToPythonEvents subscribes to events from Python backend with a durable subscription
func (pb *PythonBridge) SubscribeToPythonEvents(handler func(*BridgeEvent)) error {
	// Subscribe to all Python-originated events: tracertm.bridge.python.>
	subject := pb.subjectPrefix + ".python.>"
	durableName := "go-python-events"

	sub, err := pb.js.Subscribe(subject, func(msg *natslib.Msg) {
		var event BridgeEvent
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			slog.Error("Failed to unmarshal bridge event", "error", err)
			return
		}

		// Call the handler
		handler(&event)

		// Acknowledge the message
		if err := msg.Ack(); err != nil {
			slog.Error("Failed to acknowledge message", "error", err)
		}
	}, natslib.Durable(durableName), natslib.ManualAck())
	if err != nil {
		return fmt.Errorf("failed to subscribe to Python events: %w", err)
	}

	pb.subscriptions[durableName] = sub
	return nil
}

// SubscribeToEventType subscribes to a specific event type from Python
func (pb *PythonBridge) SubscribeToEventType(eventType string, handler func(*BridgeEvent)) error {
	// Subscribe to: tracertm.bridge.python.*.{eventType}
	subject := pb.subjectPrefix + ".python.*." + eventType
	durableName := "go-" + eventType

	sub, err := pb.js.Subscribe(subject, func(msg *natslib.Msg) {
		var event BridgeEvent
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			slog.Error("Failed to unmarshal bridge event", "error", err)
			return
		}

		// Call the handler
		handler(&event)

		// Acknowledge the message
		if err := msg.Ack(); err != nil {
			slog.Error("Failed to acknowledge message", "error", err)
		}
	}, natslib.Durable(durableName), natslib.ManualAck())
	if err != nil {
		return fmt.Errorf("failed to subscribe to event type %s: %w", eventType, err)
	}

	pb.subscriptions[durableName] = sub
	slog.Info("Subscribed to Python event type with durable consumer", "type", eventType, "name", durableName)
	return nil
}

// PublishItemEvent publishes an item event to Python
func (pb *PythonBridge) PublishItemEvent(eventType, projectID, itemID string, data map[string]interface{}) error {
	return pb.PublishPythonEvent(eventType, projectID, itemID, "item", data)
}

// PublishLinkEvent publishes a link event to Python
func (pb *PythonBridge) PublishLinkEvent(eventType, projectID, linkID string, data map[string]interface{}) error {
	return pb.PublishPythonEvent(eventType, projectID, linkID, "link", data)
}

// PublishProjectEvent publishes a project event to Python
func (pb *PythonBridge) PublishProjectEvent(eventType, projectID string, data map[string]interface{}) error {
	return pb.PublishPythonEvent(eventType, projectID, projectID, "project", data)
}

// ConvertEventToBridge converts a standard Event to a BridgeEvent
func (pb *PythonBridge) ConvertEventToBridge(event *events.Event) *BridgeEvent {
	return &BridgeEvent{
		Type:       string(event.EventType),
		ProjectID:  event.ProjectID,
		EntityID:   event.EntityID,
		EntityType: string(event.EntityType),
		Data:       event.Data,
		Source:     "go",
	}
}

// PublishEvent publishes a standard Event to Python
func (pb *PythonBridge) PublishEvent(event *events.Event) error {
	bridgeEvent := pb.ConvertEventToBridge(event)
	return pb.PublishPythonEvent(
		bridgeEvent.Type,
		bridgeEvent.ProjectID,
		bridgeEvent.EntityID,
		bridgeEvent.EntityType,
		bridgeEvent.Data,
	)
}

// Unsubscribe removes a subscription
func (pb *PythonBridge) Unsubscribe(durableName string) error {
	sub, exists := pb.subscriptions[durableName]
	if !exists {
		return fmt.Errorf("subscription not found: %s", durableName)
	}

	if err := sub.Unsubscribe(); err != nil {
		return fmt.Errorf("failed to unsubscribe: %w", err)
	}

	delete(pb.subscriptions, durableName)
	slog.Info("Unsubscribed from", "name", durableName)
	return nil
}

// Close closes all subscriptions
func (pb *PythonBridge) Close() error {
	for name, sub := range pb.subscriptions {
		if err := sub.Unsubscribe(); err != nil {
			slog.Error("Error unsubscribing from", "error", name, "error", err)
		}
	}
	return nil
}
