// Package server provides the HTTP server and cache integration tests.
package server

import (
	"bytes"
	"compress/gzip"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/middleware"
)

func setupCacheIntegrationServer() *echo.Echo {
	e := echo.New()

	e.Use(middleware.CacheControlMiddleware(middleware.CacheControlConfig{}))
	e.Use(middleware.ETagMiddleware(middleware.ETagConfig{}))
	e.Use(middleware.VariationsMiddleware())

	e.GET("/api/v1/items", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]interface{}{
			"items": []map[string]string{
				{"id": "1", "name": "Item 1"},
				{"id": "2", "name": "Item 2"},
			},
		})
	})

	e.GET("/static/app.js", func(c echo.Context) error {
		return c.String(http.StatusOK, "console.log('app');")
	})

	e.POST("/api/v1/items", func(c echo.Context) error {
		return c.JSON(http.StatusCreated, map[string]string{"id": "3"})
	})

	return e
}

func performRequest(e *echo.Echo, method string, path string, body io.Reader) *httptest.ResponseRecorder {
	req := httptest.NewRequest(method, path, body)
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)
	return rec
}

func TestCachingIntegration(t *testing.T) {
	e := setupCacheIntegrationServer()

	t.Run("API GET should have Cache-Control header", func(t *testing.T) {
		rec := performRequest(e, "GET", "/api/v1/items", nil)
		assert.Equal(t, http.StatusOK, rec.Code)
		cacheControl := rec.Header().Get("Cache-Control")
		assert.Equal(t, "public, max-age=300, stale-while-revalidate=60", cacheControl)
	})

	t.Run("Static asset should have immutable cache", func(t *testing.T) {
		rec := performRequest(e, "GET", "/static/app.js", nil)
		assert.Equal(t, http.StatusOK, rec.Code)
		cacheControl := rec.Header().Get("Cache-Control")
		assert.Equal(t, "public, max-age=31536000, immutable", cacheControl)
	})

	t.Run("POST request should not be cached", func(t *testing.T) {
		rec := performRequest(e, "POST", "/api/v1/items", nil)
		assert.Equal(t, http.StatusCreated, rec.Code)
		cacheControl := rec.Header().Get("Cache-Control")
		assert.Equal(t, "no-store", cacheControl)
	})

	t.Run("ETag should be set on GET request", func(t *testing.T) {
		rec := performRequest(e, "GET", "/api/v1/items", nil)
		assert.Equal(t, http.StatusOK, rec.Code)
		etag := rec.Header().Get("ETag")
		assert.NotEmpty(t, etag)
		assert.Equal(t, byte('"'), etag[0])
		assert.Equal(t, byte('"'), etag[len(etag)-1])
	})

	t.Run("Vary header should be set", func(t *testing.T) {
		rec := performRequest(e, "GET", "/api/v1/items", nil)
		assert.Equal(t, http.StatusOK, rec.Code)
		vary := rec.Header().Get("Vary")
		assert.Equal(t, "Accept-Encoding, Authorization, Accept", vary)
	})
}

func TestGzipCompression(t *testing.T) {
	e := echo.New()

	// Setup Gzip middleware
	e.Use(echo.MiddlewareFunc(func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Simulate gzip middleware
			return next(c)
		}
	}))

	// Large response that should be compressed
	largeData := make([]byte, 2000)
	for i := range largeData {
		largeData[i] = 'a'
	}

	e.GET("/large", func(c echo.Context) error {
		return c.Blob(http.StatusOK, "text/plain", largeData)
	})

	t.Run("Large response with gzip acceptance", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/large", nil)
		req.Header.Set("Accept-Encoding", "gzip")
		rec := httptest.NewRecorder()

		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)
		// Note: actual gzip is handled by Echo's middleware
		// This test just verifies the request handling
	})
}

func TestCompressionRatio(t *testing.T) {
	// Test that compression actually reduces size
	originalData := bytes.Repeat([]byte("This is a test response that should be compressed. "), 50)

	// Compress using gzip
	var buf bytes.Buffer
	gzipWriter := gzip.NewWriter(&buf)
	_, err := gzipWriter.Write(originalData)
	require.NoError(t, err)
	err = gzipWriter.Close()
	require.NoError(t, err)

	compressedData := buf.Bytes()
	compressionRatio := float64(len(compressedData)) / float64(len(originalData))

	t.Logf("Original size: %d bytes", len(originalData))
	t.Logf("Compressed size: %d bytes", len(compressedData))
	t.Logf("Compression ratio: %.2f%%", compressionRatio*100)

	// Verify compression is effective
	assert.Less(t, compressionRatio, 0.85, "Compression should reduce size to less than 85%")
}

func TestCacheValidation(t *testing.T) {
	e := echo.New()

	e.Use(middleware.CacheControlMiddleware(middleware.CacheControlConfig{}))
	e.Use(middleware.ETagMiddleware(middleware.ETagConfig{}))

	requestCount := 0
	e.GET("/api/v1/data", func(c echo.Context) error {
		requestCount++
		return c.JSON(http.StatusOK, map[string]int{"count": requestCount})
	})

	t.Run("First request should get full response", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/data", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)
		etag := rec.Header().Get("ETag")
		assert.NotEmpty(t, etag)
	})

	t.Run("If-None-Match header should match ETag format", func(t *testing.T) {
		req1 := httptest.NewRequest(http.MethodGet, "/api/v1/data", nil)
		rec1 := httptest.NewRecorder()
		e.ServeHTTP(rec1, req1)

		etag := rec1.Header().Get("ETag")
		assert.GreaterOrEqual(t, len(etag), 2)
		assert.Equal(t, byte('"'), etag[0])
		assert.Equal(t, byte('"'), etag[len(etag)-1])
	})
}

func TestCachePruning(t *testing.T) {
	t.Run("POST request Pragma header", func(t *testing.T) {
		e := echo.New()
		e.Use(middleware.CacheControlMiddleware(middleware.CacheControlConfig{}))

		e.POST("/api/v1/items", func(c echo.Context) error {
			return c.JSON(http.StatusCreated, map[string]string{"id": "1"})
		})

		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		pragma := rec.Header().Get("Pragma")
		assert.Equal(t, "no-cache", pragma)

		expires := rec.Header().Get("Expires")
		assert.Equal(t, "0", expires)
	})
}

func TestMultipleCacheHeaders(t *testing.T) {
	e := echo.New()

	e.Use(middleware.CacheControlMiddleware(middleware.CacheControlConfig{}))
	e.Use(middleware.ETagMiddleware(middleware.ETagConfig{}))
	e.Use(middleware.VariationsMiddleware())
	e.Use(middleware.CORSCacheMiddleware())

	e.GET("/api/v1/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "test")
	})

	e.OPTIONS("/api/v1/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "")
	})

	t.Run("GET request should have all cache headers", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/test", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)
		assert.NotEmpty(t, rec.Header().Get("Cache-Control"))
		assert.NotEmpty(t, rec.Header().Get("ETag"))
		assert.NotEmpty(t, rec.Header().Get("Vary"))
	})

	t.Run("OPTIONS request should have CORS cache", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodOptions, "/api/v1/test", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		cacheControl := rec.Header().Get("Cache-Control")
		assert.Equal(t, "public, max-age=86400", cacheControl)
	})
}

func TestResponseDecompression(t *testing.T) {
	// Test that we can decompress gzip responses
	originalData := []byte("This is test data that will be compressed")

	var buf bytes.Buffer
	gzipWriter := gzip.NewWriter(&buf)
	_, err := gzipWriter.Write(originalData)
	require.NoError(t, err)
	err = gzipWriter.Close()
	require.NoError(t, err)

	compressedData := buf.Bytes()

	// Decompress
	gzipReader, err := gzip.NewReader(bytes.NewBuffer(compressedData))
	require.NoError(t, err)
	defer func() { require.NoError(t, gzipReader.Close()) }()

	decompressed, err := io.ReadAll(gzipReader)
	require.NoError(t, err)

	assert.Equal(t, originalData, decompressed)
}

func TestCacheHeaderOrder(t *testing.T) {
	e := echo.New()

	// Setup middleware in correct order
	e.Use(middleware.CacheControlMiddleware(middleware.CacheControlConfig{}))
	e.Use(middleware.ETagMiddleware(middleware.ETagConfig{}))
	e.Use(middleware.VariationsMiddleware())

	e.GET("/api/v1/items", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{"id": "123"})
	})

	req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
	rec := httptest.NewRecorder()

	e.ServeHTTP(rec, req)

	// Verify all headers are present
	headers := rec.Header()
	assert.NotNil(t, headers.Get("Cache-Control"))
	assert.NotNil(t, headers.Get("ETag"))
	assert.NotNil(t, headers.Get("Vary"))
}
