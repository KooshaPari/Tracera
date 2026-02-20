package handlers

import (
	"net/http"
	"strings"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/temporal"
)

// VersionDiffHandler handles version diff operations
type VersionDiffHandler struct {
	diffService *temporal.DiffService
}

// NewVersionDiffHandler creates a new version diff handler
func NewVersionDiffHandler(diffService *temporal.DiffService) *VersionDiffHandler {
	return &VersionDiffHandler{
		diffService: diffService,
	}
}

// CompareVersionsRequest represents a request to compare two versions
type CompareVersionsRequest struct {
	FromVersionID string `query:"from" validate:"required"`
	ToVersionID   string `query:"to" validate:"required"`
}

// CompareVersionsResponse represents the response from comparing versions
type CompareVersionsResponse struct {
	VersionDiff *temporal.VersionDiff `json:"version_diff"`
	Status      string                `json:"status"`
	Message     string                `json:"message,omitempty"`
}

// CompareVersions godoc
// @Summary Compare two versions
// @Description Returns the differences between two project versions
// @Tags versions
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param from query string true "Source version ID"
// @Param to query string true "Target version ID"
// @Success 200 {object} CompareVersionsResponse "Diff result"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Version not found"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Security ApiKeyAuth
// @Router /api/v1/projects/{projectId}/versions/compare [get]
func (h *VersionDiffHandler) CompareVersions(c echo.Context) error {
	projectID := c.Param("projectId")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "project_id is required",
		})
	}

	fromVersionID := c.QueryParam("from")
	toVersionID := c.QueryParam("to")

	if fromVersionID == "" || toVersionID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "from and to version IDs are required",
		})
	}

	// Sanitize IDs
	fromVersionID = strings.TrimSpace(fromVersionID)
	toVersionID = strings.TrimSpace(toVersionID)

	// Calculate diff
	ctx := c.Request().Context()
	diff, err := h.diffService.CalculateVersionDiff(ctx, fromVersionID, toVersionID)
	if err != nil {
		// Log error for debugging
		c.Logger().Errorf("Failed to calculate version diff: %v", err)

		// Return appropriate error based on error type
		if strings.Contains(err.Error(), "invalid") {
			return c.JSON(http.StatusBadRequest, ErrorResponse{
				Error: "Invalid version ID format",
			})
		}

		if strings.Contains(err.Error(), "not found") {
			return c.JSON(http.StatusNotFound, ErrorResponse{
				Error: "Version not found",
			})
		}

		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "Failed to compare versions",
		})
	}

	return c.JSON(http.StatusOK, CompareVersionsResponse{
		VersionDiff: diff,
		Status:      "success",
		Message:     "",
	})
}

// GetVersionDiffSummary godoc
// @Summary Get summary of version differences
// @Description Returns a high-level summary of changes between two versions
// @Tags versions
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param from query string true "Source version ID"
// @Param to query string true "Target version ID"
// @Success 200 {object} map[string]interface{} "Diff summary"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Version not found"
// @Security ApiKeyAuth
// @Router /api/v1/projects/{projectId}/versions/compare/summary [get]
func (h *VersionDiffHandler) GetVersionDiffSummary(c echo.Context) error {
	projectID := c.Param("projectId")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "project_id is required",
		})
	}

	fromVersionID := c.QueryParam("from")
	toVersionID := c.QueryParam("to")

	if fromVersionID == "" || toVersionID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "from and to version IDs are required",
		})
	}

	ctx := c.Request().Context()
	summary, err := h.diffService.CompareVersions(ctx, fromVersionID, toVersionID)
	if err != nil {
		c.Logger().Errorf("Failed to get version diff summary: %v", err)
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: "Failed to get version summary",
		})
	}

	return c.JSON(http.StatusOK, summary)
}

// BulkCompareVersionsRequest represents a request to compare multiple version pairs
type BulkCompareVersionsRequest struct {
	Comparisons []VersionComparisonPair `json:"comparisons" validate:"required"`
}

// VersionComparisonPair represents a single comparison pair
type VersionComparisonPair struct {
	FromVersionID string `json:"from_version_id" validate:"required"`
	ToVersionID   string `json:"to_version_id" validate:"required"`
}

// BulkCompareVersions godoc
// @Summary Compare multiple version pairs
// @Description Returns differences for multiple version pairs in a single request
// @Tags versions
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param request body BulkCompareVersionsRequest true "Comparison pairs"
// @Success 200 {object} map[string]interface{} "Bulk diff results"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Security ApiKeyAuth
// @Router /api/v1/projects/{projectId}/versions/compare/bulk [post]
func (h *VersionDiffHandler) BulkCompareVersions(c echo.Context) error {
	projectID := c.Param("projectId")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "project_id is required",
		})
	}

	var req BulkCompareVersionsRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "Invalid request body",
		})
	}

	if len(req.Comparisons) == 0 {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "At least one comparison pair is required",
		})
	}

	// Limit bulk operations to prevent abuse
	const maxComparisons = 10
	if len(req.Comparisons) > maxComparisons {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error: "Too many comparison pairs (max: 10)",
		})
	}

	ctx := c.Request().Context()
	results := make(map[string]interface{})

	for index, pair := range req.Comparisons {
		key := pair.FromVersionID + "_" + pair.ToVersionID
		diff, err := h.diffService.CalculateVersionDiff(ctx, pair.FromVersionID, pair.ToVersionID)
		if err != nil {
			results[key] = map[string]interface{}{
				"error": err.Error(),
			}
		} else {
			results[key] = diff
		}

		// Prevent overwhelming the system
		if index >= maxComparisons-1 {
			break
		}
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"status":  "success",
		"results": results,
	})
}
