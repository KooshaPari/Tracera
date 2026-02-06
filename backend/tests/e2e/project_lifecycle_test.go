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

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestE2E_CreateProject_AddItems_CreateLinks_Search tests complete project workflow
func TestE2E_CreateProject_AddItems_CreateLinks_Search(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Step 1: Create user and login
	userReq := map[string]interface{}{
		"email":    "project.user@test.com",
		"password": "securePass123!",
		"name":     "Project User",
	}
	userBody, _ := json.Marshal(userReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(userBody))
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)

	var authResp struct {
		Token  string `json:"token"`
		UserID string `json:"user_id"`
	}
	err = json.NewDecoder(resp.Body).Decode(&authResp)
	require.NoError(t, err)
	resp.Body.Close()

	token := authResp.Token

	// Step 2: Create project
	projectReq := map[string]interface{}{
		"name":        "E2E Test Project",
		"description": "Full lifecycle test project",
		"settings": map[string]interface{}{
			"visibility": "private",
		},
	}
	projectBody, _ := json.Marshal(projectReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/projects", bytes.NewBuffer(projectBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)

	var projectResp struct {
		ID          string    `json:"id"`
		Name        string    `json:"name"`
		Description string    `json:"description"`
		CreatedAt   time.Time `json:"created_at"`
	}
	err = json.NewDecoder(resp.Body).Decode(&projectResp)
	require.NoError(t, err)
	resp.Body.Close()

	projectID := projectResp.ID
	assert.Equal(t, "E2E Test Project", projectResp.Name)

	// Step 3: Create multiple items
	itemIDs := make([]string, 0, 5)
	itemTypes := []string{"task", "bug", "feature", "documentation", "research"}

	for i, itemType := range itemTypes {
		itemReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       fmt.Sprintf("Test %s %d", itemType, i+1),
			"type":        itemType,
			"description": "This is a test " + itemType + " for E2E testing",
			"metadata": map[string]interface{}{
				"priority": 3,
				"tags":     []string{"e2e", "test", itemType},
			},
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err = client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusCreated, resp.StatusCode)

		var itemResp struct {
			ID    string `json:"id"`
			Title string `json:"title"`
		}
		err = json.NewDecoder(resp.Body).Decode(&itemResp)
		require.NoError(t, err)
		resp.Body.Close()

		itemIDs = append(itemIDs, itemResp.ID)
		time.Sleep(100 * time.Millisecond) // Allow indexing
	}

	require.Len(t, itemIDs, 5)

	// Step 4: Create links between items
	linkReq := map[string]interface{}{
		"source_id": itemIDs[0],
		"target_id": itemIDs[1],
		"type":      "blocks",
		"metadata": map[string]interface{}{
			"reason": "E2E dependency",
		},
	}
	linkBody, _ := json.Marshal(linkReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	resp.Body.Close()

	// Create more links
	for i := 1; i < len(itemIDs)-1; i++ {
		linkReq := map[string]interface{}{
			"source_id": itemIDs[i],
			"target_id": itemIDs[i+1],
			"type":      "depends_on",
		}
		linkBody, _ := json.Marshal(linkReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err = client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusCreated, resp.StatusCode)
		resp.Body.Close()
	}

	// Step 5: Search for items
	time.Sleep(500 * time.Millisecond) // Allow search indexing

	searchReq := map[string]interface{}{
		"query":      "test",
		"project_id": projectID,
		"limit":      10,
	}
	searchBody, _ := json.Marshal(searchReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(searchBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)

	var searchResp struct {
		Results []struct {
			ID    string  `json:"id"`
			Title string  `json:"title"`
			Score float64 `json:"score"`
		} `json:"results"`
		Total int `json:"total"`
	}
	err = json.NewDecoder(resp.Body).Decode(&searchResp)
	require.NoError(t, err)
	resp.Body.Close()

	assert.GreaterOrEqual(t, searchResp.Total, 5)
	assert.GreaterOrEqual(t, len(searchResp.Results), 5)

	// Step 6: Get project with all items
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID+"?include_items=true", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)

	var fullProjectResp struct {
		ID         string `json:"id"`
		Name       string `json:"name"`
		ItemsCount int    `json:"items_count"`
		LinksCount int    `json:"links_count"`
	}
	err = json.NewDecoder(resp.Body).Decode(&fullProjectResp)
	require.NoError(t, err)
	resp.Body.Close()

	assert.Equal(t, 5, fullProjectResp.ItemsCount)
	assert.Equal(t, 4, fullProjectResp.LinksCount)
}

// TestE2E_ProjectWithMultipleUsers_Collaboration tests multi-user collaboration
func TestE2E_ProjectWithMultipleUsers_Collaboration(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Create two users
	tokens := make([]string, 2)
	userIDs := make([]string, 2)

	for i := 0; i < 2; i++ {
		userReq := map[string]interface{}{
			"email":    fmt.Sprintf("collab.user%d@test.com", i+1),
			"password": "securePass123!",
			"name":     fmt.Sprintf("Collab User %d", i+1),
		}
		userBody, _ := json.Marshal(userReq)
		resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(userBody))
		require.NoError(t, err)

		var authResp struct {
			Token  string `json:"token"`
			UserID string `json:"user_id"`
		}
		json.NewDecoder(resp.Body).Decode(&authResp)
		resp.Body.Close()

		tokens[i] = authResp.Token
		userIDs[i] = authResp.UserID
	}

	// User 1 creates project
	projectReq := map[string]interface{}{
		"name":        "Collaboration Project",
		"description": "Multi-user test",
	}
	projectBody, _ := json.Marshal(projectReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/projects", bytes.NewBuffer(projectBody))
	req.Header.Set("Authorization", "Bearer "+tokens[0])
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var projectResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&projectResp)
	resp.Body.Close()
	projectID := projectResp.ID

	// User 1 adds User 2 as collaborator
	memberReq := map[string]interface{}{
		"user_id": userIDs[1],
		"role":    "editor",
	}
	memberBody, _ := json.Marshal(memberReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/projects/"+projectID+"/members", bytes.NewBuffer(memberBody))
	req.Header.Set("Authorization", "Bearer "+tokens[0])
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	resp.Body.Close()

	// User 2 creates item in project
	itemReq := map[string]interface{}{
		"project_id": projectID,
		"title":      "Item by User 2",
		"type":       "task",
	}
	itemBody, _ := json.Marshal(itemReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
	req.Header.Set("Authorization", "Bearer "+tokens[1])
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)

	var itemResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&itemResp)
	resp.Body.Close()

	// User 1 can see item created by User 2
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemResp.ID, nil)
	req.Header.Set("Authorization", "Bearer "+tokens[0])

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()
}

// TestE2E_ProjectDeletion_CascadeBehavior tests cascade deletion
func TestE2E_ProjectDeletion_CascadeBehavior(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Create user and login
	userReq := map[string]interface{}{
		"email":    "delete.user@test.com",
		"password": "securePass123!",
		"name":     "Delete User",
	}
	userBody, _ := json.Marshal(userReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(userBody))
	require.NoError(t, err)

	var authResp struct {
		Token string `json:"token"`
	}
	json.NewDecoder(resp.Body).Decode(&authResp)
	resp.Body.Close()
	token := authResp.Token

	// Create project
	projectReq := map[string]interface{}{
		"name": "Project to Delete",
	}
	projectBody, _ := json.Marshal(projectReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/projects", bytes.NewBuffer(projectBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)

	var projectResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&projectResp)
	resp.Body.Close()
	projectID := projectResp.ID

	// Create items
	itemIDs := make([]string, 3)
	for i := 0; i < 3; i++ {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("Item %d", i),
			"type":       "task",
		}
		itemBody, _ := json.Marshal(itemReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(itemBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err = client.Do(req)
		require.NoError(t, err)

		var itemResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&itemResp)
		resp.Body.Close()
		itemIDs[i] = itemResp.ID
	}

	// Delete project
	req, _ = http.NewRequestWithContext(context.Background(), "DELETE", baseURL+"/api/v1/projects/"+projectID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusNoContent, resp.StatusCode)
	resp.Body.Close()

	// Verify project is gone
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, resp.StatusCode)
	resp.Body.Close()

	// Verify items are gone
	for _, itemID := range itemIDs {
		req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemID, nil)
		req.Header.Set("Authorization", "Bearer "+token)

		resp, err = client.Do(req)
		require.NoError(t, err)
		assert.Equal(t, http.StatusNotFound, resp.StatusCode)
		resp.Body.Close()
	}
}
