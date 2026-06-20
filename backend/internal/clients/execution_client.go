package clients

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"time"
)

const (
	executionStatusCacheTTL = 5 * time.Second
	executionPollInterval   = 2 * time.Second
	executionOutputCacheTTL = 1 * time.Minute
	executionStatusComplete = "completed"
	executionStatusFailed   = "failed"
)

// ExecutionClient manages execution orchestration via Python services
type ExecutionClient struct {
	pythonClient *PythonServiceClient
}

// RecordingOptions configures recording for execution
type RecordingOptions struct {
	OutputPath string `json:"output_path"`
	Format     string `json:"format"` // "mp4", "gif", "tape"
	Width      int    `json:"width"`
	Height     int    `json:"height"`
}

// StartExecutionRequest represents a request to start an execution
type StartExecutionRequest struct {
	ProjectID     string            `json:"project_id"`
	ExecutionType string            `json:"execution_type"` // "docker", "native", "playwright", "vhs"
	Command       string            `json:"command,omitempty"`
	Script        string            `json:"script,omitempty"`
	Environment   map[string]string `json:"environment,omitempty"`
	RecordingOpts *RecordingOptions `json:"recording_opts,omitempty"`
}

// ExecutionStatus represents the current status of an execution
type ExecutionStatus struct {
	ExecutionID   string     `json:"execution_id"`
	ProjectID     string     `json:"project_id"`
	Status        string     `json:"status"` // "pending", "running", "completed", "failed"
	ExitCode      *int       `json:"exit_code,omitempty"`
	Output        string     `json:"output,omitempty"`
	Error         string     `json:"error,omitempty"`
	StartedAt     time.Time  `json:"started_at"`
	CompletedAt   *time.Time `json:"completed_at,omitempty"`
	RecordingPath string     `json:"recording_path,omitempty"`
}

// NewExecutionClient creates a new execution client
func NewExecutionClient(pythonClient *PythonServiceClient) *ExecutionClient {
	return &ExecutionClient{
		pythonClient: pythonClient,
	}
}

// StartExecution initiates a new execution
func (executionClient *ExecutionClient) StartExecution(
	ctx context.Context,
	req StartExecutionRequest,
) (*ExecutionStatus, error) {
	var result ExecutionStatus

	err := executionClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodPost,
		"/api/v1/execution/start",
		req,
		&result,
		false, // Not cacheable - each execution is unique
		"",
		0,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to start execution: %w", err)
	}

	return &result, nil
}

// GetStatus retrieves the current status of an execution
func (executionClient *ExecutionClient) GetStatus(
	ctx context.Context,
	executionID string,
) (*ExecutionStatus, error) {
	var result ExecutionStatus

	// Cache for 5 seconds to reduce polling load
	cacheKey := GenerateCacheKey("execution:status", http.MethodGet, "/api/v1/execution/"+executionID+"/status", nil)

	err := executionClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodGet,
		"/api/v1/execution/"+executionID+"/status",
		nil,
		&result,
		true, // Cacheable
		cacheKey,
		executionStatusCacheTTL, // Short cache for polling
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get execution status: %w", err)
	}

	return &result, nil
}

// WaitForCompletion polls until execution completes or timeout
func (executionClient *ExecutionClient) WaitForCompletion(
	ctx context.Context,
	executionID string,
	timeout time.Duration,
) (*ExecutionStatus, error) {
	deadline := time.Now().Add(timeout)
	pollInterval := executionPollInterval

	for {
		if err := validateExecutionWait(ctx, deadline); err != nil {
			return nil, err
		}

		// Get current status
		status, err := executionClient.GetStatus(ctx, executionID)
		if err != nil {
			return nil, fmt.Errorf("failed to poll execution status: %w", err)
		}

		// Check if execution is complete
		if isExecutionTerminal(status.Status) {
			return status, nil
		}

		// Wait before next poll
		if err := waitForExecutionPoll(ctx, pollInterval); err != nil {
			return nil, err
		}
	}
}

func validateExecutionWait(ctx context.Context, deadline time.Time) error {
	// Check if context is cancelled or deadline exceeded.
	if ctx.Err() != nil {
		return fmt.Errorf("context cancelled: %w", ctx.Err())
	}
	if time.Now().After(deadline) {
		return errors.New("timeout waiting for execution to complete")
	}
	return nil
}

func isExecutionTerminal(status string) bool {
	return status == executionStatusComplete || status == executionStatusFailed
}

func waitForExecutionPoll(ctx context.Context, pollInterval time.Duration) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-time.After(pollInterval):
		return nil
	}
}

// CancelExecution cancels a running execution
func (executionClient *ExecutionClient) CancelExecution(
	ctx context.Context,
	executionID string,
) error {
	// Use a placeholder response struct for DELETE requests
	var result map[string]interface{}

	err := executionClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodDelete,
		"/api/v1/execution/"+executionID,
		nil,
		&result,
		false, // Not cacheable
		"",
		0,
	)
	if err != nil {
		return fmt.Errorf("failed to cancel execution: %w", err)
	}

	return nil
}

// GetOutput retrieves the full output of an execution
func (executionClient *ExecutionClient) GetOutput(
	ctx context.Context,
	executionID string,
) (string, error) {
	type OutputResponse struct {
		Output string `json:"output"`
	}

	var result OutputResponse

	// Cache output for 1 minute (output doesn't change after completion)
	cacheKey := GenerateCacheKey("execution:output", http.MethodGet, "/api/v1/execution/"+executionID+"/output", nil)

	err := executionClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodGet,
		"/api/v1/execution/"+executionID+"/output",
		nil,
		&result,
		true, // Cacheable
		cacheKey,
		executionOutputCacheTTL,
	)
	if err != nil {
		return "", fmt.Errorf("failed to get execution output: %w", err)
	}

	return result.Output, nil
}

// GetRecording retrieves the recording file for an execution
func (executionClient *ExecutionClient) GetRecording(
	ctx context.Context,
	executionID string,
) ([]byte, error) {
	type RecordingResponse struct {
		Recording []byte `json:"recording"`
	}

	var result RecordingResponse

	// Don't cache recordings (they can be large)
	err := executionClient.pythonClient.DelegateRequest(
		ctx,
		http.MethodGet,
		"/api/v1/execution/"+executionID+"/recording",
		nil,
		&result,
		false, // Not cacheable
		"",
		0,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get execution recording: %w", err)
	}

	return result.Recording, nil
}
