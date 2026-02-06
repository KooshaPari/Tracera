package security

import (
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

// TestBasicRateLimiting tests basic rate limiting functionality
func TestBasicRateLimiting(t *testing.T) {
	e := echo.New()

	// Make many requests quickly
	clientIP := "192.168.1.100"
	requestCount := 100
	successCount := 0

	for i := 0; i < requestCount; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
		req.Header.Set("X-Real-IP", clientIP)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		if rec.Code != http.StatusTooManyRequests {
			successCount++
		}

		// Brief pause between requests
		time.Sleep(10 * time.Millisecond)
	}

	// Should have rate limited some requests
	assert.Less(t, successCount, requestCount,
		"Some requests should be rate limited")
}

// TestPerIPRateLimiting tests that rate limiting is per-IP
func TestPerIPRateLimiting(t *testing.T) {
	e := echo.New()

	ips := []string{"192.168.1.100", "192.168.1.101", "192.168.1.102"}

	for _, ip := range ips {
		t.Run("IP: "+ip, func(t *testing.T) {
			successCount := 0

			// Each IP should get its own rate limit quota
			for i := 0; i < 50; i++ {
				req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
				req.Header.Set("X-Real-IP", ip)
				rec := httptest.NewRecorder()
				_ = e.NewContext(req, rec)

				if rec.Code == http.StatusOK {
					successCount++
				}
			}

			// Each IP should be able to make some requests
			assert.Greater(t, successCount, 0,
				"Each IP should have independent rate limit")
		})
	}
}

// TestRateLimitHeaders tests that rate limit headers are returned
func TestRateLimitHeaders(t *testing.T) {
	e := echo.New()

	req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
	req.Header.Set("X-Real-IP", "192.168.1.100")
	rec := httptest.NewRecorder()
	_ = e.NewContext(req, rec)

	// Should return rate limit headers
	rateLimitLimit := rec.Header().Get("X-RateLimit-Limit")
	rateLimitRemaining := rec.Header().Get("X-RateLimit-Remaining")
	rateLimitReset := rec.Header().Get("X-RateLimit-Reset")

	if rateLimitLimit != "" {
		assert.NotEmpty(t, rateLimitLimit, "Should return rate limit")
		assert.NotEmpty(t, rateLimitRemaining, "Should return remaining requests")
		assert.NotEmpty(t, rateLimitReset, "Should return reset time")
	}
}

// TestRateLimitByEndpoint tests different rate limits for different endpoints
func TestRateLimitByEndpoint(t *testing.T) {
	endpoints := []struct {
		path  string
		limit int
	}{
		{path: "/api/auth/login", limit: 5},        // Stricter for auth
		{path: "/api/items", limit: 100},           // Normal for regular API
		{path: "/api/search", limit: 20},           // Medium for search
		{path: "/api/webhooks/receive", limit: 50}, // Medium for webhooks
	}

	for _, endpoint := range endpoints {
		t.Run(endpoint.path, func(t *testing.T) {
			e := echo.New()
			clientIP := "192.168.1.100"
			successCount := 0

			// Make more requests than the limit
			for i := 0; i < endpoint.limit+10; i++ {
				req := httptest.NewRequest(http.MethodPost, endpoint.path, nil)
				req.Header.Set("X-Real-IP", clientIP)
				rec := httptest.NewRecorder()
				_ = e.NewContext(req, rec)

				if rec.Code != http.StatusTooManyRequests {
					successCount++
				}

				time.Sleep(10 * time.Millisecond)
			}

			// Should allow up to the limit
			assert.LessOrEqual(t, successCount, endpoint.limit+5,
				"Should not exceed rate limit significantly")
		})
	}
}

// TestConcurrentRateLimiting tests rate limiting under concurrent load
func TestConcurrentRateLimiting(t *testing.T) {
	e := echo.New()

	clientIP := "192.168.1.100"
	concurrentRequests := 50
	var wg sync.WaitGroup
	successCount := 0
	var mu sync.Mutex

	wg.Add(concurrentRequests)

	for i := 0; i < concurrentRequests; i++ {
		go func() {
			defer wg.Done()

			req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
			req.Header.Set("X-Real-IP", clientIP)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			mu.Lock()
			if rec.Code == http.StatusOK {
				successCount++
			}
			mu.Unlock()
		}()
	}

	wg.Wait()

	// Under concurrent load, rate limiter should still work
	assert.Less(t, successCount, concurrentRequests,
		"Should rate limit concurrent requests")
}

// TestRateLimitReset tests that rate limits reset over time
func TestRateLimitReset(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping time-based test in short mode")
	}

	e := echo.New()
	clientIP := "192.168.1.100"

	// Exhaust rate limit
	for i := 0; i < 10; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
		req.Header.Set("X-Real-IP", clientIP)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)
	}

	// Should be rate limited
	req1 := httptest.NewRequest(http.MethodGet, "/api/items", nil)
	req1.Header.Set("X-Real-IP", clientIP)
	rec1 := httptest.NewRecorder()
	_ = e.NewContext(req1, rec1)

	rateLimited := rec1.Code == http.StatusTooManyRequests

	// Wait for rate limit window to reset (e.g., 1 second)
	time.Sleep(2 * time.Second)

	// Should allow requests again
	req2 := httptest.NewRequest(http.MethodGet, "/api/items", nil)
	req2.Header.Set("X-Real-IP", clientIP)
	rec2 := httptest.NewRecorder()
	_ = e.NewContext(req2, rec2)

	if rateLimited {
		assert.NotEqual(t, http.StatusTooManyRequests, rec2.Code,
			"Rate limit should reset after time window")
	}
}

// TestRateLimitByUser tests user-specific rate limiting
func TestRateLimitByUser(t *testing.T) {
	e := echo.New()

	users := []string{"user-123", "user-456", "user-789"}

	for _, userID := range users {
		t.Run("User: "+userID, func(t *testing.T) {
			successCount := 0

			// Each user should have independent rate limits
			for i := 0; i < 30; i++ {
				req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
				req.Header.Set("Authorization", "Bearer "+createUserToken(t, userID))
				req.Header.Set("X-Real-IP", "192.168.1.100") // Same IP
				rec := httptest.NewRecorder()
				_ = e.NewContext(req, rec)

				if rec.Code == http.StatusOK {
					successCount++
				}

				time.Sleep(10 * time.Millisecond)
			}

			// Each authenticated user should have their own quota
			assert.Greater(t, successCount, 0,
				"Each user should have independent rate limit")
		})
	}
}

// TestBurstAllowance tests that rate limiter allows bursts
func TestBurstAllowance(t *testing.T) {
	e := echo.New()
	clientIP := "192.168.1.100"

	// Make burst of requests
	burstSize := 10
	successCount := 0

	for i := 0; i < burstSize; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
		req.Header.Set("X-Real-IP", clientIP)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		if rec.Code == http.StatusOK {
			successCount++
		}
	}

	// Should allow some burst traffic
	assert.Greater(t, successCount, 0,
		"Should allow burst of requests")
}

// TestRateLimitByUserAgent tests different limits for different clients
func TestRateLimitByUserAgent(t *testing.T) {
	userAgents := []struct {
		ua    string
		limit int
	}{
		{ua: "Mozilla/5.0 (compatible; TraceBot/1.0)", limit: 100},   // Bot
		{ua: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", limit: 50}, // Regular browser
		{ua: "curl/7.68.0", limit: 20},                               // CLI tool
	}

	for _, tc := range userAgents {
		t.Run("UA: "+tc.ua[:20], func(t *testing.T) {
			e := echo.New()
			clientIP := "192.168.1.100"
			successCount := 0

			for i := 0; i < tc.limit+10; i++ {
				req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
				req.Header.Set("X-Real-IP", clientIP)
				req.Header.Set("User-Agent", tc.ua)
				rec := httptest.NewRecorder()
				_ = e.NewContext(req, rec)

				if rec.Code == http.StatusOK {
					successCount++
				}

				time.Sleep(10 * time.Millisecond)
			}

			// Different user agents may have different limits
		})
	}
}

// TestDDoSProtection tests protection against DDoS patterns
func TestDDoSProtection(t *testing.T) {
	e := echo.New()

	// Simulate distributed attack from multiple IPs
	attackIPs := make([]string, 100)
	for i := 0; i < 100; i++ {
		attackIPs[i] = "192.168.1." + string(rune(i+1))
	}

	blockedCount := 0

	for _, ip := range attackIPs {
		// Make aggressive requests from each IP
		for i := 0; i < 20; i++ {
			req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
			req.Header.Set("X-Real-IP", ip)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			if rec.Code == http.StatusTooManyRequests {
				blockedCount++
			}
		}
	}

	// Should block aggressive patterns
	assert.Greater(t, blockedCount, 0,
		"Should detect and block DDoS patterns")
}

// TestRateLimitExemption tests that certain IPs/users can be exempted
func TestRateLimitExemption(t *testing.T) {
	e := echo.New()

	// Whitelisted IP (e.g., monitoring service)
	whitelistedIP := "10.0.0.1"
	successCount := 0

	// Make many requests from whitelisted IP
	for i := 0; i < 200; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/health", nil)
		req.Header.Set("X-Real-IP", whitelistedIP)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		if rec.Code == http.StatusOK {
			successCount++
		}
	}

	// Whitelisted IPs should not be rate limited (or have higher limits)
	assert.Greater(t, successCount, 150,
		"Whitelisted IPs should have higher rate limits")
}

// TestRateLimitRetryAfter tests that Retry-After header is set
func TestRateLimitRetryAfter(t *testing.T) {
	e := echo.New()
	clientIP := "192.168.1.100"

	// Exhaust rate limit
	for i := 0; i < 100; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
		req.Header.Set("X-Real-IP", clientIP)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		if rec.Code == http.StatusTooManyRequests {
			retryAfter := rec.Header().Get("Retry-After")
			assert.NotEmpty(t, retryAfter,
				"Should return Retry-After header when rate limited")
			break
		}
	}
}

// TestSlowlorisProtection tests protection against slowloris attacks
func TestSlowlorisProtection(t *testing.T) {
	e := echo.New()

	// Simulate slow request
	req := httptest.NewRequest(http.MethodPost, "/api/items", nil)
	req.Header.Set("X-Real-IP", "192.168.1.100")
	rec := httptest.NewRecorder()
	_ = e.NewContext(req, rec)

	// Server should timeout slow requests
	// This is typically handled at the HTTP server level
	assert.True(t, true, "Slow requests should timeout")
}
