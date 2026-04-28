package handlers

import (
	"fmt"
	"net/http"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

// ChaosHandler handles chaos engineering and zombie detection requests
type ChaosHandler struct {
	chaosClient *clients.ChaosClient
}

// NewChaosHandler creates a new chaos handler
func NewChaosHandler(chaosClient *clients.ChaosClient) *ChaosHandler {
	return &ChaosHandler{
		chaosClient: chaosClient,
	}
}

// DetectZombiesRequest represents the HTTP request body
type DetectZombiesRequest struct {
	ProjectID string `json:"project_id" validate:"required"`
}

// DetectZombies detects zombie items in a project
func (h *ChaosHandler) DetectZombies(echoCtx echo.Context) error {
	var req DetectZombiesRequest
	if err := echoCtx.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid request body")
	}

	if err := echoCtx.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	report, err := h.chaosClient.DetectZombies(echoCtx.Request().Context(), clients.DetectZombiesRequest{
		ProjectID: req.ProjectID,
	})
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to detect zombies: %v", err))
	}

	return echoCtx.JSON(http.StatusOK, report)
}

// AnalyzeImpact analyzes the impact of an item
func (h *ChaosHandler) AnalyzeImpact(c echo.Context) error {
	itemID := c.Param("itemId")
	if itemID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "item_id is required")
	}

	analysis, err := h.chaosClient.AnalyzeImpact(c.Request().Context(), itemID)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, fmt.Sprintf("failed to analyze impact: %v", err))
	}

	return c.JSON(http.StatusOK, analysis)
}

// RegisterChaosRoutes registers chaos handler routes
func RegisterChaosRoutes(e *echo.Group, chaosClient *clients.ChaosClient) {
	handler := NewChaosHandler(chaosClient)

	chaos := e.Group("/chaos")
	chaos.POST("/detect-zombies", handler.DetectZombies)
	chaos.GET("/impact/:itemId", handler.AnalyzeImpact)
}
