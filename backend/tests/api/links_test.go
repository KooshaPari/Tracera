//go:build !integration && !e2e

package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestLinks_Create_Success tests successful link creation
func TestLinks_Create_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	sourceID := createTestItem(t, server, projectID)
	targetID := createTestItem(t, server, projectID)

	linkReq := map[string]interface{}{
		"source_id":   sourceID,
		"target_id":   targetID,
		"type":        "depends_on",
		"description": "Target must be completed before source",
		"metadata": map[string]interface{}{
			"strength": "hard",
			"weight":   1.0,
		},
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.NotEmpty(t, response["id"])
	assert.Equal(t, sourceID, response["source_id"])
	assert.Equal(t, targetID, response["target_id"])
	assert.Equal(t, "depends_on", response["type"])
	assert.Contains(t, response, "metadata")
	assert.NotEmpty(t, response["created_at"])
}

// TestLinks_Create_Duplicate_Prevention tests prevention of duplicate links
func TestLinks_Create_Duplicate_Prevention(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	sourceID := createTestItem(t, server, projectID)
	targetID := createTestItem(t, server, projectID)

	// Create first link
	linkReq := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      "depends_on",
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)

	// Try to create duplicate link
	req = httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusConflict, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)
	assert.Contains(t, response["error"], "link already exists")
}

// TestLinks_Create_ValidationError tests validation errors on link creation
func TestLinks_Create_ValidationError(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	validItemID := createTestItem(t, server, projectID)

	testCases := []struct {
		name           string
		payload        map[string]interface{}
		expectedStatus int
		expectedError  string
	}{
		{
			name:           "missing source_id",
			payload:        map[string]interface{}{"target_id": validItemID, "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "source_id is required",
		},
		{
			name:           "missing target_id",
			payload:        map[string]interface{}{"source_id": validItemID, "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "target_id is required",
		},
		{
			name:           "missing type",
			payload:        map[string]interface{}{"source_id": validItemID, "target_id": validItemID},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "type is required",
		},
		{
			name:           "invalid type",
			payload:        map[string]interface{}{"source_id": validItemID, "target_id": validItemID, "type": "invalid_type"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "invalid link type",
		},
		{
			name:           "self-reference",
			payload:        map[string]interface{}{"source_id": validItemID, "target_id": validItemID, "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "cannot link item to itself",
		},
		{
			name:           "non-existent source",
			payload:        map[string]interface{}{"source_id": uuid.New().String(), "target_id": validItemID, "type": "depends_on"},
			expectedStatus: http.StatusNotFound,
			expectedError:  "source item not found",
		},
		{
			name:           "non-existent target",
			payload:        map[string]interface{}{"source_id": validItemID, "target_id": uuid.New().String(), "type": "depends_on"},
			expectedStatus: http.StatusNotFound,
			expectedError:  "target item not found",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			body, err := json.Marshal(tc.payload)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
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

// TestLinks_Get_Success tests successful link retrieval
func TestLinks_Get_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	sourceID := createTestItem(t, server, projectID)
	targetID := createTestItem(t, server, projectID)

	// Create a link
	linkReq := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      "relates_to",
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var createResponse map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&createResponse)
	require.NoError(t, err)
	linkID := createResponse["id"].(string)

	// Get the link
	req = httptest.NewRequest(http.MethodGet, "/api/v1/links/"+linkID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, linkID, response["id"])
	assert.Equal(t, sourceID, response["source_id"])
	assert.Equal(t, targetID, response["target_id"])
	assert.Equal(t, "relates_to", response["type"])
}

// TestLinks_List_Success tests listing all links
func TestLinks_List_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create multiple items
	items := make([]string, 4)
	for i := 0; i < 4; i++ {
		items[i] = createTestItem(t, server, projectID)
	}

	// Create multiple links
	linkTypes := []string{"depends_on", "relates_to", "blocks"}
	for i := 0; i < 3; i++ {
		linkReq := map[string]interface{}{
			"source_id": items[i],
			"target_id": items[i+1],
			"type":      linkTypes[i],
		}

		body, err := json.Marshal(linkReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// List all links
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links", nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	links, ok := response["links"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(links), 3)

	assert.Contains(t, response, "total")
}

// TestLinks_List_FilterBySource tests filtering links by source item
func TestLinks_List_FilterBySource(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create items
	source1ID := createTestItem(t, server, projectID)
	source2ID := createTestItem(t, server, projectID)
	target1ID := createTestItem(t, server, projectID)
	target2ID := createTestItem(t, server, projectID)

	// Create links from source1 to multiple targets
	for _, targetID := range []string{target1ID, target2ID} {
		linkReq := map[string]interface{}{
			"source_id": source1ID,
			"target_id": targetID,
			"type":      "depends_on",
		}

		body, err := json.Marshal(linkReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Create link from source2
	linkReq := map[string]interface{}{
		"source_id": source2ID,
		"target_id": target1ID,
		"type":      "relates_to",
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)
	require.Equal(t, http.StatusCreated, w.Code)

	// Filter links by source1
	url := "/api/v1/links?source_id=" + source1ID
	req = httptest.NewRequest(http.MethodGet, url, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	links, ok := response["links"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 2, len(links))

	// Verify all links have source1 as source
	for _, link := range links {
		linkMap := link.(map[string]interface{})
		assert.Equal(t, source1ID, linkMap["source_id"])
	}
}

// TestLinks_Update_Success tests successful link update
func TestLinks_Update_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	sourceID := createTestItem(t, server, projectID)
	targetID := createTestItem(t, server, projectID)

	// Create a link
	linkReq := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      "depends_on",
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var createResponse map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&createResponse)
	require.NoError(t, err)
	linkID := createResponse["id"].(string)

	// Update the link
	updateReq := map[string]interface{}{
		"type":        "blocks",
		"description": "Updated: This blocks the target",
		"metadata": map[string]interface{}{
			"priority": 3,
			"weight":   2.5,
		},
	}

	body, err = json.Marshal(updateReq)
	require.NoError(t, err)

	req = httptest.NewRequest(http.MethodPut, "/api/v1/links/"+linkID, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, linkID, response["id"])
	assert.Equal(t, "blocks", response["type"])
	assert.Equal(t, "Updated: This blocks the target", response["description"])
	assert.NotEqual(t, response["created_at"], response["updated_at"])
}

// TestLinks_Delete_Success tests successful link deletion
func TestLinks_Delete_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	sourceID := createTestItem(t, server, projectID)
	targetID := createTestItem(t, server, projectID)

	// Create a link
	linkReq := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      "depends_on",
	}

	body, err := json.Marshal(linkReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var createResponse map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&createResponse)
	require.NoError(t, err)
	linkID := createResponse["id"].(string)

	// Delete the link
	req = httptest.NewRequest(http.MethodDelete, "/api/v1/links/"+linkID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)

	// Verify link is deleted
	req = httptest.NewRequest(http.MethodGet, "/api/v1/links/"+linkID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)

	// Verify items still exist
	req = httptest.NewRequest(http.MethodGet, "/api/v1/items/"+sourceID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	req = httptest.NewRequest(http.MethodGet, "/api/v1/items/"+targetID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}
