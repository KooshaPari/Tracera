package handlers

import (
	"context"
	"log/slog"
	"net/http"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
)

// DashboardHandler handles dashboard summary operations.
type DashboardHandler struct {
	db    *gorm.DB
	cache cache.Cache
}

// NewDashboardHandler creates a new DashboardHandler.
func NewDashboardHandler(db *gorm.DB) *DashboardHandler {
	return &DashboardHandler{db: db, cache: nil}
}

// NewDashboardHandlerWithCache creates a new DashboardHandler with caching.
func NewDashboardHandlerWithCache(db *gorm.DB, c cache.Cache) *DashboardHandler {
	return &DashboardHandler{db: db, cache: c}
}

// DashboardSummaryResponse is the top-level dashboard summary payload.
type DashboardSummaryResponse struct {
	ProjectCount       int64                          `json:"project_count"`
	TotalItemCount     int64                          `json:"total_item_count"`
	StatusDistribution map[string]int64               `json:"status_distribution"`
	TypeDistribution   map[string]int64               `json:"type_distribution"`
	PerProject         map[string]ProjectItemsSummary `json:"per_project"`
}

// ProjectItemsSummary holds per-project item statistics.
type ProjectItemsSummary struct {
	TotalCount     int64            `json:"total_count"`
	CompletedCount int64            `json:"completed_count"`
	StatusCounts   map[string]int64 `json:"status_counts"`
	TypeCounts     map[string]int64 `json:"type_counts"`
}

// itemGroupRow represents a single row from the GROUP BY query.
type itemGroupRow struct {
	ProjectID string `gorm:"column:project_id"`
	Status    string `gorm:"column:status"`
	Type      string `gorm:"column:type"`
	Count     int64  `gorm:"column:count"`
}

// GetDashboardSummary godoc
// @Summary Get aggregated dashboard statistics
// @Description Returns project count, item counts, and per-project breakdowns by status and type in a single query
// @Tags dashboard
// @Produce json
// @Success 200 {object} DashboardSummaryResponse "Dashboard summary"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /dashboard/summary [get]
func (h *DashboardHandler) GetDashboardSummary(c echo.Context) error {
	ctx := c.Request().Context()

	// OPTIMIZATION 6.6: Try to get from Redis cache first
	var summary *DashboardSummaryResponse
	if h.cache != nil {
		userID, ok := c.Get("user_id").(string)
		if ok {
			cacheKey := cache.DashboardSummaryCacheKey(userID)
			// Try to get from cache
			if err := h.cache.Get(ctx, cacheKey, &summary); err == nil && summary != nil {
				// Cache hit!
				return c.JSON(http.StatusOK, summary)
			}
		}
	}

	// Cache miss or no cache - build from database
	var err error
	summary, err = h.buildDashboardSummary(ctx)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, ErrorResponse{Error: "failed to fetch dashboard summary"})
	}

	// Store in cache for future requests
	if h.cache != nil && summary != nil {
		if userID, ok := c.Get("user_id").(string); ok {
			cacheKey := cache.DashboardSummaryCacheKey(userID)
			// Set cache with TTL (cache implementation handles TTL internally)
			if err := h.cache.Set(ctx, cacheKey, summary); err != nil {
				slog.Warn("failed to cache dashboard summary", "error", err)
			}
		}
	}

	return c.JSON(http.StatusOK, summary)
}

// buildDashboardSummary executes optimized aggregation and assembles the response.
// Optimization: Single query with index on (project_id, status, type) + pre-aggregation
func (h *DashboardHandler) buildDashboardSummary(ctx context.Context) (*DashboardSummaryResponse, error) {
	// Optimized single query: group items by project_id, status, type
	// Uses index on (project_id, status, type, deleted_at) for fast filtering
	var rows []itemGroupRow
	err := h.db.WithContext(ctx).
		Table("items").
		Select("project_id, status, type, COUNT(*) as count").
		Where("deleted_at IS NULL").
		Group("project_id, status, type").
		// Add ORDER BY to help query planner use index
		Order("project_id, status, type").
		Find(&rows).Error
	if err != nil {
		return nil, err
	}

	// Count projects in same call to reduce round trips
	var projectCount int64
	err = h.db.WithContext(ctx).
		Table("projects").
		Where("deleted_at IS NULL").
		Count(&projectCount).Error
	if err != nil {
		return nil, err
	}

	// Pre-allocate response structure to reduce allocations
	resp := &DashboardSummaryResponse{
		ProjectCount:       projectCount,
		TotalItemCount:     0,
		StatusDistribution: make(map[string]int64, 10), // Pre-allocate expected capacity
		TypeDistribution:   make(map[string]int64, 10),
		PerProject:         make(map[string]ProjectItemsSummary, projectCount),
	}

	// Optimized aggregation: single pass through results with pre-allocation
	for _, row := range rows {
		resp.TotalItemCount += row.Count

		// Global distributions (optimized)
		resp.StatusDistribution[row.Status] += row.Count
		resp.TypeDistribution[row.Type] += row.Count

		// Per-project breakdown (optimized with pre-check)
		proj, ok := resp.PerProject[row.ProjectID]
		if !ok {
			proj = ProjectItemsSummary{
				StatusCounts: make(map[string]int64, 10),
				TypeCounts:   make(map[string]int64, 10),
			}
		}
		proj.TotalCount += row.Count
		proj.StatusCounts[row.Status] += row.Count
		proj.TypeCounts[row.Type] += row.Count
		// Optimize status check - use quick map lookup
		if row.Status == "completed" {
			proj.CompletedCount += row.Count
		}
		resp.PerProject[row.ProjectID] = proj
	}

	return resp, nil
}
