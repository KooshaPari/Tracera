package handlers

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/labstack/echo/v4"
	"gorm.io/datatypes"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/uuidutil"
)

// LinkHandler handles HTTP requests for link operations.
type LinkHandler struct {
	linkService services.LinkService // Service layer for operations (REQUIRED)
	itemService services.ItemService // For validation of linked items
	binder      RequestBinder
}

// NewLinkHandler constructs a LinkHandler with its dependencies.
func NewLinkHandler(
	linkService services.LinkService,
	itemService services.ItemService,
	binder RequestBinder,
) *LinkHandler {
	return &LinkHandler{
		linkService: linkService,
		itemService: itemService,
		binder:      binder,
	}
}

// CreateLink handles POST requests to create a link.
func (h *LinkHandler) CreateLink(c echo.Context) error {
	if h.linkService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "LinkService not initialized"})
	}

	var req struct {
		SourceID string          `json:"source_id"`
		TargetID string          `json:"target_id"`
		Type     string          `json:"type"`
		Metadata json.RawMessage `json:"metadata"`
	}
	if err := h.binder.Bind(c, &req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	// Validate UUIDs
	if _, err := uuidutil.StringToUUID(req.SourceID); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid source_id"})
	}
	if _, err := uuidutil.StringToUUID(req.TargetID); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid target_id"})
	}

	// Convert request to service model
	metadata := datatypes.JSON([]byte("{}"))
	if req.Metadata != nil {
		metadata = datatypes.JSON(req.Metadata)
	}

	link := &models.Link{
		SourceID: req.SourceID,
		TargetID: req.TargetID,
		Type:     req.Type,
		Metadata: metadata,
	}

	// Create link via service (handles validation, events, caching)
	if err := h.linkService.CreateLink(c.Request().Context(), link); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, link)
}

// ListLinks handles GET requests to list links.
func (h *LinkHandler) ListLinks(c echo.Context) error {
	if h.linkService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "LinkService not initialized"})
	}

	filter, err := parseLinkFilterParams(c)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	serviceLinks, err := h.linkService.ListLinks(c.Request().Context(), filter)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Convert models.Link to db.Link for backward compatibility
	dbLinks := make([]db.Link, len(serviceLinks))
	for i, link := range serviceLinks {
		dbLinks[i] = h.modelLinkToDBLink(link)
	}
	return c.JSON(http.StatusOK, dbLinks)
}

func parseLinkFilterParams(c echo.Context) (repository.LinkFilter, error) {
	sourceIDStr := c.QueryParam("source_id")
	targetIDStr := c.QueryParam("target_id")
	projectIDStr := c.QueryParam("project_id")
	linkType := c.QueryParam("type")

	// At least one of source_id or target_id is required
	if sourceIDStr == "" && targetIDStr == "" {
		return repository.LinkFilter{}, errors.New("source_id or target_id is required")
	}

	if err := validateLinkUUID(sourceIDStr, "source_id"); err != nil {
		return repository.LinkFilter{}, err
	}
	if err := validateLinkUUID(targetIDStr, "target_id"); err != nil {
		return repository.LinkFilter{}, err
	}
	if err := validateLinkUUID(projectIDStr, "project_id"); err != nil {
		return repository.LinkFilter{}, err
	}

	filter := repository.LinkFilter{}
	if sourceIDStr != "" {
		filter.SourceID = &sourceIDStr
	}
	if targetIDStr != "" {
		filter.TargetID = &targetIDStr
	}
	if projectIDStr != "" {
		filter.ProjectID = &projectIDStr
	}
	if linkType != "" {
		filter.Type = &linkType
	}

	return filter, nil
}

func validateLinkUUID(value, fieldName string) error {
	if value == "" {
		return nil
	}
	if _, err := uuidutil.StringToUUID(value); err != nil {
		return fmt.Errorf("invalid %s", fieldName)
	}
	return nil
}

// GetLink handles GET requests to fetch a single link.
func (h *LinkHandler) GetLink(echoCtx echo.Context) error {
	if h.linkService == nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "LinkService not initialized"})
	}

	idStr := echoCtx.Param("id")
	if _, err := uuidutil.StringToUUID(idStr); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid link ID"})
	}

	// LinkService handles caching internally
	serviceLink, err := h.linkService.GetLink(echoCtx.Request().Context(), idStr)
	if err != nil {
		return echoCtx.JSON(http.StatusNotFound, map[string]string{"error": "Link not found"})
	}

	// Convert models.Link to db.Link for backward compatibility
	dbLink := h.modelLinkToDBLink(serviceLink)
	return echoCtx.JSON(http.StatusOK, dbLink)
}

// UpdateLink handles PATCH/PUT requests to update a link.
func (handler *LinkHandler) UpdateLink(echoCtx echo.Context) error {
	if handler.linkService == nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": "LinkService not initialized"})
	}

	idStr := echoCtx.Param("id")
	if _, err := uuidutil.StringToUUID(idStr); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid link ID"})
	}

	var req struct {
		Type     string          `json:"type"`
		Metadata json.RawMessage `json:"metadata"`
	}
	if err := handler.binder.Bind(echoCtx, &req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
	}

	// Validate link type is not empty
	if req.Type == "" {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "Link type is required"})
	}

	// Convert to service model
	metadata := datatypes.JSON([]byte("{}"))
	if req.Metadata != nil {
		metadata = datatypes.JSON(req.Metadata)
	}

	link := &models.Link{
		ID:       idStr,
		Type:     req.Type,
		Metadata: metadata,
	}

	// Update via service (handles cache invalidation, events)
	if err := handler.linkService.UpdateLink(echoCtx.Request().Context(), link); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, link)
}

// DeleteLink handles DELETE requests to remove a link.
func (h *LinkHandler) DeleteLink(c echo.Context) error {
	if h.linkService == nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "LinkService not initialized"})
	}

	idStr := c.Param("id")

	// Validate UUID format
	if _, err := uuidutil.StringToUUID(idStr); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid link ID"})
	}

	// Delete via service (handles cache invalidation, events)
	if err := h.linkService.DeleteLink(c.Request().Context(), idStr); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Link deleted"})
}

// modelLinkToDBLink converts a models.Link to db.Link for backward compatibility
func (h *LinkHandler) modelLinkToDBLink(link *models.Link) db.Link {
	// Parse UUID
	id := parseUUIDOrZero(link.ID)
	sourceID := parseUUIDOrZero(link.SourceID)
	targetID := parseUUIDOrZero(link.TargetID)

	// Convert timestamps
	createdAt := pgtype.Timestamp{Time: link.CreatedAt, Valid: !link.CreatedAt.IsZero()}
	updatedAt := pgtype.Timestamp{Time: link.UpdatedAt, Valid: !link.UpdatedAt.IsZero()}
	// Note: Link model doesn't have DeletedAt field
	deletedAt := pgtype.Timestamp{Valid: false}

	return db.Link{
		ID:        id,
		SourceID:  sourceID,
		TargetID:  targetID,
		Type:      link.Type,
		Metadata:  []byte(link.Metadata),
		CreatedAt: createdAt,
		UpdatedAt: updatedAt,
		DeletedAt: deletedAt,
	}
}

func parseUUIDOrZero(id string) pgtype.UUID {
	parsed, err := uuidutil.StringToUUID(id)
	if err != nil {
		return pgtype.UUID{}
	}
	return parsed
}
