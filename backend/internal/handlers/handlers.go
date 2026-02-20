package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/labstack/echo/v4"
	"gorm.io/datatypes"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/realtime"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// ErrorResponse represents an error response
// @Description Error response with error message
type ErrorResponse struct {
	Error string `json:"error"`
}

// HealthResponse represents a health check response
// @Description Health check response with service status
type HealthResponse struct {
	Status  string `json:"status" example:"ok"`
	Service string `json:"service" example:"tracertm-backend"`
}

// HealthCheck godoc
// @Summary Health check endpoint
// @Description Returns the health status of the service
// @Tags health
// @Accept json
// @Produce json
// @Success 200 {object} HealthResponse "Service is healthy"
// @Router /health [get]
func HealthCheck(c echo.Context) error {
	return c.JSON(http.StatusOK, HealthResponse{
		Status:  "ok",
		Service: "tracertm-backend",
	})
}

// AuthMe godoc
// @Summary Get current user information
// @Description Returns information about the currently authenticated user
// @Tags auth
// @Accept json
// @Produce json
// @Success 200 {object} auth.User "Current user information"
// @Failure 401 {object} ErrorResponse "Unauthenticated"
// @Security ApiKeyAuth
// @Router /auth/me [get]
func AuthMe(c echo.Context) error {
	user, ok := c.Get("user").(*auth.User)
	if !ok || user == nil {
		return c.JSON(http.StatusUnauthorized, ErrorResponse{Error: "unauthenticated"})
	}
	return c.JSON(http.StatusOK, user)
}

// CSRFTokenResponse represents a CSRF token response
// @Description CSRF token response
type CSRFTokenResponse struct {
	Token string `json:"token" example:"base64-encoded-token"`
	Valid bool   `json:"valid" example:"true"`
}

// CSRFTokenContextKey is the context key for CSRF token (defined in middleware)
const CSRFTokenContextKey = "csrf_token"

// GetCSRFToken godoc
// @Summary Get CSRF token
// @Description Returns a CSRF token for use in state-changing requests
// @Tags security
// @Accept json
// @Produce json
// @Success 200 {object} CSRFTokenResponse "CSRF token retrieved successfully"
// @Failure 500 {object} ErrorResponse "Failed to generate CSRF token"
// @Router /api/v1/csrf-token [get]
func GetCSRFToken(c echo.Context) error {
	// Get token from context (should have been set by middleware)
	token, ok := c.Get(CSRFTokenContextKey).(string)
	if !ok || token == "" {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "failed to generate CSRF token",
		})
	}

	return c.JSON(http.StatusOK, CSRFTokenResponse{
		Token: token,
		Valid: true,
	})
}

// ProjectHandler handles project operations
type ProjectHandler struct {
	projectService      services.ProjectService // Service layer for operations
	cache               cache.Cache
	publisher           *nats.EventPublisher
	realtimeBroadcaster interface{} // realtime.Broadcaster
	authProvider        interface{} // auth.Provider
	binder              RequestBinder
}

// NewProjectHandler creates a new project handler with required dependencies
func NewProjectHandler(
	redisCache cache.Cache,
	eventPublisher *nats.EventPublisher,
	realtimeBroadcaster interface{},
	authProvider interface{},
	binder RequestBinder,
	projectService services.ProjectService,
) *ProjectHandler {
	return &ProjectHandler{
		projectService:      projectService,
		cache:               redisCache,
		publisher:           eventPublisher,
		realtimeBroadcaster: realtimeBroadcaster,
		authProvider:        authProvider,
		binder:              binder,
	}
}

// CreateProject creates a new project
func (handler *ProjectHandler) CreateProject(c echo.Context) error {
	var req struct {
		Name        string          `json:"name"`
		Description string          `json:"description"`
		Metadata    json.RawMessage `json:"metadata"`
	}
	if err := handler.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if handler.projectService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "project service not initialized"})
	}

	// Validate name is not empty
	if req.Name == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project name is required"})
	}

	// Use ProjectService for creation (service layer path)
	// Convert request to service model
	metadata := datatypes.JSON([]byte("{}"))
	if req.Metadata != nil {
		metadata = datatypes.JSON(req.Metadata)
	}

	project := &models.Project{
		Name:        req.Name,
		Description: req.Description,
		Metadata:    metadata,
	}

	// Create project via service (handles validation, events, caching)
	if err := handler.projectService.CreateProject(c.Request().Context(), project); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
	handler.invalidateProjectCache(c.Request().Context(), project.ID)

	// Convert service model back to db.Project format for consistent API response
	dbProject := handler.modelProjectToDBProject(project)
	return c.JSON(http.StatusCreated, dbProject)
}

// ListProjects returns a list of projects with pagination
func (h *ProjectHandler) ListProjects(c echo.Context) error {
	limit, offset := parseProjectListPagination(c)
	if err := ensureProjectServiceInitialized(h.projectService); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	serviceProjects, err := h.projectService.ListProjects(c.Request().Context())
	if err != nil {
		return handleProjectListError(c, err)
	}

	paginatedProjects := paginateProjects(serviceProjects, limit, offset)

	// Convert models.Project to db.Project for backward compatibility
	dbProjects := make([]db.Project, len(paginatedProjects))
	for i, project := range paginatedProjects {
		dbProjects[i] = h.modelProjectToDBProject(project)
	}
	return c.JSON(http.StatusOK, dbProjects)
}

func parseProjectListPagination(c echo.Context) (int, int) {
	const defaultLimit = 100
	limit := parseProjectListParam(c.QueryParam("limit"), defaultLimit)
	offset := parseProjectListParam(c.QueryParam("offset"), 0)
	return limit, offset
}

func parseProjectListParam(value string, fallback int) int {
	if value == "" {
		return fallback
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return fallback
	}
	return parsed
}

func ensureProjectServiceInitialized(service services.ProjectService) error {
	if service == nil {
		return errors.New("project service not initialized")
	}
	return nil
}

func handleProjectListError(c echo.Context, err error) error {
	if errors.Is(err, context.Canceled) {
		return nil
	}
	return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
}

func paginateProjects(projects []*models.Project, limit int, offset int) []*models.Project {
	start := offset
	end := offset + limit
	if start > len(projects) {
		start = len(projects)
	}
	if end > len(projects) {
		end = len(projects)
	}
	return projects[start:end]
}

// GetProject returns a single project by ID
func (h *ProjectHandler) GetProject(c echo.Context) error {
	idStr := c.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project ID"})
	}

	if h.projectService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "project service not initialized"})
	}

	// ProjectService handles caching internally
	serviceProject, err := h.projectService.GetProject(c.Request().Context(), idStr)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Project not found"})
	}
	// Convert models.Project to db.Project for backward compatibility
	dbProject := h.modelProjectToDBProject(serviceProject)
	return c.JSON(http.StatusOK, dbProject)
}

// UpdateProject updates an existing project
func (handler *ProjectHandler) UpdateProject(echoCtx echo.Context) error {
	idStr := echoCtx.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project ID"})
	}

	var req struct {
		Name        string          `json:"name"`
		Description string          `json:"description"`
		Metadata    json.RawMessage `json:"metadata"`
	}
	if err := handler.binder.Bind(echoCtx, &req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	if handler.projectService == nil {
		errMsg := "project service not initialized"
		errorResponse := map[string]string{"error": errMsg}
		return echoCtx.JSON(http.StatusInternalServerError, errorResponse)
	}

	// Build updated project from request
	metadata := datatypes.JSON([]byte("{}"))
	if req.Metadata != nil {
		metadata = datatypes.JSON(req.Metadata)
	}

	project := &models.Project{
		ID:          idStr,
		Name:        req.Name,
		Description: req.Description,
		Metadata:    metadata,
	}

	// Call service (handles validation, caching, and events)
	if err := handler.projectService.UpdateProject(echoCtx.Request().Context(), project); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
	handler.invalidateProjectCache(echoCtx.Request().Context(), idStr)

	// Get updated project for response
	updatedProject, err := handler.projectService.GetProject(echoCtx.Request().Context(), idStr)
	if err != nil {
		errMsg := "Project updated but failed to retrieve"
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": errMsg})
	}

	// Convert to db.Project for response compatibility
	dbProject := handler.modelProjectToDBProject(updatedProject)

	// Broadcast via realtime (service doesn't handle realtime)
	if handler.realtimeBroadcaster != nil {
		go handler.broadcastProjectEvent(echoCtx.Request().Context(), "updated", idStr)
	}

	return echoCtx.JSON(http.StatusOK, dbProject)
}

// DeleteProject deletes a project by ID
func (h *ProjectHandler) DeleteProject(c echo.Context) error {
	idStr := c.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project ID"})
	}

	if h.projectService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "project service not initialized"})
	}

	// Call service (handles validation, caching, and events)
	if err := h.projectService.DeleteProject(c.Request().Context(), idStr); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
	h.invalidateProjectCache(c.Request().Context(), idStr)

	// Broadcast via realtime (service doesn't handle realtime)
	if h.realtimeBroadcaster != nil {
		go h.broadcastProjectEvent(c.Request().Context(), "deleted", idStr)
	}

	return c.NoContent(http.StatusNoContent)
}

// broadcastProjectEvent broadcasts a project event via realtime
func (h *ProjectHandler) broadcastProjectEvent(ctx context.Context, eventType string, projectID string) {
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
		Table:     "projects",
		Schema:    "public",
		Record:    map[string]interface{}{"id": projectID},
		Timestamp: time.Now().Unix(),
	}

	if err := broadcaster.Publish(ctx, event); err != nil {
		slog.Error("Failed to broadcast project event", "error", err)
	}
}

// ============================================================================
// MODEL CONVERSION HELPERS
// ============================================================================

// modelProjectToDBProject converts models.Project (from service layer) to db.Project (for API response)
// This maintains backward compatibility while allowing gradual migration to service layer
func (h *ProjectHandler) modelProjectToDBProject(project *models.Project) db.Project {
	if project == nil {
		return db.Project{}
	}

	// Convert UUID string to pgtype.UUID
	var projectID pgtype.UUID
	projectUUID, err := uuid.Parse(project.ID)
	if err != nil {
		slog.Error("Warning: Failed to parse project ID", "error", err)
	} else {
		projectID = pgtype.UUID{Bytes: projectUUID, Valid: true}
	}

	// Convert description to pgtype.Text
	description := pgtype.Text{
		String: project.Description,
		Valid:  project.Description != "",
	}

	// Convert metadata JSON
	metadata := []byte("{}")
	if len(project.Metadata) > 0 {
		// project.Metadata is datatypes.JSON which is []byte
		metadata = []byte(project.Metadata)
	}

	// Convert timestamps
	createdAt := pgtype.Timestamp{Time: project.CreatedAt, Valid: !project.CreatedAt.IsZero()}
	updatedAt := pgtype.Timestamp{Time: project.UpdatedAt, Valid: !project.UpdatedAt.IsZero()}
	deletedAt := pgtype.Timestamp{Valid: false}
	if project.DeletedAt != nil {
		deletedAt = pgtype.Timestamp{Time: *project.DeletedAt, Valid: true}
	}

	return db.Project{
		ID:          projectID,
		Name:        project.Name,
		Description: description,
		Metadata:    metadata,
		CreatedAt:   createdAt,
		UpdatedAt:   updatedAt,
		DeletedAt:   deletedAt,
	}
}

func (h *ProjectHandler) getCacheKey(projectID string) string {
	return "project:" + projectID
}

func (h *ProjectHandler) invalidateProjectCache(ctx context.Context, projectID string) {
	if h.cache == nil {
		return
	}
	key := h.getCacheKey(projectID)
	if err := h.cache.Delete(ctx, key); err != nil {
		slog.Error("Failed to invalidate project cache", "error", err)
	}
	if err := h.cache.InvalidatePattern(ctx, "projects:*"); err != nil {
		slog.Error("Failed to invalidate project list cache", "error", err)
	}
	// OPTIMIZATION 6.6: Also invalidate dashboard summary cache since projects changed
	if err := h.cache.InvalidatePattern(ctx, cache.DashboardSummaryKey+"*"); err != nil {
		slog.Error("Failed to invalidate dashboard cache", "error", err)
	}
}
