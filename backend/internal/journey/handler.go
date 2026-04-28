package journey

import (
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Handler provides HTTP endpoints for journey operations
type Handler struct {
	pool        *pgxpool.Pool
	detector    Detector
	journeyRepo Repository
}

const (
	defaultQueryLimit = 50
	maxQueryLimit     = 500
	minScoreValue     = 0.0
	maxScoreValue     = 1.0
)

// NewHandler creates a new journey handler with all dependencies
func NewHandler(
	pool *pgxpool.Pool,
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	journeyRepo Repository,
	config *DetectionConfig,
) *Handler {
	// Use default config if not provided
	if config == nil {
		config = &DetectionConfig{
			MinPathLength:       defaultMinPathLength,
			MaxPathLength:       defaultMaxPathLength,
			MinFrequency:        defaultMinFrequency,
			MinScore:            defaultMinScore,
			AllowCycles:         false,
			GroupSimilar:        true,
			SimilarityThreshold: defaultSimilarityThreshold,
		}
	}

	return &Handler{
		pool:        pool,
		detector:    NewJourneyDetector(itemRepo, linkRepo, config),
		journeyRepo: journeyRepo,
	}
}

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

// validateDetectRequest validates a detection request
func (h *Handler) validateDetectRequest(req *DetectJourneysRequest) error {
	if req.ProjectID == "" {
		return errors.New("project_id is required")
	}
	if req.MinScore < minScoreValue || req.MinScore > maxScoreValue {
		return errors.New("min_score must be between 0 and 1")
	}
	if req.MaxResults < 0 {
		return errors.New("max_results must be non-negative")
	}
	for _, t := range req.Types {
		if t != UserFlow && t != DataPath && t != CallChain && t != TestTrace {
			return fmt.Errorf("invalid journey type: %s", t)
		}
	}
	return nil
}

// parseLimit parses and validates limit parameter
func parseLimit(limitStr string) int {
	limit := defaultQueryLimit
	if limitStr != "" {
		if parsed, err := strconv.Atoi(limitStr); err == nil {
			if parsed > 0 && parsed <= maxQueryLimit {
				limit = parsed
			}
		}
	}
	return limit
}

// parseOffset parses and validates offset parameter
func parseOffset(offsetStr string) int {
	offset := 0 // default
	if offsetStr != "" {
		if parsed, err := strconv.Atoi(offsetStr); err == nil && parsed >= 0 {
			offset = parsed
		}
	}
	return offset
}

// parseScore parses a score parameter
func parseScore(scoreStr string) float64 {
	if scoreStr == "" {
		return minScoreValue
	}
	score, err := strconv.ParseFloat(scoreStr, 64)
	if err != nil {
		return minScoreValue
	}
	if score < minScoreValue {
		score = minScoreValue
	} else if score > maxScoreValue {
		score = maxScoreValue
	}
	return score
}

// RegisterRoutes registers the journey routes with an Echo group
func (h *Handler) RegisterRoutes(group *echo.Group) {
	journey := group.Group("/journeys")

	// Journey detection and management
	journey.GET("", h.ListJourneys)
	journey.POST("/detect", h.DetectJourneys)
	journey.GET("/:id", h.GetJourney)
	journey.PUT("/:id", h.UpdateJourney)
	journey.DELETE("/:id", h.DeleteJourney)

	// Journey steps
	journey.GET("/:id/steps", h.GetJourneySteps)
	journey.POST("/:id/steps", h.AddJourneyStep)
	journey.DELETE("/:id/steps/:itemId", h.RemoveJourneyStep)

	// Journey types
	journey.GET("/user-flows", h.GetUserFlows)
	journey.GET("/data-paths", h.GetDataPaths)
	journey.GET("/call-chains", h.GetCallChains)

	// Statistics
	journey.GET("/stats", h.GetJourneyStats)

	// Visualization
	journey.GET("/:id/visualization", h.GetJourneyVisualization)

	// Project-scoped routes
	p := group.Group("/projects/:projectId/journeys")
	p.GET("", h.ListProjectJourneys)
	p.POST("", h.CreateProjectJourney)
	p.POST("/detect", h.DetectProjectJourneys)
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

// DetectJourneysRequest represents a request to detect journeys
type DetectJourneysRequest struct {
	ProjectID   string  `json:"project_id" binding:"required"`
	Types       []Type  `json:"types,omitempty"`
	MinScore    float64 `json:"min_score,omitempty"`
	MaxResults  int     `json:"max_results,omitempty"`
	StartNodeID *string `json:"start_node_id,omitempty"`
	EndNodeID   *string `json:"end_node_id,omitempty"`
}

// ListJourneysRequest represents a request to list journeys
type ListJourneysRequest struct {
	ProjectID string  `form:"project_id" binding:"required"`
	Type      string  `form:"type"`
	MinScore  float64 `form:"min_score"`
	Limit     int     `form:"limit"`
	Offset    int     `form:"offset"`
	SortBy    string  `form:"sort_by"`
}

// UpdateJourneyRequest represents a request to update a journey
type UpdateJourneyRequest struct {
	Name        string         `json:"name,omitempty"`
	Description string         `json:"description,omitempty"`
	Type        string         `json:"type,omitempty"`
	ItemIDs     []string       `json:"item_ids,omitempty"`
	Metadata    map[string]any `json:"metadata,omitempty"`
}

// CreateJourneyRequest represents a request to create a journey
type CreateJourneyRequest struct {
	Name        string         `json:"name" binding:"required"`
	Description string         `json:"description,omitempty"`
	Type        string         `json:"type" binding:"required"`
	ItemIDs     []string       `json:"item_ids,omitempty"`
	Metadata    map[string]any `json:"metadata,omitempty"`
}

// AddStepRequest represents a request to add a step to a journey
type AddStepRequest struct {
	ItemID string `json:"item_id" binding:"required"`
	Order  int    `json:"order,omitempty"`
}

// Step represents a step in a journey
type Step struct {
	ItemID      string `json:"item_id"`
	Order       int    `json:"order"`
	Duration    int    `json:"duration,omitempty"`
	Description string `json:"description,omitempty"`
}

// Step is kept for backwards compatibility with repository interfaces.
// ============================================================================
// RESPONSE TYPES
// ============================================================================

// ListJourneysResponse contains journeys with pagination
type ListJourneysResponse struct {
	Data    []*DerivedJourney `json:"data"`
	Total   int               `json:"total"`
	Limit   int               `json:"limit"`
	Offset  int               `json:"offset"`
	HasMore bool              `json:"has_more"`
}

// DetectJourneysResponse contains detection results
type DetectJourneysResponse struct {
	Journeys   []*DerivedJourney `json:"journeys"`
	Stats      DetectionStats    `json:"stats"`
	DetectedAt time.Time         `json:"detected_at"`
}

// DetectionStats contains statistics about detection run
type DetectionStats struct {
	TotalPaths        int            `json:"total_paths"`
	ValidPaths        int            `json:"valid_paths"`
	DetectionTimeMs   int64          `json:"detection_time_ms"`
	ByType            map[string]int `json:"by_type"`
	AverageScore      float64        `json:"average_score"`
	AveragePathLength float64        `json:"average_path_length"`
}

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error string `json:"error"`
}

// ============================================================================
// HANDLER METHODS
// ============================================================================

// ListJourneys handles GET /journeys
// @Summary List all journeys
// @Description Returns a paginated list of journeys
// @Tags journeys
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Param type query string false "Journey type filter"
// @Param min_score query number false "Minimum score threshold"
// @Param limit query integer false "Page size (default: 50)"
// @Param offset query integer false "Pagination offset"
// @Success 200 {object} ListJourneysResponse "List of journeys"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /journeys [get]
func (h *Handler) ListJourneys(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	return h.listJourneysWithProjectID(c, projectID, "project_id is required")
}

// DetectJourneys handles POST /journeys/detect
// @Summary Detect journeys in a project
// @Description Analyzes the project graph to detect user flows, data paths, and call chains
// @Tags journeys
// @Accept json
// @Produce json
// @Param body body DetectJourneysRequest true "Detection parameters"
// @Success 200 {object} DetectJourneysResponse "Detection results"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /journeys/detect [post]
func (h *Handler) DetectJourneys(c echo.Context) error {
	var req DetectJourneysRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}

	if err := h.validateDetectRequest(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
	}

	result, err := h.detector.DetectJourneys(c.Request().Context(), req.ProjectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "detection failed: " + err.Error()})
	}

	// Build type breakdown
	byType := make(map[string]int)
	var totalScore float64
	var totalLength float64
	for _, j := range result.Journeys {
		byType[string(j.Type)]++
		totalScore += j.Score
		totalLength += float64(len(j.NodeIDs))
	}

	avgScore := 0.0
	avgLength := 0.0
	if len(result.Journeys) > 0 {
		avgScore = totalScore / float64(len(result.Journeys))
		avgLength = totalLength / float64(len(result.Journeys))
	}

	response := DetectJourneysResponse{
		Journeys: result.Journeys,
		Stats: DetectionStats{
			TotalPaths:        result.TotalPaths,
			ValidPaths:        result.ValidPaths,
			DetectionTimeMs:   result.DetectionTimeMs,
			ByType:            byType,
			AverageScore:      avgScore,
			AveragePathLength: avgLength,
		},
		DetectedAt: time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}

// GetJourney handles GET /journeys/:id
// @Summary Get a specific journey
// @Description Returns details of a specific journey
// @Tags journeys
// @Accept json
// @Produce json
// @Param id path string true "Journey ID"
// @Success 200 {object} DerivedJourney "Journey details"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Journey not found"
// @Router /journeys/{id} [get]
func (h *Handler) GetJourney(c echo.Context) error {
	journeyID := c.Param("id")
	if journeyID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
	}

	journey, err := h.journeyRepo.GetByID(c.Request().Context(), journeyID)
	if err != nil {
		notFoundError := &NotFoundError{}
		if errors.As(err, &notFoundError) {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
		}
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch journey"})
	}

	return c.JSON(http.StatusOK, journey)
}

// DeleteJourney handles DELETE /journeys/:id
// @Summary Delete a journey
// @Description Deletes a specific journey
// @Tags journeys
// @Accept json
// @Produce json
// @Param id path string true "Journey ID"
// @Success 204 "Deletion successful"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Journey not found"
// @Router /journeys/{id} [delete]
func (h *Handler) DeleteJourney(c echo.Context) error {
	journeyID := c.Param("id")
	if journeyID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
	}

	err := h.journeyRepo.Delete(c.Request().Context(), journeyID)
	if err != nil {
		notFoundError := &NotFoundError{}
		if errors.As(err, &notFoundError) {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
		}
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to delete journey"})
	}

	return c.NoContent(http.StatusNoContent)
}

// UpdateJourney handles PUT /journeys/:id
// @Summary Update a journey
// @Description Updates a specific journey
// @Tags journeys
// @Accept json
// @Produce json
// applyJourneyUpdates applies update request fields to a journey
func applyJourneyUpdates(journey *DerivedJourney, req UpdateJourneyRequest) {
	if req.Name != "" {
		journey.Name = req.Name
	}
	if req.Description != "" {
		journey.Metadata.Description = req.Description
	}
	if req.Type != "" {
		journey.Type = Type(req.Type)
	}
	if len(req.ItemIDs) > 0 {
		journey.NodeIDs = req.ItemIDs
	}
	if len(req.Metadata) > 0 {
		if journey.Metadata.CustomData == nil {
			journey.Metadata.CustomData = make(map[string]interface{})
		}
		for k, v := range req.Metadata {
			journey.Metadata.CustomData[k] = v
		}
	}
	journey.UpdatedAt = time.Now()
}

// UpdateJourney handles PUT /journeys/:id
//
// @Param id path string true "Journey ID"
// @Param body body UpdateJourneyRequest true "Update parameters"
// @Success 200 {object} DerivedJourney "Updated journey"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Journey not found"
// @Router /journeys/{id} [put]
func (h *Handler) UpdateJourney(c echo.Context) error {
	journeyID := c.Param("id")
	if journeyID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
	}

	var req UpdateJourneyRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}

	journey, err := h.journeyRepo.GetByID(c.Request().Context(), journeyID)
	if err != nil {
		notFoundError := &NotFoundError{}
		if errors.As(err, &notFoundError) {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
		}
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch journey"})
	}

	applyJourneyUpdates(journey, req)

	if err := h.journeyRepo.Update(c.Request().Context(), journey); err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to update journey"})
	}

	return c.JSON(http.StatusOK, journey)
}

// GetJourneySteps handles GET /journeys/:id/steps
// @Summary Get journey steps
// @Description Returns the ordered steps of a journey
// @Tags journeys
// @Accept json
// @Produce json
// @Param id path string true "Journey ID"
// @Success 200 {array} Step "Journey steps"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Journey not found"
// @Router /journeys/{id}/steps [get]
func (h *Handler) GetJourneySteps(c echo.Context) error {
	journeyID := c.Param("id")
	if journeyID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
	}

	steps, err := h.journeyRepo.GetSteps(c.Request().Context(), journeyID)
	if err != nil {
		notFoundError := &NotFoundError{}
		if errors.As(err, &notFoundError) {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
		}
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch steps"})
	}

	return c.JSON(http.StatusOK, steps)
}

// AddJourneyStep handles POST /journeys/:id/steps
// @Summary Add a step to a journey
// @Description Adds an item as a step in the journey
// @Tags journeys
// @Accept json
// @Produce json
// @Param id path string true "Journey ID"
// @Param body body AddStepRequest true "Step details"
// @Success 200 {object} DerivedJourney "Updated journey"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Journey not found"
// @Router /journeys/{id}/steps [post]
func (h *Handler) AddJourneyStep(c echo.Context) error {
	journeyID := c.Param("id")
	if journeyID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
	}

	var req AddStepRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}

	if req.ItemID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "itemId is required"})
	}

	step := &Step{
		ItemID: req.ItemID,
		Order:  req.Order,
	}

	err := h.journeyRepo.AddStep(c.Request().Context(), journeyID, step)
	if err != nil {
		notFoundError := &NotFoundError{}
		if errors.As(err, &notFoundError) {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
		}
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to add step"})
	}

	journey, err := h.journeyRepo.GetByID(c.Request().Context(), journeyID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to retrieve updated journey"})
	}
	return c.JSON(http.StatusOK, journey)
}

// RemoveJourneyStep handles DELETE /journeys/:id/steps/:itemId
// @Summary Remove a step from a journey
// @Description Removes an item from the journey
// @Tags journeys
// @Accept json
// @Produce json
// @Param id path string true "Journey ID"
// @Param itemId path string true "Item ID to remove"
// @Success 204 "Step removed successfully"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 404 {object} ErrorResponse "Journey or step not found"
// @Router /journeys/{id}/steps/{itemId} [delete]
func (h *Handler) RemoveJourneyStep(c echo.Context) error {
	journeyID := c.Param("id")
	itemID := c.Param("itemId")
	if journeyID == "" || itemID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id and item id are required"})
	}

	err := h.journeyRepo.RemoveStep(c.Request().Context(), journeyID, itemID)
	if err != nil {
		notFoundError := &NotFoundError{}
		if errors.As(err, &notFoundError) {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
		}
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to remove step"})
	}

	return c.NoContent(http.StatusNoContent)
}

// CreateProjectJourney handles POST /projects/:projectId/journeys
// @Summary Create a new journey
// @Description Creates a manual journey in the project
// @Tags journeys
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param body body CreateJourneyRequest true "Journey details"
// @Success 201 {object} DerivedJourney "Created journey"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /projects/{projectId}/journeys [post]
func (h *Handler) CreateProjectJourney(c echo.Context) error {
	projectID := c.Param("projectId")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "projectId is required"})
	}

	var req CreateJourneyRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}

	if req.Name == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "name is required"})
	}
	if req.Type == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "type is required"})
	}

	now := time.Now()
	journey := &DerivedJourney{
		ProjectID: projectID,
		Name:      req.Name,
		Type:      Type(req.Type),
		NodeIDs:   req.ItemIDs,
		Links:     []Link{},
		Metadata: Metadata{
			Description:  req.Description,
			CustomData:   req.Metadata,
			LastDetected: now,
		},
		Score:     1.0,
		CreatedAt: now,
		UpdatedAt: now,
	}

	if err := h.journeyRepo.Create(c.Request().Context(), journey); err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to create journey"})
	}

	return c.JSON(http.StatusCreated, journey)
}

// GetUserFlows handles GET /journeys/user-flows
// @Summary Get detected user flows
// @Description Returns user flows (UI navigation paths) for a project
// @Tags journeys
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {array} DerivedJourney "User flows"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Router /journeys/user-flows [get]
func (h *Handler) GetUserFlows(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "project_id is required"})
	}

	journeys, err := h.detector.DetectUserFlows(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "detection failed: " + err.Error()})
	}

	return c.JSON(http.StatusOK, journeys)
}

// GetDataPaths handles GET /journeys/data-paths
// @Summary Get detected data paths
// @Description Returns data flow paths for a project
// @Tags journeys
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {array} DerivedJourney "Data paths"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Router /journeys/data-paths [get]
func (h *Handler) GetDataPaths(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "project_id is required"})
	}

	journeys, err := h.detector.DetectDataPaths(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "detection failed: " + err.Error()})
	}

	return c.JSON(http.StatusOK, journeys)
}

// GetCallChains handles GET /journeys/call-chains
// @Summary Get detected call chains
// @Description Returns function call chains for a project
// @Tags journeys
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {array} DerivedJourney "Call chains"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Router /journeys/call-chains [get]
func (h *Handler) GetCallChains(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "project_id is required"})
	}

	journeys, err := h.detector.DetectCallChains(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "detection failed: " + err.Error()})
	}

	return c.JSON(http.StatusOK, journeys)
}

// GetJourneyStats handles GET /journeys/stats
// @Summary Get journey statistics
// @Description Returns aggregate statistics about detected journeys
// @Tags journeys
// @Accept json
// @Produce json
// @Param project_id query string true "Project ID"
// @Success 200 {object} Stats "Journey statistics"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Router /journeys/stats [get]
func (h *Handler) GetJourneyStats(c echo.Context) error {
	projectID := c.QueryParam("project_id")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "project_id is required"})
	}

	stats, err := h.detector.GetJourneyStats(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "stats calculation failed: " + err.Error()})
	}

	return c.JSON(http.StatusOK, stats)
}

// GetJourneyVisualization handles GET /journeys/:id/visualization
// @Summary Get journey visualization data
// @Description Returns formatted data for rendering a journey visualization
// @Tags journeys
// @Accept json
// @Produce json
// @Param id path string true "Journey ID"
// @Success 200 {object} VisualizationData "Visualization data"
// @Failure 400 {object} ErrorResponse "Invalid ID format"
// @Failure 404 {object} ErrorResponse "Journey not found"
// @Router /journeys/{id}/visualization [get]
func (h *Handler) GetJourneyVisualization(c echo.Context) error {
	journeyID := c.Param("id")
	if journeyID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
	}

	journey, err := h.journeyRepo.GetByID(c.Request().Context(), journeyID)
	if err != nil {
		notFoundError := &NotFoundError{}
		if errors.As(err, &notFoundError) {
			return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
		}
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch journey"})
	}

	// Build visualization data
	nodes := make(map[string]*VisualizationNode)
	edges := make([]*VisualizationEdge, 0, len(journey.Links))

	for i, nodeID := range journey.NodeIDs {
		_ = i // Use index for ordering if needed
		nodes[nodeID] = &VisualizationNode{
			ID:    nodeID,
			Label: nodeID,
			Type:  "node",
			Size:  1,
			Color: "#4CAF50",
		}
	}

	for _, link := range journey.Links {
		edges = append(edges, &VisualizationEdge{
			Source: link.SourceID,
			Target: link.TargetID,
			Type:   link.Type,
			Weight: link.Weight,
		})
	}

	visualization := VisualizationData{
		Journey: journey,
		Nodes:   nodes,
		Edges:   edges,
	}

	return c.JSON(http.StatusOK, visualization)
}

// ListProjectJourneys handles GET /projects/:projectId/journeys
// @Summary List journeys for a project
// @Description Returns journeys for a specific project
// @Tags journeys
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param type query string false "Journey type filter"
// @Param limit query integer false "Page size"
// @Param offset query integer false "Pagination offset"
// @Success 200 {object} ListJourneysResponse "List of journeys"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Router /projects/{projectId}/journeys [get]
func (h *Handler) ListProjectJourneys(c echo.Context) error {
	projectID := c.Param("projectId")
	return h.listJourneysWithProjectID(c, projectID, "projectId is required")
}

func (h *Handler) listJourneysWithProjectID(c echo.Context, projectID string, missingMsg string) error {
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: missingMsg})
	}

	limit := parseLimit(c.QueryParam("limit"))
	offset := parseOffset(c.QueryParam("offset"))
	minScore := parseScore(c.QueryParam("min_score"))

	journeyType := c.QueryParam("type")
	var jType *Type
	if journeyType != "" {
		t := Type(journeyType)
		jType = &t
	}

	filter := Filter{
		ProjectID: &projectID,
		Type:      jType,
		MinScore:  minScore,
		Limit:     limit,
		Offset:    offset,
		SortBy:    c.QueryParam("sort_by"),
	}

	journeys, err := h.journeyRepo.List(c.Request().Context(), filter)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch journeys"})
	}

	total, err := h.journeyRepo.Count(c.Request().Context(), projectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to count journeys"})
	}

	response := ListJourneysResponse{
		Data:    journeys,
		Total:   int(total),
		Limit:   limit,
		Offset:  offset,
		HasMore: offset+limit < int(total),
	}

	return c.JSON(http.StatusOK, response)
}

// DetectProjectJourneys handles POST /projects/:projectId/journeys/detect
// @Summary Detect journeys in a project
// @Description Analyzes the project graph to detect journeys
// @Tags journeys
// @Accept json
// @Produce json
// @Param projectId path string true "Project ID"
// @Param body body DetectJourneysRequest false "Detection parameters"
// @Success 200 {object} DetectJourneysResponse "Detection results"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Router /projects/{projectId}/journeys/detect [post]
func (h *Handler) DetectProjectJourneys(c echo.Context) error {
	projectID := c.Param("projectId")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "projectId is required"})
	}

	var req DetectJourneysRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "invalid request body"})
	}
	req.ProjectID = projectID

	result, err := h.detector.DetectJourneys(c.Request().Context(), req.ProjectID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "detection failed: " + err.Error()})
	}

	byType := make(map[string]int)
	for _, j := range result.Journeys {
		byType[string(j.Type)]++
	}

	response := DetectJourneysResponse{
		Journeys: result.Journeys,
		Stats: DetectionStats{
			TotalPaths:      result.TotalPaths,
			ValidPaths:      result.ValidPaths,
			DetectionTimeMs: result.DetectionTimeMs,
			ByType:          byType,
		},
		DetectedAt: time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}
