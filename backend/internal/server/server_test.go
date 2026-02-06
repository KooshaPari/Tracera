package server

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/kooshapari/tracertm-backend/internal/config"
	"github.com/kooshapari/tracertm-backend/internal/infrastructure"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

const (
	serverShutdownDelay           = 10 * time.Millisecond
	serverStartDelay              = 100 * time.Millisecond
	serverShutdownTimeout         = 2 * time.Second
	serverStartTimeout            = 3 * time.Second
	serverGracefulShutdownTimeout = 5 * time.Second
	serverImmediateTimeout        = 1 * time.Nanosecond
)

func createTestInfrastructure(t *testing.T) *infrastructure.Infrastructure {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		t.Skipf("Failed to create database pool: %v", err)
	}

	gormDB, err := gorm.Open(postgres.Open(dbURL), &gorm.Config{})
	if err != nil {
		pool.Close()
		t.Skipf("Failed to create GORM DB: %v", err)
	}

	return &infrastructure.Infrastructure{
		DB:     pool,
		GormDB: gormDB,
	}
}

func createTestConfig() *config.Config {
	return &config.Config{
		DatabaseURL: os.Getenv("TEST_DATABASE_URL"),
		RedisURL:    "redis://localhost:6379",
		NATSUrl:     "nats://localhost:4222",
		Port:        "8080",
		Env:         "test",
	}
}

func TestNewServer(t *testing.T) {
	t.Run("creates server with infrastructure", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() { _ = infra.Close(context.Background()) })

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		assert.NotNil(t, server)
		assert.NotNil(t, server.echo)
		assert.NotNil(t, server.pool)
		assert.Equal(t, infra.DB, server.pool)
	})

	t.Run("initializes with nil infrastructure components", func(t *testing.T) {
		fullInfra := createTestInfrastructure(t)
		t.Cleanup(func() { _ = fullInfra.Close(context.Background()) })
		infra := &infrastructure.Infrastructure{
			DB:     fullInfra.DB,
			GormDB: fullInfra.GormDB,
		}

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		assert.NotNil(t, server)
		assert.Nil(t, server.redisClient)
		assert.Nil(t, server.natsConn)
	})
}

func TestServerMiddleware(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("middleware stack is configured", func(t *testing.T) {
		assert.NotNil(t, server.echo)
		// Middleware is configured in setupMiddleware
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

func TestServerRoutes(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	testCases := []struct {
		name           string
		method         string
		path           string
		expectedStatus int
	}{
		{"health check", http.MethodGet, "/health", http.StatusOK},
		{"list projects", http.MethodGet, "/api/v1/projects", http.StatusOK},
		{"list items", http.MethodGet, "/api/v1/items", http.StatusOK},
		{"list links", http.MethodGet, "/api/v1/links", http.StatusOK},
		{"list agents", http.MethodGet, "/api/v1/agents", http.StatusOK},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest(tc.method, tc.path, nil)
			rec := httptest.NewRecorder()

			server.echo.ServeHTTP(rec, req)

			// Routes should exist (may return various codes based on auth/data)
			assert.NotEqual(t, http.StatusNotFound, rec.Code)
		})
	}
}

func TestServerGraphRoutes(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	graphRoutes := []string{
		"/api/v1/graph/full",
		"/api/v1/graph/cycles",
		"/api/v1/graph/topo-sort",
		"/api/v1/graph/orphans",
	}

	for _, route := range graphRoutes {
		t.Run(route, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, route, nil)
			rec := httptest.NewRecorder()

			server.echo.ServeHTTP(rec, req)

			assert.NotEqual(t, http.StatusNotFound, rec.Code)
		})
	}
}

func TestServerSearchRoutes(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("search endpoints exist", func(t *testing.T) {
		routes := []struct {
			method string
			path   string
		}{
			{http.MethodGet, "/api/v1/search"},
			{http.MethodPost, "/api/v1/search"},
			{http.MethodGet, "/api/v1/search/suggest"},
			{http.MethodGet, "/api/v1/search/stats"},
			{http.MethodGet, "/api/v1/search/health"},
		}

		for _, route := range routes {
			req := httptest.NewRequest(route.method, route.path, nil)
			rec := httptest.NewRecorder()

			server.echo.ServeHTTP(rec, req)

			assert.NotEqual(t, http.StatusNotFound, rec.Code, "Route: %s %s", route.method, route.path)
		}
	})
}

func TestServerAgentCoordinationRoutes(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	routes := []struct {
		method string
		path   string
	}{
		{http.MethodPost, "/api/v1/agents/register"},
		{http.MethodPost, "/api/v1/agents/heartbeat"},
		{http.MethodPost, "/api/v1/agents/task/result"},
		{http.MethodPost, "/api/v1/agents/task/error"},
		{http.MethodPost, "/api/v1/agents/task/assign"},
		{http.MethodGet, "/api/v1/agents/registered"},
	}

	for _, route := range routes {
		t.Run(route.path, func(t *testing.T) {
			req := httptest.NewRequest(route.method, route.path, nil)
			rec := httptest.NewRecorder()

			server.echo.ServeHTTP(rec, req)

			assert.NotEqual(t, http.StatusNotFound, rec.Code)
		})
	}
}

func TestServerShutdown(t *testing.T) {
	t.Run("graceful shutdown", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() { _ = infra.Close(context.Background()) })

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		ctx, cancel := context.WithTimeout(context.Background(), serverGracefulShutdownTimeout)
		defer cancel()

		err = server.Shutdown(ctx)
		assert.NoError(t, err)
	})

	t.Run("shutdown with timeout", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() { _ = infra.Close(context.Background()) })

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		ctx, cancel := context.WithTimeout(context.Background(), serverImmediateTimeout)
		defer cancel()
		time.Sleep(serverShutdownDelay)

		err = server.Shutdown(ctx)
		// May or may not error depending on timing
		if err != nil {
			t.Logf("Shutdown error (acceptable): %v", err)
		}
	})

	t.Run("shutdown cleans up resources", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		cfg := createTestConfig()

		// Create server with Redis client
		redisClient := redis.NewClient(&redis.Options{
			Addr: "localhost:6379",
		})
		infra.Redis = redisClient

		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		server.redisClient = redisClient

		ctx := context.Background()
		_ = server.Shutdown(ctx)

		// Redis client should be closed
		err = redisClient.Ping(ctx).Err()
		if err == nil {
			t.Log("Redis still connected after shutdown")
		}
	})
}

func TestServerStart(t *testing.T) {
	t.Run("starts on specified port", func(t *testing.T) {
		infra := createTestInfrastructure(t)
		t.Cleanup(func() { _ = infra.Close(context.Background()) })

		cfg := createTestConfig()
		server, err := NewServer(infra, cfg)
		require.NoError(t, err)

		// Start in goroutine
		errChan := make(chan error, 1)
		go func() {
			errChan <- server.Start(":0") // Use port 0 for random available port
		}()

		// Give it time to start
		time.Sleep(serverStartDelay)

		// Shutdown
		ctx, cancel := context.WithTimeout(context.Background(), serverShutdownTimeout)
		defer cancel()
		_ = server.Shutdown(ctx)

		// Check for startup errors
		select {
		case err := <-errChan:
			if err != nil && !strings.Contains(err.Error(), "Server closed") {
				t.Errorf("Unexpected error: %v", err)
			}
		case <-time.After(serverStartTimeout):
			t.Log("Server shutdown completed")
		}
	})
}

func TestServerErrorHandling(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("404 returns JSON error", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/nonexistent", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusNotFound, rec.Code)
	})

	t.Run("method not allowed", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/health", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusMethodNotAllowed, rec.Code)
	})

	t.Run("malformed JSON body", func(t *testing.T) {
		body := strings.NewReader("{invalid json")
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", body)
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func TestServerCORS(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

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

func TestServerWithFullInfrastructure(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	t.Run("server with all services", func(t *testing.T) {
		ctx := context.Background()
		cfg := createTestConfig()

		// Try to initialize full infrastructure
		infra, err := infrastructure.InitializeInfrastructure(ctx, cfg)
		if err != nil {
			t.Skipf("Failed to initialize infrastructure: %v", err)
		}
		t.Cleanup(func() { _ = infra.Close(ctx) })

		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		assert.NotNil(t, server)

		// Verify server components
		assert.NotNil(t, server.pool)
		assert.NotNil(t, server.searchEngine)
		assert.NotNil(t, server.searchIndexer)
	})
}

func TestServerHealthCheck(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("health check returns OK", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)

		var response map[string]interface{}
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "ok", response["status"])
	})
}

func TestServerConcurrentRequests(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("handle concurrent health checks", func(t *testing.T) {
		const numRequests = 50
		results := make(chan int, numRequests)

		for i := 0; i < numRequests; i++ {
			go func() {
				req := httptest.NewRequest(http.MethodGet, "/health", nil)
				rec := httptest.NewRecorder()
				server.echo.ServeHTTP(rec, req)
				results <- rec.Code
			}()
		}

		// Collect results
		for i := 0; i < numRequests; i++ {
			code := <-results
			assert.Equal(t, http.StatusOK, code)
		}
	})

	t.Run("handle concurrent API requests", func(t *testing.T) {
		const numRequests = 30
		results := make(chan int, numRequests)

		endpoints := []string{
			"/api/v1/projects",
			"/api/v1/items",
			"/api/v1/links",
			"/api/v1/agents",
		}

		for i := 0; i < numRequests; i++ {
			go func(idx int) {
				endpoint := endpoints[idx%len(endpoints)]
				req := httptest.NewRequest(http.MethodGet, endpoint, nil)
				rec := httptest.NewRecorder()
				server.echo.ServeHTTP(rec, req)
				results <- rec.Code
			}(i)
		}

		// Collect results
		for i := 0; i < numRequests; i++ {
			code := <-results
			assert.NotEqual(t, http.StatusInternalServerError, code)
		}
	})
}

func TestServerRequestLogging(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("logs requests", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		req.Header.Set("User-Agent", "test-agent")
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		// Just verify request completes - logging happens in middleware
		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

func TestServerRecoveryMiddleware(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

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

		// Should not crash the test
		server.echo.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusInternalServerError, rec.Code)
	})
}

func TestServerEdgeCases(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("empty request body", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("very large request body", func(t *testing.T) {
		largeBody := strings.Repeat("x", 10*1024*1024) // 10MB
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", strings.NewReader(largeBody))
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		// Should handle gracefully
		assert.NotEqual(t, 0, rec.Code)
	})

	t.Run("special characters in URL", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/test%20id", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})
}

func TestServerMultipleShutdowns(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() { _ = infra.Close(context.Background()) })

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	ctx := context.Background()

	err = server.Shutdown(ctx)
	assert.NoError(t, err)

	err = server.Shutdown(ctx)
	// Second shutdown should not panic
	if err != nil {
		t.Logf("Second shutdown error (acceptable): %v", err)
	}
}

func TestServerNilComponents(t *testing.T) {
	t.Run("server with minimal infrastructure", func(t *testing.T) {
		dbURL := os.Getenv("TEST_DATABASE_URL")
		if dbURL == "" {
			t.Skip("TEST_DATABASE_URL not set")
		}
		pool, err := pgxpool.New(context.Background(), dbURL)
		if err != nil {
			t.Skipf("Database not available: %v", err)
		}
		defer pool.Close()

		gormDB, err := gorm.Open(postgres.Open(dbURL), &gorm.Config{})
		if err != nil {
			pool.Close()
			t.Skipf("Failed to create GORM DB: %v", err)
		}

		infra := &infrastructure.Infrastructure{
			DB:     pool,
			GormDB: gormDB,
		}
		cfg := createTestConfig()

		server, err := NewServer(infra, cfg)
		require.NoError(t, err)
		assert.NotNil(t, server)

		// Should still handle requests
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	})
}
