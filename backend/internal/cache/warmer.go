package cache

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/repository"
)

const (
	recentItemsWarmLimit = 500
	hotItemsWarmLimit    = 200
	cacheWarmInterval    = 1 * time.Hour
)

// DefaultCacheWarmer provides cache warming functionality
type DefaultCacheWarmer struct {
	cache       Cache
	projectRepo repository.ProjectRepository
	itemRepo    repository.ItemRepository
	linkRepo    repository.LinkRepository
}

// NewCacheWarmer creates a new cache warmer instance
func NewCacheWarmer(
	cache Cache,
	projectRepo repository.ProjectRepository,
	itemRepo repository.ItemRepository,
	linkRepo repository.LinkRepository,
) *DefaultCacheWarmer {
	return &DefaultCacheWarmer{
		cache:       cache,
		projectRepo: projectRepo,
		itemRepo:    itemRepo,
		linkRepo:    linkRepo,
	}
}

// WarmOnStartup warms critical data on application startup
func (warmer *DefaultCacheWarmer) WarmOnStartup(ctx context.Context) error {
	log.Println("[CACHE WARMER] Starting cache warming on startup...")
	startTime := time.Now()

	var errors []error

	// Warm projects (critical - small dataset)
	if err := warmer.warmProjects(ctx); err != nil {
		log.Printf("[CACHE WARMER] Warning: Project warming failed: %v", err)
		errors = append(errors, err)
	}

	// Warm recent items (high priority)
	if err := warmer.warmRecentItems(ctx); err != nil {
		log.Printf("[CACHE WARMER] Warning: Recent items warming failed: %v", err)
		errors = append(errors, err)
	}

	duration := time.Since(startTime)
	log.Printf("[CACHE WARMER] Startup warming completed in %v", duration)

	if len(errors) > 0 {
		return fmt.Errorf("cache warming completed with %d errors", len(errors))
	}

	return nil
}

// warmProjects warms all active projects
func (warmer *DefaultCacheWarmer) warmProjects(ctx context.Context) error {
	log.Println("[CACHE WARMER] Warming projects...")

	projects, err := warmer.projectRepo.List(ctx)
	if err != nil {
		return fmt.Errorf("failed to list projects: %w", err)
	}

	count := 0
	for _, project := range projects {
		cacheKey := ProjectKey(project.ID)
		if err := warmer.cache.Set(ctx, cacheKey, project); err != nil {
			log.Printf("[CACHE WARMER] Warning: Failed to cache project %s: %v", project.ID, err)
			continue
		}
		count++
	}

	log.Printf("[CACHE WARMER] Warmed %d projects", count)
	return nil
}

// warmRecentItems warms items modified in the last 24 hours
func (warmer *DefaultCacheWarmer) warmRecentItems(ctx context.Context) error {
	log.Println("[CACHE WARMER] Warming recent items...")

	// Get recent items (ItemFilter has no UpdatedAfter; use limit for bounded warming)
	items, err := warmer.itemRepo.List(ctx, repository.ItemFilter{
		Limit: recentItemsWarmLimit,
	})
	if err != nil {
		return fmt.Errorf("failed to list recent items: %w", err)
	}

	count := 0
	for _, item := range items {
		cacheKey := ItemKey(item.ID)
		if err := warmer.cache.Set(ctx, cacheKey, item); err != nil {
			log.Printf("[CACHE WARMER] Warning: Failed to cache item %s: %v", item.ID, err)
			continue
		}
		count++
	}

	log.Printf("[CACHE WARMER] Warmed %d recent items", count)
	return nil
}

// WarmProject warms all data for a specific project
func (warmer *DefaultCacheWarmer) WarmProject(ctx context.Context, projectID string) error {
	log.Printf("[CACHE WARMER] Warming project %s...", projectID)

	// Warm project
	project, err := warmer.projectRepo.GetByID(ctx, projectID)
	if err != nil {
		return fmt.Errorf("failed to get project: %w", err)
	}

	projectKey := ProjectKey(projectID)
	if err := warmer.cache.Set(ctx, projectKey, project); err != nil {
		return fmt.Errorf("failed to cache project: %w", err)
	}

	// Warm project items
	projectIDPtr := &projectID
	items, err := warmer.itemRepo.List(ctx, repository.ItemFilter{ProjectID: projectIDPtr})
	if err != nil {
		return fmt.Errorf("failed to list project items: %w", err)
	}

	for _, item := range items {
		itemKey := ItemKey(item.ID)
		if err := warmer.cache.Set(ctx, itemKey, item); err != nil {
			log.Printf("[CACHE WARMER] Warning: Failed to cache item %s: %v", item.ID, err)
		}
	}

	log.Printf("[CACHE WARMER] Warmed project %s with %d items", projectID, len(items))
	return nil
}

// WarmRelatedItems warms items related to a given item (predictive warming)
func (warmer *DefaultCacheWarmer) WarmRelatedItems(ctx context.Context, itemID string) error {
	// Get links from this item
	links, err := warmer.linkRepo.GetBySourceID(ctx, itemID)
	if err != nil {
		return err
	}

	// Warm target items
	for _, link := range links {
		item, err := warmer.itemRepo.GetByID(ctx, link.TargetID)
		if err != nil {
			continue
		}

		cacheKey := ItemKey(item.ID)
		if err := warmer.cache.Set(ctx, cacheKey, item); err != nil {
			log.Printf("[CACHE WARMER] Warning: Failed to cache related item %s: %v", item.ID, err)
		}
	}

	return nil
}

// StartScheduledWarming starts background cache warming
func (warmer *DefaultCacheWarmer) StartScheduledWarming(ctx context.Context) {
	log.Println("[CACHE WARMER] Starting scheduled cache warming...")

	// Warm hot data every hour
	ticker := time.NewTicker(cacheWarmInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			if err := warmer.warmHotData(ctx); err != nil {
				log.Printf("[CACHE WARMER] Error during scheduled warming: %v", err)
			}
		case <-ctx.Done():
			log.Println("[CACHE WARMER] Stopping scheduled warming")
			return
		}
	}
}

// warmHotData warms frequently accessed data
func (warmer *DefaultCacheWarmer) warmHotData(ctx context.Context) error {
	log.Println("[CACHE WARMER] Running scheduled hot data warming...")

	// Warm recent items (ItemFilter has no UpdatedAfter; use limit for bounded warming)
	items, err := warmer.itemRepo.List(ctx, repository.ItemFilter{
		Limit: hotItemsWarmLimit,
	})
	if err != nil {
		return err
	}

	for _, item := range items {
		cacheKey := ItemKey(item.ID)
		if err := warmer.cache.Set(ctx, cacheKey, item); err != nil {
			log.Printf("[CACHE WARMER] Warning: Failed to cache item %s: %v", item.ID, err)
		}
	}

	log.Printf("[CACHE WARMER] Warmed %d hot items", len(items))
	return nil
}

// GetStats returns cache warmer statistics
func (warmer *DefaultCacheWarmer) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"status": "active",
		// Add more stats as needed
	}
}
