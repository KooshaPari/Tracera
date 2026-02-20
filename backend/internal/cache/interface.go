package cache

import "context"

// Cache is the interface for cache implementations
type Cache interface {
	// Get retrieves a value from cache
	Get(ctx context.Context, key string, dest interface{}) error

	// Set stores a value in cache
	Set(ctx context.Context, key string, value interface{}) error

	// Delete removes values from cache
	Delete(ctx context.Context, keys ...string) error

	// InvalidatePattern deletes all keys matching a pattern (optional)
	InvalidatePattern(ctx context.Context, pattern string) error

	// Close closes the cache connection
	Close() error
}
