//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestE2E_CreateItems_Index_Search_FullText tests full-text search workflow
func TestE2E_CreateItems_Index_Search_FullText(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "search.user@test.com")

	// Create items with specific searchable content
	testData := []struct {
		title       string
		description string
		tags        []string
	}{
		{"User Authentication System", "Implement JWT-based authentication with refresh tokens", []string{"auth", "security"}},
		{"Database Migration Tool", "Create automated database migration utility using Alembic", []string{"database", "migration"}},
		{"API Rate Limiting", "Add rate limiting middleware to prevent API abuse", []string{"api", "security"}},
		{"User Profile Dashboard", "Build user profile management dashboard with authentication", []string{"ui", "auth"}},
		{"Cache Implementation", "Implement Redis-based caching layer for database queries", []string{"performance", "database"}},
	}

	itemIDs := make([]string, len(testData))

	for i, data := range testData {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       data.title,
			"description": data.description,
			"type":        "feature",
			"metadata": map[string]interface{}{
				"tags": data.tags,
			},
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var itemResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&itemResp)
		resp.Body.Close()
		itemIDs[i] = itemResp.ID
	}

	// Wait for indexing
	time.Sleep(1 * time.Second)

	// Test 1: Search for "authentication" - should find items 0 and 3
	searchReq := map[string]interface{}{
		"query":       "authentication",
		"project_id":  projectID,
		"search_type": "fulltext",
		"limit":       10,
	}
	searchBody, _ := json.Marshal(searchReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var searchResp struct {
		Results []struct {
			ID    string  `json:"id"`
			Title string  `json:"title"`
			Score float64 `json:"score"`
		} `json:"results"`
		Total int `json:"total"`
	}
	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.GreaterOrEqual(t, searchResp.Total, 2)
	foundTitles := make([]string, len(searchResp.Results))
	for i, result := range searchResp.Results {
		foundTitles[i] = result.Title
	}
	assert.Contains(t, foundTitles, "User Authentication System")
	assert.Contains(t, foundTitles, "User Profile Dashboard")

	// Test 2: Search for "database" - should find items 1 and 4
	searchReq["query"] = "database"
	searchBody, _ = json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.GreaterOrEqual(t, searchResp.Total, 2)

	// Test 3: Search with filters (tag: security)
	searchReq = map[string]interface{}{
		"query":       "",
		"project_id":  projectID,
		"search_type": "fulltext",
		"filters": map[string]interface{}{
			"tags": []string{"security"},
		},
		"limit": 10,
	}
	searchBody, _ = json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.Equal(t, 2, searchResp.Total)
}

// TestE2E_CreateItems_Index_Search_Vector tests vector/semantic search
func TestE2E_CreateItems_Index_Search_Vector(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "vector.user@test.com")

	// Create items with semantically related content
	testData := []struct {
		title       string
		description string
	}{
		{"Login Form", "Create HTML form for user login with email and password"},
		{"Sign In Page", "Design authentication page for users to access their accounts"},
		{"Payment Gateway", "Integrate Stripe payment processing for subscriptions"},
		{"Billing System", "Implement recurring payment collection mechanism"},
		{"User Dashboard", "Build main interface showing user statistics and actions"},
	}

	for _, data := range testData {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       data.title,
			"description": data.description,
			"type":        "feature",
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		resp.Body.Close()
	}

	// Wait for vector indexing
	time.Sleep(2 * time.Second)

	// Semantic search: "authentication" should find login/signin items
	searchReq := map[string]interface{}{
		"query":       "user authentication",
		"project_id":  projectID,
		"search_type": "vector",
		"limit":       10,
	}
	searchBody, _ := json.Marshal(searchReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var searchResp struct {
		Results []struct {
			ID    string  `json:"id"`
			Title string  `json:"title"`
			Score float64 `json:"score"`
		} `json:"results"`
		Total int `json:"total"`
	}
	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.GreaterOrEqual(t, len(searchResp.Results), 2)
	// Top results should be semantically related to authentication
	topTitles := make([]string, 0)
	for i := 0; i < min(2, len(searchResp.Results)); i++ {
		topTitles = append(topTitles, searchResp.Results[i].Title)
	}
	assert.True(t, containsAny(topTitles, []string{"Login Form", "Sign In Page"}))

	// Semantic search: "payment" should find payment/billing items
	searchReq["query"] = "payment processing"
	searchBody, _ = json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.GreaterOrEqual(t, len(searchResp.Results), 2)
}

// TestE2E_CreateItems_Index_Search_Hybrid tests hybrid search (fulltext + vector)
func TestE2E_CreateItems_Index_Search_Hybrid(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "hybrid.user@test.com")

	// Create diverse items
	testData := []struct {
		title       string
		description string
	}{
		{"API Gateway Configuration", "Configure Kong API gateway with rate limiting and auth"},
		{"REST API Development", "Build RESTful API endpoints for user management"},
		{"GraphQL Schema Design", "Design GraphQL schema for flexible data queries"},
		{"Microservices Architecture", "Plan microservices structure for scalability"},
		{"Database Schema", "Design PostgreSQL database schema with relationships"},
		{"API Documentation", "Write comprehensive API documentation using OpenAPI"},
	}

	for _, data := range testData {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       data.title,
			"description": data.description,
			"type":        "task",
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		resp.Body.Close()
	}

	time.Sleep(2 * time.Second)

	// Hybrid search for "API"
	searchReq := map[string]interface{}{
		"query":       "API development",
		"project_id":  projectID,
		"search_type": "hybrid",
		"limit":       10,
	}
	searchBody, _ := json.Marshal(searchReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var searchResp struct {
		Results []struct {
			ID    string  `json:"id"`
			Title string  `json:"title"`
			Score float64 `json:"score"`
		} `json:"results"`
		Total int    `json:"total"`
		Type  string `json:"search_type"`
	}
	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.GreaterOrEqual(t, searchResp.Total, 3)
	assert.Equal(t, "hybrid", searchResp.Type)

	// Should find API-related items with good ranking
	foundAPIItems := 0
	for _, result := range searchResp.Results {
		if contains(result.Title, "API") {
			foundAPIItems++
		}
	}
	assert.GreaterOrEqual(t, foundAPIItems, 3)
}

// TestE2E_UpdateItem_ReindexAutomatic tests automatic reindexing on update
func TestE2E_UpdateItem_ReindexAutomatic(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "reindex.user@test.com")

	// Create item with original content
	itemReq := map[string]interface{}{
		"project_id":  projectID,
		"title":       "Original Title About Cats",
		"description": "This is about cats and kittens",
		"type":        "task",
	}
	itemBody, _ := json.Marshal(itemReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var itemResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&itemResp)
	resp.Body.Close()
	itemID := itemResp.ID

	time.Sleep(1 * time.Second)

	// Search for "cats" - should find the item
	searchReq := map[string]interface{}{
		"query":      "cats",
		"project_id": projectID,
	}
	searchBody, _ := json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	var searchResp struct {
		Results []struct {
			ID string `json:"id"`
		} `json:"results"`
	}
	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.Equal(t, 1, len(searchResp.Results))
	assert.Equal(t, itemID, searchResp.Results[0].ID)

	// Update item to completely different content
	updateReq := map[string]interface{}{
		"title":       "Updated Title About Dogs",
		"description": "Now this is about dogs and puppies",
	}
	updateBody, _ := json.Marshal(updateReq)
	req, _ = http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/items/"+itemID, bytes.NewBuffer(updateBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	time.Sleep(1 * time.Second)

	// Search for "cats" - should NOT find the item
	searchBody, _ = json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.Equal(t, 0, len(searchResp.Results))

	// Search for "dogs" - should find the item
	searchReq["query"] = "dogs"
	searchBody, _ = json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	json.NewDecoder(resp.Body).Decode(&searchResp)
	resp.Body.Close()

	assert.Equal(t, 1, len(searchResp.Results))
	assert.Equal(t, itemID, searchResp.Results[0].ID)
}

// Helper functions
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > len(substr) && containsSubstring(s, substr))
}

func containsSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

func containsAny(slice []string, targets []string) bool {
	for _, s := range slice {
		for _, t := range targets {
			if s == t {
				return true
			}
		}
	}
	return false
}
