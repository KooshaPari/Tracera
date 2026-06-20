package middleware

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// Cache durations for different types of responses
const (
	CacheShort  = 1 * time.Minute
	CacheMedium = 5 * time.Minute
	CacheLong   = 1 * time.Hour
	CacheDay    = 24 * time.Hour
	CacheYear   = 365 * 24 * time.Hour

	// HTTP method constants
	httpMethodGet = http.MethodGet

	cacheControlStaticAssets           = "public, max-age=31536000, immutable"
	cacheControlAPIGet                 = "public, max-age=300, stale-while-revalidate=60"
	cacheControlDefault                = "public, max-age=60"
	cacheControlNoStore                = "no-store"
	cacheControlNoCache                = "no-cache"
	cacheControlExpires                = "0"
	cacheControlCORSPreflight          = "public, max-age=86400"
	cacheControlStaleRevalidateSeconds = 60
	cacheCompressionPercentScale       = 100.0
)

// CompressionMetrics tracks compression statistics
type CompressionMetrics struct {
	mu               sync.RWMutex
	totalRequests    int64
	compressedSize   int64
	uncompressedSize int64
	etagHits         int64
	notModified      int64
}

// Singleton pattern for global compression metrics tracking
//
//nolint:gochecknoglobals // Singleton pattern: thread-safe initialization via sync.Once
var (
	compressionMetrics     *CompressionMetrics
	compressionMetricsOnce sync.Once
)

// CacheControlConfig holds the configuration for the cache control middleware
type CacheControlConfig struct {
	Skipper middleware.Skipper
}

// CacheControlMiddleware adds appropriate Cache-Control headers to responses
// based on the request path and HTTP method
func CacheControlMiddleware(config CacheControlConfig) echo.MiddlewareFunc {
	if config.Skipper == nil {
		config.Skipper = middleware.DefaultSkipper
	}

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if config.Skipper(c) {
				return next(c)
			}

			path := c.Path()
			method := c.Request().Method

			// Determine cache strategy based on path and method
			switch {
			case isStaticAsset(path):
				// Static assets - cache for 1 year (immutable)
				c.Response().Header().Set("Cache-Control", cacheControlStaticAssets)
			case isAPIEndpoint(path) && method == httpMethodGet:
				// GET requests - cache for 5 minutes
				c.Response().Header().Set("Cache-Control", cacheControlAPIGet)
			case isAPIEndpoint(path):
				// POST/PUT/DELETE/PATCH - no cache
				c.Response().Header().Set("Cache-Control", cacheControlNoStore)
				c.Response().Header().Set("Pragma", cacheControlNoCache)
				c.Response().Header().Set("Expires", cacheControlExpires)
			default:
				// Default: cache for 1 minute
				c.Response().Header().Set("Cache-Control", cacheControlDefault)
			}

			return next(c)
		}
	}
}

// isStaticAsset checks if the path is a static asset
func isStaticAsset(path string) bool {
	staticExts := []string{
		".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2",
		".ttf", ".eot", ".webp", ".ico", ".webmanifest",
	}

	for _, ext := range staticExts {
		if strings.HasSuffix(path, ext) {
			return true
		}
	}

	return false
}

// isAPIEndpoint checks if the path is an API endpoint
func isAPIEndpoint(path string) bool {
	return strings.HasPrefix(path, "/api/")
}

// ETagConfig holds configuration for ETag middleware
type ETagConfig struct {
	Skipper middleware.Skipper
}

// ResponseWriter wraps http.ResponseWriter to capture body for ETag computation
type responseWriter struct {
	http.ResponseWriter
	body       []byte
	statusCode int
	written    bool
}

// WriteHeader captures the status code but doesn't write it yet
func (w *responseWriter) WriteHeader(statusCode int) {
	if !w.written {
		w.statusCode = statusCode
		w.written = true
	}
}

// Write captures the response body for ETag generation
// Does not write to underlying writer yet - we need to check ETag first
func (w *responseWriter) Write(b []byte) (int, error) {
	if !w.written {
		w.WriteHeader(http.StatusOK)
	}
	w.body = append(w.body, b...)
	return len(b), nil
}

// ETagMiddleware adds ETag support for GET requests
// Returns 304 Not Modified if the ETag matches the If-None-Match header
func ETagMiddleware(config ETagConfig) echo.MiddlewareFunc {
	if config.Skipper == nil {
		config.Skipper = middleware.DefaultSkipper
	}

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if config.Skipper(c) {
				return next(c)
			}

			// Only for GET requests
			if c.Request().Method != httpMethodGet {
				return next(c)
			}

			// Skip WebSocket and streaming responses
			if isStreamingPath(c.Path()) {
				return next(c)
			}

			// Get If-None-Match header before processing
			ifNoneMatch := c.Request().Header.Get("If-None-Match")

			// Process request with wrapped writer
			return processRequestWithETag(c, next, ifNoneMatch)
		}
	}
}

// processRequestWithETag wraps the request processing to capture response for ETag
func processRequestWithETag(c echo.Context, next echo.HandlerFunc, ifNoneMatch string) error {
	// Wrap response writer to capture body
	originalWriter := c.Response().Writer
	wrappedWriter := &responseWriter{
		ResponseWriter: originalWriter,
		body:           make([]byte, 0),
		statusCode:     http.StatusOK,
		written:        false,
	}
	c.Response().Writer = wrappedWriter

	// Process the request
	if err := next(c); err != nil {
		// Restore original writer
		c.Response().Writer = originalWriter
		return err
	}

	// Restore original writer
	c.Response().Writer = originalWriter

	// Get the response status
	status := c.Response().Status

	// Handle response and ETag
	return handleETagResponse(c, originalWriter, wrappedWriter, status, ifNoneMatch)
}

// shouldHandleETagForStatus checks if ETag should be computed for this response status
func shouldHandleETagForStatus(status int) bool {
	return status >= 200 && status < 300
}

// handleETagResponse processes the ETag logic after request completion
func handleETagResponse(
	c echo.Context, originalWriter http.ResponseWriter, wrappedWriter *responseWriter, status int, ifNoneMatch string,
) error {
	if !shouldHandleETagForStatus(status) {
		return nil
	}

	contentType := c.Response().Header().Get("Content-Type")
	if !shouldComputeETag(contentType) {
		return nil
	}

	// Generate ETag from response body using SHA256
	etag := generateETagFromBody(wrappedWriter.body)
	GetCompressionMetrics().recordCompression(int64(len(wrappedWriter.body)), int64(len(wrappedWriter.body)))

	// Check If-None-Match header
	if ifNoneMatch != "" && matchesETag(ifNoneMatch, etag) {
		GetCompressionMetrics().recordETagHit()
		c.Response().Header().Set("ETag", fmt.Sprintf(`"%s"`, etag))
		c.Response().Header().Set("Cache-Control", cacheControlAPIGet)
		originalWriter.WriteHeader(http.StatusNotModified)
		return nil
	}

	// Set ETag header for future requests
	c.Response().Header().Set("ETag", fmt.Sprintf(`"%s"`, etag))

	// Write the status code and buffered response body to the actual response writer
	originalWriter.WriteHeader(wrappedWriter.statusCode)
	if len(wrappedWriter.body) > 0 {
		_, err := originalWriter.Write(wrappedWriter.body)
		return err
	}

	return nil
}

// shouldComputeETag determines if we should compute ETag for this content type
func shouldComputeETag(contentType string) bool {
	computableTypes := []string{
		"application/json",
		"text/html",
		"text/plain",
		"application/xml",
		"text/xml",
		"application/javascript",
		"text/javascript",
	}

	for _, ct := range computableTypes {
		if strings.Contains(contentType, ct) {
			return true
		}
	}

	return false
}

// matchesETag checks if the provided ETag matches any in the If-None-Match header
func matchesETag(ifNoneMatch, etag string) bool {
	if ifNoneMatch == "*" {
		return true
	}

	// Handle comma-separated ETags
	for _, tag := range strings.Split(ifNoneMatch, ",") {
		tag = strings.TrimSpace(tag)
		// Remove quotes if present
		tag = strings.Trim(tag, `"`)
		if tag == etag {
			return true
		}
	}

	return false
}

// isStreamingPath checks if the path is for streaming data
func isStreamingPath(path string) bool {
	streamingPaths := []string{"/ws", "/stream", "/download"}
	for _, sp := range streamingPaths {
		if strings.Contains(path, sp) {
			return true
		}
	}
	return false
}

// generateETag generates an ETag from a string using SHA256
func generateETag(s string) string {
	hash := sha256.Sum256([]byte(s))
	return hex.EncodeToString(hash[:])[:16] // Use first 16 chars of SHA256 hash
}

// generateETagFromBody generates an ETag from the response body using SHA256
func generateETagFromBody(body []byte) string {
	return generateETag(string(body))
}

// VariationsMiddleware adds Vary header to indicate which headers affect the response
func VariationsMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Add Vary header to indicate which request headers affect caching
			c.Response().Header().Set("Vary", "Accept-Encoding, Authorization, Accept")

			return next(c)
		}
	}
}

// CORSCacheMiddleware optimizes caching for CORS preflight requests
func CORSCacheMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Cache preflight requests for 24 hours
			if c.Request().Method == http.MethodOptions {
				c.Response().Header().Set("Cache-Control", cacheControlCORSPreflight)
			}

			return next(c)
		}
	}
}

// GetCacheControlHeaderForEndpoint returns appropriate Cache-Control header for an endpoint
// This helper can be used in individual handlers for fine-grained control
func GetCacheControlHeaderForEndpoint(method string, duration time.Duration) string {
	if method != httpMethodGet {
		return cacheControlNoStore
	}

	seconds := int(duration.Seconds())
	return "public, max-age=" + strconv.Itoa(seconds) + ", stale-while-revalidate=" + strconv.Itoa(cacheControlStaleRevalidateSeconds)
}

// GetCacheControlHeaderForStaticAsset returns Cache-Control header for static assets
func GetCacheControlHeaderForStaticAsset() string {
	return cacheControlStaticAssets
}

// CompressionConfig holds configuration for the compression middleware
type CompressionConfig struct {
	Level     int // 1-9, higher = better compression but slower
	MinLength int // Minimum response size to compress (bytes)
	Skipper   middleware.Skipper
}

// RecordCompression records compression statistics
func (m *CompressionMetrics) recordCompression(uncompressed, compressed int64) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.totalRequests++
	m.uncompressedSize += uncompressed
	m.compressedSize += compressed
}

// RecordETagHit records when an ETag results in 304 Not Modified
func (m *CompressionMetrics) recordETagHit() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.etagHits++
	m.notModified++
}

// GetCompressionRatio returns the current compression ratio (0-1, where 1 = no compression)
func (m *CompressionMetrics) GetCompressionRatio() float64 {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if m.uncompressedSize == 0 {
		return 0
	}

	return float64(m.compressedSize) / float64(m.uncompressedSize)
}

// GetCompressionStats returns current compression statistics
func (m *CompressionMetrics) GetCompressionStats() map[string]interface{} {
	m.mu.RLock()
	defer m.mu.RUnlock()

	ratio := 0.0
	if m.uncompressedSize > 0 {
		ratio = float64(m.compressedSize) / float64(m.uncompressedSize)
	}

	savings := int64(0)
	if m.uncompressedSize > 0 {
		savings = m.uncompressedSize - m.compressedSize
	}

	return map[string]interface{}{
		"total_requests":     m.totalRequests,
		"uncompressed_bytes": m.uncompressedSize,
		"compressed_bytes":   m.compressedSize,
		"saved_bytes":        savings,
		"compression_ratio":  fmt.Sprintf("%.1f%%", (1-ratio)*cacheCompressionPercentScale),
		"etag_hits":          m.etagHits,
		"not_modified":       m.notModified,
		"bandwidth_saved":    fmt.Sprintf("%.1f%%", (1-ratio)*cacheCompressionPercentScale),
	}
}

// GetCompressionMetrics returns the global compression metrics instance
func GetCompressionMetrics() *CompressionMetrics {
	compressionMetricsOnce.Do(func() {
		compressionMetrics = &CompressionMetrics{}
	})
	return compressionMetrics
}
