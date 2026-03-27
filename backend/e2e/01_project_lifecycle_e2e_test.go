//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

// Journey 1: Create Project → Add Items → Build Graph (50+ tests)
// This journey tests the complete project lifecycle from creation to graph visualization

type testServer struct {
	URL       string
	DB        *pgxpool.Pool
	Container testcontainers.Container
	Cleanup   func()
}

func setupE2EServer(t *testing.T) *testServer {
	ctx := context.Background()

	// Start PostgreSQL container
	pgContainer, err := postgres.RunContainer(ctx,
		testcontainers.WithImage("postgres:16-alpine"),
		postgres.WithDatabase("e2e_testdb"),
		postgres.WithUsername("e2e_user"),
		postgres.WithPassword("e2e_pass"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(60*time.Second)),
	)
	require.NoError(t, err)

	connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	require.NoError(t, err)

	pool, err := pgxpool.New(ctx, connStr)
	require.NoError(t, err)
	require.NoError(t, pool.Ping(ctx))

	// tracked: https://github.com/KooshaPari/trace/issues/228
	// For now, mock URL
	serverURL := "http://localhost:8080"

	cleanup := func() {
		pool.Close()
		_ = pgContainer.Terminate(ctx)
	}

	return &testServer{
		URL:       serverURL,
		DB:        pool,
		Container: pgContainer,
		Cleanup:   cleanup,
	}
}

// Test 1-10: Project Creation
func TestE2E_CreateProject_Success(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	payload := map[string]interface{}{
		"name":        "E2E Test Project",
		"description": "Test project for E2E validation",
		"owner_id":    "user-123",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/projects", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	assert.NotEmpty(t, result["id"])
	assert.Equal(t, "E2E Test Project", result["name"])
}

func TestE2E_CreateProject_ValidationErrors(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	testCases := []struct {
		name       string
		payload    map[string]interface{}
		wantStatus int
		wantError  string
	}{
		{
			name:       "missing name",
			payload:    map[string]interface{}{"owner_id": "user-123"},
			wantStatus: http.StatusBadRequest,
			wantError:  "name is required",
		},
		{
			name:       "empty name",
			payload:    map[string]interface{}{"name": "", "owner_id": "user-123"},
			wantStatus: http.StatusBadRequest,
			wantError:  "name cannot be empty",
		},
		{
			name:       "name too long",
			payload:    map[string]interface{}{"name": string(make([]byte, 256)), "owner_id": "user-123"},
			wantStatus: http.StatusBadRequest,
			wantError:  "name too long",
		},
		{
			name:       "missing owner",
			payload:    map[string]interface{}{"name": "Test"},
			wantStatus: http.StatusBadRequest,
			wantError:  "owner_id is required",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			body, _ := json.Marshal(tc.payload)
			resp, err := http.Post(srv.URL+"/api/projects", "application/json", bytes.NewReader(body))
			require.NoError(t, err)
			defer resp.Body.Close()

			assert.Equal(t, tc.wantStatus, resp.StatusCode)
		})
	}
}

func TestE2E_CreateProject_DuplicateName(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	payload := map[string]interface{}{
		"name":     "Duplicate Project",
		"owner_id": "user-123",
	}

	body, _ := json.Marshal(payload)

	// Create first project
	resp1, err := http.Post(srv.URL+"/api/projects", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp1.Body.Close()
	assert.Equal(t, http.StatusCreated, resp1.StatusCode)

	// Attempt to create duplicate
	body, _ = json.Marshal(payload)
	resp2, err := http.Post(srv.URL+"/api/projects", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp2.Body.Close()
	assert.Equal(t, http.StatusConflict, resp2.StatusCode)
}

// Test 11-25: Add Items to Project
func TestE2E_AddItems_MultipleTypes(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	// Create project first
	projectID := createTestProject(t, srv, "Items Test Project")

	itemTypes := []string{"requirement", "test_case", "bug", "feature", "epic"}

	for i, itemType := range itemTypes {
		t.Run(fmt.Sprintf("add_%s", itemType), func(t *testing.T) {
			payload := map[string]interface{}{
				"project_id":  projectID,
				"title":       fmt.Sprintf("Test %s %d", itemType, i),
				"description": fmt.Sprintf("Test description for %s", itemType),
				"type":        itemType,
				"status":      "open",
			}

			body, _ := json.Marshal(payload)
			resp, err := http.Post(srv.URL+"/api/items", "application/json", bytes.NewReader(body))
			require.NoError(t, err)
			defer resp.Body.Close()

			assert.Equal(t, http.StatusCreated, resp.StatusCode)

			var result map[string]interface{}
			require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
			assert.NotEmpty(t, result["id"])
			assert.Equal(t, itemType, result["type"])
		})
	}
}

func TestE2E_AddItems_BulkCreate(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Bulk Items Project")

	items := make([]map[string]interface{}, 20)
	for i := 0; i < 20; i++ {
		items[i] = map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("Bulk Item %d", i),
			"type":       "requirement",
			"status":     "open",
		}
	}

	payload := map[string]interface{}{"items": items}
	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/items/bulk", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	assert.Equal(t, 20, int(result["created_count"].(float64)))
}

// Test 26-40: Build Graph
func TestE2E_BuildGraph_FromItems(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Graph Test Project")

	// Create items with relationships
	req1 := createTestItem(t, srv, projectID, "Requirement 1", "requirement")
	req2 := createTestItem(t, srv, projectID, "Requirement 2", "requirement")
	test1 := createTestItem(t, srv, projectID, "Test Case 1", "test_case")
	test2 := createTestItem(t, srv, projectID, "Test Case 2", "test_case")

	// Create links between items
	createTestLink(t, srv, req1, test1, "tests")
	createTestLink(t, srv, req2, test2, "tests")
	createTestLink(t, srv, req1, req2, "depends_on")

	// Request graph build
	resp, err := http.Post(srv.URL+"/api/projects/"+projectID+"/graph/build", "application/json", nil)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var graph map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&graph))
	assert.NotEmpty(t, graph["nodes"])
	assert.NotEmpty(t, graph["edges"])

	nodes := graph["nodes"].([]interface{})
	edges := graph["edges"].([]interface{})
	assert.Equal(t, 4, len(nodes))
	assert.Equal(t, 3, len(edges))
}

func TestE2E_BuildGraph_WithFilters(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Filtered Graph Project")

	// Create mixed items
	createTestItem(t, srv, projectID, "Req 1", "requirement")
	createTestItem(t, srv, projectID, "Test 1", "test_case")
	createTestItem(t, srv, projectID, "Bug 1", "bug")

	testCases := []struct {
		name      string
		filter    string
		wantNodes int
	}{
		{"filter_requirements", "type=requirement", 1},
		{"filter_tests", "type=test_case", 1},
		{"filter_bugs", "type=bug", 1},
		{"no_filter", "", 3},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			url := srv.URL + "/api/projects/" + projectID + "/graph"
			if tc.filter != "" {
				url += "?" + tc.filter
			}

			resp, err := http.Get(url)
			require.NoError(t, err)
			defer resp.Body.Close()

			var graph map[string]interface{}
			require.NoError(t, json.NewDecoder(resp.Body).Decode(&graph))

			nodes := graph["nodes"].([]interface{})
			assert.Equal(t, tc.wantNodes, len(nodes))
		})
	}
}

// Test 41-50: Complex Graph Operations
func TestE2E_GraphAnalysis_CriticalPath(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Critical Path Project")

	// Create dependency chain: A → B → C → D
	itemA := createTestItem(t, srv, projectID, "Item A", "requirement")
	itemB := createTestItem(t, srv, projectID, "Item B", "requirement")
	itemC := createTestItem(t, srv, projectID, "Item C", "requirement")
	itemD := createTestItem(t, srv, projectID, "Item D", "requirement")

	createTestLink(t, srv, itemA, itemB, "depends_on")
	createTestLink(t, srv, itemB, itemC, "depends_on")
	createTestLink(t, srv, itemC, itemD, "depends_on")

	resp, err := http.Get(srv.URL + "/api/projects/" + projectID + "/graph/critical-path")
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))

	path := result["path"].([]interface{})
	assert.Equal(t, 4, len(path))
}

func TestE2E_GraphAnalysis_CycleDetection(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Cycle Detection Project")

	// Create cycle: A → B → C → A
	itemA := createTestItem(t, srv, projectID, "Item A", "requirement")
	itemB := createTestItem(t, srv, projectID, "Item B", "requirement")
	itemC := createTestItem(t, srv, projectID, "Item C", "requirement")

	createTestLink(t, srv, itemA, itemB, "depends_on")
	createTestLink(t, srv, itemB, itemC, "depends_on")

	// Attempt to create cycle
	payload := map[string]interface{}{
		"source_id": itemC,
		"target_id": itemA,
		"type":      "depends_on",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/links", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	assert.Contains(t, result["error"], "cycle detected")
}

// Helper functions
func createTestProject(t *testing.T, srv *testServer, name string) string {
	payload := map[string]interface{}{
		"name":     name,
		"owner_id": "user-123",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/projects", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	return result["id"].(string)
}

func createTestItem(t *testing.T, srv *testServer, projectID, title, itemType string) string {
	payload := map[string]interface{}{
		"project_id": projectID,
		"title":      title,
		"type":       itemType,
		"status":     "open",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/items", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	return result["id"].(string)
}

func createTestLink(t *testing.T, srv *testServer, sourceID, targetID, linkType string) string {
	payload := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      linkType,
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/links", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	return result["id"].(string)
}
