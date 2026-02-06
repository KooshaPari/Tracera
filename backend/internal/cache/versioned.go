package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"time"
)

// CacheVersion is the current cache schema version
// Increment this when cache data structure changes
const CacheVersion = "v2"

// VersionedCache wraps Cache with versioning support
type VersionedCache struct {
	cache   Cache
	version string
}

// NewVersionedCache creates a cache with versioning support
func NewVersionedCache(cache Cache) *VersionedCache {
	return &VersionedCache{
		cache:   cache,
		version: CacheVersion,
	}
}

// VersionedEntry wraps cached data with version metadata
type VersionedEntry struct {
	Version  string      `json:"version"`
	Data     interface{} `json:"data"`
	CachedAt time.Time   `json:"cached_at"`
}

// Get retrieves a versioned value from cache
func (vc *VersionedCache) Get(ctx context.Context, key string, dest interface{}) error {
	versionedKey := vc.versionedKey(key)

	var entry VersionedEntry
	if err := vc.cache.Get(ctx, versionedKey, &entry); err != nil {
		return err
	}

	// Check version compatibility
	if entry.Version != vc.version {
		// Version mismatch - invalidate and return miss
		if err := vc.cache.Delete(ctx, versionedKey); err != nil {
			return fmt.Errorf(
				"cache version mismatch: expected %s, got %s; failed to delete stale entry: %w",
				vc.version,
				entry.Version,
				err,
			)
		}
		return fmt.Errorf("cache version mismatch: expected %s, got %s", vc.version, entry.Version)
	}

	// Unmarshal data into destination
	dataBytes, err := json.Marshal(entry.Data)
	if err != nil {
		return fmt.Errorf("failed to marshal entry data: %w", err)
	}

	if err := json.Unmarshal(dataBytes, dest); err != nil {
		return fmt.Errorf("failed to unmarshal entry data: %w", err)
	}

	return nil
}

// Set stores a versioned value in cache
func (vc *VersionedCache) Set(ctx context.Context, key string, value interface{}) error {
	versionedKey := vc.versionedKey(key)

	entry := VersionedEntry{
		Version:  vc.version,
		Data:     value,
		CachedAt: time.Now(),
	}

	return vc.cache.Set(ctx, versionedKey, entry)
}

// Delete removes a versioned value from cache
func (vc *VersionedCache) Delete(ctx context.Context, keys ...string) error {
	versionedKeys := make([]string, len(keys))
	for i, key := range keys {
		versionedKeys[i] = vc.versionedKey(key)
	}
	return vc.cache.Delete(ctx, versionedKeys...)
}

// InvalidatePattern invalidates all keys matching a pattern
func (vc *VersionedCache) InvalidatePattern(ctx context.Context, pattern string) error {
	versionedPattern := vc.versionedKey(pattern)
	return vc.cache.InvalidatePattern(ctx, versionedPattern)
}

// Close closes the underlying cache
func (vc *VersionedCache) Close() error {
	return vc.cache.Close()
}

// versionedKey returns the cache key with version prefix
func (vc *VersionedCache) versionedKey(key string) string {
	return vc.version + ":" + key
}

// GetVersion returns the current cache version
func (vc *VersionedCache) GetVersion() string {
	return vc.version
}

// BumpVersion increments the cache version globally
// This effectively invalidates all cached data
func BumpVersion(_ string) {
	// In production, this would be coordinated across all instances
	// For now, it's a compile-time constant
	// CacheVersion = newVersion // Commented out - requires code change
	panic("BumpVersion must be done by updating CacheVersion constant and redeploying")
}

// VersionMetadata returns metadata about cache versioning
func (vc *VersionedCache) VersionMetadata() map[string]interface{} {
	return map[string]interface{}{
		"current_version": vc.version,
		"version_scheme":  "semantic",
		"version_prefix":  true,
	}
}
