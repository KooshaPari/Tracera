package handlers

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/docservice"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/realtime"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// DocIndexHandler handles documentation indexing operations
type DocIndexHandler struct {
	docService          *docservice.Service
	cache               cache.Cache
	publisher           *nats.EventPublisher
	realtimeBroadcaster interface{} // realtime.Broadcaster
	authProvider        interface{} // auth.Provider
	binder              RequestBinder
}

// NewDocIndexHandler creates a new documentation handler
func NewDocIndexHandler(
	pool *pgxpool.Pool,
	redisCache cache.Cache,
	eventPublisher *nats.EventPublisher,
	realtimeBroadcaster interface{},
	authProvider interface{},
	binder RequestBinder,
) *DocIndexHandler {
	docService := docservice.NewService(pool)

	return &DocIndexHandler{
		docService:          docService,
		cache:               redisCache,
		publisher:           eventPublisher,
		realtimeBroadcaster: realtimeBroadcaster,
		authProvider:        authProvider,
		binder:              binder,
	}
}

// IndexDocumentationRequest represents a request to index documentation
type IndexDocumentationRequest struct {
	ProjectID string                 `json:"project_id"`
	Title     string                 `json:"title"`
	Format    string                 `json:"format"` // markdown, rst, html, plaintext
	Content   string                 `json:"content"`
	SourceURL string                 `json:"source_url,omitempty"`
	FilePath  string                 `json:"file_path,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// IndexDocumentation godoc
// @Summary Index new documentation
// @Description Parses and indexes documentation in various formats (markdown, rst, etc.)
// @Tags documentation
// @Accept json
// @Produce json
// @Param request body IndexDocumentationRequest true "Documentation to index"
// @Success 201 {object} map[string]interface{} "Documentation indexed successfully"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Failed to index documentation"
// @Security ApiKeyAuth
// @Router /api/v1/docs [post]
func (h *DocIndexHandler) IndexDocumentation(c echo.Context) error {
	var req IndexDocumentationRequest
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: fmt.Sprintf("invalid request: %v", err)})
	}

	format, err := validateIndexDocumentationRequest(&req)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
	}

	// Parse project ID
	projectID, err := uuidutil.StringToUUID(req.ProjectID)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid project_id"})
	}

	// Call service to index documentation
	docReq := &docservice.IndexDocumentationRequest{
		ProjectID: projectID.String(),
		Title:     req.Title,
		Format:    format,
		Content:   req.Content,
	}

	resp, err := h.docService.IndexDocumentation(c.Request().Context(), docReq)
	if err != nil {
		return c.JSON(
			http.StatusInternalServerError,
			ErrorResponse{Error: fmt.Sprintf("failed to index documentation: %v", err)},
		)
	}

	// Type assert response to get ID
	var respID uuid.UUID
	if respTyped, ok := resp.(*docservice.ParsedDocument); ok && respTyped != nil {
		respID = respTyped.ID
	} else {
		// Fallback: generate new ID if response doesn't have one
		respID = uuid.New()
	}

	// Publish event
	if h.publisher != nil {
		go h.publishDocEvent(c.Request().Context(), "indexed", respID.String(), resp)
	}

	// Broadcast via realtime
	if h.realtimeBroadcaster != nil {
		go h.broadcastDocEvent(c.Request().Context(), "indexed", respID.String(), projectID.String())
	}

	return c.JSON(http.StatusCreated, resp)
}

func validateIndexDocumentationRequest(req *IndexDocumentationRequest) (string, error) {
	if req.ProjectID == "" {
		return "", errors.New("project_id is required")
	}
	if req.Title == "" {
		return "", errors.New("title is required")
	}
	if req.Content == "" {
		return "", errors.New("content is required")
	}
	return normalizeDocFormat(req.Format)
}

func normalizeDocFormat(format string) (string, error) {
	normalized := strings.ToLower(format)
	validFormats := map[string]bool{
		"markdown":         true,
		"md":               true,
		"rst":              true,
		"restructuredtext": true,
		"html":             true,
		"plaintext":        true,
		"text":             true,
	}
	if !validFormats[normalized] {
		return "", errors.New("invalid format: must be markdown, rst, html, or plaintext")
	}
	return normalized, nil
}

// ListDocumentation godoc
// @Summary List documentation
// @Description Lists all documentation for a project with pagination
// @Tags documentation
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Param limit query int false "Limit (default 100)"
// @Param offset query int false "Offset (default 0)"
// @Success 200 {object} map[string]interface{} "List of documentation"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Failed to list documentation"
// @Security ApiKeyAuth
// @Router /api/v1/docs [get]
func (h *DocIndexHandler) ListDocumentation(c echo.Context) error {
	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "project_id is required"})
	}

	projectID, err := uuidutil.StringToUUID(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid project_id"})
	}

	limit := 100
	offset := 0

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil {
			limit = l
		}
	}
	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if o, err := strconv.Atoi(offsetStr); err == nil {
			offset = o
		}
	}

	// Convert pgtype.UUID to uuid.UUID
	projectUUID, err := uuid.Parse(projectID.String())
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid project_id format"})
	}
	docs, total, err := h.docService.ListDocumentation(c.Request().Context(), projectUUID, limit, offset)
	if err != nil {
		errMsg := fmt.Sprintf("failed to list documentation: %v", err)
		errorResponse := ErrorResponse{Error: errMsg}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"data":   docs,
		"total":  total,
		"limit":  limit,
		"offset": offset,
	})
}

// GetDocumentation godoc
// @Summary Get documentation by ID
// @Description Retrieves a specific documentation by ID
// @Tags documentation
// @Accept json
// @Produce json
// @Param id path string true "Documentation ID"
// @Success 200 {object} map[string]interface{} "Documentation retrieved"
// @Failure 400 {object} ErrorResponse "Invalid ID"
// @Failure 404 {object} ErrorResponse "Documentation not found"
// @Failure 500 {object} ErrorResponse "Failed to get documentation"
// @Security ApiKeyAuth
// @Router /api/v1/docs/{id} [get]
func (h *DocIndexHandler) GetDocumentation(c echo.Context) error {
	idStr := c.Param("id")
	docID, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid documentation ID"})
	}

	// Convert pgtype.UUID to uuid.UUID
	docUUID, err := uuid.Parse(docID.String())
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid documentation ID format"})
	}

	// Try to get from cache first
	cacheKey := h.getCacheKey("doc", docID.String())
	if h.cache != nil {
		var cachedResp interface{}
		if err := h.cache.Get(c.Request().Context(), cacheKey, &cachedResp); err == nil {
			return c.JSON(http.StatusOK, cachedResp)
		}
	}

	resp, err := h.docService.GetDocumentation(c.Request().Context(), docUUID)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "documentation not found"})
		}
		errorResponse := ErrorResponse{Error: fmt.Sprintf("failed to get documentation: %v", err)}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	// Cache the response
	if h.cache != nil {
		if err := h.cache.Set(c.Request().Context(), cacheKey, resp); err != nil {
			slog.Error("failed to cache documentation", "error", docID.String(), "error", err)
		}
	}

	return c.JSON(http.StatusOK, resp)
}

// UpdateDocumentation godoc
// @Summary Update documentation
// @Description Updates an existing documentation
// @Tags documentation
// @Accept json
// @Produce json
// @Param id path string true "Documentation ID"
// @Param request body IndexDocumentationRequest true "Updated documentation"
// @Success 200 {object} map[string]interface{} "Documentation updated"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Documentation not found"
// @Failure 500 {object} ErrorResponse "Failed to update documentation"
// @Security ApiKeyAuth
// @Router /api/v1/docs/{id} [put]
func (h *DocIndexHandler) UpdateDocumentation(c echo.Context) error {
	idStr := c.Param("id")
	docID, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid documentation ID"})
	}

	var req IndexDocumentationRequest
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: fmt.Sprintf("invalid request: %v", err)})
	}

	// Convert pgtype.UUID to uuid.UUID
	docUUID, err := uuid.Parse(docID.String())
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid documentation ID format"})
	}

	docReq := &docservice.IndexDocumentationRequest{
		ProjectID: "",
		Title:     req.Title,
		Format:    req.Format,
		Content:   req.Content,
	}

	resp, err := h.docService.UpdateDocumentation(c.Request().Context(), docUUID, docReq)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "documentation not found"})
		}
		errMsg := fmt.Sprintf("failed to update documentation: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: errMsg})
	}

	// Invalidate cache
	h.invalidateDocCache(c.Request().Context(), docID.String())

	// Type assert response to get ID
	var respID uuid.UUID
	if respTyped, ok := resp.(*docservice.ParsedDocument); ok && respTyped != nil {
		respID = respTyped.ID
	} else {
		respID = docUUID
	}

	// Publish event
	if h.publisher != nil {
		go h.publishDocEvent(c.Request().Context(), "updated", docID.String(), resp)
	}

	// Broadcast via realtime
	if h.realtimeBroadcaster != nil {
		go h.broadcastDocEvent(c.Request().Context(), "updated", docID.String(), respID.String())
	}

	return c.JSON(http.StatusOK, resp)
}

// DeleteDocumentation godoc
// @Summary Delete documentation
// @Description Deletes a documentation record (soft delete)
// @Tags documentation
// @Accept json
// @Produce json
// @Param id path string true "Documentation ID"
// @Success 200 {object} map[string]string "Documentation deleted"
// @Failure 400 {object} ErrorResponse "Invalid ID"
// @Failure 404 {object} ErrorResponse "Documentation not found"
// @Failure 500 {object} ErrorResponse "Failed to delete documentation"
// @Security ApiKeyAuth
// @Router /api/v1/docs/{id} [delete]
func (h *DocIndexHandler) DeleteDocumentation(c echo.Context) error {
	idStr := c.Param("id")
	docID, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid documentation ID"})
	}

	// Convert pgtype.UUID to uuid.UUID
	docUUID, err := uuid.Parse(docID.String())
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid documentation ID format"})
	}

	err = h.docService.DeleteDocumentation(c.Request().Context(), docUUID)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "documentation not found"})
		}
		errMsg := fmt.Sprintf("failed to delete documentation: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: errMsg})
	}

	// Invalidate cache
	h.invalidateDocCache(c.Request().Context(), docID.String())

	// Publish event
	if h.publisher != nil {
		go h.publishDocEvent(c.Request().Context(), "deleted", docID.String(), nil)
	}

	// Broadcast via realtime
	if h.realtimeBroadcaster != nil {
		go h.broadcastDocEvent(c.Request().Context(), "deleted", docID.String(), "")
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "documentation deleted"})
}

// SearchDocumentation godoc
// @Summary Search documentation
// @Description Performs full-text search on documentation
// @Tags documentation
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Param query query string true "Search query"
// @Param limit query int false "Limit (default 100)"
// @Param offset query int false "Offset (default 0)"
// @Success 200 {object} map[string]interface{} "Search results"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Failed to search documentation"
// @Security ApiKeyAuth
// @Router /api/v1/docs/search [get]
func (h *DocIndexHandler) SearchDocumentation(c echo.Context) error {
	projectIDStr := c.QueryParam("project_id")
	query := c.QueryParam("query")

	if projectIDStr == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "project_id is required"})
	}
	if query == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "query is required"})
	}

	projectID, err := uuidutil.StringToUUID(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid project_id"})
	}

	limit := 100
	offset := 0

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil {
			limit = l
		}
	}
	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if o, err := strconv.Atoi(offsetStr); err == nil {
			offset = o
		}
	}

	// Convert pgtype.UUID to uuid.UUID
	projectUUID, err := uuid.Parse(projectID.String())
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid project_id format"})
	}

	docs, total, err := h.docService.SearchDocumentation(c.Request().Context(), projectUUID, query, limit, offset)
	if err != nil {
		errorResponse := ErrorResponse{Error: fmt.Sprintf("failed to search documentation: %v", err)}
		return c.JSON(http.StatusInternalServerError, errorResponse)
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"data":   docs,
		"total":  total,
		"limit":  limit,
		"offset": offset,
		"query":  query,
	})
}

// Helper functions

func (h *DocIndexHandler) getCacheKey(prefix, id string) string {
	return "doc:" + prefix + ":" + id
}

func (h *DocIndexHandler) invalidateDocCache(ctx context.Context, docID string) {
	if h.cache == nil {
		return
	}
	key := h.getCacheKey("doc", docID)
	if err := h.cache.Delete(ctx, key); err != nil {
		slog.Error("Error invalidating doc cache for", "error", docID, "error", err)
	}
	// Invalidate search cache pattern
	if err := h.cache.InvalidatePattern(ctx, "docs:search:*"); err != nil {
		slog.Error("Error invalidating search cache pattern", "error", err)
	}
}

func (h *DocIndexHandler) publishDocEvent(_ context.Context, eventType string, docID string, doc interface{}) {
	if h.publisher == nil {
		return
	}

	// Extract project ID from doc if possible, otherwise use empty string
	projectID := ""
	// Note: ParsedDocument may have ProjectID field, but we use empty string as fallback for now

	// Publish event
	eventData := map[string]interface{}{
		"doc_id": docID,
		"data":   doc,
		"event":  eventType,
	}
	if err := h.publisher.PublishProjectEvent("documentation:"+eventType, projectID, eventData); err != nil {
		slog.Error("Error publishing doc event for", "error", eventType, "id", docID, "error", err)
	}
}

func (h *DocIndexHandler) broadcastDocEvent(ctx context.Context, eventType string, docID string, projectID string) {
	if h.realtimeBroadcaster == nil {
		return
	}

	broadcaster, ok := h.realtimeBroadcaster.(realtime.Broadcaster)
	if !ok {
		return
	}

	event := &realtime.Event{
		Type:   eventType,
		Table:  "documentation",
		Schema: "public",
		Record: map[string]interface{}{
			"id":         docID,
			"project_id": projectID,
		},
		Timestamp: time.Now().Unix(),
	}

	if err := broadcaster.Publish(ctx, event); err != nil {
		slog.Error("Error broadcasting doc event for", "error", eventType, "id", docID, "error", err)
	}
}
