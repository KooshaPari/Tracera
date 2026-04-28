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

// TestAgents_Register_Success tests successful agent registration
func TestAgents_Register_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	agentReq := map[string]interface{}{
		"name":         "test-agent-1",
		"type":         "worker",
		"version":      "1.0.0",
		"capabilities": []string{"process", "analyze", "transform"},
		"metadata": map[string]interface{}{
			"hostname": "agent-host-1",
			"region":   "us-west-2",
			"tags":     []string{"production", "critical"},
		},
	}

	body, err := json.Marshal(agentReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/agents/register", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.NotEmpty(t, response["id"])
	assert.Equal(t, "test-agent-1", response["name"])
	assert.Equal(t, "worker", response["type"])
	assert.Equal(t, "1.0.0", response["version"])
	assert.Equal(t, "active", response["status"])
	assert.NotEmpty(t, response["registered_at"])
	assert.NotEmpty(t, response["last_heartbeat"])
	assert.Contains(t, response, "capabilities")
}

// TestAgents_Register_Duplicate tests duplicate agent registration prevention
func TestAgents_Register_Duplicate(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	agentReq := map[string]interface{}{
		"name":    "duplicate-agent",
		"type":    "worker",
		"version": "1.0.0",
	}

	body, err := json.Marshal(agentReq)
	require.NoError(t, err)

	// First registration
	req := httptest.NewRequest(http.MethodPost, "/api/v1/agents/register", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)

	// Duplicate registration
	req = httptest.NewRequest(http.MethodPost, "/api/v1/agents/register", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusConflict, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)
	assert.Contains(t, response["error"], "agent already registered")
}

// TestAgents_Register_ValidationError tests validation errors on agent registration
func TestAgents_Register_ValidationError(t *testing.T) {
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
			payload:        map[string]interface{}{"type": "worker", "version": "1.0.0"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "name is required",
		},
		{
			name:           "empty name",
			payload:        map[string]interface{}{"name": "", "type": "worker", "version": "1.0.0"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "name cannot be empty",
		},
		{
			name:           "missing type",
			payload:        map[string]interface{}{"name": "test-agent", "version": "1.0.0"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "type is required",
		},
		{
			name:           "invalid type",
			payload:        map[string]interface{}{"name": "test-agent", "type": "invalid", "version": "1.0.0"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "invalid agent type",
		},
		{
			name:           "missing version",
			payload:        map[string]interface{}{"name": "test-agent", "type": "worker"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "version is required",
		},
		{
			name:           "invalid version format",
			payload:        map[string]interface{}{"name": "test-agent", "type": "worker", "version": "not-semver"},
			expectedStatus: http.StatusBadRequest,
			expectedError:  "invalid version format",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			body, err := json.Marshal(tc.payload)
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodPost, "/api/v1/agents/register", bytes.NewReader(body))
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

// TestAgents_Heartbeat_Success tests successful agent heartbeat
func TestAgents_Heartbeat_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Register an agent
	agentID := registerTestAgent(t, server, "heartbeat-agent")

	// Wait a bit to ensure timestamp difference
	time.Sleep(100 * time.Millisecond)

	// Send heartbeat
	heartbeatReq := map[string]interface{}{
		"status": "active",
		"metrics": map[string]interface{}{
			"cpu_usage":       45.2,
			"memory_usage":    67.8,
			"tasks_processed": 123,
		},
	}

	body, err := json.Marshal(heartbeatReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/agents/"+agentID+"/heartbeat", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, "active", response["status"])
	assert.NotEmpty(t, response["last_heartbeat"])
}

// TestAgents_List_Success tests listing agents
func TestAgents_List_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Register multiple agents
	agentTypes := []string{"worker", "coordinator", "monitor"}
	for i, agentType := range agentTypes {
		agentReq := map[string]interface{}{
			"name":    fmt.Sprintf("agent-%d", i),
			"type":    agentType,
			"version": "1.0.0",
		}

		body, err := json.Marshal(agentReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/agents/register", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// List agents
	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents", nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	agents, ok := response["agents"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(agents), 3)

	assert.Contains(t, response, "total")
}

// TestAgents_Get_Success tests retrieving a specific agent
func TestAgents_Get_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	agentID := registerTestAgent(t, server, "get-test-agent")

	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents/"+agentID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, agentID, response["id"])
	assert.Equal(t, "get-test-agent", response["name"])
	assert.NotEmpty(t, response["registered_at"])
}

// TestAgents_Update_Success tests updating agent information
func TestAgents_Update_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	agentID := registerTestAgent(t, server, "update-test-agent")

	updateReq := map[string]interface{}{
		"status":       "maintenance",
		"capabilities": []string{"process", "analyze", "transform", "report"},
		"metadata": map[string]interface{}{
			"updated": true,
			"reason":  "scheduled maintenance",
		},
	}

	body, err := json.Marshal(updateReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPut, "/api/v1/agents/"+agentID, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	assert.Equal(t, agentID, response["id"])
	assert.Equal(t, "maintenance", response["status"])

	capabilities, ok := response["capabilities"].([]interface{})
	require.True(t, ok)
	assert.Equal(t, 4, len(capabilities))
}

// TestAgents_Delete_Success tests agent deregistration
func TestAgents_Delete_Success(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	agentID := registerTestAgent(t, server, "delete-test-agent")

	req := httptest.NewRequest(http.MethodDelete, "/api/v1/agents/"+agentID, nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)

	// Verify agent is deleted
	req = httptest.NewRequest(http.MethodGet, "/api/v1/agents/"+agentID, nil)
	w = httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}

// TestAgents_List_FilterByType tests filtering agents by type
func TestAgents_List_FilterByType(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Register agents of different types
	types := []string{"worker", "worker", "coordinator", "monitor"}
	for i, agentType := range types {
		agentReq := map[string]interface{}{
			"name":    fmt.Sprintf("agent-type-%d", i),
			"type":    agentType,
			"version": "1.0.0",
		}

		body, err := json.Marshal(agentReq)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/api/v1/agents/register", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()

		server.Config.Handler.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	// Filter by worker type
	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents?type=worker", nil)
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	agents, ok := response["agents"].([]interface{})
	require.True(t, ok)
	assert.GreaterOrEqual(t, len(agents), 2)

	// Verify all are workers
	for _, agent := range agents {
		agentMap := agent.(map[string]interface{})
		assert.Equal(t, "worker", agentMap["type"])
	}
}

// Helper functions

func registerTestAgent(t *testing.T, server *httptest.Server, name string) string {
	agentReq := map[string]interface{}{
		"name":         name,
		"type":         "worker",
		"version":      "1.0.0",
		"capabilities": []string{"process", "analyze"},
	}

	body, err := json.Marshal(agentReq)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/api/v1/agents/register", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.Config.Handler.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var response map[string]interface{}
	err = json.NewDecoder(w.Body).Decode(&response)
	require.NoError(t, err)

	return response["id"].(string)
}
