//go:build integration

package testutil

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/stretchr/testify/require"
)

const (
	neo4jTestTimeout         = 30 * time.Second
	neo4jConnectivityRetries = 5
	neo4jConnectivityWait    = 500 * time.Millisecond
)

// Neo4jTestClient wraps a Neo4j driver for testing
type Neo4jTestClient struct {
	driver neo4j.DriverWithContext
	ctx    context.Context
	cancel context.CancelFunc
}

// NewNeo4jTestClient creates a Neo4j driver connected to the test container
func NewNeo4jTestClient(t *testing.T, uri, user, password string) *Neo4jTestClient {
	ctx, cancel := context.WithTimeout(context.Background(), neo4jTestTimeout)

	driver, err := neo4j.NewDriverWithContext(uri, neo4j.BasicAuth(user, password, ""))
	require.NoError(t, err, "failed to create Neo4j driver")

	// Verify connectivity with retry logic
	var lastErr error
	for i := 0; i < neo4jConnectivityRetries; i++ {
		lastErr = driver.VerifyConnectivity(ctx)
		if lastErr == nil {
			break
		}
		select {
		case <-time.After(neo4jConnectivityWait):
		case <-ctx.Done():
			cancel()
			driver.Close(ctx)
			t.Fatalf("failed to verify Neo4j connectivity after retries: %v", lastErr)
		}
	}

	if lastErr != nil {
		cancel()
		driver.Close(ctx)
		t.Fatalf("failed to verify Neo4j connectivity: %v", lastErr)
	}

	client := &Neo4jTestClient{
		driver: driver,
		ctx:    ctx,
		cancel: cancel,
	}

	// Register cleanup
	t.Cleanup(func() {
		client.Close()
	})

	return client
}

// GetDriver returns the underlying Neo4j driver
func (ntc *Neo4jTestClient) GetDriver() neo4j.DriverWithContext {
	return ntc.driver
}

// GetContext returns the context
func (ntc *Neo4jTestClient) GetContext() context.Context {
	return ntc.ctx
}

// ExecuteQuery executes a Cypher query and returns results
func (ntc *Neo4jTestClient) ExecuteQuery(t *testing.T, query string, params map[string]interface{}) neo4j.ResultWithContext {
	session := ntc.driver.NewSession(ntc.ctx, neo4j.SessionConfig{})
	t.Cleanup(func() {
		_ = session.Close(ntc.ctx)
	})

	result, err := session.Run(ntc.ctx, query, params)
	require.NoError(t, err, "failed to execute query: %s", query)

	return result
}

// ExecuteQueryAndCollect executes a query and collects all results
func (ntc *Neo4jTestClient) ExecuteQueryAndCollect(t *testing.T, query string, params map[string]interface{}) []map[string]interface{} {
	result := ntc.ExecuteQuery(t, query, params)

	records, err := result.Collect(ntc.ctx)
	require.NoError(t, err, "failed to collect results")

	var results []map[string]interface{}
	for _, record := range records {
		results = append(results, record.AsMap())
	}

	return results
}

// ExecuteQuerySingle executes a query and returns a single result
func (ntc *Neo4jTestClient) ExecuteQuerySingle(t *testing.T, query string, params map[string]interface{}) map[string]interface{} {
	result := ntc.ExecuteQuery(t, query, params)

	record, err := result.Single(ntc.ctx)
	require.NoError(t, err, "failed to get single result")

	return record.AsMap()
}

// ClearDatabase clears all nodes and relationships from the database
func (ntc *Neo4jTestClient) ClearDatabase(t *testing.T) {
	query := "MATCH (n) DETACH DELETE n"
	_ = ntc.ExecuteQuery(t, query, nil)
}

// Close closes the driver and cancels context
func (ntc *Neo4jTestClient) Close() {
	ntc.cancel()
	if ntc.driver != nil {
		_ = ntc.driver.Close(ntc.ctx)
	}
}

// AssertNodeExists verifies a node exists with given properties
func (ntc *Neo4jTestClient) AssertNodeExists(t *testing.T, label string, properties map[string]interface{}) {
	query := "MATCH (n:" + label + ") WHERE "
	params := make(map[string]interface{})

	conditions := make([]string, 0, len(properties))
	i := 0
	for key, val := range properties {
		paramKey := fmt.Sprintf("p%d", i)
		conditions = append(conditions, fmt.Sprintf("n.%s = $%s", key, paramKey))
		params[paramKey] = val
		i++
	}

	for j, cond := range conditions {
		if j > 0 {
			query += " AND "
		}
		query += cond
	}
	query += " RETURN n LIMIT 1"

	result := ntc.ExecuteQuery(t, query, params)
	records, err := result.Collect(ntc.ctx)
	require.NoError(t, err, "failed to check node existence")
	require.Greater(t, len(records), 0, "node with properties %v not found", properties)
}

// AssertRelationshipExists verifies a relationship exists between nodes
func (ntc *Neo4jTestClient) AssertRelationshipExists(t *testing.T, fromLabel, relType, toLabel string) {
	query := fmt.Sprintf(
		"MATCH (from:%s)-[r:%s]->(to:%s) RETURN r LIMIT 1",
		fromLabel, relType, toLabel,
	)

	result := ntc.ExecuteQuery(t, query, nil)
	records, err := result.Collect(ntc.ctx)
	require.NoError(t, err, "failed to check relationship existence")
	require.Greater(t, len(records), 0, "relationship %s not found between %s and %s", relType, fromLabel, toLabel)
}

// GetNodeCount returns the count of nodes with the given label
func (ntc *Neo4jTestClient) GetNodeCount(t *testing.T, label string) int64 {
	query := "MATCH (n:" + label + ") RETURN COUNT(n) as count"

	result := ntc.ExecuteQuerySingle(t, query, nil)
	count, ok := result["count"].(int64)
	require.True(t, ok, "count should be int64")

	return count
}

// GetRelationshipCount returns the count of relationships with the given type
func (ntc *Neo4jTestClient) GetRelationshipCount(t *testing.T, relType string) int64 {
	query := "MATCH ()-[r:" + relType + "]->() RETURN COUNT(r) as count"

	result := ntc.ExecuteQuerySingle(t, query, nil)
	count, ok := result["count"].(int64)
	require.True(t, ok, "count should be int64")

	return count
}
