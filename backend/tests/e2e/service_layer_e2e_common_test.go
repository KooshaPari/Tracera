//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"

	"github.com/stretchr/testify/require"
)

// Helper functions for E2E tests

func setupUser(t *testing.T, client *http.Client, baseURL, email string) string {
	userReq := map[string]interface{}{
		"email":    email,
		"password": "SecurePass123!",
		"name":     "Test User",
	}
	userBody, _ := json.Marshal(userReq)
	resp, err := client.Post(baseURL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(userBody))
	require.NoError(t, err)
	defer resp.Body.Close()

	var authResp struct {
		Token string `json:"token"`
	}
	json.NewDecoder(resp.Body).Decode(&authResp)
	return authResp.Token
}

func setupUserAndProject(t *testing.T, client *http.Client, baseURL, email, projectName string) (string, string) {
	token := setupUser(t, client, baseURL, email)
	projectID := createProject(t, client, baseURL, token, map[string]interface{}{
		"name": projectName,
	})
	return token, projectID
}

func createProject(t *testing.T, client *http.Client, baseURL, token string, data map[string]interface{}) string {
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/projects", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	defer resp.Body.Close()

	var projectResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&projectResp)
	return projectResp.ID
}

func createItem(t *testing.T, client *http.Client, baseURL, token, projectID string, data map[string]interface{}) string {
	data["project_id"] = projectID
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	defer resp.Body.Close()

	var itemResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&itemResp)
	return itemResp.ID
}

func updateItem(t *testing.T, client *http.Client, baseURL, token, itemID string, data map[string]interface{}) {
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/items/"+itemID, bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()
}

func deleteItem(t *testing.T, client *http.Client, baseURL, token, itemID string) {
	req, _ := http.NewRequestWithContext(context.Background(), "DELETE", baseURL+"/api/v1/items/"+itemID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusNoContent, resp.StatusCode)
	resp.Body.Close()
}

func getItem(t *testing.T, client *http.Client, baseURL, token, itemID string) map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var item map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&item)
	return item
}

func getProject(t *testing.T, client *http.Client, baseURL, token, projectID string) map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var project map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&project)
	return project
}

func createLink(t *testing.T, client *http.Client, baseURL, token, sourceID, targetID, linkType string, metadata map[string]interface{}) {
	linkReq := map[string]interface{}{
		"source_id": sourceID,
		"target_id": targetID,
		"type":      linkType,
	}
	if metadata != nil {
		linkReq["metadata"] = metadata
	}

	body, _ := json.Marshal(linkReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/links", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusCreated, resp.StatusCode)
	resp.Body.Close()
}

func getItemLinks(t *testing.T, client *http.Client, baseURL, token, itemID string) []map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemID+"/links", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var links []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&links)
	return links
}

func listProjectItems(t *testing.T, client *http.Client, baseURL, token, projectID string) []map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID+"/items", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var items []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&items)
	return items
}

func searchItems(t *testing.T, client *http.Client, baseURL, token string, query map[string]interface{}) []map[string]interface{} {
	body, _ := json.Marshal(query)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/search", bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var searchResp struct {
		Results []map[string]interface{} `json:"results"`
	}
	json.NewDecoder(resp.Body).Decode(&searchResp)
	return searchResp.Results
}

func filterProjectItems(t *testing.T, client *http.Client, baseURL, token, projectID string, filters map[string]string) []map[string]interface{} {
	url := baseURL + "/api/v1/projects/" + projectID + "/items?"
	for k, v := range filters {
		url += fmt.Sprintf("%s=%s&", k, v)
	}

	req, _ := http.NewRequestWithContext(context.Background(), "GET", url, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var items []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&items)
	return items
}

func updateAgent(t *testing.T, client *http.Client, baseURL, token, agentID string, data map[string]interface{}) {
	body, _ := json.Marshal(data)
	req, _ := http.NewRequestWithContext(context.Background(), "PATCH", baseURL+"/api/v1/agents/"+agentID, bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()
}

func getAgent(t *testing.T, client *http.Client, baseURL, token, agentID string) map[string]interface{} {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/agents/"+agentID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	defer resp.Body.Close()

	var agent map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&agent)
	return agent
}

func verifyItemDeleted(t *testing.T, client *http.Client, baseURL, token, itemID string) {
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/items/"+itemID, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusNotFound, resp.StatusCode)
	resp.Body.Close()
}
