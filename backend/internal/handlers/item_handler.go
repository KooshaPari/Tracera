package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"math"
	"net/http"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/labstack/echo/v4"
	"gorm.io/datatypes"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/pagination"
	"github.com/kooshapari/tracertm-backend/internal/realtime"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// ItemHandler handles HTTP requests for item operations.
type ItemHandler struct {
	itemService         services.ItemService // Service layer for operations - REQUIRED
	cache               cache.Cache
	publisher           *nats.EventPublisher
	realtimeBroadcaster interface{} // realtime.Broadcaster
	authProvider        interface{} // auth.Provider
	binder              RequestBinder
}

const (
	itemDefaultPriority  = 50
	cursorDefaultOffset  = 0
	cursorDefaultLimit   = 50
	cursorMaxLimit       = 100
	listDefaultLimit     = 100
	listMaxLimit         = 100
	listDefaultOffset    = 0
	priorityLowValue     = 1
	priorityMediumValue  = 2
	priorityHighValue    = 3
	pivotDefaultMaxDepth = 1
)

// NewItemHandler constructs an ItemHandler with its dependencies.
func NewItemHandler(
	cacheImpl cache.Cache,
	eventPublisher *nats.EventPublisher,
	realtimeBroadcaster interface{},
	authProvider interface{},
	binder RequestBinder,
) *ItemHandler {
	return &ItemHandler{
		itemService:         nil, // Will be set via SetItemService - REQUIRED
		cache:               cacheImpl,
		publisher:           eventPublisher,
		realtimeBroadcaster: realtimeBroadcaster,
		authProvider:        authProvider,
		binder:              binder,
	}
}

// SetItemService sets the ItemService for GET operations
// This allows optional use of service layer when available
func (h *ItemHandler) SetItemService(itemService services.ItemService) {
	h.itemService = itemService
}

// CreateItem handles POST requests to create an item.
func (h *ItemHandler) CreateItem(echoCtx echo.Context) error {
	if h.itemService == nil {
		return echo.NewHTTPError(http.StatusServiceUnavailable, "ItemService not available")
	}

	var req struct {
		ProjectID   string          `json:"project_id"`
		Title       string          `json:"title"`
		Description string          `json:"description"`
		Type        string          `json:"type"`
		Status      string          `json:"status"`
		Priority    *int            `json:"priority"`
		Metadata    json.RawMessage `json:"metadata"`
	}
	if err := h.binder.Bind(echoCtx, &req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	// Validate project_id format
	projectID, err := uuidutil.StringToUUID(req.ProjectID)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid project_id"})
	}

	// Service layer path ONLY
	return h.createItemWithService(echoCtx, req, projectID.String())
}

// createItemWithService uses ItemService for creation (service layer path)
func (h *ItemHandler) createItemWithService(c echo.Context, req struct {
	ProjectID   string          `json:"project_id"`
	Title       string          `json:"title"`
	Description string          `json:"description"`
	Type        string          `json:"type"`
	Status      string          `json:"status"`
	Priority    *int            `json:"priority"`
	Metadata    json.RawMessage `json:"metadata"`
}, projectID string,
) error {
	// Convert request to service model
	metadata := datatypes.JSON([]byte("{}"))
	if req.Metadata != nil {
		metadata = datatypes.JSON(req.Metadata)
	}

	item := &models.Item{
		ProjectID:   projectID,
		Title:       req.Title,
		Description: req.Description,
		Type:        req.Type,
		Status:      req.Status,
		Priority:    formatPriorityForService(req.Priority),
		Metadata:    metadata,
	}

	// Create item via service (handles validation, events, caching)
	if err := h.itemService.CreateItem(c.Request().Context(), item); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Convert service model back to db.Item format for consistent API response
	dbItem := h.modelItemToGetItemRow(item)
	return c.JSON(http.StatusCreated, dbItem)
}

// formatPriorityForService converts priority int pointer to models.Priority for service layer
func formatPriorityForService(priority *int) models.Priority {
	if priority == nil {
		return models.Priority(itemDefaultPriority) // default (schema default)
	}
	val := *priority
	if val > math.MaxInt32 {
		val = math.MaxInt32
	} else if val < math.MinInt32 {
		val = math.MinInt32
	}
	return models.Priority(int32(val)) //nolint:gosec // G115: val is bounds-checked above
}

// ListItems handles GET requests to list items.
func (h *ItemHandler) ListItems(c echo.Context) error {
	if h.itemService == nil {
		return echo.NewHTTPError(http.StatusServiceUnavailable, "ItemService not available")
	}

	projectIDPtr, err := parseProjectIDParam(c)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	paginationOpts, err := parseListItemsPagination(c)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	filter := repository.ItemFilter{
		ProjectID: projectIDPtr,
		Limit:     paginationOpts.limit,
		Offset:    paginationOpts.offset,
		Cursor:    paginationOpts.cursor,
		UseCursor: paginationOpts.useCursor,
	}

	serviceItems, err := h.itemService.ListItems(c.Request().Context(), filter)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	dbItems := h.toListItemsResponse(serviceItems)
	response := buildListItemsResponse(serviceItems, dbItems, paginationOpts)

	return c.JSON(http.StatusOK, response)
}

type listItemsPagination struct {
	limit     int
	offset    int
	cursor    *string
	useCursor bool
}

func parseProjectIDParam(c echo.Context) (*string, error) {
	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return nil, errors.New("project_id is required")
	}

	if _, err := uuidutil.StringToUUID(projectIDStr); err != nil {
		return nil, errors.New("invalid project_id")
	}

	return &projectIDStr, nil
}

func parseListItemsPagination(c echo.Context) (listItemsPagination, error) {
	cursorStr := c.QueryParam("cursor")
	limitStr := c.QueryParam("limit")
	offsetStr := c.QueryParam("offset")

	paginationOpts := listItemsPagination{
		limit:     listDefaultLimit,
		offset:    listDefaultOffset,
		useCursor: cursorStr != "",
	}

	if paginationOpts.useCursor {
		cursor, limit, err := parseCursorPagination(cursorStr)
		if err != nil {
			return paginationOpts, err
		}
		paginationOpts.cursor = &cursor
		if limitStr == "" {
			limitStr = strconv.Itoa(limit)
		}
	}

	paginationOpts.limit = parseListLimit(limitStr, paginationOpts.limit)
	paginationOpts.offset = parseListOffset(offsetStr, paginationOpts.offset, paginationOpts.useCursor)

	return paginationOpts, nil
}

func parseCursorPagination(cursorStr string) (string, int, error) {
	cursor, limit, err := pagination.ParseCursorPaginationParams(
		cursorStr,
		cursorDefaultOffset,
		cursorDefaultLimit,
		cursorMaxLimit,
	)
	if err != nil {
		return "", 0, fmt.Errorf("invalid cursor: %w", err)
	}
	return cursor, limit, nil
}

func parseListLimit(limitStr string, defaultLimit int) int {
	if limitStr == "" {
		return defaultLimit
	}
	parsed, err := strconv.Atoi(limitStr)
	if err != nil || parsed <= 0 {
		return defaultLimit
	}
	if parsed > listMaxLimit {
		return listMaxLimit
	}
	return parsed
}

func parseListOffset(offsetStr string, defaultOffset int, useCursor bool) int {
	if useCursor || offsetStr == "" {
		return defaultOffset
	}
	parsed, err := strconv.Atoi(offsetStr)
	if err != nil || parsed < 0 {
		return defaultOffset
	}
	return parsed
}

func (h *ItemHandler) toListItemsResponse(serviceItems []*models.Item) []db.ListItemsByProjectRow {
	dbItems := make([]db.ListItemsByProjectRow, len(serviceItems))
	for i, item := range serviceItems {
		itemRow := h.modelItemToGetItemRow(item)
		dbItems[i] = db.ListItemsByProjectRow(itemRow)
	}
	return dbItems
}

func buildListItemsResponse(
	serviceItems []*models.Item,
	dbItems []db.ListItemsByProjectRow,
	paginationOpts listItemsPagination,
) map[string]interface{} {
	response := map[string]interface{}{
		"items": dbItems,
	}

	if paginationOpts.useCursor {
		nextCursor, hasMore := buildCursorMetadata(serviceItems, paginationOpts.limit)
		response["next_cursor"] = nextCursor
		response["has_more"] = hasMore
		response["count"] = len(serviceItems)
	}

	return response
}

func buildCursorMetadata(serviceItems []*models.Item, limit int) (string, bool) {
	hasMore := len(serviceItems) >= limit
	if !hasMore || len(serviceItems) == 0 {
		return "", hasMore
	}

	lastItem := serviceItems[len(serviceItems)-1]
	return pagination.EncodeCursor(lastItem.ID, lastItem.CreatedAt), hasMore
}

// GetItem handles GET requests to fetch a single item.
func (handler *ItemHandler) GetItem(echoCtx echo.Context) error {
	if handler.itemService == nil {
		return echo.NewHTTPError(http.StatusServiceUnavailable, "ItemService not available")
	}

	idStr := echoCtx.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid item ID"})
	}

	// Service layer path ONLY - ItemService handles caching internally
	serviceItem, err := handler.itemService.GetItem(echoCtx.Request().Context(), idStr)
	if err != nil {
		return echoCtx.JSON(http.StatusNotFound, map[string]string{"error": "Item not found"})
	}
	// Convert models.Item to db.Item for backward compatibility
	dbItem := handler.modelItemToGetItemRow(serviceItem)
	return echoCtx.JSON(http.StatusOK, dbItem)
}

// UpdateItem handles PATCH/PUT requests to update an item.
func (h *ItemHandler) UpdateItem(c echo.Context) error {
	if h.itemService == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]string{"error": "ItemService not available"})
	}

	item, err := h.buildUpdatedItemFromRequest(c)
	if err != nil {
		var he *echo.HTTPError
		if errors.As(err, &he) {
			return c.JSON(he.Code, he.Message)
		}
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	// Call service (handles validation, caching, and events)
	if err := h.itemService.UpdateItem(c.Request().Context(), item); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Broadcast via realtime (service doesn't handle realtime)
	if h.realtimeBroadcaster != nil {
		go h.broadcastItemEvent(c.Request().Context(), "updated", item.ID)
	}

	return h.respondWithUpdatedItem(c, item.ID)
}

type updateItemRequest struct {
	Title       string          `json:"title"`
	Description string          `json:"description"`
	Type        string          `json:"type"`
	Status      string          `json:"status"`
	Priority    *int            `json:"priority"`
	Metadata    json.RawMessage `json:"metadata"`
}

func (h *ItemHandler) buildUpdatedItemFromRequest(c echo.Context) (*models.Item, error) {
	idStr := c.Param("id")
	if _, err := uuidutil.StringToUUID(idStr); err != nil {
		return nil, echo.NewHTTPError(http.StatusBadRequest, map[string]string{"error": "Invalid item ID"})
	}

	req, err := h.parseUpdateItemRequest(c)
	if err != nil {
		return nil, err
	}

	existingItem, err := h.itemService.GetItem(c.Request().Context(), idStr)
	if err != nil {
		return nil, echo.NewHTTPError(http.StatusNotFound, map[string]string{"error": "Item not found"})
	}

	priority := resolvePriority(existingItem.Priority, req.Priority)
	item := &models.Item{
		ID:          idStr,
		ProjectID:   existingItem.ProjectID,
		Title:       req.Title,
		Description: req.Description,
		Type:        req.Type,
		Status:      req.Status,
		Priority:    priority,
	}

	return item, nil
}

func (h *ItemHandler) parseUpdateItemRequest(c echo.Context) (updateItemRequest, error) {
	var req updateItemRequest
	if err := h.binder.Bind(c, &req); err != nil {
		return req, echo.NewHTTPError(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	return req, nil
}

func resolvePriority(existing models.Priority, requested *int) models.Priority {
	if requested == nil {
		return existing
	}

	switch *requested {
	case priorityLowValue:
		return models.PriorityLow
	case priorityMediumValue:
		return models.PriorityMedium
	case priorityHighValue:
		return models.PriorityHigh
	default:
		return models.PriorityMedium
	}
}

func (h *ItemHandler) respondWithUpdatedItem(c echo.Context, idStr string) error {
	updatedItem, err := h.itemService.GetItem(c.Request().Context(), idStr)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Item updated but failed to retrieve"})
	}

	dbItem := h.modelItemToGetItemRow(updatedItem)
	return c.JSON(http.StatusOK, dbItem)
}

// DeleteItem handles DELETE requests to remove an item.
func (handler *ItemHandler) DeleteItem(c echo.Context) error {
	if handler.itemService == nil {
		return echo.NewHTTPError(http.StatusServiceUnavailable, "ItemService not available")
	}

	idStr := c.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid item ID"})
	}

	// Service layer path ONLY - handles validation, link deletion, caching, and events
	if err := handler.itemService.DeleteItem(c.Request().Context(), idStr); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Broadcast via realtime (service doesn't handle realtime)
	if handler.realtimeBroadcaster != nil {
		go handler.broadcastItemEvent(c.Request().Context(), "deleted", idStr)
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Item deleted"})
}

// Helper methods for realtime events

// broadcastItemEvent broadcasts an item event via realtime
func (h *ItemHandler) broadcastItemEvent(ctx context.Context, eventType string, itemID string) {
	if h.realtimeBroadcaster == nil {
		return
	}

	broadcaster, ok := h.realtimeBroadcaster.(realtime.Broadcaster)
	if !ok {
		slog.Info("Invalid realtime broadcaster type")
		return
	}

	event := &realtime.Event{
		Type:      eventType,
		Table:     "items",
		Schema:    "public",
		Record:    map[string]interface{}{"id": itemID},
		Timestamp: time.Now().Unix(),
	}

	if err := broadcaster.Publish(ctx, event); err != nil {
		slog.Error("Failed to broadcast item event", "error", err)
	}
}

// ============================================================================
// PIVOT NAVIGATION ENDPOINT
// ============================================================================

// PivotNavigationRequest represents a request to get equivalent items for pivot navigation
type PivotNavigationRequest struct {
	Perspectives       []string `json:"perspectives,omitempty"`
	MaxDepth           int      `json:"max_depth,omitempty"`
	IncludeMetadata    bool     `json:"include_metadata,omitempty"`
	GroupByPerspective bool     `json:"group_by_perspective,omitempty"`
}

// PivotNavigationResponse contains equivalent items grouped by perspective
type PivotNavigationResponse struct {
	SourceItemID             string                 `json:"source_item_id"`
	SourceItem               *PivotItemInfo         `json:"source_item,omitempty"`
	EquivalentsByPerspective map[string][]PivotItem `json:"equivalents_by_perspective"`
	AllEquivalents           []PivotItem            `json:"all_equivalents"`
	CanonicalConcept         *CanonicalConceptInfo  `json:"canonical_concept,omitempty"`
	LinkCount                int                    `json:"link_count"`
	PerspectiveCount         int                    `json:"perspective_count"`
}

// PivotItem represents an equivalent item in pivot navigation
type PivotItem struct {
	ItemID             string         `json:"item_id"`
	Title              string         `json:"title"`
	ItemType           string         `json:"item_type"`
	Perspective        string         `json:"perspective"`
	LinkType           string         `json:"link_type"`
	Confidence         float64        `json:"confidence"`
	Status             string         `json:"status"`
	Item               *PivotItemInfo `json:"item,omitempty"`
	RelatedCanonicalID *string        `json:"related_canonical_id,omitempty"`
	PathDepth          int            `json:"path_depth"`
}

// PivotItemInfo contains basic information about an item
type PivotItemInfo struct {
	ID          string                 `json:"id"`
	ProjectID   string                 `json:"project_id"`
	Title       string                 `json:"title"`
	Description string                 `json:"description,omitempty"`
	ItemType    string                 `json:"item_type"`
	Status      string                 `json:"status"`
	Priority    *int                   `json:"priority,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
}

// CanonicalConceptInfo contains basic information about a canonical concept
type CanonicalConceptInfo struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description,omitempty"`
	Domain      string   `json:"domain,omitempty"`
	Category    string   `json:"category,omitempty"`
	Tags        []string `json:"tags,omitempty"`
}

// PivotNavigation handles POST /items/:id/pivot
// @Summary Get equivalent items for pivot navigation
// @Description Returns items equivalent to a source item, grouped by perspective
// @Tags items
// @Accept json
// @Produce json
// @Param id path string true "Item ID to pivot from"
// @Param body body PivotNavigationRequest true "Pivot navigation options"
// @Success 200 {object} PivotNavigationResponse "Equivalent items grouped by perspective"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Item not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /items/{id}/pivot [post]
// PivotNavigation handles requests to navigate pivot views for an item.
func (h *ItemHandler) PivotNavigation(echoCtx echo.Context) error {
	if h.itemService == nil {
		return echo.NewHTTPError(http.StatusServiceUnavailable, "ItemService not available")
	}

	idStr := echoCtx.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid item ID"})
	}

	var req PivotNavigationRequest
	if err := h.binder.Bind(echoCtx, &req); err != nil {
		// Use defaults if binding fails
		req = PivotNavigationRequest{
			Perspectives:       nil,
			MaxDepth:           pivotDefaultMaxDepth,
			IncludeMetadata:    false,
			GroupByPerspective: true,
		}
	}

	// Service layer path ONLY
	serviceItem, err := h.itemService.GetItem(echoCtx.Request().Context(), idStr)
	if err != nil {
		return echoCtx.JSON(http.StatusNotFound, map[string]string{"error": "Item not found"})
	}
	item := h.modelItemToGetItemRow(serviceItem)

	// Build source item info
	var sourceItem *PivotItemInfo
	if req.IncludeMetadata {
		priority := (*int)(nil)
		if item.Priority.Valid {
			p := int(item.Priority.Int32)
			priority = &p
		}
		sourceItem = &PivotItemInfo{
			ID:          item.ID.String(),
			ProjectID:   item.ProjectID.String(),
			Title:       item.Title,
			Description: item.Description.String,
			ItemType:    item.Type,
			Status:      item.Status,
			Priority:    priority,
			CreatedAt:   item.CreatedAt.Time,
			UpdatedAt:   item.UpdatedAt.Time,
		}
	}

	// Note: Equivalence lookup via equivalence service not yet implemented
	// Return empty equivalences with the source item info
	response := PivotNavigationResponse{
		SourceItemID:             idStr,
		SourceItem:               sourceItem,
		EquivalentsByPerspective: make(map[string][]PivotItem),
		AllEquivalents:           []PivotItem{},
		CanonicalConcept:         nil,
		LinkCount:                0,
		PerspectiveCount:         0,
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// GetPivotTargets handles GET /items/:id/pivot-targets
// @Summary Get pivot target information for an item
// @Description Returns item information needed for pivot navigation including type and available perspectives
// @Tags items
// @Produce json
// @Param id path string true "Item ID"
// @Success 200 {object} PivotTargetsResponse "Pivot target information"
// @Failure 400 {object} ErrorResponse "Invalid item ID"
// @Failure 404 {object} ErrorResponse "Item not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /items/{id}/pivot-targets [get]
// GetPivotTargets handles requests to resolve pivot targets.
func (h *ItemHandler) GetPivotTargets(c echo.Context) error {
	if h.itemService == nil {
		return echo.NewHTTPError(http.StatusServiceUnavailable, "ItemService not available")
	}

	idStr := c.Param("id")
	_, err := uuidutil.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid item ID"})
	}

	// Service layer path ONLY
	serviceItem, err := h.itemService.GetItem(c.Request().Context(), idStr)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Item not found"})
	}
	item := h.modelItemToGetItemRow(serviceItem)

	// Build response with item info and empty targets
	// Note: Perspectives and targets population from equivalence service not yet implemented
	response := PivotTargetsResponse{
		ItemID:       idStr,
		ItemType:     item.Type,
		Title:        item.Title,
		Status:       item.Status,
		Perspectives: []string{},
		Targets:      []PivotTarget{},
	}

	return c.JSON(http.StatusOK, response)
}

// PivotTargetsResponse represents the response for pivot targets endpoint
type PivotTargetsResponse struct {
	ItemID       string        `json:"item_id"`
	ItemType     string        `json:"item_type"`
	Title        string        `json:"title"`
	Status       string        `json:"status"`
	Perspectives []string      `json:"perspectives"`
	Targets      []PivotTarget `json:"targets"`
}

// PivotTarget represents a single pivot target
type PivotTarget struct {
	ItemID      string  `json:"item_id"`
	Title       string  `json:"title"`
	ItemType    string  `json:"item_type"`
	Perspective string  `json:"perspective"`
	Confidence  float64 `json:"confidence"`
}

// ============================================================================
// MODEL CONVERSION HELPERS
// ============================================================================

// modelItemToGetItemRow converts models.Item (from service layer) to db.Item (for API response)
// This maintains backward compatibility while allowing gradual migration to service layer
func (h *ItemHandler) modelItemToGetItemRow(item *models.Item) db.GetItemRow {
	if item == nil {
		return db.GetItemRow{}
	}

	// Convert UUID strings to pgtype.UUID
	var itemID, projectID pgtype.UUID
	itemUUID, err := uuid.Parse(item.ID)
	if err != nil {
		slog.Error("Warning: Failed to parse item ID", "error", err)
	} else {
		itemID = pgtype.UUID{Bytes: itemUUID, Valid: true}
	}

	projectUUID, err := uuid.Parse(item.ProjectID)
	if err != nil {
		slog.Error("Warning: Failed to parse project ID", "error", err)
	} else {
		projectID = pgtype.UUID{Bytes: projectUUID, Valid: true}
	}

	// Convert description to pgtype.Text
	description := pgtype.Text{
		String: item.Description,
		Valid:  item.Description != "",
	}

	// Convert priority (int32) to pgtype.Int4
	priority := pgtype.Int4{Valid: false}
	if item.Priority != 0 {
		priority = pgtype.Int4{Int32: int32(item.Priority), Valid: true}
	}

	// Convert metadata JSON
	metadata := []byte("{}")
	if len(item.Metadata) > 0 {
		// item.Metadata is datatypes.JSON which is []byte
		metadata = []byte(item.Metadata)
	}

	// Convert timestamps
	createdAt := pgtype.Timestamp{Time: item.CreatedAt, Valid: !item.CreatedAt.IsZero()}
	updatedAt := pgtype.Timestamp{Time: item.UpdatedAt, Valid: !item.UpdatedAt.IsZero()}
	deletedAt := pgtype.Timestamp{Valid: false}
	if item.DeletedAt != nil {
		deletedAt = pgtype.Timestamp{Time: *item.DeletedAt, Valid: true}
	}

	return db.GetItemRow{
		ID:          itemID,
		ProjectID:   projectID,
		Title:       item.Title,
		Description: description,
		Type:        item.Type,
		Status:      item.Status,
		Priority:    priority,
		Metadata:    metadata,
		CreatedAt:   createdAt,
		UpdatedAt:   updatedAt,
		DeletedAt:   deletedAt,
	}
}
