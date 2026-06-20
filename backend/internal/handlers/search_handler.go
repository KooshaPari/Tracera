package handlers

import (
	"net/http"
	"strconv"
	"strings"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/pagination"
	"github.com/kooshapari/tracertm-backend/internal/search"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

const (
	searchHandlerMaxLimit        = 100
	searchHandlerDefaultLimit    = 20
	searchHandlerCursorOffset    = 0
	searchHandlerCursorLimit     = 20
	searchHandlerDefaultMinScore = 0.1
	searchHandlerDefaultFuzzy    = 0.3
)

// SearchHandler handles search-related HTTP requests
type SearchHandler struct {
	service services.SearchService
}

// NewSearchHandler creates a new search handler with required service
func NewSearchHandler(service services.SearchService) *SearchHandler {
	return &SearchHandler{
		service: service,
	}
}

// SearchRequestPayload represents the incoming search request
type SearchRequestPayload struct {
	Query          string   `json:"query"`
	Type           string   `json:"type,omitempty"` // fulltext, vector, hybrid, fuzzy, phonetic
	ProjectID      string   `json:"project_id,omitempty"`
	ItemTypes      []string `json:"item_types,omitempty"`
	Status         []string `json:"status,omitempty"`
	Limit          int      `json:"limit,omitempty"`
	Offset         int      `json:"offset,omitempty"` // Deprecated: Use cursor instead
	Cursor         string   `json:"cursor,omitempty"` // Cursor for pagination
	MinScore       float64  `json:"min_score,omitempty"`
	IncludeDeleted bool     `json:"include_deleted,omitempty"`
	// Similarity threshold (0.0-1.0, default: 0.3)
	FuzzyThreshold      float64 `json:"fuzzy_threshold,omitempty"`
	EnableTypoTolerance bool    `json:"enable_typo_tolerance,omitempty"` // Enable fuzzy matching for typos
}

// Search handles POST /api/v1/search
func (h *SearchHandler) Search(c echo.Context) error {
	var req SearchRequestPayload
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request payload: " + err.Error(),
		})
	}

	// Validate query
	if strings.TrimSpace(req.Query) == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Query parameter is required",
		})
	}

	// Convert to service request
	searchType := search.TypeFullText
	if req.Type != "" {
		searchType = search.Type(strings.ToLower(req.Type))
	}

	serviceReq := &services.SearchServiceRequest{
		Query:               req.Query,
		Type:                searchType,
		ProjectID:           req.ProjectID,
		ItemTypes:           req.ItemTypes,
		Status:              req.Status,
		Limit:               req.Limit,
		Offset:              req.Offset,
		MinScore:            req.MinScore,
		IncludeDeleted:      req.IncludeDeleted,
		FuzzyThreshold:      req.FuzzyThreshold,
		EnableTypoTolerance: req.EnableTypoTolerance,
	}

	results, err := h.service.Search(c.Request().Context(), serviceReq)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Search failed: " + err.Error(),
		})
	}

	return c.JSON(http.StatusOK, results)
}

// SearchGet handles GET /api/v1/search with query parameters
func (h *SearchHandler) SearchGet(c echo.Context) error {
	query := c.QueryParam("q")
	if strings.TrimSpace(query) == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Query parameter 'q' is required",
		})
	}

	searchType := search.TypeFullText
	if t := c.QueryParam("type"); t != "" {
		searchType = search.Type(strings.ToLower(t))
	}

	// Parse pagination parameters
	pagination := parseSearchPaginationParams(c)
	limit := pagination.limit
	offset := pagination.offset

	// Parse search-specific parameters
	minScore := parseMinScore(c)
	fuzzyThreshold := parseFuzzyThreshold(c)
	enableTypoTolerance := c.QueryParam("typo_tolerance") == "true"

	// Parse list parameters
	itemTypes := parseCommaSeparatedList(c.QueryParam("item_types"))
	statuses := parseCommaSeparatedList(c.QueryParam("status"))

	serviceReq := &services.SearchServiceRequest{
		Query:               query,
		Type:                searchType,
		ProjectID:           c.QueryParam("project_id"),
		ItemTypes:           itemTypes,
		Status:              statuses,
		Limit:               limit,
		Offset:              offset,
		MinScore:            minScore,
		IncludeDeleted:      c.QueryParam("include_deleted") == "true",
		FuzzyThreshold:      fuzzyThreshold,
		EnableTypoTolerance: enableTypoTolerance,
	}

	results, err := h.service.Search(c.Request().Context(), serviceReq)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Search failed: " + err.Error(),
		})
	}

	return c.JSON(http.StatusOK, results)
}

// searchPagination holds parsed pagination parameters
type searchPagination struct {
	limit  int
	offset int
}

// parseSearchPaginationParams parses pagination parameters from the request
func parseSearchPaginationParams(c echo.Context) searchPagination {
	cursorStr := c.QueryParam("cursor")
	limit := parseSearchLimitForCursor(cursorStr, c.QueryParam("limit"))
	offset := parseSearchOffsetParam(cursorStr, c.QueryParam("offset"))

	return searchPagination{
		limit:  limit,
		offset: offset,
	}
}

func parseSearchLimitForCursor(cursorStr, limitStr string) int {
	if cursorStr != "" {
		return parseSearchCursorLimit(cursorStr)
	}
	return parseSearchLimitParam(limitStr)
}

func parseSearchCursorLimit(cursorStr string) int {
	_, defaultLimit, err := pagination.ParseCursorPaginationParams(
		cursorStr,
		searchHandlerCursorOffset,
		searchHandlerCursorLimit,
		searchHandlerMaxLimit,
	)
	if err != nil {
		return defaultLimit
	}
	return defaultLimit
}

func parseSearchLimitParam(value string) int {
	if value == "" {
		return searchHandlerDefaultLimit
	}
	parsed, err := strconv.Atoi(value)
	if err != nil || parsed <= 0 {
		return searchHandlerDefaultLimit
	}
	if parsed > searchHandlerMaxLimit {
		return searchHandlerMaxLimit
	}
	return parsed
}

func parseSearchOffsetParam(cursorStr, offsetStr string) int {
	if cursorStr != "" || offsetStr == "" {
		return searchHandlerCursorOffset
	}
	parsed, err := strconv.Atoi(offsetStr)
	if err != nil || parsed < 0 {
		return searchHandlerCursorOffset
	}
	return parsed
}

// parseMinScore parses the min_score query parameter
func parseMinScore(c echo.Context) float64 {
	minScore := searchHandlerDefaultMinScore
	if ms := c.QueryParam("min_score"); ms != "" {
		if parsed, err := strconv.ParseFloat(ms, 64); err == nil {
			minScore = parsed
		}
	}
	return minScore
}

// parseFuzzyThreshold parses the fuzzy_threshold query parameter
func parseFuzzyThreshold(c echo.Context) float64 {
	fuzzyThreshold := searchHandlerDefaultFuzzy
	if ft := c.QueryParam("fuzzy_threshold"); ft != "" {
		if parsed, err := strconv.ParseFloat(ft, 64); err == nil && parsed >= 0 && parsed <= 1 {
			fuzzyThreshold = parsed
		}
	}
	return fuzzyThreshold
}

// parseCommaSeparatedList parses a comma-separated list of strings
func parseCommaSeparatedList(value string) []string {
	if value == "" {
		return nil
	}
	items := strings.Split(value, ",")
	for i := range items {
		items[i] = strings.TrimSpace(items[i])
	}
	return items
}

// Suggest handles GET /api/v1/search/suggest
func (h *SearchHandler) Suggest(ctx echo.Context) error {
	prefix := ctx.QueryParam("prefix")
	if strings.TrimSpace(prefix) == "" {
		return ctx.JSON(http.StatusBadRequest, map[string]string{
			"error": "Prefix parameter is required",
		})
	}

	projectID := ctx.QueryParam("project_id")

	limit := 10
	if l := ctx.QueryParam("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil && parsed > 0 {
			limit = parsed
		}
	}

	suggestions, err := h.service.Suggest(ctx.Request().Context(), prefix, projectID, limit)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Suggestion failed: " + err.Error(),
		})
	}

	return ctx.JSON(http.StatusOK, map[string]interface{}{
		"suggestions": suggestions,
		"prefix":      prefix,
	})
}

// IndexItem handles POST /api/v1/search/index/:id
func (h *SearchHandler) IndexItem(c echo.Context) error {
	itemID := c.Param("id")
	if itemID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Item ID is required",
		})
	}

	if err := h.service.IndexItem(c.Request().Context(), itemID); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusAccepted, map[string]string{
		"message": "Item queued for indexing",
		"item_id": itemID,
	})
}

// ReindexAll handles POST /api/v1/search/reindex
func (h *SearchHandler) ReindexAll(c echo.Context) error {
	if err := h.service.ReindexAll(c.Request().Context()); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusAccepted, map[string]string{
		"message": "Full reindex started",
	})
}

// IndexStats handles GET /api/v1/search/stats
func (h *SearchHandler) IndexStats(c echo.Context) error {
	stats, err := h.service.GetIndexStats(c.Request().Context())
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"total_jobs":      stats.TotalJobs,
		"completed_jobs":  stats.CompletedJobs,
		"failed_jobs":     stats.FailedJobs,
		"queue_size":      stats.QueueSize,
		"processing_rate": stats.ProcessingRate,
		"last_indexed_at": stats.LastIndexedAt,
		"last_error":      stats.LastError,
	})
}

// SearchHealth handles GET /api/v1/search/health
func (h *SearchHandler) SearchHealth(c echo.Context) error {
	ctx := c.Request().Context()

	health, err := h.service.GetSearchHealth(ctx)
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"status": health.Status,
			"error":  err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"status":       health.Status,
		"extensions":   health.Extensions,
		"capabilities": health.Capabilities,
		"search_types": health.SearchTypes,
	})
}

// BatchIndexRequest describes the payload for batch indexing.
type BatchIndexRequest struct {
	ItemIDs []string `json:"item_i_ds"`
}

// BatchIndex handles POST /api/v1/search/batch-index.
func (h *SearchHandler) BatchIndex(c echo.Context) error {
	var req BatchIndexRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request payload: " + err.Error(),
		})
	}

	if len(req.ItemIDs) == 0 {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "No item IDs provided",
		})
	}

	if len(req.ItemIDs) > searchHandlerMaxLimit {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Maximum 100 items can be indexed at once",
		})
	}

	result, err := h.service.BatchIndex(c.Request().Context(), req.ItemIDs)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusAccepted, map[string]interface{}{
		"message": "Items queued for indexing",
		"queued":  result.Queued,
		"failed":  result.Failed,
		"total":   result.Total,
	})
}

// DeleteIndex handles DELETE /api/v1/search/index/:id
func (h *SearchHandler) DeleteIndex(c echo.Context) error {
	itemID := c.Param("id")
	if itemID == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Item ID is required",
		})
	}

	if err := h.service.DeleteIndex(c.Request().Context(), itemID); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusAccepted, map[string]string{
		"message": "Item queued for index deletion",
		"item_id": itemID,
	})
}
