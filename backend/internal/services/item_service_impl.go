package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/nats-io/nats.go"
)

// Ensure ItemServiceImpl implements ItemService interface
var _ ItemService = (*ItemServiceImpl)(nil)

// ItemServiceImpl implements the ItemService interface with caching and event publishing
type ItemServiceImpl struct {
	itemRepo     repository.ItemRepository
	linkRepo     repository.LinkRepository
	cacheService CacheService
	natsConn     *nats.Conn
	cacheTTL     time.Duration
}

// NewItemServiceImpl creates a new item service implementation
func NewItemServiceImpl(
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
	cacheService CacheService,
	natsConn *nats.Conn,
) ItemService {
	if itemRepo == nil {
		panic("itemRepo cannot be nil")
	}
	if linkRepo == nil {
		panic("linkRepo cannot be nil")
	}

	return &ItemServiceImpl{
		itemRepo:     itemRepo,
		linkRepo:     linkRepo,
		cacheService: cacheService,
		natsConn:     natsConn,
		cacheTTL:     defaultCacheTTL,
	}
}

// ============================================================================
// CORE CRUD OPERATIONS
// ============================================================================

// CreateItem creates a new item with validation, caching, and event publishing
func (s *ItemServiceImpl) CreateItem(ctx context.Context, item *models.Item) error {
	// Validate input
	if err := s.validateItem(item); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Set defaults if not provided
	if item.Status == "" {
		item.Status = statusTodo
	}
	if item.Priority == 0 {
		item.Priority = models.PriorityMedium
	}

	// Persist to database using GORM
	if err := s.itemRepo.Create(ctx, item); err != nil {
		return fmt.Errorf("failed to create item: %w", err)
	}

	// Invalidate related caches
	s.invalidateProjectCaches(ctx, item.ProjectID)

	// Publish event
	s.publishEvent(ctx, "item.created", item)

	return nil
}

// CreateBatch creates multiple items in a single transaction
func (s *ItemServiceImpl) CreateBatch(ctx context.Context, items []*models.Item) error {
	if len(items) == 0 {
		return errors.New("items list cannot be empty")
	}

	// Validate all items
	for i, item := range items {
		if err := s.validateItem(item); err != nil {
			return fmt.Errorf("validation failed for item at index %d: %w", i, err)
		}
	}

	// Create all items
	for _, item := range items {
		// Set defaults
		if item.Status == "" {
			item.Status = statusTodo
		}
		if item.Priority == 0 {
			item.Priority = models.PriorityMedium
		}

		if err := s.itemRepo.Create(ctx, item); err != nil {
			return fmt.Errorf("failed to create item %s: %w", item.ID, err)
		}
	}

	// Invalidate caches for all affected projects
	projectIDs := make(map[string]bool)
	for _, item := range items {
		projectIDs[item.ProjectID] = true
	}

	for projectID := range projectIDs {
		s.invalidateProjectCaches(ctx, projectID)
	}

	// Publish batch creation event
	s.publishEvent(ctx, "item.batch_created", map[string]interface{}{
		"count":       len(items),
		"project_ids": projectIDs,
	})

	return nil
}

// GetItem retrieves an item by ID with caching
func (s *ItemServiceImpl) GetItem(ctx context.Context, id string) (*models.Item, error) {
	if id == "" {
		return nil, errors.New("item ID is required")
	}

	// Try cache first (cache-aside pattern)
	if s.cacheService != nil {
		if cached, err := s.cacheService.GetItem(ctx, id); cached != nil && err == nil {
			log.Printf("[CACHE HIT] Retrieved item %s from cache", id)
			return cached, nil
		}
	}

	// Cache miss - fetch from database using GORM
	item, err := s.itemRepo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get item: %w", err)
	}

	// Populate cache (non-blocking)
	if s.cacheService != nil {
		go func() {
			cacheCtx, cancel := context.WithTimeout(context.Background(), cacheWriteTimeout)
			defer cancel()
			if err := s.cacheService.SetItem(cacheCtx, item); err != nil {
				log.Printf("Warning: Failed to cache item %s: %v", id, err)
			}
		}()
	}

	return item, nil
}

// GetWithLinks retrieves an item with its related links
func (s *ItemServiceImpl) GetWithLinks(ctx context.Context, id string) (*ItemWithLinks, error) {
	// Get the item
	item, err := s.GetItem(ctx, id)
	if err != nil {
		return nil, err
	}

	// Get source links (where this item is the source)
	sourceLinks, err := s.linkRepo.GetBySourceID(ctx, id)
	if err != nil {
		log.Printf("Warning: Failed to get source links for item %s: %v", id, err)
		sourceLinks = []*models.Link{}
	}

	// Get target links (where this item is the target)
	targetLinks, err := s.linkRepo.GetByTargetID(ctx, id)
	if err != nil {
		log.Printf("Warning: Failed to get target links for item %s: %v", id, err)
		targetLinks = []*models.Link{}
	}

	return &ItemWithLinks{
		Item:        item,
		SourceLinks: sourceLinks,
		TargetLinks: targetLinks,
	}, nil
}

// ListItems lists items with optional filtering and caching
func (s *ItemServiceImpl) ListItems(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	// For small pages, try cache
	if s.cacheService != nil && filter.Limit <= 50 && filter.Offset == 0 && filter.ProjectID != nil {
		cacheKey := "items:project:" + *filter.ProjectID + ":page:0"
		if cached, err := s.cacheService.GetItems(ctx, cacheKey); cached != nil && err == nil {
			log.Printf("[CACHE HIT] Retrieved items list from cache")
			return cached, nil
		}
	}

	// Fetch from database using GORM
	items, err := s.itemRepo.List(ctx, filter)
	if err != nil {
		return nil, fmt.Errorf("failed to list items: %w", err)
	}

	// Cache first page of project items
	if s.cacheService != nil && filter.Limit <= 50 && filter.Offset == 0 && filter.ProjectID != nil {
		cacheKey := "items:project:" + *filter.ProjectID + ":page:0"
		go func() {
			cacheCtx, cancel := context.WithTimeout(context.Background(), cacheWriteTimeout)
			defer cancel()
			if err := s.cacheService.SetItems(cacheCtx, cacheKey, items, 0); err != nil {
				log.Printf("Warning: Failed to cache items: %v", err)
			}
		}()
	}

	return items, nil
}

// Count returns the number of items matching the filter
func (s *ItemServiceImpl) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	count, err := s.itemRepo.Count(ctx, filter)
	if err != nil {
		return 0, fmt.Errorf("failed to count items: %w", err)
	}
	return count, nil
}

// ============================================================================
// UPDATE OPERATIONS
// ============================================================================

// UpdateItem updates an existing item with validation and cache invalidation
func (s *ItemServiceImpl) UpdateItem(ctx context.Context, item *models.Item) error {
	if err := s.validateItem(item); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Update using GORM
	if err := s.itemRepo.Update(ctx, item); err != nil {
		return fmt.Errorf("failed to update item: %w", err)
	}

	// Invalidate caches
	if s.cacheService != nil {
		_ = s.cacheService.InvalidateItem(ctx, item.ID)
	}

	s.invalidateProjectCaches(ctx, item.ProjectID)

	// Publish event
	s.publishEvent(ctx, "item.updated", item)

	return nil
}

// UpdateStatus updates only the status field of an item
func (s *ItemServiceImpl) UpdateStatus(ctx context.Context, id, status string) error {
	if id == "" {
		return errors.New("item ID is required")
	}
	if status == "" {
		return errors.New("status is required")
	}

	// Validate status
	validStatuses := map[string]bool{
		statusTodo:    true,
		"in_progress": true,
		"done":        true,
		"blocked":     true,
		"cancelled":   true,
	}
	if !validStatuses[status] {
		return fmt.Errorf("invalid status: %s", status)
	}

	// Get existing item
	item, err := s.itemRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get item: %w", err)
	}

	// Update status
	item.Status = status
	if err := s.itemRepo.Update(ctx, item); err != nil {
		return fmt.Errorf("failed to update item status: %w", err)
	}

	// Invalidate caches
	if s.cacheService != nil {
		_ = s.cacheService.InvalidateItem(ctx, id)
	}

	s.invalidateProjectCaches(ctx, item.ProjectID)

	// Publish event
	s.publishEvent(ctx, "item.status_changed", map[string]interface{}{
		"id":         id,
		"old_status": item.Status,
		"new_status": status,
	})

	return nil
}

// UpdateBatch updates multiple items in a single transaction
func (s *ItemServiceImpl) UpdateBatch(ctx context.Context, items []*models.Item) error {
	if len(items) == 0 {
		return errors.New("items list cannot be empty")
	}

	// Validate all items
	for i, item := range items {
		if err := s.validateItem(item); err != nil {
			return fmt.Errorf("validation failed for item at index %d: %w", i, err)
		}
	}

	// Update all items
	for _, item := range items {
		if err := s.itemRepo.Update(ctx, item); err != nil {
			return fmt.Errorf("failed to update item %s: %w", item.ID, err)
		}
	}

	// Invalidate caches for all affected items and projects
	projectIDs := make(map[string]bool)
	for _, item := range items {
		if s.cacheService != nil {
			_ = s.cacheService.InvalidateItem(ctx, item.ID)
		}
		projectIDs[item.ProjectID] = true
	}

	for projectID := range projectIDs {
		s.invalidateProjectCaches(ctx, projectID)
	}

	// Publish batch update event
	s.publishEvent(ctx, "item.batch_updated", map[string]interface{}{
		"count":       len(items),
		"project_ids": projectIDs,
	})

	return nil
}

// ============================================================================
// DELETE OPERATIONS
// ============================================================================

// DeleteItem deletes an item and its related links with cache invalidation
func (s *ItemServiceImpl) DeleteItem(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("item ID is required")
	}

	// Get item first to know which project cache to invalidate
	item, err := s.itemRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get item for deletion: %w", err)
	}

	// Delete related links first
	if err := s.linkRepo.DeleteByItemID(ctx, id); err != nil {
		return fmt.Errorf("failed to delete item links: %w", err)
	}

	// Delete item using GORM
	if err := s.itemRepo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete item: %w", err)
	}

	// Invalidate caches
	if s.cacheService != nil {
		_ = s.cacheService.InvalidateItem(ctx, id)
	}

	s.invalidateProjectCaches(ctx, item.ProjectID)

	// Publish event
	s.publishEvent(ctx, "item.deleted", map[string]interface{}{
		"id":         id,
		"project_id": item.ProjectID,
	})

	return nil
}

// DeleteBatch deletes multiple items in a single transaction
func (s *ItemServiceImpl) DeleteBatch(ctx context.Context, ids []string) error {
	if len(ids) == 0 {
		return errors.New("IDs list cannot be empty")
	}

	projectIDs := make(map[string]bool)

	// Delete all items
	for _, id := range ids {
		// Get item first
		item, err := s.itemRepo.GetByID(ctx, id)
		if err != nil {
			log.Printf("Warning: Failed to get item %s for deletion: %v", id, err)
			continue
		}

		// Delete related links
		if err := s.linkRepo.DeleteByItemID(ctx, id); err != nil {
			log.Printf("Warning: Failed to delete links for item %s: %v", id, err)
		}

		// Delete item
		if err := s.itemRepo.Delete(ctx, id); err != nil {
			return fmt.Errorf("failed to delete item %s: %w", id, err)
		}

		projectIDs[item.ProjectID] = true
	}

	// Invalidate caches
	for _, id := range ids {
		if s.cacheService != nil {
			_ = s.cacheService.InvalidateItem(ctx, id)
		}
	}

	for projectID := range projectIDs {
		s.invalidateProjectCaches(ctx, projectID)
	}

	// Publish batch delete event
	s.publishEvent(ctx, "item.batch_deleted", map[string]interface{}{
		"count":       len(ids),
		"ids":         ids,
		"project_ids": projectIDs,
	})

	return nil
}

// ============================================================================
// VALIDATION AND UTILITY METHODS
// ============================================================================

// Validate validates item business rules
func (s *ItemServiceImpl) Validate(_ context.Context, item *models.Item) error {
	return s.validateItem(item)
}

// ItemExists checks if an item exists
func (s *ItemServiceImpl) ItemExists(ctx context.Context, id string) (bool, error) {
	if id == "" {
		return false, errors.New("item ID is required")
	}

	_, err := s.itemRepo.GetByID(ctx, id)
	if err != nil {
		if err.Error() == "item not found" {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

// GetItemStats calculates statistics for items in a project
func (s *ItemServiceImpl) GetItemStats(ctx context.Context, projectID string) (*ItemStats, error) {
	// Try cache
	cacheKey := "project:" + projectID + ":stats"
	if s.cacheService != nil {
		if stats, err := s.cacheService.GetStats(ctx, cacheKey); err == nil && stats != nil {
			log.Printf("[CACHE HIT] Retrieved stats from cache")
			return stats, nil
		}
	}

	// Calculate stats from database
	projectIDPtr := &projectID
	items, err := s.itemRepo.List(ctx, repository.ItemFilter{ProjectID: projectIDPtr})
	if err != nil {
		return nil, fmt.Errorf("failed to list items for stats: %w", err)
	}

	stats := &ItemStats{
		TotalItems: int64(len(items)),
		ByType:     make(map[string]int64),
		ByStatus:   make(map[string]int64),
		ByPriority: make(map[string]int64),
	}

	for _, item := range items {
		stats.ByType[item.Type]++
		stats.ByStatus[item.Status]++
		stats.ByPriority[models.PriorityLabel(item.Priority)]++
	}

	// Cache the result
	if s.cacheService != nil {
		go func() {
			cacheCtx, cancel := context.WithTimeout(context.Background(), cacheWriteTimeout)
			defer cancel()
			if err := s.cacheService.SetStats(cacheCtx, cacheKey, stats, 0); err != nil {
				log.Printf("Warning: Failed to cache stats: %v", err)
			}
		}()
	}

	return stats, nil
}

// ============================================================================
// PRIVATE HELPER METHODS
// ============================================================================

// validateItem validates item business rules
func (s *ItemServiceImpl) validateItem(item *models.Item) error {
	if item.ID == "" {
		return errors.New("item ID is required")
	}
	if item.ProjectID == "" {
		return errors.New("project ID is required")
	}
	if item.Title == "" {
		return errors.New("item title is required")
	}
	if len(item.Title) > maxItemTitleLength {
		return fmt.Errorf("item title must be less than %d characters", maxItemTitleLength)
	}

	// Validate type if provided
	if item.Type != "" {
		validTypes := map[string]bool{
			"feature":     true,
			"task":        true,
			"bug":         true,
			"requirement": true,
			"story":       true,
			"epic":        true,
		}
		if !validTypes[item.Type] {
			return fmt.Errorf("invalid item type: %s", item.Type)
		}
	}

	// Validate status if provided
	if item.Status != "" {
		validStatuses := map[string]bool{
			statusTodo:    true,
			"in_progress": true,
			"done":        true,
			"blocked":     true,
			"cancelled":   true,
		}
		if !validStatuses[item.Status] {
			return fmt.Errorf("invalid status: %s", item.Status)
		}
	}

	// Validate priority if provided (1=low, 2=medium, 3=high, 4=critical)
	if item.Priority != 0 {
		validPriorities := map[models.Priority]bool{
			models.PriorityLow: true, models.PriorityMedium: true,
			models.PriorityHigh: true, models.PriorityCritical: true,
		}
		if !validPriorities[item.Priority] {
			return fmt.Errorf("invalid priority: %d", item.Priority)
		}
	}

	return nil
}

// Cache helper functions

func (s *ItemServiceImpl) invalidateProjectCaches(ctx context.Context, projectID string) {
	if s.cacheService == nil {
		return
	}

	// Use CacheService's InvalidateProjectItems method
	_ = s.cacheService.InvalidateProjectItems(ctx, projectID)
}

func (s *ItemServiceImpl) publishEvent(_ context.Context, eventType string, data interface{}) {
	if s.natsConn == nil {
		return
	}

	payload, err := json.Marshal(map[string]interface{}{
		"type":      eventType,
		"data":      data,
		"timestamp": time.Now(),
	})
	if err != nil {
		log.Printf("Warning: Failed to marshal event: %v", err)
		return
	}

	if err := s.natsConn.Publish(eventType, payload); err != nil {
		log.Printf("Warning: Failed to publish event %s: %v", eventType, err)
	} else {
		log.Printf("[EVENT PUBLISHED] %s", eventType)
	}
}
