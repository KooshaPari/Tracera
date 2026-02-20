// Package integration provides integration orchestration.
package integration

import (
	"context"
	"errors"
	"fmt"
	"log/slog"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/websocket"
)

const exampleItemPriorityDefault = 50

// EventSystem integrates event store, NATS pub/sub, and WebSocket broadcasting
type EventSystem struct {
	Store       events.EventStore
	NATSBus     *nats.EventBus
	WSHub       *websocket.Hub
	Broadcaster *websocket.EventBroadcaster
}

// NewEventSystem creates a fully integrated event sourcing and real-time system
func NewEventSystem(pool *pgxpool.Pool, natsConfig *nats.Config) (*EventSystem, error) {
	// Create event store
	store := events.NewPostgresEventStore(pool)

	// Create NATS event bus
	natsBus, err := nats.NewEventBus(natsConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create NATS bus: %w", err)
	}

	// Create WebSocket hub
	hub := websocket.NewHub()

	// Create broadcaster
	broadcaster := websocket.NewEventBroadcaster(hub)

	return &EventSystem{
		Store:       store,
		NATSBus:     natsBus,
		WSHub:       hub,
		Broadcaster: broadcaster,
	}, nil
}

// Start starts the event system
func (es *EventSystem) Start(ctx context.Context) {
	// Start WebSocket hub
	go es.WSHub.Run(ctx)

	// Subscribe to NATS events and broadcast to WebSocket clients
	err := es.NATSBus.Subscribe(func(event *events.Event) {
		if err := es.Broadcaster.PublishToProject(event.ProjectID, event); err != nil {
			slog.Error("Failed to publish event to project", "error", err)
		}
	})
	if err != nil {
		slog.Error("Failed to subscribe to NATS events", "error", err)
	}

	slog.Info("Event system started successfully")
}

// Stop gracefully shuts down the event system
func (es *EventSystem) Stop(ctx context.Context) error {
	slog.Info("Stopping event system...")

	// Close NATS connection
	if err := es.NATSBus.DrainAndClose(ctx); err != nil {
		slog.Error("Error draining NATS", "error", err)
	}

	slog.Info("Event system stopped")
	return nil
}

// PublishEvent publishes an event to all systems (store, NATS, WebSocket)
func (es *EventSystem) PublishEvent(event *events.Event) error {
	// Store event in database
	if err := es.Store.Store(event); err != nil {
		return fmt.Errorf("failed to store event: %w", err)
	}

	// Publish to NATS for distributed systems
	if err := es.NATSBus.PublishToProject(event.ProjectID, event); err != nil {
		slog.Error("Failed to publish to NATS", "error", err)
		// Don't fail the entire operation if NATS fails
	}

	// Broadcast to WebSocket clients for real-time updates
	if err := es.Broadcaster.PublishToProject(event.ProjectID, event); err != nil {
		slog.Error("Failed to broadcast to WebSocket clients", "error", err)
		// Don't fail the entire operation if WebSocket broadcast fails
	}

	return nil
}

// PublishEvents publishes multiple events atomically
func (es *EventSystem) PublishEvents(events []*events.Event) error {
	// Store events in database (atomic transaction)
	if err := es.Store.StoreMany(events); err != nil {
		return fmt.Errorf("failed to store events: %w", err)
	}

	// Publish to NATS
	for _, event := range events {
		if err := es.NATSBus.PublishToProject(event.ProjectID, event); err != nil {
			slog.Error("Failed to publish to NATS", "error", err)
		}

		// Broadcast to WebSocket clients
		if err := es.Broadcaster.PublishToProject(event.ProjectID, event); err != nil {
			slog.Error("Failed to broadcast to WebSocket clients", "error", err)
		}
	}

	return nil
}

// CreateSnapshot creates a snapshot of an entity's current state
func (es *EventSystem) CreateSnapshot(entityID string) error {
	// Replay events to get current state
	state, err := es.Store.Replay(entityID)
	if err != nil {
		return fmt.Errorf("failed to replay events: %w", err)
	}

	// Get event count to determine version
	store, ok := es.Store.(*events.PostgresEventStore)
	if !ok {
		return errors.New("store is not a PostgresEventStore")
	}
	count, err := store.GetEventCount(entityID)
	if err != nil {
		return fmt.Errorf("failed to get event count: %w", err)
	}

	// Get first event to get metadata
	eventList, err := es.Store.GetByEntityID(entityID)
	if err != nil || len(eventList) == 0 {
		return fmt.Errorf("failed to get events for snapshot: %w", err)
	}

	firstEvent := eventList[0]

	// Create snapshot
	snapshot := events.NewSnapshot(
		firstEvent.ProjectID,
		entityID,
		firstEvent.EntityType,
		count,
		state,
	)

	// Save snapshot
	if err := es.Store.SaveSnapshot(snapshot); err != nil {
		return fmt.Errorf("failed to save snapshot: %w", err)
	}

	slog.Info("Created snapshot for entity at version", "id", entityID, "version", count)
	return nil
}

// GetEntityState retrieves the current state of an entity
func (es *EventSystem) GetEntityState(entityID string) (map[string]interface{}, error) {
	// Try to get latest snapshot
	snapshot, err := es.Store.GetLatestSnapshot(entityID)
	if err != nil {
		return nil, fmt.Errorf("failed to get snapshot: %w", err)
	}

	var version int64
	if snapshot != nil {
		version = snapshot.Version
	}

	// Replay from snapshot
	state, err := es.Store.ReplayFromSnapshot(entityID, version)
	if err != nil {
		return nil, fmt.Errorf("failed to replay from snapshot: %w", err)
	}

	return state, nil
}

// GetStats returns statistics about the event system
func (es *EventSystem) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"websocket": es.WSHub.GetStats(),
		"nats":      es.NATSBus.GetStats(),
	}
}

// Example usage functions

// ExampleItemCreated demonstrates creating an item created event
func ExampleItemCreated(es *EventSystem, projectID, itemID, title, itemType string) error {
	event := events.NewEvent(
		projectID,
		itemID,
		events.EntityTypeItem,
		events.EventTypeCreated,
		map[string]interface{}{
			"title":       title,
			"type":        itemType,
			"status":      "todo",
			"priority":    exampleItemPriorityDefault,
			"description": "",
		},
	)

	event.WithMetadata("user_id", "system")
	event.WithMetadata("source", "api")

	return es.PublishEvent(event)
}

// ExampleItemStatusChanged demonstrates creating an item status changed event
func ExampleItemStatusChanged(es *EventSystem, projectID, itemID, oldStatus, newStatus string) error {
	event := events.NewEvent(
		projectID,
		itemID,
		events.EntityTypeItem,
		events.EventTypeItemStatusChanged,
		map[string]interface{}{
			"status":     newStatus,
			"old_status": oldStatus,
		},
	)

	event.WithMetadata("user_id", "system")
	event.WithMetadata("source", "api")

	return es.PublishEvent(event)
}

// ExampleLinkCreated demonstrates creating a link created event
func ExampleLinkCreated(es *EventSystem, projectID, linkID, sourceID, targetID, linkType string) error {
	event := events.NewEvent(
		projectID,
		linkID,
		events.EntityTypeLink,
		events.EventTypeLinkCreated,
		map[string]interface{}{
			"source_id": sourceID,
			"target_id": targetID,
			"type":      linkType,
		},
	)

	event.WithMetadata("user_id", "system")
	event.WithMetadata("source", "api")

	return es.PublishEvent(event)
}

// ExampleAgentActivity demonstrates creating an agent activity event
func ExampleAgentActivity(es *EventSystem, projectID, agentID, activity string, metadata map[string]interface{}) error {
	data := map[string]interface{}{
		"activity": activity,
	}

	// Merge additional metadata into data
	for k, v := range metadata {
		data[k] = v
	}

	event := events.NewEvent(
		projectID,
		agentID,
		events.EntityTypeAgent,
		events.EventTypeAgentActivity,
		data,
	)

	event.WithMetadata("source", "agent")

	return es.PublishEvent(event)
}
