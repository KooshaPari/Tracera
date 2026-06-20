//go:build !integration && !e2e

package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// Test constants
const (
	authTestSessionTTL      = 24 * time.Hour
	authTestShortSessionTTL = 1 * time.Hour
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
		require.Error(t, err)
	})

	// Test expired session
	t.Run("expired session", func(t *testing.T) {
		// Delete the session from Redis
		sessionKey := "session:" + user.ID
		redisClient.Del(ctx, sessionKey)

		// Try to validate the token
		_, err := authHandler.validateSessionToken(ctx, token)
		require.Error(t, err)
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

	// Get original session
	sessionKey := "session:" + user.ID
	sessionJSONBefore, err := redisClient.Get(ctx, sessionKey).Result()
	require.NoError(t, err)

	var sessionDataBefore SessionData
	err = json.Unmarshal([]byte(sessionJSONBefore), &sessionDataBefore)
	require.NoError(t, err)

	// Extend session with a new token
	newToken, err := authHandler.extendSession(ctx, user)
	require.NoError(t, err)
	assert.NotEmpty(t, newToken)

	// Get updated session
	sessionJSONAfter, err := redisClient.Get(ctx, sessionKey).Result()
	require.NoError(t, err)

	var sessionDataAfter SessionData
	err = json.Unmarshal([]byte(sessionJSONAfter), &sessionDataAfter)
	require.NoError(t, err)

	// Verify session was updated (LastActive should be more recent)
	assert.True(t, sessionDataAfter.LastActive.Equal(sessionDataBefore.LastActive) ||
		sessionDataAfter.LastActive.After(sessionDataBefore.LastActive),
		"Session last_active should be updated or equal")
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
