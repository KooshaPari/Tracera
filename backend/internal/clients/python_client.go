// Package clients provides HTTP clients for external service communication.
package clients

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"time"

	"github.com/hashicorp/go-retryablehttp"
	"github.com/sony/gobreaker"

	"github.com/kooshapari/tracertm-backend/internal/cache"
)

const (
	pythonRetryMax                = 3
	pythonRetryWaitMinimum        = 1 * time.Second
	pythonRetryWaitMaximum        = 5 * time.Second
	pythonHTTPTimeout             = 30 * time.Second
	pythonCBMaxRequests           = 3
	pythonCBInterval              = 60 * time.Second
	pythonCBTimeout               = 30 * time.Second
	pythonCBMinRequests           = 3
	pythonCBConsecutiveFailures   = 5
	pythonCBFailureRatioThreshold = 0.6
)

// PythonServiceClient provides HTTP client for Python backend communication
type PythonServiceClient struct {
	httpClient     *retryablehttp.Client
	baseURL        string
	cache          cache.Cache
	circuitBreaker *gobreaker.CircuitBreaker
	serviceToken   string
}

// NewPythonServiceClient creates a new Python service client
func NewPythonServiceClient(baseURL string, serviceToken string, cache cache.Cache) *PythonServiceClient {
	// Configure retryable HTTP client
	retryClient := retryablehttp.NewClient()
	retryClient.RetryMax = pythonRetryMax
	retryClient.RetryWaitMin = pythonRetryWaitMinimum
	retryClient.RetryWaitMax = pythonRetryWaitMaximum
	retryClient.HTTPClient.Timeout = pythonHTTPTimeout

	// Configure circuit breaker
	cbSettings := gobreaker.Settings{
		Name:        "PythonService",
		MaxRequests: pythonCBMaxRequests,
		Interval:    pythonCBInterval,
		Timeout:     pythonCBTimeout,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			// Trip circuit after 5 consecutive failures
			failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
			return counts.Requests >= pythonCBMinRequests &&
				(counts.ConsecutiveFailures >= pythonCBConsecutiveFailures ||
					failureRatio >= pythonCBFailureRatioThreshold)
		},
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			// Log state changes (can be extended with proper logging)
			slog.Info("Circuit breaker ' ' changed from to", "name", name, "detail", from, "detail", to)
		},
	}

	return &PythonServiceClient{
		httpClient:     retryClient,
		baseURL:        baseURL,
		cache:          cache,
		circuitBreaker: gobreaker.NewCircuitBreaker(cbSettings),
		serviceToken:   serviceToken,
	}
}

// DelegateRequest makes an HTTP request to Python backend with retry, circuit breaker, and caching
func (pythonClient *PythonServiceClient) DelegateRequest(
	ctx context.Context,
	method string,
	path string,
	body interface{},
	response interface{},
	cacheable bool,
	cacheKey string,
	_ time.Duration,
) error {
	if pythonClient.tryCacheGet(ctx, cacheable, cacheKey, response) {
		return nil
	}

	// Execute request through circuit breaker
	result, err := pythonClient.circuitBreaker.Execute(func() (interface{}, error) {
		return pythonClient.executeRequest(ctx, method, path, body)
	})
	if err != nil {
		return fmt.Errorf("circuit breaker execution failed: %w", err)
	}

	// Parse response
	respBody, ok := result.([]byte)
	if !ok {
		return errors.New("unexpected response type from circuit breaker")
	}

	if err := json.Unmarshal(respBody, response); err != nil {
		return fmt.Errorf("failed to unmarshal response: %w", err)
	}

	// Cache the response if cacheable
	pythonClient.tryCacheSet(ctx, cacheable, cacheKey, response)

	return nil
}

func (pythonClient *PythonServiceClient) tryCacheGet(
	ctx context.Context,
	cacheable bool,
	cacheKey string,
	response interface{},
) bool {
	if !cacheable || cacheKey == "" || pythonClient.cache == nil {
		return false
	}
	if err := pythonClient.cache.Get(ctx, cacheKey, response); err == nil {
		return true
	}
	return false
}

func (pythonClient *PythonServiceClient) tryCacheSet(
	ctx context.Context,
	cacheable bool,
	cacheKey string,
	response interface{},
) {
	if !cacheable || cacheKey == "" || pythonClient.cache == nil {
		return
	}
	if err := pythonClient.cache.Set(ctx, cacheKey, response); err != nil {
		slog.Error("Warning: failed to cache response", "error", err)
	}
}

// executeRequest performs the actual HTTP request
func (pythonClient *PythonServiceClient) executeRequest(
	ctx context.Context,
	method string,
	path string,
	body interface{},
) ([]byte, error) {
	url := pythonClient.baseURL + path

	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewBuffer(jsonData)
	}

	req, err := retryablehttp.NewRequestWithContext(ctx, method, url, reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")
	if pythonClient.serviceToken != "" {
		req.Header.Set("Authorization", "Bearer "+pythonClient.serviceToken)
	}

	resp, err := pythonClient.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("error closing python response", "error", err)
		}
	}()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// GenerateCacheKey creates a consistent cache key from request parameters
func GenerateCacheKey(prefix, method, path string, body interface{}) string {
	hasher := sha256.New()
	hasher.Write([]byte(prefix))
	hasher.Write([]byte(method))
	hasher.Write([]byte(path))
	if body != nil {
		if jsonBody, err := json.Marshal(body); err == nil {
			hasher.Write(jsonBody)
		}
	}
	return prefix + ":" + hex.EncodeToString(hasher.Sum(nil)[:16])
}

// GetCircuitBreakerState returns the current state of the circuit breaker
func (pythonClient *PythonServiceClient) GetCircuitBreakerState() gobreaker.State {
	return pythonClient.circuitBreaker.State()
}

// Note: Circuit breaker reset is not implemented as gobreaker doesn't expose Settings
// For testing, create a new client instance instead
