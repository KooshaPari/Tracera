package equivalence

import (
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

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

// CreateCanonicalConcept handles POST /equivalences/concepts
func (handler *Handler) CreateCanonicalConcept(echoCtx echo.Context) error {
	var req CreateCanonicalConceptRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if req.Name == "" {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "name is required",
			Code:      "MISSING_NAME",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if req.ProjectID == uuid.Nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "project_id is required",
			Code:      "MISSING_PROJECT_ID",
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

	concept, err := handler.service.CreateCanonicalConcept(echoCtx.Request().Context(), &req, userID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
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

	return echoCtx.JSON(http.StatusCreated, response)
}

// GetCanonicalConcept handles GET /equivalences/concepts/:id
func (handler *Handler) GetCanonicalConcept(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	concept, err := handler.service.GetCanonicalConcept(echoCtx.Request().Context(), conceptID)
	if err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if concept == nil {
		return echoCtx.JSON(http.StatusNotFound, ErrorResponse{
			Error:     "concept not found",
			Code:      "NOT_FOUND",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	return echoCtx.JSON(http.StatusOK, concept)
}

// UpdateCanonicalConcept handles PUT /equivalences/concepts/:id
func (handler *Handler) UpdateCanonicalConcept(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	var req CreateCanonicalConceptRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if req.Name == "" {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "name is required",
			Code:      "MISSING_NAME",
			Details:   nil,
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
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	return echoCtx.JSON(http.StatusOK, updated)
}

// DeleteCanonicalConcept handles DELETE /equivalences/concepts/:id
func (handler *Handler) DeleteCanonicalConcept(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("id"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if err := handler.service.DeleteCanonicalConcept(echoCtx.Request().Context(), conceptID); err != nil {
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to delete concept: " + err.Error(),
			Code:      "DELETE_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// GetConceptProjections handles GET /equivalences/concepts/:id/projections
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
				Details:   nil,
				Timestamp: time.Now(),
			})
		}
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "GET_PROJECTIONS_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	filtered := filterProjectionsByPerspective(projections, perspective)
	paginatedProjections := paginateProjections(filtered, limit, offset)
	perspectiveMap := buildPerspectiveBreakdown(filtered)

	response := GetProjectionsResponse{
		ConceptID:            conceptID,
		Concept:              nil,
		Projections:          paginatedProjections,
		PerspectiveBreakdown: perspectiveMap,
		Total:                int64(len(filtered)),
	}

	return echoCtx.JSON(http.StatusOK, response)
}

// CreateCanonicalProjection handles POST /equivalences/concepts/:id/projections
func (handler *Handler) CreateCanonicalProjection(ctx echo.Context) error {
	conceptID, err := uuid.Parse(ctx.Param("id"))
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_CONCEPT_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	var req CreateCanonicalProjectionRequest
	if err := ctx.Bind(&req); err != nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid request body",
			Code:      "INVALID_REQUEST",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if req.ItemID == uuid.Nil {
		return ctx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "item_id is required",
			Code:      "MISSING_ITEM_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	userID := getUserIDFromEchoContext(ctx)
	if userID == uuid.Nil {
		return ctx.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:     "user not authenticated",
			Code:      "UNAUTHORIZED",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	// Get the concept to extract project ID
	concept, err := handler.service.GetCanonicalConcept(ctx.Request().Context(), conceptID)
	if err != nil {
		return ctx.JSON(http.StatusNotFound, ErrorResponse{
			Error:     "concept not found",
			Code:      "NOT_FOUND",
			Details:   nil,
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
			Details:   nil,
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
func (handler *Handler) DeleteCanonicalProjection(echoCtx echo.Context) error {
	conceptID, err := uuid.Parse(echoCtx.Param("conceptId"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_CONCEPT_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	projectionID, err := uuid.Parse(echoCtx.Param("projectionId"))
	if err != nil {
		return echoCtx.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "invalid projection id format",
			Code:      "INVALID_PROJECTION_ID",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	if err := handler.service.DeleteProjection(echoCtx.Request().Context(), conceptID, projectionID); err != nil {
		// Check if it's a not found error
		if strings.Contains(err.Error(), "not found") {
			return echoCtx.JSON(http.StatusNotFound, ErrorResponse{
				Error:     err.Error(),
				Code:      "NOT_FOUND",
				Details:   nil,
				Timestamp: time.Now(),
			})
		}
		return echoCtx.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     "Failed to delete projection: " + err.Error(),
			Code:      "DELETE_ERROR",
			Details:   nil,
			Timestamp: time.Now(),
		})
	}

	return echoCtx.NoContent(http.StatusNoContent)
}

// Helpers

func parseConceptIDParam(c echo.Context) (uuid.UUID, *ErrorResponse, int) {
	conceptID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		return uuid.Nil, &ErrorResponse{
			Error:     "invalid concept id format",
			Code:      "INVALID_ID",
			Details:   nil,
			Timestamp: time.Now(),
		}, http.StatusBadRequest
	}

	return conceptID, nil, http.StatusOK
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
