package clients_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

// MockCache implements cache.Cache interface for testing
type MockCache struct {
	data map[string]interface{}
}

func NewMockCache() *MockCache {
	return &MockCache{
		data: make(map[string]interface{}),
	}
}

func (m *MockCache) Get(ctx context.Context, key string, dest interface{}) error {
	if val, ok := m.data[key]; ok {
		// Marshal and unmarshal to simulate real cache behavior
		data, _ := json.Marshal(val)
		return json.Unmarshal(data, dest)
	}
	return nil
}

func (m *MockCache) Set(ctx context.Context, key string, value interface{}) error {
	m.data[key] = value
	return nil
}

func (m *MockCache) Delete(ctx context.Context, keys ...string) error {
	for _, key := range keys {
		delete(m.data, key)
	}
	return nil
}

func (m *MockCache) InvalidatePattern(ctx context.Context, pattern string) error {
	return nil
}

func (m *MockCache) Close() error {
	return nil
}

func TestPythonServiceClient_SuccessfulRequest(t *testing.T) {
	// Create mock Python backend
	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Verify headers
		assert.Equal(t, "application/json", r.Header.Get("Content-Type"))
		assert.Equal(t, "application/json", r.Header.Get("Accept"))
		assert.Equal(t, "Bearer test-token", r.Header.Get("Authorization"))

		// Return mock response
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "success",
			"data":   map[string]string{"id": "123", "name": "test"},
		})
	}))
	defer mockServer.Close()

	mockCache := NewMockCache()
	client := clients.NewPythonServiceClient(mockServer.URL, "test-token", mockCache)

	ctx := context.Background()
	var response map[string]interface{}

	err := client.DelegateRequest(
		ctx,
		"GET",
		"/test",
		nil,
		&response,
		false, // not cacheable for this test
		"",
		0,
	)

	require.NoError(t, err)
	assert.Equal(t, "success", response["status"])
}

func TestPythonServiceClient_CacheHit(t *testing.T) {
	requestCount := 0

	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestCount++
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "success",
			"count":  requestCount,
		})
	}))
	defer mockServer.Close()

	mockCache := NewMockCache()
	client := clients.NewPythonServiceClient(mockServer.URL, "test-token", mockCache)

	ctx := context.Background()
	cacheKey := "test-cache-key"

	// First request - cache miss
	var response1 map[string]interface{}
	err := client.DelegateRequest(ctx, "GET", "/test", nil, &response1, true, cacheKey, 5*time.Minute)
	require.NoError(t, err)
	assert.Equal(t, 1, requestCount)

	// Second request - cache hit (should not increment requestCount)
	var response2 map[string]interface{}
	err = client.DelegateRequest(ctx, "GET", "/test", nil, &response2, true, cacheKey, 5*time.Minute)
	require.NoError(t, err)
	assert.Equal(t, 1, requestCount, "Should have used cached response")
	assert.Equal(t, response1, response2)
}

func TestPythonServiceClient_CircuitBreakerTrips(t *testing.T) {
	failureCount := 0

	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		failureCount++
		// Always fail
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Internal Server Error"))
	}))
	defer mockServer.Close()

	mockCache := NewMockCache()
	client := clients.NewPythonServiceClient(mockServer.URL, "test-token", mockCache)

	ctx := context.Background()
	var response map[string]interface{}

	// Make requests until circuit breaker trips (should be around 5 consecutive failures)
	maxAttempts := 10
	for i := 0; i < maxAttempts; i++ {
		err := client.DelegateRequest(ctx, "GET", "/test", nil, &response, false, "", 0)
		if err != nil {
			// Circuit breaker may have tripped
			if client.GetCircuitBreakerState() != 0 { // 0 = StateClosed
				t.Logf("Circuit breaker tripped after %d attempts", i+1)
				break
			}
		}
		time.Sleep(100 * time.Millisecond)
	}

	// Verify circuit breaker state changed from closed
	assert.NotEqual(t, 0, int(client.GetCircuitBreakerState()), "Circuit breaker should have tripped")
}

func TestPythonServiceClient_RetryLogic(t *testing.T) {
	attemptCount := 0

	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		attemptCount++
		if attemptCount < 3 {
			// Fail first 2 attempts
			w.WriteHeader(http.StatusServiceUnavailable)
			return
		}
		// Succeed on 3rd attempt
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{"status": "success"})
	}))
	defer mockServer.Close()

	mockCache := NewMockCache()
	client := clients.NewPythonServiceClient(mockServer.URL, "test-token", mockCache)

	ctx := context.Background()
	var response map[string]interface{}

	err := client.DelegateRequest(ctx, "GET", "/test", nil, &response, false, "", 0)
	require.NoError(t, err)
	assert.Equal(t, "success", response["status"])
	assert.GreaterOrEqual(t, attemptCount, 3, "Should have retried at least 3 times")
}

func TestPythonServiceClient_RequestTimeout(t *testing.T) {
	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Simulate slow response
		time.Sleep(35 * time.Second)
		w.WriteHeader(http.StatusOK)
	}))
	defer mockServer.Close()

	mockCache := NewMockCache()
	client := clients.NewPythonServiceClient(mockServer.URL, "test-token", mockCache)

	ctx := context.Background()
	var response map[string]interface{}

	err := client.DelegateRequest(ctx, "GET", "/test", nil, &response, false, "", 0)
	assert.Error(t, err, "Should timeout after 30 seconds")
}

func TestGenerateCacheKey(t *testing.T) {
	key1 := clients.GenerateCacheKey("prefix", "GET", "/path", map[string]string{"foo": "bar"})
	key2 := clients.GenerateCacheKey("prefix", "GET", "/path", map[string]string{"foo": "bar"})
	key3 := clients.GenerateCacheKey("prefix", "GET", "/path", map[string]string{"foo": "baz"})

	assert.Equal(t, key1, key2, "Same inputs should generate same key")
	assert.NotEqual(t, key1, key3, "Different inputs should generate different keys")
	assert.Contains(t, key1, "prefix:", "Cache key should include prefix")
}

func TestPythonServiceClient_ConnectionPooling(t *testing.T) {
	requestCount := 0

	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestCount++
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{"request": requestCount})
	}))
	defer mockServer.Close()

	mockCache := NewMockCache()
	client := clients.NewPythonServiceClient(mockServer.URL, "test-token", mockCache)

	ctx := context.Background()

	// Make multiple concurrent requests
	concurrentRequests := 10
	results := make(chan error, concurrentRequests)

	for i := 0; i < concurrentRequests; i++ {
		go func() {
			var response map[string]interface{}
			err := client.DelegateRequest(ctx, "GET", "/test", nil, &response, false, "", 0)
			results <- err
		}()
	}

	// Collect results
	for i := 0; i < concurrentRequests; i++ {
		err := <-results
		assert.NoError(t, err)
	}

	assert.Equal(t, concurrentRequests, requestCount, "All requests should have completed")
}
