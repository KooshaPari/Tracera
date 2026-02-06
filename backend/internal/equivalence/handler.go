package equivalence

import (
	"net/http"
	"strconv"
	"strings"
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

	// Legacy routes for backward compatibility
	eq.GET("/suggestions", handler.GetSuggestions)
	eq.POST("/suggestions/:id/confirm", handler.ConfirmSuggestion)
	eq.POST("/suggestions/:id/reject", handler.RejectSuggestion)
	eq.POST("/suggestions/bulk-confirm", handler.BulkConfirm)
	eq.POST("/suggestions/bulk-reject", handler.BulkReject)

	// Project-scoped routes (matches frontend API calls)
	// GET /api/v1/projects/:projectId/equivalences
	// POST /api/v1/projects/:projectId/equivalences/detect
	proj := group.Group("/projects/:projectId/equivalences")
	proj.GET("", handler.ListProjectEquivalences)
	proj.POST("/detect", handler.DetectProjectEquivalences)

	// Project-scoped canonical concepts
	// GET /api/v1/projects/:projectId/concepts
	// POST /api/v1/projects/:projectId/concepts
	projConcepts := group.Group("/projects/:projectId/concepts")
	projConcepts.GET("", handler.ListProjectConcepts)
	projConcepts.POST("", handler.CreateProjectConcept)
}

// DetectEquivalences handles POST /equivalences/detect
func (handler *Handler) DetectEquivalences(echoCtx echo.Context) error {
	var req DetectionRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	suggestions, err := handler.service.DetectEquivalences(echoCtx.Request().Context(), &req)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, suggestions)
}

// GetSuggestions handles GET /equivalences/suggestions
func (handler *Handler) GetSuggestions(ctx echo.Context) error {
	projectID, err := uuid.Parse(ctx.QueryParam("project_id"))
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	limit, offset := parsePagination(ctx)

	suggestions, err := handler.service.GetSuggestions(ctx.Request().Context(), projectID, limit, offset)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return ctx.JSON(http.StatusOK, suggestions)
}

// ConfirmSuggestion handles POST /equivalences/suggestions/:id/confirm
func (handler *Handler) ConfirmSuggestion(ctx echo.Context) error {
	suggestionID, err := uuid.Parse(ctx.Param("id"))
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid suggestion id"})
	}

	userID := getUserIDFromEchoContext(ctx)

	link, err := handler.service.ConfirmSuggestion(ctx.Request().Context(), suggestionID, userID)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return ctx.JSON(http.StatusOK, link)
}

// RejectSuggestion handles POST /equivalences/suggestions/:id/reject
func (handler *Handler) RejectSuggestion(echoCtx echo.Context) error {
	suggestionID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid suggestion id"})
	}

	userID := getUserIDFromEchoContext(echoCtx)

	if err := handler.service.RejectSuggestion(echoCtx.Request().Context(), suggestionID, userID); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// BulkConfirm handles POST /equivalences/suggestions/bulk-confirm
func (handler *Handler) BulkConfirm(echoCtx echo.Context) error {
	var req BulkConfirmRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	userID := getUserIDFromEchoContext(echoCtx)

	links, err := handler.service.BulkConfirm(echoCtx.Request().Context(), req.EquivalenceIDs, userID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return echoCtx.JSON(http.StatusOK, links)
}

// BulkReject handles POST /equivalences/suggestions/bulk-reject
func (handler *Handler) BulkReject(ctx echo.Context) error {
	var req BulkConfirmRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid request body"})
	}

	userID := getUserIDFromEchoContext(ctx)

	if err := handler.service.BulkReject(ctx.Request().Context(), req.EquivalenceIDs, userID); err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return ctx.NoContent(http.StatusNoContent)
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

// GetCanonicalConcepts handles GET /equivalences/concepts
func (handler *Handler) GetCanonicalConcepts(ctx echo.Context) error {
	projectID, err := uuid.Parse(ctx.QueryParam("project_id"))
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{"error": "invalid project_id"})
	}

	concepts, err := handler.service.GetCanonicalConcepts(ctx.Request().Context(), projectID)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return ctx.JSON(http.StatusOK, concepts)
}

// ============================================================================
// NEW ENDPOINTS - API Contract Handlers
// ============================================================================

// ListEquivalences handles GET /equivalences
// @Summary List equivalence links for a project
// @Description Returns a paginated list of equivalence links with optional filtering
// @Tags equivalences
// @Accept json
// @Produce json
// @Param project_id query string false "Project ID (required)"
// @Param status query string false "Filter by status (suggested, confirmed, rejected, auto)"
// @Param min_confidence query number false "Minimum confidence threshold (0.0-1.0)"
// @Param link_type query string false "Filter by link type"
// @Param limit query integer false "Page size (default: 50, max: 500)"
// @Param offset query integer false "Pagination offset (default: 0)"
// @Param sort_by query string false "Sort field (created_at, confidence, updated_at)"
// @Param sort_direction query string false "Sort direction (asc, desc)"
// @Success 200 {object} ListEquivalencesResponse "List of equivalence links"
// @Failure 400 {object} ErrorResponse "Invalid request parameters"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences [get]
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

func parseProjectIDParam(c echo.Context) (uuid.UUID, *ErrorResponse, int) {
	projectIDStr := c.QueryParam("project_id")
	if projectIDStr == "" {
		return uuid.Nil, &ErrorResponse{
			Error:     "project_id is required",
			Code:      "MISSING_PROJECT_ID",
			Timestamp: time.Now(),
		}, http.StatusBadRequest
	}

	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return uuid.Nil, &ErrorResponse{
			Error:     "invalid project_id format",
			Code:      "INVALID_PROJECT_ID",
			Timestamp: time.Now(),
		}, http.StatusBadRequest
	}

	return projectID, nil, http.StatusOK
}

func parseConceptIDParam(c echo.Context) (uuid.UUID, *ErrorResponse, int) {
	conceptID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		return uuid.Nil, &ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Timestamp: time.Now(),
		}, http.StatusBadRequest
	}

	return conceptID, nil, http.StatusOK
}

func parseProjectIDPathParam(ctx echo.Context, param string) (uuid.UUID, *ErrorResponse, int) {
	projectID, err := uuid.Parse(ctx.Param(param))
	if err != nil {
		return uuid.Nil, &ErrorResponse{
			Error:     "Invalid project ID format",
			Code:      "INVALID_PROJECT_ID",
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

func filterProjectionsByPerspective(projections []CanonicalProjection, perspective string) []CanonicalProjection {
	if perspective == "" {
		return projections
	}

	filtered := make([]CanonicalProjection, 0)
	for _, projection := range projections {
		if projection.Perspective == perspective {
			filtered = append(filtered, projection)
		}
	}

	return filtered
}

func paginateProjections(projections []CanonicalProjection, limit, offset int) []CanonicalProjection {
	if offset > len(projections) {
		offset = len(projections)
	}
	endIdx := offset + limit
	if endIdx > len(projections) {
		endIdx = len(projections)
	}

	return projections[offset:endIdx]
}

func buildPerspectiveBreakdown(projections []CanonicalProjection) map[string][]CanonicalProjection {
	perspectiveMap := make(map[string][]CanonicalProjection)
	for _, projection := range projections {
		perspectiveMap[projection.Perspective] = append(perspectiveMap[projection.Perspective], projection)
	}

	return perspectiveMap
}

func applyDetectionDefaults(req *DetectionRequest) {
	if req.MaxResults <= 0 {
		req.MaxResults = 100
	}
	if req.MinConfidence <= 0 {
		req.MinConfidence = defaultMinConfidence
	}
}

func buildDetectionStats(suggestions []Suggestion, req *DetectionRequest, startTime time.Time) DetectionStats {
	strategyBreakdown := make(map[StrategyType]int)
	avgConf := 0.0
	for _, suggestion := range suggestions {
		for _, strategy := range suggestion.Strategies {
			strategyBreakdown[strategy]++
		}
		avgConf += suggestion.Confidence
	}
	if len(suggestions) > 0 {
		avgConf /= float64(len(suggestions))
	}

	return DetectionStats{
		TotalItemsScanned: len(req.CandidatePool),
		EquivalencesFound: len(suggestions),
		AverageConfidence: avgConf,
		StrategyBreakdown: strategyBreakdown,
		DurationMs:        time.Since(startTime).Milliseconds(),
	}
}

// GetEquivalence handles GET /equivalences/:id
// @Summary Get a specific equivalence link
// @Description Returns details of a specific equivalence link
// @Tags equivalences
// @Accept json
// @Produce json
// @Param id path string true "Equivalence ID"
// @Success 200 {object} Link "Equivalence link details"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Equivalence not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/{id} [get]
func (handler *Handler) GetEquivalence(echoCtx echo.Context) error {
	eqID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid equivalence id format",
			Code:      "INVALID_ID",
			Timestamp: time.Now(),
		})
	}

	link, err := handler.service.GetEquivalenceByID(echoCtx.Request().Context(), eqID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_ERROR",
			Timestamp: time.Now(),
		})
	}

	if link == nil {
		return echoCtx.JSON(http.StatusNotFound, ErrorResponse{
			Error:     "equivalence not found",
			Code:      "NOT_FOUND",
			Timestamp: time.Now(),
		})
	}

	return echoCtx.JSON(http.StatusOK, link)
}

// ConfirmEquivalence handles POST /equivalences/:id/confirm
// @Summary Confirm an equivalence link
// @Description Confirms an equivalence link and makes it permanent
// @Tags equivalences
// @Accept json
// @Produce json
// @Param id path string true "Equivalence ID"
// @Param body body ConfirmEquivalenceRequest false "Confirmation details"
// @Success 200 {object} ConfirmEquivalenceResponse "Confirmation successful"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Equivalence not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/{id}/confirm [post]
func (handler *Handler) ConfirmEquivalence(echoCtx echo.Context) error {
	eqID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid equivalence id format",
			Code:      "INVALID_ID",
			Timestamp: time.Now(),
		})
	}

	var req ConfirmEquivalenceRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Timestamp: time.Now(),
		})
	}

	link, err := handler.service.ConfirmEquivalenceByID(echoCtx.Request().Context(), eqID, userID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "CONFIRM_ERROR",
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
// @Summary Reject an equivalence link
// @Description Rejects and removes an equivalence link
// @Tags equivalences
// @Accept json
// @Produce json
// @Param id path string true "Equivalence ID"
// @Param body body RejectEquivalenceRequest false "Rejection details"
// @Success 204 "Rejection successful"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Equivalence not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/{id}/reject [post]
func (handler *Handler) RejectEquivalence(echoCtx echo.Context) error {
	eqID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid equivalence id format",
			Code:      "INVALID_ID",
			Timestamp: time.Now(),
		})
	}

	var req RejectEquivalenceRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Timestamp: time.Now(),
		})
	}

	if err := handler.service.RejectEquivalenceByID(echoCtx.Request().Context(), eqID, userID); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "REJECT_ERROR",
			Timestamp: time.Now(),
		})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// BulkConfirmEquivalences handles POST /equivalences/bulk-confirm
// @Summary Confirm multiple equivalences
// @Description Confirms multiple equivalence links in a single operation
// @Tags equivalences
// @Accept json
// @Produce json
// @Param body body BulkConfirmRequest true "Equivalence IDs to confirm"
// @Success 200 {object} BulkConfirmResponse "Confirmation results"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/bulk-confirm [post]
func (handler *Handler) BulkConfirmEquivalences(echoCtx echo.Context) error {
	var req BulkConfirmRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	if len(req.EquivalenceIDs) == 0 {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "equivalence_ids is required and must not be empty",
			Code:      "EMPTY_IDS",
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
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
// @Summary Reject multiple equivalences
// @Description Rejects multiple equivalence links in a single operation
// @Tags equivalences
// @Accept json
// @Produce json
// @Param body body BulkRejectRequest true "Equivalence IDs to reject"
// @Success 200 {object} BulkRejectResponse "Rejection results"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/bulk-reject [post]
func (handler *Handler) BulkRejectEquivalences(echoCtx echo.Context) error {
	var req BulkRejectRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	if len(req.EquivalenceIDs) == 0 {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "equivalence_ids is required and must not be empty",
			Code:      "EMPTY_IDS",
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
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

// CreateCanonicalConcept handles POST /equivalences/concepts
// @Summary Create a new canonical concept
// @Description Creates a new abstract canonical concept for the project
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param body body CreateCanonicalConceptRequest true "Canonical concept details"
// @Success 201 {object} CreateCanonicalConceptResponse "Concept created successfully"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 409 {object} ErrorResponse "Duplicate concept"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/concepts [post]
func (handler *Handler) CreateCanonicalConcept(echoCtx echo.Context) error {
	var req CreateCanonicalConceptRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	if req.Name == "" {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "name is required",
			Code:      "MISSING_NAME",
			Timestamp: time.Now(),
		})
	}

	if req.ProjectID == uuid.Nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "project_id is required",
			Code:      "MISSING_PROJECT_ID",
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(echoCtx)
	if userID == uuid.Nil {
		return echoCtx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Timestamp: time.Now(),
		})
	}

	concept, err := handler.service.CreateCanonicalConcept(echoCtx.Request().Context(), &req, userID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to create concept: " + err.Error(),
			Code:      "CREATE_ERROR",
			Timestamp: time.Now(),
		})
	}

	response := CreateCanonicalConceptResponse{
		Concept:   *concept,
		Message:   "Canonical concept created successfully",
		CreatedAt: concept.CreatedAt,
	}

	return echoCtx.JSON(http.StatusCreated, response)
}

// GetCanonicalConcept handles GET /equivalences/concepts/:id
// @Summary Get a canonical concept
// @Description Returns details of a specific canonical concept
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param id path string true "Canonical Concept ID"
// @Success 200 {object} CanonicalConcept "Concept details"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Concept not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/concepts/{id} [get]
func (handler *Handler) GetCanonicalConcept(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Timestamp: time.Now(),
		})
	}

	concept, err := handler.service.GetCanonicalConcept(echoCtx.Request().Context(), conceptID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_ERROR",
			Timestamp: time.Now(),
		})
	}

	if concept == nil {
		return echoCtx.JSON(http.StatusNotFound, ErrorResponse{
			Error:     "concept not found",
			Code:      "NOT_FOUND",
			Timestamp: time.Now(),
		})
	}

	return echoCtx.JSON(http.StatusOK, concept)
}

// UpdateCanonicalConcept handles PUT /equivalences/concepts/:id
// @Summary Update a canonical concept
// @Description Updates an existing canonical concept
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param id path string true "Canonical Concept ID"
// @Param body body CreateCanonicalConceptRequest true "Updated concept details"
// @Success 200 {object} CanonicalConcept "Updated concept"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Concept not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/concepts/{id} [put]
func (handler *Handler) UpdateCanonicalConcept(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Timestamp: time.Now(),
		})
	}

	var req CreateCanonicalConceptRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	if req.Name == "" {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "name is required",
			Code:      "MISSING_NAME",
			Timestamp: time.Now(),
		})
	}

	concept := &CanonicalConcept{
		ID:          conceptID,
		ProjectID:   req.ProjectID,
		Name:        req.Name,
		Description: req.Description,
		Domain:      req.Domain,
		Category:    req.Category,
		Tags:        req.Tags,
		UpdatedAt:   time.Now(),
	}

	updated, err := handler.service.UpdateCanonicalConcept(echoCtx.Request().Context(), conceptID, concept)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to update concept: " + err.Error(),
			Code:      "UPDATE_ERROR",
			Timestamp: time.Now(),
		})
	}

	return echoCtx.JSON(http.StatusOK, updated)
}

// DeleteCanonicalConcept handles DELETE /equivalences/concepts/:id
// @Summary Delete a canonical concept
// @Description Deletes a canonical concept and its projections
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param id path string true "Canonical Concept ID"
// @Success 204 "Deletion successful"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Concept not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/concepts/{id} [delete]
func (handler *Handler) DeleteCanonicalConcept(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Timestamp: time.Now(),
		})
	}

	if err := handler.service.DeleteCanonicalConcept(echoCtx.Request().Context(), conceptID); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to delete concept: " + err.Error(),
			Code:      "DELETE_ERROR",
			Timestamp: time.Now(),
		})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// GetConceptProjections handles GET /equivalences/concepts/:id/projections
// @Summary Get projections of a canonical concept
// @Description Returns all view manifestations (projections) of a canonical concept
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param id path string true "Canonical Concept ID"
// @Param perspective query string false "Filter by perspective"
// @Param status query string false "Filter by status (suggested, confirmed, rejected)"
// @Param limit query integer false "Page size (default: 50)"
// @Param offset query integer false "Pagination offset"
// @Success 200 {object} GetProjectionsResponse "Projections list"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Concept not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/concepts/{id}/projections [get]
func (handler *Handler) GetConceptProjections(echoCtx echo.Context) error {
	conceptID, errResponse, statusCode := parseConceptIDParam(echoCtx)
	if errResponse != nil {
		return echoCtx.JSON(statusCode, errResponse)
	}

	perspective := echoCtx.QueryParam("perspective")
	_ = Status(echoCtx.QueryParam("status"))

	limit, offset := parsePagination(echoCtx)

	projections, err := handler.service.GetConceptProjections(echoCtx.Request().Context(), conceptID)
	if err != nil {
		// If concept not found, return 404
		if strings.Contains(err.Error(), "not found") {
			return echoCtx.JSON(http.StatusNotFound, ErrorResponse{
				Error:     "concept not found",
				Code:      "NOT_FOUND",
				Timestamp: time.Now(),
			})
		}
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_PROJECTIONS_ERROR",
			Timestamp: time.Now(),
		})
	}

	filtered := filterProjectionsByPerspective(projections, perspective)
	paginatedProjections := paginateProjections(filtered, limit, offset)
	perspectiveMap := buildPerspectiveBreakdown(filtered)

	response := GetProjectionsResponse{
		ConceptID:            conceptID,
		Projections:          paginatedProjections,
		PerspectiveBreakdown: perspectiveMap,
		Total:                int64(len(filtered)),
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// ============================================================================
// PIVOT NAVIGATION HANDLER (POST /api/v1/items/{id}/pivot)
// ============================================================================

// PivotNavigation handles POST /items/:id/pivot
// This endpoint needs to be registered in the item handler, not equivalence handler
// But we provide the implementation here for reference
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
// NOTE: This should be implemented in ItemHandler, not equivalence Handler

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

// getUserIDFromEchoContext extracts the user ID from the Echo context
// This should be set by the auth middleware
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

// ============================================================================
// PROJECT-SCOPED EQUIVALENCE HANDLERS
// ============================================================================

// ListProjectEquivalences handles GET /projects/:projectId/equivalences
// @Summary List equivalence links for a specific project
// @Description Returns a paginated list of equivalence links for the given project
// @Tags equivalences
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param status query string false "Filter by status (suggested, confirmed, rejected, auto)"
// @Param min_confidence query number false "Minimum confidence threshold (0.0-1.0)"
// @Param link_type query string false "Filter by link type"
// @Param limit query integer false "Page size (default: 50, max: 500)"
// @Param offset query integer false "Pagination offset (default: 0)"
// @Param sort_by query string false "Sort field (created_at, confidence, updated_at)"
// @Param sort_direction query string false "Sort direction (asc, desc)"
// @Success 200 {object} ListEquivalencesResponse "List of equivalence links"
// @Failure 400 {object} ErrorResponse "Invalid project ID"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /projects/{projectId}/equivalences [get]
func (handler *Handler) ListProjectEquivalences(echoCtx echo.Context) error {
	projectIDStr := echoCtx.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "Invalid project ID format",
			Code:      "INVALID_PROJECT_ID",
			Timestamp: time.Now(),
		})
	}

	// Parse pagination
	limit, offset := parsePagination(echoCtx)

	// Parse filters
	status := Status(echoCtx.QueryParam("status"))
	minConfStr := echoCtx.QueryParam("min_confidence")
	minConf := 0.0
	if minConfStr != "" {
		if conf, err := strconv.ParseFloat(minConfStr, 64); err == nil {
			minConf = conf
		}
	}

	linkType := echoCtx.QueryParam("link_type")

	// Build filter for repository query
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

// DetectProjectEquivalences handles POST /projects/:projectId/equivalences/detect
// @Summary Detect equivalences within a project
// @Description Runs equivalence detection for items in the specified project
// @Tags equivalences
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param body body DetectionRequest true "Detection configuration"
// @Success 200 {object} DetectionResponse "Detection results with suggestions"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Detection failed"
// @Router /projects/{projectId}/equivalences/detect [post]
func (handler *Handler) DetectProjectEquivalences(ctx echo.Context) error {
	projectID, errResponse, statusCode := parseProjectIDPathParam(ctx, "projectId")
	if errResponse != nil {
		return ctx.JSON(statusCode, errResponse)
	}

	var req DetectionRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "Invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	// Override project ID from path parameter (path takes precedence)
	req.ProjectID = projectID

	applyDetectionDefaults(&req)

	startTime := time.Now()

	// Run detection
	suggestions, err := handler.service.DetectEquivalences(ctx.Request().Context(), &req)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "DETECTION_ERROR",
			Timestamp: time.Now(),
		})
	}

	response := DetectionResponse{
		Suggestions: suggestions,
		Stats:       buildDetectionStats(suggestions, &req, startTime),
		DetectedAt:  time.Now(),
	}

	return ctx.JSON(http.StatusOK, response)
}

// ListProjectConcepts handles GET /projects/:projectId/concepts
// @Summary List canonical concepts for a project
// @Description Returns all canonical concepts for the given project
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Success 200 {array} CanonicalConcept "List of concepts"
// @Failure 400 {object} ErrorResponse "Invalid project ID"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /projects/{projectId}/concepts [get]
func (handler *Handler) ListProjectConcepts(ctx echo.Context) error {
	projectIDStr := ctx.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid project id format",
			Code:      "INVALID_PROJECT_ID",
			Timestamp: time.Now(),
		})
	}

	concepts, err := handler.service.GetCanonicalConcepts(ctx.Request().Context(), projectID)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_CONCEPTS_ERROR",
			Timestamp: time.Now(),
		})
	}

	return ctx.JSON(http.StatusOK, concepts)
}

// CreateProjectConcept handles POST /projects/:projectId/concepts
// @Summary Create a canonical concept for a project
// @Description Creates a new canonical concept scoped to the given project
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param body body CreateCanonicalConceptRequest true "Concept details"
// @Success 201 {object} CreateCanonicalConceptResponse "Concept created successfully"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /projects/{projectId}/concepts [post]
func (handler *Handler) CreateProjectConcept(ctx echo.Context) error {
	projectIDStr := ctx.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid project id format",
			Code:      "INVALID_PROJECT_ID",
			Timestamp: time.Now(),
		})
	}

	var req CreateCanonicalConceptRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	if req.Name == "" {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "name is required",
			Code:      "MISSING_NAME",
			Timestamp: time.Now(),
		})
	}

	// Override project ID from path parameter (path takes precedence)
	req.ProjectID = projectID

	userID := getUserIDFromEchoContext(ctx)
	if userID == uuid.Nil {
		return ctx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Timestamp: time.Now(),
		})
	}

	concept, err := handler.service.CreateCanonicalConcept(ctx.Request().Context(), &req, userID)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to create concept: " + err.Error(),
			Code:      "CREATE_ERROR",
			Timestamp: time.Now(),
		})
	}

	response := CreateCanonicalConceptResponse{
		Concept:   *concept,
		Message:   "Canonical concept created successfully",
		CreatedAt: concept.CreatedAt,
	}

	return ctx.JSON(http.StatusCreated, response)
}

// CreateCanonicalProjection handles POST /equivalences/concepts/:id/projections
// @Summary Create a projection of a canonical concept
// @Description Links an item to a canonical concept in a specific perspective
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param id path string true "Canonical Concept ID"
// @Param body body CreateCanonicalProjectionRequest true "Projection details"
// @Success 201 {object} CreateCanonicalProjectionResponse "Projection created successfully"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Concept not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/concepts/{id}/projections [post]
func (handler *Handler) CreateCanonicalProjection(ctx echo.Context) error {
	conceptID, err := uuid.Parse(ctx.Param("id"))
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_CONCEPT_ID",
			Timestamp: time.Now(),
		})
	}

	var req CreateCanonicalProjectionRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	if req.ItemID == uuid.Nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "item_id is required",
			Code:      "MISSING_ITEM_ID",
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(ctx)
	if userID == uuid.Nil {
		return ctx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Timestamp: time.Now(),
		})
	}

	// Get the concept to extract project ID
	concept, err := handler.service.GetCanonicalConcept(ctx.Request().Context(), conceptID)
	if err != nil {
		return ctx.JSON(http.StatusNotFound, ErrorResponse{
			Error:     "concept not found",
			Code:      "NOT_FOUND",
			Timestamp: time.Now(),
		})
	}

	projection, err := handler.service.CreateProjection(
		ctx.Request().Context(),
		&req,
		conceptID,
		concept.ProjectID,
		userID,
	)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to create projection: " + err.Error(),
			Code:      "CREATE_ERROR",
			Timestamp: time.Now(),
		})
	}

	response := CreateCanonicalProjectionResponse{
		Projection: *projection,
		Message:    "Projection created successfully",
		CreatedAt:  projection.CreatedAt,
	}

	return ctx.JSON(http.StatusCreated, response)
}

// DeleteCanonicalProjection handles DELETE /equivalences/concepts/:conceptId/projections/:projectionId
// @Summary Delete a projection of a canonical concept
// @Description Removes a link between an item and a canonical concept
// @Tags canonical-concepts
// @Accept json
// @Produce json
// @Param conceptId path string true "Canonical Concept ID"
// @Param projectionId path string true "Projection ID"
// @Success 204 "Deletion successful"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Projection or concept not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /equivalences/concepts/{conceptId}/projections/{projectionId} [delete]
func (handler *Handler) DeleteCanonicalProjection(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("conceptId"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_CONCEPT_ID",
			Timestamp: time.Now(),
		})
	}

	projectionID, err := uuid.Parse(echoCtx.Param("projectionId"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid projection id format",
			Code:      "INVALID_PROJECTION_ID",
			Timestamp: time.Now(),
		})
	}

	if err := handler.service.DeleteProjection(echoCtx.Request().Context(), conceptID, projectionID); err != nil {
		// Check if it's a not found error
		if strings.Contains(err.Error(), "not found") {
			return echoCtx.JSON(http.StatusNotFound, ErrorResponse{
				Error:     err.Error(),
				Code:      "NOT_FOUND",
				Timestamp: time.Now(),
			})
		}
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to delete projection: " + err.Error(),
			Code:      "DELETE_ERROR",
			Timestamp: time.Now(),
		})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}
