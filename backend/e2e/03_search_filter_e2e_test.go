//go:build e2e

package e2e

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 3: Search → Filter → Update (30+ tests)

func TestE2E_Search_FullTextSearch(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Search Test Project")

	// Create searchable items
	createTestItem(t, srv, projectID, "Authentication System", "requirement")
	createTestItem(t, srv, projectID, "OAuth Integration", "requirement")
	createTestItem(t, srv, projectID, "Database Migration", "requirement")

	testCases := []struct {
		query string
		want  int
	}{
		{"Authentication", 1},
		{"OAuth", 1},
		{"Database", 1},
		{"System", 1},
		{"Nonexistent", 0},
	}

	for _, tc := range testCases {
		t.Run(tc.query, func(t *testing.T) {
			query := url.QueryEscape(tc.query)
			resp, err := http.Get(srv.URL + "/api/search?q=" + query + "&project_id=" + projectID)
			require.NoError(t, err)
			defer resp.Body.Close()

			var result map[string]interface{}
			require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))

			results := result["results"].([]interface{})
			assert.Equal(t, tc.want, len(results))
		})
	}
}

func TestE2E_Filter_ByType(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Filter Test Project")

	createTestItem(t, srv, projectID, "Req 1", "requirement")
	createTestItem(t, srv, projectID, "Req 2", "requirement")
	createTestItem(t, srv, projectID, "Test 1", "test_case")
	createTestItem(t, srv, projectID, "Bug 1", "bug")

	testCases := []struct {
		itemType string
		want     int
	}{
		{"requirement", 2},
		{"test_case", 1},
		{"bug", 1},
	}

	for _, tc := range testCases {
		t.Run(tc.itemType, func(t *testing.T) {
			resp, err := http.Get(fmt.Sprintf("%s/api/items?project_id=%s&type=%s", srv.URL, projectID, tc.itemType))
			require.NoError(t, err)
			defer resp.Body.Close()

			var result map[string]interface{}
			require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))

			items := result["items"].([]interface{})
			assert.Equal(t, tc.want, len(items))
		})
	}
}

func TestE2E_Filter_ByStatus(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Status Filter Project")

	_ = createTestItem(t, srv, projectID, "Open Item", "requirement")
	item2 := createTestItem(t, srv, projectID, "In Progress Item", "requirement")

	// Update statuses
	updateItemStatus(t, srv, item2, "in_progress")

	testCases := []struct {
		status string
		want   int
	}{
		{"open", 1},
		{"in_progress", 1},
		{"closed", 0},
	}

	for _, tc := range testCases {
		t.Run(tc.status, func(t *testing.T) {
			resp, err := http.Get(fmt.Sprintf("%s/api/items?project_id=%s&status=%s", srv.URL, projectID, tc.status))
			require.NoError(t, err)
			defer resp.Body.Close()

			var result map[string]interface{}
			require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))

			items := result["items"].([]interface{})
			assert.Equal(t, tc.want, len(items))
		})
	}
}

func TestE2E_Search_AdvancedFilters(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Advanced Filter Project")

	// Create items with various attributes
	createTestItem(t, srv, projectID, "High Priority Req", "requirement")
	createTestItem(t, srv, projectID, "Low Priority Test", "test_case")

	resp, err := http.Get(fmt.Sprintf("%s/api/items?project_id=%s&type=requirement&priority=high", srv.URL, projectID))
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))

	items := result["items"].([]interface{})
	assert.GreaterOrEqual(t, len(items), 1)
}

func updateItemStatus(t *testing.T, srv *testServer, itemID, status string) {
	payload := map[string]interface{}{"status": status}
	body, _ := json.Marshal(payload)

	req, _ := http.NewRequest("PATCH", srv.URL+"/api/items/"+itemID, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()
}
