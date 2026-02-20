//go:build !integration && !e2e

package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestGraph_Traverse_BFS_Success tests breadth-first traversal
func TestGraph_Traverse_BFS_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a graph: A -> B -> D
	//                 A -> C -> D
	projectID := createTestProject(t, server)
	itemA := createTestItem(t, server, projectID)
	itemB := createTestItem(t, server, projectID)
	itemC := createTestItem(t, server, projectID)
	itemD := createTestItem(t, server, projectID)

	// Create links
	createTestLink(t, server, itemA, itemB, "depends_on")
	createTestLink(t, server, itemA, itemC, "depends_on")
	createTestLink(t, server, itemB, itemD, "depends_on")
	createTestLink(t, server, itemC, itemD, "depends_on")

	// Traverse BFS from A
	traverseReq := map[string]interface{}{
		"start_node": itemA,
		"algorithm":  "bfs",
		"max_depth":  10,
	}

	body, err := json.Marshal(traverseReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/graph/traverse", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, "bfs", response["algorithm"])
	assert.Equal(t, itemA, response["start_node"])

	nodes, ok := response["nodes"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 4, len(nodes)) // A, B, C, D

	// Verify BFS order (level by level)
	assert.Equal(t, itemA, nodes[0].(map[string]interface{})["id"])
	// B and C should be at depth 1
	depth1Nodes := []string{nodes[1].(map[string]interface{})["id"].(string), nodes[2].(map[string]interface{})["id"].(string)}
	assert.Contains(t, depth1Nodes, itemB)
	assert.Contains(t, depth1Nodes, itemC)
	// D should be at depth 2
	assert.Equal(t, itemD, nodes[3].(map[string]interface{})["id"])
}

// TestGraph_Traverse_DFS_Success tests depth-first traversal
func TestGraph_Traverse_DFS_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a graph: A -> B -> C -> D
	projectID := createTestProject(t, server)
	itemA := createTestItem(t, server, projectID)
	itemB := createTestItem(t, server, projectID)
	itemC := createTestItem(t, server, projectID)
	itemD := createTestItem(t, server, projectID)

	// Create links
	createTestLink(t, server, itemA, itemB, "depends_on")
	createTestLink(t, server, itemB, itemC, "depends_on")
	createTestLink(t, server, itemC, itemD, "depends_on")

	// Traverse DFS from A
	traverseReq := map[string]interface{}{
		"start_node": itemA,
		"algorithm":  "dfs",
		"max_depth":  10,
	}

	body, err := json.Marshal(traverseReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/graph/traverse", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, "dfs", response["algorithm"])
	assert.Equal(t, itemA, response["start_node"])

	nodes, ok := response["nodes"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 4, len(nodes))

	// Verify DFS order (depth-first)
	nodeIDs := make([]string, len(nodes))
	for i, node := range nodes {
		nodeIDs[i] = node.(map[string]interface{})["id"].(string)
	}
	assert.Equal(t, itemA, nodeIDs[0])
	assert.Equal(t, itemB, nodeIDs[1])
	assert.Equal(t, itemC, nodeIDs[2])
	assert.Equal(t, itemD, nodeIDs[3])
}

// TestGraph_DependencyAnalysis_Success tests dependency analysis
func TestGraph_DependencyAnalysis_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a dependency graph
	projectID := createTestProject(t, server)
	itemA := createTestItem(t, server, projectID) // Depends on B and C
	itemB := createTestItem(t, server, projectID) // Depends on D
	itemC := createTestItem(t, server, projectID) // No dependencies
	itemD := createTestItem(t, server, projectID) // No dependencies

	createTestLink(t, server, itemA, itemB, "depends_on")
	createTestLink(t, server, itemA, itemC, "depends_on")
	createTestLink(t, server, itemB, itemD, "depends_on")

	// Analyze dependencies for A
	req := httptest.NewRequest(http.MethodGet, "/api/v1/graph/dependencies/"+itemA, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, itemA, response["item_id"])

	directDeps, ok := response["direct_dependencies"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 2, len(directDeps)) // B and C

	allDeps, ok := response["all_dependencies"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 3, len(allDeps)) // B, C, and D

	dependencyChain, ok := response["dependency_chain"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(dependencyChain), 1)
}

// TestGraph_ImpactAnalysis_Success tests impact analysis
func TestGraph_ImpactAnalysis_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a graph where D is depended upon by multiple items
	projectID := createTestProject(t, server)
	itemA := createTestItem(t, server, projectID)
	itemB := createTestItem(t, server, projectID)
	itemC := createTestItem(t, server, projectID)
	itemD := createTestItem(t, server, projectID) // Base item

	createTestLink(t, server, itemA, itemD, "depends_on")
	createTestLink(t, server, itemB, itemD, "depends_on")
	createTestLink(t, server, itemC, itemB, "depends_on")

	// Analyze impact of changing D
	req := httptest.NewRequest(http.MethodGet, "/api/v1/graph/impact/"+itemD, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, itemD, response["item_id"])

	directImpact, ok := response["direct_impact"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 2, len(directImpact)) // A and B directly depend on D

	totalImpact, ok := response["total_impact"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 3, len(totalImpact)) // A, B, and C

	impactScore, ok := response["impact_score"].(float64)
	require.True(t, ok)
	assert.Greater(t, impactScore, 0.0)
}

// TestGraph_CycleDetection_Success tests cycle detection
func TestGraph_CycleDetection_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	testCases := []struct {
		name          string
		hasCycle      bool
		setupFunc     func() []string
		expectedCycle int
	}{
		{
			name:     "no cycle - linear chain",
			hasCycle: false,
			setupFunc: func() []string {
				itemA := createTestItem(t, server, projectID)
				itemB := createTestItem(t, server, projectID)
				itemC := createTestItem(t, server, projectID)
				createTestLink(t, server, itemA, itemB, "depends_on")
				createTestLink(t, server, itemB, itemC, "depends_on")
				return []string{itemA, itemB, itemC}
			},
		},
		{
			name:     "simple cycle - A -> B -> A",
			hasCycle: true,
			setupFunc: func() []string {
				itemA := createTestItem(t, server, projectID)
				itemB := createTestItem(t, server, projectID)
				createTestLink(t, server, itemA, itemB, "depends_on")
				createTestLink(t, server, itemB, itemA, "depends_on")
				return []string{itemA, itemB}
			},
			expectedCycle: 2,
		},
		{
			name:     "complex cycle - A -> B -> C -> A",
			hasCycle: true,
			setupFunc: func() []string {
				itemA := createTestItem(t, server, projectID)
				itemB := createTestItem(t, server, projectID)
				itemC := createTestItem(t, server, projectID)
				createTestLink(t, server, itemA, itemB, "depends_on")
				createTestLink(t, server, itemB, itemC, "depends_on")
				createTestLink(t, server, itemC, itemA, "depends_on")
				return []string{itemA, itemB, itemC}
			},
			expectedCycle: 3,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			items := tc.setupFunc()
			_ = items

			req := httptest.NewRequest(http.MethodGet, "/api/v1/graph/cycles?project_id="+projectID, nil)
			w := httptest.NewRecorder()

			server.Config.Handler.ServeHTTP(w, req)

			assert.Equal(t, http.StatusOK, w.Code)

			var response map[string]interface{}
			err := json.NewDecoder(w.Body).Decode(&response)
			require.NoError(t, err)

			hasCycles, ok := response["has_cycles"].(bool)
			require.True(t, ok)
			assert.Equal(t, tc.hasCycle, hasCycles)

			if tc.hasCycle {
				cycles, ok := response["cycles"].([]interface{})
				require.True(t, ok)
				assert.GreaterOrEqual(t, len(cycles), 1)

				firstCycle := cycles[0].(map[string]interface{})
				cycleNodes := firstCycle["nodes"].([]interface{})
				assert.Equal(t, tc.expectedCycle, len(cycleNodes))
			}
		})
	}
}

// TestGraph_CriticalPath_Success tests critical path analysis
func TestGraph_CriticalPath_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a project with multiple paths of different lengths
	projectID := createTestProject(t, server)

	// Path 1: A -> B -> E (length 2)
	// Path 2: A -> C -> D -> E (length 3) - Critical path
	itemA := createTestItem(t, server, projectID)
	itemB := createTestItem(t, server, projectID)
	itemC := createTestItem(t, server, projectID)
	itemD := createTestItem(t, server, projectID)
	itemE := createTestItem(t, server, projectID)

	createTestLink(t, server, itemA, itemB, "depends_on")
	createTestLink(t, server, itemB, itemE, "depends_on")
	createTestLink(t, server, itemA, itemC, "depends_on")
	createTestLink(t, server, itemC, itemD, "depends_on")
	createTestLink(t, server, itemD, itemE, "depends_on")

	// Find critical path
	req := httptest.NewRequest(http.MethodGet, "/api/v1/graph/critical-path?project_id="+projectID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	criticalPath, ok := response["critical_path"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 4, len(criticalPath)) // A -> C -> D -> E

	// Verify the path
	pathIDs := make([]string, len(criticalPath))
	for i, node := range criticalPath {
		pathIDs[i] = node.(map[string]interface{})["id"].(string)
	}
	assert.Equal(t, itemA, pathIDs[0])
	assert.Equal(t, itemC, pathIDs[1])
	assert.Equal(t, itemD, pathIDs[2])
	assert.Equal(t, itemE, pathIDs[3])

	pathLength, ok := response["path_length"].(float64)
	require.True(t, ok)
	assert.Equal(t, 3.0, pathLength)
}

// Helper functions

func createTestLink(t *testing.T, server *httptest.Server, sourceID, targetID, linkType string) string {
	linkReq := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      linkType,
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	return response["id"].(string)
}
