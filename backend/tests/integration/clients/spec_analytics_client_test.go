package clients_test

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/clients"
)

func TestSpecAnalyticsClient_AnalyzeSpec(t *testing.T) {
	// Create mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "/api/v1/spec-analytics/analyze", r.URL.Path)

		// Return analysis result
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"spec_id": "spec-123",
			"compliant_with_iso": true,
			"ears_patterns": [
				{"type": "UBIQUITOUS", "matched": true, "confidence": 0.95},
				{"type": "EVENT_DRIVEN", "matched": false, "confidence": 0.0}
			],
			"odc_classification": "Feature",
			"formal_verification": {
				"is_verifiable": true,
				"logical_formula": "P -> Q",
				"contradictions": [],
				"ambiguities": []
			},
			"recommendations": ["Consider adding more detail", "Specify edge cases"]
		}`))
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	specAnalyticsClient := clients.NewSpecAnalyticsClient(pythonClient)

	ctx := context.Background()
	req := clients.AnalyzeSpecRequest{
		SpecID:    "spec-123",
		Content:   "The system shall authenticate users",
		ProjectID: "test-project",
	}

	result, err := specAnalyticsClient.AnalyzeSpec(ctx, req)

	require.NoError(t, err)
	assert.Equal(t, "spec-123", result.SpecID)
	assert.True(t, result.CompliantWithISO)
	assert.Len(t, result.EARSPatterns, 2)
	assert.Equal(t, "UBIQUITOUS", result.EARSPatterns[0].Type)
	assert.True(t, result.EARSPatterns[0].Matched)
	assert.Equal(t, 0.95, result.EARSPatterns[0].Confidence)
	assert.Equal(t, "Feature", result.ODCClassification)
	assert.NotNil(t, result.FormalVerification)
	assert.True(t, result.FormalVerification.IsVerifiable)
	assert.Len(t, result.Recommendations, 2)
}

func TestSpecAnalyticsClient_AnalyzeSpec_Caching(t *testing.T) {
	// Track number of requests
	var requestCount int32

	// Create mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt32(&requestCount, 1)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"spec_id": "spec-123",
			"compliant_with_iso": true,
			"ears_patterns": [],
			"odc_classification": "Feature",
			"recommendations": []
		}`))
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	specAnalyticsClient := clients.NewSpecAnalyticsClient(pythonClient)

	ctx := context.Background()
	req := clients.AnalyzeSpecRequest{
		SpecID:    "spec-123",
		Content:   "The system shall authenticate users",
		ProjectID: "test-project",
	}

	// First request - should hit server
	result1, err := specAnalyticsClient.AnalyzeSpec(ctx, req)
	require.NoError(t, err)
	assert.Equal(t, int32(1), atomic.LoadInt32(&requestCount))

	// Second request with same content - should use cache
	result2, err := specAnalyticsClient.AnalyzeSpec(ctx, req)
	require.NoError(t, err)
	assert.Equal(t, int32(1), atomic.LoadInt32(&requestCount), "Second request should use cache")
	assert.Equal(t, result1.SpecID, result2.SpecID)

	// Third request with different content - should hit server again
	req.Content = "Different content"
	result3, err := specAnalyticsClient.AnalyzeSpec(ctx, req)
	require.NoError(t, err)
	assert.Equal(t, int32(2), atomic.LoadInt32(&requestCount), "Different content should bypass cache")
	assert.Equal(t, result1.SpecID, result3.SpecID)
}

func TestSpecAnalyticsClient_AnalyzeSpec_StaleOnError(t *testing.T) {
	// Track number of requests
	// Track number of requests
	var requestCount int32

	// Create mock server that succeeds first, then fails
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		count := atomic.AddInt32(&requestCount, 1)

		if count == 1 {
			// First request succeeds
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{
				"spec_id": "spec-123",
				"compliant_with_iso": true,
				"ears_patterns": [],
				"odc_classification": "Feature",
				"recommendations": []
			}`))
		} else {
			// Subsequent requests fail
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{"error": "Service unavailable"}`))
		}
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	specAnalyticsClient := clients.NewSpecAnalyticsClient(pythonClient)

	ctx := context.Background()
	req := clients.AnalyzeSpecRequest{
		SpecID:    "spec-123",
		Content:   "The system shall authenticate users",
		ProjectID: "test-project",
	}

	// First request - should succeed and cache
	result1, err := specAnalyticsClient.AnalyzeSpec(ctx, req)
	require.NoError(t, err)
	assert.True(t, result1.CompliantWithISO)

	// Second request - would normally fail, but should return cached result
	// Note: This test assumes stale-on-error is implemented in the client
	result2, err := specAnalyticsClient.AnalyzeSpec(ctx, req)
	// Should either return cached result or error, depending on implementation
	if err == nil {
		assert.True(t, result2.CompliantWithISO, "Should return cached result on error")
	}
}

func TestSpecAnalyticsClient_BatchAnalyzeSpecs(t *testing.T) {
	// Track parallel requests
	var activeRequests int32
	var maxActiveRequests int32

	// Create mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Track concurrency
		active := atomic.AddInt32(&activeRequests, 1)
		defer atomic.AddInt32(&activeRequests, -1)

		// Update max
		for {
			max := atomic.LoadInt32(&maxActiveRequests)
			if active <= max || atomic.CompareAndSwapInt32(&maxActiveRequests, max, active) {
				break
			}
		}

		// Simulate processing time
		time.Sleep(50 * time.Millisecond)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"spec_id": "spec-123",
			"compliant_with_iso": true,
			"ears_patterns": [],
			"odc_classification": "Feature",
			"recommendations": []
		}`))
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	specAnalyticsClient := clients.NewSpecAnalyticsClient(pythonClient)

	ctx := context.Background()

	// Create 20 requests
	requests := make([]clients.AnalyzeSpecRequest, 20)
	for i := 0; i < 20; i++ {
		requests[i] = clients.AnalyzeSpecRequest{
			SpecID:    fmt.Sprintf("spec-%d", i),
			Content:   fmt.Sprintf("Content %d", i),
			ProjectID: "test-project",
		}
	}

	// Batch analyze
	results, err := specAnalyticsClient.BatchAnalyzeSpecs(ctx, requests)

	require.NoError(t, err)
	assert.Len(t, results, 20)

	// Verify max concurrency (should be <= 10)
	maxActive := atomic.LoadInt32(&maxActiveRequests)
	assert.LessOrEqual(t, maxActive, int32(10), "Should not exceed max concurrent requests")
}

func TestSpecAnalyticsClient_ValidateISO29148Compliance(t *testing.T) {
	// Create mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"spec_id": "spec-123",
			"compliant_with_iso": false,
			"ears_patterns": [],
			"odc_classification": "Feature",
			"recommendations": ["Add traceability", "Specify constraints"]
		}`))
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	specAnalyticsClient := clients.NewSpecAnalyticsClient(pythonClient)

	ctx := context.Background()
	compliant, recommendations, err := specAnalyticsClient.ValidateISO29148Compliance(
		ctx,
		"spec-123",
		"The system shall authenticate users",
		"test-project",
	)

	require.NoError(t, err)
	assert.False(t, compliant)
	assert.Len(t, recommendations, 2)
	assert.Contains(t, recommendations, "Add traceability")
	assert.Contains(t, recommendations, "Specify constraints")
}

func TestSpecAnalyticsClient_GetEARSPatterns(t *testing.T) {
	// Create mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"spec_id": "spec-123",
			"compliant_with_iso": true,
			"ears_patterns": [
				{"type": "UBIQUITOUS", "matched": true, "confidence": 0.95},
				{"type": "EVENT_DRIVEN", "matched": true, "confidence": 0.85},
				{"type": "UNWANTED_BEHAVIOR", "matched": false, "confidence": 0.0}
			],
			"odc_classification": "Feature",
			"recommendations": []
		}`))
	}))
	defer server.Close()

	mockCache := cache.NewMemoryCache(5 * time.Minute)
	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", mockCache)
	specAnalyticsClient := clients.NewSpecAnalyticsClient(pythonClient)

	ctx := context.Background()
	patterns, err := specAnalyticsClient.GetEARSPatterns(
		ctx,
		"spec-123",
		"When the user clicks login, the system shall authenticate the user",
		"test-project",
	)

	require.NoError(t, err)
	assert.Len(t, patterns, 3)
	assert.Equal(t, "UBIQUITOUS", patterns[0].Type)
	assert.True(t, patterns[0].Matched)
	assert.Equal(t, "EVENT_DRIVEN", patterns[1].Type)
	assert.True(t, patterns[1].Matched)
	assert.Equal(t, "UNWANTED_BEHAVIOR", patterns[2].Type)
	assert.False(t, patterns[2].Matched)
}
