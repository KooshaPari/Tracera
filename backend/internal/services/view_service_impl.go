package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/nats-io/nats.go"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Ensure ViewServiceImpl implements ViewService
var _ ViewService = (*ViewServiceImpl)(nil)

// ViewServiceImpl implements the ViewService interface
type ViewServiceImpl struct {
	viewRepo repository.ViewRepository
	cache    cache.Cache
	natsConn *nats.Conn
}

// NewViewServiceImpl creates a new view service implementation
func NewViewServiceImpl(
	viewRepo repository.ViewRepository,
	cache cache.Cache,
	natsConn *nats.Conn,
) ViewService {
	if viewRepo == nil {
		panic("viewRepo cannot be nil")
	}

	return &ViewServiceImpl{
		viewRepo: viewRepo,
		cache:    cache,
		natsConn: natsConn,
	}
}

// CreateView creates a new view with validation
func (s *ViewServiceImpl) CreateView(ctx context.Context, view *models.View) error {
	if err := s.ValidateView(view); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	if view.ID == "" {
		view.ID = uuid.New().String()
	}
	now := time.Now()
	if view.CreatedAt.IsZero() {
		view.CreatedAt = now
	}
	view.UpdatedAt = now

	if err := s.viewRepo.Create(ctx, view); err != nil {
		return fmt.Errorf("failed to create view: %w", err)
	}

	if s.cache != nil {
		if err := s.cache.Delete(ctx, "views:project:"+view.ProjectID, "views:all"); err != nil {
			slog.Warn("failed to invalidate view cache", "error", err)
		}
	}

	s.publishViewEvent(ctx, "view.created", view)
	return nil
}

// GetView retrieves a view by ID
func (s *ViewServiceImpl) GetView(ctx context.Context, id string) (*models.View, error) {
	if id == "" {
		return nil, errors.New("view ID cannot be empty")
	}

	cacheKey := "view:" + id
	if s.cache != nil {
		if view, err := s.getViewFromCache(ctx, cacheKey); err == nil {
			return view, nil
		}
	}

	view, err := s.viewRepo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get view: %w", err)
	}

	if s.cache != nil {
		if err := s.setViewInCache(ctx, cacheKey, view); err != nil {
			slog.Warn("failed to cache view", "error", err)
		}
	}

	return view, nil
}

// GetViewsByProject retrieves all views for a project
func (s *ViewServiceImpl) GetViewsByProject(ctx context.Context, projectID string) ([]*models.View, error) {
	if projectID == "" {
		return nil, errors.New("project ID cannot be empty")
	}

	cacheKey := "views:project:" + projectID
	if s.cache != nil {
		if views, err := s.getViewsFromCache(ctx, cacheKey); err == nil {
			return views, nil
		}
	}

	views, err := s.viewRepo.GetByProjectID(ctx, projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to get views by project: %w", err)
	}

	if s.cache != nil {
		if err := s.setViewsInCache(ctx, cacheKey, views); err != nil {
			slog.Warn("failed to cache views", "error", err)
		}
	}

	return views, nil
}

// ListViews lists all views
func (s *ViewServiceImpl) ListViews(ctx context.Context) ([]*models.View, error) {
	cacheKey := "views:all"
	if s.cache != nil {
		if views, err := s.getViewsFromCache(ctx, cacheKey); err == nil {
			return views, nil
		}
	}

	views, err := s.viewRepo.List(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to list views: %w", err)
	}

	if s.cache != nil {
		if err := s.setViewsInCache(ctx, cacheKey, views); err != nil {
			slog.Warn("failed to cache views", "error", err)
		}
	}

	return views, nil
}

// UpdateView updates a view
func (s *ViewServiceImpl) UpdateView(ctx context.Context, view *models.View) error {
	if view == nil {
		return errors.New("view cannot be nil")
	}

	if err := s.ValidateView(view); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	existing, err := s.viewRepo.GetByID(ctx, view.ID)
	if err != nil {
		return fmt.Errorf("view not found: %w", err)
	}

	view.UpdatedAt = time.Now()
	view.CreatedAt = existing.CreatedAt

	if err := s.viewRepo.Update(ctx, view); err != nil {
		return fmt.Errorf("failed to update view: %w", err)
	}

	if s.cache != nil {
		if err := s.cache.Delete(ctx,
			"view:"+view.ID,
			"views:project:"+view.ProjectID,
			"views:all",
			"view:stats:"+view.ID,
		); err != nil {
			slog.Warn("failed to invalidate view cache", "error", err)
		}
	}

	s.publishViewEvent(ctx, "view.updated", view)
	return nil
}

// DeleteView deletes a view
func (s *ViewServiceImpl) DeleteView(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("view ID cannot be empty")
	}

	view, err := s.viewRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("view not found: %w", err)
	}

	if err := s.viewRepo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete view: %w", err)
	}

	if s.cache != nil {
		if err := s.cache.Delete(ctx,
			"view:"+id,
			"views:project:"+view.ProjectID,
			"views:all",
			"view:stats:"+id,
		); err != nil {
			slog.Warn("failed to invalidate view cache", "error", err)
		}
	}

	s.publishViewEvent(ctx, "view.deleted", view)
	return nil
}

// GetViewStats returns statistics for a view
func (s *ViewServiceImpl) GetViewStats(ctx context.Context, viewID string) (*models.ViewStats, error) {
	if viewID == "" {
		return nil, errors.New("view ID cannot be empty")
	}

	cacheKey := "view:stats:" + viewID
	if s.cache != nil {
		if stats, err := s.getStatsFromCache(ctx, cacheKey); err == nil {
			return stats, nil
		}
	}

	view, err := s.viewRepo.GetByID(ctx, viewID)
	if err != nil {
		return nil, fmt.Errorf("view not found: %w", err)
	}

	itemCount, err := s.viewRepo.CountItemsByView(ctx, viewID)
	if err != nil {
		return nil, fmt.Errorf("failed to count items: %w", err)
	}

	stats := &models.ViewStats{
		ViewID:    viewID,
		ItemCount: itemCount,
		UpdatedAt: view.UpdatedAt,
	}

	if s.cache != nil {
		if err := s.setStatsInCache(ctx, cacheKey, stats); err != nil {
			slog.Warn("failed to cache view stats", "error", err)
		}
	}

	return stats, nil
}

// ValidateView validates view business rules
func (s *ViewServiceImpl) ValidateView(view *models.View) error {
	if view == nil {
		return errors.New("view cannot be nil")
	}

	if view.Name == "" {
		return errors.New("view name is required")
	}

	if view.ProjectID == "" {
		return errors.New("project ID is required")
	}

	if view.Type == "" {
		return errors.New("view type is required")
	}

	if len(view.Name) > maxViewNameLength {
		return fmt.Errorf("view name cannot exceed %d characters", maxViewNameLength)
	}

	validTypes := map[string]bool{
		"kanban": true, "timeline": true, "matrix": true, "graph": true,
		"table": true, "board": true, "list": true,
	}

	if !validTypes[view.Type] {
		return fmt.Errorf("invalid view type: %s", view.Type)
	}

	if view.Config != "" {
		var config map[string]interface{}
		if err := json.Unmarshal([]byte(view.Config), &config); err != nil {
			return fmt.Errorf("invalid config JSON: %w", err)
		}
	}

	return nil
}

// Cache helper methods

func (s *ViewServiceImpl) getViewFromCache(ctx context.Context, key string) (*models.View, error) {
	var view models.View
	if err := s.cache.Get(ctx, key, &view); err != nil {
		return nil, err
	}
	return &view, nil
}

func (s *ViewServiceImpl) setViewInCache(ctx context.Context, key string, view *models.View) error {
	return s.cache.Set(ctx, key, view)
}

func (s *ViewServiceImpl) getViewsFromCache(ctx context.Context, key string) ([]*models.View, error) {
	var views []*models.View
	if err := s.cache.Get(ctx, key, &views); err != nil {
		return nil, err
	}
	return views, nil
}

func (s *ViewServiceImpl) setViewsInCache(ctx context.Context, key string, views []*models.View) error {
	return s.cache.Set(ctx, key, views)
}

func (s *ViewServiceImpl) getStatsFromCache(ctx context.Context, key string) (*models.ViewStats, error) {
	var stats models.ViewStats
	if err := s.cache.Get(ctx, key, &stats); err != nil {
		return nil, err
	}
	return &stats, nil
}

func (s *ViewServiceImpl) setStatsInCache(ctx context.Context, key string, stats *models.ViewStats) error {
	return s.cache.Set(ctx, key, stats)
}

// publishViewEvent publishes a view event to NATS
func (s *ViewServiceImpl) publishViewEvent(_ context.Context, eventType string, view *models.View) {
	if s.natsConn == nil {
		return
	}

	event := map[string]interface{}{
		"type":       eventType,
		"view_id":    view.ID,
		"project_id": view.ProjectID,
		"view_type":  view.Type,
		"timestamp":  time.Now().Format(time.RFC3339),
	}

	data, err := json.Marshal(event)
	if err != nil {
		slog.Warn("failed to marshal view event", "error", err)
		return
	}
	subject := strings.ReplaceAll(eventType, ".", "_")
	if err := s.natsConn.Publish(subject, data); err != nil {
		slog.Warn("failed to publish view event", "subject", subject, "error", err)
	}
}
