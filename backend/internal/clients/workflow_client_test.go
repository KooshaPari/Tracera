package clients_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

func TestWorkflowClient_TriggerWorkflow(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/v1/workflows/trigger", r.URL.Path)
		assert.Equal(t, "POST", r.Method)

		// Verify request body
		var req clients.WorkflowTriggerRequest
		err := json.NewDecoder(r.Body).Decode(&req)
		assert.NoError(t, err)
		assert.Equal(t, "test-workflow", req.WorkflowName)
		assert.Equal(t, "test-project", req.ProjectID)

		// Return mock response
		response := clients.WorkflowRun{
			RunID:        "run-123",
			ProjectID:    req.ProjectID,
			WorkflowName: "test-workflow",
			Status:       "pending",
			Input:        req.Input,
			StartedAt:    "2024-01-01T00:00:00Z",
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	workflowClient := clients.NewWorkflowClient(pythonClient)

	result, err := workflowClient.TriggerWorkflow(context.Background(), clients.WorkflowTriggerRequest{
		WorkflowName: "test-workflow",
		ProjectID:    "test-project",
		Input:        map[string]interface{}{"key": "value"},
	})

	require.NoError(t, err)
	assert.Equal(t, "run-123", result.RunID)
	assert.Equal(t, "test-workflow", result.WorkflowName)
	assert.Equal(t, "pending", result.Status)
}

func TestWorkflowClient_GetWorkflowRun(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/v1/workflows/runs/run-123", r.URL.Path)
		assert.Equal(t, "GET", r.Method)

		response := clients.WorkflowRun{
			RunID:        "run-123",
			ProjectID:    "test-project",
			WorkflowName: "test-workflow",
			Status:       "completed",
			Output:       map[string]interface{}{"result": "success"},
			StartedAt:    "2024-01-01T00:00:00Z",
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	workflowClient := clients.NewWorkflowClient(pythonClient)

	result, err := workflowClient.GetWorkflowRun(context.Background(), "run-123")

	require.NoError(t, err)
	assert.Equal(t, "run-123", result.RunID)
	assert.Equal(t, "completed", result.Status)
}

func TestWorkflowClient_CancelWorkflowRun(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/v1/workflows/runs/run-123", r.URL.Path)
		assert.Equal(t, "DELETE", r.Method)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		assert.NoError(t, json.NewEncoder(w).Encode(map[string]string{"message": "cancelled"}))
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	workflowClient := clients.NewWorkflowClient(pythonClient)

	err := workflowClient.CancelWorkflowRun(context.Background(), "run-123")

	require.NoError(t, err)
}

func TestWorkflowClient_ListWorkflowRuns(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/v1/workflows/runs", r.URL.Path)
		assert.Equal(t, "GET", r.Method)
		assert.Equal(t, "test-project", r.URL.Query().Get("project_id"))
		assert.Equal(t, "10", r.URL.Query().Get("limit"))

		response := map[string]interface{}{
			"runs": []*clients.WorkflowRun{
				{
					RunID:        "run-1",
					ProjectID:    "test-project",
					WorkflowName: "workflow-1",
					Status:       "completed",
					StartedAt:    "2024-01-01T00:00:00Z",
				},
				{
					RunID:        "run-2",
					ProjectID:    "test-project",
					WorkflowName: "workflow-2",
					Status:       "running",
					StartedAt:    "2024-01-01T01:00:00Z",
				},
			},
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	workflowClient := clients.NewWorkflowClient(pythonClient)

	runs, err := workflowClient.ListWorkflowRuns(context.Background(), "test-project", 10)

	require.NoError(t, err)
	assert.Len(t, runs, 2)
	assert.Equal(t, "run-1", runs[0].RunID)
	assert.Equal(t, "run-2", runs[1].RunID)
}
