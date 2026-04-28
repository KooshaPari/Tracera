package handlers

import (
	"fmt"
	"net/http"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/clients"
	"github.com/kooshapari/tracertm-backend/internal/nats"
)

// WorkflowHandler handles workflow-related HTTP requests
type WorkflowHandler struct {
	workflowClient *clients.WorkflowClient
	publisher      *nats.EventPublisher
}

// NewWorkflowHandler creates a new workflow handler
func NewWorkflowHandler(workflowClient *clients.WorkflowClient, publisher *nats.EventPublisher) *WorkflowHandler {
	return &WorkflowHandler{
		workflowClient: workflowClient,
		publisher:      publisher,
	}
}

// TriggerWorkflowRequest represents the HTTP request body
type TriggerWorkflowRequest struct {
	WorkflowName string                 `json:"workflow_name" validate:"required"`
	ProjectID    string                 `json:"project_id" validate:"required"`
	Input        map[string]interface{} `json:"input"`
}

// TriggerWorkflow triggers a new workflow
func (h *WorkflowHandler) TriggerWorkflow(c echo.Context) error {
	var req TriggerWorkflowRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	// Trigger workflow
	run, err := h.workflowClient.TriggerWorkflow(c.Request().Context(), clients.WorkflowTriggerRequest{
		WorkflowName: req.WorkflowName,
		ProjectID:    req.ProjectID,
		Input:        req.Input,
	})
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to trigger workflow: %v", err))
	}

	// Publish NATS event - workflow triggered
	if h.publisher != nil {
		eventData := map[string]interface{}{
			"run_id":        run.RunID,
			"workflow_name": req.WorkflowName,
			"status":        run.Status,
		}
		if err := h.publisher.PublishProjectEvent("workflow.triggered", run.ProjectID, eventData); err != nil {
			// Log error but don't fail the request
			c.Logger().Errorf("failed to publish workflow.triggered event: %v", err)
		}
	}

	return c.JSON(http.StatusAccepted, run)
}

// GetWorkflowRun retrieves the status of a workflow run
func (h *WorkflowHandler) GetWorkflowRun(c echo.Context) error {
	runID := c.Param("runId")
	if runID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "run_id is required")
	}

	run, err := h.workflowClient.GetWorkflowRun(c.Request().Context(), runID)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to get workflow run: %v", err))
	}

	return c.JSON(http.StatusOK, run)
}

// CancelWorkflowRun cancels a running workflow
func (h *WorkflowHandler) CancelWorkflowRun(c echo.Context) error {
	runID := c.Param("runId")
	if runID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "run_id is required")
	}

	if err := h.workflowClient.CancelWorkflowRun(c.Request().Context(), runID); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to cancel workflow run: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]string{
		"message": "workflow cancelled successfully",
	})
}

// ListWorkflowRuns lists workflow runs for a project
func (h *WorkflowHandler) ListWorkflowRuns(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "project_id is required")
	}

	limit := 50
	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if _, err := fmt.Sscanf(limitStr, "%d", &limit); err != nil {
			return echo.NewHTTPError(http.StatusBadRequest, "invalid limit parameter")
		}
	}

	runs, err := h.workflowClient.ListWorkflowRuns(c.Request().Context(), projectID, limit)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to list workflow runs: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"runs": runs,
	})
}

// RegisterWorkflowRoutes registers workflow handler routes
func RegisterWorkflowRoutes(e *echo.Group, workflowClient *clients.WorkflowClient, publisher *nats.EventPublisher) {
	handler := NewWorkflowHandler(workflowClient, publisher)

	workflow := e.Group("/workflows")
	workflow.POST("/trigger", handler.TriggerWorkflow)
	workflow.GET("/runs/:runId", handler.GetWorkflowRun)
	workflow.POST("/runs/:runId/cancel", handler.CancelWorkflowRun)
	workflow.GET("/runs", handler.ListWorkflowRuns)
}
