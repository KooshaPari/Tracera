package middleware

import (
	"encoding/base64"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestSecurityHeadersGeneratesNonce tests nonce generation in CSP
func TestSecurityHeadersGeneratesNonce(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	csp := rec.Header().Get("Content-Security-Policy")
	assert.NotEmpty(t, csp, "CSP header should be set")

	// Verify nonce is in CSP
	assert.Contains(t, csp, "'nonce-", "CSP should contain nonce")
	assert.Contains(t, csp, "script-src 'self' 'nonce-", "script-src should use nonce")
	assert.Contains(t, csp, "style-src 'self' 'nonce-", "style-src should use nonce")
}

// TestSecurityHeadersNonceUniqueness tests that nonces are unique per request
func TestSecurityHeadersNonceUniqueness(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := SecurityHeaders()
	handler = mw(handler)

	nonces := make(map[string]bool)

	// Make multiple requests
	for i := 0; i < 5; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler(c)
		require.NoError(t, err)

		csp := rec.Header().Get("Content-Security-Policy")

		// Extract nonce
		parts := strings.Split(csp, "'nonce-")
		require.GreaterOrEqual(t, len(parts), 2, "CSP should contain nonce")

		nonce := strings.Split(parts[1], "'")[0]
		nonces[nonce] = true
	}

	// Each request should have a unique nonce
	assert.Len(t, nonces, 5, "Should generate 5 unique nonces")
}

// TestSecurityHeadersNonceIsBase64 tests that nonce is valid base64
func TestSecurityHeadersNonceIsBase64(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	csp := rec.Header().Get("Content-Security-Policy")

	// Extract nonce
	parts := strings.Split(csp, "'nonce-")
	nonce := strings.Split(parts[1], "'")[0]

	// Verify it's valid base64
	decoded, err := base64.StdEncoding.DecodeString(nonce)
	require.NoError(t, err, "Nonce should be valid base64")
	assert.Len(t, decoded, 32, "Nonce should decode to 32 bytes")
}

// TestSecurityHeadersNoUnsafeDirectives tests that unsafe directives are not present
func TestSecurityHeadersNoUnsafeDirectives(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	csp := rec.Header().Get("Content-Security-Policy")

	// Verify no unsafe directives
	assert.NotContains(t, csp, "'unsafe-inline'", "CSP should not contain 'unsafe-inline'")
	assert.NotContains(t, csp, "'unsafe-eval'", "CSP should not contain 'unsafe-eval'")
}

// TestSecurityHeadersRequiredDirectives tests that all required directives are present
func TestSecurityHeadersRequiredDirectives(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	csp := rec.Header().Get("Content-Security-Policy")

	requiredDirectives := []string{
		"default-src 'self'",
		"script-src 'self' 'nonce-",
		"style-src 'self' 'nonce-",
		"img-src 'self' data: https:",
		"font-src 'self' data:",
		"connect-src 'self' wss: https:",
		"frame-ancestors 'none'",
	}

	for _, directive := range requiredDirectives {
		assert.Contains(t, csp, directive,
			"CSP should contain directive: %s", directive)
	}
}

// TestGetNonceRetrievesFromContext tests GetNonce function
func TestGetNonceRetrievesFromContext(t *testing.T) {
	e := echo.New()

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	// Set a nonce in context
	testNonce := "test-nonce-12345"
	c.Set("csp_nonce", testNonce)

	// Retrieve it
	nonce := GetNonce(c)
	assert.Equal(t, testNonce, nonce)
}

// TestGetNonceReturnsEmptyWhenMissing tests GetNonce with missing nonce
func TestGetNonceReturnsEmptyWhenMissing(t *testing.T) {
	e := echo.New()

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	// Don't set a nonce
	nonce := GetNonce(c)
	assert.Empty(t, nonce)
}

// TestSecurityHeadersOnErrorResponse tests that security headers are set on errors
func TestSecurityHeadersOnErrorResponse(t *testing.T) {
	e := echo.New()
	handler := func(_ echo.Context) error {
		return echo.NewHTTPError(http.StatusInternalServerError, "test error")
	}

	mw := SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.Error(t, err)

	// Verify security headers are still set
	csp := rec.Header().Get("Content-Security-Policy")
	assert.NotEmpty(t, csp, "CSP should be set on error responses")
	assert.Contains(t, csp, "'nonce-", "CSP should contain nonce on error")

	assert.NotEmpty(t, rec.Header().Get("X-Content-Type-Options"))
	assert.NotEmpty(t, rec.Header().Get("X-Frame-Options"))
}

// TestSecurityHeadersAllHeadersSet tests all security headers are present
func TestSecurityHeadersAllHeadersSet(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	headers := map[string]string{
		"X-Content-Type-Options": "nosniff",
		"X-Frame-Options":        "DENY",
		"X-XSS-Protection":       "1; mode=block",
		"Referrer-Policy":        "strict-origin-when-cross-origin",
		"Permissions-Policy":     "geolocation=(), microphone=(), camera=()",
	}

	for header, expectedValue := range headers {
		actual := rec.Header().Get(header)
		assert.NotEmpty(t, actual, "Header %s should be set", header)
		assert.Contains(t, actual, expectedValue, "Header %s should contain %s", header, expectedValue)
	}

	// CSP is special due to nonce
	csp := rec.Header().Get("Content-Security-Policy")
	assert.NotEmpty(t, csp, "Content-Security-Policy should be set")
	assert.Contains(t, csp, "'nonce-")
}

// TestNonceStoredInContext tests that nonce is stored in context
func TestNonceStoredInContext(t *testing.T) {
	e := echo.New()
	var capturedNonce string
	handler := func(c echo.Context) error {
		capturedNonce = GetNonce(c)
		return c.String(http.StatusOK, "ok")
	}

	mw := SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	// Verify nonce was captured
	assert.NotEmpty(t, capturedNonce, "Nonce should be available in context")
	assert.Len(t, capturedNonce, 44, "Base64 encoded 32-byte nonce should be 44 characters")

	// Verify it matches the CSP
	csp := rec.Header().Get("Content-Security-Policy")
	assert.Contains(t, csp, capturedNonce, "CSP should contain the captured nonce")
}
