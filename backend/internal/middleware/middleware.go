package middleware

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/redis/go-redis/v9"
	"golang.org/x/time/rate"
)

// JWTClaims represents the claims in the JWT token
type JWTClaims struct {
	UserID    string `json:"user_id"`
	ProjectID string `json:"project_id"`
	Role      string `json:"role"`
	jwt.RegisteredClaims
}

// JWTConfig holds JWT middleware configuration
type JWTConfig struct {
	SecretKey []byte
	Skipper   middleware.Skipper
}

const (
	httpStatusBadRequest   = http.StatusBadRequest
	httpStatusServerError  = http.StatusInternalServerError
	corsMaxAgeSeconds      = 24 * 60 * 60
	recoveryStackSizeBytes = 4 << 10
)

// AuthAdapterConfig holds auth adapter middleware configuration
type AuthAdapterConfig struct {
	AuthProvider auth.Provider
	Skipper      middleware.Skipper
}

// JWTMiddleware creates a JWT authentication middleware
func JWTMiddleware(config JWTConfig) echo.MiddlewareFunc {
	if config.Skipper == nil {
		config.Skipper = middleware.DefaultSkipper
	}

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if config.Skipper(c) {
				return next(c)
			}

			// Extract token from Authorization header
			authHeader := c.Request().Header.Get("Authorization")
			if authHeader == "" {
				return echo.NewHTTPError(http.StatusUnauthorized, "missing authorization header")
			}

			// Check if it's a Bearer token
			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" {
				return echo.NewHTTPError(http.StatusUnauthorized, "invalid authorization format")
			}

			tokenString := parts[1]

			// Parse and validate token
			token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
				// Verify signing method
				if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
					return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
				}
				return config.SecretKey, nil
			})
			if err != nil {
				return echo.NewHTTPError(http.StatusUnauthorized, "invalid token")
			}

			if !token.Valid {
				return echo.NewHTTPError(http.StatusUnauthorized, "invalid token")
			}

			// Extract claims and set in context
			if claims, ok := token.Claims.(*JWTClaims); ok {
				c.Set("user_id", claims.UserID)
				c.Set("project_id", claims.ProjectID)
				c.Set("role", claims.Role)
				c.Set("claims", claims)
			}

			return next(c)
		}
	}
}

// AuthAdapterMiddleware creates an authentication middleware using the adapter pattern
// This allows swapping between AuthKit, Supabase Auth, or other providers
func AuthAdapterMiddleware(config AuthAdapterConfig) echo.MiddlewareFunc {
	if config.Skipper == nil {
		config.Skipper = middleware.DefaultSkipper
	}

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if config.Skipper(c) {
				return next(c)
			}

			// Extract token from Authorization header
			authHeader := c.Request().Header.Get("Authorization")
			var tokenString string

			if authHeader != "" {
				// Check if it's a Bearer token
				parts := strings.Split(authHeader, " ")
				if len(parts) != 2 || parts[0] != "Bearer" {
					return echo.NewHTTPError(http.StatusUnauthorized, "invalid authorization format")
				}
				tokenString = parts[1]
			} else {
				// Fallback to query parameter (for SSE/WebSocket which can't send custom headers)
				tokenString = c.QueryParam("token")
				if tokenString == "" {
					return echo.NewHTTPError(http.StatusUnauthorized, "missing authorization header or token query parameter")
				}
			}

			// Validate token using the auth provider adapter
			user, err := config.AuthProvider.ValidateToken(c.Request().Context(), tokenString)
			if err != nil {
				return echo.NewHTTPError(http.StatusUnauthorized, "invalid token")
			}

			// Set user information in context
			c.Set("user", user)
			c.Set("user_id", user.ID)
			c.Set("user_email", user.Email)
			c.Set("project_id", user.ProjectID)
			c.Set("role", user.Role)

			return next(c)
		}
	}
}

// limiterEntry tracks a rate limiter with its last access time
type limiterEntry struct {
	limiter      *rate.Limiter
	lastAccessed time.Time
}

// RateLimitConfig holds rate limiting configuration
type RateLimitConfig struct {
	RedisClient        *redis.Client
	RequestsPerSecond  float64
	BurstSize          int
	Skipper            middleware.Skipper
	LimiterTTL         time.Duration // Time after which unused limiters are cleaned up
	CleanupInterval    time.Duration // Frequency of cleanup runs
	stopCleanupChannel chan struct{} // For stopping the cleanup goroutine
	cleanupStopped     bool          // Flag to track if cleanup has been stopped
	cleanupMu          sync.Mutex    // Mutex to protect cleanupStopped flag
}

// CreateRateLimitMiddleware creates a rate limiting middleware using token bucket algorithm
// with TTL-based cleanup to prevent memory leaks
func CreateRateLimitMiddleware(config *RateLimitConfig) echo.MiddlewareFunc {
	if config.Skipper == nil {
		config.Skipper = middleware.DefaultSkipper
	}

	// Set default TTL and cleanup interval if not provided
	setRateLimiterDefaults(config)

	// Create a map to store per-client limiters with last access time
	var mu sync.RWMutex
	limiters := make(map[string]*limiterEntry)

	// Initialize the stop channel for cleanup goroutine
	config.stopCleanupChannel = make(chan struct{})

	// Start background cleanup goroutine
	go cleanupStaleLimiters(&mu, limiters, config.LimiterTTL, config.CleanupInterval, config.stopCleanupChannel)

	return createRateLimitHandler(config, &mu, limiters)
}

// setRateLimiterDefaults sets default values for rate limiter configuration
func setRateLimiterDefaults(config *RateLimitConfig) {
	if config.LimiterTTL == 0 {
		// Try to get from environment variable, default to 5 minutes
		ttlStr := os.Getenv("RATE_LIMITER_TTL_SECONDS")
		ttlSeconds := 300 // default 5 minutes
		if ttlStr != "" {
			if parsed, err := strconv.Atoi(ttlStr); err == nil {
				ttlSeconds = parsed
			}
		}
		config.LimiterTTL = time.Duration(ttlSeconds) * time.Second
	}

	if config.CleanupInterval == 0 {
		// Try to get from environment variable, default to 1 minute
		intervalStr := os.Getenv("RATE_LIMITER_CLEANUP_INTERVAL_SECONDS")
		intervalSeconds := 60 // default 1 minute
		if intervalStr != "" {
			if parsed, err := strconv.Atoi(intervalStr); err == nil {
				intervalSeconds = parsed
			}
		}
		config.CleanupInterval = time.Duration(intervalSeconds) * time.Second
	}
}

// createRateLimitHandler creates the rate limit handler function
func createRateLimitHandler(config *RateLimitConfig, mu *sync.RWMutex, limiters map[string]*limiterEntry) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if config.Skipper(c) {
				return next(c)
			}

			// Get client identifier (IP or user ID)
			clientID := getClientID(c)

			// Check rate limit
			allowed := checkRateLimit(c, config, mu, limiters, clientID)
			if !allowed {
				return echo.NewHTTPError(http.StatusTooManyRequests, "rate limit exceeded")
			}

			return next(c)
		}
	}
}

// getClientID extracts the client identifier from the request context
func getClientID(c echo.Context) string {
	clientID := c.RealIP()
	if userID := c.Get("user_id"); userID != nil {
		clientID = "user:" + fmt.Sprint(userID)
	}
	return clientID
}

// checkRateLimit performs rate limit check using Redis or in-memory limiter
func checkRateLimit(c echo.Context, config *RateLimitConfig, mu *sync.RWMutex, limiters map[string]*limiterEntry, clientID string) bool {
	// Check rate limit using Redis if available
	if config.RedisClient != nil {
		return checkRateLimitWithRedis(c, config, mu, limiters, clientID)
	}
	// Use in-memory limiter
	return checkRateLimitInMemory(mu, limiters, config, clientID)
}

// checkRateLimitWithRedis checks rate limit using Redis with fallback
func checkRateLimitWithRedis(c echo.Context, config *RateLimitConfig, mu *sync.RWMutex, limiters map[string]*limiterEntry, clientID string) bool {
	allowed, err := checkRedisRateLimit(c.Request().Context(), config.RedisClient, clientID, config.RequestsPerSecond, config.BurstSize)
	if err != nil {
		// Fallback to in-memory limiter on Redis error
		return checkRateLimitInMemoryWithEntry(mu, limiters, config, clientID)
	}
	return allowed
}

// checkRateLimitInMemory checks rate limit using in-memory limiter
func checkRateLimitInMemory(mu *sync.RWMutex, limiters map[string]*limiterEntry, config *RateLimitConfig, clientID string) bool {
	mu.Lock()
	entry, exists := limiters[clientID]
	if !exists {
		entry = &limiterEntry{
			limiter:      rate.NewLimiter(rate.Limit(config.RequestsPerSecond), config.BurstSize),
			lastAccessed: time.Now(),
		}
		limiters[clientID] = entry
	} else {
		entry.lastAccessed = time.Now()
	}
	limiter := entry.limiter
	mu.Unlock()

	return limiter.Allow()
}

// checkRateLimitInMemoryWithEntry gets or creates a limiter entry
func checkRateLimitInMemoryWithEntry(mu *sync.RWMutex, limiters map[string]*limiterEntry, config *RateLimitConfig, clientID string) bool {
	mu.Lock()
	entry, exists := limiters[clientID]
	if !exists {
		entry = &limiterEntry{
			limiter:      rate.NewLimiter(rate.Limit(config.RequestsPerSecond), config.BurstSize),
			lastAccessed: time.Now(),
		}
		limiters[clientID] = entry
	} else {
		entry.lastAccessed = time.Now()
	}
	limiter := entry.limiter
	mu.Unlock()

	return limiter.Allow()
}

// cleanupStaleLimiters is a background goroutine that periodically removes unused limiters
func cleanupStaleLimiters(mu *sync.RWMutex, limiters map[string]*limiterEntry, ttl, interval time.Duration, stopChan chan struct{}) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-stopChan:
			log.Println("Rate limiter cleanup goroutine stopped")
			return
		case <-ticker.C:
			mu.Lock()
			now := time.Now()
			removedCount := 0

			for clientID, entry := range limiters {
				if now.Sub(entry.lastAccessed) > ttl {
					delete(limiters, clientID)
					removedCount++
				}
			}

			limiterCount := len(limiters)
			mu.Unlock()

			if removedCount > 0 {
				log.Printf("Rate limiter cleanup: removed %d stale limiters, %d active limiters remaining", removedCount, limiterCount)
			}
		}
	}
}

// StopRateLimitCleanup stops the background cleanup goroutine for the rate limiter
func StopRateLimitCleanup(config *RateLimitConfig) {
	if config == nil || config.stopCleanupChannel == nil {
		return
	}

	config.cleanupMu.Lock()
	defer config.cleanupMu.Unlock()

	if !config.cleanupStopped {
		close(config.stopCleanupChannel)
		config.cleanupStopped = true
	}
}

// checkRedisRateLimit implements token bucket algorithm in Redis
func checkRedisRateLimit(ctx context.Context, client *redis.Client, key string, rps float64, burst int) (bool, error) {
	now := time.Now().Unix()
	rateLimitKey := "rate_limit:" + key

	// Lua script for atomic token bucket check
	script := `
		local key = KEYS[1]
		local now = tonumber(ARGV[1])
		local rate = tonumber(ARGV[2])
		local burst = tonumber(ARGV[3])

		local current = redis.call('HMGET', key, 'tokens', 'last_update')
		local tokens = tonumber(current[1])
		local last_update = tonumber(current[2])

		if tokens == nil then
			tokens = burst
			last_update = now
		end

		-- Calculate tokens to add based on time passed
		local delta = math.max(0, now - last_update)
		tokens = math.min(burst, tokens + (delta * rate))

		local allowed = 0
		if tokens >= 1 then
			tokens = tokens - 1
			allowed = 1
		end

		redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
		redis.call('EXPIRE', key, 3600)

		return allowed
	`

	result, err := client.Eval(ctx, script, []string{rateLimitKey}, now, rps, burst).Int()
	if err != nil {
		return false, err
	}

	return result == 1, nil
}

// ErrorHandlerMiddleware creates a centralized error handling middleware
func ErrorHandlerMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			err := next(c)
			if err != nil {
				// Log 401 missing/invalid auth at Info — expected when unauthenticated clients hit protected routes
				if he, ok := err.(*echo.HTTPError); ok && he.Code == http.StatusUnauthorized {
					msg := fmt.Sprint(he.Message)
					if msg == "missing authorization header" || msg == "invalid authorization format" || msg == "invalid token" {
						c.Logger().Infoj(map[string]interface{}{
							"message": msg,
							"path":    c.Request().URL.Path,
							"method":  c.Request().Method,
						})
						// Still return the 401 response below
					} else {
						c.Logger().Errorj(map[string]interface{}{
							"error":  err.Error(),
							"path":   c.Request().URL.Path,
							"method": c.Request().Method,
						})
					}
				} else {
					// Log all other errors at Error
					c.Logger().Errorj(map[string]interface{}{
						"error":  err.Error(),
						"path":   c.Request().URL.Path,
						"method": c.Request().Method,
					})
				}

				// Handle different error types
				if he, ok := err.(*echo.HTTPError); ok {
					return c.JSON(he.Code, map[string]interface{}{
						"error":     he.Message,
						"code":      he.Code,
						"path":      c.Request().URL.Path,
						"method":    c.Request().Method,
						"timestamp": time.Now().Unix(),
					})
				}

				// Default internal server error
				return c.JSON(http.StatusInternalServerError, map[string]interface{}{
					"error":     err.Error(),
					"code":      http.StatusInternalServerError,
					"path":      c.Request().URL.Path,
					"method":    c.Request().Method,
					"timestamp": time.Now().Unix(),
				})
			}
			return nil
		}
	}
}

// RequestLoggerMiddleware creates a detailed request logging middleware
func RequestLoggerMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			start := time.Now()

			// Process request
			err := next(c)

			// Log request details
			duration := time.Since(start)
			status := c.Response().Status

			logData := map[string]interface{}{
				"time":       start.Format(time.RFC3339),
				"method":     c.Request().Method,
				"path":       c.Request().URL.Path,
				"status":     status,
				"duration":   duration.Milliseconds(),
				"ip":         c.RealIP(),
				"user_agent": c.Request().UserAgent(),
			}

			if userID := c.Get("user_id"); userID != nil {
				logData["user_id"] = userID
			}

			switch {
			case status >= httpStatusServerError:
				c.Logger().Errorj(logData)
			case status >= httpStatusBadRequest:
				c.Logger().Warnj(logData)
			default:
				c.Logger().Infoj(logData)
			}

			return err
		}
	}
}

// CORSConfig returns a CORS middleware configuration with allowed origins from environment.
// External clients must use the gateway only; allow gateway + frontend origins (no wildcards).
func CORSConfig() middleware.CORSConfig {
	// Default: gateway (4000) + frontend dev (5173, 3000) and 127.0.0.1 variants
	allowedOrigins := []string{
		"http://localhost:4000", "http://127.0.0.1:4000",
		"http://localhost:5173", "http://127.0.0.1:5173",
		"http://localhost:3000", "http://127.0.0.1:3000",
	}

	if corsEnv := os.Getenv("CORS_ALLOWED_ORIGINS"); corsEnv != "" {
		// Split by comma and trim whitespace from each origin
		origins := strings.Split(corsEnv, ",")
		cleanOrigins := make([]string, 0, len(origins))
		for _, origin := range origins {
			if trimmed := strings.TrimSpace(origin); trimmed != "" && trimmed != "*" {
				cleanOrigins = append(cleanOrigins, trimmed)
			}
		}
		if len(cleanOrigins) > 0 {
			allowedOrigins = cleanOrigins
		}
	}

	// Validate that no wildcards are present (security check)
	for _, origin := range allowedOrigins {
		if origin == "*" || strings.Contains(origin, "*") {
			log.Printf("SECURITY WARNING: Wildcard origin detected in CORS_ALLOWED_ORIGINS. Wildcards are not allowed. Origin '%s' will be skipped.", origin)
		}
	}

	return middleware.CORSConfig{
		AllowOrigins: allowedOrigins,
		AllowMethods: []string{
			http.MethodGet,
			http.MethodPost,
			http.MethodPut,
			http.MethodPatch,
			http.MethodDelete,
			http.MethodOptions,
		},
		AllowHeaders: []string{
			echo.HeaderOrigin,
			echo.HeaderContentType,
			echo.HeaderAccept,
			echo.HeaderAuthorization,
			"X-Request-ID",
			CSRFTokenHeader, // X-CSRF-Token
			"X-Bulk-Operation",
		},
		ExposeHeaders: []string{
			"X-Request-ID",
			CSRFTokenHeader, // Expose X-CSRF-Token header
		},
		AllowCredentials: true,
		MaxAge:           corsMaxAgeSeconds, // 24 hours
	}
}

// RecoveryMiddleware creates a panic recovery middleware
func RecoveryMiddleware() echo.MiddlewareFunc {
	return middleware.RecoverWithConfig(middleware.RecoverConfig{
		StackSize: recoveryStackSizeBytes, // 4 KB
		LogErrorFunc: func(c echo.Context, err error, stack []byte) error {
			c.Logger().Errorf("PANIC RECOVERED: %v\nStack: %s", err, stack)
			return err
		},
	})
}

// HealthCheckSkipper skips middleware for health check endpoints
func HealthCheckSkipper(c echo.Context) bool {
	p := c.Request().URL.Path
	return p == "/health" || p == "/api/v1/health" || p == "/metrics"
}
