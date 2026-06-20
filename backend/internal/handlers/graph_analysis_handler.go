package handlers

import (
	"net/http"
	"strconv"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/graph"
)

// GraphAnalysisHandler handles Neo4j-based graph analysis HTTP requests
type GraphAnalysisHandler struct {
	analysisService *graph.AnalysisService
}

// NewGraphAnalysisHandler creates a new graph analysis handler
func NewGraphAnalysisHandler(analysisService *graph.AnalysisService) *GraphAnalysisHandler {
	return &GraphAnalysisHandler{
		analysisService: analysisService,
	}
}

// GetShortestPath handles GET /api/v1/graph/analysis/shortest-path
// @Summary Find shortest path between two items
// @Description Computes the shortest path between source and target items using Neo4j
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param source query string true "Source item ID"
// @Param target query string true "Target item ID"
// @Success 200 {object} graph.Path
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/shortest-path [get]
func (h *GraphAnalysisHandler) GetShortestPath(c echo.Context) error {
	sourceID := c.QueryParam("source")
	targetID := c.QueryParam("target")

	if sourceID == "" || targetID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "source and target parameters are required",
		})
	}

	path, err := h.analysisService.ShortestPath(c.Request().Context(), sourceID, targetID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, path)
}

// DetectCycles handles GET /api/v1/graph/analysis/cycles
// @Summary Detect cycles in project graph
// @Description Finds all cycles in the project's dependency graph using Neo4j
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {array} graph.Cycle
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/cycles [get]
func (handler *GraphAnalysisHandler) DetectCycles(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id parameter is required",
		})
	}

	cycles, err := handler.analysisService.DetectCycles(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"cycles": cycles,
		"count":  len(cycles),
	})
}

// GetCentrality handles GET /api/v1/graph/analysis/centrality
// @Summary Calculate centrality metrics
// @Description Computes betweenness, closeness, and PageRank centrality for project items
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {object} graph.CentralityMetrics
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/centrality [get]
func (h *GraphAnalysisHandler) GetCentrality(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id parameter is required",
		})
	}

	metrics, err := h.analysisService.CalculateCentrality(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, metrics)
}

// GetDependencies handles GET /api/v1/graph/analysis/dependencies
// @Summary Get item dependencies (forward)
// @Description Retrieves all items that this item depends on
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param item_id query string true "Item ID"
// @Param max_depth query int false "Maximum traversal depth" default(3)
// @Success 200 {object} graph.DependencyTree
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/dependencies [get]
func (h *GraphAnalysisHandler) GetDependencies(c echo.Context) error {
	itemID := c.QueryParam("item_id")
	maxDepthStr := c.QueryParam("max_depth")

	if itemID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "item_id parameter is required",
		})
	}

	maxDepth := 3
	if maxDepthStr != "" {
		depth, err := strconv.Atoi(maxDepthStr)
		if err != nil || depth < 1 || depth > 10 {
			return c.JSON(http.StatusBadRequest, map[string]string{
				"error": "max_depth must be between 1 and 10",
			})
		}
		maxDepth = depth
	}

	tree, err := h.analysisService.GetDependencies(c.Request().Context(), itemID, maxDepth)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, tree)
}

// GetDependents handles GET /api/v1/graph/analysis/dependents
// @Summary Get item dependents (backward)
// @Description Retrieves all items that depend on this item
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param item_id query string true "Item ID"
// @Param max_depth query int false "Maximum traversal depth" default(3)
// @Success 200 {object} graph.DependencyTree
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/dependents [get]
func (h *GraphAnalysisHandler) GetDependents(echoCtx echo.Context) error {
	itemID := echoCtx.QueryParam("item_id")
	maxDepthStr := echoCtx.QueryParam("max_depth")

	if itemID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{
			"error": "item_id parameter is required",
		})
	}

	maxDepth := 3
	if maxDepthStr != "" {
		depth, err := strconv.Atoi(maxDepthStr)
		if err != nil || depth < 1 || depth > 10 {
			return echoCtx.JSON(http.StatusBadRequest, map[string]string{
				"error": "max_depth must be between 1 and 10",
			})
		}
		maxDepth = depth
	}

	tree, err := h.analysisService.GetDependents(echoCtx.Request().Context(), itemID, maxDepth)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return echoCtx.JSON(http.StatusOK, tree)
}

// AnalyzeImpact handles POST /api/v1/graph/analysis/impact
// @Summary Analyze impact of changes
// @Description Computes which items would be affected by changes to the specified items
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param request body ImpactAnalysisRequest true "Items to analyze"
// @Success 200 {object} graph.ImpactReport
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/impact [post]
func (h *GraphAnalysisHandler) AnalyzeImpact(c echo.Context) error {
	var req ImpactAnalysisRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "invalid request body",
		})
	}

	if len(req.ItemIDs) == 0 {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "at least one item_id is required",
		})
	}

	report, err := h.analysisService.AnalyzeImpact(c.Request().Context(), req.ItemIDs)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, report)
}

// AnalyzeCoverage handles GET /api/v1/graph/analysis/coverage
// @Summary Analyze graph coverage
// @Description Computes coverage statistics (connected vs isolated items)
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {object} graph.CoverageReport
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/coverage [get]
func (handler *GraphAnalysisHandler) AnalyzeCoverage(echoCtx echo.Context) error {
	projectID := echoCtx.QueryParam("project_id")

	if projectID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id parameter is required",
		})
	}

	report, err := handler.analysisService.AnalyzeCoverage(echoCtx.Request().Context(), projectID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return echoCtx.JSON(http.StatusOK, report)
}

// GetMetrics handles GET /api/v1/graph/analysis/metrics
// @Summary Get graph metrics
// @Description Computes overall graph statistics for a project
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {object} graph.Metrics
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/metrics [get]
func (h *GraphAnalysisHandler) GetMetrics(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id parameter is required",
		})
	}

	metrics, err := h.analysisService.GetMetrics(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, metrics)
}

// InvalidateCache handles POST /api/v1/graph/analysis/cache/invalidate
// @Summary Invalidate graph cache
// @Description Clears all cached graph analysis results for a project
// @Tags graph-analysis
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {object} map[string]string
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/graph/analysis/cache/invalidate [post]
func (handler *GraphAnalysisHandler) InvalidateCache(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id parameter is required",
		})
	}

	err := handler.analysisService.InvalidateCache(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"message": "cache invalidated successfully",
	})
}

// Request types

// ImpactAnalysisRequest represents a request to analyze impact
type ImpactAnalysisRequest struct {
	ItemIDs []string `json:"item_i_ds" validate:"required,min=1"`
}
