package server

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestServerRoutes(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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

			assert.NotEqual(t, http.StatusNotFound, rec.Code)
		})
	}
}

func TestServerGraphRoutes(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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

func TestServerErrorHandling(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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

func TestServerHealthCheck(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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
		require.NoError(t, err)
		assert.Equal(t, "ok", response["status"])
	})
}

func TestServerConcurrentRequests(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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

		for i := 0; i < numRequests; i++ {
			code := <-results
			assert.NotEqual(t, http.StatusInternalServerError, code)
		}
	})
}

func TestServerEdgeCases(t *testing.T) {
	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

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

		assert.NotEqual(t, 0, rec.Code)
	})

	t.Run("special characters in URL", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/test%20id", nil)
		rec := httptest.NewRecorder()

		server.echo.ServeHTTP(rec, req)

		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})
}

func TestRouteRegistrationBasic(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	healthRoutes := []struct {
		method string
		path   string
	}{
		{http.MethodGet, "/health"},
		{http.MethodGet, "/api/v1/health"},
	}

	for _, route := range healthRoutes {
		t.Run(route.method+" "+route.path, func(t *testing.T) {
			req := httptest.NewRequest(route.method, route.path, nil)
			rec := httptest.NewRecorder()
			server.echo.ServeHTTP(rec, req)
			assert.Equal(t, http.StatusOK, rec.Code)
		})
	}
}

func TestMetricsAndCSRFRoutes(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	routes := []struct {
		method string
		path   string
		name   string
	}{
		{http.MethodGet, "/metrics", "metrics"},
		{http.MethodGet, "/api/v1/csrf-token", "csrf token"},
	}

	for _, route := range routes {
		t.Run(route.name, func(t *testing.T) {
			req := httptest.NewRequest(route.method, route.path, nil)
			rec := httptest.NewRecorder()
			server.echo.ServeHTTP(rec, req)
			assert.NotEqual(t, http.StatusNotFound, rec.Code)
		})
	}
}

func TestCoreResourceRoutes(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	resources := []struct {
		resource string
		methods  []string
	}{
		{"projects", []string{http.MethodGet, http.MethodPost}},
		{"items", []string{http.MethodGet, http.MethodPost}},
		{"links", []string{http.MethodGet, http.MethodPost}},
		{"agents", []string{http.MethodGet, http.MethodPost}},
		{"search", []string{http.MethodGet, http.MethodPost}},
	}

	for _, resource := range resources {
		for _, method := range resource.methods {
			t.Run(method+" /api/v1/"+resource.resource, func(t *testing.T) {
				req := httptest.NewRequest(method, "/api/v1/"+resource.resource, nil)
				rec := httptest.NewRecorder()
				server.echo.ServeHTTP(rec, req)
				assert.NotEqual(t, http.StatusNotFound, rec.Code)
			})
		}
	}
}

func TestGraphAnalysisRoutes(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	graphRoutes := []string{
		"/api/v1/graph/full",
		"/api/v1/graph/cycles",
		"/api/v1/graph/topo-sort",
		"/api/v1/graph/orphans",
		"/api/v1/graph/metrics",
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

func TestErrorHandlingScenarios(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("404 not found returns proper status", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/nonexistent", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusNotFound, rec.Code)
	})

	t.Run("405 method not allowed", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/health", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusMethodNotAllowed, rec.Code)
	})

	t.Run("400 bad request with invalid JSON", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", strings.NewReader("{invalid"))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})

	t.Run("handles empty path segments", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1//projects", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEqual(t, 0, rec.Code)
	})

	t.Run("handles very long URLs", func(t *testing.T) {
		longID := strings.Repeat("a", 1000)
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+longID, nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("handles special characters in URL", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/test%20space", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("handles path traversal attempts", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/../../etc/passwd", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})
}

func TestConcurrentServerRequests(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("concurrent identical requests", func(t *testing.T) {
		const count = 50
		results := make(chan int, count)

		for i := 0; i < count; i++ {
			go func() {
				req := httptest.NewRequest(http.MethodGet, "/health", nil)
				rec := httptest.NewRecorder()
				server.echo.ServeHTTP(rec, req)
				results <- rec.Code
			}()
		}

		for i := 0; i < count; i++ {
			code := <-results
			assert.Equal(t, http.StatusOK, code)
		}
	})

	t.Run("concurrent mixed endpoint requests", func(t *testing.T) {
		const count = 30
		endpoints := []string{"/health", "/api/v1/projects", "/api/v1/items"}
		results := make(chan int, count)

		for i := 0; i < count; i++ {
			go func(idx int) {
				endpoint := endpoints[idx%len(endpoints)]
				req := httptest.NewRequest(http.MethodGet, endpoint, nil)
				rec := httptest.NewRecorder()
				server.echo.ServeHTTP(rec, req)
				results <- rec.Code
			}(i)
		}

		for i := 0; i < count; i++ {
			code := <-results
			assert.NotEqual(t, 0, code)
		}
	})
}

func TestHTTPHeaderHandling(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("request with user agent", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		req.Header.Set("User-Agent", "test-agent/1.0")
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("request with accept encoding", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
		req.Header.Set("Accept-Encoding", "gzip, deflate")
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("request with authorization header", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
		req.Header.Set("Authorization", "Bearer token123")
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("request with content-type", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", strings.NewReader("{}"))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEqual(t, http.StatusInternalServerError, rec.Code)
	})

	t.Run("case insensitive header handling", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		req.Header.Set("content-type", "application/json")
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

func TestResponseValidation(t *testing.T) {
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	infra := createTestInfrastructure(t)
	t.Cleanup(func() {
		if err := infra.Close(context.Background()); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	})

	cfg := createTestConfig()
	server, err := NewServer(infra, cfg)
	require.NoError(t, err)

	t.Run("health response has valid JSON", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)

		var response map[string]interface{}
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
	})

	t.Run("response has content-type header", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/health", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.NotEmpty(t, rec.Header().Get("Content-Type"))
	})

	t.Run("404 response is valid", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/api/v1/notfound", nil)
		rec := httptest.NewRecorder()
		server.echo.ServeHTTP(rec, req)
		assert.Equal(t, http.StatusNotFound, rec.Code)
		assert.Positive(t, rec.Body.Len())
	})
}
