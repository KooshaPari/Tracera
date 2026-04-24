package services

import (
	"context"
	"errors"
	"fmt"
	"strconv"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

const (
	defaultRetryMaxAttempts   = 3
	defaultRetryInitialDelay  = 100 * time.Millisecond
	defaultRetryMaxDelay      = 2 * time.Second
	defaultRetryBackoffFactor = 2.0
)

// ============================================================================
// CROSS-SERVICE API COMMUNICATION PATTERNS
// ============================================================================
// This file provides reusable patterns for service-to-service communication.
// Pattern 4 in SERVICE_IMPLEMENTATION_PATTERNS.md

// ============================================================================
// CUSTOM ERROR TYPES
// ============================================================================

// ServiceUnavailableError indicates a service is temporarily unavailable
type ServiceUnavailableError struct {
	Service string
	Cause   error
}

func (e *ServiceUnavailableError) Error() string {
	return fmt.Sprintf("service %s is unavailable: %v", e.Service, e.Cause)
}

func (e *ServiceUnavailableError) Unwrap() error {
	return e.Cause
}

// IsServiceUnavailable checks if an error is a ServiceUnavailableError
func IsServiceUnavailable(err error) bool {
	var sErr *ServiceUnavailableError
	return errors.As(err, &sErr)
}

// CircuitBreakerOpenError indicates the circuit breaker is open
type CircuitBreakerOpenError struct {
	Service string
	Until   time.Time
}

func (e *CircuitBreakerOpenError) Error() string {
	return fmt.Sprintf("circuit breaker open for service %s until %v", e.Service, e.Until)
}

// IsCircuitBreakerOpen checks if an error is a CircuitBreakerOpenError
func IsCircuitBreakerOpen(err error) bool {
	var cbErr *CircuitBreakerOpenError
	return errors.As(err, &cbErr)
}

// ItemNotFoundError indicates an item was not found
type ItemNotFoundError struct {
	ItemID string
}

func (e *ItemNotFoundError) Error() string {
	return "item not found: " + e.ItemID
}

// IsItemNotFound checks if an error is an ItemNotFoundError
func IsItemNotFound(err error) bool {
	var infErr *ItemNotFoundError
	return errors.As(err, &infErr)
}

// ============================================================================
// HELPER FUNCTIONS FOR COMMON CROSS-SERVICE PATTERNS
// ============================================================================

// ValidateItemExists validates that an item exists by calling ItemService
// This is the canonical way to check item existence across services
func ValidateItemExists(ctx context.Context, itemService ItemService, itemID string) error {
	if itemID == "" {
		return errors.New("item ID cannot be empty")
	}

	exists, err := itemService.ItemExists(ctx, itemID)
	if err != nil {
		return fmt.Errorf("failed to validate item existence: %w", err)
	}

	if !exists {
		return &ItemNotFoundError{ItemID: itemID}
	}

	return nil
}

// GetItemWithFallback attempts to get an item with cache fallback
// Returns item from service, using cache as a secondary source
func GetItemWithFallback(ctx context.Context, itemService ItemService, itemID string) (*models.Item, error) {
	if itemID == "" {
		return nil, errors.New("item ID cannot be empty")
	}

	// Try to get from service (which may use cache internally)
	item, err := itemService.GetItem(ctx, itemID)
	if err == nil {
		return item, nil
	}

	// If service call failed, return the error
	// (services should handle their own cache fallback internally)
	return nil, fmt.Errorf("failed to get item %s: %w", itemID, err)
}

// BulkItemValidation validates multiple items exist in a batch
// Returns map of itemID -> exists, and any errors encountered
func BulkItemValidation(ctx context.Context, itemService ItemService, itemIDs []string) (map[string]bool, error) {
	if len(itemIDs) == 0 {
		return make(map[string]bool), nil
	}

	results := make(map[string]bool)
	var firstError error

	for _, itemID := range itemIDs {
		if itemID == "" {
			continue
		}

		exists, err := itemService.ItemExists(ctx, itemID)
		if err != nil {
			// Store first error but continue checking other items
			if firstError == nil {
				firstError = fmt.Errorf("validation failed for item %s: %w", itemID, err)
			}
			results[itemID] = false
			continue
		}

		results[itemID] = exists
	}

	return results, firstError
}

// ValidateAllItemsExist validates that all items in the list exist
// Returns error immediately if any item is not found
func ValidateAllItemsExist(ctx context.Context, itemService ItemService, itemIDs []string) error {
	results, err := BulkItemValidation(ctx, itemService, itemIDs)
	if err != nil {
		return err
	}

	var missingIDs []string
	for _, itemID := range itemIDs {
		if !results[itemID] {
			missingIDs = append(missingIDs, itemID)
		}
	}

	if len(missingIDs) > 0 {
		return fmt.Errorf("items not found: %v", missingIDs)
	}

	return nil
}

// GetMultipleItems fetches multiple items in a batch
// Returns map of itemID -> item, and any errors encountered
func GetMultipleItems(ctx context.Context, itemService ItemService, itemIDs []string) (map[string]*models.Item, error) {
	if len(itemIDs) == 0 {
		return make(map[string]*models.Item), nil
	}

	results := make(map[string]*models.Item)
	var firstError error

	for _, itemID := range itemIDs {
		if itemID == "" {
			continue
		}

		item, err := itemService.GetItem(ctx, itemID)
		if err != nil {
			// Store first error but continue fetching other items
			if firstError == nil {
				firstError = fmt.Errorf("failed to get item %s: %w", itemID, err)
			}
			continue
		}

		results[itemID] = item
	}

	return results, firstError
}

// ============================================================================
// RETRY WITH BACKOFF HELPER
// ============================================================================

// RetryConfig configures retry behavior
type RetryConfig struct {
	MaxAttempts     int           // Maximum number of retry attempts
	InitialDelay    time.Duration // Initial delay between retries
	MaxDelay        time.Duration // Maximum delay between retries
	BackoffFactor   float64       // Exponential backoff factor (e.g., 2.0)
	RetryableErrors []error       // List of errors that should trigger retry
}

// DefaultRetryConfig returns a sensible default retry configuration
func DefaultRetryConfig() RetryConfig {
	return RetryConfig{
		MaxAttempts:     defaultRetryMaxAttempts,
		InitialDelay:    defaultRetryInitialDelay,
		MaxDelay:        defaultRetryMaxDelay,
		BackoffFactor:   defaultRetryBackoffFactor,
		RetryableErrors: nil,
	}
}

// RetryWithBackoff executes a function with exponential backoff retry logic
func RetryWithBackoff(ctx context.Context, config RetryConfig, fn func() error) error {
	if config.MaxAttempts <= 0 {
		config.MaxAttempts = 1
	}

	var lastErr error
	delay := config.InitialDelay

	for attempt := 1; attempt <= config.MaxAttempts; attempt++ {
		// Execute the function
		err := fn()
		if err == nil {
			return nil
		}

		lastErr = err

		// Check if we should retry based on error type
		if !shouldRetry(err, config.RetryableErrors) {
			return err
		}

		// Don't sleep after the last attempt
		if attempt >= config.MaxAttempts {
			break
		}

		// Check context cancellation before sleeping
		select {
		case <-ctx.Done():
			return fmt.Errorf("retry cancelled: %w", ctx.Err())
		case <-time.After(delay):
			// Calculate next delay with exponential backoff
			delay = time.Duration(float64(delay) * config.BackoffFactor)
			if delay > config.MaxDelay {
				delay = config.MaxDelay
			}
		}
	}

	return fmt.Errorf("operation failed after %d attempts: %w", config.MaxAttempts, lastErr)
}

// shouldRetry determines if an error should trigger a retry
func shouldRetry(err error, retryableErrors []error) bool {
	// If no specific retryable errors are defined, retry on any error
	if len(retryableErrors) == 0 {
		return true
	}

	// Check if error matches any retryable error
	for _, retryableErr := range retryableErrors {
		if errors.Is(err, retryableErr) {
			return true
		}
	}

	// Check for specific error types that are commonly retryable
	if IsServiceUnavailable(err) {
		return true
	}

	return false
}

// ============================================================================
// CONTEXT PROPAGATION PATTERNS
// ============================================================================

// contextKey is a type for context keys to avoid collisions
type contextKey string

const (
	// Context keys for service calls
	serviceCallKey  contextKey = "service_call"
	traceIDKey      contextKey = "trace_id"
	serviceNameKey  contextKey = "service_name"
	requestStartKey contextKey = "request_start"
)

// ServiceCallInfo contains metadata about a service call
type ServiceCallInfo struct {
	TraceID     string
	ServiceName string
	StartTime   time.Time
}

// WithServiceCall adds tracing metadata to context for cross-service calls
// This enables distributed tracing across service boundaries
func WithServiceCall(ctx context.Context, serviceName string) context.Context {
	// Get or generate trace ID
	traceID, ok := ctx.Value(traceIDKey).(string)
	if !ok || traceID == "" {
		traceID = generateTraceID()
	}

	callInfo := ServiceCallInfo{
		TraceID:     traceID,
		ServiceName: serviceName,
		StartTime:   time.Now(),
	}

	ctx = context.WithValue(ctx, serviceCallKey, callInfo)
	ctx = context.WithValue(ctx, traceIDKey, traceID)
	ctx = context.WithValue(ctx, serviceNameKey, serviceName)
	ctx = context.WithValue(ctx, requestStartKey, time.Now())

	return ctx
}

// GetServiceCallInfo retrieves service call metadata from context
func GetServiceCallInfo(ctx context.Context) (*ServiceCallInfo, bool) {
	callInfo, ok := ctx.Value(serviceCallKey).(ServiceCallInfo)
	return &callInfo, ok
}

// WithTimeout creates a context with a timeout for service calls
// This prevents calls from hanging indefinitely
func WithTimeout(ctx context.Context, timeout time.Duration) (context.Context, context.CancelFunc) {
	return context.WithTimeout(ctx, timeout)
}

// WithServiceCallTimeout combines service call metadata with timeout
func WithServiceCallTimeout(ctx context.Context, serviceName string, timeout time.Duration) (context.Context, context.CancelFunc) {
	ctx = WithServiceCall(ctx, serviceName)
	return WithTimeout(ctx, timeout)
}

// generateTraceID generates a simple trace ID for request tracking
func generateTraceID() string {
	return "trace-" + strconv.FormatInt(time.Now().UnixNano(), 10)
}

// ============================================================================
// CROSS-SERVICE VALIDATION HELPERS
// ============================================================================

// ValidateLinkCompatibility checks if two items can be linked
// This encapsulates common validation logic used across services
func ValidateLinkCompatibility(ctx context.Context, itemService ItemService, sourceID, targetID string) error {
	// Validate IDs are not empty
	if sourceID == "" || targetID == "" {
		return errors.New("source and target IDs are required")
	}

	// Validate items are not the same
	if sourceID == targetID {
		return errors.New("cannot link item to itself")
	}

	// Validate both items exist
	sourceItem, err := itemService.GetItem(ctx, sourceID)
	if err != nil {
		return fmt.Errorf("source item not found: %w", err)
	}

	targetItem, err := itemService.GetItem(ctx, targetID)
	if err != nil {
		return fmt.Errorf("target item not found: %w", err)
	}

	// Validate items are in the same project
	if sourceItem.ProjectID != targetItem.ProjectID {
		return errors.New("items must be in the same project")
	}

	return nil
}

// GetItemsByProject fetches all items for a project using ItemService
// This is a common pattern for cross-service data retrieval
func GetItemsByProject(ctx context.Context, itemService ItemService, projectID string) ([]*models.Item, error) {
	if projectID == "" {
		return nil, errors.New("project ID cannot be empty")
	}

	filter := repository.ItemFilter{
		ProjectID: &projectID,
	}

	items, err := itemService.ListItems(ctx, filter)
	if err != nil {
		return nil, fmt.Errorf("failed to get items for project %s: %w", projectID, err)
	}

	return items, nil
}

// ============================================================================
// CIRCUIT BREAKER PATTERN (SIMPLIFIED)
// ============================================================================

// CircuitBreaker provides a simple circuit breaker implementation
type CircuitBreaker struct {
	maxFailures int
	resetTime   time.Duration
	failures    int
	lastFailure time.Time
	state       string // "closed", "open", "half-open"
}

// NewCircuitBreaker creates a new circuit breaker
func NewCircuitBreaker(maxFailures int, resetTime time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		maxFailures: maxFailures,
		resetTime:   resetTime,
		state:       "closed",
	}
}

// Execute executes a function through the circuit breaker
func (cb *CircuitBreaker) Execute(fn func() error) error {
	// Check if circuit is open
	if cb.state == statusOpen {
		if time.Since(cb.lastFailure) > cb.resetTime {
			// Move to half-open state
			cb.state = "half-open"
		} else {
			return &CircuitBreakerOpenError{
				Service: "unknown",
				Until:   cb.lastFailure.Add(cb.resetTime),
			}
		}
	}

	// Execute function
	err := fn()
	if err != nil {
		cb.recordFailure()
		return err
	}

	// Success - reset circuit breaker
	cb.recordSuccess()
	return nil
}

func (cb *CircuitBreaker) recordFailure() {
	cb.failures++
	cb.lastFailure = time.Now()

	if cb.failures >= cb.maxFailures {
		cb.state = statusOpen
	}
}

func (cb *CircuitBreaker) recordSuccess() {
	cb.failures = 0
	cb.state = "closed"
}

// ============================================================================
// HELPER COUNT: 15 HELPERS TOTAL
// ============================================================================
// 1. ValidateItemExists
// 2. GetItemWithFallback
// 3. BulkItemValidation
// 4. ValidateAllItemsExist
// 5. GetMultipleItems
// 6. RetryWithBackoff
// 7. WithServiceCall
// 8. GetServiceCallInfo
// 9. WithTimeout
// 10. WithServiceCallTimeout
// 11. ValidateLinkCompatibility
// 12. GetItemsByProject
// 13. IsServiceUnavailable
// 14. IsCircuitBreakerOpen
// 15. IsItemNotFound
// ============================================================================
