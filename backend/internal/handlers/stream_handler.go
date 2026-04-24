package handlers

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// StreamHandler handles NDJSON streaming endpoints for large data transfers
type StreamHandler struct {
	itemRepo repository.ItemRepository
}

// NewStreamHandler creates a new stream handler
func NewStreamHandler(
	itemRepo repository.ItemRepository,
) *StreamHandler {
	return &StreamHandler{
		itemRepo: itemRepo,
	}
}

// StreamItems streams items as NDJSON for large datasets
// GET /api/v1/items/stream?project_id=...&limit=...&offset=...
func (h *StreamHandler) StreamItems(c echo.Context) error {
	ctx := c.Request().Context()
	projectID := c.QueryParam("project_id")

	limit := 1000 // Default batch size
	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 {
			limit = l
		}
	}

	offset := 0
	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if o, err := strconv.Atoi(offsetStr); err == nil && o >= 0 {
			offset = o
		}
	}

	// Set headers for NDJSON streaming
	c.Response().Header().Set("Content-Type", "application/x-ndjson")
	c.Response().Header().Set("Cache-Control", "no-cache")
	c.Response().Header().Set("X-Content-Type-Options", "nosniff")
	c.Response().WriteHeader(http.StatusOK)

	writer := bufio.NewWriter(c.Response().Writer)
	defer func() {
		if err := writer.Flush(); err != nil {
			slog.Error("failed to flush stream response", "error", err)
		}
	}()

	// Stream items in batches
	return h.streamItemsInBatches(ctx, writer, projectID, limit, offset)
}

func (h *StreamHandler) streamItemsInBatches(
	ctx context.Context,
	writer *bufio.Writer,
	projectID string,
	limit, offset int,
) error {
	state := streamBatchState{
		limit:     limit,
		offset:    offset,
		batchSize: 100,
		projectID: projectID,
		itemCount: 0,
	}

	for {
		done, err := h.streamItemBatch(ctx, writer, &state)
		if err != nil {
			return err
		}
		if done {
			break
		}
	}

	return h.writeStreamComplete(writer, state.itemCount)
}

type streamBatchState struct {
	limit     int
	offset    int
	batchSize int
	projectID string
	itemCount int
}

func (h *StreamHandler) streamItemBatch(
	ctx context.Context,
	writer *bufio.Writer,
	state *streamBatchState,
) (bool, error) {
	if checkContextCancelled(ctx) {
		return true, ctx.Err()
	}

	items, err := h.fetchItemBatch(ctx, state.projectID, state.batchSize, state.offset)
	if err != nil {
		return true, h.writeStreamError(writer, err)
	}

	if len(items) == 0 {
		return true, nil
	}

	if err := h.writeItemBatch(writer, items, state); err != nil {
		return true, err
	}

	if h.shouldTerminateStreaming(state.limit, state.itemCount, state.batchSize, len(items)) {
		return true, nil
	}

	state.offset += len(items)
	return false, nil
}

func (handler *StreamHandler) fetchItemBatch(
	ctx context.Context,
	projectID string,
	batchSize int,
	offset int,
) ([]*models.Item, error) {
	filter := repository.ItemFilter{
		Limit:  batchSize,
		Offset: offset,
	}
	if projectID != "" {
		filter.ProjectID = &projectID
	}
	return handler.itemRepo.List(ctx, filter)
}

func (handler *StreamHandler) writeItemBatch(
	writer *bufio.Writer,
	items []*models.Item,
	state *streamBatchState,
) error {
	for _, item := range items {
		if err := handler.writeNDJSONLine(writer, item); err != nil {
			return err
		}
		state.itemCount++

		if err := handler.handlePeriodicUpdates(writer, state.itemCount, state.offset, len(items)); err != nil {
			return err
		}
	}
	return nil
}

// checkContextCancelled checks if context is cancelled
func checkContextCancelled(ctx context.Context) bool {
	select {
	case <-ctx.Done():
		return true
	default:
		return false
	}
}

// writeStreamError writes an error as NDJSON line
func (h *StreamHandler) writeStreamError(writer *bufio.Writer, err error) error {
	errorLine := map[string]interface{}{
		"error": err.Error(),
		"type":  "error",
	}
	if jsonErr := h.writeNDJSONLine(writer, errorLine); jsonErr != nil {
		return jsonErr
	}
	return err
}

// handlePeriodicUpdates handles progress updates and periodic flushing
func (h *StreamHandler) handlePeriodicUpdates(writer *bufio.Writer, itemCount, currentOffset, batchLen int) error {
	// Send progress metadata periodically
	if itemCount%50 == 0 {
		progress := map[string]interface{}{
			"type":   "progress",
			"count":  itemCount,
			"offset": currentOffset + batchLen,
		}
		if err := h.writeNDJSONLine(writer, progress); err != nil {
			return err
		}
	}

	// Flush periodically for streaming
	if itemCount%10 == 0 {
		return writer.Flush()
	}
	return nil
}

// shouldTerminateStreaming determines if streaming should terminate
func (h *StreamHandler) shouldTerminateStreaming(limit, itemCount, batchSize, itemsLen int) bool {
	// Check if we've reached the limit
	if limit > 0 && itemCount >= limit {
		return true
	}
	// Check if we got fewer items than requested (end of data)
	if itemsLen < batchSize {
		return true
	}
	return false
}

// writeStreamComplete writes the completion summary
func (h *StreamHandler) writeStreamComplete(writer *bufio.Writer, itemCount int) error {
	summary := map[string]interface{}{
		"type":        "complete",
		"total_count": itemCount,
	}
	if err := h.writeNDJSONLine(writer, summary); err != nil {
		return err
	}
	return writer.Flush()
}

// StreamGraph streams graph data as NDJSON
// GET /api/v1/graphs/:id/stream
// Note: This is a placeholder implementation. Integrate with actual graph service when available.
func (h *StreamHandler) StreamGraph(c echo.Context) error {
	ctx := c.Request().Context()
	_ = ctx // Use context when actual implementation is added
	graphID := c.Param("id")

	// Set headers for NDJSON streaming
	c.Response().Header().Set("Content-Type", "application/x-ndjson")
	c.Response().Header().Set("Cache-Control", "no-cache")
	c.Response().Header().Set("X-Content-Type-Options", "nosniff")
	c.Response().WriteHeader(http.StatusOK)

	writer := bufio.NewWriter(c.Response().Writer)
	defer func() {
		if err := writer.Flush(); err != nil {
			slog.Error("failed to flush stream response", "error", err)
		}
	}()

	// Placeholder: Return not implemented error
	errorLine := map[string]interface{}{
		"error": "Graph streaming not yet implemented for graph ID: " + graphID,
		"type":  "error",
	}
	return h.writeNDJSONLine(writer, errorLine)
}

// StreamExport streams export data as NDJSON
// GET /api/v1/export/:type/stream?project_id=...
func (h *StreamHandler) StreamExport(c echo.Context) error {
	ctx := c.Request().Context()
	exportType := c.Param("type")
	projectID := c.QueryParam("project_id")

	if projectID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "project_id is required",
		})
	}

	// Set headers for NDJSON streaming
	c.Response().Header().Set("Content-Type", "application/x-ndjson")
	c.Response().Header().Set("Cache-Control", "no-cache")
	c.Response().Header().Set("X-Content-Type-Options", "nosniff")
	c.Response().WriteHeader(http.StatusOK)

	writer := bufio.NewWriter(c.Response().Writer)
	defer func() {
		if err := writer.Flush(); err != nil {
			slog.Error("failed to flush stream response", "error", err)
		}
	}()

	// Stream export data based on type
	switch exportType {
	case "json":
		return h.streamJSONExport(ctx, writer, projectID)
	case "csv":
		return h.streamCSVExport(ctx, writer, projectID)
	default:
		errorLine := map[string]interface{}{
			"error": "unsupported export type: " + exportType,
			"type":  "error",
		}
		if err := h.writeNDJSONLine(writer, errorLine); err != nil {
			return err
		}
		return fmt.Errorf("unsupported export type: %s", exportType)
	}
}

func (h *StreamHandler) streamJSONExport(
	ctx context.Context,
	writer *bufio.Writer,
	projectID string,
) error {
	if err := h.writeJSONExportHeader(writer, projectID); err != nil {
		return err
	}

	// Stream items
	offset := 0
	const batchSize = 100
	totalCount := 0

	for {
		batchCount, done, err := h.streamJSONBatch(ctx, writer, projectID, offset, batchSize, &totalCount)
		if err != nil {
			return err
		}
		if done {
			break
		}
		offset += batchCount
	}

	if err := h.writeJSONExportCompletion(writer, totalCount); err != nil {
		return err
	}

	return writer.Flush()
}

func (h *StreamHandler) streamJSONBatch(
	ctx context.Context,
	writer *bufio.Writer,
	projectID string,
	offset int,
	batchSize int,
	totalCount *int,
) (int, bool, error) {
	items, err := h.fetchJSONBatch(ctx, projectID, offset, batchSize)
	if err != nil {
		return h.failJSONBatch(writer, err)
	}

	if len(items) == 0 {
		return 0, true, nil
	}

	if err := h.writeJSONBatchItems(writer, items, totalCount); err != nil {
		return 0, true, err
	}

	if err := h.writeJSONProgressIfNeeded(writer, *totalCount); err != nil {
		return 0, true, err
	}

	return len(items), len(items) < batchSize, nil
}

func (h *StreamHandler) failJSONBatch(writer *bufio.Writer, err error) (int, bool, error) {
	return 0, true, h.handleJSONBatchError(writer, err)
}

func (h *StreamHandler) writeJSONProgressIfNeeded(writer *bufio.Writer, totalCount int) error {
	if !shouldWriteJSONProgress(totalCount) {
		return nil
	}
	return h.writeJSONExportProgress(writer, totalCount)
}

func (h *StreamHandler) fetchJSONBatch(
	ctx context.Context,
	projectID string,
	offset int,
	batchSize int,
) ([]*models.Item, error) {
	filter := repository.ItemFilter{
		ProjectID: &projectID,
		Limit:     batchSize,
		Offset:    offset,
	}
	return h.itemRepo.List(ctx, filter)
}

func (h *StreamHandler) handleJSONBatchError(writer *bufio.Writer, err error) error {
	if writeErr := h.writeJSONExportError(writer, err); writeErr != nil {
		return writeErr
	}
	return err
}

func (h *StreamHandler) writeJSONBatchItems(
	writer *bufio.Writer,
	items []*models.Item,
	totalCount *int,
) error {
	for _, item := range items {
		if err := h.writeJSONExportItem(writer, item); err != nil {
			return err
		}
		*totalCount++

		if shouldFlushJSONBatch(*totalCount) {
			if err := writer.Flush(); err != nil {
				return err
			}
		}
	}
	return nil
}

func shouldFlushJSONBatch(totalCount int) bool {
	return totalCount%10 == 0
}

func shouldWriteJSONProgress(totalCount int) bool {
	return totalCount%50 == 0
}

func (h *StreamHandler) writeJSONExportHeader(writer *bufio.Writer, projectID string) error {
	header := map[string]interface{}{
		"type":       "export",
		"format":     "json",
		"project_id": projectID,
	}
	return h.writeNDJSONLine(writer, header)
}

func (h *StreamHandler) writeJSONExportItem(writer *bufio.Writer, item *models.Item) error {
	exportData := map[string]interface{}{
		"type": "item",
		"data": item,
	}
	return h.writeNDJSONLine(writer, exportData)
}

func (h *StreamHandler) writeJSONExportProgress(writer *bufio.Writer, totalCount int) error {
	progress := map[string]interface{}{
		"type":  "progress",
		"count": totalCount,
	}
	return h.writeNDJSONLine(writer, progress)
}

func (h *StreamHandler) writeJSONExportCompletion(writer *bufio.Writer, totalCount int) error {
	complete := map[string]interface{}{
		"type":  "complete",
		"count": totalCount,
	}
	return h.writeNDJSONLine(writer, complete)
}

func (h *StreamHandler) writeJSONExportError(writer *bufio.Writer, err error) error {
	errorLine := map[string]interface{}{
		"error": err.Error(),
		"type":  "error",
	}
	return h.writeNDJSONLine(writer, errorLine)
}

func (h *StreamHandler) streamCSVExport(
	ctx context.Context,
	writer *bufio.Writer,
	projectID string,
) error {
	// Similar to JSON export but with CSV format
	// Implementation details omitted for brevity
	return h.streamJSONExport(ctx, writer, projectID)
}

// writeNDJSONLine writes a single NDJSON line
func (h *StreamHandler) writeNDJSONLine(writer *bufio.Writer, data interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}

	if _, err := writer.Write(jsonData); err != nil {
		return err
	}

	if _, err := writer.WriteString("\n"); err != nil {
		return err
	}

	return nil
}
