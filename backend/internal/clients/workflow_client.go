package clients

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
)

// WorkflowClient manages workflow orchestration via Temporal-backed Python service
type WorkflowClient struct {
	pythonClient *PythonServiceClient
}

// WorkflowTriggerRequest represents a request to trigger a workflow
type WorkflowTriggerRequest struct {
	WorkflowName string                 `json:"workflow_name"`
	Input        map[string]interface{} `json:"input"`
	ProjectID    string                 `json:"project_id"`
}

// WorkflowRun represents a workflow execution
type WorkflowRun struct {
	RunID        string                 `json:"run_id"`
	ProjectID    string                 `json:"project_id"`
	WorkflowName string                 `json:"workflow_name"`
	Status       string                 `json:"status"` // "pending", "running", "completed", "failed"
	Input        map[string]interface{} `json:"input"`
	Output       map[string]interface{} `json:"output,omitempty"`
	Error        string                 `json:"error,omitempty"`
	StartedAt    string                 `json:"started_at"`             // ISO 8601 string
	CompletedAt  *string                `json:"completed_at,omitempty"` // ISO 8601 string
}

// NewWorkflowClient creates a new workflow client
func NewWorkflowClient(pythonClient *PythonServiceClient) *WorkflowClient {
	return &WorkflowClient{
		pythonClient: pythonClient,
	}
}

// TriggerWorkflow triggers a new workflow
func (workflowClient *WorkflowClient) TriggerWorkflow(
	ctx context.Context,
	req WorkflowTriggerRequest,
) (*WorkflowRun, error) {
	var result WorkflowRun

	err := workflowClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodPost,
		"/api/v1/workflows/trigger",
		req,
		&result,
		false, // Not cacheable - workflows have side effects
		"",
		0,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to trigger workflow: %w", err)
	}

	return &result, nil
}

// GetWorkflowRun retrieves the status of a workflow run
func (workflowClient *WorkflowClient) GetWorkflowRun(
	ctx context.Context,
	runID string,
) (*WorkflowRun, error) {
	var result WorkflowRun

	// No caching - workflow state changes frequently
	err := workflowClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodGet,
		"/api/v1/workflows/runs/"+runID,
		nil,
		&result,
		false, // Not cacheable - state changes frequently
		"",
		0,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get workflow run: %w", err)
	}

	return &result, nil
}

// CancelWorkflowRun cancels a running workflow
func (workflowClient *WorkflowClient) CancelWorkflowRun(
	ctx context.Context,
	runID string,
) error {
	// Use a placeholder response struct for DELETE requests
	var result map[string]interface{}

	err := workflowClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodDelete,
		"/api/v1/workflows/runs/"+runID,
		nil,
		&result,
		false, // Not cacheable
		"",
		0,
	)
	if err != nil {
		return fmt.Errorf("failed to cancel workflow run: %w", err)
	}

	return nil
}

// ListWorkflowRuns lists workflow runs for a project
func (workflowClient *WorkflowClient) ListWorkflowRuns(
	ctx context.Context,
	projectID string,
	limit int,
) ([]*WorkflowRun, error) {
	type ListResponse struct {
		Runs []*WorkflowRun `json:"runs"`
	}

	var result ListResponse

	err := workflowClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodGet,
		"/api/v1/workflows/runs?project_id="+projectID+"&limit="+strconv.Itoa(limit),
		nil,
		&result,
		false, // Not cacheable - list can change
		"",
		0,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to list workflow runs: %w", err)
	}

	return result.Runs, nil
}
