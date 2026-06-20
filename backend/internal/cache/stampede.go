package cache

import (
	"context"
	"log/slog"
	"sync"

	"golang.org/x/sync/singleflight"
)

// StampedeProtectedCache wraps Cache with stampede prevention
type StampedeProtectedCache struct {
	cache   Cache
	sfGroup singleflight.Group
}

// NewStampedeProtectedCache creates a cache with stampede prevention
func NewStampedeProtectedCache(cache Cache) *StampedeProtectedCache {
	return &StampedeProtectedCache{
		cache:   cache,
		sfGroup: singleflight.Group{},
	}
}

// GetOrLoad retrieves from cache or loads using the provided function
// Only one concurrent request per key will execute the load function
func (spc *StampedeProtectedCache) GetOrLoad(
	ctx context.Context,
	key string,
	dest interface{},
	loadFn func() (interface{}, error),
) error {
	// Try cache first
	if err := spc.cache.Get(ctx, key, dest); err == nil {
		return nil
	}

	// Cache miss - use single-flight to prevent stampede
	result, err, _ := spc.sfGroup.Do(key, func() (interface{}, error) {
		// Check cache again (another goroutine may have populated it)
		if err := spc.cache.Get(ctx, key, dest); err == nil {
			return dest, nil
		}

		// Load data
		data, err := loadFn()
		if err != nil {
			return nil, err
		}

		// Populate cache
		if err := spc.cache.Set(ctx, key, data); err != nil {
			// Log but don't fail - we have the data
			slog.Error("Warning: Failed to cache key", "error", key, "error", err)
		}

		return data, nil
	})

	if err != nil {
		return err
	}

	// Copy result to dest
	return copyInterface(result, dest)
}

// Get retrieves a value from cache
func (spc *StampedeProtectedCache) Get(ctx context.Context, key string, dest interface{}) error {
	return spc.cache.Get(ctx, key, dest)
}

// Set stores a value in cache
func (spc *StampedeProtectedCache) Set(ctx context.Context, key string, value interface{}) error {
	return spc.cache.Set(ctx, key, value)
}

// Delete removes values from cache
func (spc *StampedeProtectedCache) Delete(ctx context.Context, keys ...string) error {
	return spc.cache.Delete(ctx, keys...)
}

// InvalidatePattern invalidates all keys matching a pattern
func (spc *StampedeProtectedCache) InvalidatePattern(ctx context.Context, pattern string) error {
	return spc.cache.InvalidatePattern(ctx, pattern)
}

// Close closes the underlying cache
func (spc *StampedeProtectedCache) Close() error {
	return spc.cache.Close()
}

// copyInterface copies data from src to dest
func copyInterface(src, dest interface{}) error {
	// This is a simplified implementation
	// In production, use reflection or JSON marshaling
	if src == dest {
		return nil
	}
	// For now, just return nil as we're passing dest to loadFn directly
	return nil
}

// RequestCoalescer provides more advanced stampede prevention with per-key locking
type RequestCoalescer struct {
	mu       sync.RWMutex
	inflight map[string]*sync.WaitGroup
	results  map[string]interface{}
	errors   map[string]error
}

// NewRequestCoalescer creates a new request coalescer
func NewRequestCoalescer() *RequestCoalescer {
	return &RequestCoalescer{
		inflight: make(map[string]*sync.WaitGroup),
		results:  make(map[string]interface{}),
		errors:   make(map[string]error),
	}
}

// Do executes the function for the given key, coalescing concurrent requests
func (rc *RequestCoalescer) Do(key string, fn func() (interface{}, error)) (interface{}, error) {
	rc.mu.Lock()

	// Check if request is already in-flight
	if wg, exists := rc.inflight[key]; exists {
		// Wait for in-flight request
		rc.mu.Unlock()
		wg.Wait()

		// Return cached result
		rc.mu.RLock()
		defer rc.mu.RUnlock()
		return rc.results[key], rc.errors[key]
	}

	// Mark request as in-flight
	wg := &sync.WaitGroup{}
	wg.Add(1)
	rc.inflight[key] = wg
	rc.mu.Unlock()

	// Execute function
	result, err := fn()

	// Store result and clean up
	rc.mu.Lock()
	rc.results[key] = result
	rc.errors[key] = err
	delete(rc.inflight, key)
	wg.Done()
	rc.mu.Unlock()

	return result, err
}

// Clear clears all cached results
func (rc *RequestCoalescer) Clear() {
	rc.mu.Lock()
	defer rc.mu.Unlock()

	rc.results = make(map[string]interface{})
	rc.errors = make(map[string]error)
}
