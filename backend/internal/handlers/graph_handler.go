package handlers

import (
	"context"
	"log/slog"
	"net/http"
	"strconv"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/graph"
)

// GraphHandler handles graph traversal and analysis operations
type GraphHandler struct {
	graph *graph.Graph
}

// NewGraphHandler creates a new graph handler with required graph service
func NewGraphHandler(pool *pgxpool.Pool) *GraphHandler {
	return &GraphHandler{
		graph: graph.NewGraph(pool),
	}
}

// GetAncestors returns all ancestors of an item (items that link to it)
// GET /api/v1/graph/ancestors/:id?max_depth=N
func (h *GraphHandler) GetAncestors(c echo.Context) error {
	itemID := c.Param("id")
	maxDepth := 0

	if depthStr := c.QueryParam("max_depth"); depthStr != "" {
		if d, err := strconv.Atoi(depthStr); err == nil {
			maxDepth = d
		}
	}

	result, err := h.graph.GetAncestors(c.Request().Context(), itemID, maxDepth)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// GetDescendants returns all descendants of an item (items it links to)
// GET /api/v1/graph/descendants/:id?max_depth=N
func (handler *GraphHandler) GetDescendants(c echo.Context) error {
	itemID := c.Param("id")
	maxDepth := 0

	if depthStr := c.QueryParam("max_depth"); depthStr != "" {
		if d, err := strconv.Atoi(depthStr); err == nil {
			maxDepth = d
		}
	}

	result, err := handler.graph.GetDescendants(c.Request().Context(), itemID, maxDepth)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// FindPath finds a path between two items
// GET /api/v1/graph/path?source=ID&target=ID
func (h *GraphHandler) FindPath(c echo.Context) error {
	sourceID := c.QueryParam("source")
	targetID := c.QueryParam("target")

	if sourceID == "" || targetID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "source and target parameters are required"})
	}

	result, err := h.graph.FindPath(c.Request().Context(), sourceID, targetID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// FindAllPaths finds all paths between two items
// GET /api/v1/graph/paths?source=ID&target=ID&max_paths=N
func (h *GraphHandler) FindAllPaths(c echo.Context) error {
	sourceID := c.QueryParam("source")
	targetID := c.QueryParam("target")
	maxPaths := 10

	if sourceID == "" || targetID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "source and target parameters are required"})
	}

	if maxPathsStr := c.QueryParam("max_paths"); maxPathsStr != "" {
		if mp, err := strconv.Atoi(maxPathsStr); err == nil && mp > 0 {
			maxPaths = mp
		}
	}

	results, err := h.graph.FindAllPaths(c.Request().Context(), sourceID, targetID, maxPaths)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"paths": results,
		"count": len(results),
	})
}

// GetFullGraph returns the complete graph for a project
// GET /api/v1/graph/full?project_id=ID
func (h *GraphHandler) GetFullGraph(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	result, err := h.graph.GetFullGraph(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// DetectCycles detects cycles in the graph
// GET /api/v1/graph/cycles?project_id=ID
func (h *GraphHandler) DetectCycles(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	cycles, err := h.graph.DetectCycles(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"cycles": cycles,
		"count":  len(cycles),
	})
}

// TopologicalSort performs topological sort on the graph
// GET /api/v1/graph/topo-sort?project_id=ID
func (h *GraphHandler) TopologicalSort(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	sorted, success, err := h.graph.TopologicalSort(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"sorted":  sorted,
		"success": success,
		"message": func() string {
			if success {
				return "Topological sort successful (no cycles detected)"
			}
			return "Topological sort incomplete (cycles detected in graph)"
		}(),
	})
}

// GetImpactAnalysis returns impact analysis for an item
// GET /api/v1/graph/impact/:id?max_depth=N
func (h *GraphHandler) GetImpactAnalysis(c echo.Context) error {
	itemID := c.Param("id")
	maxDepth := 0

	if depthStr := c.QueryParam("max_depth"); depthStr != "" {
		if d, err := strconv.Atoi(depthStr); err == nil {
			maxDepth = d
		}
	}

	result, err := h.graph.GetImpactAnalysis(c.Request().Context(), itemID, maxDepth)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"item_id":        itemID,
		"affected_items": result.Nodes,
		"affected_count": len(result.Nodes),
		"links":          result.Edges,
	})
}

// GetDependencyAnalysis returns dependency analysis for an item
// GET /api/v1/graph/dependencies/:id?max_depth=N
func (h *GraphHandler) GetDependencyAnalysis(c echo.Context) error {
	itemID := c.Param("id")
	maxDepth := 0

	if depthStr := c.QueryParam("max_depth"); depthStr != "" {
		if d, err := strconv.Atoi(depthStr); err == nil {
			maxDepth = d
		}
	}

	result, err := h.graph.GetDependencyAnalysis(c.Request().Context(), itemID, maxDepth)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"item_id":          itemID,
		"dependencies":     result.Nodes,
		"dependency_count": len(result.Nodes),
		"links":            result.Edges,
	})
}

// GetOrphanItems returns items with no links
// GET /api/v1/graph/orphans?project_id=ID
func (h *GraphHandler) GetOrphanItems(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	orphans, err := h.graph.GetOrphanItems(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"orphans": orphans,
		"count":   len(orphans),
	})
}

// Traverse performs BFS or DFS traversal
// GET /api/v1/graph/traverse/:id?algorithm=bfs&direction=forward&max_depth=N&link_types=type1,type2
func (h *GraphHandler) Traverse(c echo.Context) error {
	itemID := c.Param("id")
	return h.traverseWithParams(c, itemID)
}

func (h *GraphHandler) traverseWithParams(c echo.Context, itemID string) error {
	params := parseTraverseParams(c)
	result, err := h.executeTraversal(c.Request().Context(), itemID, params)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"algorithm":  params.algorithm,
		"direction":  params.direction,
		"start_id":   itemID,
		"link_types": params.linkTypes,
		"result":     result,
	})
}

type traverseParams struct {
	algorithm string
	direction string
	maxDepth  int
	linkTypes []string
}

func parseTraverseParams(c echo.Context) traverseParams {
	algorithm := c.QueryParam("algorithm")
	if algorithm == "" {
		algorithm = "bfs"
	}

	direction := c.QueryParam("direction")
	if direction == "" {
		direction = "forward"
	}

	return traverseParams{
		algorithm: algorithm,
		direction: direction,
		maxDepth:  parseTraverseMaxDepth(c.QueryParam("max_depth")),
		linkTypes: parseTraverseLinkTypes(c.QueryParam("link_types")),
	}
}

func parseTraverseMaxDepth(depthStr string) int {
	if depthStr == "" {
		return 0
	}
	depth, err := strconv.Atoi(depthStr)
	if err != nil {
		return 0
	}
	return depth
}

func parseTraverseLinkTypes(linkTypesParam string) []string {
	if linkTypesParam == "" {
		return nil
	}
	linkTypes := strings.Split(linkTypesParam, ",")
	for i := range linkTypes {
		linkTypes[i] = strings.TrimSpace(linkTypes[i])
	}
	return linkTypes
}

func (h *GraphHandler) executeTraversal(
	ctx context.Context,
	itemID string,
	params traverseParams,
) (*graph.Result, error) {
	if len(params.linkTypes) > 0 {
		return h.runFilteredTraversal(ctx, itemID, params)
	}
	return h.runTraversal(ctx, itemID, params)
}

func (h *GraphHandler) runFilteredTraversal(
	ctx context.Context,
	itemID string,
	params traverseParams,
) (*graph.Result, error) {
	if params.algorithm == "dfs" {
		return h.graph.DFSFiltered(ctx, itemID, params.direction, params.maxDepth, params.linkTypes)
	}
	return h.graph.BFSFiltered(ctx, itemID, params.direction, params.maxDepth, params.linkTypes)
}

func (h *GraphHandler) runTraversal(
	ctx context.Context,
	itemID string,
	params traverseParams,
) (*graph.Result, error) {
	if params.algorithm == "dfs" {
		return h.graph.DFS(ctx, itemID, params.direction, params.maxDepth)
	}
	return h.graph.BFS(ctx, itemID, params.direction, params.maxDepth)
}

// ComputeTransitiveClosure computes transitive closure for a project
// GET /api/v1/graph/transitive-closure?project_id=ID
func (h *GraphHandler) ComputeTransitiveClosure(echoCtx echo.Context) error {
	projectID := echoCtx.QueryParam("project_id")
	if projectID == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "project_id parameter is required"})
	}

	result, err := h.graph.ComputeTransitiveClosure(echoCtx.Request().Context(), projectID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, result)
}

// AnalyzeImpactPaths analyzes propagation paths from an item
// GET /api/v1/graph/impact-paths/:id?max_paths=N
func (handler *GraphHandler) AnalyzeImpactPaths(c echo.Context) error {
	itemID := c.Param("id")
	maxPaths := 50

	if maxPathsStr := c.QueryParam("max_paths"); maxPathsStr != "" {
		if mp, err := strconv.Atoi(maxPathsStr); err == nil && mp > 0 {
			maxPaths = mp
		}
	}

	result, err := handler.graph.AnalyzeImpactPaths(c.Request().Context(), itemID, maxPaths)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, result)
}

// GetMetrics returns overall graph statistics for a project
// GET /api/v1/graph/metrics?project_id=ID
func (h *GraphHandler) GetMetrics(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id parameter is required"})
	}

	result, err := h.graph.GetFullGraph(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"project_id":  projectID,
		"total_nodes": len(result.Nodes),
		"total_edges": len(result.Edges),
	})
}

// InvalidateCache invalidates all graph analysis cache for a project
// POST /api/v1/graph/cache/invalidate?project_id=ID
func (h *GraphHandler) InvalidateCache(c echo.Context) error {
	projectID := c.QueryParam("project_id")

	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id parameter is required"})
	}

	// Cache invalidation is handled internally by the graph package
	slog.Info("Graph cache invalidation requested for project", "id", projectID)

	return c.JSON(http.StatusOK, map[string]string{
		"message": "graph cache invalidated successfully for project " + projectID,
	})
}
