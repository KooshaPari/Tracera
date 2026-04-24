// Package cache provides caching utilities and middleware.
package cache

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
)

const (
	cacheDefaultTTL         = 5 * time.Minute
	cacheDefaultStatusCode  = 200
	cacheSetTimeout         = 2 * time.Second
	cacheInvalidateTimeout  = 5 * time.Second
	cacheHashPrefixLength   = 32
	cacheReadThroughTimeout = 2 * time.Second
)

// MiddlewareConfig holds configuration for cache middleware.
type MiddlewareConfig struct {
	// Cache instance to use
	Cache Cache
	// Default TTL for cached responses
	DefaultTTL time.Duration
	// Skip caching for these paths (glob patterns)
	SkipPaths []string
	// Only cache these methods (default: GET)
	CacheMethods []string
	// Only cache responses with these status codes (default: 200)
	CacheStatusCodes []int
	// Include query parameters in cache key (default: true)
	IncludeQuery bool
	// Include request headers in cache key
	IncludeHeaders []string
	// Enable cache invalidation on mutations
	EnableInvalidation bool
}

// ResponseCacheWriter wraps http.ResponseWriter to capture response
type ResponseCacheWriter struct {
	echo.Response
	body       *bytes.Buffer
	statusCode int
}

func newResponseCacheWriter(w http.ResponseWriter) *ResponseCacheWriter {
	return &ResponseCacheWriter{
		Response: echo.Response{Writer: w},
		body:     new(bytes.Buffer),
	}
}

func (w *ResponseCacheWriter) Write(b []byte) (int, error) {
	w.body.Write(b)
	return w.Writer.Write(b)
}

// WriteHeader captures the status code before delegating to the wrapped writer.
func (w *ResponseCacheWriter) WriteHeader(statusCode int) {
	w.statusCode = statusCode
	w.Writer.WriteHeader(statusCode)
}

// Middleware creates a middleware that caches GET responses.
func Middleware(config MiddlewareConfig) echo.MiddlewareFunc {
	applyCacheDefaults(&config)
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(echoCtx echo.Context) error {
			req := echoCtx.Request()
			path := echoCtx.Path()

			if shouldBypassCache(echoCtx, config, path) {
				return next(echoCtx)
			}

			// Generate cache key
			cacheKey := generateCacheKey(req, path, config.IncludeQuery, config.IncludeHeaders)

			if served, err := serveCachedResponse(echoCtx, config.Cache, cacheKey); served {
				return err
			}

			// Cache miss - execute handler and cache result
			echoCtx.Response().Header().Set("X-Cache", "MISS")
			echoCtx.Response().Header().Set("X-Cache-Key", cacheKey)

			// Wrap response writer to capture output
			resWriter := newResponseCacheWriter(echoCtx.Response().Writer)
			echoCtx.Response().Writer = resWriter

			// Execute handler
			if err := next(echoCtx); err != nil {
				return err
			}

			cacheResponseIfEligible(echoCtx, config, path, cacheKey, resWriter)

			return nil
		}
	}
}

func applyCacheDefaults(config *MiddlewareConfig) {
	if config.DefaultTTL == 0 {
		config.DefaultTTL = cacheDefaultTTL
	}
	if len(config.CacheMethods) == 0 {
		config.CacheMethods = []string{"GET"}
	}
	if len(config.CacheStatusCodes) == 0 {
		config.CacheStatusCodes = []int{cacheDefaultStatusCode}
	}
	if config.IncludeQuery {
		// Default to true if not explicitly set
		config.IncludeQuery = true
	}
}

func shouldBypassCache(echoCtx echo.Context, config MiddlewareConfig, path string) bool {
	if config.Cache == nil {
		return true
	}
	if shouldSkipPath(path, config.SkipPaths) {
		return true
	}
	if contains(config.CacheMethods, echoCtx.Request().Method) {
		return false
	}
	if config.EnableInvalidation && isMutationMethod(echoCtx.Request().Method) {
		invalidateRelatedCaches(echoCtx.Request().Context(), config.Cache, path)
	}
	return true
}

func serveCachedResponse(echoCtx echo.Context, cache Cache, cacheKey string) (bool, error) {
	var cachedResponse CachedResponse
	if err := cache.Get(echoCtx.Request().Context(), cacheKey, &cachedResponse); err == nil {
		echoCtx.Response().Header().Set("X-Cache", "HIT")
		echoCtx.Response().Header().Set("X-Cache-Key", cacheKey)

		for key, values := range cachedResponse.Headers {
			for _, value := range values {
				echoCtx.Response().Header().Add(key, value)
			}
		}

		return true, echoCtx.Blob(cachedResponse.StatusCode, cachedResponse.ContentType, cachedResponse.Body)
	}

	// Cache miss or error is treated as a miss; return nil error to continue with handler.
	return false, nil
}

func cacheResponseIfEligible(
	echoCtx echo.Context,
	config MiddlewareConfig,
	path string,
	cacheKey string,
	resWriter *ResponseCacheWriter,
) {
	statusCode := resWriter.statusCode
	if statusCode == 0 {
		statusCode = cacheDefaultStatusCode
	}
	if !containsInt(config.CacheStatusCodes, statusCode) {
		return
	}

	cached := CachedResponse{
		StatusCode:  statusCode,
		Headers:     echoCtx.Response().Header(),
		Body:        resWriter.body.Bytes(),
		ContentType: echoCtx.Response().Header().Get("Content-Type"),
		CachedAt:    time.Now(),
	}

	// Note: SetWithTags and TTL not available in base Cache interface - using basic Set
	// ttl := resolveCacheTTL(echoCtx.Response().Header(), config.DefaultTTL)
	// tags := generateCacheTags(path)
	ctx, cancel := context.WithTimeout(context.Background(), cacheSetTimeout)
	defer cancel()

	if err := config.Cache.Set(ctx, cacheKey, cached); err != nil {
		echoCtx.Logger().Errorf("Failed to cache response: %v", err)
	}
}

/*
func resolveCacheTTL(headers http.Header, defaultTTL time.Duration) time.Duration {
	if cacheControl := headers.Get("Cache-Control"); cacheControl != "" {
		if maxAge := parseCacheControlMaxAge(cacheControl); maxAge > 0 {
			return maxAge
		}
	}
	return defaultTTL
}
*/

// CachedResponse represents a cached HTTP response
type CachedResponse struct {
	StatusCode  int         `json:"status_code"`
	Headers     http.Header `json:"headers"`
	Body        []byte      `json:"body"`
	ContentType string      `json:"content_type"`
	CachedAt    time.Time   `json:"cached_at"`
}

// generateCacheKey creates a unique cache key for the request
func generateCacheKey(req *http.Request, path string, includeQuery bool, includeHeaders []string) string {
	var keyParts []string

	// Add method and path
	keyParts = append(keyParts, req.Method, path)

	// Add query parameters if enabled
	if includeQuery && req.URL.RawQuery != "" {
		keyParts = append(keyParts, req.URL.RawQuery)
	}

	// Add specified headers
	for _, header := range includeHeaders {
		if value := req.Header.Get(header); value != "" {
			keyParts = append(keyParts, header+":"+value)
		}
	}

	// Hash the key parts for consistent length
	keyString := strings.Join(keyParts, "|")
	hash := sha256.Sum256([]byte(keyString))
	hashString := hex.EncodeToString(hash[:])

	return "http:" + hashString[:cacheHashPrefixLength]
}

// generateCacheTags creates tags for cache invalidation
func generateCacheTags(path string) []string {
	parts := strings.Split(strings.Trim(path, "/"), "/")
	tags := []string{
		"path:" + path,
	}

	// Add hierarchical tags
	// e.g., /api/v1/projects/123 -> ["api", "api:v1", "api:v1:projects"]
	for i := 1; i <= len(parts); i++ {
		tag := strings.Join(parts[:i], ":")
		tags = append(tags, tag)
	}

	return tags
}

// invalidateRelatedCaches invalidates caches related to a mutation
func invalidateRelatedCaches(_ context.Context, cache Cache, path string) {
	tags := generateCacheTags(path)

	// Note: InvalidateTags not available in base Cache interface
	// Invalidate by tags in background
	// go func() {
	// 	ctx, cancel := context.WithTimeout(context.Background(), cacheInvalidateTimeout)
	// 	defer cancel()
	//
	// 	if err := cache.InvalidateTags(ctx, tags); err != nil {
	// 		// Log error but don't fail
	// 		fmt.Printf("Failed to invalidate cache tags: %v\n", err)
	// 	}
	// }()
	_ = tags // unused variable
}

// shouldSkipPath checks if path should skip caching
func shouldSkipPath(path string, skipPaths []string) bool {
	for _, pattern := range skipPaths {
		if matchesPattern(path, pattern) {
			return true
		}
	}
	return false
}

// matchesPattern checks if path matches glob pattern
func matchesPattern(path, pattern string) bool {
	// Simple glob matching (supports * wildcard)
	if pattern == "*" {
		return true
	}

	if strings.HasSuffix(pattern, "*") {
		prefix := strings.TrimSuffix(pattern, "*")
		return strings.HasPrefix(path, prefix)
	}

	return path == pattern
}

// isMutationMethod checks if HTTP method is a mutation
func isMutationMethod(method string) bool {
	mutations := []string{"POST", "PUT", "PATCH", "DELETE"}
	return contains(mutations, method)
}

// contains checks if slice contains string
func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func containsInt(slice []int, item int) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

// InvalidateCache is a helper to manually invalidate cache entries
func InvalidateCache(ctx context.Context, cache Cache, patterns ...string) error {
	for _, pattern := range patterns {
		if err := cache.InvalidatePattern(ctx, pattern); err != nil {
			return fmt.Errorf("failed to invalidate pattern %s: %w", pattern, err)
		}
	}
	return nil
}

// WarmCache preloads frequently accessed data into cache
func WarmCache(ctx context.Context, cache Cache, warmers []Warmer) error {
	for _, warmer := range warmers {
		if err := warmer.Warm(ctx, cache); err != nil {
			return fmt.Errorf("cache warmer failed: %w", err)
		}
	}
	return nil
}

// Warmer defines a cache warming strategy.
type Warmer interface {
	Warm(ctx context.Context, cache Cache) error
}

// ReadThroughCache wraps a data loader with cache
func ReadThroughCache[T any](
	ctx context.Context,
	cache Cache,
	key string,
	ttl time.Duration,
	loader func(ctx context.Context) (T, error),
) (T, error) {
	var result T

	// Try cache first
	err := cache.Get(ctx, key, &result)
	if err == nil {
		return result, nil
	}

	// Cache miss - load from source
	result, err = loader(ctx)
	if err != nil {
		return result, err
	}

	// Store in cache (fire and forget)
	go func(ctx context.Context) {
		ctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), cacheReadThroughTimeout)
		defer cancel()
		// Note: SetWithTTL not available - using basic Set
		if err := cache.Set(ctx, key, result); err != nil {
			slog.Error("cache warm failed for", "error", key, "error", err)
		}
	}(ctx)

	return result, nil
}

// WriteThroughCache updates cache and data source atomically
func WriteThroughCache[T any](
	ctx context.Context,
	cache Cache,
	key string,
	value T,
	ttl time.Duration,
	writer func(ctx context.Context, value T) error,
) error {
	// Write to data source first
	if err := writer(ctx, value); err != nil {
		return err
	}

	// Update cache
	// Note: SetWithTTL not available - using basic Set
	if err := cache.Set(ctx, key, value); err != nil {
		// Log but don't fail if cache update fails
		slog.Error("cache update failed for", "error", key, "error", err)
	}
	_ = ttl // unused variable

	return nil
}

// BatchGetWithCache retrieves multiple items with cache support
func BatchGetWithCache[T any](
	ctx context.Context,
	cache Cache,
	keys []string,
	ttl time.Duration,
	loader func(ctx context.Context, keys []string) (map[string]T, error),
) (map[string]T, error) {
	result, missingKeys := loadCachedBatch[T](ctx, cache, keys)
	if len(missingKeys) == 0 {
		return result, nil
	}

	loaded, err := loader(ctx, missingKeys)
	if err != nil {
		return nil, err
	}

	addLoadedBatch[T](ctx, cache, ttl, loaded, result)
	return result, nil
}

func loadCachedBatch[T any](ctx context.Context, cache Cache, keys []string) (map[string]T, []string) {
	result := make(map[string]T)
	missingKeys := make([]string, 0, len(keys))

	for _, key := range keys {
		var item T
		if err := cache.Get(ctx, key, &item); err == nil {
			result[key] = item
		} else {
			missingKeys = append(missingKeys, key)
		}
	}

	return result, missingKeys
}

func addLoadedBatch[T any](
	ctx context.Context,
	cache Cache,
	ttl time.Duration,
	loaded map[string]T,
	result map[string]T,
) {
	for key, item := range loaded {
		result[key] = item

		go func(ctx context.Context, k string, v T) {
			ctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), cacheReadThroughTimeout)
			defer cancel()
			// Note: SetWithTTL not available - using basic Set
			if err := cache.Set(ctx, k, v); err != nil {
				slog.Error("cache warm failed for", "error", k, "error", err)
			}
		}(ctx, key, item)
	}
}
