package resilience

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	retryPolicyContextTimeout = 50 * time.Millisecond
	testSuccessResult         = "success"
)

func TestDefaultRetryPolicy(t *testing.T) {
	policy := DefaultRetryPolicy()

	assert.Equal(t, 3, policy.MaxRetries)
	assert.Equal(t, 1*time.Second, policy.InitialDelay)
	assert.Equal(t, 16*time.Second, policy.MaxDelay)
	assert.InEpsilon(t, 2.0, policy.Multiplier, 1e-9)
	assert.Equal(t, 20, policy.JitterPercent)
	assert.Contains(t, policy.RetryableStatusCodes, http.StatusTooManyRequests)
}

func TestAggressiveRetryPolicy(t *testing.T) {
	policy := AggressiveRetryPolicy()

	assert.Equal(t, 5, policy.MaxRetries)
	assert.Equal(t, 500*time.Millisecond, policy.InitialDelay)
	assert.Equal(t, 32*time.Second, policy.MaxDelay)
}

func TestConservativeRetryPolicy(t *testing.T) {
	policy := ConservativeRetryPolicy()

	assert.Equal(t, 2, policy.MaxRetries)
	assert.Equal(t, 2*time.Second, policy.InitialDelay)
	assert.Equal(t, 10*time.Second, policy.MaxDelay)
}

func TestRetryPolicy_calculateDelay(t *testing.T) {
	policy := RetryPolicy{
		InitialDelay:  1 * time.Second,
		MaxDelay:      16 * time.Second,
		Multiplier:    2.0,
		JitterPercent: 0, // No jitter for predictable testing
	}

	tests := []struct {
		attempt     int
		expectedMin time.Duration
		expectedMax time.Duration
	}{
		{0, 1 * time.Second, 1 * time.Second},
		{1, 2 * time.Second, 2 * time.Second},
		{2, 4 * time.Second, 4 * time.Second},
		{3, 8 * time.Second, 8 * time.Second},
		{4, 16 * time.Second, 16 * time.Second}, // Capped at maxDelay
		{5, 16 * time.Second, 16 * time.Second}, // Still capped
	}

	for _, tt := range tests {
		t.Run(string(rune(tt.attempt)), func(t *testing.T) {
			delay := policy.calculateDelay(tt.attempt)
			assert.GreaterOrEqual(t, delay, tt.expectedMin)
			assert.LessOrEqual(t, delay, tt.expectedMax)
		})
	}
}

func TestRetryPolicy_calculateDelay_WithJitter(t *testing.T) {
	policy := RetryPolicy{
		InitialDelay:  1 * time.Second,
		MaxDelay:      16 * time.Second,
		Multiplier:    2.0,
		JitterPercent: 20,
	}

	// Run multiple times to ensure jitter varies
	delays := make([]time.Duration, 10)
	for i := 0; i < 10; i++ {
		delays[i] = policy.calculateDelay(0)
	}

	// All delays should be within ±20% of 1 second
	for _, delay := range delays {
		assert.GreaterOrEqual(t, delay, 800*time.Millisecond)
		assert.LessOrEqual(t, delay, 1200*time.Millisecond)
	}

	// At least some variation should exist
	allSame := true
	for i := 1; i < len(delays); i++ {
		if delays[i] != delays[0] {
			allSame = false
			break
		}
	}
	assert.False(t, allSame, "jitter should cause variation in delays")
}

func TestRetryPolicy_IsRetryable(t *testing.T) {
	policy := DefaultRetryPolicy()

	tests := []struct {
		name       string
		statusCode int
		err        error
		expected   bool
	}{
		{"429 Too Many Requests", http.StatusTooManyRequests, nil, true},
		{"500 Internal Server Error", http.StatusInternalServerError, nil, true},
		{"502 Bad Gateway", http.StatusBadGateway, nil, true},
		{"503 Service Unavailable", http.StatusServiceUnavailable, nil, true},
		{"504 Gateway Timeout", http.StatusGatewayTimeout, nil, true},
		{"404 Not Found", http.StatusNotFound, nil, false},
		{"200 OK", http.StatusOK, nil, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := policy.IsRetryable(tt.statusCode, tt.err)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestRetryWithPolicy_Success(t *testing.T) {
	policy := RetryPolicy{
		MaxRetries:   3,
		InitialDelay: 10 * time.Millisecond,
		MaxDelay:     100 * time.Millisecond,
		Multiplier:   2.0,
	}

	attempts := 0
	err := RetryWithPolicy(context.Background(), policy, func() error {
		attempts++
		return nil // Success on first try
	})

	require.NoError(t, err)
	assert.Equal(t, 1, attempts)
}

func TestRetryWithPolicy_SuccessAfterRetries(t *testing.T) {
	policy := RetryPolicy{
		MaxRetries:   3,
		InitialDelay: 10 * time.Millisecond,
		MaxDelay:     100 * time.Millisecond,
		Multiplier:   2.0,
	}

	attempts := 0
	err := RetryWithPolicy(context.Background(), policy, func() error {
		attempts++
		if attempts < 3 {
			return errors.New("temporary failure")
		}
		return nil // Success on third try
	})

	require.NoError(t, err)
	assert.Equal(t, 3, attempts)
}

func TestRetryWithPolicy_ExhaustedRetries(t *testing.T) {
	policy := RetryPolicy{
		MaxRetries:   3,
		InitialDelay: 10 * time.Millisecond,
		MaxDelay:     100 * time.Millisecond,
		Multiplier:   2.0,
	}

	attempts := 0
	err := RetryWithPolicy(context.Background(), policy, func() error {
		attempts++
		return errors.New("persistent failure")
	})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "operation failed after 3 retries")
	assert.Equal(t, 4, attempts) // Initial attempt + 3 retries
}

func TestRetryWithPolicy_ContextCancellation(t *testing.T) {
	policy := RetryPolicy{
		MaxRetries:   10,
		InitialDelay: 100 * time.Millisecond,
		MaxDelay:     1 * time.Second,
		Multiplier:   2.0,
	}

	ctx, cancel := context.WithTimeout(context.Background(), retryPolicyContextTimeout)
	defer cancel()

	attempts := 0
	err := RetryWithPolicy(ctx, policy, func() error {
		attempts++
		return errors.New("failure")
	})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "context")
	assert.Less(t, attempts, 5, "should not complete all retries due to context cancellation")
}

func TestRetryWithPolicyAndResult_Success(t *testing.T) {
	policy := RetryPolicy{
		MaxRetries:   3,
		InitialDelay: 10 * time.Millisecond,
		MaxDelay:     100 * time.Millisecond,
		Multiplier:   2.0,
	}

	result, err := RetryWithPolicyAndResult(context.Background(), policy, func() (string, error) {
		return testSuccessResult, nil
	})

	require.NoError(t, err)
	assert.Equal(t, "success", result)
}

func TestRetryWithPolicyAndResult_ReturnValue(t *testing.T) {
	policy := RetryPolicy{
		MaxRetries:   3,
		InitialDelay: 10 * time.Millisecond,
		MaxDelay:     100 * time.Millisecond,
		Multiplier:   2.0,
	}

	attempts := 0
	result, err := RetryWithPolicyAndResult(context.Background(), policy, func() (int, error) {
		attempts++
		if attempts < 3 {
			return 0, errors.New("failure")
		}
		return 42, nil
	})

	require.NoError(t, err)
	assert.Equal(t, 42, result)
	assert.Equal(t, 3, attempts)
}

func TestHTTPRetry_Success(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("success"))
	}))
	defer server.Close()

	policy := DefaultRetryPolicy()
	client := &http.Client{}
	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, server.URL, nil)
	require.NoError(t, err)

	resp, err := HTTPRetry(context.Background(), policy, client, req)
	require.NoError(t, err)
	defer func() {
		if err := resp.Body.Close(); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	}()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
}

func TestHTTPRetry_RetryableError(t *testing.T) {
	attempts := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		attempts++
		if attempts < 3 {
			w.WriteHeader(http.StatusServiceUnavailable)
		} else {
			w.WriteHeader(http.StatusOK)
		}
	}))
	defer server.Close()

	policy := RetryPolicy{
		MaxRetries:           3,
		InitialDelay:         10 * time.Millisecond,
		MaxDelay:             100 * time.Millisecond,
		Multiplier:           2.0,
		RetryableStatusCodes: []int{http.StatusServiceUnavailable},
	}

	client := &http.Client{}
	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, server.URL, nil)
	require.NoError(t, err)

	resp, err := HTTPRetry(context.Background(), policy, client, req)
	require.NoError(t, err)
	defer func() {
		if err := resp.Body.Close(); err != nil {
			t.Logf("cleanup close error: %v", err)
		}
	}()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
	assert.Equal(t, 3, attempts)
}

func TestRetryBudget_CanRetry(t *testing.T) {
	budget := NewRetryBudget(3)

	assert.True(t, budget.CanRetry())
	budget.RecordRetry()
	assert.True(t, budget.CanRetry())
	budget.RecordRetry()
	assert.True(t, budget.CanRetry())
	budget.RecordRetry()
	assert.False(t, budget.CanRetry())
}

func TestRetryBudget_GetRemainingRetries(t *testing.T) {
	budget := NewRetryBudget(5)

	assert.Equal(t, 5, budget.GetRemainingRetries())
	budget.RecordRetry()
	assert.Equal(t, 4, budget.GetRemainingRetries())
	budget.RecordRetry()
	assert.Equal(t, 3, budget.GetRemainingRetries())
}

func TestRetryBudget_Reset(t *testing.T) {
	budget := NewRetryBudget(3)

	budget.RecordRetry()
	budget.RecordRetry()
	assert.Equal(t, 1, budget.GetRemainingRetries())

	budget.Reset()
	assert.Equal(t, 3, budget.GetRemainingRetries())
}

func TestIdempotencyKey(t *testing.T) {
	key1 := IdempotencyKey("request-123", 1)
	key2 := IdempotencyKey("request-123", 2)

	assert.Contains(t, key1, "request-123-retry-1")
	assert.Contains(t, key2, "request-123-retry-2")
	assert.NotEqual(t, key1, key2)
}

func TestWithIdempotencyKey(t *testing.T) {
	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, "http://example.com", nil)
	require.NoError(t, err)
	key := "test-idempotency-key"

	WithIdempotencyKey(req, key)

	assert.Equal(t, key, req.Header.Get("Idempotency-Key"))
}
