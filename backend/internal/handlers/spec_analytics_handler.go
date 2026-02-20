package handlers

import (
	"fmt"
	"net/http"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

// SpecAnalyticsHandler handles specification analytics requests
type SpecAnalyticsHandler struct {
	specAnalyticsClient *clients.SpecAnalyticsClient
}

// NewSpecAnalyticsHandler creates a new specification analytics handler
func NewSpecAnalyticsHandler(specAnalyticsClient *clients.SpecAnalyticsClient) *SpecAnalyticsHandler {
	return &SpecAnalyticsHandler{
		specAnalyticsClient: specAnalyticsClient,
	}
}

// AnalyzeSpecRequest represents the HTTP request for spec analysis
type AnalyzeSpecRequest struct {
	SpecID    string `json:"spec_id" validate:"required"`
	Content   string `json:"content" validate:"required"`
	ProjectID string `json:"project_id" validate:"required"`
}

// BatchAnalyzeRequest represents the HTTP request for batch spec analysis
type BatchAnalyzeRequest struct {
	Requests []AnalyzeSpecRequest `json:"requests" validate:"required,min=1,max=100"`
}

// AnalyzeSpec handles single specification analysis requests
// @Summary Analyze a specification
// @Description Analyzes a specification for ISO 29148 compliance, EARS patterns, and formal verification
// @Tags spec-analytics
// @Accept json
// @Produce json
// @Param request body AnalyzeSpecRequest true "Analyze spec request"
// @Success 200 {object} clients.SpecAnalysisResult "Analysis result"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /api/v1/spec-analytics/analyze [post]
func (h *SpecAnalyticsHandler) AnalyzeSpec(c echo.Context) error {
	var req AnalyzeSpecRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request body")
	}

	if err := c.Validate(req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	// Convert to client request
	clientReq := clients.AnalyzeSpecRequest{
		SpecID:    req.SpecID,
		Content:   req.Content,
		ProjectID: req.ProjectID,
	}

	result, err := h.specAnalyticsClient.AnalyzeSpec(c.Request().Context(), clientReq)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("Analysis failed: %v", err))
	}

	return c.JSON(http.StatusOK, result)
}

// BatchAnalyzeSpecs handles batch specification analysis requests
// @Summary Batch analyze specifications
// @Description Analyzes multiple specifications in parallel
// @Tags spec-analytics
// @Accept json
// @Produce json
// @Param request body BatchAnalyzeRequest true "Batch analyze request"
// @Success 200 {object} map[string]interface{} "Batch analysis results"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /api/v1/spec-analytics/batch-analyze [post]
func (h *SpecAnalyticsHandler) BatchAnalyzeSpecs(c echo.Context) error {
	var req BatchAnalyzeRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request body")
	}

	if err := c.Validate(req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	// Convert to client requests
	clientReqs := make([]clients.AnalyzeSpecRequest, len(req.Requests))
	for i, r := range req.Requests {
		clientReqs[i] = clients.AnalyzeSpecRequest{
			SpecID:    r.SpecID,
			Content:   r.Content,
			ProjectID: r.ProjectID,
		}
	}

	// Use optimized batch endpoint if available
	results, err := h.specAnalyticsClient.BatchAnalyzeSpecsOptimized(c.Request().Context(), clientReqs)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("Batch analysis failed: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"results": results,
		"count":   len(results),
	})
}

// ValidateISO29148 handles ISO 29148 compliance validation requests
// @Summary Validate ISO 29148 compliance
// @Description Checks if a specification complies with ISO 29148 standard
// @Tags spec-analytics
// @Accept json
// @Produce json
// @Param request body AnalyzeSpecRequest true "Validate request"
// @Success 200 {object} map[string]interface{} "Validation result"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /api/v1/spec-analytics/validate-iso29148 [post]
func (h *SpecAnalyticsHandler) ValidateISO29148(c echo.Context) error {
	var req AnalyzeSpecRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request body")
	}

	if err := c.Validate(req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	compliant, recommendations, err := h.specAnalyticsClient.ValidateISO29148Compliance(
		c.Request().Context(),
		req.SpecID,
		req.Content,
		req.ProjectID,
	)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("Validation failed: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"spec_id":         req.SpecID,
		"compliant":       compliant,
		"recommendations": recommendations,
	})
}

// GetEARSPatterns handles EARS pattern extraction requests
// @Summary Extract EARS patterns
// @Description Extracts EARS patterns from a specification
// @Tags spec-analytics
// @Accept json
// @Produce json
// @Param request body AnalyzeSpecRequest true "EARS patterns request"
// @Success 200 {object} map[string]interface{} "EARS patterns result"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Internal server error"
// @Router /api/v1/spec-analytics/ears-patterns [post]
func (h *SpecAnalyticsHandler) GetEARSPatterns(c echo.Context) error {
	var req AnalyzeSpecRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request body")
	}

	if err := c.Validate(req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	patterns, err := h.specAnalyticsClient.GetEARSPatterns(
		c.Request().Context(),
		req.SpecID,
		req.Content,
		req.ProjectID,
	)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("Pattern extraction failed: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"spec_id":  req.SpecID,
		"patterns": patterns,
	})
}

// RegisterSpecAnalyticsRoutes registers spec analytics handler routes
func RegisterSpecAnalyticsRoutes(e *echo.Group, specAnalyticsClient *clients.SpecAnalyticsClient) {
	handler := NewSpecAnalyticsHandler(specAnalyticsClient)

	specAnalytics := e.Group("/spec-analytics")
	specAnalytics.POST("/analyze", handler.AnalyzeSpec)
	specAnalytics.POST("/batch-analyze", handler.BatchAnalyzeSpecs)
	specAnalytics.POST("/validate-iso29148", handler.ValidateISO29148)
	specAnalytics.POST("/ears-patterns", handler.GetEARSPatterns)
}
