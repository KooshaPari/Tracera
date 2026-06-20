//go:build e2e

package e2e

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 5: API Integration - GitHub, Linear, Jira (35+ tests)

func TestE2E_GitHub_ImportIssues(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "GitHub Import Project")

	payload := map[string]interface{}{
		"project_id": projectID,
		"repo":       "owner/repo",
		"token":      "test-token",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/integrations/github/import", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusAccepted, resp.StatusCode)

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	assert.NotEmpty(t, result["job_id"])
}

func TestE2E_Linear_SyncIssues(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Linear Sync Project")

	payload := map[string]interface{}{
		"project_id": projectID,
		"api_key":    "linear-api-key",
		"team_id":    "team-123",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/integrations/linear/sync", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
}

func TestE2E_Jira_ImportEpics(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Jira Import Project")

	payload := map[string]interface{}{
		"project_id":  projectID,
		"jira_url":    "https://company.atlassian.net",
		"project_key": "PROJ",
		"username":    "user@example.com",
		"api_token":   "jira-token",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/integrations/jira/import", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusAccepted, resp.StatusCode)
}

func TestE2E_Webhook_GitHub_PullRequest(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	_ = createTestProject(t, srv, "Webhook Test Project")

	webhookPayload := map[string]interface{}{
		"action": "opened",
		"pull_request": map[string]interface{}{
			"number": 123,
			"title":  "Add new feature",
			"body":   "Implements #456",
		},
	}

	body, _ := json.Marshal(webhookPayload)
	resp, err := http.Post(srv.URL+"/api/webhooks/github", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
}
