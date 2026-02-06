//go:build !integration && !e2e

package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test constants
const (
	testSecurePassword      = "SecurePassword123!"
	authTestSessionTTL      = 24 * time.Hour
	authTestShortSessionTTL = 1 * time.Hour
	authTestTTLMinuteute    = 59 * time.Minute
	authTestSleep           = 100 * time.Millisecond
)

// MockAuthProvider implements auth.Provider for testing
type MockAuthProvider struct {
	users map[string]*auth.User
}

type closeable interface {
	Close() error
}

func closeWithRequire(t *testing.T, c closeable) {
	t.Helper()
	require.NoError(t, c.Close())
}

func NewMockAuthProvider() *MockAuthProvider {
	return &MockAuthProvider{
		users: make(map[string]*auth.User),
	}
}

func (m *MockAuthProvider) ValidateToken(ctx context.Context, token string) (*auth.User, error) {
	// Parse JWT and extract user ID
	claims := jwt.MapClaims{}
	_, err := jwt.ParseWithClaims(token, claims, func(_ *jwt.Token) (interface{}, error) {
		return []byte("test-secret"), nil
	})
	if err != nil {
		return nil, err
	}

	userID, ok := claims["sub"].(string)
	if !ok {
		return nil, errors.New("invalid user ID in token")
	}

	return m.GetUser(ctx, userID)
}

func (m *MockAuthProvider) GetUser(_ context.Context, userID string) (*auth.User, error) {
	if user, ok := m.users[userID]; ok {
		return user, nil
	}
	return nil, errors.New("user not found")
}

func (m *MockAuthProvider) CreateUser(_ context.Context, email, _ string, name string) (*auth.User, error) {
	user := &auth.User{
		ID:       fmt.Sprintf("user_%d", time.Now().UnixNano()),
		Email:    email,
		Name:     name,
		Role:     "user",
		Metadata: make(map[string]interface{}),
	}
	m.users[user.ID] = user
	return user, nil
}

func (m *MockAuthProvider) UpdateUser(_ context.Context, userID string, _ map[string]interface{}) (*auth.User, error) {
	user, ok := m.users[userID]
	if !ok {
		return nil, errors.New("user not found")
	}
	return user, nil
}

func (m *MockAuthProvider) DeleteUser(_ context.Context, userID string) error {
	delete(m.users, userID)
	return nil
}

func (m *MockAuthProvider) ListUsers(_ context.Context, _ int, _ int) ([]*auth.User, error) {
	users := make([]*auth.User, 0, len(m.users))
	for _, user := range m.users {
		users = append(users, user)
	}
	return users, nil
}

func (m *MockAuthProvider) Close() error {
	return nil
}

type authHandlerTestEnv struct {
	handler     *AuthHandler
	redisClient *redis.Client
	echo        *echo.Echo
	close       func()
}

type authRegisterCase struct {
	name             string
	requestBody      string
	expectedStatus   int
	validateResponse func(t *testing.T, body []byte)
}

func newAuthHandlerTestEnv(t *testing.T, sessionTTL time.Duration, isProduction bool) *authHandlerTestEnv {
	t.Helper()
	miniredis, err := NewMiniredis()
	if err != nil {
		t.Fatalf("Failed to create miniredis: %v", err)
	}

	redisClient := redis.NewClient(&redis.Options{
		Addr: miniredis.Addr(),
	})

	mockAuthProvider := NewMockAuthProvider()
	authHandler := NewAuthHandler(
		mockAuthProvider,
		redisClient,
		"test-secret",
		sessionTTL,
		isProduction,
	)

	closeFn := func() {
		closeWithRequire(t, miniredis)
		closeWithRequire(t, redisClient)
	}

	return &authHandlerTestEnv{
		handler:     authHandler,
		redisClient: redisClient,
		echo:        echo.New(),
		close:       closeFn,
	}
}

func seedAuthUser(t *testing.T, handler *AuthHandler, email, password, name string) *auth.User {
	t.Helper()

	hashedPassword, err := handler.passwordHasher.HashPassword(password)
	require.NoError(t, err)

	user := &auth.User{
		ID:       fmt.Sprintf("user_%d", time.Now().UnixNano()),
		Email:    email,
		Name:     name,
		Role:     "user",
		Metadata: make(map[string]interface{}),
	}

	err = handler.storeUserRecord(context.Background(), user, hashedPassword)
	require.NoError(t, err)

	return user
}

// TestAuthHandlerLogin tests the Login endpoint
func TestAuthHandlerLogin(t *testing.T) {
	env := newAuthHandlerTestEnv(t, authTestSessionTTL, false)
	defer env.close()

	runAuthLoginCases(t, env.handler, env.echo)
}

// TestAuthHandlerRegister tests the Register endpoint with password hashing
func TestAuthHandlerRegister(t *testing.T) {
	env := newAuthHandlerTestEnv(t, authTestSessionTTL, false)
	defer env.close()

	for _, tt := range authRegisterTestCases() {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/register",
				strings.NewReader(tt.requestBody))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()

			c := env.echo.NewContext(req, rec)
			err := env.handler.Register(c)

			require.NoError(t, err)
			assert.Equal(t, tt.expectedStatus, rec.Code)

			if tt.validateResponse != nil {
				tt.validateResponse(t, rec.Body.Bytes())
			}
		})
	}
}

// TestPasswordHashingIntegration tests password hashing integration in auth flow
func TestPasswordHashingIntegration(t *testing.T) {
	hasher := auth.NewPasswordHasher()
	validator := auth.NewPasswordStrengthValidator()

	// Test password hashing and verification
	t.Run("password hashing and verification", func(t *testing.T) {
		password := testSecurePassword

		// Verify password meets strength requirements
		validationErrors := validator.ValidatePassword(password)
		assert.Empty(t, validationErrors)

		// Hash the password
		hash, err := hasher.HashPassword(password)
		require.NoError(t, err)
		assert.NotEmpty(t, hash)

		// Verify correct password
		isValid := hasher.VerifyPassword(hash, password)
		assert.True(t, isValid)

		// Verify incorrect password
		isValid = hasher.VerifyPassword(hash, "WrongPassword456!")
		assert.False(t, isValid)
	})

	// Test that hashing fails with empty password
	t.Run("hashing fails with empty password", func(t *testing.T) {
		hash, err := hasher.HashPassword("")
		assert.Error(t, err)
		assert.Empty(t, hash)
	})

	// Test that verification fails with empty password
	t.Run("verification fails with empty password", func(t *testing.T) {
		password := testSecurePassword
		hash, _ := hasher.HashPassword(password)

		isValid := hasher.VerifyPassword(hash, "")
		assert.False(t, isValid)
	})

	// Test that verification fails with empty hash
	t.Run("verification fails with empty hash", func(t *testing.T) {
		isValid := hasher.VerifyPassword("", testSecurePassword)
		assert.False(t, isValid)
	})

	// Test that different passwords produce different hashes
	t.Run("different passwords produce different hashes", func(t *testing.T) {
		password1 := "SecurePassword123!"
		password2 := "DifferentPassword456!"

		hash1, _ := hasher.HashPassword(password1)
		hash2, _ := hasher.HashPassword(password2)

		assert.NotEqual(t, hash1, hash2)
		assert.True(t, hasher.VerifyPassword(hash1, password1))
		assert.False(t, hasher.VerifyPassword(hash1, password2))
	})

	// Test bcrypt format validation
	t.Run("hash uses bcrypt format", func(t *testing.T) {
		password := "SecurePassword123!"
		hash, _ := hasher.HashPassword(password)

		// Bcrypt hashes start with $2a$ or $2b$
		assert.True(t, strings.HasPrefix(hash, "$2a$") || strings.HasPrefix(hash, "$2b$"))
	})
}

// TestAuthHandlerSessionStorage tests session storage in Redis
func TestAuthHandlerSessionStorage(t *testing.T) {
	miniredis, err := NewMiniredis()
	if err != nil {
		t.Fatalf("Failed to create miniredis: %v", err)
	}
	defer closeWithRequire(t, miniredis)

	redisClient := redis.NewClient(&redis.Options{
		Addr: miniredis.Addr(),
	})
	defer closeWithRequire(t, redisClient)

	mockAuthProvider := NewMockAuthProvider()
	authHandler := NewAuthHandler(
		mockAuthProvider,
		redisClient,
		"test-secret",
		authTestShortSessionTTL,
		false,
	)

	ctx := context.Background()

	// Create a session
	user := &auth.User{
		ID:        "user123",
		Email:     "test@example.com",
		Name:      "Test User",
		ProjectID: "project123",
		Role:      "admin",
		Metadata:  make(map[string]interface{}),
	}

	token, err := authHandler.createSessionToken(ctx, user)
	require.NoError(t, err)
	assert.NotEmpty(t, token)

	// Verify session is stored in Redis
	sessionKey := "session:" + user.ID
	sessionJSON, err := redisClient.Get(ctx, sessionKey).Result()
	require.NoError(t, err)

	var sessionData SessionData
	err = json.Unmarshal([]byte(sessionJSON), &sessionData)
	require.NoError(t, err)
	assert.Equal(t, user.ID, sessionData.UserID)
	assert.Equal(t, user.Email, sessionData.Email)
	assert.Equal(t, user.ProjectID, sessionData.ProjectID)
}

// TestAuthHandlerRefresh tests the Refresh endpoint
func TestAuthHandlerRefresh(t *testing.T) {
	env := newAuthHandlerTestEnv(t, authTestShortSessionTTL, false)
	defer env.close()

	user, token := setupAuthRefreshSession(t, env.handler)

	runAuthRefreshCases(t, env.handler, env.echo, user, token)
}

// TestAuthHandlerLogout tests the Logout endpoint
func TestAuthHandlerLogout(t *testing.T) {
	env := newAuthHandlerTestEnv(t, authTestShortSessionTTL, false)
	defer env.close()

	user, token := setupAuthLogoutSession(t, env.handler, env.redisClient)

	runAuthLogoutCases(t, env.handler, env.echo, env.redisClient, user, token)
}

// TestAuthHandlerTokenValidation tests token validation
func TestAuthHandlerTokenValidation(t *testing.T) {
	miniredis, err := NewMiniredis()
	if err != nil {
		t.Fatalf("Failed to create miniredis: %v", err)
	}
	defer closeWithRequire(t, miniredis)

	redisClient := redis.NewClient(&redis.Options{
		Addr: miniredis.Addr(),
	})
	defer closeWithRequire(t, redisClient)

	mockAuthProvider := NewMockAuthProvider()
	authHandler := NewAuthHandler(
		mockAuthProvider,
		redisClient,
		"test-secret",
		authTestShortSessionTTL,
		false,
	)

	ctx := context.Background()

	// Create a valid token
	user := &auth.User{
		ID:        "user123",
		Email:     "test@example.com",
		Name:      "Test User",
		ProjectID: "project123",
		Role:      "user",
		Metadata:  make(map[string]interface{}),
	}

	token, err := authHandler.createSessionToken(ctx, user)
	require.NoError(t, err)

	// Test valid token validation
	t.Run("valid token", func(t *testing.T) {
		retrievedUser, err := authHandler.validateSessionToken(ctx, token)
		require.NoError(t, err)
		assert.Equal(t, user.ID, retrievedUser.ID)
		assert.Equal(t, user.Email, retrievedUser.Email)
	})

	// Test invalid token
	t.Run("invalid token", func(t *testing.T) {
		_, err := authHandler.validateSessionToken(ctx, "invalid-token")
		assert.Error(t, err)
	})

	// Test expired session
	t.Run("expired session", func(t *testing.T) {
		// Delete the session from Redis
		sessionKey := "session:" + user.ID
		redisClient.Del(ctx, sessionKey)

		// Try to validate the token
		_, err := authHandler.validateSessionToken(ctx, token)
		assert.Error(t, err)
	})
}

// TestAuthHandlerHttpOnlyCookie tests HttpOnly cookie handling
func TestAuthHandlerHttpOnlyCookie(t *testing.T) {
	miniredis, err := NewMiniredis()
	if err != nil {
		t.Fatalf("Failed to create miniredis: %v", err)
	}
	defer closeWithRequire(t, miniredis)

	redisClient := redis.NewClient(&redis.Options{
		Addr: miniredis.Addr(),
	})
	defer closeWithRequire(t, redisClient)

	mockAuthProvider := NewMockAuthProvider()
	authHandler := NewAuthHandler(
		mockAuthProvider,
		redisClient,
		"test-secret",
		authTestSessionTTL,
		true, // Production mode
	)

	e := echo.New()

	seedAuthUser(t, authHandler, "test@example.com", testSecurePassword, "Test User")

	// Test cookie in login response
	t.Run("secure cookie in login", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`{"email":"test@example.com","password":"SecurePassword123!"}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := authHandler.Login(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		// Check cookie properties
		cookies := rec.Result().Cookies()
		assert.NotEmpty(t, cookies)

		authCookie := findCookie(cookies, "auth_token")
		assert.NotNil(t, authCookie)
		assert.True(t, authCookie.HttpOnly)
		assert.True(t, authCookie.Secure) // Production mode
		assert.Equal(t, http.SameSiteStrictMode, authCookie.SameSite)
		assert.Equal(t, "/", authCookie.Path)
	})

	// Test non-production mode
	authHandler.isProduction = false
	t.Run("insecure cookie in dev mode", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`{"email":"test@example.com","password":"SecurePassword123!"}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := authHandler.Login(c)

		require.NoError(t, err)

		// Check cookie properties
		cookies := rec.Result().Cookies()
		authCookie := findCookie(cookies, "auth_token")
		assert.NotNil(t, authCookie)
		assert.True(t, authCookie.HttpOnly)
		assert.False(t, authCookie.Secure) // Dev mode
	})
}

// TestAuthHandlerSessionExtension tests session extension on refresh
func TestAuthHandlerSessionExtension(t *testing.T) {
	miniredis, err := NewMiniredis()
	if err != nil {
		t.Fatalf("Failed to create miniredis: %v", err)
	}
	defer closeWithRequire(t, miniredis)

	redisClient := redis.NewClient(&redis.Options{
		Addr: miniredis.Addr(),
	})
	defer closeWithRequire(t, redisClient)

	mockAuthProvider := NewMockAuthProvider()
	sessionTTL := authTestShortSessionTTL
	authHandler := NewAuthHandler(
		mockAuthProvider,
		redisClient,
		"test-secret",
		sessionTTL,
		false,
	)

	ctx := context.Background()

	// Create initial session
	user := &auth.User{
		ID:        "user123",
		Email:     "test@example.com",
		Name:      "Test User",
		ProjectID: "project123",
		Role:      "user",
		Metadata:  make(map[string]interface{}),
	}

	_, err = authHandler.createSessionToken(ctx, user)
	require.NoError(t, err)

	// Get original session TTL
	sessionKey := "session:" + user.ID
	ttlBefore := redisClient.TTL(ctx, sessionKey).Val()

	// Wait a bit
	time.Sleep(authTestSleep)

	// Extend session
	_, err = authHandler.extendSession(ctx, user)
	require.NoError(t, err)

	// Get new session TTL
	ttlAfter := redisClient.TTL(ctx, sessionKey).Val()

	// TTL should be greater after extension (or at least close to the original)
	assert.Greater(t, ttlAfter, ttlBefore)
	assert.Greater(t, ttlAfter, authTestTTLMinuteute) // Should be close to 1 hour
}

// TestAuthHandlerGetUser tests the GetUser endpoint
func TestAuthHandlerGetUser(t *testing.T) {
	miniredis, err := NewMiniredis()
	if err != nil {
		t.Fatalf("Failed to create miniredis: %v", err)
	}
	defer closeWithRequire(t, miniredis)

	redisClient := redis.NewClient(&redis.Options{
		Addr: miniredis.Addr(),
	})
	defer closeWithRequire(t, redisClient)

	mockAuthProvider := NewMockAuthProvider()
	authHandler := NewAuthHandler(
		mockAuthProvider,
		redisClient,
		"test-secret",
		authTestShortSessionTTL,
		false,
	)

	e := echo.New()

	// Test with authenticated user
	t.Run("get authenticated user", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/auth/me", nil)
		rec := httptest.NewRecorder()

		user := &auth.User{
			ID:        "user123",
			Email:     "test@example.com",
			Name:      "Test User",
			ProjectID: "project123",
			Role:      "user",
		}

		c := e.NewContext(req, rec)
		c.Set("user", user)

		err := authHandler.GetUser(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp auth.User
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.Equal(t, user.ID, resp.ID)
		assert.Equal(t, user.Email, resp.Email)
	})

	// Test without authentication
	t.Run("get unauthenticated user", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/auth/me", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)

		err := authHandler.GetUser(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})
}

func runAuthLoginCases(t *testing.T, handler *AuthHandler, e *echo.Echo) {
	seedAuthUser(t, handler, "test@example.com", testSecurePassword, "Test User")

	t.Run("successful login", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`{"email":"test@example.com","password":"SecurePassword123!"}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Login(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp AuthResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.NotEmpty(t, resp.AccessToken)
		assert.Equal(t, resp.AccessToken, resp.Token)
		assert.NotNil(t, resp.User)
		assert.Equal(t, "test@example.com", resp.User.Email)
	})

	t.Run("missing email", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`{"password":"password123"}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Login(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("missing password", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`{"email":"test@example.com"}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Login(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("invalid json", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`invalid json`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Login(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("unknown user", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`{"email":"unknown@example.com","password":"SecurePassword123!"}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Login(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})

	t.Run("wrong password", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/login",
			strings.NewReader(`{"email":"test@example.com","password":"WrongPassword456!"}`))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Login(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})
}

func authRegisterTestCases() []authRegisterCase {
	cases := make([]authRegisterCase, 0, 9)
	cases = append(cases,
		authRegisterSuccessCase(),
		authRegisterWeakPasswordCase(),
	)
	cases = append(cases, authRegisterMissingComplexityCases()...)
	cases = append(cases, authRegisterMissingFieldCases()...)
	return cases
}

func authRegisterSuccessCase() authRegisterCase {
	return authRegisterCase{
		name:           "successful registration with strong password",
		requestBody:    `{"email":"newuser@example.com","password":"SecurePassword123!","name":"New User"}`,
		expectedStatus: http.StatusCreated,
		validateResponse: func(t *testing.T, body []byte) {
			var resp AuthResponse
			err := json.Unmarshal(body, &resp)
			require.NoError(t, err)
			assert.NotEmpty(t, resp.AccessToken)
			assert.Equal(t, resp.AccessToken, resp.Token)
			assert.NotNil(t, resp.User)
			assert.Equal(t, "newuser@example.com", resp.User.Email)
			assert.Equal(t, "New User", resp.User.Name)
		},
	}
}

func authRegisterWeakPasswordCase() authRegisterCase {
	return authRegisterCase{
		name:           "registration with weak password (too short)",
		requestBody:    `{"email":"user@example.com","password":"Weak1!","name":"User"}`,
		expectedStatus: http.StatusBadRequest,
		validateResponse: func(t *testing.T, body []byte) {
			var resp map[string]interface{}
			err := json.Unmarshal(body, &resp)
			require.NoError(t, err)
			assert.Contains(t, resp["error"], "strength requirements")
		},
	}
}

func authRegisterMissingComplexityCases() []authRegisterCase {
	return []authRegisterCase{
		{
			name:           "registration with password missing uppercase",
			requestBody:    `{"email":"user@example.com","password":"securepassword123!","name":"User"}`,
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "registration with password missing lowercase",
			requestBody:    `{"email":"user@example.com","password":"SECUREPASSWORD123!","name":"User"}`,
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "registration with password missing numbers",
			requestBody:    `{"email":"user@example.com","password":"SecurePassword!","name":"User"}`,
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "registration with password missing special characters",
			requestBody:    `{"email":"user@example.com","password":"SecurePassword123","name":"User"}`,
			expectedStatus: http.StatusBadRequest,
		},
	}
}

func authRegisterMissingFieldCases() []authRegisterCase {
	return []authRegisterCase{
		{
			name:           "registration with missing email",
			requestBody:    `{"password":"SecurePassword123!","name":"User"}`,
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "registration with missing password",
			requestBody:    `{"email":"user@example.com","name":"User"}`,
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "registration with missing name",
			requestBody:    `{"email":"user@example.com","password":"SecurePassword123!"}`,
			expectedStatus: http.StatusBadRequest,
		},
	}
}

func setupAuthRefreshSession(t *testing.T, handler *AuthHandler) (*auth.User, string) {
	t.Helper()
	ctx := context.Background()
	user := &auth.User{
		ID:        "user123",
		Email:     "test@example.com",
		Name:      "Test User",
		ProjectID: "project123",
		Role:      "user",
		Metadata:  make(map[string]interface{}),
	}

	token, err := handler.createSessionToken(ctx, user)
	require.NoError(t, err)
	return user, token
}

func runAuthRefreshCases(t *testing.T, handler *AuthHandler, e *echo.Echo, user *auth.User, token string) {
	t.Run("successful refresh", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/refresh", nil)
		req.Header.Set("Cookie", "auth_token="+token)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Refresh(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp AuthResponse
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.NotEmpty(t, resp.AccessToken)
		assert.Equal(t, resp.AccessToken, resp.Token)
		assert.NotNil(t, resp.User)
		assert.Equal(t, user.Email, resp.User.Email)
	})

	t.Run("missing token", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/refresh", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Refresh(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})

	t.Run("invalid token", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/refresh", nil)
		req.Header.Set("Cookie", "auth_token=invalid-token")
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Refresh(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})
}

func setupAuthLogoutSession(t *testing.T, handler *AuthHandler, redisClient *redis.Client) (*auth.User, string) {
	t.Helper()
	ctx := context.Background()
	user := &auth.User{
		ID:        "user123",
		Email:     "test@example.com",
		Name:      "Test User",
		ProjectID: "project123",
		Role:      "user",
		Metadata:  make(map[string]interface{}),
	}

	token, err := handler.createSessionToken(ctx, user)
	require.NoError(t, err)

	sessionKey := "session:" + user.ID
	_, err = redisClient.Get(ctx, sessionKey).Result()
	require.NoError(t, err)

	return user, token
}

func runAuthLogoutCases(t *testing.T, handler *AuthHandler, e *echo.Echo, redisClient *redis.Client, user *auth.User, token string) {
	sessionKey := "session:" + user.ID

	t.Run("successful logout", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/logout", nil)
		req.Header.Set("Cookie", "auth_token="+token)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Logout(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp map[string]bool
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp["success"])

		_, err = redisClient.Get(context.Background(), sessionKey).Result()
		assert.Equal(t, redis.Nil, err)
	})

	t.Run("logout without token", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/auth/logout", nil)
		rec := httptest.NewRecorder()

		c := e.NewContext(req, rec)
		err := handler.Logout(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var resp map[string]bool
		err = json.Unmarshal(rec.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp["success"])
	})
}

// Helper function to find a cookie by name
func findCookie(cookies []*http.Cookie, name string) *http.Cookie {
	for _, cookie := range cookies {
		if cookie.Name == name {
			return cookie
		}
	}
	return nil
}
