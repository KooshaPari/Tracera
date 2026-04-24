package equivalence

import (
	"net/http"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// Handler provides HTTP endpoints for equivalence operations
type Handler struct {
	service Service
}

const (
	defaultEquivalencePageLimit = 50
	maxEquivalencePageLimit     = 500
	defaultMinConfidence        = 0.5
)

// NewHandler creates a new equivalence handler
func NewHandler(service Service) *Handler {
	return &Handler{service: service}
}

// RegisterRoutes registers the equivalence routes with an Echo group
func (handler *Handler) RegisterRoutes(group *echo.Group) {
	eq := group.Group("/equivalences")

	// Equivalence detection and management
	eq.GET("", handler.ListEquivalences)
	eq.POST("/detect", handler.DetectEquivalences)
	eq.GET("/:id", handler.GetEquivalence)
	eq.POST("/:id/confirm", handler.ConfirmEquivalence)
	eq.POST("/:id/reject", handler.RejectEquivalence)
	eq.POST("/bulk-confirm", handler.BulkConfirmEquivalences)
	eq.POST("/bulk-reject", handler.BulkRejectEquivalences)
	eq.POST("/batch-confirm", handler.BulkConfirmEquivalences) // Alias for frontend compatibility
	eq.POST("/batch-reject", handler.BulkRejectEquivalences)   // Alias for frontend compatibility

	// Manual link creation
	eq.POST("/links", handler.CreateManualLink)
	eq.GET("/items/:id", handler.GetEquivalences)

	// Canonical concepts management
	eq.GET("/concepts", handler.GetCanonicalConcepts)
	eq.POST("/concepts", handler.CreateCanonicalConcept)
	eq.GET("/concepts/:id", handler.GetCanonicalConcept)
	eq.GET("/concepts/:id/projections", handler.GetConceptProjections)
	eq.PUT("/concepts/:id", handler.UpdateCanonicalConcept)
	eq.DELETE("/concepts/:id", handler.DeleteCanonicalConcept)
	eq.POST("/concepts/:id/projections", handler.CreateCanonicalProjection)
	eq.DELETE("/concepts/:conceptId/projections/:projectionId", handler.DeleteCanonicalProjection)

	// Legacy routes for backward compatibility
	eq.GET("/suggestions", handler.GetSuggestions)
	eq.POST("/suggestions/:id/confirm", handler.ConfirmSuggestion)
	eq.POST("/suggestions/:id/reject", handler.RejectSuggestion)
	eq.POST("/suggestions/bulk-confirm", handler.BulkConfirm)
	eq.POST("/suggestions/bulk-reject", handler.BulkReject)

	// Project-scoped routes (matches frontend API calls)
	proj := group.Group("/projects/:projectId/equivalences")
	proj.GET("", handler.ListProjectEquivalences)
	proj.POST("/detect", handler.DetectProjectEquivalences)

	// Project-scoped canonical concepts
	projConcepts := group.Group("/projects/:projectId/concepts")
	projConcepts.GET("", handler.ListProjectConcepts)
	projConcepts.POST("", handler.CreateProjectConcept)
}

// ListEquivalences handles GET /equivalences
func (handler *Handler) ListEquivalences(echoCtx echo.Context) error {
	projectID, errResponse, statusCode := parseProjectIDParam(echoCtx)
	if errResponse != nil {
		return echoCtx.JSON(statusCode, errResponse)
	}

	limit, offset := parsePagination(echoCtx)
	status := Status(echoCtx.QueryParam("status"))
	minConf := parseMinConfidence(echoCtx)
	linkType := echoCtx.QueryParam("link_type")

	// Build filter
	filter := Filter{
		ProjectID:     projectID,
		Status:        status,
		MinConfidence: minConf,
		LinkType:      linkType,
	}

	// Get equivalences from service
	equivalences, total, err := handler.service.ListEquivalencesByProject(
		echoCtx.Request().Context(),
		filter,
		limit,
		offset,
	)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "LIST_EQUIVALENCES_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	response := ListEquivalencesResponse{
		Data:    equivalences,
		Total:   total,
		Limit:   limit,
		Offset:  offset,
		HasMore: int64(offset+len(equivalences)) < total,
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// GetEquivalence handles GET /equivalences/:id
func (handler *Handler) GetEquivalence(echoCtx echo.Context) error {
	eqID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid equivalence id format",
			Code:      "INVALID_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	link, err := handler.service.GetEquivalenceByID(echoCtx.Request().Context(), eqID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if link == nil {
		return echoCtx.JSON(http.StatusNotFound, ErrorResponse{
			Error:     "equivalence not found",
			Code:      "NOT_FOUND",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	return echoCtx.JSON(http.StatusOK, link)
}

// ConfirmEquivalence handles POST /equivalences/:id/confirm
func (handler *Handler) ConfirmEquivalence(echoCtx echo.Context) error {
	eqID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid equivalence id format",
			Code:      "INVALID_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	var req ConfirmEquivalenceRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	link, err := handler.service.ConfirmEquivalenceByID(echoCtx.Request().Context(), eqID, userID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "CONFIRM_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	response := ConfirmEquivalenceResponse{
		Link:        *link,
		Message:     "Equivalence confirmed successfully",
		ConfirmedAt: time.Now(),
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// RejectEquivalence handles POST /equivalences/:id/reject
func (handler *Handler) RejectEquivalence(echoCtx echo.Context) error {
	eqID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid equivalence id format",
			Code:      "INVALID_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	var req RejectEquivalenceRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if err := handler.service.RejectEquivalenceByID(echoCtx.Request().Context(), eqID, userID); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "REJECT_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// BulkConfirmEquivalences handles POST /equivalences/bulk-confirm
func (handler *Handler) BulkConfirmEquivalences(echoCtx echo.Context) error {
	var req BulkConfirmRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if len(req.EquivalenceIDs) == 0 {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "equivalence_ids is required and must not be empty",
			Code:      "EMPTY_IDS",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	links, failedIDs := handler.service.BulkConfirmWithTracking(
		echoCtx.Request().Context(),
		req.EquivalenceIDs,
		userID,
	)

	response := BulkConfirmResponse{
		Confirmed: len(links),
		Failed:    len(failedIDs),
		Links:     links,
		Errors:    failedIDs,
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// BulkRejectEquivalences handles POST /equivalences/bulk-reject
func (handler *Handler) BulkRejectEquivalences(echoCtx echo.Context) error {
	var req BulkRejectRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if len(req.EquivalenceIDs) == 0 {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "equivalence_ids is required and must not be empty",
			Code:      "EMPTY_IDS",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	failedIDs := handler.service.BulkRejectWithTracking(echoCtx.Request().Context(), req.EquivalenceIDs, userID)

	response := BulkRejectResponse{
		Rejected: len(req.EquivalenceIDs) - len(failedIDs),
		Failed:   len(failedIDs),
		Errors:   failedIDs,
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// GetEquivalences handles GET /equivalences/items/:id
func (handler *Handler) GetEquivalences(echoCtx echo.Context) error {
	itemID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid item id"})
	}

	links, err := handler.service.GetEquivalences(echoCtx.Request().Context(), itemID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, links)
}

// CreateManualLink handles POST /equivalences/links
func (handler *Handler) CreateManualLink(echoCtx echo.Context) error {
	var link Link
	if err := echoCtx.Bind(&link); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	userID := getUserIDFromEchoContext(echoCtx)

	created, err := handler.service.CreateManualLink(echoCtx.Request().Context(), &link, userID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusCreated, created)
}

// Helpers

func parseProjectIDParam(c echo.Context) (uuid.UUID, *ErrorResponse, int) {
	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return uuid.Nil, &ErrorResponse{
			Error:     "project_id is required",
			Code:      "MISSING_PROJECT_ID",
			Details:   nil,
			Timestamp: time.Now(),
		}, http.StatusBadRequest
	}

	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return uuid.Nil, &ErrorResponse{
			Error:     "invalid project_id format",
			Code:      "INVALID_PROJECT_ID",
			Details:   nil,
			Timestamp: time.Now(),
		}, http.StatusBadRequest
	}

	return projectID, nil, http.StatusOK
}

func parsePagination(ctx echo.Context) (int, int) {
	limitValue, limitErr := strconv.Atoi(ctx.QueryParam("limit"))
	limit := limitValue
	if limitErr != nil || limit <= 0 || limit > maxEquivalencePageLimit {
		limit = defaultEquivalencePageLimit
	}

	offsetValue, offsetErr := strconv.Atoi(ctx.QueryParam("offset"))
	offset := offsetValue
	if offsetErr != nil || offset < 0 {
		offset = 0
	}

	return limit, offset
}

func parseMinConfidence(ctx echo.Context) float64 {
	minConfStr := ctx.QueryParam("min_confidence")
	if minConfStr == "" {
		return 0.0
	}

	confidence, err := strconv.ParseFloat(minConfStr, 64)
	if err != nil {
		return 0.0
	}

	return confidence
}

func getUserIDFromEchoContext(c echo.Context) uuid.UUID {
	if userID, ok := c.Get("user_id").(uuid.UUID); ok {
		return userID
	}
	if userIDStr, ok := c.Get("user_id").(string); ok {
		if id, err := uuid.Parse(userIDStr); err == nil {
			return id
		}
	}
	return uuid.Nil
}
