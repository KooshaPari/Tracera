package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

const (
	defaultGraphStreamBufferPx      = 500
	defaultGraphStreamChunkSize     = 50
	maxGraphStreamChunkSize         = 1000
	prefetchCacheControlHeader      = "private, max-age=60"
	prefetchChunkSize               = 25
	prefetchVelocityScaleDivisor    = 1000.0
	prefetchScaleCap                = 2.0
	prefetchDiagonalScaleFactor     = 0.7
	recommendedChunkSmallThreshold  = 100
	recommendedChunkMediumThreshold = 1000
	recommendedChunkSmallSize       = 25
	recommendedChunkMediumSize      = 50
	recommendedChunkLargeSize       = 100
	estimatedNodeSizeBytes          = 250
	estimatedEdgeSizeBytes          = 150
	estimatedMillisPerItem          = 2
	graphStreamPercentScale         = 100
)

// GraphStreamHandler handles streaming graph data
type GraphStreamHandler struct {
	db   *gorm.DB
	pool *pgxpool.Pool
}

// NewGraphStreamHandler creates a new graph stream handler
func NewGraphStreamHandler(db *gorm.DB, pool *pgxpool.Pool) *GraphStreamHandler {
	return &GraphStreamHandler{
		db:   db,
		pool: pool,
	}
}

// StreamChunk represents a single chunk in the NDJSON stream
type StreamChunk struct {
	Type      string        `json:"type"` // "node", "edge", "metadata", "progress", "complete"
	Data      interface{}   `json:"data"` // NodeData, EdgeData, or metadata
	Progress  *ProgressInfo `json:"progress,omitempty"`
	Timestamp int64         `json:"timestamp"`
}

// ProgressInfo represents loading progress
type ProgressInfo struct {
	Current    int     `json:"current"`
	Total      int     `json:"total"`
	Percentage float64 `json:"percentage"`
	Stage      string  `json:"stage"` // "nodes", "edges", "complete"
}

// StreamMetadata represents initial metadata about the stream
type StreamMetadata struct {
	ProjectID     string         `json:"project_id"`
	TotalNodes    int64          `json:"total_nodes"`
	TotalEdges    int64          `json:"total_edges"`
	Viewport      ViewportBounds `json:"viewport"`
	EstimatedTime int            `json:"estimated_time"` // milliseconds
	ChunkSize     int            `json:"chunk_size"`
}

// StreamGraphIncremental streams graph data incrementally with NDJSON format
// POST /api/v1/projects/:project_id/graph/stream
// @Summary Stream graph data incrementally
// @Description Streams graph nodes and edges in NDJSON format with progress updates and predictive prefetch
// @Tags graph
// @Accept json
// @Produce application/x-ndjson
// @Param project_id path string true "Project ID"
// @Param request body ViewportRequest true "Viewport bounds and parameters"
// @Success 200 {string} string "NDJSON stream of graph chunks"
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /projects/{project_id}/graph/stream [post]
func (h *GraphStreamHandler) StreamGraphIncremental(echoCtx echo.Context) error {
	projectID, req, chunkSize, err := h.parseStreamGraphRequest(echoCtx)
	if err != nil {
		return err
	}

	minX, maxX, minY, maxY := expandViewport(req)

	// Get total counts first for progress tracking
	totalNodes, err := h.countViewportNodes(projectID, minX, maxX, minY, maxY)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}
	var totalEdges int64
	ctx := echoCtx.Request().Context()

	setupNDJSONResponse(echoCtx)
	metadata := buildStreamMetadata(projectID, totalNodes, minX, maxX, minY, maxY, chunkSize)

	if err := h.sendChunk(echoCtx, StreamChunk{
		Type:      "metadata",
		Data:      metadata,
		Timestamp: time.Now().UnixMilli(),
	}); err != nil {
		return err
	}

	// Stream nodes in chunks
	nodeIDs := make([]string, 0, int(totalNodes))
	if err := h.streamNodes(ctx, echoCtx, projectID, minX, maxX, minY, maxY, chunkSize, &nodeIDs); err != nil {
		return err
	}

	// Count edges between visible nodes
	if len(nodeIDs) > 0 {
		if err := h.db.Model(&models.Link{}).
			Where("source_id IN ?", nodeIDs).
			Where("target_id IN ?", nodeIDs).
			Count(&totalEdges).Error; err != nil {
			return h.sendError(echoCtx, "failed to count edges: "+err.Error())
		}

		// Stream edges in chunks
		if err := h.streamEdges(ctx, echoCtx, nodeIDs, chunkSize, int(totalEdges)); err != nil {
			return err
		}
	}

	// Send completion marker
	return h.sendChunk(echoCtx, StreamChunk{
		Type: "complete",
		Data: map[string]interface{}{
			"totalNodes": totalNodes,
			"totalEdges": totalEdges,
		},
		Timestamp: time.Now().UnixMilli(),
	})
}

func (h *GraphStreamHandler) parseStreamGraphRequest(c echo.Context) (string, ViewportRequest, int, error) {
	projectID := c.Param("project_id")
	if projectID == "" {
		err := c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
		return "", ViewportRequest{}, 0, err
	}

	var req ViewportRequest
	if err := c.Bind(&req); err != nil {
		errorResponse := map[string]string{"error": "invalid request body"}
		return "", ViewportRequest{}, 0, c.JSON(http.StatusBadRequest, errorResponse)
	}

	if req.BufferPx == 0 {
		req.BufferPx = defaultGraphStreamBufferPx
	}

	chunkSize := defaultGraphStreamChunkSize
	if cs := c.QueryParam("chunk_size"); cs != "" {
		if size, err := strconv.Atoi(cs); err == nil && size > 0 && size <= maxGraphStreamChunkSize {
			chunkSize = size
		}
	}

	return projectID, req, chunkSize, nil
}

func expandViewport(req ViewportRequest) (float64, float64, float64, float64) {
	buffer := float64(req.BufferPx)
	minX := req.Viewport.MinX - buffer
	minY := req.Viewport.MinY - buffer
	maxX := req.Viewport.MaxX + buffer
	maxY := req.Viewport.MaxY + buffer
	return minX, maxX, minY, maxY
}

func (h *GraphStreamHandler) countViewportNodes(projectID string, minX, maxX, minY, maxY float64) (int64, error) {
	var totalNodes int64
	if err := h.db.Model(&models.Item{}).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_x BETWEEN ? AND ?", minX, maxX).
		Where("position_y BETWEEN ? AND ?", minY, maxY).
		Count(&totalNodes).Error; err != nil {
		return 0, fmt.Errorf("failed to count nodes: %w", err)
	}
	return totalNodes, nil
}

func setupNDJSONResponse(c echo.Context) {
	c.Response().Header().Set(echo.HeaderContentType, "application/x-ndjson")
	c.Response().Header().Set("Cache-Control", "no-cache")
	c.Response().Header().Set("Connection", "keep-alive")
	c.Response().Header().Set("X-Accel-Buffering", "no")
	c.Response().WriteHeader(http.StatusOK)
}

func buildStreamMetadata(
	projectID string,
	totalNodes int64,
	minX, maxX, minY, maxY float64,
	chunkSize int,
) StreamMetadata {
	return StreamMetadata{
		ProjectID:  projectID,
		TotalNodes: totalNodes,
		TotalEdges: 0,
		Viewport: ViewportBounds{
			MinX: minX,
			MinY: minY,
			MaxX: maxX,
			MaxY: maxY,
		},
		EstimatedTime: int(totalNodes * estimatedMillisPerItem),
		ChunkSize:     chunkSize,
	}
}

func (h *GraphStreamHandler) streamNodes(
	ctx context.Context,
	c echo.Context,
	projectID string,
	minX, maxX, minY, maxY float64,
	chunkSize int,
	nodeIDs *[]string,
) error {
	offset := 0
	current := 0
	totalNodes, err := h.countViewportNodes(projectID, minX, maxX, minY, maxY)
	if err != nil {
		return h.sendError(c, "failed to count nodes: "+err.Error())
	}

	for {
		if err := checkStreamContext(ctx); err != nil {
			return err
		}

		items, err := h.fetchNodeChunk(projectID, minX, maxX, minY, maxY, chunkSize, offset)
		if err != nil {
			return h.sendError(c, "failed to query nodes: "+err.Error())
		}
		if len(items) == 0 {
			break
		}

		if err := h.sendNodeChunk(c, items, nodeIDs, &current, int(totalNodes)); err != nil {
			return err
		}
		flushStream(c)

		offset += chunkSize
	}

	return nil
}

func checkStreamContext(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	default:
		return nil
	}
}

func (h *GraphStreamHandler) fetchNodeChunk(
	projectID string,
	minX, maxX, minY, maxY float64,
	chunkSize int,
	offset int,
) ([]models.Item, error) {
	var items []models.Item
	result := h.db.Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Where("position_x BETWEEN ? AND ?", minX, maxX).
		Where("position_y BETWEEN ? AND ?", minY, maxY).
		Order("id").
		Limit(chunkSize).
		Offset(offset).
		Find(&items)

	return items, result.Error
}

func (h *GraphStreamHandler) sendNodeChunk(
	c echo.Context,
	items []models.Item,
	nodeIDs *[]string,
	current *int,
	total int,
) error {
	for _, item := range items {
		*nodeIDs = append(*nodeIDs, item.ID)
		*current++

		node := serializeNode(&item)
		if err := h.sendChunk(c, StreamChunk{
			Type: "node",
			Data: node,
			Progress: &ProgressInfo{
				Current:    *current,
				Total:      total,
				Percentage: float64(*current) / float64(total) * graphStreamPercentScale,
				Stage:      "nodes",
			},
			Timestamp: time.Now().UnixMilli(),
		}); err != nil {
			return err
		}
	}
	return nil
}

func flushStream(c echo.Context) {
	if flusher, ok := c.Response().Writer.(http.Flusher); ok {
		flusher.Flush()
	}
}

// streamEdges streams edges in chunks with progress updates
func (h *GraphStreamHandler) streamEdges(
	ctx context.Context,
	c echo.Context,
	nodeIDs []string,
	chunkSize int,
	totalEdges int,
) error {
	offset := 0
	current := 0

	for {
		batchCount, done, err := h.streamEdgeBatch(ctx, c, nodeIDs, chunkSize, offset, &current, totalEdges)
		if err != nil {
			return err
		}
		if done {
			break
		}
		offset += batchCount
	}

	return nil
}

func (h *GraphStreamHandler) streamEdgeBatch(
	ctx context.Context,
	c echo.Context,
	nodeIDs []string,
	chunkSize int,
	offset int,
	current *int,
	totalEdges int,
) (int, bool, error) {
	if err := checkStreamContext(ctx); err != nil {
		return 0, true, err
	}

	links, err := h.fetchEdgeBatch(nodeIDs, chunkSize, offset)
	if err != nil {
		return 0, true, h.sendError(c, "failed to query edges: "+err.Error())
	}

	if len(links) == 0 {
		return 0, true, nil
	}

	for _, link := range links {
		*current++
		if err := h.sendEdgeChunk(c, &link, *current, totalEdges); err != nil {
			return 0, true, err
		}
	}

	flushStream(c)

	return len(links), len(links) < chunkSize, nil
}

func (h *GraphStreamHandler) fetchEdgeBatch(
	nodeIDs []string,
	chunkSize int,
	offset int,
) ([]models.Link, error) {
	var links []models.Link
	result := h.db.Where("source_id IN ?", nodeIDs).
		Where("target_id IN ?", nodeIDs).
		Order("id").
		Limit(chunkSize).
		Offset(offset).
		Find(&links)
	if result.Error != nil {
		return nil, result.Error
	}
	return links, nil
}

func (h *GraphStreamHandler) sendEdgeChunk(
	c echo.Context,
	link *models.Link,
	current int,
	totalEdges int,
) error {
	edge := serializeEdge(link)
	return h.sendChunk(c, StreamChunk{
		Type: "edge",
		Data: edge,
		Progress: &ProgressInfo{
			Current:    current,
			Total:      totalEdges,
			Percentage: float64(current) / float64(totalEdges) * graphStreamPercentScale,
			Stage:      "edges",
		},
		Timestamp: time.Now().UnixMilli(),
	})
}

// sendChunk sends a single NDJSON chunk
func (h *GraphStreamHandler) sendChunk(c echo.Context, chunk StreamChunk) error {
	data, err := json.Marshal(chunk)
	if err != nil {
		return err
	}

	if _, err := c.Response().Write(append(data, '\n')); err != nil {
		return err
	}

	return nil
}

// sendError sends an error chunk
func (h *GraphStreamHandler) sendError(c echo.Context, message string) error {
	return h.sendChunk(c, StreamChunk{
		Type: "error",
		Data: map[string]string{
			"error": message,
		},
		Timestamp: time.Now().UnixMilli(),
	})
}

// StreamGraphPrefetch handles predictive prefetch for adjacent viewports
// POST /api/v1/projects/:project_id/graph/stream/prefetch
// @Summary Prefetch adjacent viewport data
// @Description Streams nodes from adjacent viewports based on pan direction for smooth navigation
// @Tags graph
// @Accept json
// @Produce application/x-ndjson
// @Param project_id path string true "Project ID"
// @Param request body PrefetchRequest true "Current viewport and pan direction"
// @Success 200 {string} string "NDJSON stream of prefetched chunks"
// @Failure 400 {object} map[string]string
// @Router /projects/{project_id}/graph/stream/prefetch [post]
func (h *GraphStreamHandler) StreamGraphPrefetch(c echo.Context) error {
	projectID := c.Param("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	var req PrefetchRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	// Calculate prefetch viewport based on direction
	prefetchViewport := h.calculatePrefetchViewport(req.CurrentViewport, req.Direction, req.Velocity)

	// Set response headers
	c.Response().Header().Set(echo.HeaderContentType, "application/x-ndjson")
	c.Response().Header().Set("Cache-Control", prefetchCacheControlHeader)
	c.Response().WriteHeader(http.StatusOK)

	// Stream prefetch data
	var nodeIDs []string
	chunkSize := prefetchChunkSize // Smaller chunks for prefetch

	if err := h.streamNodes(
		c.Request().Context(),
		c,
		projectID,
		prefetchViewport.MinX,
		prefetchViewport.MaxX,
		prefetchViewport.MinY,
		prefetchViewport.MaxY,
		chunkSize,
		&nodeIDs,
	); err != nil {
		return err
	}

	return nil
}

// PrefetchRequest represents a prefetch request
type PrefetchRequest struct {
	CurrentViewport ViewportBounds `json:"current_viewport"`
	Direction       string         `json:"direction"` // "north", "south", "east", "west", "northeast", etc.
	Velocity        float64        `json:"velocity"`  // pixels per second
}

type prefetchVector struct {
	dx       int
	dy       int
	diagonal bool
}

func (h *GraphStreamHandler) calculatePrefetchViewport(
	current ViewportBounds,
	direction string,
	velocity float64,
) ViewportBounds {
	width := current.MaxX - current.MinX
	height := current.MaxY - current.MinY

	vector, ok := prefetchVectorForDirection(direction)
	if !ok {
		return current
	}

	scale := calculatePrefetchScale(velocity)
	xScale, yScale := applyDiagonalScale(width*scale, height*scale, vector.diagonal)

	result := current
	result = applyPrefetchX(result, current, vector.dx, xScale)
	result = applyPrefetchY(result, current, vector.dy, yScale)

	return result
}

func applyDiagonalScale(xScale, yScale float64, diagonal bool) (float64, float64) {
	if !diagonal {
		return xScale, yScale
	}
	return xScale * prefetchDiagonalScaleFactor, yScale * prefetchDiagonalScaleFactor
}

func applyPrefetchX(result, current ViewportBounds, dx int, xScale float64) ViewportBounds {
	if dx > 0 {
		result.MinX = current.MaxX
		result.MaxX = current.MaxX + xScale
	} else if dx < 0 {
		result.MaxX = current.MinX
		result.MinX = current.MinX - xScale
	}
	return result
}

func applyPrefetchY(result, current ViewportBounds, dy int, yScale float64) ViewportBounds {
	if dy > 0 {
		result.MinY = current.MaxY
		result.MaxY = current.MaxY + yScale
	} else if dy < 0 {
		result.MaxY = current.MinY
		result.MinY = current.MinY - yScale
	}
	return result
}

func prefetchVectorForDirection(direction string) (prefetchVector, bool) {
	switch direction {
	case "north":
		return prefetchVector{dx: 0, dy: -1}, true
	case "south":
		return prefetchVector{dx: 0, dy: 1}, true
	case "east":
		return prefetchVector{dx: 1, dy: 0}, true
	case "west":
		return prefetchVector{dx: -1, dy: 0}, true
	case "northeast":
		return prefetchVector{dx: 1, dy: -1, diagonal: true}, true
	case "northwest":
		return prefetchVector{dx: -1, dy: -1, diagonal: true}, true
	case "southeast":
		return prefetchVector{dx: 1, dy: 1, diagonal: true}, true
	case "southwest":
		return prefetchVector{dx: -1, dy: 1, diagonal: true}, true
	default:
		return prefetchVector{}, false
	}
}

func calculatePrefetchScale(velocity float64) float64 {
	if velocity <= 0 {
		return 1.0
	}

	scale := 1.0 + (velocity / prefetchVelocityScaleDivisor) // Up to 2x for high velocity
	if scale > prefetchScaleCap {
		return prefetchScaleCap
	}
	return scale
}

// GetStreamStats returns statistics about streaming performance
// GET /api/v1/projects/:project_id/graph/stream/stats
// @Summary Get stream statistics
// @Description Returns statistics for estimating stream performance
// @Tags graph
// @Produce json
// @Param project_id path string true "Project ID"
// @Success 200 {object} map[string]interface{}
// @Router /projects/{project_id}/graph/stream/stats [get]
func (h *GraphStreamHandler) GetStreamStats(c echo.Context) error {
	projectID := c.Param("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "project_id is required"})
	}

	var totalNodes int64
	var totalEdges int64

	h.db.Model(&models.Item{}).
		Where("project_id = ?", projectID).
		Where("deleted_at IS NULL").
		Count(&totalNodes)

	h.db.Model(&models.Link{}).
		Joins("JOIN items ON links.source_id = items.id").
		Where("items.project_id = ?", projectID).
		Count(&totalEdges)

	avgNodeSize := estimatedNodeSizeBytes // bytes
	avgEdgeSize := estimatedEdgeSizeBytes // bytes
	estimatedBytes := (int(totalNodes) * avgNodeSize) + (int(totalEdges) * avgEdgeSize)

	return c.JSON(http.StatusOK, map[string]interface{}{
		"projectId":       projectID,
		"totalNodes":      totalNodes,
		"totalEdges":      totalEdges,
		"estimatedBytes":  estimatedBytes,
		"estimatedTimeMs": (totalNodes + totalEdges) * estimatedMillisPerItem, // ~2ms per item
		"recommendedChunkSize": func() int {
			if totalNodes < recommendedChunkSmallThreshold {
				return recommendedChunkSmallSize
			} else if totalNodes < recommendedChunkMediumThreshold {
				return recommendedChunkMediumSize
			}
			return recommendedChunkLargeSize
		}(),
	})
}
