package middleware

import (
	"context"
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"golang.org/x/time/rate"
)

const nonceByteLength = 32

// generateNonce generates a cryptographically secure random nonce
func generateNonce() (string, error) {
	nonceBytes := make([]byte, nonceByteLength)
	if _, err := rand.Read(nonceBytes); err != nil {
		return "", fmt.Errorf("failed to generate nonce: %w", err)
	}
	return base64.StdEncoding.EncodeToString(nonceBytes), nil
}

// contextKeyNonce is the context key for storing the nonce
const contextKeyNonce = "csp_nonce"

// GetNonce retrieves the CSP nonce from the request context
func GetNonce(c echo.Context) string {
	nonce, ok := c.Get(contextKeyNonce).(string)
	if !ok {
		return ""
	}
	return nonce
}

// SecurityHeaders creates a middleware that sets security headers including nonce-based CSP
func SecurityHeaders() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Generate unique nonce for this request
			nonce, err := generateNonce()
			if err != nil {
				c.Logger().Errorf("failed to generate CSP nonce: %v", err)
				// Continue with empty nonce rather than failing the request
				nonce = ""
			}
			c.Set(contextKeyNonce, nonce)

			// Prevent MIME type sniffing
			c.Response().Header().Set("X-Content-Type-Options", "nosniff")

			// Prevent clickjacking
			c.Response().Header().Set("X-Frame-Options", "DENY")

			// Enable XSS protection
			c.Response().Header().Set("X-XSS-Protection", "1; mode=block")

			// Enforce HTTPS
			c.Response().Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

			// Content Security Policy with nonce-based script and style sources
			csp := fmt.Sprintf(
				"default-src 'self'; "+
					"script-src 'self' 'nonce-%s'; "+
					"style-src 'self' 'nonce-%s'; "+
					"img-src 'self' data: https:; "+
					"font-src 'self' data:; "+
					"connect-src 'self' wss: https:; "+
					"frame-ancestors 'none'",
				nonce, nonce)
			c.Response().Header().Set("Content-Security-Policy", csp)

			// Referrer Policy
			c.Response().Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")

			// Permissions Policy
			c.Response().Header().Set("Permissions-Policy",
				"geolocation=(), microphone=(), camera=()")

			return next(c)
		}
	}
}

// RateLimiter enforces per-IP request limits.
type RateLimiter struct {
	limiters map[string]*rate.Limiter
	rate     rate.Limit
	burst    int
}

// NewRateLimiter constructs a RateLimiter with the provided limits.
func NewRateLimiter(requestsPerSecond int, burst int) *RateLimiter {
	return &RateLimiter{
		limiters: make(map[string]*rate.Limiter),
		rate:     rate.Limit(requestsPerSecond),
		burst:    burst,
	}
}

func (rl *RateLimiter) getLimiter(ip string) *rate.Limiter {
	if limiter, exists := rl.limiters[ip]; exists {
		return limiter
	}

	limiter := rate.NewLimiter(rl.rate, rl.burst)
	rl.limiters[ip] = limiter
	return limiter
}

// Middleware returns an Echo middleware that enforces rate limits.
func (rl *RateLimiter) Middleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ip := c.RealIP()
			limiter := rl.getLimiter(ip)

			if !limiter.Allow() {
				return echo.NewHTTPError(http.StatusTooManyRequests,
					"Rate limit exceeded. Please try again later.")
			}

			return next(c)
		}
	}
}

// APIKeyAuth validates API keys from the X-API-Key header.
func APIKeyAuth(validKeys map[string]bool) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			apiKey := c.Request().Header.Get("X-API-Key")

			if apiKey == "" {
				return echo.NewHTTPError(http.StatusUnauthorized, "Missing API key")
			}

			if !validKeys[apiKey] {
				return echo.NewHTTPError(http.StatusUnauthorized, "Invalid API key")
			}

			return next(c)
		}
	}
}

// SanitizeInput sanitizes query parameters to reduce injection risk.
func SanitizeInput() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Sanitize query parameters
			for _, values := range c.QueryParams() {
				for i, value := range values {
					values[i] = sanitizeString(value)
				}
			}

			return next(c)
		}
	}
}

// Sanitize string input to prevent injection attacks
func sanitizeString(input string) string {
	// Remove null bytes
	input = strings.ReplaceAll(input, "\x00", "")

	// Trim whitespace
	input = strings.TrimSpace(input)

	// Remove potentially dangerous characters
	dangerous := []string{
		"<script>", "</script>",
		"javascript:",
		"onerror=",
		"onload=",
		"onclick=",
	}

	lower := strings.ToLower(input)
	for _, danger := range dangerous {
		if strings.Contains(lower, danger) {
			input = strings.ReplaceAll(input, danger, "")
		}
	}

	return input
}

// SecureCORS provides strict CORS validation with whitelisted origins only.
// This middleware:
// - Only allows explicitly whitelisted origins (NO wildcards)
// - Validates Origin header against allowedOrigins list
// - Rejects requests from non-whitelisted origins
// - Requires exact string matching (case-sensitive)
//
// Usage:
//
//	origins := []string{"https://example.com", "https://app.example.com"}
//	router.Use(SecureCORS(origins))
//
// Important: Pass origins from CORS_ALLOWED_ORIGINS environment variable.
// Never use wildcards (*) - they bypass all CORS protections.
// isOriginAllowed checks if the given origin is in the allowed list (exact match, no wildcards).
func isOriginAllowed(origin string, allowedOrigins []string) bool {
	for _, ao := range allowedOrigins {
		if ao == "*" || strings.Contains(ao, "*") {
			continue
		}
		if origin == ao {
			return true
		}
	}
	return false
}

// setCORSHeaders sets standard CORS response headers for an allowed origin.
func setCORSHeaders(c echo.Context, origin string) {
	h := c.Response().Header()
	h.Set("Access-Control-Allow-Origin", origin)
	h.Set("Access-Control-Allow-Credentials", "true")
	h.Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
	h.Set("Access-Control-Allow-Headers", "Accept, Authorization, Content-Type, X-CSRF-Token, X-API-Key, X-Request-ID")
	h.Set("Access-Control-Max-Age", "86400")
}

// SecureCORS configures secure CORS middleware with strict defaults.
func SecureCORS(allowedOrigins []string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			origin := c.Request().Header.Get("Origin")

			if isOriginAllowed(origin, allowedOrigins) {
				setCORSHeaders(c, origin)
			} else if origin != "" {
				c.Logger().Warnf("CORS: Rejected request from origin: %s", origin)
			}

			if c.Request().Method == http.MethodOptions {
				return c.NoContent(http.StatusNoContent)
			}

			return next(c)
		}
	}
}

// RequestSizeLimit limits request bodies to the given size.
func RequestSizeLimit(maxBytes int64) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			c.Request().Body = http.MaxBytesReader(c.Response(), c.Request().Body, maxBytes)
			return next(c)
		}
	}
}

// Timeout middleware
func Timeout(duration time.Duration) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()
			ctx, cancel := context.WithTimeout(ctx, duration)
			defer cancel()

			c.SetRequest(c.Request().WithContext(ctx))

			done := make(chan error, 1)
			go func() {
				done <- next(c)
			}()

			select {
			case err := <-done:
				return err
			case <-ctx.Done():
				return echo.NewHTTPError(http.StatusRequestTimeout, "Request timeout")
			}
		}
	}
}

// SecureCompare performs a constant-time string comparison.
func SecureCompare(a, b string) bool {
	return subtle.ConstantTimeCompare([]byte(a), []byte(b)) == 1
}
