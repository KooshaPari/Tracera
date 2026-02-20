package handlers

import (
	"net/http"
	"strconv"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
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
func (h *GraphViewportHandler) GetViewportGraph(ctx echo.Context) error {
	projectID := ctx.Param("project_id")
	if projectID == "" {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	var req ViewportRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	if req.BufferPx == 0 {
		req.BufferPx = defaultViewportBufferPx
	}

	vp := bufferViewport(req.Viewport, float64(req.BufferPx))

	items, err := h.queryViewportNodes(projectID, vp)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "failed to query viewport nodes: " + err.Error(),
		})
	}

	nodeIDs := make([]string, len(items))
	for i, item := range items {
		nodeIDs[i] = item.ID
	}

	links, err := h.queryViewportEdges(nodeIDs)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "failed to query viewport edges: " + err.Error(),
		})
	}

	hasMore, totalCount := h.viewportOverflow(projectID, vp)

	nodes := make([]NodeData, len(items))
	for i, item := range items {
		nodes[i] = serializeNode(&item)
	}
	edges := make([]EdgeData, len(links))
	for i, link := range links {
		edges[i] = serializeEdge(&link)
	}

	return ctx.JSON(http.StatusOK, ViewportResponse{
		Nodes:      nodes,
		Edges:      edges,
		HasMore:    hasMore,
		TotalCount: totalCount,
		Viewport:   vp,
	})
}

func bufferViewport(vp ViewportBounds, buffer float64) ViewportBounds {
	return ViewportBounds{
		MinX: vp.MinX - buffer,
		MinY: vp.MinY - buffer,
		MaxX: vp.MaxX + buffer,
		MaxY: vp.MaxY + buffer,
	}
}

func (h *GraphViewportHandler) queryViewportNodes(projectID string, vp ViewportBounds) ([]models.Item, error) {
	var items []models.Item
	result := h.db.Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_x BETWEEN ? AND ?", vp.MinX, vp.MaxX).
		Where("position_y BETWEEN ? AND ?", vp.MinY, vp.MaxY).
		Find(&items)
	return items, result.Error
}

func (h *GraphViewportHandler) queryViewportEdges(nodeIDs []string) ([]models.Link, error) {
	if len(nodeIDs) == 0 {
		return nil, nil
	}
	var links []models.Link
	result := h.db.Where("source_id IN ?", nodeIDs).
		Where("target_id IN ?", nodeIDs).
		Find(&links)
	return links, result.Error
}

func (h *GraphViewportHandler) viewportOverflow(projectID string, vp ViewportBounds) (map[string]bool, int64) {
	base := h.db.Model(&models.Item{}).Where("project_id = ?", projectID).Where("deleted_at IS NULL")

	countWhere := func(col, op string, val float64) bool {
		var cnt int64
		base.Where(col+" "+op+" ?", val).Count(&cnt)
		return cnt > 0
	}

	hasMore := map[string]bool{
		"north": countWhere("position_y", "<", vp.MinY),
		"south": countWhere("position_y", ">", vp.MaxY),
		"east":  countWhere("position_x", ">", vp.MaxX),
		"west":  countWhere("position_x", "<", vp.MinX),
	}

	var totalCount int64
	base.Count(&totalCount)

	return hasMore, totalCount
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
