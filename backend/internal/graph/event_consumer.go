package graph

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/nats"
)

// EventConsumer listens to NATS events and updates Neo4j
type EventConsumer struct {
	bus    *nats.EventBus
	driver neo4j.DriverWithContext
}

// NewEventConsumer creates a new graph event consumer
func NewEventConsumer(bus *nats.EventBus, driver neo4j.DriverWithContext) *EventConsumer {
	return &EventConsumer{
		bus:    bus,
		driver: driver,
	}
}

// Start starts the event consumer
func (c *EventConsumer) Start(ctx context.Context) error {
	slog.Info("Starting Graph Event Consumer...")

	// Subscribe to all relevant events
	err := c.bus.Subscribe(func(event *events.Event) {
		if err := c.handleEvent(ctx, event); err != nil {
			slog.Error("Error handling graph event", "error", err)
		}
	})
	if err != nil {
		return fmt.Errorf("failed to subscribe to events: %w", err)
	}

	return nil
}

func (c *EventConsumer) handleEvent(ctx context.Context, event *events.Event) error {
	switch event.EventType {
	case events.EventTypeCreated:
		if event.EntityType == events.EntityTypeItem {
			return c.handleItemCreated(ctx, event)
		}
	case events.EventTypeUpdated:
		if event.EntityType == events.EntityTypeItem {
			return c.handleItemUpdated(ctx, event)
		}
	case events.EventTypeDeleted:
		if event.EntityType == events.EntityTypeItem {
			return c.handleItemDeleted(ctx, event)
		}
	case events.EventTypeLinkCreated:
		return c.handleLinkCreated(ctx, event)
	case events.EventTypeLinkDeleted:
		return c.handleLinkDeleted(ctx, event)
	case events.EventTypeItemStatusChanged,
		events.EventTypeItemPriorityChanged,
		events.EventTypeAgentStarted,
		events.EventTypeAgentStopped,
		events.EventTypeAgentActivity,
		events.EventTypeAgentError,
		events.EventTypeSnapshot,
		events.EventTypeRollback:
		// These event types do not require graph updates
	}

	return nil
}

func (c *EventConsumer) handleItemCreated(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer func() {
		if err := session.Close(ctx); err != nil {
			slog.Warn("failed to close neo4j session", "error", err)
		}
	}()

	query := `
		MERGE (i:Item {id: $id})
		SET i.project_id = $projectID,
		    i.title = $title,
		    i.type = $type,
		    i.status = $status,
		    i.created_at = datetime($createdAt)
	`

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		return tx.Run(ctx, query, map[string]interface{}{
			"id":        event.EntityID,
			"projectID": event.ProjectID,
			"title":     event.Data["title"],
			"type":      event.Data["type"],
			"status":    event.Data["status"],
			"createdAt": event.CreatedAt.Format(time.RFC3339),
		})
	})

	if err == nil {
		slog.Info("[GRAPH] Created item node", "id", event.EntityID)
	}
	return err
}

func (c *EventConsumer) handleItemUpdated(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer func() {
		if err := session.Close(ctx); err != nil {
			slog.Warn("failed to close neo4j session", "error", err)
		}
	}()

	query := `
		MATCH (i:Item {id: $id})
		SET i.title = $title,
		    i.type = $type,
		    i.status = $status,
		    i.updated_at = datetime($updatedAt)
	`

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		return tx.Run(ctx, query, map[string]interface{}{
			"id":        event.EntityID,
			"title":     event.Data["title"],
			"type":      event.Data["type"],
			"status":    event.Data["status"],
			"updatedAt": event.CreatedAt.Format(time.RFC3339),
		})
	})

	if err == nil {
		slog.Info("[GRAPH] Updated item node", "id", event.EntityID)
	}
	return err
}

func (c *EventConsumer) handleItemDeleted(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer func() {
		if err := session.Close(ctx); err != nil {
			slog.Warn("failed to close neo4j session", "error", err)
		}
	}()

	query := `
		MATCH (i:Item {id: $id})
		DETACH DELETE i
	`

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		return tx.Run(ctx, query, map[string]interface{}{
			"id": event.EntityID,
		})
	})

	if err == nil {
		slog.Info("[GRAPH] Deleted item node", "id", event.EntityID)
	}
	return err
}

func (c *EventConsumer) handleLinkCreated(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer func() {
		if err := session.Close(ctx); err != nil {
			slog.Warn("failed to close neo4j session", "error", err)
		}
	}()

	// In Cypher, relationship types cannot be dynamic easily with a single parameter
	// but we can use APOC or just build the query if the type is trusted.
	// For now, we'll use a fixed relationship type or generic one.
	linkType, ok := event.Data["type"].(string)
	if !ok {
		return errors.New("link event missing type field")
	}
	query := fmt.Sprintf(`
		MATCH (s:Item {id: $sourceID})
		MATCH (t:Item {id: $targetID})
		MERGE (s)-[r:%s {id: $linkID}]->(t)
		SET r.created_at = datetime($createdAt)
	`, linkType)

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		return tx.Run(ctx, query, map[string]interface{}{
			"sourceID":  event.Data["source_id"],
			"targetID":  event.Data["target_id"],
			"linkID":    event.EntityID,
			"createdAt": event.CreatedAt.Format(time.RFC3339),
		})
	})

	if err == nil {
		slog.Info("[GRAPH] Created link ( -> )", "id", event.EntityID, "id", event.Data["source_id"], "id", event.Data["target_id"])
	}
	return err
}

func (c *EventConsumer) handleLinkDeleted(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer func() {
		if err := session.Close(ctx); err != nil {
			slog.Warn("failed to close neo4j session", "error", err)
		}
	}()

	query := `
		MATCH ()-[r {id: $id}]->()
		DELETE r
	`

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		return tx.Run(ctx, query, map[string]interface{}{
			"id": event.EntityID,
		})
	})

	if err == nil {
		slog.Info("[GRAPH] Deleted link", "id", event.EntityID)
	}
	return err
}
