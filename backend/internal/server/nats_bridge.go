package server

import (
	"encoding/json"
	"log/slog"
	"strings"
	"time"

	natslib "github.com/nats-io/nats.go"

	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/websocket"
)

// setupNATSToWebSocketBridge subscribes to NATS events and forwards them to WebSocket clients
func (s *Server) setupNATSToWebSocketBridge() {
	if s.infra.NATS == nil {
		slog.Warn("⚠️  NATS not available, skipping WebSocket bridge")
		return
	}

	// Create Python bridge for cross-backend events
	bridge, err := nats.NewPythonBridge(s.infra.NATS.GetConnection())
	if err != nil {
		slog.Error("⚠️ Failed to create Python bridge", "error", err)
		return
	}

	// Subscribe to all Python-originated events
	err = bridge.SubscribeToPythonEvents(func(event *nats.BridgeEvent) {
		// Convert BridgeEvent to NATSEvent
		natsEvent := &websocket.NATSEvent{
			EventType:  event.Type,
			ProjectID:  event.ProjectID,
			EntityID:   event.EntityID,
			EntityType: event.EntityType,
			Data:       event.Data,
			Timestamp:  time.Now().Format(time.RFC3339),
			Source:     event.Source,
		}

		// Forward to WebSocket hub
		s.wsHub.HandleNATSEvent(natsEvent)
	})
	if err != nil {
		slog.Error("⚠️ Failed to subscribe to Python events", "error", err)
		return
	}

	// Also subscribe to Go-originated events for completeness
	// This allows frontend to receive all events regardless of backend source

	// Item events
	subscribeToEventPattern(s.infra.NATS.GetConnection(), "tracertm.bridge.go.*.item.created", s.wsHub)
	subscribeToEventPattern(s.infra.NATS.GetConnection(), "tracertm.bridge.go.*.item.updated", s.wsHub)
	subscribeToEventPattern(s.infra.NATS.GetConnection(), "tracertm.bridge.go.*.item.deleted", s.wsHub)

	// Link events
	subscribeToEventPattern(s.infra.NATS.GetConnection(), "tracertm.bridge.go.*.link.created", s.wsHub)
	subscribeToEventPattern(s.infra.NATS.GetConnection(), "tracertm.bridge.go.*.link.deleted", s.wsHub)

	// Project events
	subscribeToEventPattern(s.infra.NATS.GetConnection(), "tracertm.bridge.go.*.project.*", s.wsHub)
}

// subscribeToEventPattern is a helper to subscribe to NATS event patterns
func subscribeToEventPattern(conn *natslib.Conn, subject string, hub *websocket.Hub) {
	js, err := conn.JetStream()
	if err != nil {
		slog.Error("⚠️ Failed to create JetStream context for", "error", subject, "error", err)
		return
	}

	// Sanitize consumer name: replace wildcards (*) and dots (.) with underscores
	// NATS consumer names must be valid identifiers (no wildcards or special chars)
	consumerName := "ws-bridge-" + subject
	consumerName = strings.ReplaceAll(consumerName, "*", "_")
	consumerName = strings.ReplaceAll(consumerName, ".", "_")

	_, err = js.Subscribe(subject, func(msg *natslib.Msg) {
		// Parse the bridge event
		var event nats.BridgeEvent
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			slog.Error("Failed to unmarshal NATS event", "error", err)
			if ackErr := msg.Ack(); ackErr != nil {
				slog.Warn("failed to ack NATS message", "error", ackErr)
			}
			return
		}

		// Convert to NATSEvent
		natsEvent := &websocket.NATSEvent{
			EventType:  event.Type,
			ProjectID:  event.ProjectID,
			EntityID:   event.EntityID,
			EntityType: event.EntityType,
			Data:       event.Data,
			Timestamp:  time.Now().Format(time.RFC3339),
			Source:     event.Source,
		}

		// Forward to WebSocket hub
		hub.HandleNATSEvent(natsEvent)

		// Acknowledge message
		if ackErr := msg.Ack(); ackErr != nil {
			slog.Warn("failed to ack NATS message", "error", ackErr)
		}
	}, natslib.Durable(consumerName), natslib.ManualAck())
	if err != nil {
		slog.Error("⚠️ Failed to subscribe to", "error", subject, "error", err)
	}
}
