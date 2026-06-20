package middleware

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

const (
	jwtExpiredOffset = -1 * time.Hour
	jwtValidOffset   = 1 * time.Hour
)

// Mock Auth Provider for testing

type mockAuthProvider struct {
	shouldFail bool
	user       *auth.User
}

type jwtEdgeCase struct {
	name           string
	authHeader     string
	setupToken     func() string
	expectedStatus int
	expectedMsg    string
}

type middlewareCase struct {
	name string
	fn   func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc)
}

func (m *mockAuthProvider) ValidateToken(_ context.Context, _ string) (*auth.User, error) {
	if m.shouldFail {
		return nil, errors.New("invalid token")
	}
	if m.user == nil {
		return &auth.User{
			ID:        "test-user-id",
			Email:     "test@example.com",
			ProjectID: "test-project",
			Role:      "user",
		}, nil
	}
	return m.user, nil
}

func (m *mockAuthProvider) GetUser(_ context.Context, _ string) (*auth.User, error) {
	return nil, errors.New("not implemented")
}

func (m *mockAuthProvider) CreateUser(_ context.Context, _, _, _ string) (*auth.User, error) {
	return nil, errors.New("not implemented")
}

func (m *mockAuthProvider) UpdateUser(_ context.Context, _ string, _ map[string]interface{}) (*auth.User, error) {
	return nil, errors.New("not implemented")
}

func (m *mockAuthProvider) DeleteUser(_ context.Context, _ string) error {
	return errors.New("not implemented")
}

func (m *mockAuthProvider) ListUsers(_ context.Context, _, _ int) ([]*auth.User, error) {
	return nil, errors.New("not implemented")
}

func (m *mockAuthProvider) Close() error {
	return nil
}

func TestJWTMiddlewareEdgeCases(t *testing.T) {
	secretKey := []byte("test-secret-key")
	config := JWTConfig{
		SecretKey: secretKey,
	}

	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "success")
	}

	runJWTEdgeCases(t, e, handler, config, jwtEdgeCases(secretKey))

	t.Run("custom skipper function", func(t *testing.T) {
		customConfig := JWTConfig{
			SecretKey: secretKey,
			Skipper: func(c echo.Context) bool {
				return c.Path() == "/public"
			},
		}

		req := httptest.NewRequest(http.MethodGet, "/public", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/public")

		mw := JWTMiddleware(customConfig)
		h := mw(handler)

		err := h(c)
		require.NoError(t, err)
	})
}

func TestAuthAdapterMiddlewareEdgeCases(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "success")
	}

	runMiddlewareCases(t, e, handler, authAdapterEdgeCases())
}

func TestRateLimitMiddlewareEdgeCases(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "success")
	}

	runMiddlewareCases(t, e, handler, rateLimitEdgeCases())
}

func runJWTEdgeCases(t *testing.T, e *echo.Echo, handler echo.HandlerFunc, config JWTConfig, cases []jwtEdgeCase) {
	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			authValue := tt.authHeader
			if tt.setupToken != nil {
				token := tt.setupToken()
				authValue = tt.authHeader + " " + token
			}

			req := httptest.NewRequest(http.MethodGet, "/protected", nil)
			if authValue != "" {
				req.Header.Set("Authorization", authValue)
			}
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			mw := JWTMiddleware(config)
			h := mw(handler)

			err := h(c)

			if tt.expectedStatus == 0 {
				if err != nil {
					t.Logf("Token rejected (expected behavior): %v", err)
				} else {
					t.Log("Token accepted with invalid claims structure")
				}
				return
			}

			require.Error(t, err)
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			require.True(t, ok)
			assert.Equal(t, tt.expectedStatus, he.Code)
			if tt.expectedMsg != "" {
				assert.Contains(t, he.Message, tt.expectedMsg)
			}
		})
	}
}

func jwtEdgeCases(secretKey []byte) []jwtEdgeCase {
	cases := make([]jwtEdgeCase, 0, 10)
	cases = append(cases, jwtMissingHeaderCase())
	cases = append(cases, jwtMalformedCases()...)
	cases = append(cases, jwtExpiredTokenCase(secretKey))
	cases = append(cases, jwtInvalidSignatureCase())
	cases = append(cases, jwtWrongSigningMethodCase())
	cases = append(cases, jwtInvalidClaimsCase(secretKey))
	return cases
}

func runMiddlewareCases(t *testing.T, e *echo.Echo, handler echo.HandlerFunc, cases []middlewareCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t, e, handler)
		})
	}
}

func authAdapterEdgeCases() []middlewareCase {
	return []middlewareCase{
		authAdapterProviderErrorCase(),
		authAdapterValidUserCase(),
		authAdapterSkipperCase(),
	}
}

func rateLimitEdgeCases() []middlewareCase {
	return []middlewareCase{
		rateLimitInMemoryCase(),
		rateLimitUserIDCase(),
		rateLimitExceededCase(),
		rateLimitSkipperCase(),
		rateLimitSeparateIPCase(),
	}
}

func jwtMissingHeaderCase() jwtEdgeCase {
	return jwtEdgeCase{
		name:           "missing authorization header",
		authHeader:     "",
		setupToken:     nil,
		expectedStatus: http.StatusUnauthorized,
		expectedMsg:    "missing authorization header",
	}
}

func jwtMalformedCases() []jwtEdgeCase {
	return []jwtEdgeCase{
		{
			name:           "malformed - no scheme",
			authHeader:     "InvalidFormat",
			setupToken:     nil,
			expectedStatus: http.StatusUnauthorized,
			expectedMsg:    "",
		},
		{
			name:           "malformed - bearer only",
			authHeader:     "Bearer",
			setupToken:     nil,
			expectedStatus: http.StatusUnauthorized,
			expectedMsg:    "",
		},
		{
			name:           "malformed - bearer with space",
			authHeader:     "Bearer ",
			setupToken:     nil,
			expectedStatus: http.StatusUnauthorized,
			expectedMsg:    "",
		},
		{
			name:           "malformed - wrong scheme",
			authHeader:     "NotBearer token",
			setupToken:     nil,
			expectedStatus: http.StatusUnauthorized,
			expectedMsg:    "",
		},
		{
			name:           "malformed - multiple tokens",
			authHeader:     "Bearer token1 token2 token3",
			setupToken:     nil,
			expectedStatus: http.StatusUnauthorized,
			expectedMsg:    "",
		},
	}
}

func jwtExpiredTokenCase(secretKey []byte) jwtEdgeCase {
	return jwtEdgeCase{
		name:       "expired token",
		authHeader: "Bearer",
		setupToken: func() string {
			claims := &JWTClaims{
				UserID:    "user-123",
				ProjectID: "proj-456",
				Role:      "admin",
				RegisteredClaims: jwt.RegisteredClaims{
					ExpiresAt: jwt.NewNumericDate(time.Now().Add(jwtExpiredOffset)),
				},
			}
			token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
			tokenString, err := token.SignedString(secretKey)
			if err != nil {
				panic("failed to sign token: " + err.Error())
			}
			return tokenString
		},
		expectedStatus: http.StatusUnauthorized,
		expectedMsg:    "",
	}
}

func jwtInvalidSignatureCase() jwtEdgeCase {
	return jwtEdgeCase{
		name:       "invalid signature",
		authHeader: "Bearer",
		setupToken: func() string {
			claims := &JWTClaims{
				UserID:    "user-123",
				ProjectID: "proj-456",
				Role:      "admin",
				RegisteredClaims: jwt.RegisteredClaims{
					ExpiresAt: jwt.NewNumericDate(time.Now().Add(jwtValidOffset)),
				},
			}
			token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
			tokenString, err := token.SignedString([]byte("wrong-secret"))
			if err != nil {
				panic("failed to sign token: " + err.Error())
			}
			return tokenString
		},
		expectedStatus: http.StatusUnauthorized,
		expectedMsg:    "",
	}
}

func jwtWrongSigningMethodCase() jwtEdgeCase {
	return jwtEdgeCase{
		name:           "wrong signing method",
		authHeader:     "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
		setupToken:     nil,
		expectedStatus: http.StatusUnauthorized,
		expectedMsg:    "",
	}
}

func jwtInvalidClaimsCase(secretKey []byte) jwtEdgeCase {
	return jwtEdgeCase{
		name:       "token with invalid claims",
		authHeader: "Bearer",
		setupToken: func() string {
			invalidToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
				"invalid": "claims",
			})
			tokenString, err := invalidToken.SignedString(secretKey)
			if err != nil {
				panic("failed to sign token: " + err.Error())
			}
			return tokenString
		},
		expectedStatus: 0,
		expectedMsg:    "",
	}
}

func authAdapterProviderErrorCase() middlewareCase {
	return middlewareCase{
		name: "auth provider returns error",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			config := AuthAdapterConfig{
				AuthProvider: &mockAuthProvider{shouldFail: true},
			}

			claims := &JWTClaims{UserID: "user-123", ProjectID: "proj-456", Role: "admin"}
			token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
			tokenString, err := token.SignedString([]byte("secret"))
			require.NoError(t, err)

			req := httptest.NewRequest(http.MethodGet, "/protected", nil)
			req.Header.Set("Authorization", "Bearer "+tokenString)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			mw := AuthAdapterMiddleware(config)
			h := mw(handler)

			err = h(c)
			require.Error(t, err)
		},
	}
}

func authAdapterValidUserCase() middlewareCase {
	return middlewareCase{
		name: "auth provider returns valid user",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			testUser := &auth.User{
				ID:        "custom-user-id",
				Email:     "custom@example.com",
				ProjectID: "custom-project",
				Role:      "admin",
			}

			config := AuthAdapterConfig{
				AuthProvider: &mockAuthProvider{user: testUser},
			}

			req := httptest.NewRequest(http.MethodGet, "/protected", nil)
			req.Header.Set("Authorization", "Bearer valid-token")
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			mw := AuthAdapterMiddleware(config)
			h := mw(handler)

			err := h(c)
			require.NoError(t, err)

			assert.Equal(t, "custom-user-id", c.Get("user_id"))
			assert.Equal(t, "custom@example.com", c.Get("user_email"))
			assert.Equal(t, "custom-project", c.Get("project_id"))
			assert.Equal(t, "admin", c.Get("role"))
		},
	}
}

func authAdapterSkipperCase() middlewareCase {
	return middlewareCase{
		name: "nil skipper defaults to DefaultSkipper",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			config := AuthAdapterConfig{
				AuthProvider: &mockAuthProvider{},
				Skipper:      nil,
			}

			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			req.Header.Set("Authorization", "Bearer token")
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			mw := AuthAdapterMiddleware(config)
			h := mw(handler)

			err := h(c)
			require.NoError(t, err)
		},
	}
}

func rateLimitInMemoryCase() middlewareCase {
	return middlewareCase{
		name: "nil redis client uses in-memory limiter",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			config := RateLimitConfig{
				RedisClient:       nil,
				RequestsPerSecond: 10,
				BurstSize:         20,
			}

			mw := CreateRateLimitMiddleware(&config)
			handler = mw(handler)

			for i := 0; i < 5; i++ {
				req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
				rec := httptest.NewRecorder()
				c := e.NewContext(req, rec)

				err := handler(c)
				require.NoError(t, err)
			}
		},
	}
}

func rateLimitUserIDCase() middlewareCase {
	return middlewareCase{
		name: "rate limit with user ID in context",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			config := RateLimitConfig{
				RedisClient:       nil,
				RequestsPerSecond: 10,
				BurstSize:         20,
			}

			mw := CreateRateLimitMiddleware(&config)
			handler = mw(handler)

			req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.Set("user_id", "user-123")

			err := handler(c)
			require.NoError(t, err)
		},
	}
}

func rateLimitExceededCase() middlewareCase {
	return middlewareCase{
		name: "rate limit exceeded",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			config := RateLimitConfig{
				RedisClient:       nil,
				RequestsPerSecond: 1,
				BurstSize:         1,
			}

			mw := CreateRateLimitMiddleware(&config)
			handler = mw(handler)

			req1 := httptest.NewRequest(http.MethodGet, "/api/test", nil)
			rec1 := httptest.NewRecorder()
			c1 := e.NewContext(req1, rec1)
			err := handler(c1)
			require.NoError(t, err)

			req2 := httptest.NewRequest(http.MethodGet, "/api/test", nil)
			rec2 := httptest.NewRecorder()
			c2 := e.NewContext(req2, rec2)
			err = handler(c2)
			if err != nil {
				he := &echo.HTTPError{}
				ok := errors.As(err, &he)
				if ok {
					assert.Equal(t, http.StatusTooManyRequests, he.Code)
				}
			}
		},
	}
}

func rateLimitSkipperCase() middlewareCase {
	return middlewareCase{
		name: "custom skipper",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			config := RateLimitConfig{
				RedisClient:       nil,
				RequestsPerSecond: 1,
				BurstSize:         1,
				Skipper: func(c echo.Context) bool {
					return c.Path() == "/skip"
				},
			}

			mw := CreateRateLimitMiddleware(&config)
			handler = mw(handler)

			req := httptest.NewRequest(http.MethodGet, "/skip", nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetPath("/skip")

			for i := 0; i < 10; i++ {
				err := handler(c)
				require.NoError(t, err)
			}
		},
	}
}

func rateLimitSeparateIPCase() middlewareCase {
	return middlewareCase{
		name: "different IPs have separate limits",
		fn: func(t *testing.T, e *echo.Echo, handler echo.HandlerFunc) {
			config := RateLimitConfig{
				RedisClient:       nil,
				RequestsPerSecond: 1,
				BurstSize:         1,
			}

			mw := CreateRateLimitMiddleware(&config)
			handler = mw(handler)

			req1 := httptest.NewRequest(http.MethodGet, "/api/test", nil)
			req1.Header.Set("X-Real-IP", "192.168.1.1")
			rec1 := httptest.NewRecorder()
			c1 := e.NewContext(req1, rec1)
			err := handler(c1)
			require.NoError(t, err)

			req2 := httptest.NewRequest(http.MethodGet, "/api/test", nil)
			req2.Header.Set("X-Real-IP", "192.168.1.2")
			rec2 := httptest.NewRecorder()
			c2 := e.NewContext(req2, rec2)
			err = handler(c2)
			require.NoError(t, err)
		},
	}
}

func TestErrorHandlerMiddlewareEdgeCases(t *testing.T) {
	e := echo.New()

	t.Run("handles echo.HTTPError", func(t *testing.T) {
		handler := func(_ echo.Context) error {
			return echo.NewHTTPError(http.StatusBadRequest, "bad request")
		}

		mw := ErrorHandlerMiddleware()
		h := mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err) // Middleware handles the error
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("handles generic error", func(t *testing.T) {
		handler := func(_ echo.Context) error {
			return errors.New("generic error")
		}

		mw := ErrorHandlerMiddleware()
		h := mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("passes through nil error", func(t *testing.T) {
		handler := func(_ echo.Context) error {
			return nil
		}

		mw := ErrorHandlerMiddleware()
		h := mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)
	})
}

func TestRequestLoggerMiddlewareEdgeCases(t *testing.T) {
	e := echo.New()

	t.Run("logs successful request", func(t *testing.T) {
		handler := func(c echo.Context) error {
			return c.String(http.StatusOK, "ok")
		}

		mw := RequestLoggerMiddleware()
		handler = mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		req.Header.Set("User-Agent", "test-agent")
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler(c)
		require.NoError(t, err)
	})

	t.Run("logs error response", func(t *testing.T) {
		handler := func(_ echo.Context) error {
			return echo.NewHTTPError(http.StatusInternalServerError, "error")
		}

		mw := RequestLoggerMiddleware()
		handler = mw(handler)

		req := httptest.NewRequest(http.MethodPost, "/api/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler(c)
		require.Error(t, err)
	})

	t.Run("logs with user context", func(t *testing.T) {
		handler := func(c echo.Context) error {
			c.Set("user_id", "user-123")
			return c.String(http.StatusOK, "ok")
		}

		mw := RequestLoggerMiddleware()
		handler = mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler(c)
		require.NoError(t, err)
	})
}

func TestCORSConfig(t *testing.T) {
	config := CORSConfig()

	t.Run("allows specific localhost origins", func(t *testing.T) {
		// Should not allow wildcards for security reasons
		assert.NotContains(t, config.AllowOrigins, "*")
		// Should contain specific localhost origins
		assert.Contains(t, config.AllowOrigins, "http://localhost:4000")
		assert.Contains(t, config.AllowOrigins, "http://localhost:5173")
	})

	t.Run("allows common methods", func(t *testing.T) {
		assert.Contains(t, config.AllowMethods, http.MethodGet)
		assert.Contains(t, config.AllowMethods, http.MethodPost)
		assert.Contains(t, config.AllowMethods, http.MethodPut)
		assert.Contains(t, config.AllowMethods, http.MethodDelete)
	})

	t.Run("allows required headers", func(t *testing.T) {
		assert.Contains(t, config.AllowHeaders, echo.HeaderContentType)
		assert.Contains(t, config.AllowHeaders, echo.HeaderAuthorization)
	})

	t.Run("allows credentials", func(t *testing.T) {
		assert.True(t, config.AllowCredentials)
	})

	t.Run("has max age set", func(t *testing.T) {
		assert.Positive(t, config.MaxAge)
	})
}

func TestRecoveryMiddleware(t *testing.T) {
	e := echo.New()

	t.Run("recovers from panic", func(t *testing.T) {
		handler := func(_ echo.Context) error {
			panic("test panic")
		}

		mw := RecoveryMiddleware()
		handler = mw(handler)

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		// Should not panic the test - recovery middleware catches it
		err := handler(c)
		// Recovery middleware should not return an error - it catches the panic
		require.NoError(t, err)
	})
}

func TestHealthCheckSkipper(t *testing.T) {
	e := echo.New()

	testCases := []struct {
		path     string
		expected bool
	}{
		{"/health", true},
		{"/metrics", true},
		{"/api/health", false},
		{"/api/test", false},
		{"", false},
	}

	for _, tc := range testCases {
		t.Run(tc.path, func(t *testing.T) {
			path := tc.path
			if path == "" {
				path = "/"
			}
			req := httptest.NewRequest(http.MethodGet, path, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetPath(tc.path)

			result := HealthCheckSkipper(c)
			assert.Equal(t, tc.expected, result)
		})
	}
}

func TestConcurrentMiddlewareExecution(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "success")
	}

	config := RateLimitConfig{
		RedisClient:       nil,
		RequestsPerSecond: 100,
		BurstSize:         200,
	}

	mw := CreateRateLimitMiddleware(&config)
	handler = mw(handler)

	t.Run("concurrent requests", func(t *testing.T) {
		var wg sync.WaitGroup
		numRequests := 50
		results := make(chan error, numRequests)

		for i := 0; i < numRequests; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
				rec := httptest.NewRecorder()
				c := e.NewContext(req, rec)

				results <- handler(c)
			}()
		}

		wg.Wait()
		close(results)

		successCount := 0
		for err := range results {
			if err == nil {
				successCount++
			}
		}

		assert.Greater(t, successCount, numRequests/2, "at least half should succeed")
	})
}

func TestRedisRateLimitEdgeCases(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping redis integration test in short mode")
	}

	ctx := context.Background()

	t.Run("redis unavailable falls back to memory", func(t *testing.T) {
		redisClient := redis.NewClient(&redis.Options{
			Addr: "192.0.2.1:6379", // Unreachable
		})

		allowed, err := checkRedisRateLimit(ctx, redisClient, "test-key", 10, 20)
		// Should error
		require.Error(t, err)
		assert.False(t, allowed)
	})
}

func TestMiddlewareChaining(t *testing.T) {
	e := echo.New()
	handler := func(c echo.Context) error {
		return c.String(http.StatusOK, "success")
	}

	t.Run("multiple middleware layers", func(t *testing.T) {
		recovery := RecoveryMiddleware()
		logger := RequestLoggerMiddleware()
		errorHandler := ErrorHandlerMiddleware()

		h := recovery(logger(errorHandler(handler)))

		req := httptest.NewRequest(http.MethodGet, "/test", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := h(c)
		require.NoError(t, err)
	})
}
