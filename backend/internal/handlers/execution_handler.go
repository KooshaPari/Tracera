package handlers

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/clients"
	"github.com/kooshapari/tracertm-backend/internal/nats"
)

const executionWaitTimeout = 30 * time.Minute

// ExecutionHandler handles execution-related HTTP requests
type ExecutionHandler struct {
	executionClient *clients.ExecutionClient
	publisher       *nats.EventPublisher
}

// NewExecutionHandler creates a new execution handler
func NewExecutionHandler(executionClient *clients.ExecutionClient, publisher *nats.EventPublisher) *ExecutionHandler {
	return &ExecutionHandler{
		executionClient: executionClient,
		publisher:       publisher,
	}
}

// StartExecutionRequest represents the HTTP request body
type StartExecutionRequest struct {
	ProjectID     string                    `json:"project_id" validate:"required"`
	ExecutionType string                    `json:"execution_type" validate:"required"`
	Command       string                    `json:"command,omitempty"`
	Script        string                    `json:"script,omitempty"`
	Environment   map[string]string         `json:"environment,omitempty"`
	RecordingOpts *clients.RecordingOptions `json:"recording_opts,omitempty"`
}

// RunTests starts a test execution workflow
func (h *ExecutionHandler) RunTests(c echo.Context) error {
	var req StartExecutionRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}
	if err := validateExecutionType(req.ExecutionType); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	// Start execution
	exec, err := h.executionClient.StartExecution(c.Request().Context(), clients.StartExecutionRequest{
		ProjectID:     req.ProjectID,
		ExecutionType: req.ExecutionType,
		Command:       req.Command,
		Script:        req.Script,
		Environment:   req.Environment,
		RecordingOpts: req.RecordingOpts,
	})
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to start execution: %v", err))
	}

	// Publish NATS event - execution started
	if h.publisher != nil {
		eventData := map[string]interface{}{
			"execution_id": exec.ExecutionID,
			"status":       exec.Status,
		}
		if err := h.publisher.PublishProjectEvent("execution.started", exec.ProjectID, eventData); err != nil {
			// Log error but don't fail the request
			c.Logger().Errorf("failed to publish execution.started event: %v", err)
		}
	}

	// Wait for completion in background
	go h.waitForExecutionCompletion(exec.ExecutionID, exec.ProjectID)

	return c.JSON(http.StatusAccepted, map[string]interface{}{
		"execution_id": exec.ExecutionID,
		"status":       exec.Status,
		"message":      "execution started successfully",
	})
}

// waitForExecutionCompletion waits for execution to complete and publishes event
func (h *ExecutionHandler) waitForExecutionCompletion(executionID, projectID string) {
	ctx, cancel := context.WithTimeout(context.Background(), executionWaitTimeout)
	defer cancel()

	_, waitErr := h.executionClient.WaitForCompletion(ctx, executionID, executionWaitTimeout)
	if waitErr != nil {
		// Log error
		slog.Error("execution failed or timed out", "id", executionID, "error", waitErr)
		return
	}

	// Publish completion event
	if h.publisher != nil {
		eventData := map[string]interface{}{
			"execution_id": executionID,
			"status":       "completed",
		}
		if err := h.publisher.PublishProjectEvent("execution.completed", projectID, eventData); err != nil {
			slog.Error("failed to publish execution.completed event", "error", err)
		}
	}
}

// GetExecutionStatus retrieves the status of an execution
func (handler *ExecutionHandler) GetExecutionStatus(c echo.Context) error {
	executionID := c.Param("executionId")
	if executionID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "execution_id is required")
	}

	status, err := handler.executionClient.GetStatus(c.Request().Context(), executionID)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to get execution status: %v", err))
	}

	return c.JSON(http.StatusOK, status)
}

func validateExecutionType(executionType string) error {
	switch executionType {
	case "docker", "native", "playwright", "vhs":
		return nil
	default:
		return errors.New("execution_type must be one of docker, native, playwright, vhs")
	}
}

// CancelExecution cancels a running execution
func (h *ExecutionHandler) CancelExecution(echoCtx echo.Context) error {
	executionID := echoCtx.Param("executionId")
	if executionID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "execution_id is required")
	}

	if err := h.executionClient.CancelExecution(echoCtx.Request().Context(), executionID); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to cancel execution: %v", err))
	}

	return echoCtx.JSON(http.StatusOK, map[string]string{
		"message": "execution cancelled successfully",
	})
}

// GetExecutionOutput retrieves the output of an execution
func (h *ExecutionHandler) GetExecutionOutput(c echo.Context) error {
	executionID := c.Param("executionId")
	if executionID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "execution_id is required")
	}

	output, err := h.executionClient.GetOutput(c.Request().Context(), executionID)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to get execution output: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]string{
		"output": output,
	})
}

// GetExecutionRecording retrieves the recording of an execution
func (h *ExecutionHandler) GetExecutionRecording(c echo.Context) error {
	executionID := c.Param("executionId")
	if executionID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "execution_id is required")
	}

	recording, err := h.executionClient.GetRecording(c.Request().Context(), executionID)
	if err != nil {
		errMsg := fmt.Sprintf("failed to get execution recording: %v", err)
		return echo.NewHTTPError(http.StatusInternalServerError, errMsg)
	}

	// Return the recording as a binary response
	return c.Blob(http.StatusOK, "application/octet-stream", recording)
}

// RegisterExecutionRoutes registers execution handler routes
func RegisterExecutionRoutes(e *echo.Group, executionClient *clients.ExecutionClient, publisher *nats.EventPublisher) {
	handler := NewExecutionHandler(executionClient, publisher)

	execution := e.Group("/execution")
	execution.POST("/run-tests", handler.RunTests)
	execution.GET("/:executionId/status", handler.GetExecutionStatus)
	execution.POST("/:executionId/cancel", handler.CancelExecution)
	execution.GET("/:executionId/output", handler.GetExecutionOutput)
	execution.GET("/:executionId/recording", handler.GetExecutionRecording)
}
