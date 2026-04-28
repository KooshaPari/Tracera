package handlers

import (
	"net/http"
	"time"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/agents"
)

const lockManagerTTL = 5 * time.Minute

// CoordinationHandler handles agent coordination endpoints
type CoordinationHandler struct {
	db                     *gorm.DB
	lockManager            *agents.LockManager
	conflictDetector       *agents.ConflictDetector
	teamManager            *agents.TeamManager
	distributedCoordinator *agents.DistributedCoordinator
}

// NewCoordinationHandler creates a new coordination handler
func NewCoordinationHandler(db *gorm.DB) *CoordinationHandler {
	lockManager := agents.NewLockManager(db, lockManagerTTL)
	conflictDetector := agents.NewConflictDetector(db, lockManager)
	teamManager := agents.NewTeamManager(db)
	distributedCoordinator := agents.NewDistributedCoordinator(db, lockManager, conflictDetector, teamManager)

	return &CoordinationHandler{
		db:                     db,
		lockManager:            lockManager,
		conflictDetector:       conflictDetector,
		teamManager:            teamManager,
		distributedCoordinator: distributedCoordinator,
	}
}

// AcquireLock handles lock acquisition requests
func (h *CoordinationHandler) AcquireLock(c echo.Context) error {
	var req struct {
		ItemID   string          `json:"item_id"`
		ItemType string          `json:"item_type"`
		AgentID  string          `json:"agent_id"`
		LockType agents.LockType `json:"lock_type"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	lock, err := h.lockManager.AcquireLock(c.Request().Context(), req.ItemID, req.ItemType, req.AgentID, req.LockType)
	if err != nil {
		return c.JSON(http.StatusConflict, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, lock)
}

// ReleaseLock handles lock release requests
func (h *CoordinationHandler) ReleaseLock(c echo.Context) error {
	lockID := c.Param("lock_id")
	agentID := c.QueryParam("agent_id")

	if agentID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "agent_id is required"})
	}

	if err := h.lockManager.ReleaseLock(c.Request().Context(), lockID, agentID); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Lock released successfully"})
}

// GetActiveLocks returns active locks for an agent or item
func (h *CoordinationHandler) GetActiveLocks(c echo.Context) error {
	agentID := c.QueryParam("agent_id")
	itemID := c.QueryParam("item_id")

	locks, err := h.lockManager.GetActiveLocks(c.Request().Context(), agentID, itemID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, locks)
}

// DetectConflict checks for conflicts on an item
func (handler *CoordinationHandler) DetectConflict(c echo.Context) error {
	var req struct {
		ItemID          string `json:"item_id"`
		AgentID         string `json:"agent_id"`
		ExpectedVersion int64  `json:"expected_version"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	ctx := c.Request().Context()
	conflict, err := handler.conflictDetector.DetectConflict(
		ctx,
		req.ItemID,
		req.AgentID,
		req.ExpectedVersion,
	)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	if conflict == nil {
		return c.JSON(http.StatusOK, map[string]interface{}{
			"has_conflict": false,
			"message":      "No conflict detected",
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"has_conflict": true,
		"conflict":     conflict,
	})
}

// ResolveConflict resolves a detected conflict
func (h *CoordinationHandler) ResolveConflict(c echo.Context) error {
	conflictID := c.Param("conflict_id")

	var req struct {
		ResolverAgentID string                            `json:"resolver_agent_id"`
		Strategy        agents.ConflictResolutionStrategy `json:"strategy"`
		Resolution      map[string]interface{}            `json:"resolution"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := h.conflictDetector.ResolveConflict(
		c.Request().Context(),
		conflictID,
		req.ResolverAgentID,
		req.Strategy,
		req.Resolution,
	); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Conflict resolved successfully"})
}

// GetPendingConflicts returns all pending conflicts
func (h *CoordinationHandler) GetPendingConflicts(echoCtx echo.Context) error {
	itemID := echoCtx.QueryParam("item_id")
	agentID := echoCtx.QueryParam("agent_id")

	conflicts, err := h.conflictDetector.GetPendingConflicts(echoCtx.Request().Context(), itemID, agentID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, conflicts)
}

// CreateTeam creates a new agent team
func (h *CoordinationHandler) CreateTeam(c echo.Context) error {
	var team agents.AgentTeam
	if err := c.Bind(&team); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := h.teamManager.CreateTeam(c.Request().Context(), &team); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, team)
}

// AddTeamMember adds an agent to a team
func (h *CoordinationHandler) AddTeamMember(c echo.Context) error {
	teamID := c.Param("team_id")

	var req struct {
		AgentID  string `json:"agent_id"`
		RoleName string `json:"role_name"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := h.teamManager.AddTeamMember(c.Request().Context(), teamID, req.AgentID, req.RoleName); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, map[string]string{"message": "Team member added successfully"})
}

// GetAgentPermissions returns permissions for an agent
func (h *CoordinationHandler) GetAgentPermissions(c echo.Context) error {
	agentID := c.Param("agent_id")

	permissions, priority, err := h.teamManager.GetAgentPermissions(c.Request().Context(), agentID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"agent_id":    agentID,
		"permissions": permissions,
		"priority":    priority,
	})
}

// CreateDistributedOperation creates a new distributed operation
func (h *CoordinationHandler) CreateDistributedOperation(c echo.Context) error {
	var op agents.DistributedOperation
	if err := c.Bind(&op); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if err := h.distributedCoordinator.CreateDistributedOperation(c.Request().Context(), &op); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, op)
}

// AssignOperationToAgents assigns work to agents for a distributed operation
func (h *CoordinationHandler) AssignOperationToAgents(c echo.Context) error {
	operationID := c.Param("operation_id")

	var req struct {
		Assignments map[string][]string `json:"assignments"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	ctx := c.Request().Context()
	if err := h.distributedCoordinator.AssignOperationToAgents(ctx, operationID, req.Assignments); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Operation assigned successfully"})
}

// StartParticipation marks an agent as starting work
func (h *CoordinationHandler) StartParticipation(c echo.Context) error {
	operationID := c.Param("operation_id")
	agentID := c.QueryParam("agent_id")

	if agentID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "agent_id is required"})
	}

	if err := h.distributedCoordinator.StartParticipation(c.Request().Context(), operationID, agentID); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Participation started"})
}

// CompleteParticipation marks an agent's work as complete
func (handler *CoordinationHandler) CompleteParticipation(echoCtx echo.Context) error {
	operationID := echoCtx.Param("operation_id")

	var req struct {
		AgentID string                 `json:"agent_id"`
		Result  map[string]interface{} `json:"result"`
	}

	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	ctx := echoCtx.Request().Context()
	err := handler.distributedCoordinator.CompleteParticipation(ctx, operationID, req.AgentID, req.Result)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, map[string]string{"message": "Participation completed"})
}

// GetOperationStatus returns the status of a distributed operation
func (h *CoordinationHandler) GetOperationStatus(c echo.Context) error {
	operationID := c.Param("operation_id")

	op, participants, err := h.distributedCoordinator.GetOperationStatus(c.Request().Context(), operationID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"operation":    op,
		"participants": participants,
	})
}

// CoordinatedUpdate performs a coordinated batch update
func (h *CoordinationHandler) CoordinatedUpdate(c echo.Context) error {
	var req struct {
		ProjectID     string                            `json:"project_id"`
		Updates       map[string]map[string]interface{} `json:"updates"`
		CoordinatorID string                            `json:"coordinator_id"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	ctx := c.Request().Context()
	op, err := h.distributedCoordinator.CoordinatedUpdate(ctx, req.ProjectID, req.Updates, req.CoordinatorID)
	if err != nil {
		return c.JSON(http.StatusConflict, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, op)
}

// CompleteCoordinatedUpdate completes a coordinated update
func (h *CoordinationHandler) CompleteCoordinatedUpdate(c echo.Context) error {
	operationID := c.Param("operation_id")
	coordinatorID := c.QueryParam("coordinator_id")

	if coordinatorID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "coordinator_id is required"})
	}

	ctx := c.Request().Context()
	if err := h.distributedCoordinator.CompleteCoordinatedUpdate(ctx, operationID, coordinatorID); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Coordinated update completed"})
}

// GetAgentOperations returns operations for an agent
func (h *CoordinationHandler) GetAgentOperations(c echo.Context) error {
	agentID := c.Param("agent_id")
	status := c.QueryParam("status")

	operations, err := h.distributedCoordinator.GetAgentOperations(c.Request().Context(), agentID, status)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, operations)
}

// Shutdown gracefully shuts down coordination components
func (h *CoordinationHandler) Shutdown() {
	if h.lockManager != nil {
		h.lockManager.Shutdown()
	}
}
