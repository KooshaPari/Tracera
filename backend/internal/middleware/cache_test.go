package middleware

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	cacheTestAPITTL      = 5 * time.Minute
	cacheTestStaticTTL   = 1 * time.Hour
	cacheTestMaxAgeShort = "public, max-age=60"
	cacheTestMaxAgeAPI   = "public, max-age=300, stale-while-revalidate=60"
	cacheTestMaxAgeHour  = "public, max-age=3600, stale-while-revalidate=60"
)

type cacheControlCase struct {
	name           string
	path           string
	method         string
	expectedHeader string
}

type etagCase struct {
	name            string
	method          string
	path            string
	ifNoneMatch     string
	handlerStatus   int
	expectETag      bool
	expectETagEmpty bool
}

func TestCacheControlMiddleware(t *testing.T) {
	runCacheControlCases(t, cacheControlTestCases())
}

func TestCacheControlMiddlewareNoStoreHeaders(t *testing.T) {
	e := echo.New()
	e.Use(CacheControlMiddleware(CacheControlConfig{}))

	e.POST("/api/v1/items", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.PUT("/api/v1/items", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.DELETE("/api/v1/items", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.PATCH("/api/v1/items", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })

	tests := []struct {
		name   string
		method string
	}{
		{"POST", "POST"},
		{"PUT", "PUT"},
		{"DELETE", "DELETE"},
		{"PATCH", "PATCH"},
	}

	for _, tt := range tests {
		t.Run("Mutation method "+tt.name+" should set no-cache headers", func(t *testing.T) {
			req := httptest.NewRequest(tt.method, "/api/v1/items", nil)
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)

			assert.Equal(t, "no-store", rec.Header().Get("Cache-Control"), "Cache-Control for %s", tt.method)
			assert.Equal(t, "no-cache", rec.Header().Get("Pragma"), "Pragma for %s", tt.method)
			assert.Equal(t, "0", rec.Header().Get("Expires"), "Expires for %s", tt.method)
		})
	}
}

func TestIsStaticAsset(t *testing.T) {
	tests := []struct {
		path     string
		expected bool
	}{
		{"/static/app.js", true},
		{"/assets/style.css", true},
		{"/images/logo.png", true},
		{"/fonts/roboto.woff2", true},
		{"/icons/check.svg", true},
		{"/api/v1/items", false},
		{"/health", false},
		{"/docs", false},
	}

	for _, tt := range tests {
		t.Run(tt.path, func(t *testing.T) {
			result := isStaticAsset(tt.path)
			assert.Equal(t, tt.expected, result, "isStaticAsset(%s) should return %v", tt.path, tt.expected)
		})
	}
}

func TestIsAPIEndpoint(t *testing.T) {
	tests := []struct {
		path     string
		expected bool
	}{
		{"/api/v1/items", true},
		{"/api/v2/projects", true},
		{"/api/v1/", true},
		{"/v1/items", false},
		{"/items", false},
		{"/static/app.js", false},
	}

	for _, tt := range tests {
		t.Run(tt.path, func(t *testing.T) {
			result := isAPIEndpoint(tt.path)
			assert.Equal(t, tt.expected, result, "isAPIEndpoint(%s) should return %v", tt.path, tt.expected)
		})
	}
}

func TestETagMiddleware(t *testing.T) {
	runETagMiddlewareCases(t, etagTestCases())
}

func cacheControlTestCases() []cacheControlCase {
	return []cacheControlCase{
		{
			name:           "Static JS file should have immutable cache",
			path:           "/dist/app.js",
			method:         "GET",
			expectedHeader: "public, max-age=31536000, immutable",
		},
		{
			name:           "Static CSS file should have immutable cache",
			path:           "/styles.css",
			method:         "GET",
			expectedHeader: "public, max-age=31536000, immutable",
		},
		{
			name:           "Static SVG should have immutable cache",
			path:           "/logo.svg",
			method:         "GET",
			expectedHeader: "public, max-age=31536000, immutable",
		},
		{
			name:           "API GET request should have 5 minute cache",
			path:           "/api/v1/items",
			method:         "GET",
			expectedHeader: cacheTestMaxAgeAPI,
		},
		{
			name:           "API POST request should not be cached",
			path:           "/api/v1/items",
			method:         "POST",
			expectedHeader: "no-store",
		},
		{
			name:           "API PUT request should not be cached",
			path:           "/api/v1/items/123",
			method:         "PUT",
			expectedHeader: "no-store",
		},
		{
			name:           "API DELETE request should not be cached",
			path:           "/api/v1/items/123",
			method:         "DELETE",
			expectedHeader: "no-store",
		},
		{
			name:           "Non-API, non-static path should have 1 minute cache",
			path:           "/docs",
			method:         "GET",
			expectedHeader: cacheTestMaxAgeShort,
		},
	}
}

func setupCacheControlTestServer() *echo.Echo {
	e := echo.New()
	e.Use(CacheControlMiddleware(CacheControlConfig{}))
	e.GET("/dist/app.js", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.GET("/styles.css", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.GET("/logo.svg", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.GET("/api/v1/items", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.POST("/api/v1/items", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.GET("/api/v1/items/123", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.PUT("/api/v1/items/123", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.DELETE("/api/v1/items/123", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	e.GET("/docs", func(c echo.Context) error { return c.String(http.StatusOK, "OK") })
	return e
}

func runCacheControlCases(t *testing.T, cases []cacheControlCase) {
	e := setupCacheControlTestServer()
	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(tt.method, tt.path, nil)
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)

			assert.Equal(t, tt.expectedHeader, rec.Header().Get("Cache-Control"), "Path: %s, Method: %s", tt.path, tt.method)
		})
	}
}

func etagTestCases() []etagCase {
	return []etagCase{
		{
			name:          "GET request should set ETag header",
			method:        http.MethodGet,
			path:          "/api/v1/items",
			handlerStatus: http.StatusOK,
			expectETag:    true,
		},
		{
			name:          "Non-GET request should not set ETag",
			method:        http.MethodPost,
			path:          "/api/v1/items",
			handlerStatus: http.StatusOK,
		},
		{
			name:          "If-None-Match header should be checked",
			method:        http.MethodGet,
			path:          "/api/v1/items",
			ifNoneMatch:   `"matching-etag"`,
			handlerStatus: http.StatusOK,
			expectETag:    true,
		},
		{
			name:          "WebSocket requests should be skipped",
			method:        http.MethodGet,
			path:          "/api/v1/ws",
			handlerStatus: http.StatusOK,
		},
		{
			name:            "Non-2xx responses should not get ETag",
			method:          http.MethodGet,
			path:            "/api/v1/nonexistent",
			handlerStatus:   http.StatusNotFound,
			expectETagEmpty: true,
		},
	}
}

func runETagMiddlewareCases(t *testing.T, cases []etagCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			e := echo.New()
			handler := func(c echo.Context) error {
				return c.String(tc.handlerStatus, "OK")
			}

			req := httptest.NewRequest(tc.method, tc.path, nil)
			if tc.ifNoneMatch != "" {
				req.Header.Set("If-None-Match", tc.ifNoneMatch)
			}
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			middleware := ETagMiddleware(ETagConfig{})
			err := middleware(handler)(c)
			require.NoError(t, err)

			if tc.expectETagEmpty {
				assert.Empty(t, rec.Header().Get("ETag"))
				return
			}
			if tc.expectETag {
				etag := rec.Header().Get("ETag")
				assert.NotEmpty(t, etag)
				assert.True(t, etag[0] == '"' && etag[len(etag)-1] == '"', "ETag should be quoted")
			}
		})
	}
}

func TestVariationsMiddleware(t *testing.T) {
	t.Run("Should set Vary header", func(t *testing.T) {
		e := echo.New()
		handler := func(c echo.Context) error {
			return c.String(http.StatusOK, "OK")
		}

		req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		middleware := VariationsMiddleware()
		err := middleware(handler)(c)

		require.NoError(t, err)
		vary := rec.Header().Get("Vary")
		assert.Equal(t, "Accept-Encoding, Authorization, Accept", vary)
	})
}

func TestCORSCacheMiddleware(t *testing.T) {
	t.Run("OPTIONS request should have 24-hour cache", func(t *testing.T) {
		e := echo.New()
		handler := func(c echo.Context) error {
			return c.String(http.StatusOK, "OK")
		}

		req := httptest.NewRequest(http.MethodOptions, "/api/v1/items", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		middleware := CORSCacheMiddleware()
		err := middleware(handler)(c)

		require.NoError(t, err)
		cacheControl := rec.Header().Get("Cache-Control")
		assert.Equal(t, "public, max-age=86400", cacheControl)
	})

	t.Run("Non-OPTIONS request should not be affected", func(t *testing.T) {
		e := echo.New()
		handler := func(c echo.Context) error {
			return c.String(http.StatusOK, "OK")
		}

		req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		middleware := CORSCacheMiddleware()
		err := middleware(handler)(c)

		require.NoError(t, err)
		// Should not have the CORS cache header
		cacheControl := rec.Header().Get("Cache-Control")
		assert.NotEqual(t, "public, max-age=86400", cacheControl)
	})
}

func TestGetCacheControlHeaderForEndpoint(t *testing.T) {
	tests := []struct {
		method   string
		duration time.Duration
		expected string
	}{
		{"GET", cacheTestAPITTL, cacheTestMaxAgeAPI},
		{"GET", cacheTestStaticTTL, cacheTestMaxAgeHour},
		{"POST", cacheTestAPITTL, "no-store"},
		{"PUT", cacheTestAPITTL, "no-store"},
		{"DELETE", cacheTestAPITTL, "no-store"},
	}

	for _, tt := range tests {
		t.Run(fmt.Sprintf("%s with %v", tt.method, tt.duration), func(t *testing.T) {
			result := GetCacheControlHeaderForEndpoint(tt.method, tt.duration)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestGetCacheControlHeaderForStaticAsset(t *testing.T) {
	header := GetCacheControlHeaderForStaticAsset()
	assert.Equal(t, "public, max-age=31536000, immutable", header)
}

func TestETagGeneration(t *testing.T) {
	t.Run("Should generate consistent ETags", func(t *testing.T) {
		etag1 := generateETag("test-content")
		etag2 := generateETag("test-content")
		assert.Equal(t, etag1, etag2)
	})

	t.Run("Should generate different ETags for different content", func(t *testing.T) {
		etag1 := generateETag("content-1")
		etag2 := generateETag("content-2")
		assert.NotEqual(t, etag1, etag2)
	})

	t.Run("Should return 16 character hash", func(t *testing.T) {
		etag := generateETag("test")
		assert.Len(t, etag, 16)
	})
}

func TestIsStreamingPath(t *testing.T) {
	tests := []struct {
		path     string
		expected bool
	}{
		{"/api/v1/ws", true},
		{"/api/v1/stream", true},
		{"/storage/download", true},
		{"/api/v1/items", false},
		{"/api/v1/projects", false},
	}

	for _, tt := range tests {
		t.Run(tt.path, func(t *testing.T) {
			result := isStreamingPath(tt.path)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCacheControlMiddlewareIntegration(t *testing.T) {
	e := echo.New()

	// Add middleware
	e.Use(CacheControlMiddleware(CacheControlConfig{}))
	e.Use(ETagMiddleware(ETagConfig{}))
	e.Use(VariationsMiddleware())
	e.Use(CORSCacheMiddleware())

	e.GET("/api/v1/items", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{"id": "123"})
	})

	req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
	rec := httptest.NewRecorder()

	e.ServeHTTP(rec, req)

	// Check all cache-related headers
	assert.Equal(t, "public, max-age=300, stale-while-revalidate=60", rec.Header().Get("Cache-Control"))
	assert.NotEmpty(t, rec.Header().Get("ETag"))
	assert.Equal(t, "Accept-Encoding, Authorization, Accept", rec.Header().Get("Vary"))
}

func TestCompressionMetrics(t *testing.T) {
	// Reset metrics for testing
	metrics := GetCompressionMetrics()

	t.Run("Record compression should update metrics", func(t *testing.T) {
		metrics.recordCompression(1000, 300)

		stats := metrics.GetCompressionStats()
		typed432, ok := stats["total_requests"].(int64)
		require.True(t, ok)
		assert.Positive(t, typed432)
		typed433, ok := stats["uncompressed_bytes"].(int64)
		require.True(t, ok)
		assert.Positive(t, typed433)
		typed434, ok := stats["compressed_bytes"].(int64)
		require.True(t, ok)
		assert.Positive(t, typed434)
	})

	t.Run("Compression ratio should be calculated correctly", func(t *testing.T) {
		ratio := metrics.GetCompressionRatio()
		assert.GreaterOrEqual(t, ratio, 0.0)
		assert.LessOrEqual(t, ratio, 1.0)
	})

	t.Run("Record ETag hit should update metrics", func(t *testing.T) {
		metrics.recordETagHit()

		stats := metrics.GetCompressionStats()
		typed447, ok := stats["etag_hits"].(int64)
		require.True(t, ok)
		assert.Positive(t, typed447)
		typed448, ok := stats["not_modified"].(int64)
		require.True(t, ok)
		assert.Positive(t, typed448)
	})
}

func TestShouldComputeETag(t *testing.T) {
	tests := []struct {
		contentType string
		expected    bool
	}{
		{"application/json", true},
		{"application/json; charset=utf-8", true},
		{"text/html", true},
		{"text/html; charset=utf-8", true},
		{"text/plain", true},
		{"application/xml", true},
		{"application/javascript", true},
		{"text/javascript", true},
		{"application/octet-stream", false},
		{"image/png", false},
		{"image/jpeg", false},
		{"", false},
	}

	for _, tt := range tests {
		t.Run(tt.contentType, func(t *testing.T) {
			result := shouldComputeETag(tt.contentType)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestMatchesETag(t *testing.T) {
	etag := "abc123def456"

	tests := []struct {
		name        string
		ifNoneMatch string
		etag        string
		expected    bool
	}{
		{"Exact match", `"abc123def456"`, etag, true},
		{"Match without quotes in header", "abc123def456", etag, true},
		{"Multiple ETags with match", `"etag1", "abc123def456", "etag3"`, etag, true},
		{"Wildcard should match", "*", etag, true},
		{"No match", `"other123456"`, etag, false},
		{"Multiple ETags with no match", `"etag1", "etag2", "etag3"`, etag, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := matchesETag(tt.ifNoneMatch, tt.etag)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestETagFromBody(t *testing.T) {
	t.Run("Same body should generate same ETag", func(t *testing.T) {
		body := []byte(`{"id": "123", "name": "test"}`)
		etag1 := generateETagFromBody(body)
		etag2 := generateETagFromBody(body)
		assert.Equal(t, etag1, etag2)
	})

	t.Run("Different bodies should generate different ETags", func(t *testing.T) {
		body1 := []byte(`{"id": "123"}`)
		body2 := []byte(`{"id": "456"}`)
		etag1 := generateETagFromBody(body1)
		etag2 := generateETagFromBody(body2)
		assert.NotEqual(t, etag1, etag2)
	})

	t.Run("ETag should be 16 characters", func(t *testing.T) {
		body := []byte("test content")
		etag := generateETagFromBody(body)
		assert.Len(t, etag, 16)
	})

	t.Run("Empty body should still generate valid ETag", func(t *testing.T) {
		body := []byte("")
		etag := generateETagFromBody(body)
		assert.Len(t, etag, 16)
	})
}

func TestResponseWriterCapture(t *testing.T) {
	t.Run("Should capture response body", func(t *testing.T) {
		e := echo.New()
		handler := func(c echo.Context) error {
			return c.String(http.StatusOK, "test response body")
		}

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		originalWriter := c.Response().Writer
		wrappedWriter := &responseWriter{
			ResponseWriter: originalWriter,
			body:           make([]byte, 0),
		}
		c.Response().Writer = wrappedWriter

		err := handler(c)
		require.NoError(t, err)

		c.Response().Writer = originalWriter

		assert.NotEmpty(t, wrappedWriter.body)
		assert.Contains(t, string(wrappedWriter.body), "test response body")
	})
}

func TestETag304NotModified(t *testing.T) {
	t.Run("Matching ETag should return 304 Not Modified", func(t *testing.T) {
		e := echo.New()

		// Add middleware before routes
		e.Use(ETagMiddleware(ETagConfig{}))

		// First request to get the ETag
		handler := func(c echo.Context) error {
			c.Response().Header().Set("Content-Type", "application/json")
			return c.String(http.StatusOK, `{"id": "123"}`)
		}

		e.GET("/api/v1/items", handler)

		// First request to get ETag
		req1 := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
		rec1 := httptest.NewRecorder()
		e.ServeHTTP(rec1, req1)

		etag := rec1.Header().Get("ETag")
		assert.NotEmpty(t, etag)

		// Second request with If-None-Match
		req2 := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
		req2.Header.Set("If-None-Match", etag)
		rec2 := httptest.NewRecorder()
		e.ServeHTTP(rec2, req2)

		// Should return 304 Not Modified
		assert.Equal(t, http.StatusNotModified, rec2.Code)
	})
}
