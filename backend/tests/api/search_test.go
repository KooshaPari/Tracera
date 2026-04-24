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

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestSearch_FullText_Success tests full-text search functionality
func TestSearch_FullText_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create items with different content
	itemContents := []map[string]string{
		{"title": "Implement authentication system", "description": "Add OAuth2 login support"},
		{"title": "Database migration script", "description": "Create schema for user authentication"},
		{"title": "Frontend UI components", "description": "Build reusable React components"},
		{"title": "API authentication endpoints", "description": "RESTful endpoints for user login"},
	}

	for _, content := range itemContents {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       content["title"],
			"description": content["description"],
			"type":        "task",
		}

		body, err := json.Marshal(itemReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Wait for indexing
	time.Sleep(100 * time.Millisecond)

	// Search for "authentication"
	searchReq := map[string]interface{}{
		"query":      "authentication",
		"type":       "fulltext",
		"project_id": projectID,
	}

	body, err := json.Marshal(searchReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/search", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	results, ok := response["results"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(results), 3) // Should find 3 items with "authentication"

	// Verify results have scores
	for _, result := range results {
		resultMap := result.(map[string]interface{})
		assert.Contains(t, resultMap, "score")
		assert.Contains(t, resultMap, "title")
		assert.Contains(t, resultMap, "highlights")
	}

	assert.Contains(t, response, "total_results")
	assert.Contains(t, response, "search_time_ms")
}

// TestSearch_Vector_Success tests vector similarity search
func TestSearch_Vector_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create items with semantic content
	semanticItems := []map[string]string{
		{"title": "User login functionality", "description": "Allow users to authenticate with credentials"},
		{"title": "Sign in feature", "description": "User authentication and session management"},
		{"title": "Database backup", "description": "Automated daily backups of production database"},
		{"title": "Logout implementation", "description": "Securely end user sessions"},
	}

	for _, content := range semanticItems {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       content["title"],
			"description": content["description"],
			"type":        "task",
		}

		body, err := json.Marshal(itemReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Wait for embedding generation
	time.Sleep(200 * time.Millisecond)

	// Search for semantically similar items
	searchReq := map[string]interface{}{
		"query":      "authentication and login system",
		"type":       "vector",
		"project_id": projectID,
		"limit":      5,
	}

	body, err := json.Marshal(searchReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/search", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	results, ok := response["results"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(results), 2)

	// Verify similarity scores
	for _, result := range results {
		resultMap := result.(map[string]interface{})
		score, ok := resultMap["similarity_score"].(float64)
		require.True(t, ok)
		assert.GreaterOrEqual(t, score, 0.0)
		assert.LessOrEqual(t, score, 1.0)
	}

	// Results should be ordered by similarity
	if len(results) > 1 {
		score1 := results[0].(map[string]interface{})["similarity_score"].(float64)
		score2 := results[1].(map[string]interface{})["similarity_score"].(float64)
		assert.GreaterOrEqual(t, score1, score2)
	}
}

// TestSearch_Hybrid_Success tests hybrid search (fulltext + vector)
func TestSearch_Hybrid_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create diverse items
	items := []map[string]string{
		{"title": "React authentication hooks", "description": "Custom hooks for user authentication in React"},
		{"title": "Login API endpoint", "description": "REST API for user sign-in"},
		{"title": "Database schema", "description": "PostgreSQL tables and relationships"},
		{"title": "Auth middleware", "description": "Express middleware for authentication"},
	}

	for _, content := range items {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       content["title"],
			"description": content["description"],
			"type":        "task",
		}

		body, err := json.Marshal(itemReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Wait for indexing
	time.Sleep(200 * time.Millisecond)

	// Hybrid search
	searchReq := map[string]interface{}{
		"query":      "authentication API",
		"type":       "hybrid",
		"project_id": projectID,
		"weights": map[string]interface{}{
			"fulltext": 0.6,
			"vector":   0.4,
		},
	}

	body, err := json.Marshal(searchReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/search", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	results, ok := response["results"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(results), 2)

	// Verify hybrid scores
	for _, result := range results {
		resultMap := result.(map[string]interface{})
		assert.Contains(t, resultMap, "hybrid_score")
		assert.Contains(t, resultMap, "fulltext_score")
		assert.Contains(t, resultMap, "vector_score")
	}

	assert.Equal(t, "hybrid", response["search_type"])
}

// TestSearch_Fuzzy_Success tests fuzzy search for typo tolerance
func TestSearch_Fuzzy_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create items with specific terms
	itemReq := map[string]interface{}{
		"project_id":  projectID,
		"title":       "Authentication middleware implementation",
		"description": "Secure authentication layer for API requests",
		"type":        "task",
	}

	body, err := json.Marshal(itemReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)
	require.Equal(t, http.StatusCreated, w.Code)

	// Wait for indexing
	time.Sleep(100 * time.Millisecond)

	// Fuzzy search with typos
	testCases := []struct {
		query         string
		expectedMatch bool
		description   string
	}{
		{
			query:         "authentcation", // Missing 'i'
			expectedMatch: true,
			description:   "single character missing",
		},
		{
			query:         "authetication", // Missing 'n'
			expectedMatch: true,
			description:   "single character missing (different position)",
		},
		{
			query:         "authentication", // Correct spelling
			expectedMatch: true,
			description:   "exact match",
		},
		{
			query:         "middleware", // Correct spelling
			expectedMatch: true,
			description:   "exact match different word",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			searchReq := map[string]interface{}{
				"query":      tc.query,
				"type":       "fuzzy",
				"project_id": projectID,
				"fuzziness":  2,
			}

			body, err := json.Marshal(searchReq)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/v1/search", bytes.NewReader(body))
			req.Header.Set("Content-Type", "application/json")
			w := httptest.NewRecorder()

			server.Config.Handler.ServeHTTP(w, req)

			assert.Equal(t, http.StatusOK, w.Code)

			var response map[string]interface{}
			err = json.NewDecoder(w.Body).Decode(&response)
			require.NoError(t, err)

			results, ok := response["results"].([]interface{})
			require.True(t, ok)

			if tc.expectedMatch {
				assert.GreaterOrEqual(t, len(results), 1)
			}
		})
	}
}

// TestSearch_Pagination tests search result pagination
func TestSearch_Pagination(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create many items with common term
	for i := 0; i < 25; i++ {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       fmt.Sprintf("Task %d for development", i),
			"description": "Development task description",
			"type":        "task",
		}

		body, err := json.Marshal(itemReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Wait for indexing
	time.Sleep(200 * time.Millisecond)

	testCases := []struct {
		name        string
		page        int
		pageSize    int
		expectedLen int
		expectMore  bool
	}{
		{
			name:        "first page",
			page:        1,
			pageSize:    10,
			expectedLen: 10,
			expectMore:  true,
		},
		{
			name:        "second page",
			page:        2,
			pageSize:    10,
			expectedLen: 10,
			expectMore:  true,
		},
		{
			name:        "third page",
			page:        3,
			pageSize:    10,
			expectedLen: 5,
			expectMore:  false,
		},
		{
			name:        "large page size",
			page:        1,
			pageSize:    30,
			expectedLen: 25,
			expectMore:  false,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			searchReq := map[string]interface{}{
				"query":      "development",
				"type":       "fulltext",
				"project_id": projectID,
				"page":       tc.page,
				"page_size":  tc.pageSize,
			}

			body, err := json.Marshal(searchReq)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/v1/search", bytes.NewReader(body))
			req.Header.Set("Content-Type", "application/json")
			w := httptest.NewRecorder()

			server.Config.Handler.ServeHTTP(w, req)

			assert.Equal(t, http.StatusOK, w.Code)

			var response map[string]interface{}
			err = json.NewDecoder(w.Body).Decode(&response)
			require.NoError(t, err)

			results, ok := response["results"].([]interface{})
			require.True(t, ok)
			assert.Equal(t, tc.expectedLen, len(results))

			assert.Equal(t, float64(tc.page), response["page"])
			assert.Equal(t, float64(tc.pageSize), response["page_size"])
			assert.Equal(t, tc.expectMore, response["has_more"])
			assert.Equal(t, float64(25), response["total_results"])
		})
	}
}

// TestSearch_Index_Success tests manual search index update
func TestSearch_Index_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)
	itemID := createTestItem(t, server, projectID)

	// Index the item
	indexReq := map[string]interface{}{
		"item_id":    itemID,
		"project_id": projectID,
		"operation":  "index",
	}

	body, err := json.Marshal(indexReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/search/index", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, "success", response["status"])
	assert.Equal(t, itemID, response["item_id"])
	assert.Contains(t, response, "indexed_at")
}

// TestSearch_Filters tests search with filters
func TestSearch_Filters(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	projectID := createTestProject(t, server)

	// Create items with different attributes
	itemTypes := []string{"task", "bug", "feature"}
	statuses := []string{"open", "in_progress", "completed"}

	for i, itemType := range itemTypes {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       "Development " + itemType + " item",
			"description": "Development work",
			"type":        itemType,
			"status":      statuses[i],
			"priority":    "high",
		}

		body, err := json.Marshal(itemReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Wait for indexing
	time.Sleep(100 * time.Millisecond)

	// Search with filters
	searchReq := map[string]interface{}{
		"query":      "development",
		"type":       "fulltext",
		"project_id": projectID,
		"filters": map[string]interface{}{
			"type":     "task",
			"status":   "open",
			"priority": 3,
		},
	}

	body, err := json.Marshal(searchReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/search", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	results, ok := response["results"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 1, len(results))

	// Verify filtered result
	result := results[0].(map[string]interface{})
	assert.Equal(t, "task", result["type"])
	assert.Equal(t, "open", result["status"])
}
