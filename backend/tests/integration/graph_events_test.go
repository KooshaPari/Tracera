package integration

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	"github.com/kooshapari/tracertm-backend/internal/nats"
)

func TestLive_GraphEventIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx := context.Background()

	// Setup NATS Bus
	bus, err := nats.NewEventBus(nats.DefaultConfig())
	require.NoError(t, err)
	defer bus.Close()

	// Setup Neo4j
	uri := "bolt://localhost:7687"
	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth("neo4j", "neo4j_password", ""))
	if err != nil {
		t.Skip("Neo4j not available, skipping")
	}
	defer driver.Close(ctx)

	// Create Consumer
	consumer := graph.NewEventConsumer(bus, driver)
	err = consumer.Start(ctx)
	require.NoError(t, err)

	// 1. Test Item Created
	projectID := uuid.New().String()
	itemID := uuid.New().String()

	createEvent := events.NewEvent(projectID, itemID, events.EntityTypeItem, events.EventTypeCreated, map[string]interface{}{
		"title":  "Test Graph Item",
		"type":   "requirement",
		"status": "active",
	})

	err = bus.Publish(createEvent)
	require.NoError(t, err)

	// Wait for processing
	time.Sleep(1 * time.Second)

	// Verify in Neo4j
	verifyItemInNeo4j(t, ctx, driver, itemID, "Test Graph Item")

	// 2. Test Item Updated
	updateEvent := events.NewEvent(projectID, itemID, events.EntityTypeItem, events.EventTypeUpdated, map[string]interface{}{
		"title":  "Updated Graph Item",
		"type":   "requirement",
		"status": "completed",
	})

	err = bus.Publish(updateEvent)
	require.NoError(t, err)

	time.Sleep(1 * time.Second)
	verifyItemInNeo4j(t, ctx, driver, itemID, "Updated Graph Item")

	// 3. Test Link Created
	targetID := uuid.New().String()
	targetEvent := events.NewEvent(projectID, targetID, events.EntityTypeItem, events.EventTypeCreated, map[string]interface{}{
		"title":  "Target Item",
		"type":   "feature",
		"status": "active",
	})
	_ = bus.Publish(targetEvent)

	linkID := uuid.New().String()
	linkEvent := events.NewEvent(projectID, linkID, events.EntityTypeLink, events.EventTypeLinkCreated, map[string]interface{}{
		"source_id": itemID,
		"target_id": targetID,
		"type":      "DEPENDS_ON",
	})

	err = bus.Publish(linkEvent)
	require.NoError(t, err)

	time.Sleep(1 * time.Second)
	verifyLinkInNeo4j(t, ctx, driver, itemID, targetID, "DEPENDS_ON")

	// 4. Test Item Deleted
	deleteEvent := events.NewEvent(projectID, itemID, events.EntityTypeItem, events.EventTypeDeleted, nil)
	err = bus.Publish(deleteEvent)
	require.NoError(t, err)

	time.Sleep(1 * time.Second)
	verifyItemDeletedInNeo4j(t, ctx, driver, itemID)
}

func verifyItemInNeo4j(t *testing.T, ctx context.Context, driver neo4j.DriverWithContext, id string, expectedTitle string) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	result, err := session.Run(ctx, "MATCH (i:Item {id: $id}) RETURN i.title as title", map[string]interface{}{"id": id})
	require.NoError(t, err)

	if result.Next(ctx) {
		title, _ := result.Record().Get("title")
		assert.Equal(t, expectedTitle, title)
	} else {
		t.Errorf("Item %s not found in Neo4j", id)
	}
}

func verifyLinkInNeo4j(t *testing.T, ctx context.Context, driver neo4j.DriverWithContext, sourceID, targetID string, linkType string) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	query := fmt.Sprintf("MATCH (s:Item {id: $sourceID})-[r:%s]->(t:Item {id: $targetID}) RETURN count(r) as count", linkType)
	result, err := session.Run(ctx, query, map[string]interface{}{
		"sourceID": sourceID,
		"targetID": targetID,
	})
	require.NoError(t, err)

	if result.Next(ctx) {
		count, _ := result.Record().Get("count")
		assert.Greater(t, count.(int64), int64(0))
	} else {
		t.Errorf("Link from %s to %s not found in Neo4j", sourceID, targetID)
	}
}

func verifyItemDeletedInNeo4j(t *testing.T, ctx context.Context, driver neo4j.DriverWithContext, id string) {
	session := driver.NewSession(ctx, neo4j.SessionConfig{})
	defer session.Close(ctx)

	result, err := session.Run(ctx, "MATCH (i:Item {id: $id}) RETURN count(i) as count", map[string]interface{}{"id": id})
	require.NoError(t, err)

	if result.Next(ctx) {
		count, _ := result.Record().Get("count")
		assert.Equal(t, int64(0), count.(int64))
	}
}
