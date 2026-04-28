package services

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

const (
	crossServiceDelay      = 100 * time.Millisecond
	crossServiceTimeout    = 100 * time.Millisecond
	crossServiceAfterShort = 10 * time.Millisecond
	crossServiceAfterLong  = 150 * time.Millisecond
)

const testItemID2 = "item-2"

// ============================================================================
// ERROR TYPE TESTS
// ============================================================================

func TestServiceUnavailableError(t *testing.T) {
	originalErr := errors.New("connection refused")
	err := &ServiceUnavailableError{
		Service: "ItemService",
		Cause:   originalErr,
	}

	assert.Contains(t, err.Error(), "ItemService")
	assert.Contains(t, err.Error(), "unavailable")
	require.ErrorIs(t, err.Unwrap(), originalErr)
	assert.True(t, IsServiceUnavailable(err))
}

func TestCircuitBreakerOpenError(t *testing.T) {
	until := time.Now().Add(5 * time.Minute)
	err := &CircuitBreakerOpenError{
		Service: "ItemService",
		Until:   until,
	}

	assert.Contains(t, err.Error(), "circuit breaker open")
	assert.Contains(t, err.Error(), "ItemService")
	assert.True(t, IsCircuitBreakerOpen(err))
}

func TestItemNotFoundError(t *testing.T) {
	err := &ItemNotFoundError{ItemID: "test-123"}

	assert.Contains(t, err.Error(), "item not found")
	assert.Contains(t, err.Error(), "test-123")
	assert.True(t, IsItemNotFound(err))
}

// ============================================================================
// HELPER FUNCTION TESTS
// ============================================================================

func TestValidateItemExists_Success(t *testing.T) {
	mockService := &MockItemService{
		OnItemExists: func(_ context.Context, _ string) (bool, error) {
			return true, nil
		},
	}

	err := ValidateItemExists(context.Background(), mockService, "test-123")
	require.NoError(t, err)
}

func TestValidateItemExists_NotFound(t *testing.T) {
	mockService := &MockItemService{
		OnItemExists: func(_ context.Context, _ string) (bool, error) {
			return false, nil
		},
	}

	err := ValidateItemExists(context.Background(), mockService, "test-123")
	require.Error(t, err)
	assert.True(t, IsItemNotFound(err))
}

func TestValidateItemExists_EmptyID(t *testing.T) {
	mockService := &MockItemService{}

	err := ValidateItemExists(context.Background(), mockService, "")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "cannot be empty")
}

func TestGetItemWithFallback_Success(t *testing.T) {
	expectedItem := &models.Item{
		ID:    "test-123",
		Title: "Test Item",
	}

	mockService := &MockItemService{
		OnGetItem: func(_ context.Context, _ string) (*models.Item, error) {
			return expectedItem, nil
		},
	}

	item, err := GetItemWithFallback(context.Background(), mockService, "test-123")
	require.NoError(t, err)
	assert.Equal(t, expectedItem, item)
}

func TestBulkItemValidation_AllExist(t *testing.T) {
	mockService := &MockItemService{
		OnItemExists: func(_ context.Context, _ string) (bool, error) {
			return true, nil
		},
	}

	results, err := BulkItemValidation(context.Background(), mockService, []string{"item-1", "item-2", "item-3"})
	require.NoError(t, err)
	assert.Len(t, results, 3)
	assert.True(t, results["item-1"])
	assert.True(t, results["item-2"])
	assert.True(t, results["item-3"])
}

func TestBulkItemValidation_SomeNotFound(t *testing.T) {
	mockService := &MockItemService{
		OnItemExists: func(_ context.Context, id string) (bool, error) {
			return id != testItemID2, nil // testItemID2 doesn't exist
		},
	}

	results, err := BulkItemValidation(context.Background(), mockService, []string{"item-1", testItemID2, "item-3"})
	require.NoError(t, err)
	assert.Len(t, results, 3)
	assert.True(t, results["item-1"])
	assert.False(t, results[testItemID2])
	assert.True(t, results["item-3"])
}

func TestValidateAllItemsExist_Success(t *testing.T) {
	mockService := &MockItemService{
		OnItemExists: func(_ context.Context, _ string) (bool, error) {
			return true, nil
		},
	}

	err := ValidateAllItemsExist(context.Background(), mockService, []string{"item-1", "item-2"})
	require.NoError(t, err)
}

func TestValidateAllItemsExist_SomeMissing(t *testing.T) {
	mockService := &MockItemService{
		OnItemExists: func(_ context.Context, id string) (bool, error) {
			return id != testItemID2, nil
		},
	}

	err := ValidateAllItemsExist(context.Background(), mockService, []string{"item-1", testItemID2, "item-3"})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "items not found")
	assert.Contains(t, err.Error(), testItemID2)
}

func TestGetMultipleItems_Success(t *testing.T) {
	mockService := &MockItemService{
		OnGetItem: func(_ context.Context, id string) (*models.Item, error) {
			return &models.Item{ID: id, Title: "Item " + id}, nil
		},
	}

	items, err := GetMultipleItems(context.Background(), mockService, []string{"item-1", "item-2"})
	require.NoError(t, err)
	assert.Len(t, items, 2)
	assert.Equal(t, "item-1", items["item-1"].ID)
	assert.Equal(t, "item-2", items["item-2"].ID)
}

// ============================================================================
// RETRY WITH BACKOFF TESTS
// ============================================================================

func TestRetryWithBackoff_SuccessFirstAttempt(t *testing.T) {
	attempts := 0
	fn := func() error {
		attempts++
		return nil
	}

	config := DefaultRetryConfig()
	err := RetryWithBackoff(context.Background(), config, fn)

	require.NoError(t, err)
	assert.Equal(t, 1, attempts)
}

func TestRetryWithBackoff_SuccessAfterRetries(t *testing.T) {
	attempts := 0
	fn := func() error {
		attempts++
		if attempts < 3 {
			return errors.New("temporary error")
		}
		return nil
	}

	config := DefaultRetryConfig()
	config.MaxAttempts = 5
	config.InitialDelay = 1 * time.Millisecond

	err := RetryWithBackoff(context.Background(), config, fn)

	require.NoError(t, err)
	assert.Equal(t, 3, attempts)
}

func TestRetryWithBackoff_MaxAttemptsReached(t *testing.T) {
	attempts := 0
	fn := func() error {
		attempts++
		return errors.New("persistent error")
	}

	config := DefaultRetryConfig()
	config.MaxAttempts = 3
	config.InitialDelay = 1 * time.Millisecond

	err := RetryWithBackoff(context.Background(), config, fn)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "failed after 3 attempts")
	assert.Equal(t, 3, attempts)
}

func TestRetryWithBackoff_ContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	attempts := 0

	fn := func() error {
		attempts++
		if attempts == 1 {
			cancel() // Cancel context on first attempt
		}
		return errors.New("error")
	}

	config := DefaultRetryConfig()
	config.InitialDelay = 100 * time.Millisecond

	err := RetryWithBackoff(ctx, config, fn)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "retry cancelled")
}

// ============================================================================
// CONTEXT PROPAGATION TESTS
// ============================================================================

func TestWithServiceCall(t *testing.T) {
	ctx := context.Background()
	ctx = WithServiceCall(ctx, "TestService")

	callInfo, ok := GetServiceCallInfo(ctx)
	assert.True(t, ok)
	assert.Equal(t, "TestService", callInfo.ServiceName)
	assert.NotEmpty(t, callInfo.TraceID)
	assert.False(t, callInfo.StartTime.IsZero())
}

func TestWithTimeout(t *testing.T) {
	ctx := context.Background()
	ctx, cancel := WithTimeout(ctx, crossServiceTimeout)
	defer cancel()

	select {
	case <-ctx.Done():
		t.Fatal("context should not be done immediately")
	case <-time.After(crossServiceAfterShort):
		// Context still valid
	}

	// Wait for timeout
	<-time.After(crossServiceAfterLong)

	select {
	case <-ctx.Done():
		// Context should be done
	default:
		t.Fatal("context should be done after timeout")
	}
}

func TestWithServiceCallTimeout(t *testing.T) {
	ctx := context.Background()
	ctx, cancel := WithServiceCallTimeout(ctx, "TestService", 100*time.Millisecond)
	defer cancel()

	// Verify service call info is set
	callInfo, ok := GetServiceCallInfo(ctx)
	assert.True(t, ok)
	assert.Equal(t, "TestService", callInfo.ServiceName)

	// Verify timeout is set
	select {
	case <-ctx.Done():
		t.Fatal("context should not be done immediately")
	case <-time.After(crossServiceAfterShort):
		// Context still valid
	}
}

// ============================================================================
// CROSS-SERVICE VALIDATION TESTS
// ============================================================================

func TestValidateLinkCompatibility_Success(t *testing.T) {
	mockService := &MockItemService{
		OnGetItem: func(_ context.Context, id string) (*models.Item, error) {
			return &models.Item{
				ID:        id,
				ProjectID: "project-1",
			}, nil
		},
	}

	err := ValidateLinkCompatibility(context.Background(), mockService, "item-1", "item-2")
	require.NoError(t, err)
}

func TestValidateLinkCompatibility_SameItem(t *testing.T) {
	mockService := &MockItemService{}

	err := ValidateLinkCompatibility(context.Background(), mockService, "item-1", "item-1")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "cannot link item to itself")
}

func TestValidateLinkCompatibility_DifferentProjects(t *testing.T) {
	mockService := &MockItemService{
		OnGetItem: func(_ context.Context, id string) (*models.Item, error) {
			projectID := "project-1"
			if id == testItemID2 {
				projectID = "project-2"
			}
			return &models.Item{
				ID:        id,
				ProjectID: projectID,
			}, nil
		},
	}

	err := ValidateLinkCompatibility(context.Background(), mockService, "item-1", testItemID2)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "same project")
}

func TestGetItemsByProject_Success(t *testing.T) {
	expectedItems := []*models.Item{
		{ID: "item-1", ProjectID: "project-1"},
		{ID: "item-2", ProjectID: "project-1"},
	}

	mockService := &MockItemService{
		OnListItems: func(_ context.Context, _ repository.ItemFilter) ([]*models.Item, error) {
			return expectedItems, nil
		},
	}

	items, err := GetItemsByProject(context.Background(), mockService, "project-1")
	require.NoError(t, err)
	assert.Equal(t, expectedItems, items)
}

// ============================================================================
// CIRCUIT BREAKER TESTS
// ============================================================================

func TestCircuitBreaker_NormalOperation(t *testing.T) {
	cb := NewCircuitBreaker(3, 1*time.Second)
	attempts := 0

	fn := func() error {
		attempts++
		return nil
	}

	err := cb.Execute(fn)
	require.NoError(t, err)
	assert.Equal(t, 1, attempts)
	assert.Equal(t, "closed", cb.state)
}

func TestCircuitBreaker_OpensAfterFailures(t *testing.T) {
	cb := NewCircuitBreaker(3, 100*time.Millisecond)

	fn := func() error {
		return errors.New("failure")
	}

	// First 3 failures should open the circuit
	for i := 0; i < 3; i++ {
		err := cb.Execute(fn)
		require.Error(t, err)
		assert.Equal(t, "failure", err.Error())
	}

	assert.Equal(t, "open", cb.state)

	// Next call should fail immediately
	err := cb.Execute(fn)
	require.Error(t, err)
	assert.True(t, IsCircuitBreakerOpen(err))
}

func TestCircuitBreaker_ResetsAfterTimeout(t *testing.T) {
	cb := NewCircuitBreaker(2, 50*time.Millisecond)

	fn := func() error {
		return errors.New("failure")
	}

	// Open the circuit
	require.Error(t, cb.Execute(fn))
	require.Error(t, cb.Execute(fn))
	assert.Equal(t, "open", cb.state)

	// Wait for reset timeout
	time.Sleep(crossServiceDelay)

	// Should move to half-open
	successFn := func() error {
		return nil
	}
	err := cb.Execute(successFn)
	require.NoError(t, err)
	assert.Equal(t, "closed", cb.state)
}

// ============================================================================
// NOTE: MockItemService is defined in mocks.go
// ============================================================================
