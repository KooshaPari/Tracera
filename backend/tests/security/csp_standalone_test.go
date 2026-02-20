package security

import (
	"encoding/base64"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/middleware"
)

// TestSecurityHeadersCSPNonce tests the nonce-based CSP implementation
func TestSecurityHeadersCSPNonce(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	t.Run("generates unique nonce per request", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
		h := mw(handler)

		nonces := make(map[string]bool)

		// Make multiple requests
		for i := 0; i < 10; i++ {
			req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			err := h(c)
			require.NoError(t, err)

			csp := rec.Header().Get("Content-Security-Policy")
			assert.NotEmpty(t, csp, "CSP header should be set")

			// Extract nonce from CSP
			parts := strings.Split(csp, "'nonce-")
			require.Len(t, parts, 3, "CSP should contain exactly 2 nonces (script-src and style-src)")

			nonce1 := strings.Split(parts[1], "'")[0]
			nonce2 := strings.Split(parts[2], "'")[0]

			// Both nonces should be present and equal
			assert.NotEmpty(t, nonce1)
			assert.NotEmpty(t, nonce2)
			assert.Equal(t, nonce1, nonce2, "script-src and style-src should have same nonce")

			nonces[nonce1] = true
		}

		// Each request should have a unique nonce
		assert.Len(t, nonces, 10, "Should generate 10 unique nonces for 10 requests")
	})

	t.Run("nonce is valid base64", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
		h := mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)

		csp := rec.Header().Get("Content-Security-Policy")
		parts := strings.Split(csp, "'nonce-")
		nonce := strings.Split(parts[1], "'")[0]

		// Try to decode the nonce as base64
		decoded, err := base64.StdEncoding.DecodeString(nonce)
		require.NoError(t, err, "Nonce should be valid base64")
		assert.Len(t, decoded, 32, "Nonce should decode to 32 bytes")
	})

	t.Run("CSP contains no unsafe directives", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
		h := mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)

		csp := rec.Header().Get("Content-Security-Policy")
		assert.NotContains(t, csp, "'unsafe-inline'", "CSP should not contain 'unsafe-inline'")
		assert.NotContains(t, csp, "'unsafe-eval'", "CSP should not contain 'unsafe-eval'")
	})

	t.Run("CSP contains required directives", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
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
	})

	t.Run("nonce is available in context", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
		h := mw(func(c echo.Context) error {
			nonce := middleware.GetNonce(c)
			assert.NotEmpty(t, nonce, "GetNonce should return non-empty nonce")
			assert.Len(t, nonce, 44, "Base64 encoded 32-byte nonce should be 44 characters")
			return c.String(http.StatusOK, nonce)
		})

		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("security headers are always set", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
		h := mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)

		// Verify all security headers are present
		assert.NotEmpty(t, rec.Header().Get("X-Content-Type-Options"))
		assert.NotEmpty(t, rec.Header().Get("X-Frame-Options"))
		assert.NotEmpty(t, rec.Header().Get("X-XSS-Protection"))
		assert.NotEmpty(t, rec.Header().Get("Strict-Transport-Security"))
		assert.NotEmpty(t, rec.Header().Get("Content-Security-Policy"))
		assert.NotEmpty(t, rec.Header().Get("Referrer-Policy"))
		assert.NotEmpty(t, rec.Header().Get("Permissions-Policy"))
	})

	t.Run("security headers are set on error responses", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
		h := mw(func(c echo.Context) error {
			return echo.NewHTTPError(http.StatusInternalServerError, "error")
		})

		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		h(c)

		// Security headers should still be set even on error
		csp := rec.Header().Get("Content-Security-Policy")
		assert.NotEmpty(t, csp, "CSP should be set even on error response")
		assert.Contains(t, csp, "'nonce-", "CSP should contain nonce on error response")
	})

	t.Run("nonce format validation", func(t *testing.T) {
		mw := middleware.SecurityHeaders()
		h := mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)

		csp := rec.Header().Get("Content-Security-Policy")

		// Extract script-src nonce
		scriptStart := strings.Index(csp, "script-src 'self' 'nonce-")
		require.NotEqual(t, -1, scriptStart, "script-src should contain nonce")

		styleStart := strings.Index(csp, "style-src 'self' 'nonce-")
		require.NotEqual(t, -1, styleStart, "style-src should contain nonce")

		// Verify format
		assert.Contains(t, csp, "script-src 'self' 'nonce-")
		assert.Contains(t, csp, "style-src 'self' 'nonce-")
	})
}

// TestGetNonceFunction tests the GetNonce utility function
func TestGetNonceFunctionStandalone(t *testing.T) {
	e := echo.New()

	t.Run("returns nonce from context", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		testNonce := "test-nonce-value"
		c.Set("csp_nonce", testNonce)

		nonce := middleware.GetNonce(c)
		assert.Equal(t, testNonce, nonce)
	})

	t.Run("returns empty string if nonce not in context", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		nonce := middleware.GetNonce(c)
		assert.Empty(t, nonce)
	})

	t.Run("returns empty string if context value is not string", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		c.Set("csp_nonce", 123) // Wrong type

		nonce := middleware.GetNonce(c)
		assert.Empty(t, nonce)
	})
}

// TestCSPNoUnsafeKeywords verifies no unsafe keywords exist in CSP
func TestCSPNoUnsafeKeywords(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := middleware.SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	csp := rec.Header().Get("Content-Security-Policy")

	unsafeKeywords := []string{
		"'unsafe-inline'",
		"'unsafe-eval'",
		"script-src 'self';", // Without nonce
		"style-src 'self';",  // Without nonce
	}

	for _, keyword := range unsafeKeywords {
		assert.NotContains(t, csp, keyword,
			"CSP should not contain: %s", keyword)
	}
}

// TestCSPDirectivesOrder verifies CSP directives are in correct format
func TestCSPDirectivesOrder(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}

	mw := middleware.SecurityHeaders()
	h := mw(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := h(c)
	require.NoError(t, err)

	csp := rec.Header().Get("Content-Security-Policy")

	// Verify order and presence
	directives := []string{
		"default-src 'self'",
		"script-src 'self' 'nonce-",
		"style-src 'self' 'nonce-",
		"img-src 'self' data: https:",
		"font-src 'self' data:",
		"connect-src 'self' wss: https:",
		"frame-ancestors 'none'",
	}

	currentPos := 0
	for _, directive := range directives {
		pos := strings.Index(csp, directive)
		require.NotEqual(t, -1, pos, "Directive should exist: %s", directive)
		require.Greater(t, pos, currentPos, "Directives should be in order: %s", directive)
		currentPos = pos
	}
}
