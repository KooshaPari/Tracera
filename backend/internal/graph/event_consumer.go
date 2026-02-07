package graph

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

// GraphEventConsumer listens to NATS events and updates Neo4j
type GraphEventConsumer struct {
	bus    *nats.EventBus
	driver neo4j.DriverWithContext
}

// NewGraphEventConsumer creates a new graph event consumer
func NewGraphEventConsumer(bus *nats.EventBus, driver neo4j.DriverWithContext) *GraphEventConsumer {
	return &GraphEventConsumer{
		bus:    bus,
		driver: driver,
	}
}

// Start starts the event consumer
func (c *GraphEventConsumer) Start(ctx context.Context) error {
	log.Println("Starting Graph Event Consumer...")

	// Subscribe to all relevant events
	err := c.bus.Subscribe(func(event *events.Event) {
		if err := c.handleEvent(ctx, event); err != nil {
			log.Printf("Error handling graph event: %v", err)
		}
	})

	if err != nil {
		return fmt.Errorf("failed to subscribe to events: %w", err)
	}

	return nil
}

func (c *GraphEventConsumer) handleEvent(ctx context.Context, event *events.Event) error {
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
	}

	return nil
}

func (c *GraphEventConsumer) handleItemCreated(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

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
		log.Printf("[GRAPH] Created item node: %s", event.EntityID)
	}
	return err
}

func (c *GraphEventConsumer) handleItemUpdated(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

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
		log.Printf("[GRAPH] Updated item node: %s", event.EntityID)
	}
	return err
}

func (c *GraphEventConsumer) handleItemDeleted(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

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
		log.Printf("[GRAPH] Deleted item node: %s", event.EntityID)
	}
	return err
}

func (c *GraphEventConsumer) handleLinkCreated(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	// In Cypher, relationship types cannot be dynamic easily with a single parameter
	// but we can use APOC or just build the query if the type is trusted.
	// For now, we'll use a fixed relationship type or generic one.
	linkType := event.Data["type"].(string)
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
		log.Printf("[GRAPH] Created link: %s (%s -> %s)", event.EntityID, event.Data["source_id"], event.Data["target_id"])
	}
	return err
}

func (c *GraphEventConsumer) handleLinkDeleted(ctx context.Context, event *events.Event) error {
	session := c.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

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
		log.Printf("[GRAPH] Deleted link: %s", event.EntityID)
	}
	return err
}
