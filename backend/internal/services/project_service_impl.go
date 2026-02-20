package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/nats-io/nats.go"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Ensure ProjectServiceImpl implements ProjectService interface
var _ ProjectService = (*ProjectServiceImpl)(nil)

// ProjectServiceImpl implements the ProjectService interface with caching, event publishing,
// and transaction support
type ProjectServiceImpl struct {
	projectRepo repository.ProjectRepository
	itemRepo    repository.ItemRepository
	cache       cache.Cache
	natsConn    *nats.Conn
	cacheTTL    time.Duration
	db          *gorm.DB // Database connection for transaction support
}

// NewProjectServiceImpl creates a new project service implementation
func NewProjectServiceImpl(
	projectRepo repository.ProjectRepository,
	itemRepo repository.ItemRepository,
	cache cache.Cache,
	natsConn *nats.Conn,
	db *gorm.DB,
) ProjectService {
	if projectRepo == nil {
		panic("projectRepo cannot be nil")
	}
	if itemRepo == nil {
		panic("itemRepo cannot be nil")
	}
	if db == nil {
		panic("db cannot be nil")
	}

	return &ProjectServiceImpl{
		projectRepo: projectRepo,
		itemRepo:    itemRepo,
		cache:       cache,
		natsConn:    natsConn,
		db:          db,
		cacheTTL:    defaultCacheTTL,
	}
}

// ============================================================================
// CORE CRUD OPERATIONS
// ============================================================================

// CreateProject creates a new project with validation, caching, and event publishing
// Transaction-aware: if ctx contains a transaction, it will be used
func (s *ProjectServiceImpl) CreateProject(ctx context.Context, project *models.Project) error {
	// Validate input
	if err := s.validateProject(project); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Log transaction status for debugging
	if s.isInTransaction(ctx) {
		slog.Info("[TRANSACTION] Creating project within transactio", "project", project.ID)
	}

	// Persist to database (will use transaction if available in context)
	if err := s.projectRepo.Create(ctx, project); err != nil {
		return fmt.Errorf("failed to create project: %w", err)
	}

	// Invalidate list cache
	s.invalidateListCache(ctx)

	// Publish event (only after successful commit if in transaction)
	// Note: Event publishing happens after transaction commit to ensure consistency
	if !s.isInTransaction(ctx) {
		s.publishEvent(ctx, "project.created", project)
	}

	return nil
}

// GetProject retrieves a project by ID with caching
func (s *ProjectServiceImpl) GetProject(ctx context.Context, id string) (*models.Project, error) {
	if id == "" {
		return nil, errors.New("project ID is required")
	}

	// Try cache first (cache-aside pattern)
	cacheKey := s.getProjectCacheKey(id)
	if s.cache != nil {
		if cached, err := s.getFromCache(ctx, cacheKey); cached != nil && err == nil {
			slog.Info("[CACHE HIT] Retrieved project from cache", "project", id)
			return cached, nil
		}
	}

	// Cache miss - fetch from database
	project, err := s.projectRepo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get project: %w", err)
	}

	// Populate cache (non-blocking)
	if s.cache != nil {
		asyncFireAndForget(func(ctx context.Context) {
			if err := s.setInCache(ctx, cacheKey, project); err != nil {
				slog.Error("Warning: Failed to cache project", "error", id, "error", err)
			}
		})
	}

	return project, nil
}

// ListProjects lists all projects with optional caching
func (s *ProjectServiceImpl) ListProjects(ctx context.Context) ([]*models.Project, error) {
	// Try cache first for project list
	if s.cache != nil {
		cacheKey := "projects:list"
		if cached, err := s.getProjectsFromCache(ctx, cacheKey); cached != nil && err == nil {
			slog.Info("[CACHE HIT] Retrieved project list from cache")
			return cached, nil
		}
	}

	// Fetch from database
	projects, err := s.projectRepo.List(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to list projects: %w", err)
	}

	// Cache the result (non-blocking)
	if s.cache != nil {
		asyncFireAndForget(func(ctx context.Context) {
			if err := s.setProjectsInCache(ctx, "projects:list", projects); err != nil {
				slog.Error("Warning: Failed to cache project list", "error", err)
			}
		})
	}

	return projects, nil
}

// UpdateProject updates an existing project and invalidates caches
// Transaction-aware: if ctx contains a transaction, it will be used
func (s *ProjectServiceImpl) UpdateProject(ctx context.Context, project *models.Project) error {
	if err := s.validateProject(project); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Log transaction status for debugging
	if s.isInTransaction(ctx) {
		slog.Info("[TRANSACTION] Updating project within transactio", "project", project.ID)
	}

	if err := s.projectRepo.Update(ctx, project); err != nil {
		return fmt.Errorf("failed to update project: %w", err)
	}

	// Invalidate caches
	s.invalidateProjectCaches(ctx, project.ID)

	// Publish event (only after successful commit if in transaction)
	if !s.isInTransaction(ctx) {
		s.publishEvent(ctx, "project.updated", project)
	}

	return nil
}

// DeleteProject deletes a project and invalidates caches
// Transaction-aware: if ctx contains a transaction, it will be used
func (s *ProjectServiceImpl) DeleteProject(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("project ID is required")
	}

	// Log transaction status for debugging
	if s.isInTransaction(ctx) {
		slog.Info("[TRANSACTION] Deleting project within transactio", "project", id)
	}

	// Check if project exists before deleting
	_, err := s.projectRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to delete project: %w", err)
	}

	// Soft delete from database (will use transaction if available in context)
	if err := s.projectRepo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete project: %w", err)
	}

	// Invalidate all related caches
	s.invalidateProjectCaches(ctx, id)

	// Publish event (only after successful commit if in transaction)
	if !s.isInTransaction(ctx) {
		s.publishEvent(ctx, "project.deleted", map[string]string{"id": id})
	}

	return nil
}

// CreateProjectWithItems creates a project and its initial items atomically
// This demonstrates proper transaction usage for multi-step operations
func (s *ProjectServiceImpl) CreateProjectWithItems(ctx context.Context, project *models.Project, items []*models.Item) error {
	// Use WithTransaction to ensure atomic operation
	return s.WithTransaction(ctx, func(txCtx context.Context) error {
		// Create the project first
		if err := s.CreateProject(txCtx, project); err != nil {
			return fmt.Errorf("failed to create project: %w", err)
		}

		// Create each item
		for i, item := range items {
			// Ensure item belongs to the project
			item.ProjectID = project.ID

			if err := s.itemRepo.Create(txCtx, item); err != nil {
				return fmt.Errorf("failed to create item %d: %w", i, err)
			}
		}

		slog.Info("[TRANSACTION] Successfully created project with items", "project", project.ID, "value", len(items))

		// Events will be published after commit
		s.publishEvent(txCtx, "project.created_with_items", map[string]interface{}{
			"project_id": project.ID,
			"item_count": len(items),
		})

		return nil
	})
}

// UpdateProjectAndItems updates a project and multiple items atomically
// This demonstrates how to use transactions for consistent multi-entity updates
func (s *ProjectServiceImpl) UpdateProjectAndItems(ctx context.Context, project *models.Project, items []*models.Item) error {
	return s.WithTransaction(ctx, func(txCtx context.Context) error {
		// Update the project
		if err := s.UpdateProject(txCtx, project); err != nil {
			return fmt.Errorf("failed to update project: %w", err)
		}

		// Update each item
		for i, item := range items {
			// Verify item belongs to the project
			if item.ProjectID != project.ID {
				return fmt.Errorf("item %d does not belong to project %s", i, project.ID)
			}

			if err := s.itemRepo.Update(txCtx, item); err != nil {
				return fmt.Errorf("failed to update item %d: %w", i, err)
			}
		}

		slog.Info("[TRANSACTION] Successfully updated project with items", "project", project.ID, "value", len(items))

		// Events will be published after commit
		s.publishEvent(txCtx, "project.updated_with_items", map[string]interface{}{
			"project_id": project.ID,
			"item_count": len(items),
		})

		return nil
	})
}

// DeleteProjectWithItems deletes a project and all its items atomically
// This demonstrates cascading deletes within a transaction
func (s *ProjectServiceImpl) DeleteProjectWithItems(ctx context.Context, projectID string) error {
	return s.WithTransaction(ctx, func(txCtx context.Context) error {
		// Get all items for the project
		items, err := s.itemRepo.GetByProjectID(txCtx, projectID)
		if err != nil {
			return fmt.Errorf("failed to get project items: %w", err)
		}

		// Delete all items
		for _, item := range items {
			if err := s.itemRepo.Delete(txCtx, item.ID); err != nil {
				return fmt.Errorf("failed to delete item %s: %w", item.ID, err)
			}
		}

		// Delete the project
		if err := s.DeleteProject(txCtx, projectID); err != nil {
			return fmt.Errorf("failed to delete project: %w", err)
		}

		slog.Info("[TRANSACTION] Successfully deleted project with items", "project", projectID, "value", len(items))

		// Events will be published after commit
		s.publishEvent(txCtx, "project.deleted_with_items", map[string]interface{}{
			"project_id": projectID,
			"item_count": len(items),
		})

		return nil
	})
}

// ============================================================================
// STATISTICS AND ANALYTICS
// ============================================================================

// GetProjectStats calculates and returns project statistics with caching
func (s *ProjectServiceImpl) GetProjectStats(ctx context.Context, projectID string) (*ProjectStats, error) {
	if projectID == "" {
		return nil, errors.New("project ID is required")
	}

	// Try cache first
	if s.cache != nil {
		cacheKey := s.getStatsCacheKey(projectID)
		if cached, err := s.getStatsFromCache(ctx, cacheKey); cached != nil && err == nil {
			slog.Info("[CACHE HIT] Retrieved project stats for from cache", "project", projectID)
			return cached, nil
		}
	}

	// Verify project exists
	_, err := s.projectRepo.GetByID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("project not found: %w", err)
	}

	// Calculate statistics
	stats, err := s.calculateProjectStats(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to calculate project stats: %w", err)
	}

	// Cache the result (non-blocking)
	if s.cache != nil {
		cacheKey := s.getStatsCacheKey(projectID)
		asyncFireAndForget(func(ctx context.Context) {
			if err := s.setStatsInCache(ctx, cacheKey, stats); err != nil {
				slog.Error("Warning: Failed to cache project stats", "error", err)
			}
		})
	}

	return stats, nil
}

// calculateProjectStats computes project statistics from items
func (s *ProjectServiceImpl) calculateProjectStats(ctx context.Context, projectID string) (*ProjectStats, error) {
	// Get all items for this project
	projectIDPtr := &projectID
	items, err := s.itemRepo.List(ctx, repository.ItemFilter{ProjectID: projectIDPtr})
	if err != nil {
		return nil, fmt.Errorf("failed to list items: %w", err)
	}

	stats := &ProjectStats{
		ProjectID:     projectID,
		TotalItems:    int64(len(items)),
		ItemsByType:   make(map[string]int64),
		ItemsByStatus: make(map[string]int64),
		UpdatedAt:     time.Now(),
	}

	// Aggregate counts
	for _, item := range items {
		if item.Type != "" {
			stats.ItemsByType[item.Type]++
		}
		if item.Status != "" {
			stats.ItemsByStatus[item.Status]++
		}
	}

	return stats, nil
}

// ============================================================================
// VALIDATION
// ============================================================================

// validateProject validates project business rules
func (s *ProjectServiceImpl) validateProject(project *models.Project) error {
	if project == nil {
		return errors.New("project cannot be nil")
	}

	if project.ID == "" {
		return errors.New("project ID is required")
	}

	if project.Name == "" {
		return errors.New("project name is required")
	}

	if len(project.Name) > maxProjectNameLength {
		return fmt.Errorf("project name must be less than %d characters", maxProjectNameLength)
	}

	if len(project.Description) > maxProjectDescriptionLength {
		return fmt.Errorf("project description must be less than %d characters", maxProjectDescriptionLength)
	}

	return nil
}

// ============================================================================
// TRANSACTION SUPPORT
// ============================================================================

// WithTransaction executes a function within a transaction
// This is a convenience method for operations that need transactional consistency
func (s *ProjectServiceImpl) WithTransaction(ctx context.Context, fn func(context.Context) error) error {
	// Check if already in a transaction using services package
	if IsInTransaction(ctx) {
		// Already in a transaction, just execute the function
		return fn(ctx)
	}

	// Start a new transaction using GORM's Transaction method
	return s.db.Transaction(func(tx *gorm.DB) error {
		// Add transaction to context using services package
		txCtx := WithTransaction(ctx, tx)
		return fn(txCtx)
	})
}

// isInTransaction checks if the current context is in a transaction
func (s *ProjectServiceImpl) isInTransaction(ctx context.Context) bool {
	// Use the services package IsInTransaction function
	return IsInTransaction(ctx)
}

// ============================================================================
// CACHE OPERATIONS
// ============================================================================

// getProjectCacheKey returns the cache key for a project
func (s *ProjectServiceImpl) getProjectCacheKey(id string) string {
	return "project:" + id
}

// getStatsCacheKey returns the cache key for project statistics
func (s *ProjectServiceImpl) getStatsCacheKey(id string) string {
	return "project:" + id + ":stats"
}

// getFromCache retrieves a project from cache
func (s *ProjectServiceImpl) getFromCache(ctx context.Context, key string) (*models.Project, error) {
	var project models.Project
	if err := s.cache.Get(ctx, key, &project); err != nil {
		return nil, err
	}
	return &project, nil
}

// setInCache stores a project in cache
func (s *ProjectServiceImpl) setInCache(ctx context.Context, key string, project *models.Project) error {
	return s.cache.Set(ctx, key, project)
}

// getProjectsFromCache retrieves a list of projects from cache
func (s *ProjectServiceImpl) getProjectsFromCache(ctx context.Context, key string) ([]*models.Project, error) {
	var projects []*models.Project
	if err := s.cache.Get(ctx, key, &projects); err != nil {
		return nil, err
	}
	return projects, nil
}

// setProjectsInCache stores a list of projects in cache
func (s *ProjectServiceImpl) setProjectsInCache(ctx context.Context, key string, projects []*models.Project) error {
	return s.cache.Set(ctx, key, projects)
}

// getStatsFromCache retrieves project statistics from cache
func (s *ProjectServiceImpl) getStatsFromCache(ctx context.Context, key string) (*ProjectStats, error) {
	var stats ProjectStats
	if err := s.cache.Get(ctx, key, &stats); err != nil {
		return nil, err
	}
	return &stats, nil
}

// setStatsInCache stores project statistics in cache
func (s *ProjectServiceImpl) setStatsInCache(ctx context.Context, key string, stats *ProjectStats) error {
	return s.cache.Set(ctx, key, stats)
}

// invalidateProjectCaches invalidates all caches related to a project
func (s *ProjectServiceImpl) invalidateProjectCaches(ctx context.Context, projectID string) {
	if s.cache == nil {
		return
	}

	// Delete project cache
	projectKey := s.getProjectCacheKey(projectID)
	if err := s.cache.Delete(ctx, projectKey); err != nil {
		slog.Error("Warning: Failed to invalidate project cache", "error", projectKey, "error", err)
	}

	// Delete stats cache
	statsKey := s.getStatsCacheKey(projectID)
	if err := s.cache.Delete(ctx, statsKey); err != nil {
		slog.Error("Warning: Failed to invalidate stats cache", "error", statsKey, "error", err)
	}

	// Delete list cache
	s.invalidateListCache(ctx)
}

// invalidateListCache invalidates the project list cache
func (s *ProjectServiceImpl) invalidateListCache(ctx context.Context) {
	if s.cache == nil {
		return
	}

	listKey := "projects:list"
	if err := s.cache.Delete(ctx, listKey); err != nil {
		slog.Error("Warning: Failed to invalidate list cache", "error", err)
	}
}

// ============================================================================
// EVENT PUBLISHING
// ============================================================================

// publishEvent publishes a project event to NATS
func (s *ProjectServiceImpl) publishEvent(_ context.Context, eventType string, data interface{}) {
	if s.natsConn == nil {
		return
	}

	payload, err := json.Marshal(map[string]interface{}{
		"type":      eventType,
		"data":      data,
		"timestamp": time.Now(),
	})
	if err != nil {
		slog.Error("Warning: Failed to marshal event", "error", err)
		return
	}

	if err := s.natsConn.Publish(eventType, payload); err != nil {
		slog.Error("Warning: Failed to publish event", "error", eventType, "error", err)
	} else {
		slog.Info("[EVENT PUBLISHED]", "detail", eventType)
	}
}
