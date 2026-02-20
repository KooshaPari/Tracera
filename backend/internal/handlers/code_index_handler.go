package handlers

import (
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"strconv"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// CodeIndexHandler handles code indexing and search operations
type CodeIndexHandler struct {
	service services.CodeIndexService
	binder  RequestBinder
}

// NewCodeIndexHandler creates a new code index handler with required service
func NewCodeIndexHandler(
	service services.CodeIndexService,
	binder RequestBinder,
) *CodeIndexHandler {
	return &CodeIndexHandler{
		service: service,
		binder:  binder,
	}
}

// IndexCodeRequest represents a request to index code entities
type IndexCodeRequest struct {
	ProjectID     string                  `json:"project_id"`
	FilePath      string                  `json:"file_path"`
	Language      string                  `json:"language"`
	Entities      []CodeEntityInput       `json:"entities"`
	Relationships []CodeRelationshipInput `json:"relationships"`
}

// CodeEntityInput represents code entity input
type CodeEntityInput struct {
	EntityType    string          `json:"entity_type"`
	Name          string          `json:"name"`
	FullName      string          `json:"full_name"`
	Description   string          `json:"description"`
	LineNumber    int             `json:"line_number"`
	EndLineNumber int             `json:"end_line_number"`
	ColumnNumber  int             `json:"column_number"`
	CodeSnippet   string          `json:"code_snippet"`
	Signature     string          `json:"signature"`
	ReturnType    string          `json:"return_type"`
	Parameters    json.RawMessage `json:"parameters"`
	Metadata      json.RawMessage `json:"metadata"`
}

// CodeRelationshipInput represents code relationship input
type CodeRelationshipInput struct {
	SourceEntityName string          `json:"source_entity_name"`
	TargetEntityName string          `json:"target_entity_name"`
	RelationType     string          `json:"relation_type"`
	Metadata         json.RawMessage `json:"metadata"`
}

// IndexCode indexes code entities from a file
func (h *CodeIndexHandler) IndexCode(c echo.Context) error {
	if h.service == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	var req IndexCodeRequest
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	projectID, err := uuidutil.StringToUUID(req.ProjectID)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project_id"})
	}

	ctx := c.Request().Context()
	projectIDStr := projectID.String()

	// Convert handler request to service request
	serviceReq := &services.IndexCodeRequest{
		ProjectID:     projectIDStr,
		FilePath:      req.FilePath,
		Language:      req.Language,
		Entities:      convertToServiceEntityInputs(req.Entities),
		Relationships: convertToServiceRelationshipInputs(req.Relationships),
	}

	resp, err := h.service.IndexCode(ctx, serviceReq)
	if err != nil {
		slog.Error("Error indexing code", "error", err)
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to index code"})
	}

	return c.JSON(http.StatusCreated, map[string]interface{}{
		"entity_count": resp.EntityCount,
		"entities":     resp.Entities,
	})
}

// parseIntParam parses a query parameter as an int, returning defaultVal if missing or invalid.
func parseIntParam(c echo.Context, name string, defaultVal, minVal, maxVal int) int {
	raw := c.QueryParam(name)
	if raw == "" {
		return defaultVal
	}
	parsed, err := strconv.Atoi(raw)
	if err != nil || parsed < minVal || (maxVal > 0 && parsed > maxVal) {
		return defaultVal
	}
	return parsed
}

// ListEntities lists indexed code entities
func (h *CodeIndexHandler) ListEntities(c echo.Context) error {
	if h.service == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	limit := parseIntParam(c, "limit", 50, 1, 1000)
	offset := parseIntParam(c, "offset", 0, 0, 0)

	entities, err := h.service.ListEntities(c.Request().Context(), projectID, limit, offset)
	if err != nil {
		slog.Error("Error listing code entities", "error", err)
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to list entities"})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"entities": entities,
		"count":    len(entities),
		"limit":    limit,
		"offset":   offset,
	})
}

// GetEntity retrieves a single code entity by ID
func (h *CodeIndexHandler) GetEntity(c echo.Context) error {
	if h.service == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	entityID := c.Param("id")
	if entityID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "id is required"})
	}

	ctx := c.Request().Context()

	result, err := h.service.GetEntity(ctx, entityID)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Entity not found"})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"entity":         result.Entity,
		"relationships":  result.Relationships,
		"relation_count": result.RelationCount,
	})
}

// UpdateEntity updates a code entity
func (h *CodeIndexHandler) UpdateEntity(c echo.Context) error {
	if h.service == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	entityID := c.Param("id")
	if entityID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "id is required"})
	}

	var req struct {
		Description string          `json:"description"`
		Metadata    json.RawMessage `json:"metadata"`
	}
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	ctx := c.Request().Context()

	entity, err := h.service.UpdateEntity(ctx, entityID, req.Description, req.Metadata)
	if err != nil {
		slog.Error("Error updating code entity", "error", err)
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to update entity"})
	}
	return c.JSON(http.StatusOK, entity)
}

// DeleteEntity deletes a code entity
func (h *CodeIndexHandler) DeleteEntity(echoCtx echo.Context) error {
	if h.service == nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	entityID := echoCtx.Param("id")
	if entityID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "id is required"})
	}

	ctx := echoCtx.Request().Context()

	if err := h.service.DeleteEntity(ctx, entityID); err != nil {
		slog.Error("Error deleting code entity", "error", err)
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to delete entity"})
	}
	return echoCtx.JSON(http.StatusOK, map[string]string{"message": "Entity deleted successfully"})
}

// Reindex reindexes all code entities for a project (soft reset)
func (handler *CodeIndexHandler) Reindex(echoCtx echo.Context) error {
	if handler.service == nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	var req struct {
		ProjectID string `json:"project_id"`
	}
	if err := handler.binder.Bind(echoCtx, &req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	projectID, err := uuidutil.StringToUUID(req.ProjectID)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project_id"})
	}

	ctx := echoCtx.Request().Context()
	projectIDStr := projectID.String()

	if err := handler.service.Reindex(ctx, projectIDStr); err != nil {
		slog.Error("Error reindexing", "error", err)
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to reindex"})
	}

	return echoCtx.JSON(http.StatusOK, map[string]string{
		"message":    "Reindex started",
		"project_id": projectIDStr,
	})
}

// SearchEntities searches code entities
func (handler *CodeIndexHandler) SearchEntities(c echo.Context) error {
	if handler.service == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	params, err := parseSearchEntitiesParams(c)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	ctx := c.Request().Context()
	entities, err := handler.service.SearchEntities(
		ctx,
		params.projectID,
		params.query,
		params.limit,
		params.offset,
	)
	if err != nil {
		slog.Error("Error searching code entities", "error", err)
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Search failed"})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"query":    params.query,
		"entities": entities,
		"count":    len(entities),
		"limit":    params.limit,
		"offset":   params.offset,
	})
}

type searchEntitiesParams struct {
	projectID string
	query     string
	limit     int
	offset    int
}

func parseSearchEntitiesParams(c echo.Context) (searchEntitiesParams, error) {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return searchEntitiesParams{}, errors.New("project_id is required")
	}

	query := c.QueryParam("q")
	if query == "" {
		return searchEntitiesParams{}, errors.New("q (query) is required")
	}

	return searchEntitiesParams{
		projectID: projectID,
		query:     query,
		limit:     parseSearchLimit(c.QueryParam("limit")),
		offset:    parseSearchOffset(c.QueryParam("offset")),
	}, nil
}

func parseSearchLimit(value string) int {
	if value == "" {
		return 50
	}
	parsed, err := strconv.Atoi(value)
	if err != nil || parsed <= 0 || parsed > 1000 {
		return 50
	}
	return parsed
}

func parseSearchOffset(value string) int {
	if value == "" {
		return 0
	}
	parsed, err := strconv.Atoi(value)
	if err != nil || parsed < 0 {
		return 0
	}
	return parsed
}

// GetStats retrieves code indexing statistics
func (handler *CodeIndexHandler) GetStats(c echo.Context) error {
	if handler.service == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	ctx := c.Request().Context()

	stats, err := handler.service.GetStats(ctx, projectID)
	if err != nil {
		slog.Error("Error getting code index stats", "error", err)
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to get stats"})
	}
	return c.JSON(http.StatusOK, stats)
}

// BatchIndexCode indexes multiple code entities in batch
func (h *CodeIndexHandler) BatchIndexCode(c echo.Context) error {
	if h.service == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Code index service not initialized"})
	}

	var req struct {
		ProjectID string             `json:"project_id"`
		Batches   []IndexCodeRequest `json:"batches"`
	}
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	projectID, err := uuidutil.StringToUUID(req.ProjectID)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project_id"})
	}

	ctx := c.Request().Context()
	projectIDStr := projectID.String()

	// Convert handler batches to service batches
	serviceBatches := make([]services.IndexCodeRequest, 0, len(req.Batches))
	for _, batch := range req.Batches {
		serviceBatches = append(serviceBatches, services.IndexCodeRequest{
			ProjectID:     projectIDStr,
			FilePath:      batch.FilePath,
			Language:      batch.Language,
			Entities:      convertToServiceEntityInputs(batch.Entities),
			Relationships: convertToServiceRelationshipInputs(batch.Relationships),
		})
	}

	serviceReq := &services.BatchIndexRequest{
		ProjectID: projectIDStr,
		Batches:   serviceBatches,
	}

	resp, err := h.service.BatchIndexCode(ctx, serviceReq)
	if err != nil {
		slog.Error("Error batch indexing code", "error", err)
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to batch index code"})
	}

	return c.JSON(http.StatusCreated, map[string]interface{}{
		"entity_count":       resp.EntityCount,
		"relationship_count": resp.RelationshipCount,
		"batch_count":        resp.BatchCount,
	})
}

// Helper functions for converting between handler and service types

func convertToServiceEntityInputs(inputs []CodeEntityInput) []services.CodeEntityInput {
	result := make([]services.CodeEntityInput, len(inputs))
	for i, input := range inputs {
		result[i] = services.CodeEntityInput{
			EntityType:    input.EntityType,
			Name:          input.Name,
			FullName:      input.FullName,
			Description:   input.Description,
			LineNumber:    input.LineNumber,
			EndLineNumber: input.EndLineNumber,
			ColumnNumber:  input.ColumnNumber,
			CodeSnippet:   input.CodeSnippet,
			Signature:     input.Signature,
			ReturnType:    input.ReturnType,
			Parameters:    input.Parameters,
			Metadata:      input.Metadata,
		}
	}
	return result
}

func convertToServiceRelationshipInputs(inputs []CodeRelationshipInput) []services.CodeRelationshipInput {
	result := make([]services.CodeRelationshipInput, len(inputs))
	for i, input := range inputs {
		result[i] = services.CodeRelationshipInput{
			SourceEntityName: input.SourceEntityName,
			TargetEntityName: input.TargetEntityName,
			RelationType:     input.RelationType,
			Metadata:         input.Metadata,
		}
	}
	return result
}
