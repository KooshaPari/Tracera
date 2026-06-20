package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/nats-io/nats.go"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// Ensure LinkServiceImpl implements LinkService interface
var _ LinkService = (*LinkServiceImpl)(nil)

const (
	defaultLinkCacheTTL = 5 * time.Minute
	asyncOpTimeout      = 2 * time.Second
)

// LinkServiceImpl implements LinkService with cross-service calls to ItemService
// CRITICAL: Uses ItemService API for item validation, NOT ItemRepository
type LinkServiceImpl struct {
	linkRepo    repository.LinkRepository
	itemService ItemService // Cross-service dependency via interface
	cache       cache.Cache
	natsConn    *nats.Conn
	cacheTTL    time.Duration
}

// NewLinkServiceImpl creates a new link service implementation
// Note: Takes ItemService, not ItemRepository
func NewLinkServiceImpl(
	linkRepo repository.LinkRepository,
	itemService ItemService,
	cache cache.Cache,
	natsConn *nats.Conn,
) LinkService {
	if linkRepo == nil {
		panic("linkRepo cannot be nil")
	}
	if itemService == nil {
		panic("itemService cannot be nil")
	}

	return &LinkServiceImpl{
		linkRepo:    linkRepo,
		itemService: itemService,
		cache:       cache,
		natsConn:    natsConn,
		cacheTTL:    defaultLinkCacheTTL,
	}
}

// CreateLink creates a link between items
// Validates both source and target items exist via ItemService API
func (s *LinkServiceImpl) CreateLink(ctx context.Context, link *models.Link) error {
	// Validate input
	if link.SourceID == "" {
		return errors.New("source ID is required")
	}
	if link.TargetID == "" {
		return errors.New("target ID is required")
	}
	if link.Type == "" {
		return errors.New("link type is required")
	}

	// CRITICAL: Use ItemService API, not ItemRepository
	// Verify source item exists
	sourceItem, err := s.itemService.GetItem(ctx, link.SourceID)
	if err != nil {
		return fmt.Errorf("source item not found: %w", err)
	}

	// CRITICAL: Use ItemService API, not ItemRepository
	// Verify target item exists
	targetItem, err := s.itemService.GetItem(ctx, link.TargetID)
	if err != nil {
		return fmt.Errorf("target item not found: %w", err)
	}

	// Business logic: validate link compatibility
	if err := s.validateLinkCompatibility(sourceItem, targetItem); err != nil {
		return fmt.Errorf("link validation failed: %w", err)
	}

	// Persist to database (using OWN repository)
	if err := s.linkRepo.Create(ctx, link); err != nil {
		return fmt.Errorf("failed to create link: %w", err)
	}

	// Publish event (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		if err := s.publishLinkEvent(ctx, "link.created", link); err != nil {
			slog.Error("Warning: Failed to publish link created event", "error", err)
		}
	})

	// Invalidate cache (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		s.invalidateLinkCache(ctx, link)
	})

	return nil
}

// GetLink retrieves a link by ID
func (s *LinkServiceImpl) GetLink(ctx context.Context, id string) (*models.Link, error) {
	if id == "" {
		return nil, errors.New("link ID is required")
	}

	// Try cache first (cache-aside pattern)
	cacheKey := "link:" + id
	if s.cache != nil {
		var cached models.Link
		if err := s.cache.Get(ctx, cacheKey, &cached); err == nil {
			slog.Info("[CACHE HIT] Retrieved link from cache", "id", id)
			return &cached, nil
		}
	}

	// Cache miss - fetch from database
	link, err := s.linkRepo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get link: %w", err)
	}

	// Populate cache (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		if s.cache != nil {
			if err := s.cache.Set(ctx, cacheKey, link); err != nil {
				slog.Error("Warning: Failed to cache link", "error", id, "error", err)
			}
		}
	})

	return link, nil
}

// ListLinks lists links with optional filtering
func (s *LinkServiceImpl) ListLinks(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	links, err := s.linkRepo.List(ctx, filter)
	if err != nil {
		return nil, fmt.Errorf("failed to list links: %w", err)
	}

	return links, nil
}

// UpdateLink updates an existing link
func (s *LinkServiceImpl) UpdateLink(ctx context.Context, link *models.Link) error {
	if link.ID == "" {
		return errors.New("link ID is required")
	}

	// Validate if source/target changed
	if link.SourceID != "" && link.TargetID != "" {
		// CRITICAL: Use ItemService API
		sourceItem, err := s.itemService.GetItem(ctx, link.SourceID)
		if err != nil {
			return fmt.Errorf("source item not found: %w", err)
		}

		// CRITICAL: Use ItemService API
		targetItem, err := s.itemService.GetItem(ctx, link.TargetID)
		if err != nil {
			return fmt.Errorf("target item not found: %w", err)
		}

		if err := s.validateLinkCompatibility(sourceItem, targetItem); err != nil {
			return fmt.Errorf("link validation failed: %w", err)
		}
	}

	// Update in database
	if err := s.linkRepo.Update(ctx, link); err != nil {
		return fmt.Errorf("failed to update link: %w", err)
	}

	// Publish event (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		if err := s.publishLinkEvent(ctx, "link.updated", link); err != nil {
			slog.Error("Warning: Failed to publish link updated event", "error", err)
		}
	})

	// Invalidate cache (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		s.invalidateLinkCache(ctx, link)
	})

	return nil
}

// DeleteLink deletes a link
func (s *LinkServiceImpl) DeleteLink(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("link ID is required")
	}

	// Get link first for cache invalidation
	link, err := s.linkRepo.GetByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get link for deletion: %w", err)
	}

	// Delete from database
	if err := s.linkRepo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete link: %w", err)
	}

	// Publish event (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		if err := s.publishLinkDeletedEvent(ctx, id); err != nil {
			slog.Error("Warning: Failed to publish link deleted event", "error", err)
		}
	})

	// Invalidate cache (non-blocking)
	asyncFireAndForget(func(ctx context.Context) {
		s.invalidateLinkCache(ctx, link)
	})

	return nil
}

// GetItemDependencies returns dependency graph for an item
// Shows complex cross-service usage
func (s *LinkServiceImpl) GetItemDependencies(ctx context.Context, itemID string) (*DependencyGraph, error) {
	if itemID == "" {
		return nil, errors.New("item ID is required")
	}

	cacheKey := "dependencies:" + itemID
	if cached := s.getDependencyGraphFromCache(ctx, cacheKey, itemID); cached != nil {
		return cached, nil
	}

	// CRITICAL: First, verify item exists via service API
	item, err := s.itemService.GetItem(ctx, itemID)
	if err != nil {
		return nil, fmt.Errorf("item not found: %w", err)
	}

	dependencies, dependents, err := s.loadDependencyLinks(ctx, itemID)
	if err != nil {
		return nil, err
	}

	graph := s.buildDependencyGraph(ctx, itemID, item, dependencies, dependents)
	s.cacheDependencyGraph(cacheKey, itemID, graph)

	return graph, nil
}

func (s *LinkServiceImpl) getDependencyGraphFromCache(ctx context.Context, cacheKey, itemID string) *DependencyGraph {
	if s.cache == nil {
		return nil
	}

	var cached DependencyGraph
	if err := s.cache.Get(ctx, cacheKey, &cached); err == nil {
		slog.Info("[CACHE HIT] Retrieved dependencies for item from cache", "id", itemID)
		return &cached
	}

	return nil
}

func (s *LinkServiceImpl) loadDependencyLinks(
	ctx context.Context,
	itemID string,
) ([]*models.Link, []*models.Link, error) {
	dependencies, err := s.linkRepo.GetBySourceID(ctx, itemID)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get dependencies: %w", err)
	}

	dependents, err := s.linkRepo.GetByTargetID(ctx, itemID)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get dependents: %w", err)
	}

	return dependencies, dependents, nil
}

func (s *LinkServiceImpl) buildDependencyGraph(
	ctx context.Context,
	itemID string,
	item *models.Item,
	dependencies []*models.Link,
	dependents []*models.Link,
) *DependencyGraph {
	graph := &DependencyGraph{
		ItemID:       itemID,
		Dependencies: dependencies,
		Dependents:   dependents,
		Items:        make(map[string]*models.Item),
	}
	graph.Items[itemID] = item

	s.populateDependencyItems(ctx, graph, dependencies, func(link *models.Link) string { return link.TargetID })
	s.populateDependencyItems(ctx, graph, dependents, func(link *models.Link) string { return link.SourceID })

	return graph
}

func (s *LinkServiceImpl) populateDependencyItems(
	ctx context.Context,
	graph *DependencyGraph,
	links []*models.Link,
	resolveID func(*models.Link) string,
) {
	for _, link := range links {
		itemID := resolveID(link)
		if _, exists := graph.Items[itemID]; exists {
			continue
		}

		linkedItem, err := s.itemService.GetItem(ctx, itemID)
		if err != nil {
			slog.Error("Warning: Failed to load item", "error", itemID, "error", err)
			continue
		}
		graph.Items[itemID] = linkedItem
	}
}

func (s *LinkServiceImpl) cacheDependencyGraph(cacheKey, itemID string, graph *DependencyGraph) {
	asyncFireAndForget(func(ctx context.Context) {
		if s.cache == nil {
			return
		}
		if err := s.cache.Set(ctx, cacheKey, graph); err != nil {
			slog.Error("Warning: Failed to cache dependencies for item", "error", itemID, "error", err)
		}
	})
}

// validateLinkCompatibility checks if two items can be linked
func (s *LinkServiceImpl) validateLinkCompatibility(source, target *models.Item) error {
	// Business rule: Items must be in same project
	if source.ProjectID != target.ProjectID {
		return errors.New("items must be in the same project")
	}

	// Business rule: Cannot link item to itself
	if source.ID == target.ID {
		return errors.New("cannot create self-referencing link")
	}

	return nil
}

// invalidateLinkCache invalidates all caches related to a link
func (s *LinkServiceImpl) invalidateLinkCache(ctx context.Context, link *models.Link) {
	if s.cache == nil {
		return
	}

	// Invalidate link cache
	linkCacheKey := "link:" + link.ID
	if err := s.cache.Delete(ctx, linkCacheKey); err != nil {
		slog.Error("Warning: Failed to invalidate link cache", "error", linkCacheKey, "error", err)
	}

	// Invalidate dependency caches for both source and target
	sourceDepsKey := "dependencies:" + link.SourceID
	if err := s.cache.Delete(ctx, sourceDepsKey); err != nil {
		slog.Error("Warning: Failed to invalidate source dependencies cache", "error", sourceDepsKey, "error", err)
	}

	targetDepsKey := "dependencies:" + link.TargetID
	if err := s.cache.Delete(ctx, targetDepsKey); err != nil {
		slog.Error("Warning: Failed to invalidate target dependencies cache", "error", targetDepsKey, "error", err)
	}
}

// publishLinkEvent publishes a link event to NATS
func (s *LinkServiceImpl) publishLinkEvent(_ context.Context, eventType string, link *models.Link) error {
	if s.natsConn == nil {
		return nil // NATS not configured, skip silently
	}

	payload, err := json.Marshal(map[string]interface{}{
		"type":      eventType,
		"link_id":   link.ID,
		"source_id": link.SourceID,
		"target_id": link.TargetID,
		"link_type": link.Type,
		"timestamp": time.Now(),
	})
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	subject := "links." + eventType
	if err := s.natsConn.Publish(subject, payload); err != nil {
		return fmt.Errorf("failed to publish event: %w", err)
	}

	slog.Info("[EVENT PUBLISHED] for link", "detail", eventType, "id", link.ID)
	return nil
}

// publishLinkDeletedEvent publishes a link deleted event
func (s *LinkServiceImpl) publishLinkDeletedEvent(_ context.Context, linkID string) error {
	if s.natsConn == nil {
		return nil
	}

	payload, err := json.Marshal(map[string]interface{}{
		"type":      "link.deleted",
		"link_id":   linkID,
		"timestamp": time.Now(),
	})
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	if err := s.natsConn.Publish("links.link.deleted", payload); err != nil {
		return fmt.Errorf("failed to publish event: %w", err)
	}

	slog.Info("[EVENT PUBLISHED] link.deleted for link", "id", linkID)
	return nil
}
