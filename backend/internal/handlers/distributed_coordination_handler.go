package handlers

import (
	"context"
	"log/slog"
	"net/http"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/agents"
	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/realtime"
)

// DistributedCoordinationHandler handles distributed operations across multiple agents
type DistributedCoordinationHandler struct {
	queries                *db.Queries
	distributedCoordinator *agents.DistributedCoordinator
	cache                  cache.Cache
	publisher              *nats.EventPublisher
	realtimeBroadcaster    interface{} // realtime.Broadcaster
	authProvider           interface{} // auth.Provider
	binder                 RequestBinder
}

// NewDistributedCoordinationHandler creates a new distributed coordination handler
func NewDistributedCoordinationHandler(
	pool *pgxpool.Pool,
	distributedCoordinator *agents.DistributedCoordinator,
	redisCache cache.Cache,
	eventPublisher *nats.EventPublisher,
	realtimeBroadcaster interface{},
	authProvider interface{},
	binder RequestBinder,
) *DistributedCoordinationHandler {
	return &DistributedCoordinationHandler{
		queries:                db.New(pool),
		distributedCoordinator: distributedCoordinator,
		cache:                  redisCache,
		publisher:              eventPublisher,
		realtimeBroadcaster:    realtimeBroadcaster,
		authProvider:           authProvider,
		binder:                 binder,
	}
}

// CreateDistributedOperation creates a new distributed operation
// @Summary Create a new distributed operation
// @Description Creates a new distributed operation coordinated across multiple agents
// @Tags distributed-operations
// @Accept json
// @Produce json
// @Param body body CreateDistributedOperationRequest true "Operation details"
// @Success 201 {object} CreateDistributedOperationResponse "Operation created successfully"
// @Failure 400 {object} DistributedErrorResponse "Invalid request"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations [post]
func (h *DistributedCoordinationHandler) CreateDistributedOperation(c echo.Context) error {
	var req struct {
		ProjectID      string                 `json:"project_id"`
		Type           string                 `json:"type"`
		ParticipantIDs []string               `json:"participant_i_ds"`
		CoordinatorID  string                 `json:"coordinator_id"`
		TargetItems    []string               `json:"target_items"`
		OperationData  map[string]interface{} `json:"operation_data"`
	}

	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	// Validation
	if req.ProjectID == "" || req.Type == "" || len(req.ParticipantIDs) == 0 {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id, type, and participant_i_ds are required",
		})
	}

	if h.distributedCoordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	op := &agents.DistributedOperation{
		ProjectID:      req.ProjectID,
		Type:           req.Type,
		ParticipantIDs: req.ParticipantIDs,
		CoordinatorID:  req.CoordinatorID,
		TargetItems:    req.TargetItems,
		OperationData:  req.OperationData,
		Status:         "pending",
	}

	if err := h.distributedCoordinator.CreateDistributedOperation(c.Request().Context(), op); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Publish event
	if h.publisher != nil {
		go h.publishOperationEvent(c.Request().Context(), "created", op.ID, req.ProjectID, op)
	}
	h.broadcastOperationEvent(c.Request().Context(), "created", op.ID)

	return c.JSON(http.StatusCreated, map[string]interface{}{
		"operation_id": op.ID,
		"status":       op.Status,
		"message":      "Distributed operation created",
		"time":         time.Now(),
	})
}

// AssignOperationToAgents assigns parts of an operation to multiple agents
// @Summary Assign operation to agents
// @Description Assigns parts of a distributed operation to multiple participating agents
// @Tags distributed-operations
// @Accept json
// @Produce json
// @Param body body AssignOperationToAgentsRequest true "Agent assignment configuration"
// @Success 200 {object} AssignOperationResponse "Assignment successful"
// @Failure 400 {object} DistributedErrorResponse "Invalid request"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations/assign [post]
func (h *DistributedCoordinationHandler) AssignOperationToAgents(c echo.Context) error {
	var req struct {
		OperationID      string              `json:"operation_id"`
		AgentAssignments map[string][]string `json:"agent_assignments"`
	}

	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if req.OperationID == "" || len(req.AgentAssignments) == 0 {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "operation_id and agent_assignments are required",
		})
	}

	if h.distributedCoordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	if err := h.distributedCoordinator.AssignOperationToAgents(
		c.Request().Context(),
		req.OperationID,
		req.AgentAssignments,
	); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	response := map[string]interface{}{
		"operation_id":     req.OperationID,
		"agents_assigned":  len(req.AgentAssignments),
		"status":           "success",
		"message":          "Operation assigned to agents",
		"assignment_count": req.AgentAssignments,
		"timestamp":        time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// GetOperationStatus returns the status of a distributed operation
// @Summary Get distributed operation status
// @Description Returns the current status and details of a distributed operation
// @Tags distributed-operations
// @Produce json
// @Param id path string true "Operation ID"
// @Success 200 {object} map[string]interface{} "Operation details"
// @Failure 400 {object} DistributedErrorResponse "Invalid operation ID"
// @Failure 404 {object} DistributedErrorResponse "Operation not found"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations/{id}/status [get]
func (handler *DistributedCoordinationHandler) GetOperationStatus(echoCtx echo.Context) error {
	operationID := echoCtx.Param("id")
	if operationID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "operation ID is required"})
	}

	if handler.distributedCoordinator == nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	op, err := handler.distributedCoordinator.GetDistributedOperation(
		echoCtx.Request().Context(),
		operationID,
	)
	if err != nil {
		return echoCtx.JSON(http.StatusNotFound, map[string]string{"error": "Operation not found"})
	}

	return echoCtx.JSON(http.StatusOK, op)
}

// ListOperations lists all distributed operations
// @Summary List distributed operations
// @Description Returns a list of distributed operations for a project with optional filtering
// @Tags distributed-operations
// @Produce json
// @Param project_id query string true "Project ID"
// @Param status query string false "Filter by status (pending, in_progress, completed, failed)"
// @Success 200 {object} ListDistributedOperationsResponse "List of operations"
// @Failure 400 {object} DistributedErrorResponse "Invalid project ID"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations [get]
func (h *DistributedCoordinationHandler) ListOperations(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	statusFilter := c.QueryParam("status")

	if h.distributedCoordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	operations, err := h.distributedCoordinator.ListOperations(
		c.Request().Context(),
		projectID,
		statusFilter,
	)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"operations": operations,
		"total":      len(operations),
		"project_id": projectID,
		"status":     statusFilter,
	})
}

// CompleteOperation marks a distributed operation as completed
// @Summary Complete a distributed operation
// @Description Marks a distributed operation as complete and aggregates results
// @Tags distributed-operations
// @Produce json
// @Param id path string true "Operation ID"
// @Success 200 {object} OperationStatusResponse "Operation completed successfully"
// @Failure 400 {object} ErrorResponse "Invalid operation ID"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /distributed-operations/{id}/complete [post]
func (h *DistributedCoordinationHandler) CompleteOperation(ctx echo.Context) error {
	operationID := ctx.Param("id")
	if operationID == "" {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "operation ID is required"})
	}

	if h.distributedCoordinator == nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	if err := h.distributedCoordinator.CompleteOperation(
		ctx.Request().Context(),
		operationID,
	); err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
	h.broadcastOperationEvent(ctx.Request().Context(), "completed", operationID)

	response := map[string]interface{}{
		"operation_id": operationID,
		"status":       "completed",
		"message":      "Operation completed",
		"time":         time.Now(),
	}

	return ctx.JSON(http.StatusOK, response)
}

// UpdateOperationStatus updates the status of a distributed operation
// @Summary Update operation status
// @Description Updates the status of a distributed operation (e.g., pending, in_progress, completed)
// @Tags distributed-operations
// @Accept json
// @Produce json
// @Param id path string true "Operation ID"
// @Param body body UpdateOperationStatusRequest true "New status"
// @Success 200 {object} OperationStatusResponse "Status updated successfully"
// @Failure 400 {object} DistributedErrorResponse "Invalid request"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations/{id}/status [put]
func (h *DistributedCoordinationHandler) UpdateOperationStatus(c echo.Context) error {
	operationID := c.Param("id")
	if operationID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "operation ID is required"})
	}

	var req struct {
		Status string `json:"status"`
	}

	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if req.Status == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "status is required"})
	}

	if h.distributedCoordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	if err := h.distributedCoordinator.UpdateOperationStatus(
		c.Request().Context(),
		operationID,
		req.Status,
	); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
	h.broadcastOperationEvent(c.Request().Context(), "status_updated", operationID)

	response := map[string]interface{}{
		"operation_id": operationID,
		"status":       req.Status,
		"message":      "Operation status updated",
		"time":         time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// GetParticipantStatus returns the status of a participant in a distributed operation
// @Summary Get participant status in operation
// @Description Returns the current status of a specific agent participant in a distributed operation
// @Tags distributed-operations
// @Produce json
// @Param operation_id path string true "Operation ID"
// @Param agent_id path string true "Agent ID"
// @Success 200 {object} ParticipantStatus "Participant status details"
// @Failure 400 {object} DistributedErrorResponse "Invalid operation or agent ID"
// @Failure 404 {object} DistributedErrorResponse "Participant not found"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations/{operation_id}/participants/{agent_id} [get]
func (h *DistributedCoordinationHandler) GetParticipantStatus(c echo.Context) error {
	operationID := c.Param("operation_id")
	agentID := c.Param("agent_id")

	if operationID == "" || agentID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "operation_id and agent_id are required",
		})
	}

	if h.distributedCoordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	participant, err := h.distributedCoordinator.GetParticipantStatus(
		c.Request().Context(),
		operationID,
		agentID,
	)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Participant not found"})
	}

	return c.JSON(http.StatusOK, participant)
}

// SubmitParticipantResult submits a result from a participant in a distributed operation
// @Summary Submit participant result
// @Description Submits work results from a participant agent in a distributed operation
// @Tags distributed-operations
// @Accept json
// @Produce json
// @Param body body SubmitParticipantResultRequest true "Result submission"
// @Success 200 {object} ParticipantResultResponse "Result submitted successfully"
// @Failure 400 {object} DistributedErrorResponse "Invalid request"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations/participants/result [post]
func (h *DistributedCoordinationHandler) SubmitParticipantResult(c echo.Context) error {
	var req struct {
		OperationID string                 `json:"operation_id"`
		AgentID     string                 `json:"agent_id"`
		Result      map[string]interface{} `json:"result"`
	}

	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if req.OperationID == "" || req.AgentID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "operation_id and agent_id are required",
		})
	}

	if h.distributedCoordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	if err := h.distributedCoordinator.SubmitParticipantResult(
		c.Request().Context(),
		req.OperationID,
		req.AgentID,
		req.Result,
	); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	response := map[string]interface{}{
		"operation_id": req.OperationID,
		"agent_id":     req.AgentID,
		"status":       "success",
		"message":      "Participant result submitted",
		"time":         time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// GetOperationResults returns aggregated results from a distributed operation
// @Summary Get operation results
// @Description Returns aggregated results from all participants in a distributed operation
// @Tags distributed-operations
// @Produce json
// @Param id path string true "Operation ID"
// @Success 200 {object} OperationResults "Aggregated operation results"
// @Failure 400 {object} DistributedErrorResponse "Invalid operation ID"
// @Failure 404 {object} DistributedErrorResponse "Operation not found"
// @Failure 500 {object} DistributedErrorResponse "Internal server error"
// @Router /distributed-operations/{id}/results [get]
func (h *DistributedCoordinationHandler) GetOperationResults(c echo.Context) error {
	operationID := c.Param("id")
	if operationID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "operation ID is required"})
	}

	if h.distributedCoordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "distributed coordinator not initialized",
		})
	}

	results, err := h.distributedCoordinator.GetOperationResults(
		c.Request().Context(),
		operationID,
	)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Operation not found"})
	}

	return c.JSON(http.StatusOK, results)
}

// ============================================================================
// REQUEST/RESPONSE TYPES
// ============================================================================

// CreateDistributedOperationRequest represents a request to create a distributed operation
type CreateDistributedOperationRequest struct {
	ProjectID      string                 `json:"project_id" example:"550e8400-e29b-41d4-a716-446655440000"`
	Type           string                 `json:"type" example:"bulk_analysis"`
	ParticipantIDs []string               `json:"participant_i_ds" example:"[\"agent-1\",\"agent-2\"]"`
	CoordinatorID  string                 `json:"coordinator_id" example:"coordinator-1"`
	TargetItems    []string               `json:"target_items" example:"[\"item-1\",\"item-2\"]"`
	OperationData  map[string]interface{} `json:"operation_data"`
}

// CreateDistributedOperationResponse represents the response when creating a distributed operation
type CreateDistributedOperationResponse struct {
	OperationID string    `json:"operation_id"`
	Status      string    `json:"status"`
	Message     string    `json:"message"`
	Time        time.Time `json:"time"`
}

// AssignOperationToAgentsRequest represents agent assignment configuration
type AssignOperationToAgentsRequest struct {
	OperationID      string                 `json:"operation_id" example:"op-123"`
	AgentAssignments map[string]interface{} `json:"agent_assignments"`
}

// AssignOperationResponse represents the response for agent assignment
type AssignOperationResponse struct {
	OperationID     string                 `json:"operation_id"`
	AgentsAssigned  int                    `json:"agents_assigned"`
	Status          string                 `json:"status"`
	Message         string                 `json:"message"`
	AssignmentCount map[string]interface{} `json:"assignment_count"`
	Timestamp       time.Time              `json:"timestamp"`
}

// UpdateOperationStatusRequest represents a status update request
type UpdateOperationStatusRequest struct {
	Status string `json:"status" example:"in_progress"`
}

// OperationStatusResponse represents an operation status update response
type OperationStatusResponse struct {
	OperationID string    `json:"operation_id"`
	Status      string    `json:"status"`
	Message     string    `json:"message"`
	Time        time.Time `json:"time"`
}

// ListDistributedOperationsResponse represents the response for listing operations
type ListDistributedOperationsResponse struct {
	Operations []interface{} `json:"operations"`
	Total      int           `json:"total"`
	ProjectID  string        `json:"project_id"`
	Status     string        `json:"status,omitempty"`
}

// ParticipantStatus represents the status of a participant in an operation
type ParticipantStatus struct {
	OperationID string    `json:"operation_id"`
	AgentID     string    `json:"agent_id"`
	Status      string    `json:"status"`
	Progress    float64   `json:"progress"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// SubmitParticipantResultRequest represents a participant result submission
type SubmitParticipantResultRequest struct {
	OperationID string                 `json:"operation_id" example:"op-123"`
	AgentID     string                 `json:"agent_id" example:"agent-1"`
	Result      map[string]interface{} `json:"result"`
}

// ParticipantResultResponse represents the response for result submission
type ParticipantResultResponse struct {
	OperationID string    `json:"operation_id"`
	AgentID     string    `json:"agent_id"`
	Status      string    `json:"status"`
	Message     string    `json:"message"`
	Time        time.Time `json:"time"`
}

// OperationResults represents aggregated results from a distributed operation
type OperationResults struct {
	OperationID        string                            `json:"operation_id"`
	Status             string                            `json:"status"`
	ParticipantResults map[string]map[string]interface{} `json:"participant_results"`
	AggregatedResult   map[string]interface{}            `json:"aggregated_result"`
	CompletedAt        time.Time                         `json:"completed_at,omitempty"`
}

// DistributedErrorResponse represents an error response for distributed operations
type DistributedErrorResponse struct {
	Error     string    `json:"error"`
	Code      string    `json:"code,omitempty"`
	Timestamp time.Time `json:"timestamp"`
}

// Helper function to publish operation events
func (handler *DistributedCoordinationHandler) publishOperationEvent(
	_ context.Context,
	eventType string,
	operationID string,
	projectID string,
	operation interface{},
) {
	if handler.publisher == nil {
		return
	}

	// Publish event to NATS
	eventData := map[string]interface{}{
		"event_type":   eventType,
		"operation_id": operationID,
		"operation":    operation,
		"timestamp":    time.Now(),
	}
	if err := handler.publisher.PublishProjectEvent("distributed_operation", projectID, eventData); err != nil {
		slog.Error("Failed to publish operation event", "error", err)
	}
}

// Helper function to broadcast operation events
func (h *DistributedCoordinationHandler) broadcastOperationEvent(
	ctx context.Context,
	eventType string,
	operationID string,
) {
	if h.realtimeBroadcaster == nil {
		return
	}

	broadcaster, ok := h.realtimeBroadcaster.(realtime.Broadcaster)
	if !ok {
		slog.Info("Invalid realtime broadcaster type")
		return
	}

	event := &realtime.Event{
		Type:      eventType,
		Table:     "distributed_operations",
		Schema:    "public",
		Record:    map[string]interface{}{"id": operationID},
		Timestamp: time.Now().Unix(),
	}

	if err := broadcaster.Publish(ctx, event); err != nil {
		slog.Error("Failed to broadcast operation event", "error", err)
	}
}
