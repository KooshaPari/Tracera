package handlers

import (
	"net/http"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/traceability"
)

// TraceabilityHandler handles traceability matrix operations
type TraceabilityHandler struct {
	pool                *pgxpool.Pool
	service             *traceability.MatrixService
	cache               cache.Cache
	publisher           *nats.EventPublisher
	realtimeBroadcaster interface{}
	authProvider        interface{}
}

// NewTraceabilityHandler creates a new TraceabilityHandler
func NewTraceabilityHandler(
	pool *pgxpool.Pool,
	redisCache cache.Cache,
	eventPublisher *nats.EventPublisher,
	realtimeBroadcaster interface{},
	authProvider interface{},
) *TraceabilityHandler {
	return &TraceabilityHandler{
		pool:                pool,
		service:             traceability.NewMatrixService(pool, redisCache),
		cache:               redisCache,
		publisher:           eventPublisher,
		realtimeBroadcaster: realtimeBroadcaster,
		authProvider:        authProvider,
	}
}

// GenerateMatrix generates a complete traceability matrix for a project
// GET /api/v1/traceability/matrix/:project_id
func (h *TraceabilityHandler) GenerateMatrix(c echo.Context) error {
	projectID := c.Param("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id is required",
		})
	}

	matrix, err := h.service.GenerateMatrix(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, matrix)
}

// GetCoverage generates a coverage report for a project
// GET /api/v1/traceability/coverage/:project_id
func (h *TraceabilityHandler) GetCoverage(c echo.Context) error {
	projectID := c.Param("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id is required",
		})
	}

	report, err := h.service.GetCoverageReport(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, report)
}

// GetGapAnalysis identifies gaps in traceability
// GET /api/v1/traceability/gaps/:project_id
func (h *TraceabilityHandler) GetGapAnalysis(echoCtx echo.Context) error {
	projectID := echoCtx.Param("project_id")
	if projectID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id is required",
		})
	}

	analysis, err := h.service.GetGapAnalysis(echoCtx.Request().Context(), projectID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return echoCtx.JSON(http.StatusOK, analysis)
}

// GetItemTraceability gets traceability for a specific item
// GET /api/v1/traceability/items/:item_id
func (h *TraceabilityHandler) GetItemTraceability(c echo.Context) error {
	itemID := c.Param("item_id")
	if itemID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "item_id is required",
		})
	}

	traceability, err := h.service.GetItemTraceability(c.Request().Context(), itemID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, traceability)
}

// ValidateCompleteness validates traceability completeness
// GET /api/v1/traceability/validate/:project_id
func (h *TraceabilityHandler) ValidateCompleteness(c echo.Context) error {
	projectID := c.Param("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id is required",
		})
	}

	report, err := h.service.ValidateCompleteness(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, report)
}

// GetChangeImpact analyzes the impact of changes to an item
// GET /api/v1/traceability/impact/:item_id
func (h *TraceabilityHandler) GetChangeImpact(c echo.Context) error {
	itemID := c.Param("item_id")
	if itemID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "item_id is required",
		})
	}

	impact, err := h.service.GetChangeImpact(c.Request().Context(), itemID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, impact)
}
