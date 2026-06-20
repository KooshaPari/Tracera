package middleware

import (
	"net/http"
	"net/http/httptest"
	"strconv"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func closeRedisClient(t testing.TB, client *redis.Client) {
	t.Helper()
	require.NoError(t, client.Close())
}

const (
	testIP1        = "192.168.1.1:1234"
	testIP2        = "192.168.1.2:1234"
	testHealthPath = "/health"
)

type rateLimiterCase struct {
	name string
	fn   func(t *testing.T)
}

func TestEnhancedRateLimiter_InMemory(t *testing.T) {
	runRateLimiterCases(t, []rateLimiterCase{
		{name: "allows requests within limit", fn: runInMemoryAllowsWithinLimit},
		{name: "blocks requests exceeding limit", fn: runInMemoryBlocksExceedingLimit},
		{name: "different IPs have separate limits", fn: runInMemorySeparateIPs},
	})
}

func TestEnhancedRateLimiter_Redis(t *testing.T) {
	// Start miniredis
	mr, err := miniredis.Run()
	require.NoError(t, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer closeRedisClient(t, redisClient)

	runRateLimiterCases(t, []rateLimiterCase{
		{name: "allows requests within limit with Redis", fn: func(t *testing.T) {
			runRedisAllowsWithinLimit(t, redisClient)
		}},
		{name: "blocks requests exceeding limit with Redis", fn: func(t *testing.T) {
			mr.FlushAll()
			runRedisBlocksExceedingLimit(t, redisClient)
		}},
	})
}

func TestEnhancedRateLimiter_EndpointSpecific(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 100,
		DefaultBurstSize:         10,
		EndpointLimits: []EndpointLimit{
			{
				Pattern:           "/api/v1/auth/*",
				RequestsPerMinute: 5,
				BurstSize:         2,
			},
			{
				Pattern:           "/api/v1/items/*",
				RequestsPerMinute: 50,
				BurstSize:         5,
			},
		},
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.POST("/api/v1/auth/login", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})
	e.GET("/api/v1/items/123", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})
	e.GET("/api/v1/other", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	runEndpointSpecificCases(t, e)
}

func runRateLimiterCases(t *testing.T, cases []rateLimiterCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func runInMemoryAllowsWithinLimit(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 60,
		DefaultBurstSize:         5,
		AddHeaders:               true,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	for i := 0; i < 5; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = testIP1
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code, "Request %d should succeed", i+1)
		assert.NotEmpty(t, rec.Header().Get("X-RateLimit-Limit"))
		assert.NotEmpty(t, rec.Header().Get("X-RateLimit-Remaining"))
	}
}

func runInMemoryBlocksExceedingLimit(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 60,
		DefaultBurstSize:         3,
		AddHeaders:               true,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	for i := 0; i < 3; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = testIP1
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	}

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	req.RemoteAddr = testIP1
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusTooManyRequests, rec.Code)
	assert.NotEmpty(t, rec.Header().Get("Retry-After"))
}

func runInMemorySeparateIPs(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 60,
		DefaultBurstSize:         2,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	for i := 0; i < 2; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = testIP1
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	}

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	req.RemoteAddr = testIP1
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)
	assert.Equal(t, http.StatusTooManyRequests, rec.Code)

	req = httptest.NewRequest(http.MethodGet, "/test", nil)
	req.RemoteAddr = testIP2
	rec = httptest.NewRecorder()
	e.ServeHTTP(rec, req)
	assert.Equal(t, http.StatusOK, rec.Code)
}

func runRedisAllowsWithinLimit(t *testing.T, redisClient *redis.Client) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		RedisClient:              redisClient,
		DefaultRequestsPerMinute: 60,
		DefaultBurstSize:         5,
		AddHeaders:               true,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	for i := 0; i < 5; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = testIP1
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code, "Request %d should succeed", i+1)
		assert.NotEmpty(t, rec.Header().Get("X-RateLimit-Limit"))
	}
}

func runRedisBlocksExceedingLimit(t *testing.T, redisClient *redis.Client) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		RedisClient:              redisClient,
		DefaultRequestsPerMinute: 60,
		DefaultBurstSize:         2,
		AddHeaders:               true,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	for i := 0; i < 2; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = testIP1
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	}

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	req.RemoteAddr = testIP1
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusTooManyRequests, rec.Code)
	assert.NotEmpty(t, rec.Header().Get("Retry-After"))
}

func runEndpointSpecificCases(t *testing.T, e *echo.Echo) {
	t.Run("auth endpoint has strict limit", func(t *testing.T) {
		for i := 0; i < 2; i++ {
			req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login", nil)
			req.RemoteAddr = testIP1
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)
			assert.Equal(t, http.StatusOK, rec.Code)
		}

		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login", nil)
		req.RemoteAddr = testIP1
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusTooManyRequests, rec.Code)
	})

	t.Run("items endpoint has moderate limit", func(t *testing.T) {
		for i := 0; i < 5; i++ {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/items/123", nil)
			req.RemoteAddr = testIP2
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)
			assert.Equal(t, http.StatusOK, rec.Code)
		}

		req := httptest.NewRequest(http.MethodGet, "/api/v1/items/123", nil)
		req.RemoteAddr = testIP2
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusTooManyRequests, rec.Code)
	})

	t.Run("other endpoints use default limit", func(t *testing.T) {
		for i := 0; i < 10; i++ {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/other", nil)
			req.RemoteAddr = "192.168.1.3:1234"
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)
			assert.Equal(t, http.StatusOK, rec.Code)
		}
	})
}

func TestEnhancedRateLimiter_CustomKeyExtractor(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 100,
		DefaultBurstSize:         5,
		EndpointLimits: []EndpointLimit{
			{
				Pattern:           "/api/v1/auth/*",
				RequestsPerMinute: 3,
				BurstSize:         2,
				KeyExtractor: func(c *echo.Context) string {
					// Always use IP for auth, never user ID
					return "ip:" + (*c).RealIP()
				},
			},
		},
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.POST("/api/v1/auth/login", func(c echo.Context) error {
		// Simulate authentication
		c.Set("user_id", "user123")
		return c.String(http.StatusOK, "OK")
	})

	// Even with user_id set, should use IP for auth endpoints
	for i := 0; i < 2; i++ {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login", nil)
		req.RemoteAddr = testIP1
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	}

	// Third request should be blocked
	req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login", nil)
	req.RemoteAddr = testIP1
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)
	assert.Equal(t, http.StatusTooManyRequests, rec.Code)
}

func TestEnhancedRateLimiter_Headers(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 60,
		DefaultBurstSize:         5,
		AddHeaders:               true,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	req.RemoteAddr = testIP1
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	// Check rate limit headers
	limitHeader := rec.Header().Get("X-RateLimit-Limit")
	remainingHeader := rec.Header().Get("X-RateLimit-Remaining")
	resetHeader := rec.Header().Get("X-RateLimit-Reset")

	assert.NotEmpty(t, limitHeader, "X-RateLimit-Limit should be set")
	assert.NotEmpty(t, remainingHeader, "X-RateLimit-Remaining should be set")
	assert.NotEmpty(t, resetHeader, "X-RateLimit-Reset should be set")

	// Validate header values
	limit, err := strconv.Atoi(limitHeader)
	require.NoError(t, err)
	assert.Equal(t, 60, limit)

	remaining, err := strconv.Atoi(remainingHeader)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, remaining, 0)

	resetTime, err := strconv.ParseInt(resetHeader, 10, 64)
	require.NoError(t, err)
	assert.Greater(t, resetTime, time.Now().Unix())
}

func TestEnhancedRateLimiter_Skipper(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 1, // Very strict
		DefaultBurstSize:         1,
		Skipper: func(c echo.Context) bool {
			return c.Request().URL.Path == testHealthPath
		},
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET(testHealthPath, func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})
	e.GET("/api/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	// Health endpoint should never be rate limited
	for i := 0; i < 10; i++ {
		req := httptest.NewRequest(http.MethodGet, testHealthPath, nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	}

	// Regular endpoint should be rate limited
	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)
	assert.Equal(t, http.StatusOK, rec.Code)

	req = httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec = httptest.NewRecorder()
	e.ServeHTTP(rec, req)
	assert.Equal(t, http.StatusTooManyRequests, rec.Code)
}

func TestCreateStandardRateLimiter(t *testing.T) {
	t.Run("creates limiter with default configuration", func(t *testing.T) {
		limiter := CreateStandardRateLimiter(nil)
		defer limiter.Stop()

		assert.NotNil(t, limiter)
		assert.Equal(t, 100, limiter.config.DefaultRequestsPerMinute)
		assert.Len(t, limiter.config.EndpointLimits, 5) // auth, oauth, api, static, assets
	})

	t.Run("creates limiter with Redis", func(t *testing.T) {
		mr, err := miniredis.Run()
		require.NoError(t, err)
		defer mr.Close()

		redisClient := redis.NewClient(&redis.Options{
			Addr: mr.Addr(),
		})
		defer closeRedisClient(t, redisClient)

		limiter := CreateStandardRateLimiter(redisClient)
		defer limiter.Stop()

		assert.NotNil(t, limiter)
		assert.NotNil(t, limiter.config.RedisClient)
	})
}

func TestEnhancedRateLimiter_Cleanup(t *testing.T) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 60,
		DefaultBurstSize:         5,
	})

	// Add some limiters
	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "OK")
	})

	for i := 0; i < 5; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = "192.168.1." + strconv.Itoa(i) + ":1234"
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
	}

	// Should have 5 limiters
	limiter.mu.RLock()
	count := len(limiter.inMemoryLimiters)
	limiter.mu.RUnlock()
	assert.Equal(t, 5, count)

	// Manually set old access times
	limiter.mu.Lock()
	for key, state := range limiter.inMemoryLimiters {
		state.lastAccessed = time.Now().Add(-20 * time.Minute)
		limiter.inMemoryLimiters[key] = state
	}
	limiter.mu.Unlock()

	// Run cleanup
	limiter.cleanup()

	// Should have 0 limiters after cleanup
	limiter.mu.RLock()
	count = len(limiter.inMemoryLimiters)
	limiter.mu.RUnlock()
	assert.Equal(t, 0, count)

	limiter.Stop()
}

func BenchmarkRateLimiter_InMemory(b *testing.B) {
	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		DefaultRequestsPerMinute: 10000,
		DefaultBurstSize:         1000,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.NoContent(http.StatusOK)
	})

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		for pb.Next() {
			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			req.RemoteAddr = "192.168.1." + strconv.Itoa(i%256) + ":1234"
			rec := httptest.NewRecorder()
			e.ServeHTTP(rec, req)
			i++
		}
	})
}

func BenchmarkRateLimiter_Redis(b *testing.B) {
	mr, err := miniredis.Run()
	require.NoError(b, err)
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer closeRedisClient(b, redisClient)

	limiter := NewEnhancedRateLimiter(EnhancedRateLimitConfig{
		RedisClient:              redisClient,
		DefaultRequestsPerMinute: 10000,
		DefaultBurstSize:         1000,
	})
	defer limiter.Stop()

	e := echo.New()
	e.Use(limiter.Middleware())
	e.GET("/test", func(c echo.Context) error {
		return c.NoContent(http.StatusOK)
	})

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.RemoteAddr = "192.168.1." + strconv.Itoa(i%256) + ":1234"
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
	}
}
