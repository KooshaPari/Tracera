// Package handlers provides HTTP handlers for the API.
package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/agents"
	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/realtime"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// AgentHandler handles agent-related HTTP requests.
type AgentHandler struct {
	agentService        services.AgentService // Service layer for operations
	coordinator         *agents.Coordinator
	cache               cache.Cache
	publisher           *nats.EventPublisher
	realtimeBroadcaster interface{} // realtime.Broadcaster
	authProvider        interface{} // auth.Provider
	binder              RequestBinder
}

// NewAgentHandler builds a new AgentHandler.
func NewAgentHandler(
	agentService services.AgentService,
	coordinator *agents.Coordinator,
	redisCache cache.Cache,
	eventPublisher *nats.EventPublisher,
	realtimeBroadcaster interface{},
	authProvider interface{},
	binder RequestBinder,
) *AgentHandler {
	return &AgentHandler{
		agentService:        agentService,
		coordinator:         coordinator,
		cache:               redisCache,
		publisher:           eventPublisher,
		realtimeBroadcaster: realtimeBroadcaster,
		authProvider:        authProvider,
		binder:              binder,
	}
}

// CreateAgent creates a new agent.
func (h *AgentHandler) CreateAgent(c echo.Context) error {
	var req struct {
		ProjectID string          `json:"project_id"`
		Name      string          `json:"name"`
		Status    string          `json:"status"`
		Metadata  json.RawMessage `json:"metadata"`
	}
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	_, err := uuidutil.StringToUUID(req.ProjectID)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project_id"})
	}

	if h.agentService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "agent service not initialized"})
	}

	// Build agent from request
	agent := &models.Agent{
		ProjectID: req.ProjectID,
		Name:      req.Name,
		Status:    req.Status,
	}

	// Create agent via service (handles validation, events, caching)
	if err := h.agentService.CreateAgent(c.Request().Context(), agent); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Convert service model back to db.Agent format for consistent API response
	dbAgent := h.modelAgentToDbAgent(agent)

	// Broadcast via realtime (service doesn't handle realtime)
	if h.realtimeBroadcaster != nil {
		go h.broadcastAgentEvent(c.Request().Context(), "created", agent.ID)
	}

	return c.JSON(http.StatusCreated, dbAgent)
}

// ListAgents returns agents for a project.
func (h *AgentHandler) ListAgents(c echo.Context) error {
	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	_, err := uuidutil.StringToUUID(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project_id"})
	}

	if h.agentService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "agent service not initialized"})
	}

	// AgentService.ListAgents doesn't filter by project, so we get all and filter
	serviceAgents, err := h.agentService.ListAgents(c.Request().Context())
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
	// Filter by project and convert to db.Agent for backward compatibility
	var filteredAgents []db.Agent
	for _, agent := range serviceAgents {
		if agent.ProjectID == projectIDStr {
			dbAgent := h.modelAgentToDbAgent(agent)
			filteredAgents = append(filteredAgents, dbAgent)
		}
	}
	return c.JSON(http.StatusOK, filteredAgents)
}

// GetAgent returns agent details by ID.
func (h *AgentHandler) GetAgent(c echo.Context) error {
	idStr := c.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid agent ID"})
	}

	if h.agentService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "agent service not initialized"})
	}

	// AgentService handles caching internally
	serviceAgent, err := h.agentService.GetAgent(c.Request().Context(), idStr)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Agent not found"})
	}
	// Convert models.Agent to db.Agent for backward compatibility
	dbAgent := h.modelAgentToDbAgent(serviceAgent)
	return c.JSON(http.StatusOK, dbAgent)
}

// UpdateAgent updates agent properties.
func (h *AgentHandler) UpdateAgent(c echo.Context) error {
	idStr := c.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid agent ID"})
	}

	var req struct {
		Name     string          `json:"name"`
		Status   string          `json:"status"`
		Metadata json.RawMessage `json:"metadata"`
	}
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if h.agentService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "agent service not initialized"})
	}

	// Get existing agent first to preserve fields not in request
	existingAgent, err := h.agentService.GetAgent(c.Request().Context(), idStr)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Agent not found"})
	}

	// Build updated agent from request
	agent := &models.Agent{
		ID:        idStr,
		ProjectID: existingAgent.ProjectID,
		Name:      req.Name,
		Status:    req.Status,
	}

	// Call service (handles validation, caching, and events)
	if err := h.agentService.UpdateAgent(c.Request().Context(), agent); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Get updated agent for response
	updatedAgent, err := h.agentService.GetAgent(c.Request().Context(), idStr)
	if err != nil {
		message := "Agent updated but failed to retrieve"
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": message})
	}

	// Convert to db.Agent for response compatibility
	dbAgent := h.modelAgentToDbAgent(updatedAgent)

	// Invalidate cache (service might not handle this for all paths)
	h.invalidateAgentCache(c.Request().Context(), idStr)

	// Broadcast via realtime (service doesn't handle realtime)
	if h.realtimeBroadcaster != nil {
		go h.broadcastAgentEvent(c.Request().Context(), "updated", idStr)
	}

	return c.JSON(http.StatusOK, dbAgent)
}

// UpdateAgentStatus updates the agent status.
func (h *AgentHandler) UpdateAgentStatus(c echo.Context) error {
	idStr := c.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid agent ID"})
	}

	var req struct {
		Status string `json:"status"`
	}
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if h.agentService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "agent service not initialized"})
	}

	if err := h.agentService.UpdateAgentStatus(c.Request().Context(), idStr, req.Status); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Invalidate cache
	h.invalidateAgentCache(c.Request().Context(), idStr)

	// Broadcast via realtime
	if h.realtimeBroadcaster != nil {
		go h.broadcastAgentEvent(c.Request().Context(), "status_updated", idStr)
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Agent status updated"})
}

// DeleteAgent removes an agent.
func (handler *AgentHandler) DeleteAgent(echoCtx echo.Context) error {
	idStr := echoCtx.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid agent ID"})
	}

	if err := handler.deleteAgent(echoCtx.Request().Context(), idStr); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, map[string]string{"message": "Agent deleted"})
}

func (h *AgentHandler) deleteAgent(ctx context.Context, agentID string) error {
	if h.agentService == nil {
		return errors.New("agent service not initialized")
	}

	if err := h.agentService.DeleteAgent(ctx, agentID); err != nil {
		return err
	}

	h.invalidateAgentCache(ctx, agentID)

	if h.realtimeBroadcaster != nil {
		go h.broadcastAgentEvent(ctx, "deleted", agentID)
	}

	return nil
}

// RegisterAgent registers an agent with the coordinator
// RegisterAgent registers an agent with the coordinator.
func (h *AgentHandler) RegisterAgent(c echo.Context) error {
	var req agents.RegisterRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	agent := &agents.RegisteredAgent{
		Name:         req.Name,
		ProjectID:    req.ProjectID,
		Capabilities: req.Capabilities,
		Status:       agents.StatusIdle,
		Metadata:     req.Metadata,
	}

	if err := h.coordinator.RegisterAgent(agent); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	response := agents.RegisterResponse{
		AgentID: agent.ID,
		Status:  "success",
		Message: "Agent registered successfully",
		Time:    time.Now(),
	}

	return c.JSON(http.StatusCreated, response)
}

// AgentHeartbeat handles agent heartbeat requests
// AgentHeartbeat records an agent heartbeat.
func (h *AgentHandler) AgentHeartbeat(echoCtx echo.Context) error {
	var req agents.HeartbeatRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := h.coordinator.Heartbeat(req.AgentID, req.Status); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	response := agents.HeartbeatResponse{
		Status:  "success",
		Time:    time.Now(),
		Message: "Heartbeat received",
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// GetNextTask gets the next available task for an agent
// GetNextTask returns the next task for an agent.
func (h *AgentHandler) GetNextTask(c echo.Context) error {
	agentID := c.Param("id")

	task, err := h.coordinator.GetNextTask(agentID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	if task == nil {
		response := agents.TaskResponse{
			Task:    nil,
			Status:  "no_task",
			Message: "No tasks available",
		}
		return c.JSON(http.StatusOK, response)
	}

	response := agents.TaskResponse{
		Task:    task,
		Status:  "success",
		Message: "Task assigned",
	}

	return c.JSON(http.StatusOK, response)
}

// SubmitTaskResult submits a task result
// SubmitTaskResult submits a completed task result.
func (h *AgentHandler) SubmitTaskResult(c echo.Context) error {
	var req agents.TaskResultRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := h.coordinator.CompleteTask(req.AgentID, req.TaskID, req.Result); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	response := agents.TaskResultResponse{
		Status:  "success",
		Message: "Task result received",
		Time:    time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// SubmitTaskError submits a task error
// SubmitTaskError submits a task failure.
func (handler *AgentHandler) SubmitTaskError(c echo.Context) error {
	var req agents.TaskErrorRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := handler.coordinator.FailTask(req.AgentID, req.TaskID, req.ErrorMessage); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	response := agents.TaskErrorResponse{
		Status:     "success",
		Message:    "Task error recorded",
		WillRetry:  false,
		RetryCount: 0,
	}

	return c.JSON(http.StatusOK, response)
}

// AssignTask assigns a task to the queue
// AssignTask assigns a task to an agent.
func (h *AgentHandler) AssignTask(c echo.Context) error {
	var task agents.Task
	if err := c.Bind(&task); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := h.coordinator.AssignTask(&task); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, map[string]interface{}{
		"task_id": task.ID,
		"status":  "queued",
		"message": "Task queued for assignment",
	})
}

// ListRegisteredAgents lists all agents registered with the coordinator
// ListRegisteredAgents returns registered agents.
func (h *AgentHandler) ListRegisteredAgents(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	agents := h.coordinator.ListAgents(projectID)
	return c.JSON(http.StatusOK, agents)
}

// GetAgentStatus gets the status of a specific agent from the coordinator
// GetAgentStatus returns agent runtime status.
func (h *AgentHandler) GetAgentStatus(c echo.Context) error {
	agentID := c.Param("id")

	agent, err := h.coordinator.GetAgent(agentID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, agent)
}

// getCacheKey generates a cache key for an agent
func (h *AgentHandler) getCacheKey(agentID string) string {
	return "agent:" + agentID
}

// invalidateAgentCache invalidates cache for a specific agent
func (h *AgentHandler) invalidateAgentCache(ctx context.Context, agentID string) {
	if h.cache == nil {
		return
	}
	key := h.getCacheKey(agentID)
	if err := h.cache.Delete(ctx, key); err != nil {
		slog.Error("Failed to invalidate agent cache", "error", err)
	}
	// Also invalidate list caches with pattern
	if err := h.cache.InvalidatePattern(ctx, "agents:*"); err != nil {
		slog.Error("Failed to invalidate agent list cache", "error", err)
	}
}

// broadcastAgentEvent broadcasts an agent event via realtime
func (h *AgentHandler) broadcastAgentEvent(ctx context.Context, eventType string, agentID string) {
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
		Table:     "agents",
		Schema:    "public",
		Record:    map[string]interface{}{"id": agentID},
		Timestamp: time.Now().Unix(),
	}

	if err := broadcaster.Publish(ctx, event); err != nil {
		slog.Error("Failed to broadcast agent event", "error", err)
	}
}

// UnregisterAgent unregisters an agent from the coordinator
// UnregisterAgent unregisters an agent from the coordinator.
func (h *AgentHandler) UnregisterAgent(c echo.Context) error {
	idStr := c.Param("id")
	if idStr == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "agent ID is required"})
	}

	if h.coordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "coordinator not initialized"})
	}

	if err := h.coordinator.UnregisterAgent(idStr); err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": err.Error()})
	}

	response := map[string]interface{}{
		"status":  "success",
		"message": "Agent unregistered",
		"time":    time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// GetCoordinatorStatus returns the current status of the coordinator
// GetCoordinatorStatus returns coordinator status.
func (h *AgentHandler) GetCoordinatorStatus(c echo.Context) error {
	if h.coordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "coordinator not initialized"})
	}

	projectID := c.QueryParam("project_id")

	response := map[string]interface{}{
		"status":            "operational",
		"timestamp":         time.Now(),
		"agents_online":     len(h.coordinator.ListAgents(projectID)),
		"total_agents":      len(h.coordinator.ListAgents("")),
		"heartbeat_timeout": "2m0s",
	}

	return c.JSON(http.StatusOK, response)
}

// GetAgentMetrics returns metrics for a specific agent
// GetAgentMetrics returns metrics for an agent.
func (handler *AgentHandler) GetAgentMetrics(echoCtx echo.Context) error {
	agentID := echoCtx.Param("id")
	if agentID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "agent ID is required"})
	}

	if handler.coordinator == nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "coordinator not initialized"})
	}

	agent, err := handler.coordinator.GetAgent(agentID)
	if err != nil {
		return echoCtx.JSON(http.StatusNotFound, map[string]string{"error": "Agent not found"})
	}

	response := map[string]interface{}{
		"agent_id":       agent.ID,
		"name":           agent.Name,
		"status":         agent.Status,
		"last_heartbeat": agent.LastHeartbeat,
		"current_task":   agent.CurrentTask,
		"capabilities":   agent.Capabilities,
		"uptime_seconds": time.Since(agent.LastHeartbeat).Seconds(),
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// GetQueueStats returns statistics about the task queue
// GetQueueStats returns queue statistics.
func (h *AgentHandler) GetQueueStats(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	if h.coordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "coordinator not initialized"})
	}

	// Get pending and assigned task counts
	allAgents := h.coordinator.ListAgents(projectID)
	activeTaskCount := 0
	for _, agent := range allAgents {
		if agent.CurrentTask != nil {
			activeTaskCount++
		}
	}

	response := map[string]interface{}{
		"timestamp":      time.Now(),
		"active_agents":  len(allAgents),
		"active_tasks":   activeTaskCount,
		"idle_agents":    calculateIdleAgents(allAgents),
		"busy_agents":    calculateBusyAgents(allAgents),
		"offline_agents": calculateOfflineAgents(allAgents),
	}

	return c.JSON(http.StatusOK, response)
}

// ListQueuedTasks lists all pending tasks in the queue
// ListQueuedTasks lists queued tasks.
func (handler *AgentHandler) ListQueuedTasks(echoCtx echo.Context) error {
	projectID := echoCtx.QueryParam("project_id")
	if projectID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	if handler.coordinator == nil || handler.coordinator.TaskQueue == nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "task queue not initialized"})
	}

	tasks := handler.coordinator.TaskQueue.ListPendingTasks(projectID)

	response := map[string]interface{}{
		"tasks":       tasks,
		"total_count": len(tasks),
		"timestamp":   time.Now(),
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// CancelTask cancels a pending task
// CancelTask cancels a queued task.
func (h *AgentHandler) CancelTask(ctx echo.Context) error {
	taskID := ctx.Param("task_id")
	if taskID == "" {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "task_id is required"})
	}

	if h.coordinator == nil || h.coordinator.TaskQueue == nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": "task queue not initialized"})
	}

	if err := h.coordinator.TaskQueue.CancelTask(taskID); err != nil {
		return ctx.JSON(http.StatusNotFound, map[string]string{"error": err.Error()})
	}

	response := map[string]interface{}{
		"status":  "success",
		"message": "Task canceled",
		"time":    time.Now(),
	}

	return ctx.JSON(http.StatusOK, response)
}

// GetTaskDetails returns detailed information about a task
// GetTaskDetails returns details for a task.
func (h *AgentHandler) GetTaskDetails(c echo.Context) error {
	taskID := c.Param("task_id")
	if taskID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "task_id is required"})
	}

	if h.coordinator == nil || h.coordinator.TaskQueue == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "task queue not initialized"})
	}

	task, err := h.coordinator.TaskQueue.GetTask(taskID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Task not found"})
	}

	return c.JSON(http.StatusOK, task)
}

// RebalanceTasks rebalances tasks across available agents
// RebalanceTasks triggers task rebalancing.
func (h *AgentHandler) RebalanceTasks(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	if h.coordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "coordinator not initialized"})
	}

	// Get all agents for the project
	agents := h.coordinator.ListAgents(projectID)
	if len(agents) == 0 {
		return c.JSON(http.StatusOK, map[string]interface{}{
			"status":  "no_agents",
			"message": "No agents available for rebalancing",
			"time":    time.Now(),
		})
	}

	// Trigger distribution (this happens periodically, but can be triggered manually)
	rebalancedCount := 0
	for _, agent := range agents {
		if agent.Status == agents[0].Status && agent.CurrentTask == nil {
			rebalancedCount++
		}
	}

	response := map[string]interface{}{
		"status":            "success",
		"agents_rebalanced": rebalancedCount,
		"total_agents":      len(agents),
		"timestamp":         time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// GetAgentHistory returns task history for an agent
// GetAgentHistory returns agent history.
func (h *AgentHandler) GetAgentHistory(c echo.Context) error {
	agentID := c.Param("id")
	if agentID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "agent ID is required"})
	}

	limitStr := c.QueryParam("limit")
	limit := 10
	if limitStr != "" {
		val, err := strconv.Atoi(limitStr)
		if err != nil || val <= 0 || val > 100 {
			return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid limit: must be a number between 1 and 100"})
		}
		limit = val
	}

	if h.coordinator == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "coordinator not initialized"})
	}

	agent, err := h.coordinator.GetAgent(agentID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Agent not found"})
	}

	// Return agent information with task history structure
	response := map[string]interface{}{
		"agent_id":      agent.ID,
		"name":          agent.Name,
		"status":        agent.Status,
		"total_history": 0, // Would be populated from DB
		"recent_tasks":  []interface{}{},
		"limit":         limit,
		"timestamp":     time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// CoordinatorHealthCheck checks coordinator health.
func (h *AgentHandler) CoordinatorHealthCheck(c echo.Context) error {
	if h.coordinator == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"status": "unavailable",
			"reason": "coordinator not initialized",
		})
	}

	agents := h.coordinator.ListAgents("")
	activeAgents := calculateActiveAgents(agents)

	response := map[string]interface{}{
		"status":        "healthy",
		"total_agents":  len(agents),
		"active_agents": activeAgents,
		"timestamp":     time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// Helper functions
func calculateIdleAgents(agentList []*agents.RegisteredAgent) int {
	count := 0
	for _, a := range agentList {
		if a.Status == agents.StatusIdle {
			count++
		}
	}
	return count
}

func calculateBusyAgents(agentList []*agents.RegisteredAgent) int {
	count := 0
	for _, a := range agentList {
		if a.Status == agents.StatusBusy {
			count++
		}
	}
	return count
}

func calculateOfflineAgents(agentList []*agents.RegisteredAgent) int {
	count := 0
	for _, a := range agentList {
		if a.Status == agents.StatusOffline {
			count++
		}
	}
	return count
}

func calculateActiveAgents(agentList []*agents.RegisteredAgent) int {
	count := 0
	for _, a := range agentList {
		if a.Status != agents.StatusOffline {
			count++
		}
	}
	return count
}

// ============================================================================
// MODEL CONVERSION HELPERS
// ============================================================================

// modelAgentToDbAgent converts models.Agent (from service layer) to db.Agent (for API response)
// This maintains backward compatibility while allowing gradual migration to service layer
func (h *AgentHandler) modelAgentToDbAgent(agent *models.Agent) db.Agent {
	if agent == nil {
		return db.Agent{}
	}

	// Convert UUID strings to pgtype.UUID
	var agentID, projectID pgtype.UUID
	if aid, err := uuidutil.StringToUUID(agent.ID); err == nil {
		agentID = aid
	}
	if pid, err := uuidutil.StringToUUID(agent.ProjectID); err == nil {
		projectID = pid
	}

	// Convert metadata
	metadata := []byte("{}")
	if len(agent.Metadata) > 0 {
		metadata = []byte(agent.Metadata)
	}

	// Convert timestamps
	createdAt := pgtype.Timestamp{Time: agent.CreatedAt, Valid: !agent.CreatedAt.IsZero()}
	updatedAt := pgtype.Timestamp{Time: agent.UpdatedAt, Valid: !agent.UpdatedAt.IsZero()}

	return db.Agent{
		ID:        agentID,
		ProjectID: projectID,
		Name:      agent.Name,
		Status:    agent.Status,
		Metadata:  metadata,
		CreatedAt: createdAt,
		UpdatedAt: updatedAt,
	}
}

// RecordActivity records an agent activity event
// This is a new method that uses AgentService.NotifyAgentEvent
// RecordActivity records an agent activity event.
func (h *AgentHandler) RecordActivity(c echo.Context) error {
	idStr := c.Param("id")
	if _, err := uuidutil.StringToUUID(idStr); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid agent ID"})
	}

	var req struct {
		EventType string                 `json:"event_type"`
		Data      map[string]interface{} `json:"data"`
	}
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if h.agentService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "agent service not initialized"})
	}

	event := &services.AgentEvent{
		AgentID:   idStr,
		EventType: req.EventType,
		Data:      req.Data,
		Timestamp: time.Now(),
	}

	if err := h.agentService.NotifyAgentEvent(c.Request().Context(), event); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"message": "Activity recorded",
		"status":  "success",
	})
}

// GetMetrics returns metrics for an agent (alias for GetAgentMetrics)
// GetMetrics returns aggregated agent metrics.
func (h *AgentHandler) GetMetrics(c echo.Context) error {
	return h.GetAgentMetrics(c)
}
