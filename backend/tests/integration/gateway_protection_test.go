package integration

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/middleware"
	"github.com/kooshapari/tracertm-backend/internal/ratelimit"
)

// TestGatewayProtection_RateLimiting tests the rate limiting functionality
func TestGatewayProtection_RateLimiting(t *testing.T) {
	// Setup mini Redis
	mr, err := miniredis.Run()
	require.NoError(t, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer redisClient.Close()

	// Create test server with rate limit middleware
	e := echo.New()
	rateLimiter := middleware.NewRateLimitMiddleware(middleware.RateLimitMiddlewareConfig{
		Redis:                   redisClient,
		AuthenticatedUserLimit:  5,
		AuthenticatedUserWindow: 1 * time.Minute,
		AnonymousIPLimit:        3,
		AnonymousIPWindow:       1 * time.Minute,
		AddHeaders:              true,
	})
	e.Use(rateLimiter.Middleware())

	// Test handler
	e.GET("/test", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
	})

	// Test anonymous rate limiting
	t.Run("AnonymousRateLimit", func(t *testing.T) {
		for i := 0; i < 5; i++ {
			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)

			if i < 3 {
				assert.Equal(t, http.StatusOK, rec.Code, fmt.Sprintf("Request %d should succeed", i+1))
				assert.NotEmpty(t, rec.Header().Get("X-RateLimit-Limit"))
			} else {
				assert.Equal(t, http.StatusTooManyRequests, rec.Code, fmt.Sprintf("Request %d should be rate limited", i+1))
				assert.NotEmpty(t, rec.Header().Get("Retry-After"))
			}
		}
	})

	// Test authenticated rate limiting
	t.Run("AuthenticatedRateLimit", func(t *testing.T) {
		userID := uuid.New().String()

		for i := 0; i < 7; i++ {
			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			rec := httptest.NewRecorder()

			// Create context with user ID
			c := e.NewContext(req, rec)
			c.Set("user_id", userID)

			// Execute middleware chain
			handler := rateLimiter.Middleware()(func(c echo.Context) error {
				return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
			})
			_ = handler(c)

			if i < 5 {
				assert.Equal(t, http.StatusOK, rec.Code, fmt.Sprintf("Request %d should succeed", i+1))
			} else {
				assert.Equal(t, http.StatusTooManyRequests, rec.Code, fmt.Sprintf("Request %d should be rate limited", i+1))
			}
		}
	})
}

// TestGatewayProtection_Throttling tests the adaptive throttling
func TestGatewayProtection_Throttling(t *testing.T) {
	mr, err := miniredis.Run()
	require.NoError(t, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer redisClient.Close()

	config := ratelimit.ThrottleConfig{
		Redis:         redisClient,
		BaseTimeout:   5 * time.Second,
		MaxConcurrent: 5,
	}

	throttler := ratelimit.NewAdaptiveThrottler(config)
	ctx := context.Background()

	t.Run("ConcurrentAcquisition", func(t *testing.T) {
		// Acquire all slots
		releases := make([]func(), 0)
		for i := 0; i < 5; i++ {
			_, release, err := throttler.Acquire(ctx, ratelimit.PriorityNormal)
			assert.NoError(t, err)
			releases = append(releases, release)
		}

		// Next acquisition should queue
		done := make(chan error, 1)
		go func() {
			_, release, err := throttler.Acquire(ctx, ratelimit.PriorityNormal)
			if err == nil && release != nil {
				release()
			}
			done <- err
		}()

		// Release one slot
		time.Sleep(100 * time.Millisecond)
		releases[0]()

		// Wait for queued request
		select {
		case err := <-done:
			assert.NoError(t, err, "Queued request should complete")
		case <-time.After(2 * time.Second):
			t.Fatal("Queued request timed out")
		}

		// Clean up
		for _, release := range releases[1:] {
			release()
		}
	})

	t.Run("PriorityOrdering", func(t *testing.T) {
		// Acquire all slots with normal priority
		releases := make([]func(), 0)
		for i := 0; i < 5; i++ {
			_, release, _ := throttler.Acquire(ctx, ratelimit.PriorityNormal)
			releases = append(releases, release)
		}

		// Queue both high and low priority requests
		results := make(chan string, 2)

		go func() {
			_, release, err := throttler.Acquire(ctx, ratelimit.PriorityLow)
			if err == nil && release != nil {
				results <- "low"
				release()
			}
		}()

		go func() {
			_, release, err := throttler.Acquire(ctx, ratelimit.PriorityHigh)
			if err == nil && release != nil {
				results <- "high"
				release()
			}
		}()

		time.Sleep(100 * time.Millisecond)

		// Release slots and check priority ordering
		releases[0]()
		time.Sleep(50 * time.Millisecond)
		releases[1]()

		// High priority should complete first
		first := <-results
		second := <-results
		assert.Equal(t, "high", first, "High priority request should complete first")
		assert.Equal(t, "low", second, "Low priority request should complete second")

		// Clean up
		for _, release := range releases[2:] {
			release()
		}
	})

	t.Run("Metrics", func(t *testing.T) {
		metrics := throttler.GetMetrics()
		assert.Contains(t, metrics, "total_requests")
		assert.Contains(t, metrics, "current_load")
		assert.Greater(t, metrics["total_requests"].(int64), int64(0))
	})
}

// TestGatewayProtection_Quota tests quota tracking
func TestGatewayProtection_Quota(t *testing.T) {
	mr, err := miniredis.Run()
	require.NoError(t, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer redisClient.Close()

	quotaMiddleware := middleware.NewQuotaMiddleware(middleware.QuotaConfig{
		Redis:               redisClient,
		DefaultDailyQuota:   5,
		DefaultMonthlyQuota: 10,
		OverageAction:       middleware.QuotaActionReject,
		AddHeaders:          true,
	})

	e := echo.New()
	e.Use(quotaMiddleware.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
	})

	userID := uuid.New().String()

	t.Run("QuotaEnforcement", func(t *testing.T) {
		for i := 0; i < 7; i++ {
			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			rec := httptest.NewRecorder()

			c := e.NewContext(req, rec)
			c.Set("user_id", userID)

			handler := quotaMiddleware.Middleware()(func(c echo.Context) error {
				return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
			})
			_ = handler(c)

			if i < 5 {
				// Within quota (with grace)
				assert.NotEqual(t, http.StatusPaymentRequired, rec.Code)
			} else {
				// Quota exceeded
				assert.Equal(t, http.StatusPaymentRequired, rec.Code)
			}
		}
	})

	t.Run("QuotaReset", func(t *testing.T) {
		// Reset quota
		err := quotaMiddleware.ResetQuota(context.Background(), userID, "", middleware.QuotaPeriodDaily)
		assert.NoError(t, err)

		// Should allow requests again
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		c.Set("user_id", userID)

		handler := quotaMiddleware.Middleware()(func(c echo.Context) error {
			return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
		})
		_ = handler(c)

		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

// TestGatewayProtection_FullStack tests all layers together
func TestGatewayProtection_FullStack(t *testing.T) {
	mr, err := miniredis.Run()
	require.NoError(t, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer redisClient.Close()

	e := echo.New()

	// Add all middleware layers
	rateLimiter := middleware.CreateStandardRateLimitMiddleware(redisClient)
	e.Use(rateLimiter.Middleware())

	quotaMiddleware := middleware.NewQuotaMiddleware(middleware.QuotaConfig{
		Redis:               redisClient,
		DefaultDailyQuota:   100,
		DefaultMonthlyQuota: 1000,
		AddHeaders:          true,
	})
	e.Use(quotaMiddleware.Middleware())

	e.GET("/api/v1/test", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
	})

	t.Run("IntegratedProtection", func(t *testing.T) {
		userID := uuid.New().String()

		// Make several requests
		for i := 0; i < 10; i++ {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/test", nil)
			rec := httptest.NewRecorder()

			c := e.NewContext(req, rec)
			c.Set("user_id", userID)

			e.ServeHTTP(rec, req)

			// All should succeed (within both rate limit and quota)
			assert.Equal(t, http.StatusOK, rec.Code)

			// Check headers
			assert.NotEmpty(t, rec.Header().Get("X-RateLimit-Limit"))
			assert.NotEmpty(t, rec.Header().Get("X-Quota-Daily-Limit"))
		}
	})
}

// BenchmarkGatewayProtection measures performance impact
func BenchmarkGatewayProtection(b *testing.B) {
	mr, _ := miniredis.Run()
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer redisClient.Close()

	e := echo.New()
	rateLimiter := middleware.CreateStandardRateLimitMiddleware(redisClient)
	e.Use(rateLimiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
	})

	req := httptest.NewRequest(http.MethodGet, "/test", nil)

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)
		}
	})
}
