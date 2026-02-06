package security

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestSecurityHeaders tests that all required security headers are set
func TestSecurityHeaders(t *testing.T) {
	// Apply security middleware
	// e.Use(middleware.SecurityHeaders())

	rec := httptest.NewRecorder()

	// Test all critical security headers
	tests := []struct {
		header   string
		expected string
		desc     string
	}{
		{
			header:   "X-Content-Type-Options",
			expected: "nosniff",
			desc:     "Prevents MIME type sniffing",
		},
		{
			header:   "X-Frame-Options",
			expected: "DENY",
			desc:     "Prevents clickjacking attacks",
		},
		{
			header:   "X-XSS-Protection",
			expected: "1; mode=block",
			desc:     "Enables browser XSS protection",
		},
		{
			header:   "Strict-Transport-Security",
			expected: "max-age=31536000; includeSubDomains",
			desc:     "Enforces HTTPS connections",
		},
		{
			header:   "Referrer-Policy",
			expected: "strict-origin-when-cross-origin",
			desc:     "Controls referrer information",
		},
	}

	for _, tt := range tests {
		t.Run(tt.header, func(t *testing.T) {
			headerValue := rec.Header().Get(tt.header)
			assert.Contains(t, headerValue, tt.expected,
				"Header %s should be set for %s", tt.header, tt.desc)
		})
	}
}

// TestContentSecurityPolicy tests CSP header configuration with nonce-based protection
func TestContentSecurityPolicy(t *testing.T) {
	rec := httptest.NewRecorder()

	csp := rec.Header().Get("Content-Security-Policy")

	// Test CSP directives
	requiredDirectives := []string{
		"default-src 'self'",
		"script-src 'self' 'nonce-",
		"style-src 'self' 'nonce-",
		"img-src 'self' data: https:",
		"connect-src 'self'",
		"frame-ancestors 'none'",
	}

	for _, directive := range requiredDirectives {
		assert.Contains(t, csp, directive,
			"CSP should include directive: %s", directive)
	}

	// Ensure unsafe directives are NOT present
	unsafeDirectives := []string{
		"'unsafe-eval'",
		"'unsafe-inline'",
	}

	for _, unsafe := range unsafeDirectives {
		assert.NotContains(t, csp, unsafe,
			"CSP should NOT contain unsafe directive: %s", unsafe)
	}

	// Verify script-src and style-src use nonces
	assert.Contains(t, csp, "script-src 'self' 'nonce-",
		"script-src should use nonce-based protection")
	assert.Contains(t, csp, "style-src 'self' 'nonce-",
		"style-src should use nonce-based protection")
}

// TestCORSHeaders tests CORS configuration
func TestCORSHeaders(t *testing.T) {
	allowedOrigins := []string{
		"https://app.tracertm.com",
		"https://tracertm.com",
	}

	for _, origin := range allowedOrigins {
		t.Run("Allowed origin: "+origin, func(t *testing.T) {
			rec := httptest.NewRecorder()

			// Should allow configured origins
			assert.Equal(t, origin, rec.Header().Get("Access-Control-Allow-Origin"),
				"Should allow configured origin")
			assert.Equal(t, "true", rec.Header().Get("Access-Control-Allow-Credentials"),
				"Should allow credentials")
		})
	}

	t.Run("Disallowed origin", func(t *testing.T) {
		rec := httptest.NewRecorder()

		// Should not allow unauthorized origins
		assert.NotEqual(t, "https://malicious.com", rec.Header().Get("Access-Control-Allow-Origin"),
			"Should not allow unauthorized origin")
	})
}

// TestCORSPreflightRequest tests OPTIONS preflight handling
func TestCORSPreflightRequest(t *testing.T) {
	req := httptest.NewRequest(http.MethodOptions, "/api/items", nil)
	req.Header.Set("Origin", "https://app.tracertm.com")
	req.Header.Set("Access-Control-Request-Method", "POST")
	req.Header.Set("Access-Control-Request-Headers", "Content-Type, Authorization")
	rec := httptest.NewRecorder()

	// Should handle preflight request
	assert.Equal(t, http.StatusNoContent, rec.Code,
		"Preflight should return 204 No Content")

	allowedMethods := rec.Header().Get("Access-Control-Allow-Methods")
	assert.Contains(t, allowedMethods, "POST",
		"Should allow POST method")
	assert.Contains(t, allowedMethods, "GET",
		"Should allow GET method")

	allowedHeaders := rec.Header().Get("Access-Control-Allow-Headers")
	assert.Contains(t, allowedHeaders, "Content-Type",
		"Should allow Content-Type header")
	assert.Contains(t, allowedHeaders, "Authorization",
		"Should allow Authorization header")
}

// TestPermissionsPolicy tests Permissions-Policy header
func TestPermissionsPolicy(t *testing.T) {
	rec := httptest.NewRecorder()

	permissionsPolicy := rec.Header().Get("Permissions-Policy")

	// Should restrict sensitive features
	restrictedFeatures := []string{
		"geolocation=()",
		"microphone=()",
		"camera=()",
	}

	for _, feature := range restrictedFeatures {
		assert.Contains(t, permissionsPolicy, feature,
			"Should restrict feature: %s", feature)
	}
}

// TestNoCacheHeaders tests cache control for sensitive endpoints
func TestNoCacheHeaders(t *testing.T) {
	sensitiveEndpoints := []string{
		"/api/auth/login",
		"/api/auth/callback",
		"/api/users/profile",
		"/api/settings",
	}

	for _, endpoint := range sensitiveEndpoints {
		t.Run("No cache: "+endpoint, func(t *testing.T) {
			rec := httptest.NewRecorder()

			cacheControl := rec.Header().Get("Cache-Control")
			assert.Contains(t, cacheControl, "no-store",
				"Sensitive endpoint should have no-store directive")
			assert.Contains(t, cacheControl, "no-cache",
				"Sensitive endpoint should have no-cache directive")
			assert.Contains(t, cacheControl, "must-revalidate",
				"Sensitive endpoint should have must-revalidate directive")

			pragma := rec.Header().Get("Pragma")
			assert.Equal(t, "no-cache", pragma,
				"Should set Pragma: no-cache for older clients")
		})
	}
}

// TestHTTPSRedirect tests that HTTP requests are redirected to HTTPS
func TestHTTPSRedirect(t *testing.T) {
	rec := httptest.NewRecorder()

	// Should redirect to HTTPS in production
	if rec.Code == http.StatusMovedPermanently || rec.Code == http.StatusPermanentRedirect {
		location := rec.Header().Get("Location")
		assert.Contains(t, location, "https://",
			"Should redirect to HTTPS")
	}
}

// TestCrossSiteScriptingHeaders tests XSS protection headers
func TestCrossSiteScriptingHeaders(t *testing.T) {
	rec := httptest.NewRecorder()

	// X-XSS-Protection for older browsers
	xssProtection := rec.Header().Get("X-XSS-Protection")
	assert.Equal(t, "1; mode=block", xssProtection,
		"Should enable XSS protection in block mode")

	// X-Content-Type-Options prevents MIME sniffing
	contentTypeOptions := rec.Header().Get("X-Content-Type-Options")
	assert.Equal(t, "nosniff", contentTypeOptions,
		"Should prevent MIME type sniffing")
}

// TestClickjackingProtection tests X-Frame-Options and CSP frame-ancestors
func TestClickjackingProtection(t *testing.T) {
	rec := httptest.NewRecorder()

	// X-Frame-Options
	xFrameOptions := rec.Header().Get("X-Frame-Options")
	assert.Equal(t, "DENY", xFrameOptions,
		"Should deny framing to prevent clickjacking")

	// CSP frame-ancestors
	csp := rec.Header().Get("Content-Security-Policy")
	assert.Contains(t, csp, "frame-ancestors 'none'",
		"CSP should also prevent framing")
}

// TestServerHeaderExposure tests that server version is not exposed
func TestServerHeaderExposure(t *testing.T) {
	rec := httptest.NewRecorder()

	// Should not expose server version
	server := rec.Header().Get("Server")
	assert.NotContains(t, server, "Echo",
		"Should not expose framework name")
	assert.NotContains(t, server, "Go",
		"Should not expose Go version")

	// X-Powered-By should not be present
	xPoweredBy := rec.Header().Get("X-Powered-By")
	assert.Empty(t, xPoweredBy,
		"Should not expose X-Powered-By header")
}

// TestContentTypeValidation tests that Content-Type is validated
func TestContentTypeValidation(t *testing.T) {
	invalidContentTypes := []string{
		"text/html",
		"application/x-www-form-urlencoded",
		"multipart/form-data",
	}

	for _, contentType := range invalidContentTypes {
		t.Run("Invalid Content-Type: "+contentType, func(t *testing.T) {
			rec := httptest.NewRecorder()

			// Should reject non-JSON content types for API endpoints
			assert.Equal(t, http.StatusUnsupportedMediaType, rec.Code,
				"Should reject invalid Content-Type for API")
		})
	}

	t.Run("Valid Content-Type", func(t *testing.T) {
		rec := httptest.NewRecorder()

		// Should accept valid JSON content type
		assert.NotEqual(t, http.StatusUnsupportedMediaType, rec.Code,
			"Should accept application/json")
	})
}

// TestSecurityHeadersOnError tests that security headers are set even on error responses
func TestSecurityHeadersOnError(t *testing.T) {
	rec := httptest.NewRecorder()

	// Even 404 responses should have security headers
	assert.NotEmpty(t, rec.Header().Get("X-Content-Type-Options"),
		"Error responses should have security headers")
	assert.NotEmpty(t, rec.Header().Get("X-Frame-Options"),
		"Error responses should have security headers")
}
