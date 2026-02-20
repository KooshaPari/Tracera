package docindex

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// Handler handles HTTP requests for documentation indexing
type Handler struct {
	service Service
}

// NewHandler creates a new documentation handler
func NewHandler(service Service) *Handler {
	return &Handler{service: service}
}

// RegisterRoutes registers routes with an Echo group
func (h *Handler) RegisterRoutes(group *echo.Group) {
	group.POST("/index", h.Index)
	group.POST("/reindex", h.Reindex)
	group.GET("/entities", h.ListEntities)
	group.GET("/entities/:id", h.GetEntity)
	group.DELETE("/entities/:id", h.DeleteEntity)
	group.GET("/search", h.Search)
	group.POST("/entities/:id/link", h.LinkToCode)
	group.GET("/entities/:id/links", h.GetLinks)
}

// Index handles POST /docs/index - trigger documentation indexing
func (h *Handler) Index(c echo.Context) error {
	var req IndexRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
	}

	if req.ProjectID == uuid.Nil {
		return echo.NewHTTPError(http.StatusBadRequest, "project_id is required")
	}

	result, err := h.service.Index(c.Request().Context(), &req)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return c.JSON(http.StatusOK, result)
}

// Reindex handles POST /docs/reindex - reindex all documentation
func (h *Handler) Reindex(c echo.Context) error {
	var req IndexRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
	}

	if req.ProjectID == uuid.Nil {
		return echo.NewHTTPError(http.StatusBadRequest, "project_id is required")
	}

	result, err := h.service.ReindexProject(c.Request().Context(), &req)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return c.JSON(http.StatusOK, result)
}

// ListEntities handles GET /docs/entities - list documentation entities
func (h *Handler) ListEntities(c echo.Context) error {
	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "project_id is required")
	}

	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid project_id")
	}

	opts := &ListOptions{
		Type:          DocEntityType(c.QueryParam("type")),
		FilePath:      c.QueryParam("file_path"),
		DocumentID:    nil,
		Limit:         0,
		Offset:        0,
		IncludeChunks: false,
	}

	entities, err := h.service.ListDocuments(c.Request().Context(), projectID, opts)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return c.JSON(http.StatusOK, entities)
}

// GetEntity handles GET /docs/entities/:id - get a specific entity
func (h *Handler) GetEntity(c echo.Context) error {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid entity id")
	}

	entity, err := h.service.GetDocument(c.Request().Context(), id)
	if err != nil {
		return echo.NewHTTPError(http.StatusNotFound, "entity not found")
	}

	return c.JSON(http.StatusOK, entity)
}

// DeleteEntity handles DELETE /docs/entities/:id - delete an entity
func (h *Handler) DeleteEntity(c echo.Context) error {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid entity id")
	}

	if err := h.service.DeleteDocument(c.Request().Context(), id); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return c.NoContent(http.StatusNoContent)
}

// Search handles GET /docs/search - search documentation
func (h *Handler) Search(c echo.Context) error {
	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "project_id is required")
	}

	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid project_id")
	}

	query := c.QueryParam("q")
	if query == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "query (q) is required")
	}

	limit := 10 // Default limit

	results, err := h.service.SearchDocuments(c.Request().Context(), projectID, query, limit)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return c.JSON(http.StatusOK, results)
}

// LinkToCode handles POST /docs/entities/:id/link - create doc-to-code links
func (h *Handler) LinkToCode(c echo.Context) error {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid entity id")
	}

	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "project_id is required")
	}

	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid project_id")
	}

	links, err := h.service.LinkDocToCode(c.Request().Context(), projectID, id)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return c.JSON(http.StatusOK, links)
}

// GetLinks handles GET /docs/entities/:id/links - get trace links
func (h *Handler) GetLinks(c echo.Context) error {
	id, err := uuid.Parse(c.Param("id"))
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid entity id")
	}

	links, err := h.service.GetTraceLinks(c.Request().Context(), id)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}

	return c.JSON(http.StatusOK, links)
}
