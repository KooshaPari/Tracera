package server

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestServerMiddleware(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("middleware stack is configured", func(t *testing.T) {
		assert.NotNil(t, server.echo)
	})

	t.Run("health check endpoint exists", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("CORS headers present", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodOptions, "/api/v1/projects", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Contains(t, rec.Header().Get("Access-Control-Allow-Methods"), "GET")
	})
}

func TestServerCORS(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("preflight request", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodOptions, "/api/v1/projects", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		req.Header.Set("Access-Control-Request-Method", "POST")
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.NotEmpty(t, rec.Header().Get("Access-Control-Allow-Origin"))
		assert.NotEmpty(t, rec.Header().Get("Access-Control-Allow-Methods"))
	})

	t.Run("actual request with origin", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.NotEmpty(t, rec.Header().Get("Access-Control-Allow-Origin"))
	})
}

func TestServerRequestLogging(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("logs requests", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		req.Header.Set("User-Agent", "test-agent")
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

func TestServerRecoveryMiddleware(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	// Add a panic-inducing route
	server.echo.GET("/panic", func(_ echo.Context) error {
		panic("test panic")
	})

	t.Run("recovers from panic", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/panic", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusInternalServerError, rec.Code)
	})
}
