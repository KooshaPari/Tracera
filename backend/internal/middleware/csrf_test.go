//go:build !integration && !e2e

package middleware

import (
	"encoding/base64"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestGenerateCSRFToken tests CSRF token generation
func TestGenerateCSRFToken(t *testing.T) {
	token, err := generateCSRFToken(32)
	require.NoError(t, err)
	assert.NotEmpty(t, token)

	// Verify it's base64 encoded
	decoded, err := base64.StdEncoding.DecodeString(token)
	require.NoError(t, err)
	assert.Len(t, decoded, 32)

	// Verify uniqueness
	token2, err := generateCSRFToken(32)
	require.NoError(t, err)
	assert.NotEqual(t, token, token2)
}

// TestValidateCSRFToken tests CSRF token validation
func TestValidateCSRFToken(t *testing.T) {
	secret := []byte("test-secret-key")
	token, err := generateCSRFToken(32)
	require.NoError(t, err)

	// Valid token should validate
	isValid := validateCSRFToken(secret, token, token)
	assert.True(t, isValid)

	// Different token should not validate
	differentToken, err := generateCSRFToken(32)
	require.NoError(t, err)
	isValid = validateCSRFToken(secret, token, differentToken)
	assert.False(t, isValid)

	// Empty stored token should not validate
	isValid = validateCSRFToken(secret, "", token)
	assert.False(t, isValid)

	// Empty submitted token should not validate
	isValid = validateCSRFToken(secret, token, "")
	assert.False(t, isValid)
}

// TestCSRFMiddlewareGET tests CSRF token generation on GET requests
func TestCSRFMiddlewareGET(t *testing.T) {
	e := echo.New()
	config := CSRFConfig{
		Secret:      []byte("test-secret"),
		TokenLength: 32,
		Enabled:     true,
	}

	middleware := CSRFMiddleware(config)

	handler := func(c echo.Context) error {
		token := GetCSRFToken(c)
		assert.NotEmpty(t, token)
		return c.String(http.StatusOK, token)
	}

	wrappedHandler := middleware(handler)

	req := httptest.NewRequest(http.MethodGet, "/api/v1/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := wrappedHandler(c)
	require.NoError(t, err)

	// Check that token is set in cookie
	cookies := rec.Result().Cookies()
	var csrfCookie *http.Cookie
	for _, cookie := range cookies {
		if cookie.Name == CSRFTokenCookie {
			csrfCookie = cookie
			break
		}
	}
	assert.NotNil(t, csrfCookie)
	assert.NotEmpty(t, csrfCookie.Value)
	assert.False(t, csrfCookie.HttpOnly)
	assert.Equal(t, http.SameSiteStrictMode, csrfCookie.SameSite)
}

// TestCSRFMiddlewarePOSTValid tests CSRF validation on POST requests with valid token
func TestCSRFMiddlewarePOSTValid(t *testing.T) {
	e := echo.New()
	secret := []byte("test-secret")
	config := CSRFConfig{
		Secret:      secret,
		TokenLength: 32,
		Enabled:     true,
	}

	middleware := CSRFMiddleware(config)

	// First, get a token via GET
	getHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, GetCSRFToken(c))
	}
	wrappedGetHandler := middleware(getHandler)

	req := httptest.NewRequest(http.MethodGet, "/api/v1/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := wrappedGetHandler(c)
	require.NoError(t, err)

	// Extract token from cookie
	cookies := rec.Result().Cookies()
	var token string
	for _, cookie := range cookies {
		if cookie.Name == CSRFTokenCookie {
			token = cookie.Value
			break
		}
	}
	require.NotEmpty(t, token)

	// Now POST with the token in header
	postHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}
	wrappedPostHandler := middleware(postHandler)

	postReq := httptest.NewRequest(http.MethodPost, "/api/v1/test", nil)
	postReq.AddCookie(&http.Cookie{
		Name:  CSRFTokenCookie,
		Value: token,
	})
	postReq.Header.Set(CSRFHeaderName, token)

	postRec := httptest.NewRecorder()
	postC := e.NewContext(postReq, postRec)

	err = wrappedPostHandler(postC)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, postRec.Code)
}

// TestCSRFMiddlewarePOSTMissingToken tests CSRF validation with missing token
func TestCSRFMiddlewarePOSTMissingToken(t *testing.T) {
	e := echo.New()
	config := CSRFConfig{
		Secret:      []byte("test-secret"),
		TokenLength: 32,
		Enabled:     true,
	}

	middleware := CSRFMiddleware(config)

	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}
	wrappedHandler := middleware(handler)

	// POST without token
	req := httptest.NewRequest(http.MethodPost, "/api/v1/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := wrappedHandler(c)
	require.Error(t, err)

	httpErr := func() *echo.HTTPError {
		target := &echo.HTTPError{}
		_ = errors.As(err, &target)
		return target
	}()
	assert.Equal(t, http.StatusForbidden, httpErr.Code)
}

// TestCSRFMiddlewarePOSTInvalidToken tests CSRF validation with invalid token
func TestCSRFMiddlewarePOSTInvalidToken(t *testing.T) {
	e := echo.New()
	config := CSRFConfig{
		Secret:      []byte("test-secret"),
		TokenLength: 32,
		Enabled:     true,
	}

	middleware := CSRFMiddleware(config)

	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}
	wrappedHandler := middleware(handler)

	validToken, err := generateCSRFToken(32)
	require.NoError(t, err)

	invalidToken, err := generateCSRFToken(32)
	require.NoError(t, err)

	// POST with mismatched token
	req := httptest.NewRequest(http.MethodPost, "/api/v1/test", nil)
	req.AddCookie(&http.Cookie{
		Name:  CSRFTokenCookie,
		Value: validToken,
	})
	req.Header.Set(CSRFHeaderName, invalidToken)

	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = wrappedHandler(c)
	require.Error(t, err)

	httpErr := func() *echo.HTTPError {
		target := &echo.HTTPError{}
		_ = errors.As(err, &target)
		return target
	}()
	assert.Equal(t, http.StatusForbidden, httpErr.Code)
}

// TestCSRFMiddlewarePUTValid tests CSRF validation on PUT requests
func TestCSRFMiddlewarePUTValid(t *testing.T) {
	runCSRFValidMethodTest(t, http.MethodPut)
}

// TestCSRFMiddlewareDELETEValid tests CSRF validation on DELETE requests
func TestCSRFMiddlewareDELETEValid(t *testing.T) {
	runCSRFValidMethodTest(t, http.MethodDelete)
}

// TestCSRFMiddlewarePATCHValid tests CSRF validation on PATCH requests
func TestCSRFMiddlewarePATCHValid(t *testing.T) {
	runCSRFValidMethodTest(t, http.MethodPatch)
}

func runCSRFValidMethodTest(t *testing.T, method string) {
	t.Helper()

	e := echo.New()
	secret := []byte("test-secret")
	config := CSRFConfig{
		Secret:      secret,
		TokenLength: 32,
		Enabled:     true,
	}

	middleware := CSRFMiddleware(config)

	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}
	wrappedHandler := middleware(handler)

	token, err := generateCSRFToken(32)
	require.NoError(t, err)

	req := httptest.NewRequest(method, "/api/v1/test", nil)
	req.AddCookie(&http.Cookie{
		Name:  CSRFTokenCookie,
		Value: token,
	})
	req.Header.Set(CSRFHeaderName, token)

	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = wrappedHandler(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

// TestCSRFMiddlewareDisabled tests that CSRF validation is skipped when disabled
func TestCSRFMiddlewareDisabled(t *testing.T) {
	e := echo.New()
	config := CSRFConfig{
		Secret:      []byte(""),
		TokenLength: 32,
		Enabled:     false,
	}

	middleware := CSRFMiddleware(config)

	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}
	wrappedHandler := middleware(handler)

	// POST without token when CSRF is disabled
	req := httptest.NewRequest(http.MethodPost, "/api/v1/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := wrappedHandler(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

// TestCSRFSkipper tests the CSRF skipper function
func TestCSRFSkipper(t *testing.T) {
	e := echo.New()

	tests := []struct {
		name     string
		path     string
		expected bool
	}{
		{
			name:     "Health check should be skipped",
			path:     "/health",
			expected: true,
		},
		{
			name:     "Metrics should be skipped",
			path:     "/metrics",
			expected: true,
		},
		{
			name:     "Login should be skipped",
			path:     "/auth/login",
			expected: true,
		},
		{
			name:     "Register should be skipped",
			path:     "/auth/register",
			expected: true,
		},
		{
			name:     "Token refresh should be skipped",
			path:     "/auth/refresh",
			expected: true,
		},
		{
			name:     "Auth callback should be skipped",
			path:     "/auth/callback",
			expected: true,
		},
		{
			name:     "OAuth login should be skipped",
			path:     "/oauth/login",
			expected: true,
		},
		{
			name:     "OAuth callback should be skipped",
			path:     "/oauth/callback",
			expected: true,
		},
		{
			name:     "OAuth logout should be skipped",
			path:     "/oauth/logout",
			expected: true,
		},
		{
			name:     "OAuth status should be skipped",
			path:     "/oauth/status",
			expected: true,
		},
		{
			name:     "Webhook should be skipped",
			path:     "/webhook/stripe",
			expected: true,
		},
		{
			name:     "Regular API endpoint should not be skipped",
			path:     "/api/v1/items",
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, tt.path, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			result := CSRFSkipper(c)
			assert.Equal(t, tt.expected, result)
		})
	}
}

// TestGetCSRFToken tests retrieving CSRF token from context
func TestGetCSRFToken(t *testing.T) {
	e := echo.New()

	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	// Token not set should return empty
	token := GetCSRFToken(c)
	assert.Empty(t, token)

	// Set token and retrieve
	testToken := "test-token-12345"
	c.Set(CSRFTokenContextKey, testToken)
	token = GetCSRFToken(c)
	assert.Equal(t, testToken, token)
}

// TestNewCSRFConfig tests creating CSRF config from environment
func TestNewCSRFConfig(t *testing.T) {
	// This test verifies config structure, actual env loading tested via integration tests
	config := NewCSRFConfig()
	assert.NotNil(t, config)
	// Config should have default values
	assert.NotEmpty(t, config.SameSite)
}

// TestParseSameSite tests SameSite parsing
func TestParseSameSite(t *testing.T) {
	tests := []struct {
		input    string
		expected http.SameSite
	}{
		{"strict", http.SameSiteStrictMode},
		{"Strict", http.SameSiteStrictMode},
		{"STRICT", http.SameSiteStrictMode},
		{"lax", http.SameSiteLaxMode},
		{"Lax", http.SameSiteLaxMode},
		{"LAX", http.SameSiteLaxMode},
		{"none", http.SameSiteNoneMode},
		{"None", http.SameSiteNoneMode},
		{"NONE", http.SameSiteNoneMode},
		{"invalid", http.SameSiteStrictMode}, // defaults to Strict
	}

	for _, tt := range tests {
		t.Run("SameSite_"+tt.input, func(t *testing.T) {
			result := parseSameSite(tt.input)
			assert.Equal(t, tt.expected, result)
		})
	}
}

// TestCSRFTokenRotation tests that tokens are rotated after validation
func TestCSRFTokenRotation(t *testing.T) {
	e := echo.New()
	secret := []byte("test-secret")
	config := CSRFConfig{
		Secret:      secret,
		TokenLength: 32,
		Enabled:     true,
	}

	middleware := CSRFMiddleware(config)

	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}
	wrappedHandler := middleware(handler)

	token, err := generateCSRFToken(32)
	require.NoError(t, err)

	// POST with valid token
	req := httptest.NewRequest(http.MethodPost, "/api/v1/test", nil)
	req.AddCookie(&http.Cookie{
		Name:  CSRFTokenCookie,
		Value: token,
	})
	req.Header.Set(CSRFHeaderName, token)

	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = wrappedHandler(c)
	require.NoError(t, err)

	// Check that a new token is set in the response cookie
	cookies := rec.Result().Cookies()
	var newToken string
	for _, cookie := range cookies {
		if cookie.Name == CSRFTokenCookie {
			newToken = cookie.Value
			break
		}
	}

	// New token should be different from original
	assert.NotEmpty(t, newToken)
	assert.NotEqual(t, token, newToken)
}

// TestCSRFFormData tests CSRF token from form data (for POST requests)
func TestCSRFFormData(t *testing.T) {
	e := echo.New()
	secret := []byte("test-secret")
	config := CSRFConfig{
		Secret:      secret,
		TokenLength: 32,
		Enabled:     true,
	}

	middleware := CSRFMiddleware(config)

	// First, get a token via GET
	getHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, GetCSRFToken(c))
	}
	wrappedGetHandler := middleware(getHandler)

	req := httptest.NewRequest(http.MethodGet, "/api/v1/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := wrappedGetHandler(c)
	require.NoError(t, err)

	// Extract token from cookie
	cookies := rec.Result().Cookies()
	var token string
	for _, cookie := range cookies {
		if cookie.Name == CSRFTokenCookie {
			token = cookie.Value
			break
		}
	}
	require.NotEmpty(t, token)

	// Now POST with token in form data
	postHandler := func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	}
	wrappedPostHandler := middleware(postHandler)

	body := "_csrf_token=" + token + "&name=test"
	postReq := httptest.NewRequest(http.MethodPost, "/api/v1/test", strings.NewReader(body))
	postReq.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	postReq.AddCookie(&http.Cookie{
		Name:  CSRFTokenCookie,
		Value: token,
	})

	postRec := httptest.NewRecorder()
	postC := e.NewContext(postReq, postRec)

	err = wrappedPostHandler(postC)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, postRec.Code)
}

// TestIsStateChangingRequest tests state-changing request detection
func TestIsStateChangingRequest(t *testing.T) {
	tests := []struct {
		method   string
		expected bool
	}{
		{http.MethodPost, true},
		{http.MethodPut, true},
		{http.MethodPatch, true},
		{http.MethodDelete, true},
		{http.MethodGet, false},
		{http.MethodHead, false},
		{http.MethodOptions, false},
		{http.MethodTrace, false},
	}

	for _, tt := range tests {
		t.Run(tt.method, func(t *testing.T) {
			result := isStateChangingRequest(tt.method)
			assert.Equal(t, tt.expected, result)
		})
	}
}
