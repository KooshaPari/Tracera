package services

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
)

// CacheServiceImpl implements the CacheService interface with typed operations
type CacheServiceImpl struct {
	cache    cache.Cache
	cacheTTL time.Duration
}

const (
	cacheKeyNotFoundError = "key not found"
)

// NewCacheServiceImpl creates a new cache service implementation
func NewCacheServiceImpl(cache cache.Cache, cacheTTL time.Duration) CacheService {
	if cacheTTL == 0 {
		cacheTTL = defaultCacheTTL
	}
	return &CacheServiceImpl{
		cache:    cache,
		cacheTTL: cacheTTL,
	}
}

// Generic cache operations

// Get retrieves a value from cache
func (s *CacheServiceImpl) Get(ctx context.Context, key string) (string, error) {
	if s.cache == nil {
		return "", errors.New("cache not available")
	}

	var value string
	err := s.cache.Get(ctx, key, &value)
	if err != nil {
		// Check if it's a cacheKeyNotFoundError error vs actual error
		if err.Error() == cacheKeyNotFoundError {
			return "", nil
		}
		return "", err
	}

	return value, nil
}

// Set stores a value in cache with TTL
func (s *CacheServiceImpl) Set(ctx context.Context, key string, value string, _ time.Duration) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, value)
}

// Delete removes a value from cache
func (s *CacheServiceImpl) Delete(ctx context.Context, key string) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Delete(ctx, key)
}

// InvalidatePattern invalidates all cache keys matching a pattern
func (s *CacheServiceImpl) InvalidatePattern(ctx context.Context, pattern string) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.InvalidatePattern(ctx, pattern)
}

// GetMulti retrieves multiple values atomically
func (s *CacheServiceImpl) GetMulti(ctx context.Context, keys []string) (map[string]string, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	result := make(map[string]string)
	for _, key := range keys {
		var value string
		if err := s.cache.Get(ctx, key, &value); err == nil && value != "" {
			result[key] = value
		}
	}

	return result, nil
}

// SetMulti stores multiple values atomically
func (s *CacheServiceImpl) SetMulti(ctx context.Context, items map[string]string, _ time.Duration) error {
	if s.cache == nil {
		return nil
	}

	for key, value := range items {
		if err := s.cache.Set(ctx, key, value); err != nil {
			return err
		}
	}

	return nil
}

// Exists checks if a key exists
func (s *CacheServiceImpl) Exists(ctx context.Context, key string) (bool, error) {
	if s.cache == nil {
		return false, errors.New("cache not available")
	}

	var value string
	err := s.cache.Get(ctx, key, &value)
	// Key exists if no error occurred
	return err == nil, nil
}

// Expire sets TTL on existing key (not implemented in base cache interface)
func (s *CacheServiceImpl) Expire(_ context.Context, _ string, _ time.Duration) error {
	// Not supported by base cache interface - would need Redis-specific implementation
	return errors.New("expire not supported")
}

// Entity-specific operations

// GetItem retrieves an item from cache by ID
func (s *CacheServiceImpl) GetItem(ctx context.Context, itemID string) (*models.Item, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	cacheKey := "item:" + itemID
	var item models.Item
	err := s.cache.Get(ctx, cacheKey, &item)
	if err != nil {
		// Check if it's a cacheKeyNotFoundError error vs actual error (like JSON parse error)
		if err.Error() == cacheKeyNotFoundError {
			return nil, nil
		}
		// Return actual errors (like invalid JSON)
		return nil, err
	}

	return &item, nil
}

// SetItem stores an item in cache
func (s *CacheServiceImpl) SetItem(ctx context.Context, item *models.Item) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "item:" + item.ID
	return s.cache.Set(ctx, cacheKey, item)
}

// InvalidateItem removes an item from cache
func (s *CacheServiceImpl) InvalidateItem(ctx context.Context, itemID string) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "item:" + itemID
	return s.cache.Delete(ctx, cacheKey)
}

// GetProject retrieves a project from cache
func (s *CacheServiceImpl) GetProject(ctx context.Context, projectID string) (*models.Project, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	cacheKey := "project:" + projectID
	var project models.Project
	err := s.cache.Get(ctx, cacheKey, &project)
	if err != nil {
		// Check if it's a cacheKeyNotFoundError error vs actual error
		if err.Error() == cacheKeyNotFoundError {
			return nil, nil
		}
		return nil, err
	}

	return &project, nil
}

// SetProject stores a project in cache
func (s *CacheServiceImpl) SetProject(ctx context.Context, project *models.Project) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "project:" + project.ID
	return s.cache.Set(ctx, cacheKey, project)
}

// InvalidateProject removes a project from cache
func (s *CacheServiceImpl) InvalidateProject(ctx context.Context, projectID string) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "project:" + projectID
	return s.cache.Delete(ctx, cacheKey)
}

// GetLink retrieves a link from cache
func (s *CacheServiceImpl) GetLink(ctx context.Context, linkID string) (*models.Link, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	cacheKey := "link:" + linkID
	var link models.Link
	err := s.cache.Get(ctx, cacheKey, &link)
	if err != nil {
		// Check if it's a cacheKeyNotFoundError error vs actual error
		if err.Error() == cacheKeyNotFoundError {
			return nil, nil
		}
		return nil, err
	}

	return &link, nil
}

// SetLink stores a link in cache
func (s *CacheServiceImpl) SetLink(ctx context.Context, link *models.Link) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "link:" + link.ID
	return s.cache.Set(ctx, cacheKey, link)
}

// InvalidateLink removes a link from cache
func (s *CacheServiceImpl) InvalidateLink(ctx context.Context, linkID string) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "link:" + linkID
	return s.cache.Delete(ctx, cacheKey)
}

// GetAgent retrieves an agent from cache
func (s *CacheServiceImpl) GetAgent(ctx context.Context, agentID string) (*models.Agent, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	cacheKey := "agent:" + agentID
	var agent models.Agent
	err := s.cache.Get(ctx, cacheKey, &agent)
	if err != nil {
		// Check if it's a cacheKeyNotFoundError error vs actual error
		if err.Error() == cacheKeyNotFoundError {
			return nil, nil
		}
		return nil, err
	}

	return &agent, nil
}

// SetAgent stores an agent in cache
func (s *CacheServiceImpl) SetAgent(ctx context.Context, agent *models.Agent) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "agent:" + agent.ID
	return s.cache.Set(ctx, cacheKey, agent)
}

// InvalidateAgent removes an agent from cache
func (s *CacheServiceImpl) InvalidateAgent(ctx context.Context, agentID string) error {
	if s.cache == nil {
		return nil
	}

	cacheKey := "agent:" + agentID
	return s.cache.Delete(ctx, cacheKey)
}

// List cache operations

// GetItems retrieves a list of items from cache by key
func (s *CacheServiceImpl) GetItems(ctx context.Context, key string) ([]*models.Item, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var items []*models.Item
	err := s.cache.Get(ctx, key, &items)
	if err != nil {
		// Check if it's a cacheKeyNotFoundError error vs actual error
		if err.Error() == cacheKeyNotFoundError {
			return nil, nil
		}
		return nil, err
	}

	return items, nil
}

// SetItems stores a list of items in cache
func (s *CacheServiceImpl) SetItems(ctx context.Context, key string, items []*models.Item, _ time.Duration) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, items)
}

// GetStats retrieves item stats from cache
func (s *CacheServiceImpl) GetStats(ctx context.Context, key string) (*ItemStats, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	var stats ItemStats
	err := s.cache.Get(ctx, key, &stats)
	if err != nil {
		// Check if it's a cacheKeyNotFoundError error vs actual error
		if err.Error() == cacheKeyNotFoundError {
			return nil, nil
		}
		return nil, err
	}

	return &stats, nil
}

// SetStats stores item stats in cache
func (s *CacheServiceImpl) SetStats(ctx context.Context, key string, stats *ItemStats, _ time.Duration) error {
	if s.cache == nil {
		return nil
	}

	return s.cache.Set(ctx, key, stats)
}

// Batch operations

// GetItemsBatch retrieves multiple items from cache
func (s *CacheServiceImpl) GetItemsBatch(ctx context.Context, itemIDs []string) (map[string]*models.Item, error) {
	if s.cache == nil {
		return nil, errors.New("cache not available")
	}

	result := make(map[string]*models.Item)
	for _, itemID := range itemIDs {
		item, err := s.GetItem(ctx, itemID)
		if err == nil && item != nil {
			result[itemID] = item
		}
	}

	return result, nil
}

// SetItemsBatch stores multiple items in cache
func (s *CacheServiceImpl) SetItemsBatch(ctx context.Context, items []*models.Item) error {
	if s.cache == nil {
		return nil
	}

	for _, item := range items {
		if err := s.SetItem(ctx, item); err != nil {
			return err
		}
	}

	return nil
}

// InvalidateProjectItems removes all items for a project from cache
func (s *CacheServiceImpl) InvalidateProjectItems(ctx context.Context, projectID string) error {
	if s.cache == nil {
		return nil
	}

	// Invalidate list cache
	listKey := "items:project:" + projectID + ":page:0"
	if err := s.cache.Delete(ctx, listKey); err != nil {
		slog.Warn("failed to invalidate list cache", "error", err)
	}

	// Invalidate stats cache
	statsKey := "project:" + projectID + ":stats"
	if err := s.cache.Delete(ctx, statsKey); err != nil {
		slog.Warn("failed to invalidate stats cache", "error", err)
	}

	return nil
}

// HealthCheck verifies cache connectivity
func (s *CacheServiceImpl) HealthCheck(ctx context.Context) error {
	if s.cache == nil {
		return errors.New("cache not available")
	}

	// Try to set and get a test value
	testKey := "health:check"
	testValue := map[string]interface{}{"status": "ok", "timestamp": time.Now().Unix()}

	data, err := json.Marshal(testValue)
	if err != nil {
		return fmt.Errorf("failed to marshal test value: %w", err)
	}

	if err := s.cache.Set(ctx, testKey, string(data)); err != nil {
		return fmt.Errorf("failed to set test value: %w", err)
	}

	var retrieved string
	if err := s.cache.Get(ctx, testKey, &retrieved); err != nil {
		return fmt.Errorf("failed to get test value: %w", err)
	}

	if err := s.cache.Delete(ctx, testKey); err != nil {
		slog.Warn("failed to cleanup test key", "error", err)
	}

	return nil
}
