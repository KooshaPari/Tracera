//go:build !integration && !e2e

package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestItems_Create_Success tests successful item creation
func TestItems_Create_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	itemReq := map[string]interface{}{
		"project_id":  projectID,
		"title":       "Implement user authentication",
		"description": "Add OAuth2 support for user login",
		"type":        "feature",
		"status":      "in_progress",
		"priority":    "high",
		"assignee_id": uuid.New().String(),
		"metadata": map[string]interface{}{
			"sprint":       "sprint-23",
			"story_points": 8,
			"tags":         []string{"auth", "security"},
		},
	}

	body, err := json.Marshal(itemReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.NotEmpty(t, response["id"])
	assert.Equal(t, projectID, response["project_id"])
	assert.Equal(t, "Implement user authentication", response["title"])
	assert.Equal(t, "feature", response["type"])
	assert.Equal(t, "in_progress", response["status"])
	assert.Contains(t, response, "metadata")
}

// TestItems_Create_ValidationError tests validation errors on item creation
func TestItems_Create_ValidationError(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	testCases := []struct {
		name           string
		payload        map[string]interface{}
		expectedStatus int
		expectedError  string
	}{
		{
			name:           "missing project_id",
			payload:        map[string]interface{}{"title": "Test", "type": "task"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "project_id is required",
		},
		{
			name:           "missing title",
			payload:        map[string]interface{}{"project_id": projectID, "type": "task"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "title is required",
		},
		{
			name:           "empty title",
			payload:        map[string]interface{}{"project_id": projectID, "title": "", "type": "task"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "title cannot be empty",
		},
		{
			name:           "invalid type",
			payload:        map[string]interface{}{"project_id": projectID, "title": "Test", "type": "invalid_type"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "invalid item type",
		},
		{
			name:           "invalid status",
			payload:        map[string]interface{}{"project_id": projectID, "title": "Test", "type": "task", "status": "invalid_status"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "invalid status",
		},
		{
			name:           "invalid project_id",
			payload:        map[string]interface{}{"project_id": uuid.New().String(), "title": "Test", "type": "task"},
			expectedStatus: http.StatusNotFound,
			expectedError:  "project not found",
		},
		{
			name:           "invalid assignee_id format",
			payload:        map[string]interface{}{"project_id": projectID, "title": "Test", "type": "task", "assignee_id": "not-a-uuid"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "invalid assignee_id format",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			body, err := json.Marshal(tc.payload)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
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

// TestItems_Get_Success tests successful item retrieval
func TestItems_Get_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	itemID := createTestItem(t, server, projectID)

	req := httptest.NewRequest(http.MethodGet, "/api/v1/items/"+itemID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, itemID, response["id"])
	assert.Equal(t, projectID, response["project_id"])
	assert.NotEmpty(t, response["title"])
	assert.NotEmpty(t, response["created_at"])
}

// TestItems_Get_NotFound tests retrieval of non-existent item
func TestItems_Get_NotFound(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	nonExistentID := uuid.New().String()

	req := httptest.NewRequest(http.MethodGet, "/api/v1/items/"+nonExistentID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)
	assert.Contains(t, response["error"], "not found")
}

// TestItems_List_Success tests listing items
func TestItems_List_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create multiple items
	for i := 0; i < 5; i++ {
		createTestItem(t, server, projectID)
	}

	req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	items, ok := response["items"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(items), 5)

	assert.Contains(t, response, "total")
	assert.Contains(t, response, "page")
	assert.Contains(t, response, "page_size")
}

// TestItems_List_FilterByProject tests filtering items by project
func TestItems_List_FilterByProject(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	project1ID := createTestProject(t, server)
	project2ID := createTestProject(t, server)

	// Create items in project 1
	project1Items := make([]string, 3)
	for i := 0; i < 3; i++ {
		project1Items[i] = createTestItem(t, server, project1ID)
	}

	// Create items in project 2
	for i := 0; i < 2; i++ {
		createTestItem(t, server, project2ID)
	}

	// Filter by project 1
	url := "/api/v1/items?project_id=" + project1ID
	req := httptest.NewRequest(http.MethodGet, url, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	items, ok := response["items"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 3, len(items))

	// Verify all items belong to project 1
	for _, item := range items {
		itemMap := item.(map[string]interface{})
		assert.Equal(t, project1ID, itemMap["project_id"])
	}
}

// TestItems_List_FilterByStatus tests filtering items by status
func TestItems_List_FilterByStatus(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	statuses := []string{"open", "in_progress", "completed", "closed"}

	// Create items with different statuses
	for _, status := range statuses {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      "Item with status " + status,
			"type":       "task",
			"status":     status,
		}

		body, err := json.Marshal(itemReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Filter by status "in_progress"
	url := "/api/v1/items?status=in_progress"
	req := httptest.NewRequest(http.MethodGet, url, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	items, ok := response["items"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(items), 1)

	// Verify all items have status "in_progress"
	for _, item := range items {
		itemMap := item.(map[string]interface{})
		assert.Equal(t, "in_progress", itemMap["status"])
	}
}

// TestItems_Update_Success tests successful item update
func TestItems_Update_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	itemID := createTestItem(t, server, projectID)

	updateReq := map[string]interface{}{
		"title":       "Updated Item Title",
		"description": "Updated description",
		"status":      "completed",
		"priority":    "low",
		"metadata": map[string]interface{}{
			"completed_at": time.Now().Format(time.RFC3339),
			"resolution":   "fixed",
		},
	}

	body, err := json.Marshal(updateReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPut, "/api/v1/items/"+itemID, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, itemID, response["id"])
	assert.Equal(t, "Updated Item Title", response["title"])
	assert.Equal(t, "Updated description", response["description"])
	assert.Equal(t, "completed", response["status"])
	assert.NotEqual(t, response["created_at"], response["updated_at"])
}

// TestItems_Delete_Success tests successful item deletion
func TestItems_Delete_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	itemID := createTestItem(t, server, projectID)

	req := httptest.NewRequest(http.MethodDelete, "/api/v1/items/"+itemID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)

	// Verify item is deleted
	req = httptest.NewRequest(http.MethodGet, "/api/v1/items/"+itemID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}

// TestItems_Delete_CascadeLinks tests cascade deletion of item links
func TestItems_Delete_CascadeLinks(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	item1ID := createTestItem(t, server, projectID)
	item2ID := createTestItem(t, server, projectID)

	// Create a link between items
	linkReq := map[string]interface{}{
		"source_id": item1ID,
		"target_id": item2ID,
		"type":      "depends_on",
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var linkResponse map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&linkResponse)
	require.NoError(t, err)
	linkID := linkResponse["id"].(string)

	// Delete item1
	req = httptest.NewRequest(http.MethodDelete, "/api/v1/items/"+item1ID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)

	// Verify link is also deleted
	req = httptest.NewRequest(http.MethodGet, "/api/v1/links/"+linkID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}
