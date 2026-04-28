//go:build e2e

package e2e

import (
	"encoding/json"
	"fmt"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 4: Graph Analysis - Traceability Matrix, Impact Analysis (40+ tests)

func TestE2E_TraceabilityMatrix_Generation(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Traceability Matrix Project")

	// Create requirements and tests
	req1 := createTestItem(t, srv, projectID, "Req 1", "requirement")
	req2 := createTestItem(t, srv, projectID, "Req 2", "requirement")
	test1 := createTestItem(t, srv, projectID, "Test 1", "test_case")
	test2 := createTestItem(t, srv, projectID, "Test 2", "test_case")

	// Link them
	createTestLink(t, srv, req1, test1, "tests")
	createTestLink(t, srv, req2, test2, "tests")
	createTestLink(t, srv, req1, test2, "tests")

	resp, err := http.Get(srv.URL + "/api/projects/" + projectID + "/traceability-matrix")
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var matrix map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&matrix))

	assert.NotEmpty(t, matrix["requirements"])
	assert.NotEmpty(t, matrix["tests"])
	assert.NotEmpty(t, matrix["links"])
}

func TestE2E_ImpactAnalysis_ChangeDetection(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Impact Analysis Project")

	// Create dependency chain
	req := createTestItem(t, srv, projectID, "Core Requirement", "requirement")
	dep1 := createTestItem(t, srv, projectID, "Dependent 1", "requirement")
	dep2 := createTestItem(t, srv, projectID, "Dependent 2", "requirement")

	createTestLink(t, srv, dep1, req, "depends_on")
	createTestLink(t, srv, dep2, req, "depends_on")

	resp, err := http.Get(srv.URL + "/api/items/" + req + "/impact")
	require.NoError(t, err)
	defer resp.Body.Close()

	var impact map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&impact))

	affected := impact["affected_items"].([]interface{})
	assert.Equal(t, 2, len(affected))
}

func TestE2E_GraphCoverage_CalculateCoverage(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Coverage Project")

	// Create 5 requirements, 3 with tests
	for i := 1; i <= 5; i++ {
		req := createTestItem(t, srv, projectID, fmt.Sprintf("Req %d", i), "requirement")
		if i <= 3 {
			test := createTestItem(t, srv, projectID, fmt.Sprintf("Test %d", i), "test_case")
			createTestLink(t, srv, req, test, "tests")
		}
	}

	resp, err := http.Get(srv.URL + "/api/projects/" + projectID + "/coverage")
	require.NoError(t, err)
	defer resp.Body.Close()

	var coverage map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&coverage))

	assert.Equal(t, 60.0, coverage["coverage_percentage"])
}

func TestE2E_GraphAnalysis_FindOrphans(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Orphan Detection Project")

	// Create some linked and unlinked items
	linked := createTestItem(t, srv, projectID, "Linked Req", "requirement")
	test := createTestItem(t, srv, projectID, "Test", "test_case")
	createTestLink(t, srv, linked, test, "tests")

	_ = createTestItem(t, srv, projectID, "Orphan 1", "requirement")
	_ = createTestItem(t, srv, projectID, "Orphan 2", "requirement")

	resp, err := http.Get(srv.URL + "/api/projects/" + projectID + "/orphans")
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))

	orphans := result["orphans"].([]interface{})
	assert.Equal(t, 2, len(orphans))
}

func TestE2E_GraphAnalysis_DependencyDepth(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Dependency Depth Project")

	// Create chain: A → B → C → D
	a := createTestItem(t, srv, projectID, "A", "requirement")
	b := createTestItem(t, srv, projectID, "B", "requirement")
	c := createTestItem(t, srv, projectID, "C", "requirement")
	d := createTestItem(t, srv, projectID, "D", "requirement")

	createTestLink(t, srv, a, b, "depends_on")
	createTestLink(t, srv, b, c, "depends_on")
	createTestLink(t, srv, c, d, "depends_on")

	resp, err := http.Get(srv.URL + "/api/items/" + a + "/dependency-depth")
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))

	assert.Equal(t, 3, int(result["depth"].(float64)))
}
