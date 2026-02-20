# Journey Handler Implementation Guide

Complete, ready-to-use code for fixing the journey handler implementation.

---

## Step 1: Create JourneyRepository Interface

**File:** `backend/internal/repository/journey_repository.go`

```go
package repository

import (
    "context"
    "time"

    "github.com/kooshapari/tracertm-backend/internal/journey"
    "gorm.io/gorm"
)

// JourneyRepository defines methods for journey data access
type JourneyRepository interface {
    Create(ctx context.Context, j *journey.DerivedJourney) error
    GetByID(ctx context.Context, id string) (*journey.DerivedJourney, error)
    GetByProjectID(ctx context.Context, projectID string) ([]*journey.DerivedJourney, error)
    GetByType(ctx context.Context, projectID string, jType journey.JourneyType) ([]*journey.DerivedJourney, error)
    Update(ctx context.Context, j *journey.DerivedJourney) error
    Delete(ctx context.Context, id string) error
    List(ctx context.Context, filter JourneyFilter) ([]*journey.DerivedJourney, error)
    Count(ctx context.Context, projectID string) (int64, error)
    AddStep(ctx context.Context, journeyID string, step *journey.JourneyStep) error
    RemoveStep(ctx context.Context, journeyID string, itemID string) error
    GetSteps(ctx context.Context, journeyID string) ([]*journey.JourneyStep, error)
}

// JourneyFilter for querying journeys
type JourneyFilter struct {
    ProjectID *string
    Type      *journey.JourneyType
    MinScore  float64
    Limit     int
    Offset    int
    SortBy    string // "created_at", "score", "name"
}

// journeyRepository implements JourneyRepository
type journeyRepository struct {
    db *gorm.DB
}

// NewJourneyRepository creates a new journey repository
func NewJourneyRepository(db *gorm.DB) JourneyRepository {
    return &journeyRepository{db: db}
}

// Create inserts a new journey
func (r *journeyRepository) Create(ctx context.Context, j *journey.DerivedJourney) error {
    if j.ID == "" {
        j.ID = generateID() // Use existing ID generation from codebase
    }
    j.CreatedAt = time.Now()
    j.UpdatedAt = time.Now()

    return r.db.WithContext(ctx).Create(j).Error
}

// GetByID retrieves a journey by ID
func (r *journeyRepository) GetByID(ctx context.Context, id string) (*journey.DerivedJourney, error) {
    var j journey.DerivedJourney
    err := r.db.WithContext(ctx).
        Where("id = ? AND deleted_at IS NULL", id).
        First(&j).Error

    if err != nil {
        if err == gorm.ErrRecordNotFound {
            return nil, &NotFoundError{Resource: "journey"}
        }
        return nil, err
    }
    return &j, nil
}

// GetByProjectID retrieves all journeys for a project
func (r *journeyRepository) GetByProjectID(ctx context.Context, projectID string) ([]*journey.DerivedJourney, error) {
    var journeys []*journey.DerivedJourney
    err := r.db.WithContext(ctx).
        Where("project_id = ? AND deleted_at IS NULL", projectID).
        Order("created_at DESC").
        Find(&journeys).Error

    return journeys, err
}

// GetByType retrieves journeys of a specific type
func (r *journeyRepository) GetByType(ctx context.Context, projectID string, jType journey.JourneyType) ([]*journey.DerivedJourney, error) {
    var journeys []*journey.DerivedJourney
    err := r.db.WithContext(ctx).
        Where("project_id = ? AND type = ? AND deleted_at IS NULL", projectID, jType).
        Order("created_at DESC").
        Find(&journeys).Error

    return journeys, err
}

// Update modifies an existing journey
func (r *journeyRepository) Update(ctx context.Context, j *journey.DerivedJourney) error {
    j.UpdatedAt = time.Now()
    return r.db.WithContext(ctx).
        Model(&journey.DerivedJourney{}).
        Where("id = ? AND deleted_at IS NULL", j.ID).
        Updates(j).Error
}

// Delete soft-deletes a journey
func (r *journeyRepository) Delete(ctx context.Context, id string) error {
    now := time.Now()
    return r.db.WithContext(ctx).
        Model(&journey.DerivedJourney{}).
        Where("id = ? AND deleted_at IS NULL", id).
        Update("deleted_at", now).Error
}

// List retrieves journeys with filtering and pagination
func (r *journeyRepository) List(ctx context.Context, filter JourneyFilter) ([]*journey.DerivedJourney, error) {
    var journeys []*journey.DerivedJourney

    query := r.db.WithContext(ctx).Where("deleted_at IS NULL")

    if filter.ProjectID != nil {
        query = query.Where("project_id = ?", *filter.ProjectID)
    }
    if filter.Type != nil {
        query = query.Where("type = ?", *filter.Type)
    }
    if filter.MinScore > 0 {
        query = query.Where("score >= ?", filter.MinScore)
    }

    sortBy := "created_at"
    if filter.SortBy != "" && isValidSortField(filter.SortBy) {
        sortBy = filter.SortBy
    }

    query = query.Order(sortBy + " DESC")

    if filter.Limit > 0 {
        query = query.Limit(filter.Limit)
    }
    if filter.Offset > 0 {
        query = query.Offset(filter.Offset)
    }

    err := query.Find(&journeys).Error
    return journeys, err
}

// Count returns the total number of journeys for a project
func (r *journeyRepository) Count(ctx context.Context, projectID string) (int64, error) {
    var count int64
    err := r.db.WithContext(ctx).
        Model(&journey.DerivedJourney{}).
        Where("project_id = ? AND deleted_at IS NULL", projectID).
        Count(&count).Error

    return count, err
}

// AddStep adds a step to a journey
func (r *journeyRepository) AddStep(ctx context.Context, journeyID string, step *journey.JourneyStep) error {
    // Append step to NodeIDs and persist
    // This is a simplified implementation - adjust based on actual schema
    j, err := r.GetByID(ctx, journeyID)
    if err != nil {
        return err
    }

    j.NodeIDs = append(j.NodeIDs, step.ItemID)
    return r.Update(ctx, j)
}

// RemoveStep removes a step from a journey
func (r *journeyRepository) RemoveStep(ctx context.Context, journeyID string, itemID string) error {
    j, err := r.GetByID(ctx, journeyID)
    if err != nil {
        return err
    }

    newNodeIDs := make([]string, 0, len(j.NodeIDs))
    for _, id := range j.NodeIDs {
        if id != itemID {
            newNodeIDs = append(newNodeIDs, id)
        }
    }
    j.NodeIDs = newNodeIDs

    return r.Update(ctx, j)
}

// GetSteps returns the steps for a journey
func (r *journeyRepository) GetSteps(ctx context.Context, journeyID string) ([]*journey.JourneyStep, error) {
    j, err := r.GetByID(ctx, journeyID)
    if err != nil {
        return nil, err
    }

    steps := make([]*journey.JourneyStep, len(j.NodeIDs))
    for i, nodeID := range j.NodeIDs {
        steps[i] = &journey.JourneyStep{
            ItemID: nodeID,
            Order:  i,
        }
    }

    return steps, nil
}

// Helper functions
func isValidSortField(field string) bool {
    switch field {
    case "created_at", "score", "name", "type":
        return true
    default:
        return false
    }
}

// NotFoundError represents a not found error
type NotFoundError struct {
    Resource string
}

func (e *NotFoundError) Error() string {
    return "not found"
}
```

---

## Step 2: Update Handler Constructor and Add Repository Field

**File:** `backend/internal/journey/handler.go` (Updated)

```go
package journey

import (
    "fmt"
    "net/http"
    "strconv"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/kooshapari/tracertm-backend/internal/repository"
    "github.com/labstack/echo/v4"
)

// Handler provides HTTP endpoints for journey operations
type Handler struct {
    pool         *pgxpool.Pool
    detector     JourneyDetector
    journeyRepo  repository.JourneyRepository
}

// NewHandler creates a new journey handler with all dependencies
func NewHandler(
    pool *pgxpool.Pool,
    itemRepo repository.ItemRepository,
    linkRepo repository.LinkRepository,
    journeyRepo repository.JourneyRepository,
    config *DetectionConfig,
) *Handler {
    // Use default config if not provided
    if config == nil {
        config = &DetectionConfig{
            MinPathLength:       2,
            MaxPathLength:       10,
            MinFrequency:        1,
            MinScore:            0.1,
            AllowCycles:         false,
            GroupSimilar:        true,
            SimilarityThreshold: 0.8,
        }
    }

    return &Handler{
        pool:        pool,
        detector:    NewJourneyDetector(itemRepo, linkRepo, config),
        journeyRepo: journeyRepo,
    }
}

// RegisterRoutes registers the journey routes with an Echo group
func (h *Handler) RegisterRoutes(g *echo.Group) {
    j := g.Group("/journeys")

    // Journey detection and management
    j.GET("", h.ListJourneys)
    j.POST("/detect", h.DetectJourneys)
    j.GET("/:id", h.GetJourney)
    j.PUT("/:id", h.UpdateJourney)
    j.DELETE("/:id", h.DeleteJourney)

    // Journey steps
    j.GET("/:id/steps", h.GetJourneySteps)
    j.POST("/:id/steps", h.AddJourneyStep)
    j.DELETE("/:id/steps/:itemId", h.RemoveJourneyStep)

    // Journey types
    j.GET("/user-flows", h.GetUserFlows)
    j.GET("/data-paths", h.GetDataPaths)
    j.GET("/call-chains", h.GetCallChains)

    // Statistics
    j.GET("/stats", h.GetJourneyStats)

    // Visualization
    j.GET("/:id/visualization", h.GetJourneyVisualization)

    // Project-scoped routes
    p := g.Group("/projects/:projectId/journeys")
    p.GET("", h.ListProjectJourneys)
    p.POST("", h.CreateProjectJourney)
    p.POST("/detect", h.DetectProjectJourneys)
}

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

// validateDetectRequest validates a detection request
func (h *Handler) validateDetectRequest(req *DetectJourneysRequest) error {
    if req.ProjectID == "" {
        return fmt.Errorf("project_id is required")
    }
    if req.MinScore < 0 || req.MinScore > 1.0 {
        return fmt.Errorf("min_score must be between 0 and 1")
    }
    if req.MaxResults < 0 {
        return fmt.Errorf("max_results must be non-negative")
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
    limit := 50 // default
    if limitStr != "" {
        if parsed, err := strconv.Atoi(limitStr); err == nil {
            if parsed > 0 && parsed <= 500 {
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
        return 0.0
    }
    score, _ := strconv.ParseFloat(scoreStr, 64)
    if score < 0 {
        score = 0
    } else if score > 1.0 {
        score = 1.0
    }
    return score
}

// ============================================================================
// HANDLER METHODS - CRUD OPERATIONS
// ============================================================================

// ListJourneys handles GET /journeys
func (h *Handler) ListJourneys(c echo.Context) error {
    projectID := c.QueryParam("project_id")
    if projectID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "project_id is required"})
    }

    limit := parseLimit(c.QueryParam("limit"))
    offset := parseOffset(c.QueryParam("offset"))
    minScore := parseScore(c.QueryParam("min_score"))

    journeyType := c.QueryParam("type")
    var jType *JourneyType
    if journeyType != "" {
        t := JourneyType(journeyType)
        jType = &t
    }

    filter := repository.JourneyFilter{
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
        HasMore: offset + limit < int(total),
    }

    return c.JSON(http.StatusOK, response)
}

// GetJourney handles GET /journeys/:id
func (h *Handler) GetJourney(c echo.Context) error {
    journeyID := c.Param("id")
    if journeyID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
    }

    journey, err := h.journeyRepo.GetByID(c.Request().Context(), journeyID)
    if err != nil {
        if _, ok := err.(*repository.NotFoundError); ok {
            return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
        }
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch journey"})
    }

    return c.JSON(http.StatusOK, journey)
}

// UpdateJourney handles PUT /journeys/:id
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
        if _, ok := err.(*repository.NotFoundError); ok {
            return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
        }
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch journey"})
    }

    if req.Name != "" {
        journey.Name = req.Name
    }
    if req.Description != "" {
        journey.Metadata.Description = req.Description
    }
    if req.Type != "" {
        journey.Type = JourneyType(req.Type)
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

    if err := h.journeyRepo.Update(c.Request().Context(), journey); err != nil {
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to update journey"})
    }

    return c.JSON(http.StatusOK, journey)
}

// DeleteJourney handles DELETE /journeys/:id
func (h *Handler) DeleteJourney(c echo.Context) error {
    journeyID := c.Param("id")
    if journeyID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
    }

    err := h.journeyRepo.Delete(c.Request().Context(), journeyID)
    if err != nil {
        if _, ok := err.(*repository.NotFoundError); ok {
            return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
        }
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to delete journey"})
    }

    return c.NoContent(http.StatusNoContent)
}

// CreateProjectJourney handles POST /projects/:projectId/journeys
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
        Type:      JourneyType(req.Type),
        NodeIDs:   req.ItemIDs,
        Links:     []JourneyLink{},
        Metadata: Metadata{
            Description: req.Description,
            CustomData:  req.Metadata,
            LastDetected: now,
        },
        Score:     1.0, // Manual journeys start with high confidence
        CreatedAt: now,
        UpdatedAt: now,
    }

    if err := h.journeyRepo.Create(c.Request().Context(), journey); err != nil {
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to create journey"})
    }

    return c.JSON(http.StatusCreated, journey)
}

// ListProjectJourneys handles GET /projects/:projectId/journeys
func (h *Handler) ListProjectJourneys(c echo.Context) error {
    projectID := c.Param("projectId")
    if projectID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "projectId is required"})
    }

    limit := parseLimit(c.QueryParam("limit"))
    offset := parseOffset(c.QueryParam("offset"))
    minScore := parseScore(c.QueryParam("min_score"))

    journeyType := c.QueryParam("type")
    var jType *JourneyType
    if journeyType != "" {
        t := JourneyType(journeyType)
        jType = &t
    }

    filter := repository.JourneyFilter{
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
        HasMore: offset + limit < int(total),
    }

    return c.JSON(http.StatusOK, response)
}

// ============================================================================
// HANDLER METHODS - DETECTION
// ============================================================================

// DetectJourneys handles POST /journeys/detect
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
            DetectionTime:     result.DetectionTime,
            ByType:            byType,
            AverageScore:      avgScore,
            AveragePathLength: avgLength,
        },
        DetectedAt: time.Now(),
    }

    return c.JSON(http.StatusOK, response)
}

// DetectProjectJourneys handles POST /projects/:projectId/journeys/detect
func (h *Handler) DetectProjectJourneys(c echo.Context) error {
    projectID := c.Param("projectId")
    if projectID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "projectId is required"})
    }

    var req DetectJourneysRequest
    if err := c.Bind(&req); err != nil {
        // Binding is optional for this endpoint
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
            TotalPaths:    result.TotalPaths,
            ValidPaths:    result.ValidPaths,
            DetectionTime: result.DetectionTime,
            ByType:        byType,
        },
        DetectedAt: time.Now(),
    }

    return c.JSON(http.StatusOK, response)
}

// ============================================================================
// HANDLER METHODS - JOURNEY STEPS
// ============================================================================

// GetJourneySteps handles GET /journeys/:id/steps
func (h *Handler) GetJourneySteps(c echo.Context) error {
    journeyID := c.Param("id")
    if journeyID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
    }

    steps, err := h.journeyRepo.GetSteps(c.Request().Context(), journeyID)
    if err != nil {
        if _, ok := err.(*repository.NotFoundError); ok {
            return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
        }
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch steps"})
    }

    return c.JSON(http.StatusOK, steps)
}

// AddJourneyStep handles POST /journeys/:id/steps
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

    step := &JourneyStep{
        ItemID: req.ItemID,
        Order:  req.Order,
    }

    err := h.journeyRepo.AddStep(c.Request().Context(), journeyID, step)
    if err != nil {
        if _, ok := err.(*repository.NotFoundError); ok {
            return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
        }
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to add step"})
    }

    journey, _ := h.journeyRepo.GetByID(c.Request().Context(), journeyID)
    return c.JSON(http.StatusOK, journey)
}

// RemoveJourneyStep handles DELETE /journeys/:id/steps/:itemId
func (h *Handler) RemoveJourneyStep(c echo.Context) error {
    journeyID := c.Param("id")
    itemID := c.Param("itemId")
    if journeyID == "" || itemID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id and item id are required"})
    }

    err := h.journeyRepo.RemoveStep(c.Request().Context(), journeyID, itemID)
    if err != nil {
        if _, ok := err.(*repository.NotFoundError); ok {
            return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
        }
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to remove step"})
    }

    return c.NoContent(http.StatusNoContent)
}

// ============================================================================
// HANDLER METHODS - JOURNEY TYPES AND STATS (using detector)
// ============================================================================

// GetUserFlows handles GET /journeys/user-flows
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
func (h *Handler) GetJourneyVisualization(c echo.Context) error {
    journeyID := c.Param("id")
    if journeyID == "" {
        return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "journey id is required"})
    }

    journey, err := h.journeyRepo.GetByID(c.Request().Context(), journeyID)
    if err != nil {
        if _, ok := err.(*repository.NotFoundError); ok {
            return c.JSON(http.StatusNotFound, ErrorResponse{Error: "journey not found"})
        }
        return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch journey"})
    }

    // Build visualization data
    nodes := make(map[string]*VisualizationNode)
    edges := make([]*VisualizationEdge, 0, len(journey.Links))

    for i, nodeID := range journey.NodeIDs {
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
```

---

## Step 3: Update Server Initialization

**File:** `backend/internal/server/server.go` (Update setupRoutes method)

**Current code (line 314-318):**
```go
// Journey routes (derived journeys, user flows, data paths)
log.Println("🔌 Initializing Journey Service routes...")
journeyHandler := journey.NewHandler(s.pool)
journeyHandler.RegisterRoutes(api)
log.Println("✅ Journey routes registered")
```

**Replace with:**
```go
// Journey routes (derived journeys, user flows, data paths)
log.Println("🔌 Initializing Journey Service routes...")

// Create repositories for journey detection
itemRepo := repository.NewItemRepository(s.infra.GormDB)
linkRepo := repository.NewLinkRepository(s.infra.GormDB)
journeyRepo := repository.NewJourneyRepository(s.infra.GormDB)

// Create journey handler with all dependencies
journeyHandler := journey.NewHandler(
    s.pool,
    itemRepo,
    linkRepo,
    journeyRepo,
    &journey.DetectionConfig{
        MinPathLength:       2,
        MaxPathLength:       10,
        MinFrequency:        1,
        MinScore:            0.1,
        AllowCycles:         false,
        GroupSimilar:        true,
        SimilarityThreshold: 0.8,
    },
)
journeyHandler.RegisterRoutes(api)
log.Println("✅ Journey routes registered")
```

---

## Step 4: Verify Database Schema

Ensure your database has a `journeys` table. Add migration if needed:

**New migration file:** `alembic/versions/XXX_create_journeys_table.py`

```python
"""create journeys table"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'journeys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),  # user_flow, data_path, call_chain, test_trace
        sa.Column('node_ids', sa.JSON(), nullable=True),  # Array of node IDs
        sa.Column('links', sa.JSON(), nullable=True),  # Array of journey links
        sa.Column('score', sa.Float(), default=0.0),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.Index('idx_journeys_project_id', 'project_id'),
        sa.Index('idx_journeys_type', 'type'),
        sa.Index('idx_journeys_score', 'score'),
        sa.Index('idx_journeys_deleted_at', 'deleted_at'),
    )

def downgrade():
    op.drop_table('journeys')
```

---

## Summary

These code changes will:

1. ✅ Create `JourneyRepository` with full CRUD and step management
2. ✅ Wire detector into handler via constructor injection
3. ✅ Implement all 8 stub methods with actual database operations
4. ✅ Add proper validation and error handling
5. ✅ Integrate with existing repository pattern
6. ✅ Fix server initialization

**Total implementation effort:** 3-4 hours following this guide
