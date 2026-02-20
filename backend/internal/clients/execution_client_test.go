package clients_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

const (
	executionClientWaitTimeout  = 10 * time.Second
	executionClientShortTimeout = 3 * time.Second
)

func TestExecutionClient_StartExecution(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r
		assert.Equal(t, "/api/v1/execution/start", r.URL.Path)
		assert.Equal(t, "POST", r.Method)

		// Verify request body
		var req clients.StartExecutionRequest
		err := json.NewDecoder(r.Body).Decode(&req)
		assert.NoError(t, err)
		assert.Equal(t, "test-project", req.ProjectID)
		assert.Equal(t, "docker", req.ExecutionType)

		// Return mock response
		response := clients.ExecutionStatus{
			ExecutionID: "exec-123",
			ProjectID:   req.ProjectID,
			Status:      "pending",
			StartedAt:   time.Now(),
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	// Create client
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	executionClient := clients.NewExecutionClient(pythonClient)

	// Test StartExecution
	result, err := executionClient.StartExecution(context.Background(), clients.StartExecutionRequest{
		ProjectID:     "test-project",
		ExecutionType: "docker",
		Command:       "pytest tests/",
	})

	require.NoError(t, err)
	assert.Equal(t, "exec-123", result.ExecutionID)
	assert.Equal(t, "pending", result.Status)
}

func TestExecutionClient_GetStatus(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r
		assert.Equal(t, "/api/v1/execution/exec-123/status", r.URL.Path)
		assert.Equal(t, "GET", r.Method)

		response := clients.ExecutionStatus{
			ExecutionID: "exec-123",
			ProjectID:   "test-project",
			Status:      "running",
			StartedAt:   time.Now(),
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	executionClient := clients.NewExecutionClient(pythonClient)

	result, err := executionClient.GetStatus(context.Background(), "exec-123")

	require.NoError(t, err)
	assert.Equal(t, "exec-123", result.ExecutionID)
	assert.Equal(t, "running", result.Status)
}

func TestExecutionClient_WaitForCompletion(t *testing.T) {
	callCount := 0

	// Create a mock server that returns "running" then "completed"
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r
		callCount++

		status := "running"
		if callCount >= 2 {
			status = "completed"
		}

		exitCode := 0
		response := clients.ExecutionStatus{
			ExecutionID: "exec-123",
			ProjectID:   "test-project",
			Status:      status,
			ExitCode:    &exitCode,
			StartedAt:   time.Now(),
		}

		if status == "completed" {
			now := time.Now()
			response.CompletedAt = &now
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	executionClient := clients.NewExecutionClient(pythonClient)

	result, err := executionClient.WaitForCompletion(context.Background(), "exec-123", executionClientWaitTimeout)

	require.NoError(t, err)
	assert.Equal(t, "completed", result.Status)
	assert.NotNil(t, result.CompletedAt)
	assert.GreaterOrEqual(t, callCount, 2)
}

func TestExecutionClient_WaitForCompletion_Timeout(t *testing.T) {
	// Create a mock server that always returns "running"
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r
		response := clients.ExecutionStatus{
			ExecutionID: "exec-123",
			ProjectID:   "test-project",
			Status:      "running",
			StartedAt:   time.Now(),
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	executionClient := clients.NewExecutionClient(pythonClient)

	_, err := executionClient.WaitForCompletion(context.Background(), "exec-123", executionClientShortTimeout)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "timeout")
}

func TestExecutionClient_CancelExecution(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r
		assert.Equal(t, "/api/v1/execution/exec-123", r.URL.Path)
		assert.Equal(t, "DELETE", r.Method)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		assert.NoError(t, json.NewEncoder(w).Encode(map[string]string{"message": "cancelled"}))
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	executionClient := clients.NewExecutionClient(pythonClient)

	err := executionClient.CancelExecution(context.Background(), "exec-123")

	require.NoError(t, err)
}

func TestExecutionClient_GetOutput(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r
		assert.Equal(t, "/api/v1/execution/exec-123/output", r.URL.Path)
		assert.Equal(t, "GET", r.Method)

		response := map[string]string{
			"output": "test output\nline 2\nline 3",
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	executionClient := clients.NewExecutionClient(pythonClient)

	output, err := executionClient.GetOutput(context.Background(), "exec-123")

	require.NoError(t, err)
	assert.Contains(t, output, "test output")
}

func TestExecutionClient_GetRecording(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = r
		assert.Equal(t, "/api/v1/execution/exec-123/recording", r.URL.Path)
		assert.Equal(t, "GET", r.Method)

		response := map[string][]byte{
			"recording": []byte("fake recording data"),
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	executionClient := clients.NewExecutionClient(pythonClient)

	recording, err := executionClient.GetRecording(context.Background(), "exec-123")

	require.NoError(t, err)
	assert.NotEmpty(t, recording)
}
