package codeindex

import (
	"io"
	"net/http"
	"strconv"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// Handler handles HTTP requests for code indexing
type Handler struct {
	service Service
}

// NewHandler creates a new code indexing handler
func NewHandler(service Service) *Handler {
	return &Handler{service: service}
}

// RegisterRoutes registers the code indexing routes
func (handler *Handler) RegisterRoutes(group *echo.Group) {
	group.POST("/index", handler.Index)
	group.POST("/reindex", handler.Reindex)
	group.GET("/entities", handler.ListEntities)
	group.GET("/entities/:id", handler.GetEntity)
	group.DELETE("/entities/:id", handler.DeleteEntity)
	group.GET("/search", handler.SearchEntities)
	group.POST("/chains/analyze", handler.AnalyzeCallChains)
	group.GET("/chains", handler.ListCallChains)
	group.GET("/chains/:id", handler.GetCallChain)
	group.GET("/entities/:id/refs", handler.GetCrossLangRefs)
	group.POST("/webhook", handler.HandleWebhook)
	group.GET("/stats", handler.GetStats)
}

// Index triggers code indexing
func (handler *Handler) Index(echoCtx echo.Context) error {
	var req IndexRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	result, err := handler.service.Index(echoCtx.Request().Context(), &req)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, result)
}

// Reindex re-indexes all code for a project
func (handler *Handler) Reindex(echoCtx echo.Context) error {
	var req IndexRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	result, err := handler.service.ReindexProject(echoCtx.Request().Context(), &req)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, result)
}

// ListEntities lists code entities for a project
func (handler *Handler) ListEntities(echoCtx echo.Context) error {
	projectID, err := uuid.Parse(echoCtx.QueryParam("project_id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	opts := &ListOptions{
		Language:     Language(echoCtx.QueryParam("language")),
		SymbolType:   SymbolType(echoCtx.QueryParam("symbol_type")),
		FilePath:     echoCtx.QueryParam("file_path"),
		ModulePath:   "",
		IsExported:   nil,
		HasCanonical: nil,
		Limit:        0,
		Offset:       0,
	}

	if limit := echoCtx.QueryParam("limit"); limit != "" {
		if l, err := strconv.Atoi(limit); err == nil {
			opts.Limit = l
		}
	}

	entities, err := handler.service.ListEntities(echoCtx.Request().Context(), projectID, opts)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, entities)
}

// GetEntity retrieves a specific code entity
func (handler *Handler) GetEntity(echoCtx echo.Context) error {
	id, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
	}

	entity, err := handler.service.GetEntity(echoCtx.Request().Context(), id)
	if err != nil {
		return echoCtx.JSON(http.StatusNotFound, map[string]string{"error": "entity not found"})
	}

	return echoCtx.JSON(http.StatusOK, entity)
}

// DeleteEntity deletes a code entity
func (handler *Handler) DeleteEntity(echoCtx echo.Context) error {
	id, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
	}

	if err := handler.service.DeleteEntity(echoCtx.Request().Context(), id); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// SearchEntities searches code entities
func (handler *Handler) SearchEntities(echoCtx echo.Context) error {
	projectID, err := uuid.Parse(echoCtx.QueryParam("project_id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	query := echoCtx.QueryParam("q")
	limit := 20
	if l := echoCtx.QueryParam("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil {
			limit = parsed
		}
	}

	entities, err := handler.service.SearchEntities(echoCtx.Request().Context(), projectID, query, limit)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, entities)
}

// AnalyzeCallChains analyzes call chains for a project
func (handler *Handler) AnalyzeCallChains(echoCtx echo.Context) error {
	projectID, err := uuid.Parse(echoCtx.QueryParam("project_id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	chains, err := handler.service.AnalyzeCallChains(echoCtx.Request().Context(), projectID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, chains)
}

// ListCallChains lists call chains for a project
func (handler *Handler) ListCallChains(echoCtx echo.Context) error {
	projectID, err := uuid.Parse(echoCtx.QueryParam("project_id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	chains, err := handler.service.AnalyzeCallChains(echoCtx.Request().Context(), projectID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, chains)
}

// GetCallChain retrieves a specific call chain
func (handler *Handler) GetCallChain(echoCtx echo.Context) error {
	id, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
	}

	chain, err := handler.service.GetCallChain(echoCtx.Request().Context(), id)
	if err != nil {
		return echoCtx.JSON(http.StatusNotFound, map[string]string{"error": "chain not found"})
	}

	return echoCtx.JSON(http.StatusOK, chain)
}

// GetCrossLangRefs retrieves cross-language references for an entity
func (handler *Handler) GetCrossLangRefs(echoCtx echo.Context) error {
	id, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid id"})
	}

	refs, err := handler.service.GetCrossLangRefs(echoCtx.Request().Context(), id)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, refs)
}

// HandleWebhook handles GitHub webhooks
func (handler *Handler) HandleWebhook(echoCtx echo.Context) error {
	projectID, err := uuid.Parse(echoCtx.QueryParam("project_id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	eventType := echoCtx.Request().Header.Get("X-GitHub-Event")
	payload, err := io.ReadAll(echoCtx.Request().Body)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "failed to read body"})
	}

	result, err := handler.service.HandleWebhook(echoCtx.Request().Context(), projectID, eventType, payload)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, result)
}

// GetStats retrieves indexing statistics
func (handler *Handler) GetStats(echoCtx echo.Context) error {
	projectID, err := uuid.Parse(echoCtx.QueryParam("project_id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	stats, err := handler.service.GetStats(echoCtx.Request().Context(), projectID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, stats)
}
