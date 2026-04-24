//go:build !integration && !e2e

package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestProjects_Create_Success tests successful project creation
func TestProjects_Create_Success(t *testing.T) {
	// Setup
	server := setupTestServer(t)
	defer server.Close()

	projectReq := map[string]interface{}{
		"name":        "Test Project",
		"description": "A test project for API testing",
		"owner_id":    uuid.New().String(),
		"metadata": map[string]interface{}{
			"team": "engineering",
			"tags": []string{"test", "api"},
		},
	}

	body, err := json.Marshal(projectReq)
	require.NoError(t, err)

	// Execute
	req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	// Assert
	assert.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.NotEmpty(t, response["id"])
	assert.Equal(t, "Test Project", response["name"])
	assert.Equal(t, "A test project for API testing", response["description"])
	assert.NotEmpty(t, response["created_at"])
	assert.NotEmpty(t, response["updated_at"])
	assert.Contains(t, response, "metadata")
}

// TestProjects_Create_ValidationError tests validation errors on project creation
func TestProjects_Create_ValidationError(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	testCases := []struct {
		name           string
		payload        map[string]interface{}
		expectedStatus int
		expectedError  string
	}{
		{
			name:           "missing name",
			payload:        map[string]interface{}{"description": "No name"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "name is required",
		},
		{
			name:           "empty name",
			payload:        map[string]interface{}{"name": "", "description": "Empty name"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "name cannot be empty",
		},
		{
			name:           "name too long",
			payload:        map[string]interface{}{"name": string(make([]byte, 300))},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "name exceeds maximum length",
		},
		{
			name:           "invalid owner_id",
			payload:        map[string]interface{}{"name": "Test", "owner_id": "not-a-uuid"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "invalid owner_id format",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			body, err := json.Marshal(tc.payload)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(body))
			req.Header.Set("Content-Type", "application/json")
			w := httptest.NewRecorder()

			server.Config.Handler.ServeHTTP(w, req)

			assert.Equal(t, tc.expectedStatus, w.Code)

			var response map[string]interface{}
			err = json.NewDecoder(w.Body).Decode(&response)
			require.NoError(t, err)
			assert.Contains(t, response["error"], tc.expectedError)
		})
	}
}

// TestProjects_Get_Success tests successful project retrieval
func TestProjects_Get_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a project first
	projectID := createTestProject(t, server)

	// Execute
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+projectID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, projectID, response["id"])
	assert.NotEmpty(t, response["name"])
	assert.NotEmpty(t, response["created_at"])
}

// TestProjects_Get_NotFound tests retrieval of non-existent project
func TestProjects_Get_NotFound(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	nonExistentID := uuid.New().String()

	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+nonExistentID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)
	assert.Contains(t, response["error"], "not found")
}

// TestProjects_List_Success tests listing projects
func TestProjects_List_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create multiple projects
	for i := 0; i < 5; i++ {
		createTestProject(t, server)
	}

	// Execute
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	projects, ok := response["projects"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(projects), 5)

	// Verify pagination metadata
	assert.Contains(t, response, "total")
	assert.Contains(t, response, "page")
	assert.Contains(t, response, "page_size")
}

// TestProjects_List_Pagination tests project listing with pagination
func TestProjects_List_Pagination(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create 15 projects
	for i := 0; i < 15; i++ {
		createTestProject(t, server)
	}

	testCases := []struct {
		name          string
		page          int
		pageSize      int
		expectItems   int
		expectHasMore bool
	}{
		{
			name:          "first page",
			page:          1,
			pageSize:      5,
			expectItems:   5,
			expectHasMore: true,
		},
		{
			name:          "second page",
			page:          2,
			pageSize:      5,
			expectItems:   5,
			expectHasMore: true,
		},
		{
			name:          "last page",
			page:          3,
			pageSize:      5,
			expectItems:   5,
			expectHasMore: false,
		},
		{
			name:          "large page size",
			page:          1,
			pageSize:      20,
			expectItems:   15,
			expectHasMore: false,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			url := fmt.Sprintf("/api/v1/projects?page=%d&page_size=%d", tc.page, tc.pageSize)
			req := httptest.NewRequest(http.MethodGet, url, nil)
			w := httptest.NewRecorder()

			server.Config.Handler.ServeHTTP(w, req)

			assert.Equal(t, http.StatusOK, w.Code)

			var response map[string]interface{}
			err := json.NewDecoder(w.Body).Decode(&response)
			require.NoError(t, err)

			projects, ok := response["projects"].([]interface{})
			require.True(t, ok)
			assert.Equal(t, tc.expectItems, len(projects))
			assert.Equal(t, tc.expectHasMore, response["has_more"])
		})
	}
}

// TestProjects_Update_Success tests successful project update
func TestProjects_Update_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a project first
	projectID := createTestProject(t, server)

	// Update payload
	updateReq := map[string]interface{}{
		"name":        "Updated Project Name",
		"description": "Updated description",
		"metadata": map[string]interface{}{
			"status":   "active",
			"priority": 3,
		},
	}

	body, err := json.Marshal(updateReq)
	require.NoError(t, err)

	// Execute
	req := httptest.NewRequest(http.MethodPut, "/api/v1/projects/"+projectID, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	// Assert
	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, projectID, response["id"])
	assert.Equal(t, "Updated Project Name", response["name"])
	assert.Equal(t, "Updated description", response["description"])
	assert.NotEqual(t, response["created_at"], response["updated_at"])
}

// TestProjects_Delete_Success tests successful project deletion
func TestProjects_Delete_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a project first
	projectID := createTestProject(t, server)

	// Execute delete
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/projects/"+projectID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	// Assert
	assert.Equal(t, http.StatusNoContent, w.Code)

	// Verify project is deleted
	req = httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+projectID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}

// TestProjects_Delete_Cascade tests cascade deletion of project items
func TestProjects_Delete_Cascade(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create a project
	projectID := createTestProject(t, server)

	// Create items in the project
	itemIDs := make([]string, 3)
	for i := 0; i < 3; i++ {
		itemIDs[i] = createTestItem(t, server, projectID)
	}

	// Delete the project
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/projects/"+projectID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)

	// Verify all items are also deleted
	for _, itemID := range itemIDs {
		req = httptest.NewRequest(http.MethodGet, "/api/v1/items/"+itemID, nil)
		w = httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)

		assert.Equal(t, http.StatusNotFound, w.Code)
	}
}

// Helper functions

func setupTestServer(t *testing.T) *httptest.Server {
	// Initialize test database, router, and handlers
	// This is a placeholder - implement based on your actual setup
	mux := http.NewServeMux()

	// Register routes
	mux.HandleFunc("/api/v1/projects", handleProjects)
	mux.HandleFunc("/api/v1/projects/", handleProjectByID)
	mux.HandleFunc("/api/v1/items", handleItems)
	mux.HandleFunc("/api/v1/items/", handleItemByID)

	return httptest.NewServer(mux)
}

func createTestProject(t *testing.T, server *httptest.Server) string {
	projectReq := map[string]interface{}{
		"name":        fmt.Sprintf("Test Project %d", time.Now().UnixNano()),
		"description": "Test project",
		"owner_id":    uuid.New().String(),
	}

	body, err := json.Marshal(projectReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	return response["id"].(string)
}

func createTestItem(t *testing.T, server *httptest.Server, projectID string) string {
	itemReq := map[string]interface{}{
		"project_id": projectID,
		"title":      fmt.Sprintf("Test Item %d", time.Now().UnixNano()),
		"type":       "task",
		"status":     "open",
	}

	body, err := json.Marshal(itemReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	return response["id"].(string)
}

// Placeholder handlers - replace with actual implementation
func handleProjects(w http.ResponseWriter, r *http.Request) {
	// Implementation placeholder
}

func handleProjectByID(w http.ResponseWriter, r *http.Request) {
	// Implementation placeholder
}

func handleItems(w http.ResponseWriter, r *http.Request) {
	// Implementation placeholder
}

func handleItemByID(w http.ResponseWriter, r *http.Request) {
	// Implementation placeholder
}
