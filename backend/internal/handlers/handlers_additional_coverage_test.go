//go:build !integration && !e2e

package handlers

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestHealthCheck_Coverage tests the HealthCheck handler (additional coverage)
func TestHealthCheck_Coverage(t *testing.T) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := HealthCheck(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var response HealthResponse
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)
	assert.Equal(t, "ok", response.Status)
	assert.Equal(t, "tracertm-backend", response.Service)
}

// TestAuthMe tests the AuthMe handler
func TestAuthMe(t *testing.T) {
	e := echo.New()

	t.Run("authenticated user", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/auth/me", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		// Set user in context
		user := &auth.User{
			ID:    "user-1",
			Email: "test@example.com",
		}
		c.Set("user", user)

		err := AuthMe(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("unauthenticated", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/auth/me", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		// Don't set user

		err := AuthMe(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)

		var response ErrorResponse
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Contains(t, response.Error, "unauthenticated")
	})

	t.Run("nil user", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/auth/me", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.Set("user", nil)

		err := AuthMe(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})
}

// TestProjectHandler_HelperMethods tests helper methods
func TestProjectHandler_HelperMethods(t *testing.T) {
	t.Run("getCacheKey", func(t *testing.T) {
		handler := &ProjectHandler{}
		projectID := "project-123"
		key := handler.getCacheKey(projectID)
		assert.Contains(t, key, projectID)
		assert.Contains(t, key, "project")
	})

	t.Run("invalidateProjectCache with nil cache", func(_ *testing.T) {
		handler := &ProjectHandler{
			cache: nil,
		}
		// Should not panic
		handler.invalidateProjectCache(context.Background(), "project-1")
	})

	t.Run("broadcastProjectEvent with nil broadcaster", func(_ *testing.T) {
		handler := &ProjectHandler{
			realtimeBroadcaster: nil,
		}
		// Should not panic
		handler.broadcastProjectEvent(context.Background(), "created", "project-1")
	})
}
