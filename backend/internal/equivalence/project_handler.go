package equivalence

import (
	"net/http"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// ListProjectEquivalences handles GET /projects/:projectId/equivalences
func (handler *Handler) ListProjectEquivalences(echoCtx echo.Context) error {
	projectIDStr := echoCtx.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "Invalid project ID format",
			Code:      "INVALID_PROJECT_ID",
			Details:   nil,
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

// DetectProjectEquivalences handles POST /projects/:projectId/equivalences/detect
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
			Details:   nil,
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
			Details:   nil,
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
func (handler *Handler) ListProjectConcepts(ctx echo.Context) error {
	projectIDStr := ctx.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid project id format",
			Code:      "INVALID_PROJECT_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	concepts, err := handler.service.GetCanonicalConcepts(ctx.Request().Context(), projectID)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_CONCEPTS_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	return ctx.JSON(http.StatusOK, concepts)
}

// CreateProjectConcept handles POST /projects/:projectId/concepts
func (handler *Handler) CreateProjectConcept(ctx echo.Context) error {
	projectIDStr := ctx.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid project id format",
			Code:      "INVALID_PROJECT_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	var req CreateCanonicalConceptRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if req.Name == "" {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "name is required",
			Code:      "MISSING_NAME",
			Details:   nil,
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
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	concept, err := handler.service.CreateCanonicalConcept(ctx.Request().Context(), &req, userID)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to create concept: " + err.Error(),
			Code:      "CREATE_ERROR",
			Details:   nil,
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

// Helpers

func parseProjectIDPathParam(ctx echo.Context, param string) (uuid.UUID, *ErrorResponse, int) {
	projectID, err := uuid.Parse(ctx.Param(param))
	if err != nil {
		return uuid.Nil, &ErrorResponse{
			Error:     "Invalid project ID format",
			Code:      "INVALID_PROJECT_ID",
			Details:   nil,
			Timestamp: time.Now(),
		}, http.StatusBadRequest
	}

	return projectID, nil, http.StatusOK
}
