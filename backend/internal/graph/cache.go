package graph

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"sync"
	"time"
)

// CacheEntry represents a cached graph result
type CacheEntry struct {
	Data      interface{}
	ExpiresAt time.Time
}

// Cache provides caching for frequently accessed graph structures
type Cache struct {
	mu      sync.RWMutex
	entries map[string]*CacheEntry
	ttl     time.Duration
}

// NewCache creates a new cache with the specified TTL
func NewCache(ttl time.Duration) *Cache {
	cache := &Cache{
		entries: make(map[string]*CacheEntry),
		ttl:     ttl,
	}

	// Start cleanup goroutine
	go cache.cleanupExpired()

	return cache
}

// generateKey creates a cache key from parameters
func generateKey(prefix string, params ...interface{}) string {
	data, err := json.Marshal(params)
	if err != nil {
		data = []byte(prefix)
	}
	hash := sha256.Sum256(data)
	return prefix + ":" + hex.EncodeToString(hash[:8])
}

// Get retrieves a value from cache
func (c *Cache) Get(key string) (interface{}, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	entry, exists := c.entries[key]
	if !exists {
		return nil, false
	}

	if time.Now().After(entry.ExpiresAt) {
		return nil, false
	}

	return entry.Data, true
}

// Set stores a value in cache
func (c *Cache) Set(key string, value interface{}) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.entries[key] = &CacheEntry{
		Data:      value,
		ExpiresAt: time.Now().Add(c.ttl),
	}
}

// Delete removes a value from cache
func (c *Cache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	delete(c.entries, key)
}

// Clear removes all entries from cache
func (c *Cache) Clear() {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.entries = make(map[string]*CacheEntry)
}

// cleanupExpired removes expired entries periodically
func (c *Cache) cleanupExpired() {
	ticker := time.NewTicker(time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		c.mu.Lock()
		now := time.Now()
		for key, entry := range c.entries {
			if now.After(entry.ExpiresAt) {
				delete(c.entries, key)
			}
		}
		c.mu.Unlock()
	}
}

// Stats returns cache statistics
func (c *Cache) Stats() map[string]interface{} {
	c.mu.RLock()
	defer c.mu.RUnlock()

	validEntries := 0
	expiredEntries := 0
	now := time.Now()

	for _, entry := range c.entries {
		if now.After(entry.ExpiresAt) {
			expiredEntries++
		} else {
			validEntries++
		}
	}

	return map[string]interface{}{
		"total_entries":   len(c.entries),
		"valid_entries":   validEntries,
		"expired_entries": expiredEntries,
		"ttl_seconds":     c.ttl.Seconds(),
	}
}

// CachedGraph wraps Graph with caching capabilities
type CachedGraph struct {
	*Graph
	cache *Cache
}

// NewCachedGraph creates a graph with caching enabled
func NewCachedGraph(g *Graph, cacheTTL time.Duration) *CachedGraph {
	return &CachedGraph{
		Graph: g,
		cache: NewCache(cacheTTL),
	}
}

// GetDescendantsCached returns cached descendants or computes them
func (cg *CachedGraph) GetDescendantsCached(ctx context.Context, itemID string, maxDepth int) (*Result, error) {
	key := generateKey("descendants", itemID, maxDepth)

	if cached, ok := cg.cache.Get(key); ok {
		if result, ok := cached.(*Result); ok {
			return result, nil
		}
	}

	result, err := cg.GetDescendants(ctx, itemID, maxDepth)
	if err != nil {
		return nil, err
	}

	cg.cache.Set(key, result)
	return result, nil
}

// GetAncestorsCached returns cached ancestors or computes them
func (cg *CachedGraph) GetAncestorsCached(ctx context.Context, itemID string, maxDepth int) (*Result, error) {
	key := generateKey("ancestors", itemID, maxDepth)

	if cached, ok := cg.cache.Get(key); ok {
		if result, ok := cached.(*Result); ok {
			return result, nil
		}
	}

	result, err := cg.GetAncestors(ctx, itemID, maxDepth)
	if err != nil {
		return nil, err
	}

	cg.cache.Set(key, result)
	return result, nil
}

// FindPathCached returns cached path or computes it
func (cg *CachedGraph) FindPathCached(ctx context.Context, sourceID, targetID string) (*PathResult, error) {
	key := generateKey("path", sourceID, targetID)

	if cached, ok := cg.cache.Get(key); ok {
		if result, ok := cached.(*PathResult); ok {
			return result, nil
		}
	}

	result, err := cg.FindPath(ctx, sourceID, targetID)
	if err != nil {
		return nil, err
	}

	cg.cache.Set(key, result)
	return result, nil
}

// GetFullCached returns cached full graph or computes it
func (cg *CachedGraph) GetFullCached(ctx context.Context, projectID string) (*Result, error) {
	key := generateKey("full_graph", projectID)

	if cached, ok := cg.cache.Get(key); ok {
		if result, ok := cached.(*Result); ok {
			return result, nil
		}
	}

	result, err := cg.GetFullGraph(ctx, projectID)
	if err != nil {
		return nil, err
	}

	cg.cache.Set(key, result)
	return result, nil
}

// ComputeTransitiveClosureCached returns cached transitive closure or computes it
func (cg *CachedGraph) ComputeTransitiveClosureCached(ctx context.Context, projectID string) (*TransitiveClosureResult, error) {
	key := generateKey("transitive_closure", projectID)

	if cached, ok := cg.cache.Get(key); ok {
		if result, ok := cached.(*TransitiveClosureResult); ok {
			return result, nil
		}
	}

	result, err := cg.ComputeTransitiveClosure(ctx, projectID)
	if err != nil {
		return nil, err
	}

	cg.cache.Set(key, result)
	return result, nil
}

// InvalidateItem invalidates cache entries related to an item
func (cg *CachedGraph) InvalidateItem(_ string) {
	// For simplicity, clear entire cache
	// In production, implement more granular invalidation
	cg.cache.Clear()
}

// InvalidateProject invalidates cache entries for a project
func (cg *CachedGraph) InvalidateProject(_ string) {
	// For simplicity, clear entire cache
	// In production, implement more granular invalidation
	cg.cache.Clear()
}

// CacheStats returns cache statistics
func (cg *CachedGraph) CacheStats() map[string]interface{} {
	return cg.cache.Stats()
}
