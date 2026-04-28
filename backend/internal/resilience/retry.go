package resilience

import (
	"context"
	"crypto/rand"
	"encoding/binary"
	"errors"
	"fmt"
	"math"
	"net/http"
	"time"
)

const (
	retryDefaultMaxRetries        = 3
	retryDefaultInitialDelay      = 1 * time.Second
	retryDefaultMaxDelay          = 16 * time.Second
	retryAggressiveMaxRetries     = 5
	retryAggressiveInitialDelay   = 500 * time.Millisecond
	retryAggressiveMaxDelay       = 32 * time.Second
	retryConservativeMaxRetries   = 2
	retryConservativeInitialDelay = 2 * time.Second
	retryConservativeMaxDelay     = 10 * time.Second
	retryMultiplierDefault        = 2.0
	retryJitterPercentDefault     = 20
	retryPercentScale             = 100.0
	retryRandomDivisor            = 1000000
)

// RetryPolicy defines the retry behavior
type RetryPolicy struct {
	// MaxRetries is the maximum number of retry attempts
	MaxRetries int

	// InitialDelay is the initial delay before the first retry
	InitialDelay time.Duration

	// MaxDelay is the maximum delay between retries
	MaxDelay time.Duration

	// Multiplier is the exponential backoff multiplier
	Multiplier float64

	// JitterPercent is the percentage of jitter to add (0-100)
	// 20 means ±20% randomization
	JitterPercent int

	// RetryableStatusCodes are HTTP status codes that should trigger a retry
	RetryableStatusCodes []int

	// RetryableErrors are error types that should trigger a retry
	RetryableErrors []error
}

// DefaultRetryPolicy returns the default retry policy
func DefaultRetryPolicy() RetryPolicy {
	return RetryPolicy{
		MaxRetries:    retryDefaultMaxRetries,
		InitialDelay:  retryDefaultInitialDelay,
		MaxDelay:      retryDefaultMaxDelay,
		Multiplier:    retryMultiplierDefault,
		JitterPercent: retryJitterPercentDefault,
		RetryableStatusCodes: []int{
			http.StatusTooManyRequests,     // 429
			http.StatusInternalServerError, // 500
			http.StatusBadGateway,          // 502
			http.StatusServiceUnavailable,  // 503
			http.StatusGatewayTimeout,      // 504
		},
	}
}

// AggressiveRetryPolicy returns a more aggressive retry policy for critical operations
func AggressiveRetryPolicy() RetryPolicy {
	return RetryPolicy{
		MaxRetries:    retryAggressiveMaxRetries,
		InitialDelay:  retryAggressiveInitialDelay,
		MaxDelay:      retryAggressiveMaxDelay,
		Multiplier:    retryMultiplierDefault,
		JitterPercent: retryJitterPercentDefault,
		RetryableStatusCodes: []int{
			http.StatusTooManyRequests,
			http.StatusInternalServerError,
			http.StatusBadGateway,
			http.StatusServiceUnavailable,
			http.StatusGatewayTimeout,
		},
	}
}

// ConservativeRetryPolicy returns a more conservative retry policy
func ConservativeRetryPolicy() RetryPolicy {
	return RetryPolicy{
		MaxRetries:    retryConservativeMaxRetries,
		InitialDelay:  retryConservativeInitialDelay,
		MaxDelay:      retryConservativeMaxDelay,
		Multiplier:    retryMultiplierDefault,
		JitterPercent: retryJitterPercentDefault,
		RetryableStatusCodes: []int{
			http.StatusTooManyRequests,
			http.StatusServiceUnavailable,
			http.StatusGatewayTimeout,
		},
	}
}

// RetryBudget tracks retry attempts to prevent retry storms
type RetryBudget struct {
	maxRetries   int
	currentCount int
}

// NewRetryBudget creates a new retry budget
func NewRetryBudget(maxRetries int) *RetryBudget {
	return &RetryBudget{
		maxRetries:   maxRetries,
		currentCount: 0,
	}
}

// CanRetry returns true if retry budget allows another retry
func (rb *RetryBudget) CanRetry() bool {
	return rb.currentCount < rb.maxRetries
}

// RecordRetry records a retry attempt
func (rb *RetryBudget) RecordRetry() {
	rb.currentCount++
}

// Reset resets the retry budget
func (rb *RetryBudget) Reset() {
	rb.currentCount = 0
}

// GetRemainingRetries returns the number of remaining retries
func (rb *RetryBudget) GetRemainingRetries() int {
	remaining := rb.maxRetries - rb.currentCount
	if remaining < 0 {
		return 0
	}
	return remaining
}

// calculateDelay calculates the delay for the given attempt with exponential backoff and jitter
func (p *RetryPolicy) calculateDelay(attempt int) time.Duration {
	// Calculate exponential backoff: initialDelay * multiplier^attempt
	delay := float64(p.InitialDelay) * math.Pow(p.Multiplier, float64(attempt))

	// Cap at max delay
	if delay > float64(p.MaxDelay) {
		delay = float64(p.MaxDelay)
	}

	// Add jitter to prevent thundering herd using crypto/rand for security
	if p.JitterPercent > 0 {
		jitterRange := delay * float64(p.JitterPercent) / retryPercentScale
		// Use crypto/rand instead of math/rand for security
		randomFloat := cryptoRandFloat64()
		jitter := (randomFloat*2.0 - 1.0) * jitterRange // Random between -jitterRange and +jitterRange
		delay += jitter
	}

	// Ensure delay is non-negative
	if delay < 0 {
		delay = 0
	}

	return time.Duration(delay)
}

// IsRetryable checks if an error or status code is retryable
func (p *RetryPolicy) IsRetryable(statusCode int, err error) bool {
	// Check status code
	if statusCode > 0 {
		for _, code := range p.RetryableStatusCodes {
			if code == statusCode {
				return true
			}
		}
	}

	// Check error type
	if err != nil {
		for _, retryableErr := range p.RetryableErrors {
			if errors.Is(err, retryableErr) {
				return true
			}
		}
	}

	return false
}

// RetryWithPolicy executes a function with retry logic based on the policy
func RetryWithPolicy(ctx context.Context, policy RetryPolicy, operation func() error) error {
	budget := NewRetryBudget(policy.MaxRetries)

	var lastErr error
	for attempt := 0; attempt <= policy.MaxRetries; attempt++ {
		// Check context before attempting
		select {
		case <-ctx.Done():
			return fmt.Errorf("context cancelled before retry attempt %d: %w", attempt, ctx.Err())
		default:
		}

		// Execute operation
		err := operation()
		if err == nil {
			return nil // Success
		}

		lastErr = err

		// Check if we should retry
		if attempt >= policy.MaxRetries {
			break // No more retries left
		}

		if !budget.CanRetry() {
			break // Budget exhausted
		}

		// Record retry
		budget.RecordRetry()

		// Calculate delay
		delay := policy.calculateDelay(attempt)

		// Wait with context cancellation support
		select {
		case <-time.After(delay):
			// Continue to next retry
		case <-ctx.Done():
			return fmt.Errorf("context cancelled during retry delay: %w", ctx.Err())
		}
	}

	return fmt.Errorf("operation failed after %d retries: %w", policy.MaxRetries, lastErr)
}

// RetryWithPolicyAndResult executes a function with retry logic and returns a result
func RetryWithPolicyAndResult[T any](ctx context.Context, policy RetryPolicy, operation func() (T, error)) (T, error) {
	var zero T
	budget := NewRetryBudget(policy.MaxRetries)

	var lastErr error
	for attempt := 0; attempt <= policy.MaxRetries; attempt++ {
		// Check context before attempting
		select {
		case <-ctx.Done():
			return zero, fmt.Errorf("context cancelled before retry attempt %d: %w", attempt, ctx.Err())
		default:
		}

		// Execute operation
		result, err := operation()
		if err == nil {
			return result, nil // Success
		}

		lastErr = err

		// Check if we should retry
		if attempt >= policy.MaxRetries {
			break // No more retries left
		}

		if !budget.CanRetry() {
			break // Budget exhausted
		}

		// Record retry
		budget.RecordRetry()

		// Calculate delay
		delay := policy.calculateDelay(attempt)

		// Wait with context cancellation support
		select {
		case <-time.After(delay):
			// Continue to next retry
		case <-ctx.Done():
			return zero, fmt.Errorf("context cancelled during retry delay: %w", ctx.Err())
		}
	}

	return zero, fmt.Errorf("operation failed after %d retries: %w", policy.MaxRetries, lastErr)
}

// HTTPRetry wraps an HTTP client request with retry logic
func HTTPRetry(ctx context.Context, policy RetryPolicy, client *http.Client, req *http.Request) (*http.Response, error) {
	return RetryWithPolicyAndResult(ctx, policy, func() (*http.Response, error) {
		resp, err := client.Do(req)
		if err != nil {
			return nil, err
		}

		// Check if status code is retryable
		if policy.IsRetryable(resp.StatusCode, nil) {
			if cerr := resp.Body.Close(); cerr != nil {
				return nil, fmt.Errorf("retryable HTTP error: status %d (close error: %w)", resp.StatusCode, cerr)
			}
			return nil, fmt.Errorf("retryable HTTP error: status %d", resp.StatusCode)
		}

		return resp, nil
	})
}

// IdempotencyKey generates a unique idempotency key for safe retries
func IdempotencyKey(requestID string, attempt int) string {
	return fmt.Sprintf("%s-retry-%d-%d", requestID, attempt, time.Now().UnixNano())
}

// WithIdempotencyKey adds an idempotency key header to an HTTP request
func WithIdempotencyKey(req *http.Request, key string) {
	req.Header.Set("Idempotency-Key", key)
}

// cryptoRandFloat64 generates a cryptographically secure random float64 in [0, 1)
func cryptoRandFloat64() float64 {
	var backoff [8]byte
	_, err := rand.Read(backoff[:])
	if err != nil {
		// Fallback to time-based randomness if crypto/rand fails
		return float64(time.Now().UnixNano()%retryRandomDivisor) / float64(retryRandomDivisor)
	}
	// Convert bytes to uint64, then normalize to [0, 1)
	n := binary.BigEndian.Uint64(backoff[:])
	return float64(n) / float64(^uint64(0))
}
