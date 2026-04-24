//go:build integration

package graph

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/testutil"
)

// TestNeo4jClient_Connection tests basic Neo4j connection via testcontainers
func TestNeo4jClient_Connection(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	client, err := NewNeo4jClient(t.Context(), nc.GetBoltURI(), user, password)
	require.NoError(t, err, "failed to create Neo4j client")
	defer func() {
		ctx := context.Background()
		err := client.Close(ctx)
		assert.NoError(t, err, "failed to close client")
	}()

	// Verify connectivity
	ctx := context.Background()
	err = client.HealthCheck(ctx)
	assert.NoError(t, err, "health check failed")
}

// TestNeo4jClient_CreateProjectNode tests creating a project node
func TestNeo4jClient_CreateProjectNode(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	client, err := NewNeo4jClient(t.Context(), nc.GetBoltURI(), user, password)
	require.NoError(t, err)
	defer func() {
		_ = client.Close(context.Background())
	}()

	ctx := context.Background()
	projectCtx := NewProjectContext("test-project", "workspace-123")

	err = client.CreateProjectNode(ctx, projectCtx)
	assert.NoError(t, err, "failed to create project node")

	// Verify node was created
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)
	testClient.AssertNodeExists(t, "Project", map[string]interface{}{
		"id":           "test-project",
		"workspace_id": "workspace-123",
	})
}

// TestNeo4jClient_CreateMultipleProjectNodes tests creating multiple project nodes
func TestNeo4jClient_CreateMultipleProjectNodes(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	client, err := NewNeo4jClient(t.Context(), nc.GetBoltURI(), user, password)
	require.NoError(t, err)
	defer func() {
		_ = client.Close(context.Background())
	}()

	ctx := context.Background()

	projects := []struct {
		id        string
		namespace ProjectNamespace
	}{
		{"bifrost", NamespaceBifrost},
		{"vibeproxy", NamespaceVibeProxy},
		{"jarvis", NamespaceJarvis},
	}

	for _, proj := range projects {
		projectCtx := NewProjectContext(proj.id, "workspace-123")
		err := client.CreateProjectNode(ctx, projectCtx)
		require.NoError(t, err, "failed to create project node for %s", proj.id)
	}

	// Verify all nodes were created
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)
	count := testClient.GetNodeCount(t, "Project")
	assert.Equal(t, int64(3), count, "expected 3 project nodes")
}

// TestNeo4jClient_CreateNodes tests creating various node types
func TestNeo4jClient_CreateNodes(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)
	ctx := context.Background()

	t.Run("create requirement node", func(t *testing.T) {
		query := `
			CREATE (r:Requirement {
				id: 'req-001',
				project_id: 'test-project',
				title: 'Test Requirement',
				description: 'A test requirement',
				status: 'open',
				created_at: timestamp()
			})
		`
		_ = testClient.ExecuteQuery(t, query, nil)
		testClient.AssertNodeExists(t, "Requirement", map[string]interface{}{"id": "req-001"})
	})

	t.Run("create specification node", func(t *testing.T) {
		query := `
			CREATE (s:Specification {
				id: 'spec-001',
				project_id: 'test-project',
				title: 'Test Specification',
				created_at: timestamp()
			})
		`
		_ = testClient.ExecuteQuery(t, query, nil)
		testClient.AssertNodeExists(t, "Specification", map[string]interface{}{"id": "spec-001"})
	})

	t.Run("create test case node", func(t *testing.T) {
		query := `
			CREATE (t:TestCase {
				id: 'test-001',
				project_id: 'test-project',
				title: 'Test Case',
				created_at: timestamp()
			})
		`
		_ = testClient.ExecuteQuery(t, query, nil)
		testClient.AssertNodeExists(t, "TestCase", map[string]interface{}{"id": "test-001"})
	})

	t.Run("verify node counts", func(t *testing.T) {
		reqCount := testClient.GetNodeCount(t, "Requirement")
		specCount := testClient.GetNodeCount(t, "Specification")
		testCount := testClient.GetNodeCount(t, "TestCase")

		assert.Equal(t, int64(1), reqCount, "expected 1 requirement node")
		assert.Equal(t, int64(1), specCount, "expected 1 specification node")
		assert.Equal(t, int64(1), testCount, "expected 1 test case node")
	})
}

// TestNeo4jClient_CreateRelationships tests creating relationships between nodes
func TestNeo4jClient_CreateRelationships(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)
	ctx := context.Background()

	// Setup: Create nodes
	setupQuery := `
		CREATE (req:Requirement {
			id: 'req-001',
			project_id: 'test-project',
			title: 'Requirement',
			created_at: timestamp()
		}),
		(spec:Specification {
			id: 'spec-001',
			project_id: 'test-project',
			title: 'Specification',
			created_at: timestamp()
		}),
		(test:TestCase {
			id: 'test-001',
			project_id: 'test-project',
			title: 'Test Case',
			created_at: timestamp()
		})
	`
	_ = testClient.ExecuteQuery(t, setupQuery, nil)

	t.Run("create IMPLEMENTS relationship", func(t *testing.T) {
		query := `
			MATCH (req:Requirement {id: 'req-001'}),
				  (spec:Specification {id: 'spec-001'})
			CREATE (spec)-[r:IMPLEMENTS]->(req)
			RETURN r
		`
		result := testClient.ExecuteQuery(t, query, nil)
		records, err := result.Collect(ctx)
		require.NoError(t, err)
		assert.Greater(t, len(records), 0, "relationship not created")
	})

	t.Run("create VERIFIES relationship", func(t *testing.T) {
		query := `
			MATCH (test:TestCase {id: 'test-001'}),
				  (req:Requirement {id: 'req-001'})
			CREATE (test)-[r:VERIFIES]->(req)
			RETURN r
		`
		result := testClient.ExecuteQuery(t, query, nil)
		records, err := result.Collect(ctx)
		require.NoError(t, err)
		assert.Greater(t, len(records), 0, "relationship not created")
	})

	t.Run("verify relationships exist", func(t *testing.T) {
		query := `
			MATCH ()-[r:IMPLEMENTS]->() RETURN COUNT(r) as count
		`
		result := testClient.ExecuteQuerySingle(t, query, nil)
		count := result["count"].(int64)
		assert.Equal(t, int64(1), count, "expected 1 IMPLEMENTS relationship")

		query = `MATCH ()-[r:VERIFIES]->() RETURN COUNT(r) as count`
		result = testClient.ExecuteQuerySingle(t, query, nil)
		count = result["count"].(int64)
		assert.Equal(t, int64(1), count, "expected 1 VERIFIES relationship")
	})
}

// TestNeo4jClient_Traversal tests graph traversal queries
func TestNeo4jClient_Traversal(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)
	ctx := context.Background()

	// Create a chain: Req -> Spec -> Test
	setupQuery := `
		CREATE (req:Requirement {
			id: 'req-001',
			project_id: 'test-project',
			title: 'Requirement'
		})-[impl:IMPLEMENTS]->(spec:Specification {
			id: 'spec-001',
			project_id: 'test-project',
			title: 'Specification'
		})-[ver:VERIFIES]->(test:TestCase {
			id: 'test-001',
			project_id: 'test-project',
			title: 'Test Case'
		})
	`
	_ = testClient.ExecuteQuery(t, setupQuery, nil)

	t.Run("traverse forward path", func(t *testing.T) {
		query := `
			MATCH (req:Requirement {id: 'req-001'})
			-[impl:IMPLEMENTS]->(spec:Specification)
			-[ver:VERIFIES]->(test:TestCase)
			RETURN req.id, spec.id, test.id
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		require.Greater(t, len(result), 0, "traversal path not found")
		assert.Equal(t, "req-001", result[0]["req.id"])
		assert.Equal(t, "spec-001", result[0]["spec.id"])
		assert.Equal(t, "test-001", result[0]["test.id"])
	})

	t.Run("traverse reverse path", func(t *testing.T) {
		query := `
			MATCH (test:TestCase {id: 'test-001'})
			<-[ver:VERIFIES]-(spec:Specification)
			<-[impl:IMPLEMENTS]-(req:Requirement)
			RETURN req.id, spec.id, test.id
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		require.Greater(t, len(result), 0, "reverse path not found")
	})

	t.Run("find all descendants", func(t *testing.T) {
		query := `
			MATCH (req:Requirement {id: 'req-001'})-[*]->(n)
			RETURN n.id, LABELS(n) as labels
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		assert.Greater(t, len(result), 0, "no descendants found")
	})

	t.Run("find all ancestors", func(t *testing.T) {
		query := `
			MATCH (test:TestCase {id: 'test-001'})<-[*]-(n)
			RETURN n.id, LABELS(n) as labels
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		assert.Greater(t, len(result), 0, "no ancestors found")
	})
}

// TestNeo4jClient_PathFinding tests path finding queries
func TestNeo4jClient_PathFinding(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)
	ctx := context.Background()

	// Create a more complex graph
	setupQuery := `
		CREATE (req:Requirement {id: 'req-001', project_id: 'test-project', title: 'Req 1'})
		-[r1:DEPENDS_ON]->(req2:Requirement {id: 'req-002', project_id: 'test-project', title: 'Req 2'})
		-[r2:DEPENDS_ON]->(req3:Requirement {id: 'req-003', project_id: 'test-project', title: 'Req 3'})
		-[r3:DEPENDS_ON]->(req4:Requirement {id: 'req-004', project_id: 'test-project', title: 'Req 4'})
	`
	_ = testClient.ExecuteQuery(t, setupQuery, nil)

	t.Run("find shortest path", func(t *testing.T) {
		query := `
			MATCH path = shortestPath(
				(start:Requirement {id: 'req-001'})
				-[*]->(end:Requirement {id: 'req-004'})
			)
			RETURN length(path) as path_length, nodes(path) as nodes
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		require.Greater(t, len(result), 0, "path not found")
		assert.Equal(t, int64(3), result[0]["path_length"], "expected path length of 3")
	})

	t.Run("find all simple paths", func(t *testing.T) {
		query := `
			MATCH path = (start:Requirement {id: 'req-001'})
			-[*]->(end:Requirement {id: 'req-004'})
			RETURN length(path) as path_length
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		require.Greater(t, len(result), 0, "path not found")
	})

	t.Run("get path nodes and relationships", func(t *testing.T) {
		query := `
			MATCH (start:Requirement {id: 'req-001'})
			-[*]->(end:Requirement {id: 'req-004'})
			WITH start, end
			MATCH path = (start)-[rels*]->(end)
			RETURN [node in nodes(path) | node.id] as node_ids,
					[rel in rels | type(rel)] as rel_types
			LIMIT 1
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		require.Greater(t, len(result), 0, "path details not found")
	})

	t.Run("find nodes at distance", func(t *testing.T) {
		query := `
			MATCH (start:Requirement {id: 'req-001'})
			-[*2]->(end)
			RETURN end.id
		`
		result := testClient.ExecuteQueryAndCollect(t, query, nil)
		// At distance 2, should reach req-003
		require.Greater(t, len(result), 0, "no nodes at distance 2")
	})
}

// TestNeo4jClient_ComplexQueries tests more complex Cypher queries
func TestNeo4jClient_ComplexQueries(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)

	// Create test data
	setupQuery := `
		CREATE (req1:Requirement {id: 'req-001', project_id: 'test-project', priority: 'HIGH', status: 'OPEN'})
		CREATE (req2:Requirement {id: 'req-002', project_id: 'test-project', priority: 'MEDIUM', status: 'IN_PROGRESS'})
		CREATE (req3:Requirement {id: 'req-003', project_id: 'test-project', priority: 'LOW', status: 'CLOSED'})
		CREATE (spec1:Specification {id: 'spec-001', project_id: 'test-project'})
		CREATE (test1:TestCase {id: 'test-001', project_id: 'test-project'})
		CREATE (req1)-[:IMPLEMENTS]->(spec1)
		CREATE (req2)-[:IMPLEMENTS]->(spec1)
		CREATE (test1)-[:VERIFIES]->(req1)
	`
	_ = testClient.ExecuteQuery(t, setupQuery, nil)

	t.Run("aggregate by property", func(t *testing.T) {
		query := `
			MATCH (req:Requirement {project_id: 'test-project'})
			RETURN req.priority, COUNT(req) as count
			ORDER BY count DESC
		`
		results := testClient.ExecuteQueryAndCollect(t, query, nil)
		assert.Greater(t, len(results), 0, "no aggregation results")
	})

	t.Run("find nodes with multiple relationships", func(t *testing.T) {
		query := `
			MATCH (spec:Specification {id: 'spec-001'})
			<-[impl:IMPLEMENTS]-(req:Requirement)
			RETURN COUNT(req) as requirement_count
		`
		result := testClient.ExecuteQuerySingle(t, query, nil)
		assert.Equal(t, int64(2), result["requirement_count"], "expected 2 implementing requirements")
	})

	t.Run("filter and project results", func(t *testing.T) {
		query := `
			MATCH (req:Requirement {project_id: 'test-project'})
			WHERE req.priority IN ['HIGH', 'MEDIUM']
			RETURN req.id, req.priority, req.status
			ORDER BY req.priority
		`
		results := testClient.ExecuteQueryAndCollect(t, query, nil)
		assert.Greater(t, len(results), 0, "no filtered results")
	})
}

// TestNeo4jClient_GraphStatistics tests retrieving graph statistics
func TestNeo4jClient_GraphStatistics(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)

	setupQuery := `
		CREATE (req1:Requirement {id: 'req-001', project_id: 'test-project'})
		CREATE (req2:Requirement {id: 'req-002', project_id: 'test-project'})
		CREATE (spec1:Specification {id: 'spec-001', project_id: 'test-project'})
		CREATE (req1)-[:IMPLEMENTS]->(spec1)
		CREATE (req2)-[:IMPLEMENTS]->(spec1)
	`
	_ = testClient.ExecuteQuery(t, setupQuery, nil)

	t.Run("count total nodes", func(t *testing.T) {
		query := "MATCH (n) RETURN COUNT(n) as total_nodes"
		result := testClient.ExecuteQuerySingle(t, query, nil)
		assert.Greater(t, result["total_nodes"].(int64), int64(0), "should have nodes")
	})

	t.Run("count total relationships", func(t *testing.T) {
		query := "MATCH ()-[r]->() RETURN COUNT(r) as total_relationships"
		result := testClient.ExecuteQuerySingle(t, query, nil)
		assert.Greater(t, result["total_relationships"].(int64), int64(0), "should have relationships")
	})

	t.Run("count by label", func(t *testing.T) {
		query := `
			MATCH (n)
			UNWIND labels(n) as label
			RETURN label, COUNT(n) as count
			ORDER BY label
		`
		results := testClient.ExecuteQueryAndCollect(t, query, nil)
		assert.Greater(t, len(results), 0, "should have label counts")
	})

	t.Run("count by relationship type", func(t *testing.T) {
		query := `
			MATCH ()-[r]->()
			RETURN type(r) as rel_type, COUNT(r) as count
			ORDER BY rel_type
		`
		results := testClient.ExecuteQueryAndCollect(t, query, nil)
		assert.Greater(t, len(results), 0, "should have relationship type counts")
	})
}

// TestNeo4jClient_ErrorHandling tests error handling
func TestNeo4jClient_ErrorHandling(t *testing.T) {
	config := testutil.DefaultNeo4jContainerConfig()
	nc := testutil.NewNeo4jContainerForTest(t, config)

	user, password := nc.GetCredentials()
	testClient := testutil.NewNeo4jTestClient(t, nc.GetBoltURI(), user, password)
	ctx := context.Background()

	t.Run("handle invalid query syntax", func(t *testing.T) {
		query := "INVALID CYPHER QUERY"
		result := testClient.ExecuteQuery(t, query, nil)
		_, err := result.Single(ctx)
		// Should have error - don't use require.NoError
		assert.Error(t, err, "should get error for invalid query")
	})

	t.Run("handle non-existent node", func(t *testing.T) {
		query := "MATCH (n:NonExistent) RETURN n LIMIT 1"
		results := testClient.ExecuteQueryAndCollect(t, query, nil)
		assert.Equal(t, 0, len(results), "should return empty result for non-existent nodes")
	})
}
