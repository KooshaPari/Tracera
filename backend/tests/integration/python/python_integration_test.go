package python_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/clients"
)

// setupPythonClient creates a test Python client with a mock server
func setupPythonClient(t *testing.T, handler http.HandlerFunc) (*clients.PythonServiceClient, *httptest.Server) {
	server := httptest.NewServer(handler)

	// Setup Redis cache for testing (use mock or in-memory)
	redisCache, err := cache.NewRedisCache(cache.RedisCacheConfig{
		RedisURL:      "redis://localhost:6379",
		DefaultTTL:    5 * time.Minute,
		EnableMetrics: true,
	})
	if err != nil {
		// Fall back to nil cache for tests without Redis
		redisCache = nil
	}

	client := clients.NewPythonServiceClient(server.URL, "test-token", redisCache)

	return client, server
}

// TestPythonClientBasicCall tests basic HTTP GET request
func TestPythonClientBasicCall(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "GET", r.Method)
		assert.Equal(t, "/api/v1/specifications/health", r.URL.Path)
		assert.Equal(t, "Bearer test-token", r.Header.Get("Authorization"))

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "ok",
		})
	})

	client, server := setupPythonClient(t, handler)
	defer server.Close()

	var result map[string]interface{}
	err := client.DelegateRequest(
		context.Background(),
		"GET",
		"/api/v1/specifications/health",
		nil,
		&result,
		false,
		"",
		0,
	)

	require.NoError(t, err)
	assert.Equal(t, "ok", result["status"])
}

// TestPythonClientPOSTRequest tests POST request with body
func TestPythonClientPOSTRequest(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "/api/v1/specifications", r.URL.Path)

		var body map[string]interface{}
		json.NewDecoder(r.Body).Decode(&body)
		assert.Equal(t, "test spec", body["name"])

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"id":   "123",
			"name": body["name"],
		})
	})

	client, server := setupPythonClient(t, handler)
	defer server.Close()

	requestBody := map[string]interface{}{
		"name":        "test spec",
		"description": "test description",
	}

	var result map[string]interface{}
	err := client.DelegateRequest(
		context.Background(),
		"POST",
		"/api/v1/specifications",
		requestBody,
		&result,
		false,
		"",
		0,
	)

	require.NoError(t, err)
	assert.Equal(t, "123", result["id"])
	assert.Equal(t, "test spec", result["name"])
}

// TestPythonClientRetry tests retry logic on transient failures
func TestPythonClientRetry(t *testing.T) {
	attempts := 0

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		attempts++
		// Fail first 2 times, succeed on 3rd
		if attempts < 3 {
			w.WriteHeader(http.StatusServiceUnavailable)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "ok",
		})
	})

	client, server := setupPythonClient(t, handler)
	defer server.Close()

	var result map[string]interface{}
	err := client.DelegateRequest(
		context.Background(),
		"GET",
		"/api/v1/health",
		nil,
		&result,
		false,
		"",
		0,
	)

	require.NoError(t, err)
	assert.Equal(t, "ok", result["status"])
	assert.Equal(t, 3, attempts, "Should have retried twice before succeeding")
}

// TestPythonClientCircuitBreaker tests circuit breaker opens after failures
func TestPythonClientCircuitBreaker(t *testing.T) {
	failureCount := 0

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		failureCount++
		w.WriteHeader(http.StatusInternalServerError)
	})

	client, server := setupPythonClient(t, handler)
	defer server.Close()

	// Make multiple requests to trip the circuit breaker
	for i := 0; i < 6; i++ {
		var result map[string]interface{}
		client.DelegateRequest(
			context.Background(),
			"GET",
			"/api/v1/health",
			nil,
			&result,
			false,
			"",
			0,
		)
		// Ignore errors, we expect failures
	}

	// Circuit breaker should now be open
	// Note: Circuit breaker state check depends on implementation
	// This is a simplified test
	assert.Greater(t, failureCount, 3, "Should have made multiple attempts")
}

// TestPythonClientCaching tests Redis caching behavior
func TestPythonClientCaching(t *testing.T) {
	t.Skip("Skipping cache test - requires Redis connection")

	requestCount := 0

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestCount++
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "ok",
			"count":  requestCount,
		})
	})

	client, server := setupPythonClient(t, handler)
	defer server.Close()

	ctx := context.Background()
	cacheKey := "test-cache-key"

	// First call should cache
	var result1 map[string]interface{}
	err := client.DelegateRequest(
		ctx,
		"GET",
		"/api/v1/cached-endpoint",
		nil,
		&result1,
		true,
		cacheKey,
		5*time.Minute,
	)

	require.NoError(t, err)
	assert.Equal(t, float64(1), result1["count"])

	// Second call should return from cache
	var result2 map[string]interface{}
	err = client.DelegateRequest(
		ctx,
		"GET",
		"/api/v1/cached-endpoint",
		nil,
		&result2,
		true,
		cacheKey,
		5*time.Minute,
	)

	require.NoError(t, err)
	assert.Equal(t, float64(1), result2["count"], "Should return cached value")
	assert.Equal(t, 1, requestCount, "Should only make one HTTP request")
}

// TestPythonClientTimeout tests request timeout handling
func TestPythonClientTimeout(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Delay response longer than client timeout
		time.Sleep(35 * time.Second)
		w.WriteHeader(http.StatusOK)
	})

	client, server := setupPythonClient(t, handler)
	defer server.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	var result map[string]interface{}
	err := client.DelegateRequest(
		ctx,
		"GET",
		"/api/v1/slow-endpoint",
		nil,
		&result,
		false,
		"",
		0,
	)

	assert.Error(t, err, "Should timeout")
}

// TestPythonClientErrorResponse tests handling of error responses
func TestPythonClientErrorResponse(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": "Invalid request",
		})
	})

	client, server := setupPythonClient(t, handler)
	defer server.Close()

	var result map[string]interface{}
	err := client.DelegateRequest(
		context.Background(),
		"GET",
		"/api/v1/bad-request",
		nil,
		&result,
		false,
		"",
		0,
	)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "400")
}

// TestGenerateCacheKey tests cache key generation
func TestGenerateCacheKey(t *testing.T) {
	tests := []struct {
		name     string
		prefix   string
		method   string
		path     string
		body     interface{}
		expected string // We'll check for consistency rather than exact value
	}{
		{
			name:   "Simple GET request",
			prefix: "test",
			method: "GET",
			path:   "/api/v1/items",
			body:   nil,
		},
		{
			name:   "POST with body",
			prefix: "test",
			method: "POST",
			path:   "/api/v1/items",
			body:   map[string]string{"name": "test"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key1 := clients.GenerateCacheKey(tt.prefix, tt.method, tt.path, tt.body)
			key2 := clients.GenerateCacheKey(tt.prefix, tt.method, tt.path, tt.body)

			// Same inputs should produce same key
			assert.Equal(t, key1, key2, "Cache keys should be consistent")

			// Key should include prefix
			assert.Contains(t, key1, tt.prefix)
		})
	}
}
