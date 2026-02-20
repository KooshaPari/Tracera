# Task 5: Code Reference & Implementation Guide

## Project-Scoped Equivalence Handlers - Full Code

### Handler Registration (server.go, lines 298-302)
```go
log.Println("🔌 Initializing Equivalence Service routes...")
equivalenceService := equivalence.NewService(nil, nil)
equivalenceHandler := equivalence.NewHandler(equivalenceService)
equivalenceHandler.RegisterRoutes(api)
log.Println("✅ Equivalence routes registered")
```

### Route Registration (handler.go, lines 23-62)
```go
func (h *Handler) RegisterRoutes(g *echo.Group) {
	eq := g.Group("/equivalences")

	// Equivalence detection and management
	eq.GET("", h.ListEquivalences)
	eq.POST("/detect", h.DetectEquivalences)
	// ... other routes ...

	// Project-scoped routes (matches frontend API calls)
	// GET /api/v1/projects/:projectId/equivalences
	// POST /api/v1/projects/:projectId/equivalences/detect
	proj := g.Group("/projects/:projectId/equivalences")
	proj.GET("", h.ListProjectEquivalences)
	proj.POST("/detect", h.DetectProjectEquivalences)
}
```

### ListProjectEquivalences Handler (handler.go, lines 672-740)
```go
func (h *Handler) ListProjectEquivalences(c echo.Context) error {
	projectIDStr := c.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "Invalid project ID format",
			Code:      "INVALID_PROJECT_ID",
			Timestamp: time.Now(),
		})
	}

	// Parse pagination
	limit, _ := strconv.Atoi(c.QueryParam("limit"))
	if limit <= 0 || limit > 500 {
		limit = 50
	}
	offset, _ := strconv.Atoi(c.QueryParam("offset"))
	if offset < 0 {
		offset = 0
	}

	// Parse filters
	status := EquivalenceStatus(c.QueryParam("status"))
	minConfStr := c.QueryParam("min_confidence")
	minConf := 0.0
	if minConfStr != "" {
		if conf, err := strconv.ParseFloat(minConfStr, 64); err == nil {
			minConf = conf
		}
	}

	linkType := c.QueryParam("link_type")
	sortBy := c.QueryParam("sort_by")
	if sortBy == "" {
		sortBy = "created_at"
	}
	sortDir := c.QueryParam("sort_direction")
	if sortDir == "" || (sortDir != "asc" && sortDir != "desc") {
		sortDir = "desc"
	}

	// Build filter for repository query
	filter := EquivalenceFilter{
		ProjectID:     projectID,
		Status:        status,
		MinConfidence: minConf,
		LinkType:      linkType,
	}

	// Get equivalences from service
	equivalences, total, err := h.service.ListEquivalencesByProject(c.Request().Context(), filter, limit, offset)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
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

	return c.JSON(http.StatusOK, response)
}
```

### DetectProjectEquivalences Handler (handler.go, lines 754-824)
```go
func (h *Handler) DetectProjectEquivalences(c echo.Context) error {
	projectIDStr := c.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "Invalid project ID format",
			Code:      "INVALID_PROJECT_ID",
			Timestamp: time.Now(),
		})
	}

	var req DetectionRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:     "Invalid request body",
			Code:      "INVALID_REQUEST",
			Timestamp: time.Now(),
		})
	}

	// Override project ID from path parameter (path takes precedence)
	req.ProjectID = projectID

	// Set defaults
	if req.MaxResults <= 0 {
		req.MaxResults = 100
	}
	if req.MinConfidence <= 0 {
		req.MinConfidence = 0.5
	}

	startTime := time.Now()

	// Run detection
	suggestions, err := h.service.DetectEquivalences(c.Request().Context(), &req)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:     err.Error(),
			Code:      "DETECTION_ERROR",
			Timestamp: time.Now(),
		})
	}

	// Build strategy breakdown
	strategyBreakdown := make(map[StrategyType]int)
	avgConf := 0.0
	for _, s := range suggestions {
		for _, strategy := range s.Strategies {
			strategyBreakdown[strategy]++
		}
		avgConf += s.Confidence
	}
	if len(suggestions) > 0 {
		avgConf = avgConf / float64(len(suggestions))
	}

	response := DetectionResponse{
		Suggestions: suggestions,
		Stats: DetectionStats{
			TotalItemsScanned: len(req.CandidatePool),
			EquivalencesFound: len(suggestions),
			AverageConfidence: avgConf,
			StrategyBreakdown: strategyBreakdown,
			DurationMs:        time.Since(startTime).Milliseconds(),
		},
		DetectedAt: time.Now(),
	}

	return c.JSON(http.StatusOK, response)
}
```

---

## Journey Service - Project-Scoped Routes

### Route Registration (journey/handler.go, lines 28-59)
```go
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
```

### ListProjectJourneys Handler (journey/handler.go, lines 593-615)
```go
func (h *Handler) ListProjectJourneys(c echo.Context) error {
	projectID := c.Param("projectId")
	if projectID == "" {
		return c.JSON(http.StatusBadRequest, ErrorResponse{Error: "projectId is required"})
	}

	limit, _ := strconv.Atoi(c.QueryParam("limit"))
	if limit <= 0 || limit > 500 {
		limit = 50
	}
	offset, _ := strconv.Atoi(c.QueryParam("offset"))

	// TODO: Implement repository-backed listing
	response := ListJourneysResponse{
		Data:    []*DerivedJourney{},
		Total:   0,
		Limit:   limit,
		Offset:  offset,
		HasMore: false,
	}

	return c.JSON(http.StatusOK, response)
}
```

---

## Pivot Navigation Handler

### Route Registration (server.go, line 216)
```go
api.POST("/items/:id/pivot", itemHandler.PivotNavigation)
```

### Handler Implementation (item_handler.go, lines 398-454)
```go
func (h *ItemHandler) PivotNavigation(c echo.Context) error {
	idStr := c.Param("id")
	id, err := utils.StringToUUID(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid item ID"})
	}

	var req PivotNavigationRequest
	if err := h.binder.Bind(c, &req); err != nil {
		// Use defaults if binding fails
		req = PivotNavigationRequest{
			MaxDepth:           1,
			IncludeMetadata:    false,
			GroupByPerspective: true,
		}
	}

	// Get the source item
	item, err := h.queries.GetItem(c.Request().Context(), id)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Item not found"})
	}

	// Build source item info
	var sourceItem *PivotItemInfo
	if req.IncludeMetadata {
		priority := (*int)(nil)
		if item.Priority.Valid {
			p := int(item.Priority.Int32)
			priority = &p
		}
		sourceItem = &PivotItemInfo{
			ID:          item.ID.String(),
			ProjectID:   item.ProjectID.String(),
			Title:       item.Title,
			Description: item.Description.String,
			ItemType:    item.Type,
			Status:      item.Status,
			Priority:    priority,
			CreatedAt:   item.CreatedAt.Time,
			UpdatedAt:   item.UpdatedAt.Time,
		}
	}

	// TODO: Implement proper equivalence lookup via equivalence service
	response := PivotNavigationResponse{
		SourceItemID:             idStr,
		SourceItem:               sourceItem,
		EquivalentsByPerspective: make(map[string][]PivotItem),
		AllEquivalents:           []PivotItem{},
		LinkCount:                0,
		PerspectiveCount:         0,
	}

	return c.JSON(http.StatusOK, response)
}
```

---

## Key Implementation Patterns

### 1. Path Parameter Extraction Pattern
```go
// Extract and validate path parameter
projectIDStr := c.Param("projectId")
projectID, err := uuid.Parse(projectIDStr)
if err != nil {
    return c.JSON(http.StatusBadRequest, ErrorResponse{
        Error: "Invalid project ID format",
        Code: "INVALID_PROJECT_ID",
        Timestamp: time.Now(),
    })
}
```

### 2. Pagination Pattern
```go
limit, _ := strconv.Atoi(c.QueryParam("limit"))
if limit <= 0 || limit > 500 {
    limit = 50
}
offset, _ := strconv.Atoi(c.QueryParam("offset"))
if offset < 0 {
    offset = 0
}
```

### 3. Error Response Pattern
```go
return c.JSON(http.StatusBadRequest, ErrorResponse{
    Error: "descriptive error message",
    Code: "ERROR_CODE",
    Timestamp: time.Now(),
})
```

### 4. Service Delegation Pattern
```go
result, err := h.service.SomeMethod(c.Request().Context(), params...)
if err != nil {
    return c.JSON(http.StatusInternalServerError, ErrorResponse{...})
}

return c.JSON(http.StatusOK, result)
```

---

## Testing Endpoints

### Testing ListProjectEquivalences
```bash
curl -X GET \
  'http://localhost:8080/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/equivalences?limit=50&offset=0&status=confirmed&min_confidence=0.7' \
  -H 'Content-Type: application/json'
```

### Testing DetectProjectEquivalences
```bash
curl -X POST \
  'http://localhost:8080/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/equivalences/detect' \
  -H 'Content-Type: application/json' \
  -d '{
    "source_item_id": "550e8400-e29b-41d4-a716-446655440001",
    "strategies": ["naming_pattern", "semantic_similarity"],
    "min_confidence": 0.5,
    "max_results": 100
  }'
```

### Testing ListProjectJourneys
```bash
curl -X GET \
  'http://localhost:8080/api/v1/projects/550e8400-e29b-41d4-a716-446655440000/journeys?limit=50&offset=0' \
  -H 'Content-Type: application/json'
```

### Testing PivotNavigation
```bash
curl -X POST \
  'http://localhost:8080/api/v1/items/550e8400-e29b-41d4-a716-446655440001/pivot' \
  -H 'Content-Type: application/json' \
  -d '{
    "perspectives": ["code", "requirements"],
    "max_depth": 2,
    "include_metadata": true,
    "group_by_perspective": true
  }'
```

---

## References

- Full implementation verification: See `BACKEND_API_ENDPOINT_VERIFICATION.md`
- Task completion summary: See `TASK_5_COMPLETION_SUMMARY.md`
- Type definitions: `backend/internal/equivalence/endpoints.go`
- Service interface: `backend/internal/equivalence/service.go`
- Journey types: `backend/internal/journey/types.go`

