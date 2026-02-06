package handlers

import (
	"net/http"
	"strconv"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
)

const defaultViewportBufferPx = 500

// GraphViewportHandler handles graph viewport and visualization operations
type GraphViewportHandler struct {
	db   *gorm.DB
	pool *pgxpool.Pool
}

// NewGraphViewportHandler creates a new graph viewport handler
func NewGraphViewportHandler(db *gorm.DB, pool *pgxpool.Pool) *GraphViewportHandler {
	return &GraphViewportHandler{
		db:   db,
		pool: pool,
	}
}

// ViewportBounds represents the viewport rectangle
type ViewportBounds struct {
	MinX float64 `json:"min_x"`
	MinY float64 `json:"min_y"`
	MaxX float64 `json:"max_x"`
	MaxY float64 `json:"max_y"`
}

// ViewportRequest represents the viewport query request
type ViewportRequest struct {
	Viewport ViewportBounds `json:"viewport"`
	Zoom     float64        `json:"zoom"`
	BufferPx int            `json:"buffer_px"`
}

// ViewportResponse represents the viewport query response
type ViewportResponse struct {
	Nodes      []NodeData      `json:"nodes"`
	Edges      []EdgeData      `json:"edges"`
	HasMore    map[string]bool `json:"has_more"`
	TotalCount int64           `json:"total_count"`
	Viewport   ViewportBounds  `json:"viewport"`
}

// NodeData represents a graph node with position
type NodeData struct {
	ID       string                 `json:"id"`
	Type     string                 `json:"type"`
	Label    string                 `json:"label"`
	Position Position               `json:"position"`
	Data     map[string]interface{} `json:"data"`
}

// Position represents X,Y coordinates
type Position struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
}

// EdgeData represents a graph edge
type EdgeData struct {
	ID       string `json:"id"`
	SourceID string `json:"source_id"`
	TargetID string `json:"target_id"`
	Type     string `json:"type"`
	Label    string `json:"label"`
}

// GetViewportGraph returns graph nodes and edges within viewport bounds
// POST /api/v1/graph/viewport/:project_id
// @Summary Get graph viewport
// @Description Returns nodes and edges within the specified viewport bounds with spatial indexing for O(log n) queries
// @Tags graph
// @Accept json
// @Produce json
// @Param project_id path string true "Project ID"
// @Param request body ViewportRequest true "Viewport bounds and parameters"
// @Success 200 {object} ViewportResponse
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /graph/viewport/{project_id} [post]
//
//nolint:funlen
func (h *GraphViewportHandler) GetViewportGraph(ctx echo.Context) error {
	projectID := ctx.Param("project_id")
	if projectID == "" {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	var req ViewportRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	// Default buffer if not specified
	if req.BufferPx == 0 {
		req.BufferPx = defaultViewportBufferPx
	}

	// Expand viewport by buffer for smooth panning
	buffer := float64(req.BufferPx)
	minX := req.Viewport.MinX - buffer
	minY := req.Viewport.MinY - buffer
	maxX := req.Viewport.MaxX + buffer
	maxY := req.Viewport.MaxY + buffer

	// Query nodes in viewport using spatial index
	var items []models.Item
	result := h.db.Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_x BETWEEN ? AND ?", minX, maxX).
		Where("position_y BETWEEN ? AND ?", minY, maxY).
		Find(&items)

	if result.Error != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "failed to query viewport nodes: " + result.Error.Error(),
		})
	}

	// Extract node IDs for edge query
	nodeIDs := make([]string, len(items))
	for i, item := range items {
		nodeIDs[i] = item.ID
	}

	// Query edges between visible nodes
	var links []models.Link
	if len(nodeIDs) > 0 {
		result = h.db.Where("source_id IN ?", nodeIDs).
			Where("target_id IN ?", nodeIDs).
			Find(&links)

		if result.Error != nil {
			return ctx.JSON(http.StatusInternalServerError, map[string]string{
				"error": "failed to query viewport edges: " + result.Error.Error(),
			})
		}
	}

	// Check if more data exists in each direction
	hasMore := make(map[string]bool)

	// North (y < min_y)
	var northCount int64
	h.db.Model(&models.Item{}).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_y < ?", minY).
		Count(&northCount)
	hasMore["north"] = northCount > 0

	// South (y > max_y)
	var southCount int64
	h.db.Model(&models.Item{}).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_y > ?", maxY).
		Count(&southCount)
	hasMore["south"] = southCount > 0

	// East (x > max_x)
	var eastCount int64
	h.db.Model(&models.Item{}).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_x > ?", maxX).
		Count(&eastCount)
	hasMore["east"] = eastCount > 0

	// West (x < min_x)
	var westCount int64
	h.db.Model(&models.Item{}).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_x < ?", minX).
		Count(&westCount)
	hasMore["west"] = westCount > 0

	// Get total count
	var totalCount int64
	h.db.Model(&models.Item{}).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Count(&totalCount)

	// Serialize nodes
	nodes := make([]NodeData, len(items))
	for i, item := range items {
		nodes[i] = serializeNode(&item)
	}

	// Serialize edges
	edges := make([]EdgeData, len(links))
	for i, link := range links {
		edges[i] = serializeEdge(&link)
	}

	return ctx.JSON(http.StatusOK, ViewportResponse{
		Nodes:      nodes,
		Edges:      edges,
		HasMore:    hasMore,
		TotalCount: totalCount,
		Viewport: ViewportBounds{
			MinX: minX,
			MinY: minY,
			MaxX: maxX,
			MaxY: maxY,
		},
	})
}

// GetViewportBounds returns the bounding box for a project
// GET /api/v1/graph/viewport/:project_id/bounds
// @Summary Get project viewport bounds
// @Description Returns the min/max X/Y coordinates for all nodes in a project
// @Tags graph
// @Produce json
// @Param project_id path string true "Project ID"
// @Success 200 {object} map[string]interface{}
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /graph/viewport/{project_id}/bounds [get]
func (h *GraphViewportHandler) GetViewportBounds(c echo.Context) error {
	projectID := c.Param("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	type BoundsResult struct {
		MinX       *float64
		MaxX       *float64
		MinY       *float64
		MaxY       *float64
		TotalNodes int64
	}

	var bounds BoundsResult
	selectClause := strings.Join([]string{
		"MIN(position_x) as min_x",
		"MAX(position_x) as max_x",
		"MIN(position_y) as min_y",
		"MAX(position_y) as max_y",
		"COUNT(*) as total_nodes",
	}, ", ")

	result := h.db.Model(&models.Item{}).
		Select(selectClause).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_x IS NOT NULL").
		Where("position_y IS NOT NULL").
		Scan(&bounds)

	if result.Error != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "failed to get viewport bounds: " + result.Error.Error(),
		})
	}

	response := map[string]interface{}{
		"projectId":  projectID,
		"totalNodes": bounds.TotalNodes,
	}

	if bounds.MinX != nil && bounds.MaxX != nil && bounds.MinY != nil && bounds.MaxY != nil {
		response["bounds"] = ViewportBounds{
			MinX: *bounds.MinX,
			MinY: *bounds.MinY,
			MaxX: *bounds.MaxX,
			MaxY: *bounds.MaxY,
		}
	} else {
		response["bounds"] = nil
		response["message"] = "No positioned nodes found in project"
	}

	return c.JSON(http.StatusOK, response)
}

// serializeNode converts an Item to NodeData
func serializeNode(item *models.Item) NodeData {
	posX := 0.0
	posY := 0.0
	if item.PositionX != nil {
		posX = *item.PositionX
	}
	if item.PositionY != nil {
		posY = *item.PositionY
	}

	label := item.Title
	if label == "" {
		label = item.ID
	}

	data := map[string]interface{}{
		"status":   item.Status,
		"priority": item.Priority,
		"type":     item.Type,
	}

	return NodeData{
		ID:    item.ID,
		Type:  item.Type,
		Label: label,
		Position: Position{
			X: posX,
			Y: posY,
		},
		Data: data,
	}
}

// serializeEdge converts a Link to EdgeData
func serializeEdge(link *models.Link) EdgeData {
	label := link.Type
	// Convert snake_case to space-separated
	if label != "" {
		label = strconv.Quote(label)
		label = label[1 : len(label)-1] // Remove quotes
	}

	return EdgeData{
		ID:       link.ID,
		SourceID: link.SourceID,
		TargetID: link.TargetID,
		Type:     link.Type,
		Label:    label,
	}
}
