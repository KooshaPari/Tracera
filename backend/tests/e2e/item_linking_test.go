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

// TestE2E_CreateItemChain_VerifyGraph tests creating a linear chain of items
func TestE2E_CreateItemChain_VerifyGraph(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "chain.user@test.com")

	// Create chain of 10 items
	chainLength := 10
	itemIDs := make([]string, chainLength)

	for i := 0; i < chainLength; i++ {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("Chain Item %d", i),
			"type":       "task",
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

	// Create chain links (0->1->2->...->9)
	for i := 0; i < chainLength-1; i++ {
		linkReq := map[string]interface{}{
			"source_id": itemIDs[i],
			"target_id": itemIDs[i+1],
			"type":      "next",
		}
		linkBody, _ := json.Marshal(linkReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusCreated, resp.StatusCode)
		resp.Body.Close()
	}

	// Verify chain by traversing from first item
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs[0]+"/graph?depth=20", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)

	var graphResp struct {
		Nodes []struct {
			ID    string `json:"id"`
			Title string `json:"title"`
		} `json:"nodes"`
		Edges []struct {
			SourceID string `json:"source_id"`
			TargetID string `json:"target_id"`
			Type     string `json:"type"`
		} `json:"edges"`
	}
	json.NewDecoder(resp.Body).Decode(&graphResp)
	resp.Body.Close()

	assert.Equal(t, chainLength, len(graphResp.Nodes))
	assert.Equal(t, chainLength-1, len(graphResp.Edges))

	// Verify edge order
	for i, edge := range graphResp.Edges {
		assert.Equal(t, itemIDs[i], edge.SourceID)
		assert.Equal(t, itemIDs[i+1], edge.TargetID)
		assert.Equal(t, "next", edge.Type)
	}
}

// TestE2E_CreateItemTree_TraverseGraph tests creating and traversing a tree structure
func TestE2E_CreateItemTree_TraverseGraph(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "tree.user@test.com")

	// Create tree structure:
	//        Root
	//       /  |  \
	//      A   B   C
	//     / \      |
	//    D   E     F

	itemNames := []string{"Root", "A", "B", "C", "D", "E", "F"}
	itemIDs := make(map[string]string)

	for _, name := range itemNames {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      name,
			"type":       "task",
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
		itemIDs[name] = itemResp.ID
	}

	// Create tree links
	treeLinks := []struct {
		source string
		target string
	}{
		{"Root", "A"},
		{"Root", "B"},
		{"Root", "C"},
		{"A", "D"},
		{"A", "E"},
		{"C", "F"},
	}

	for _, link := range treeLinks {
		linkReq := map[string]interface{}{
			"source_id": itemIDs[link.source],
			"target_id": itemIDs[link.target],
			"type":      "parent_of",
		}
		linkBody, _ := json.Marshal(linkReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusCreated, resp.StatusCode)
		resp.Body.Close()
	}

	// Traverse from root
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs["Root"]+"/graph?depth=3", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)

	var graphResp struct {
		Nodes []struct {
			ID string `json:"id"`
		} `json:"nodes"`
		Edges []struct {
			SourceID string `json:"source_id"`
			TargetID string `json:"target_id"`
		} `json:"edges"`
	}
	json.NewDecoder(resp.Body).Decode(&graphResp)
	resp.Body.Close()

	assert.Equal(t, 7, len(graphResp.Nodes))
	assert.Equal(t, 6, len(graphResp.Edges))

	// Test traversal from leaf node (should go up the tree)
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs["F"]+"/graph?depth=3&direction=incoming", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)

	var leafGraphResp struct {
		Nodes []struct {
			ID string `json:"id"`
		} `json:"nodes"`
	}
	json.NewDecoder(resp.Body).Decode(&leafGraphResp)
	resp.Body.Close()

	// Should include F, C, and Root
	assert.GreaterOrEqual(t, len(leafGraphResp.Nodes), 3)
}

// TestE2E_LinkCycle_Detection tests cycle detection in graph
func TestE2E_LinkCycle_Detection(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "cycle.user@test.com")

	// Create 3 items
	itemIDs := make([]string, 3)
	for i := 0; i < 3; i++ {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("Cycle Item %d", i),
			"type":       "task",
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

	// Create links: 0->1, 1->2
	for i := 0; i < 2; i++ {
		linkReq := map[string]interface{}{
			"source_id": itemIDs[i],
			"target_id": itemIDs[i+1],
			"type":      "depends_on",
		}
		linkBody, _ := json.Marshal(linkReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		resp.Body.Close()
	}

	// Try to create cycle: 2->0 (should be rejected or detected)
	linkReq := map[string]interface{}{
		"source_id": itemIDs[2],
		"target_id": itemIDs[0],
		"type":      "depends_on",
	}
	linkBody, _ := json.Marshal(linkReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(linkBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	// Depending on implementation, might reject (400) or accept with cycle flag
	if resp.StatusCode == http.StatusBadRequest {
		var errResp struct {
			Error string `json:"error"`
		}
		json.NewDecoder(resp.Body).Decode(&errResp)
		resp.Body.Close()
		assert.Contains(t, errResp.Error, "cycle")
	} else {
		resp.Body.Close()

		// Check for cycle via graph analysis endpoint
		req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemIDs[0]+"/analyze?type=cycles", nil)
		req.Header.Set("Authorization", "Bearer "+token)

		resp, err = client.Do(req)
		require.NoError(t, err)

		var analysisResp struct {
			HasCycles bool       `json:"has_cycles"`
			Cycles    [][]string `json:"cycles"`
		}
		json.NewDecoder(resp.Body).Decode(&analysisResp)
		resp.Body.Close()

		assert.True(t, analysisResp.HasCycles)
		assert.NotEmpty(t, analysisResp.Cycles)
	}
}

// TestE2E_BulkLinkCreation_Performance tests bulk link creation
func TestE2E_BulkLinkCreation_Performance(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 60 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "bulk.user@test.com")

	// Create 50 items
	itemCount := 50
	itemIDs := make([]string, itemCount)

	createStart := time.Now()
	for i := 0; i < itemCount; i++ {
		itemReq := map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("Bulk Item %d", i),
			"type":       "task",
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
	createDuration := time.Since(createStart)
	t.Logf("Created %d items in %v", itemCount, createDuration)

	// Create bulk links (each item links to next 3 items)
	links := make([]map[string]interface{}, 0)
	for i := 0; i < itemCount-3; i++ {
		for j := 1; j <= 3; j++ {
			links = append(links, map[string]interface{}{
				"source_id": itemIDs[i],
				"target_id": itemIDs[i+j],
				"type":      "related",
			})
		}
	}

	bulkLinkReq := map[string]interface{}{
		"links": links,
	}
	bulkLinkBody, _ := json.Marshal(bulkLinkReq)

	linkStart := time.Now()
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links/bulk", bytes.NewBuffer(bulkLinkBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	linkDuration := time.Since(linkStart)

	var bulkResp struct {
		Created int `json:"created"`
		Failed  int `json:"failed"`
	}
	json.NewDecoder(resp.Body).Decode(&bulkResp)
	resp.Body.Close()

	t.Logf("Created %d links in %v", bulkResp.Created, linkDuration)
	assert.Equal(t, len(links), bulkResp.Created)
	assert.Equal(t, 0, bulkResp.Failed)

	// Performance assertion: should create links in reasonable time
	assert.Less(t, linkDuration, 10*time.Second, "Bulk link creation took too long")
}

// Helper function to create user and project
func createUserAndProject(t *testing.T, client *http.Client, baseURL, email string) (token, projectID string) {
	userReq := map[string]interface{}{
		"email":    email,
		"password": "securePass123!",
		"name":     "Test User",
	}
	userBody, _ := json.Marshal(userReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(userBody))
	require.NoError(t, err)

	var authResp struct {
		Token string `json:"token"`
	}
	json.NewDecoder(resp.Body).Decode(&authResp)
	resp.Body.Close()
	token = authResp.Token

	projectReq := map[string]interface{}{
		"name": "Test Project",
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
	projectID = projectResp.ID

	return
}
