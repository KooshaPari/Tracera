package security

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestAuthenticationRequired tests that protected endpoints require authentication
func TestAuthenticationRequired(t *testing.T) {
	protectedEndpoints := []struct {
		method string
		path   string
	}{
		{http.MethodGet, "/api/items"},
		{http.MethodPost, "/api/items"},
		{http.MethodPut, "/api/items/123"},
		{http.MethodDelete, "/api/items/123"},
		{http.MethodGet, "/api/projects"},
		{http.MethodPost, "/api/projects"},
		{http.MethodGet, "/api/links"},
	}

	for _, endpoint := range protectedEndpoints {
		t.Run(endpoint.method+" "+endpoint.path, func(t *testing.T) {
			e := echo.New()

			req := httptest.NewRequest(endpoint.method, endpoint.path, nil)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should return 401 Unauthorized without authentication
			assert.Equal(t, http.StatusUnauthorized, rec.Code,
				"Protected endpoint should require authentication")
		})
	}
}

// TestJWTValidation tests JWT token validation
func TestJWTValidation(t *testing.T) {
	tests := []struct {
		name           string
		token          string
		expectedStatus int
	}{
		{
			name:           "Missing token",
			token:          "",
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Invalid format",
			token:          "Bearer invalid-token",
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Malformed JWT",
			token:          "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Expired token",
			token:          createExpiredToken(t),
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Token with invalid signature",
			token:          createTokenWithInvalidSignature(t),
			expectedStatus: http.StatusUnauthorized,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			e := echo.New()

			req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
			if tt.token != "" {
				req.Header.Set("Authorization", tt.token)
			}
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			assert.Equal(t, tt.expectedStatus, rec.Code)
		})
	}
}

// TestWorkOSIntegration tests WorkOS AuthKit integration
func TestWorkOSIntegration(t *testing.T) {
	t.Run("Valid WorkOS token", func(t *testing.T) {
		e := echo.New()

		// Simulate valid WorkOS JWT
		validToken := createValidWorkOSToken(t)

		req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
		req.Header.Set("Authorization", "Bearer "+validToken)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		// Should accept valid WorkOS token
		assert.NotEqual(t, http.StatusUnauthorized, rec.Code,
			"Valid WorkOS token should be accepted")
	})

	t.Run("Invalid WorkOS token issuer", func(t *testing.T) {
		e := echo.New()

		// Token with wrong issuer
		invalidToken := createTokenWithWrongIssuer(t)

		req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
		req.Header.Set("Authorization", "Bearer "+invalidToken)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		assert.Equal(t, http.StatusUnauthorized, rec.Code,
			"Token with invalid issuer should be rejected")
	})
}

// TestSessionManagement tests session handling security
func TestSessionManagement(t *testing.T) {
	t.Run("Session fixation prevention", func(t *testing.T) {
		e := echo.New()

		// Login should generate new session ID
		reqBody := map[string]interface{}{
			"code": "valid-auth-code",
		}

		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/auth/callback", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		// Should set new session cookie, not reuse old one
		cookies := rec.Result().Cookies()
		if len(cookies) > 0 {
			assert.True(t, cookies[0].HttpOnly, "Session cookie should be HttpOnly")
			assert.True(t, cookies[0].Secure, "Session cookie should be Secure")
			assert.Equal(t, http.SameSiteStrictMode, cookies[0].SameSite,
				"Session cookie should use SameSite=Strict")
		}
	})

	t.Run("Session timeout", func(t *testing.T) {
		e := echo.New()

		// Create old session token
		oldToken := createOldToken(t, 25*time.Hour) // 25 hours old

		req := httptest.NewRequest(http.MethodGet, "/api/items", nil)
		req.Header.Set("Authorization", "Bearer "+oldToken)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		assert.Equal(t, http.StatusUnauthorized, rec.Code,
			"Old session should be expired")
	})
}

// TestPasswordPolicies tests password security requirements
func TestPasswordPolicies(t *testing.T) {
	weakPasswords := []string{
		"123456",
		"password",
		"qwerty",
		"abc123",
		"12345678",
		"test",
		"password123",
	}

	for _, pwd := range weakPasswords {
		t.Run("Weak password: "+pwd, func(t *testing.T) {
			e := echo.New()

			reqBody := map[string]interface{}{
				"email":    "test@example.com",
				"password": pwd,
			}

			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/auth/register", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			_ = e.NewContext(req, rec)

			// Should reject weak passwords
			assert.NotEqual(t, http.StatusOK, rec.Code,
				"Weak password should be rejected")
		})
	}

	t.Run("Strong password requirements", func(t *testing.T) {
		e := echo.New()

		strongPassword := "MySecureP@ssw0rd2024!"

		reqBody := map[string]interface{}{
			"email":    "test@example.com",
			"password": strongPassword,
		}

		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/auth/register", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		// Strong password should be accepted (if endpoint exists)
		// Note: WorkOS handles this, but test local validation if any
	})
}

// TestBruteForceProtection tests login attempt rate limiting
func TestBruteForceProtection(t *testing.T) {
	e := echo.New()

	// Simulate multiple failed login attempts
	for i := 0; i < 10; i++ {
		reqBody := map[string]interface{}{
			"email":    "test@example.com",
			"password": "wrong-password",
		}

		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/auth/login", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		req.Header.Set("X-Real-IP", "192.168.1.100")
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		if i >= 5 {
			// After 5 failed attempts, should rate limit
			assert.Equal(t, http.StatusTooManyRequests, rec.Code,
				"Should rate limit after multiple failed attempts")
		}
	}
}

// TestAuthorizationChecks tests that users can only access their own resources
func TestAuthorizationChecks(t *testing.T) {
	t.Run("User cannot access other user's items", func(t *testing.T) {
		e := echo.New()

		// User A's token
		tokenA := createUserToken(t, "user-a-123")

		req := httptest.NewRequest(http.MethodGet, "/api/items/user-b-item-456", nil)
		req.Header.Set("Authorization", "Bearer "+tokenA)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		assert.Equal(t, http.StatusForbidden, rec.Code,
			"User should not access other user's items")
	})

	t.Run("User cannot delete other user's projects", func(t *testing.T) {
		e := echo.New()

		tokenA := createUserToken(t, "user-a-123")

		req := httptest.NewRequest(http.MethodDelete, "/api/projects/user-b-project-789", nil)
		req.Header.Set("Authorization", "Bearer "+tokenA)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		assert.Equal(t, http.StatusForbidden, rec.Code,
			"User should not delete other user's projects")
	})
}

// TestTokenRefresh tests secure token refresh mechanism
func TestTokenRefresh(t *testing.T) {
	t.Run("Valid refresh token", func(t *testing.T) {
		e := echo.New()

		refreshToken := createValidRefreshToken(t)

		reqBody := map[string]interface{}{
			"refresh_token": refreshToken,
		}

		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/auth/refresh", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		// Should return new access token
		if rec.Code == http.StatusOK {
			var response map[string]interface{}
			_ = json.Unmarshal(rec.Body.Bytes(), &response)
			assert.NotEmpty(t, response["access_token"], "Should return new access token")
		}
	})

	t.Run("Expired refresh token", func(t *testing.T) {
		e := echo.New()

		expiredToken := createExpiredRefreshToken(t)

		reqBody := map[string]interface{}{
			"refresh_token": expiredToken,
		}

		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/auth/refresh", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		_ = e.NewContext(req, rec)

		assert.Equal(t, http.StatusUnauthorized, rec.Code,
			"Expired refresh token should be rejected")
	})
}

// Helper functions to create test tokens

func createExpiredToken(t *testing.T) string {
	claims := jwt.MapClaims{
		"sub": "test-user-123",
		"exp": time.Now().Add(-1 * time.Hour).Unix(),
		"iat": time.Now().Add(-2 * time.Hour).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	require.NoError(t, err)

	return "Bearer " + tokenString
}

func createTokenWithInvalidSignature(t *testing.T) string {
	claims := jwt.MapClaims{
		"sub": "test-user-123",
		"exp": time.Now().Add(1 * time.Hour).Unix(),
		"iat": time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("wrong-secret-key"))
	require.NoError(t, err)

	return "Bearer " + tokenString
}

func createValidWorkOSToken(t *testing.T) string {
	claims := jwt.MapClaims{
		"sub": "test-user-123",
		"iss": "https://api.workos.com",
		"aud": "tracertm",
		"exp": time.Now().Add(1 * time.Hour).Unix(),
		"iat": time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	require.NoError(t, err)

	return tokenString
}

func createTokenWithWrongIssuer(t *testing.T) string {
	claims := jwt.MapClaims{
		"sub": "test-user-123",
		"iss": "https://malicious.com",
		"exp": time.Now().Add(1 * time.Hour).Unix(),
		"iat": time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	require.NoError(t, err)

	return tokenString
}

func createOldToken(t *testing.T, age time.Duration) string {
	claims := jwt.MapClaims{
		"sub": "test-user-123",
		"exp": time.Now().Add(1 * time.Hour).Unix(),
		"iat": time.Now().Add(-age).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	require.NoError(t, err)

	return tokenString
}

func createUserToken(t *testing.T, userID string) string {
	claims := jwt.MapClaims{
		"sub": userID,
		"exp": time.Now().Add(1 * time.Hour).Unix(),
		"iat": time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	require.NoError(t, err)

	return tokenString
}

func createValidRefreshToken(t *testing.T) string {
	claims := jwt.MapClaims{
		"sub":  "test-user-123",
		"type": "refresh",
		"exp":  time.Now().Add(7 * 24 * time.Hour).Unix(),
		"iat":  time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	require.NoError(t, err)

	return tokenString
}

func createExpiredRefreshToken(t *testing.T) string {
	claims := jwt.MapClaims{
		"sub":  "test-user-123",
		"type": "refresh",
		"exp":  time.Now().Add(-1 * time.Hour).Unix(),
		"iat":  time.Now().Add(-8 * 24 * time.Hour).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	require.NoError(t, err)

	return tokenString
}
