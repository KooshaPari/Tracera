package handlers

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// TestHealthCheck tests the health check endpoint
func TestHealthCheck(t *testing.T) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := HealthCheck(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp HealthResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, "ok", resp.Status)
	assert.Equal(t, "tracertm-backend", resp.Service)
}

// TestHealthCheckResponseStructure tests health response has correct fields
func TestHealthCheckResponseStructure(t *testing.T) {
	healthResp := HealthResponse{
		Status:  "ok",
		Service: "tracertm-backend",
	}
	assert.Equal(t, "ok", healthResp.Status)
	assert.Equal(t, "tracertm-backend", healthResp.Service)
}

// TestAuthMeSuccess tests getting current user info when authenticated
func TestAuthMeSuccess(t *testing.T) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/auth/me", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	user := &auth.User{
		ID:    uuid.New().String(),
		Email: "test@example.com",
		Name:  "Test User",
	}
	c.Set("user", user)

	err := AuthMe(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp auth.User
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, user.Email, resp.Email)
	assert.Equal(t, user.Name, resp.Name)
}

// TestAuthMeUnauthenticated tests getting current user when not authenticated
func TestAuthMeUnauthenticated(t *testing.T) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/auth/me", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := AuthMe(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusUnauthorized, rec.Code)

	var resp ErrorResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Equal(t, "unauthenticated", resp.Error)
}

// TestAuthMeInvalidUserType tests when user context is wrong type
func TestAuthMeInvalidUserType(t *testing.T) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/auth/me", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	// Set user to wrong type
	c.Set("user", "not a user")

	err := AuthMe(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusUnauthorized, rec.Code)
}

// TestErrorResponseStructure tests error response structure
func TestErrorResponseStructure(t *testing.T) {
	errResp := ErrorResponse{Error: "test error"}
	assert.Equal(t, "test error", errResp.Error)
}

// TestNewProjectHandler tests creating a new project handler
func TestNewProjectHandler(t *testing.T) {
	handler := NewProjectHandler(nil, nil, nil, nil, &EchoBinder{}, nil) // last param is ProjectService
	assert.NotNil(t, handler)
	assert.Nil(t, handler.cache)
	assert.Nil(t, handler.publisher)
}

// TestNewProjectHandlerWithNilValues tests creating handler with all nil values
func TestNewProjectHandlerWithNilValues(t *testing.T) {
	handler := NewProjectHandler(nil, nil, nil, nil, &EchoBinder{}, nil) // last param is ProjectService
	require.NotNil(t, handler)
	assert.Nil(t, handler.cache)
	assert.Nil(t, handler.publisher)
	assert.Nil(t, handler.realtimeBroadcaster)
	assert.Nil(t, handler.authProvider)
}

// TestGetCacheKey tests cache key generation
func TestGetCacheKey(t *testing.T) {
	handler := &ProjectHandler{}
	projectID := uuid.New().String()
	cacheKey := handler.getCacheKey(projectID)
	assert.Equal(t, "project:"+projectID, cacheKey)
}

// TestInvalidateProjectCacheWithNilCache tests cache invalidation with nil cache
func TestInvalidateProjectCacheWithNilCache(_ *testing.T) {
	handler := &ProjectHandler{cache: nil}
	projectID := uuid.New().String()

	// Should not panic when cache is nil
	handler.invalidateProjectCache(context.TODO(), projectID)
}

// TestHealthCheckJSONResponse tests that health check returns valid JSON
func TestHealthCheckJSONResponse(t *testing.T) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := HealthCheck(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
	assert.Equal(t, echo.MIMEApplicationJSON, rec.Header().Get(echo.HeaderContentType))

	// Verify it's valid JSON
	var resp HealthResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
}

// TestAuthMeResponseHasUserFields tests that auth me response includes user fields
func TestAuthMeResponseHasUserFields(t *testing.T) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/auth/me", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	userID := uuid.New().String()
	user := &auth.User{
		ID:    userID,
		Email: "user@example.com",
		Name:  "Example User",
	}
	c.Set("user", user)

	err := AuthMe(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp auth.User
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	// Verify all user fields are present
	assert.Equal(t, userID, resp.ID)
	assert.Equal(t, "user@example.com", resp.Email)
	assert.Equal(t, "Example User", resp.Name)
}

// TestErrorResponseJSON tests error response JSON format
func TestErrorResponseJSON(t *testing.T) {
	errResp := ErrorResponse{Error: "test error message"}

	data, err := json.Marshal(errResp)
	require.NoError(t, err)

	var unmarshaled ErrorResponse
	err = json.Unmarshal(data, &unmarshaled)
	require.NoError(t, err)
	assert.Equal(t, "test error message", unmarshaled.Error)
}

// TestHealthResponseJSON tests health response JSON format
func TestHealthResponseJSON(t *testing.T) {
	healthResp := HealthResponse{
		Status:  "ok",
		Service: "tracertm-backend",
	}

	data, err := json.Marshal(healthResp)
	require.NoError(t, err)
	assert.JSONEq(t, `{"status":"ok","service":"tracertm-backend"}`, string(data))
}
