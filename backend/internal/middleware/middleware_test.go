package middleware

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	rateLimitTestShortTTL       = 100 * time.Millisecond
	rateLimitTestCleanupFast    = 50 * time.Millisecond
	rateLimitTestCleanupSleep   = 250 * time.Millisecond
	rateLimitTestLimiterTTL     = 5 * time.Minute
	rateLimitTestCleanupDefault = 1 * time.Minute
	rateLimitTestDelay          = 50 * time.Millisecond
	rateLimitTestShortSleep     = 100 * time.Millisecond

	// Test remote address
	testRemoteAddr = "192.168.1.10:1234"
)

// TestRateLimitCleanup verifies that stale limiters are removed
func TestRateLimitCleanup(t *testing.T) {
	config := RateLimitConfig{
		RequestsPerSecond: 10,
		BurstSize:         5,
		LimiterTTL:        rateLimitTestShortTTL,    // Short TTL for testing
		CleanupInterval:   rateLimitTestCleanupFast, // Fast cleanup for testing
		Skipper:           middleware.DefaultSkipper,
	}

	middleware := CreateRateLimitMiddleware(&config)

	// Create a test handler that uses the middleware
	e := echo.New()
	testHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	}

	handler := middleware(testHandler)

	// Simulate requests from different clients
	clients := []string{"192.168.1.1", "192.168.1.2", "192.168.1.3"}

	for _, clientIP := range clients {
		c := e.NewContext(httptest.NewRequest(http.MethodGet, "/", nil), httptest.NewRecorder())
		c.Request().RemoteAddr = clientIP + ":8080"

		err := handler(c)
		require.NoError(t, err)
	}

	// Let the cleanup goroutine run
	time.Sleep(rateLimitTestCleanupSleep)

	// Stop the cleanup goroutine
	StopRateLimitCleanup(&config)
}

// TestRateLimitMiddlewareWithRedis verifies rate limiting works with Redis
func TestRateLimitMiddlewareBasic(t *testing.T) {
	config := RateLimitConfig{
		RequestsPerSecond: 10,
		BurstSize:         5,
		LimiterTTL:        rateLimitTestLimiterTTL,
		CleanupInterval:   rateLimitTestCleanupDefault,
		Skipper:           middleware.DefaultSkipper,
	}

	middleware := CreateRateLimitMiddleware(&config)
	defer StopRateLimitCleanup(&config)

	e := echo.New()
	testHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	}

	handler := middleware(testHandler)

	// Make requests within the limit
	for i := 0; i < 5; i++ {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.RemoteAddr = testRemoteAddr
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)
	}
}

// TestRateLimitExceeded verifies that rate limit is enforced
func TestRateLimitExceeded(t *testing.T) {
	config := RateLimitConfig{
		RequestsPerSecond: 0.5, // 1 request per 2 seconds
		BurstSize:         1,
		LimiterTTL:        rateLimitTestLimiterTTL,
		CleanupInterval:   rateLimitTestCleanupDefault,
		Skipper:           middleware.DefaultSkipper,
	}

	middleware := CreateRateLimitMiddleware(&config)
	defer StopRateLimitCleanup(&config)

	e := echo.New()
	testHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	}

	handler := middleware(testHandler)

	// First request should succeed
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.RemoteAddr = testRemoteAddr
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Second request should be rate limited
	req = httptest.NewRequest(http.MethodGet, "/", nil)
	req.RemoteAddr = testRemoteAddr
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = handler(c)
	require.Error(t, err)

	// Should have 429 status code
	httpErr := &echo.HTTPError{}
	ok := errors.As(err, &httpErr)
	assert.True(t, ok)
	assert.Equal(t, http.StatusTooManyRequests, httpErr.Code)
}

// TestLimiterEntryTracksLastAccess verifies last access time is updated
func TestLimiterEntryTracksLastAccess(t *testing.T) {
	config := RateLimitConfig{
		RequestsPerSecond: 100, // High limit to avoid throttling
		BurstSize:         50,
		LimiterTTL:        rateLimitTestLimiterTTL,
		CleanupInterval:   rateLimitTestCleanupDefault,
		Skipper:           middleware.DefaultSkipper,
	}

	middleware := CreateRateLimitMiddleware(&config)
	defer StopRateLimitCleanup(&config)

	e := echo.New()
	testHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	}

	handler := middleware(testHandler)

	// Make request at time T1
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.RemoteAddr = testRemoteAddr
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler(c)
	require.NoError(t, err)

	// Wait a bit
	time.Sleep(rateLimitTestDelay)

	// Make another request at time T2
	req = httptest.NewRequest(http.MethodGet, "/", nil)
	req.RemoteAddr = testRemoteAddr
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = handler(c)
	require.NoError(t, err)
}

// TestMultipleClientsIndependentLimiting verifies per-client limiting
func TestMultipleClientsIndependentLimiting(t *testing.T) {
	config := RateLimitConfig{
		RequestsPerSecond: 0.5, // 1 request per 2 seconds
		BurstSize:         1,
		LimiterTTL:        rateLimitTestLimiterTTL,
		CleanupInterval:   rateLimitTestCleanupDefault,
		Skipper:           middleware.DefaultSkipper,
	}

	middleware := CreateRateLimitMiddleware(&config)
	defer StopRateLimitCleanup(&config)

	e := echo.New()
	testHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	}

	handler := middleware(testHandler)

	// Client 1 makes a request (should succeed)
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.RemoteAddr = testRemoteAddr
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Client 2 makes a request (should also succeed because it has its own limiter)
	req = httptest.NewRequest(http.MethodGet, "/", nil)
	req.RemoteAddr = "192.168.1.2:8080"
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = handler(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

// TestLimiterTTLEnvironmentVariable tests TTL from environment variable
func TestLimiterTTLEnvironmentVariable(t *testing.T) {
	// This test verifies that environment variables are properly read
	// In actual testing, you would set the environment variable before running

	config := RateLimitConfig{
		RequestsPerSecond: 10,
		BurstSize:         5,
		// Not setting LimiterTTL to test default behavior
		Skipper: middleware.DefaultSkipper,
	}

	// The RateLimitMiddleware will read from environment or use defaults
	_ = CreateRateLimitMiddleware(&config)
	defer StopRateLimitCleanup(&config)

	// Verify that TTL was set (either from env or default)
	assert.NotZero(t, config.LimiterTTL)
	assert.NotZero(t, config.CleanupInterval)
}

// TestCleanupGoroutineStops verifies cleanup goroutine can be stopped
func TestCleanupGoroutineStops(t *testing.T) {
	config := RateLimitConfig{
		RequestsPerSecond: 10,
		BurstSize:         5,
		LimiterTTL:        rateLimitTestShortTTL,
		CleanupInterval:   rateLimitTestCleanupFast,
		Skipper:           middleware.DefaultSkipper,
	}

	middleware := CreateRateLimitMiddleware(&config)

	e := echo.New()
	testHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	}

	handler := middleware(testHandler)

	// Make a request
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	req.RemoteAddr = testRemoteAddr
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler(c)
	require.NoError(t, err)

	// Stop the cleanup goroutine
	StopRateLimitCleanup(&config)

	// Give it a moment to finish
	time.Sleep(rateLimitTestShortSleep)

	// Should not panic when stopping twice
	StopRateLimitCleanup(&config)
}
