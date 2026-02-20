package middleware

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/ratelimit"
)

const (
	rateLimitPathHealth = "/health"
	rateLimitPathPython = "/health/python"
	rateLimitPathGo     = "/health/go"
	rateLimitPathStatic = "/static/*"
	rateLimitPathAssets = "/assets/*"
)

// RateLimitMiddlewareConfig configures the comprehensive rate limiting middleware
type RateLimitMiddlewareConfig struct {
	// Redis client for distributed rate limiting
	Redis *redis.Client

	// Per-user limits (authenticated users)
	AuthenticatedUserLimit  int // requests per minute
	AuthenticatedUserWindow time.Duration

	// Per-IP limits (anonymous users)
	AnonymousIPLimit  int // requests per minute
	AnonymousIPWindow time.Duration

	// Per-endpoint limits
	EndpointLimits map[string]EndpointRateLimit

	// Enable rate limit headers
	AddHeaders bool

	// Custom error handler
	ErrorHandler func(c echo.Context, err error) error
}

// EndpointRateLimit defines rate limits for a specific endpoint
type EndpointRateLimit struct {
	Pattern string
	Limit   int
	Window  time.Duration
}

const (
	defaultAuthUserLimit     = 100
	defaultAuthUserWindow    = 1 * time.Minute
	defaultAnonymousIPLimit  = 20
	defaultAnonymousIPWindow = 1 * time.Minute

	standardAuthEndpointLimit   = 5
	standardGraphAnalyzeLimit   = 10
	standardExecutionRunLimit   = 10
	standardSearchEndpointLimit = 30
)

// RateLimitMiddleware implements comprehensive rate limiting with sliding window
type RateLimitMiddleware struct {
	config RateLimitMiddlewareConfig

	// User limiter (per authenticated user)
	userLimiter *ratelimit.SlidingWindowLimiter

	// IP limiter (per IP address)
	ipLimiter *ratelimit.SlidingWindowLimiter

	// Endpoint-specific limiters
	endpointLimiters map[string]*ratelimit.SlidingWindowLimiter
}

// NewRateLimitMiddleware creates a new comprehensive rate limit middleware
func NewRateLimitMiddleware(config RateLimitMiddlewareConfig) *RateLimitMiddleware {
	// Set defaults
	if config.AuthenticatedUserLimit == 0 {
		config.AuthenticatedUserLimit = defaultAuthUserLimit // 100 req/min for authenticated users
	}
	if config.AuthenticatedUserWindow == 0 {
		config.AuthenticatedUserWindow = defaultAuthUserWindow
	}
	if config.AnonymousIPLimit == 0 {
		config.AnonymousIPLimit = defaultAnonymousIPLimit // 20 req/min for anonymous users
	}
	if config.AnonymousIPWindow == 0 {
		config.AnonymousIPWindow = defaultAnonymousIPWindow
	}
	if config.AddHeaders {
		config.AddHeaders = true
	}

	middleware := &RateLimitMiddleware{
		config: config,
		userLimiter: ratelimit.NewSlidingWindowLimiter(
			config.Redis,
			config.AuthenticatedUserWindow,
			int64(config.AuthenticatedUserLimit),
		),
		ipLimiter: ratelimit.NewSlidingWindowLimiter(
			config.Redis,
			config.AnonymousIPWindow,
			int64(config.AnonymousIPLimit),
		),
		endpointLimiters: make(map[string]*ratelimit.SlidingWindowLimiter),
	}

	// Initialize endpoint-specific limiters
	for pattern, limit := range config.EndpointLimits {
		middleware.endpointLimiters[pattern] = ratelimit.NewSlidingWindowLimiter(
			config.Redis,
			limit.Window,
			int64(limit.Limit),
		)
	}

	return middleware
}

// applyRateLimits checks endpoint, user, and IP rate limits for the request.
func (m *RateLimitMiddleware) applyRateLimits(c echo.Context) error {
	ctx := c.Request().Context()
	path := c.Request().URL.Path

	if limiter, pattern := m.findEndpointLimiter(path); limiter != nil {
		if err := m.checkLimit(ctx, c, limiter, "endpoint:"+pattern); err != nil {
			return m.handleError(c, err)
		}
	}

	if userID := m.getUserID(c); userID != "" {
		if err := m.checkLimit(ctx, c, m.userLimiter, "user:"+userID); err != nil {
			return m.handleError(c, err)
		}
	} else {
		if err := m.checkLimit(ctx, c, m.ipLimiter, "ip:"+c.RealIP()); err != nil {
			return m.handleError(c, err)
		}
	}
	return nil
}

// Middleware returns the Echo middleware function
func (m *RateLimitMiddleware) Middleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if shouldSkipRateLimit(c) {
				return next(c)
			}
			if err := m.applyRateLimits(c); err != nil {
				return err
			}
			return next(c)
		}
	}
}

// checkLimit checks a rate limit and adds appropriate headers
func (m *RateLimitMiddleware) checkLimit(ctx context.Context, c echo.Context, limiter *ratelimit.SlidingWindowLimiter, key string) error {
	allowed, remaining, resetTime, err := limiter.Allow(ctx, key)

	// Add rate limit headers if enabled
	if m.config.AddHeaders {
		c.Response().Header().Set("X-RateLimit-Limit", strconv.FormatInt(limiter.GetLimit(), 10))
		c.Response().Header().Set("X-RateLimit-Remaining", strconv.Itoa(remaining))
		c.Response().Header().Set("X-RateLimit-Reset", strconv.FormatInt(resetTime.Unix(), 10))
	}

	if err != nil {
		// Log error but fail open (allow request)
		c.Logger().Warnf("Rate limit check error: %v", err)
		return nil
	}

	if !allowed {
		// Add Retry-After header
		retryAfter := int(time.Until(resetTime).Seconds())
		if retryAfter < 0 {
			retryAfter = 60
		}
		c.Response().Header().Set("Retry-After", strconv.Itoa(retryAfter))

		return &RateLimitError{
			Message:    "Rate limit exceeded. Please try again later.",
			ResetTime:  resetTime,
			RetryAfter: retryAfter,
		}
	}

	return nil
}

// findEndpointLimiter finds the appropriate endpoint limiter for a path
func (m *RateLimitMiddleware) findEndpointLimiter(path string) (*ratelimit.SlidingWindowLimiter, string) {
	for pattern, limiter := range m.endpointLimiters {
		if matchPath(path, pattern) {
			return limiter, pattern
		}
	}
	return nil, ""
}

// getUserID extracts the user ID from the request context
func (m *RateLimitMiddleware) getUserID(c echo.Context) string {
	// Try to get user ID from context (set by auth middleware)
	if userID := c.Get("user_id"); userID != nil {
		return fmt.Sprint(userID)
	}

	// Try to get from API key (set by API key middleware)
	if apiKeyID := c.Get("api_key_id"); apiKeyID != nil {
		return "apikey:" + fmt.Sprint(apiKeyID)
	}

	return ""
}

// handleError handles rate limit errors
func (m *RateLimitMiddleware) handleError(c echo.Context, err error) error {
	if m.config.ErrorHandler != nil {
		return m.config.ErrorHandler(c, err)
	}

	rateLimitErr := &RateLimitError{}
	if errors.As(err, &rateLimitErr) {
		return c.JSON(http.StatusTooManyRequests, map[string]interface{}{
			"error":       "rate_limit_exceeded",
			"message":     rateLimitErr.Message,
			"reset_time":  rateLimitErr.ResetTime.Unix(),
			"retry_after": rateLimitErr.RetryAfter,
		})
	}

	return err
}

// shouldSkipRateLimit determines if rate limiting should be skipped
func shouldSkipRateLimit(c echo.Context) bool {
	path := c.Request().URL.Path

	// Skip health checks
	if path == rateLimitPathHealth || path == rateLimitPathPython || path == rateLimitPathGo {
		return true
	}

	// Skip static assets
	if matchPath(path, rateLimitPathStatic) || matchPath(path, rateLimitPathAssets) {
		return true
	}

	return false
}

// matchPath checks if a path matches a pattern (supports * wildcard)
func matchPath(path, pattern string) bool {
	if pattern == "*" || pattern == "/*" {
		return true
	}

	// Exact match
	if path == pattern {
		return true
	}

	// Wildcard suffix match
	if len(pattern) > 0 && pattern[len(pattern)-1] == '*' {
		prefix := pattern[:len(pattern)-1]
		return len(path) >= len(prefix) && path[:len(prefix)] == prefix
	}

	return false
}

// RateLimitError represents a rate limit exceeded error
type RateLimitError struct {
	Message    string
	ResetTime  time.Time
	RetryAfter int
}

func (e *RateLimitError) Error() string {
	return e.Message
}

// CreateStandardRateLimitMiddleware creates a middleware with standard configurations
func CreateStandardRateLimitMiddleware(redis *redis.Client) *RateLimitMiddleware {
	return NewRateLimitMiddleware(RateLimitMiddlewareConfig{
		Redis:                   redis,
		AuthenticatedUserLimit:  defaultAuthUserLimit,
		AuthenticatedUserWindow: defaultAuthUserWindow,
		AnonymousIPLimit:        defaultAnonymousIPLimit,
		AnonymousIPWindow:       defaultAnonymousIPWindow,
		AddHeaders:              true,
		ErrorHandler:            nil,
		EndpointLimits: map[string]EndpointRateLimit{
			// Auth endpoints - very strict
			"/api/v1/auth/*": {
				Pattern: "/api/v1/auth/*",
				Limit:   standardAuthEndpointLimit,
				Window:  defaultAuthUserWindow,
			},
			// Expensive operations
			"/api/v1/graph/analyze": {
				Pattern: "/api/v1/graph/analyze",
				Limit:   standardGraphAnalyzeLimit,
				Window:  defaultAuthUserWindow,
			},
			"/api/v1/executions/run": {
				Pattern: "/api/v1/executions/run",
				Limit:   standardExecutionRunLimit,
				Window:  defaultAuthUserWindow,
			},
			// Search endpoints
			"/api/v1/search/*": {
				Pattern: "/api/v1/search/*",
				Limit:   standardSearchEndpointLimit,
				Window:  defaultAuthUserWindow,
			},
		},
	})
}
