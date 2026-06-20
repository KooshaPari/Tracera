//go:build integration

package integration

import (
	"context"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/nats-io/nats.go"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/graph"
	internal_nats "github.com/kooshapari/tracertm-backend/internal/nats"
)

func TestLive_GraphNATSIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping live services integration test")
	}

	ctx := context.Background()

	// 1. Setup NATS
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}
	nc, err := nats.Connect(natsURL)
	if err != nil {
		t.Skip("NATS not available at", natsURL)
	}
	defer nc.Close()

	config := internal_nats.DefaultConfig()
	config.URL = natsURL
	bus, err := internal_nats.NewEventBus(config)
	require.NoError(t, err)

	// 2. Setup Neo4j
	neo4jURI := os.Getenv("NEO4J_URI")
	if neo4jURI == "" {
		neo4jURI = "bolt://localhost:7687"
	}
	auth := neo4j.BasicAuth("neo4j", os.Getenv("NEO4J_PASSWORD"), "")
	if os.Getenv("NEO4J_PASSWORD") == "" {
		auth = neo4j.BasicAuth("neo4j", "password", "")
	}
	neoDriver, err := neo4j.NewDriverWithContext(neo4jURI, auth)
	require.NoError(t, err)
	defer neoDriver.Close(ctx)

	if err := neoDriver.VerifyConnectivity(ctx); err != nil {
		t.Skip("Neo4j not available at", neo4jURI)
	}

	// 3. Start Graph Event Consumer
	consumer := graph.NewEventConsumer(bus, neoDriver)
	err = consumer.Start(ctx)
	require.NoError(t, err)

	// 4. Publish Event
	projectID := uuid.New().String()
	itemID := uuid.New().String()
	eventData := map[string]interface{}{
		"title":  "Integration Test Item",
		"type":   "requirement",
		"status": "active",
	}

	event := events.NewEvent(
		projectID,
		itemID,
		events.EntityTypeItem,
		events.EventTypeCreated,
		eventData,
	)

	err = bus.Publish(event)
	require.NoError(t, err)

	// 5. Wait for consumer to process
	time.Sleep(2 * time.Second)

	// 6. Verify in Neo4j
	session := neoDriver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		query := "MATCH (i:Item {id: $id}) RETURN i.title as title, i.type as type"
		res, err := tx.Run(ctx, query, map[string]interface{}{"id": itemID})
		if err != nil {
			return nil, err
		}
		if res.Next(ctx) {
			record := res.Record()
			title, _ := record.Get("title")
			itemType, _ := record.Get("type")
			return map[string]string{
				"title": title.(string),
				"type":  itemType.(string),
			}, nil
		}
		return nil, fmt.Errorf("node not found")
	})

	assert.NoError(t, err)
	require.NotNil(t, result)
	data := result.(map[string]string)
	assert.Equal(t, "Integration Test Item", data["title"])
	assert.Equal(t, "requirement", data["type"])

	// 7. Test Link Creation
	targetID := uuid.New().String()
	targetEvent := events.NewEvent(
		projectID,
		targetID,
		events.EntityTypeItem,
		events.EventTypeCreated,
		map[string]interface{}{
			"title":  "Target Item",
			"type":   "test_case",
			"status": "active",
		},
	)
	err = bus.Publish(targetEvent)
	require.NoError(t, err)

	time.Sleep(1 * time.Second)

	linkID := uuid.New().String()
	linkEvent := events.NewEvent(
		projectID,
		linkID,
		events.EntityTypeLink,
		events.EventTypeLinkCreated,
		map[string]interface{}{
			"source_id": itemID,
			"target_id": targetID,
			"type":      "VERIFIES",
		},
	)
	err = bus.Publish(linkEvent)
	require.NoError(t, err)

	time.Sleep(2 * time.Second)

	// 8. Verify Link in Neo4j
	linkResult, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		query := "MATCH (s:Item {id: $sourceID})-[r:VERIFIES]->(t:Item {id: $targetID}) RETURN r"
		res, err := tx.Run(ctx, query, map[string]interface{}{
			"sourceID": itemID,
			"targetID": targetID,
		})
		if err != nil {
			return nil, err
		}
		if res.Next(ctx) {
			return true, nil
		}
		return false, fmt.Errorf("link not found")
	})

	assert.NoError(t, err)
	assert.True(t, linkResult.(bool))
}
