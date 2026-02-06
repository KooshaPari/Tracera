package middleware

import (
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

const (
	// CSRFTokenHeader is the header name for CSRF token
	//nolint:gosec //G101 - this is a header name, not a credential
	CSRFTokenHeader = "X-CSRF-Token"

	// CSRFTokenCookie is the cookie name for CSRF token
	CSRFTokenCookie = "csrf_token"

	// CSRFTokenContextKey is the context key for CSRF token
	CSRFTokenContextKey = "csrf_token"

	// DefaultCSRFTokenLength is the default length of CSRF tokens in bytes
	DefaultCSRFTokenLength = 32

	// DefaultCSRFTokenExpiry is the default expiry time for CSRF tokens
	DefaultCSRFTokenExpiry = 24 * time.Hour

	// Exempt paths
	csrfPathHealth  = "/health"
	csrfPathMetrics = "/metrics"
)

// CSRFConfig holds CSRF middleware configuration
type CSRFConfig struct {
	// Secret key for signing tokens (from CSRF_SECRET env)
	Secret []byte

	// Skipper allows skipping CSRF validation for specific routes
	Skipper middleware.Skipper

	// TokenLength is the length of generated tokens in bytes
	TokenLength int

	// TokenExpiry is the expiry duration for tokens
	TokenExpiry time.Duration

	// Enabled controls whether CSRF protection is active
	Enabled bool

	// SameSite cookie attribute (Strict, Lax, None)
	SameSite string
}

// CSRFMiddleware creates a CSRF protection middleware
// It validates CSRF tokens on state-changing requests (POST, PUT, DELETE, PATCH)
func CSRFMiddleware(config CSRFConfig) echo.MiddlewareFunc {
	if config.Skipper == nil {
		config.Skipper = middleware.DefaultSkipper
	}

	setCSRFDefaults(&config)

	// Validate secret key
	if len(config.Secret) == 0 {
		log.Println("Warning: CSRF_SECRET not configured, CSRF protection disabled")
		config.Enabled = false
	}

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if config.Skipper(c) {
				return next(c)
			}

			// Generate and set CSRF token for GET requests
			if c.Request().Method == http.MethodGet {
				return handleCSRFForGetRequest(c, config, next)
			}

			// Validate CSRF token on state-changing requests
			if isStateChangingRequest(c.Request().Method) {
				return handleCSRFForStateChangingRequest(c, config, next)
			}

			return next(c)
		}
	}
}

// setCSRFDefaults sets default values for CSRF configuration
func setCSRFDefaults(config *CSRFConfig) {
	if config.TokenLength == 0 {
		config.TokenLength = DefaultCSRFTokenLength
	}

	if config.TokenExpiry == 0 {
		config.TokenExpiry = DefaultCSRFTokenExpiry
	}

	if config.SameSite == "" {
		config.SameSite = "Strict"
	}
}

// handleCSRFForGetRequest handles CSRF token generation for GET requests
func handleCSRFForGetRequest(c echo.Context, config CSRFConfig, next echo.HandlerFunc) error {
	token, err := generateCSRFToken(config.TokenLength)
	if err != nil {
		log.Printf("Failed to generate CSRF token: %v", err)
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to generate CSRF token")
	}

	// Store token in context
	c.Set(CSRFTokenContextKey, token)

	// Set token in cookie for client to retrieve
	c.SetCookie(&http.Cookie{
		Name:     CSRFTokenCookie,
		Value:    token,
		Path:     "/",
		HttpOnly: false, // Must be false for JavaScript to read
		Secure:   isSecureCookie(c),
		SameSite: parseSameSite(config.SameSite),
		MaxAge:   int(config.TokenExpiry.Seconds()),
	})

	return next(c)
}

// handleCSRFForStateChangingRequest handles CSRF token validation for state-changing requests
func handleCSRFForStateChangingRequest(c echo.Context, config CSRFConfig, next echo.HandlerFunc) error {
	if !config.Enabled {
		// CSRF disabled, skip validation but log warning
		log.Println("CSRF protection disabled for request:", c.Request().Method, c.Request().URL.Path)
		return next(c)
	}

	// Get token from request (header takes precedence over body)
	tokenFromRequest := extractCSRFToken(c)
	if tokenFromRequest == "" {
		return echo.NewHTTPError(http.StatusForbidden, "missing CSRF token")
	}

	// Get token from cookie
	cookie, err := c.Cookie(CSRFTokenCookie)
	if err != nil {
		return echo.NewHTTPError(http.StatusForbidden, "missing CSRF token cookie")
	}

	// Validate token
	if !validateCSRFToken(config.Secret, cookie.Value, tokenFromRequest) {
		log.Printf("CSRF token validation failed for %s %s", c.Request().Method, c.Request().URL.Path)
		return echo.NewHTTPError(http.StatusForbidden, "invalid CSRF token")
	}

	// Token is valid, generate new token for next request
	newToken, err := generateCSRFToken(config.TokenLength)
	if err != nil {
		log.Printf("Failed to generate new CSRF token: %v", err)
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to refresh CSRF token")
	}

	c.Set(CSRFTokenContextKey, newToken)
	c.SetCookie(&http.Cookie{
		Name:     CSRFTokenCookie,
		Value:    newToken,
		Path:     "/",
		HttpOnly: false,
		Secure:   isSecureCookie(c),
		SameSite: parseSameSite(config.SameSite),
		MaxAge:   int(config.TokenExpiry.Seconds()),
	})

	return next(c)
}

// extractCSRFToken extracts CSRF token from request header or form
func extractCSRFToken(c echo.Context) string {
	// Get token from request (header takes precedence over body)
	tokenFromRequest := c.Request().Header.Get(CSRFTokenHeader)
	if tokenFromRequest == "" {
		// Try form data for POST requests
		if c.Request().Method == http.MethodPost {
			tokenFromRequest = c.FormValue("_csrf_token")
		}
	}
	return tokenFromRequest
}

// generateCSRFToken generates a random CSRF token and signs it with the secret
func generateCSRFToken(length int) (string, error) {
	// Generate random bytes
	randomBytes := make([]byte, length)
	_, err := rand.Read(randomBytes)
	if err != nil {
		return "", err
	}

	// Return base64 encoded token
	return base64.StdEncoding.EncodeToString(randomBytes), nil
}

// signToken signs a token using HMAC-SHA256 and the secret key
func signToken(secret []byte, token string) string {
	h := hmac.New(sha256.New, secret)
	h.Write([]byte(token))
	return hex.EncodeToString(h.Sum(nil))
}

// validateCSRFToken validates a CSRF token against the stored token
// For double-submit pattern, we verify the token matches
func validateCSRFToken(secret []byte, storedToken, submittedToken string) bool {
	// Tokens should match exactly (double-submit cookie pattern)
	// Additional validation: ensure both are non-empty
	if storedToken == "" || submittedToken == "" {
		return false
	}

	// Use HMAC comparison for timing-safe comparison
	storedSigned := signToken(secret, storedToken)
	submittedSigned := signToken(secret, submittedToken)

	return hmac.Equal([]byte(storedSigned), []byte(submittedSigned))
}

// isStateChangingRequest returns true for HTTP methods that change state
func isStateChangingRequest(method string) bool {
	return method == http.MethodPost ||
		method == http.MethodPut ||
		method == http.MethodPatch ||
		method == http.MethodDelete
}

// isSecureCookie returns true if the cookie should have Secure flag
func isSecureCookie(c echo.Context) bool {
	// Use Secure flag if request is HTTPS
	return c.Request().URL.Scheme == "https" ||
		c.Request().Header.Get("X-Forwarded-Proto") == "https"
}

// parseSameSite converts string to http.SameSite
func parseSameSite(sameSite string) http.SameSite {
	switch strings.ToLower(sameSite) {
	case "strict":
		return http.SameSiteStrictMode
	case "lax":
		return http.SameSiteLaxMode
	case "none":
		return http.SameSiteNoneMode
	default:
		return http.SameSiteStrictMode
	}
}

// CSRFSkipper returns a skipper function for routes that should bypass CSRF validation
// This is useful for auth endpoints, webhooks, and health checks
func CSRFSkipper(c echo.Context) bool {
	// Get the path from the request URL (works in tests and production)
	path := c.Request().URL.Path

	// Always skip CSRF for health checks
	if path == csrfPathHealth || path == csrfPathMetrics {
		return true
	}

	// Skip CSRF for public auth endpoints (login, registration, token refresh)
	// These are protected by other means (origin validation, rate limiting)
	if strings.Contains(path, "/auth/") && (strings.Contains(path, "login") ||
		strings.Contains(path, "register") || strings.Contains(path, "refresh") ||
		strings.Contains(path, "callback")) {
		return true
	}

	// Skip CSRF for webhooks and external integrations
	if strings.Contains(path, "/webhook") {
		return true
	}

	// Skip CSRF for WebSocket connections (authenticated via JWT token in upgrade message)
	if strings.Contains(path, "/ws") {
		log.Printf("[DEBUG] Skipping CSRF for WebSocket: %s", path)
		return true
	}

	log.Printf("[DEBUG] CSRF Skipper: NOT skipping for %s", path)
	return false
}

// GetCSRFToken retrieves the CSRF token from the context
func GetCSRFToken(c echo.Context) string {
	token, ok := c.Get(CSRFTokenContextKey).(string)
	if !ok {
		return ""
	}
	return token
}

// NewCSRFConfig creates a new CSRF configuration from environment
func NewCSRFConfig() CSRFConfig {
	csrfSecret := os.Getenv("CSRF_SECRET")
	enabled := csrfSecret != ""
	env := os.Getenv("ENV")

	// In development, CSRF can be disabled if secret is not set
	if env == "development" && csrfSecret == "" {
		log.Println("ℹ️  CSRF protection disabled in development (set CSRF_SECRET to enable)")
		enabled = false
	}

	return CSRFConfig{
		Secret:      []byte(csrfSecret),
		Skipper:     CSRFSkipper,
		TokenLength: DefaultCSRFTokenLength,
		TokenExpiry: DefaultCSRFTokenExpiry,
		SameSite:    "Strict",
		Enabled:     enabled && csrfSecret != "",
	}
}
