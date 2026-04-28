package resilience

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/sony/gobreaker"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	circuitBreakerInterval      = 100 * time.Millisecond
	circuitBreakerShortInterval = 50 * time.Millisecond
	circuitBreakerOpenWait      = 150 * time.Millisecond
	circuitBreakerCtxTimeout    = 50 * time.Millisecond
	circuitBreakerCtxSleep      = 100 * time.Millisecond
	testResultSuccess           = "success"
)

func TestCircuitBreakerManager_GetOrCreateBreaker(t *testing.T) {
	manager := NewCircuitBreakerManager()

	breaker1 := manager.GetOrCreateBreaker("test-service")
	breaker2 := manager.GetOrCreateBreaker("test-service")

	assert.Same(t, breaker1, breaker2, "should return same breaker instance")
	assert.Equal(t, gobreaker.StateClosed, breaker1.State())
}

func TestCircuitBreakerManager_Execute_Success(t *testing.T) {
	manager := NewCircuitBreakerManager()

	result, err := manager.Execute("test-service", func() (interface{}, error) {
		return testResultSuccess, nil
	})

	require.NoError(t, err)
	assert.Equal(t, testResultSuccess, result)
	assert.Equal(t, gobreaker.StateClosed, manager.GetState("test-service"))
}

func TestCircuitBreakerManager_Execute_Failure(t *testing.T) {
	manager := NewCircuitBreakerManager()
	expectedErr := errors.New("test error")

	_, err := manager.Execute("test-service", func() (interface{}, error) {
		return nil, expectedErr
	})

	require.Error(t, err)
	assert.Equal(t, gobreaker.StateClosed, manager.GetState("test-service"))
}

func TestCircuitBreakerManager_Execute_TripsAfterFailures(t *testing.T) {
	config := DefaultCircuitBreakerConfig()
	config.Interval = circuitBreakerInterval
	manager := NewCircuitBreakerManagerWithConfig(config)

	// Trigger 5 consecutive failures to trip the circuit
	for i := 0; i < 5; i++ {
		_, err := manager.Execute("test-service", func() (interface{}, error) {
			return nil, errors.New("failure")
		})
		require.Error(t, err)
	}

	// Circuit should now be open
	assert.Equal(t, gobreaker.StateOpen, manager.GetState("test-service"))

	// Next request should fail immediately without executing
	_, err := manager.Execute("test-service", func() (interface{}, error) {
		t.Fatal("should not execute when circuit is open")
		return nil, nil
	})
	require.Error(t, err)
}

func TestCircuitBreakerManager_Execute_RecoveryToHalfOpen(t *testing.T) {
	config := DefaultCircuitBreakerConfig()
	config.Timeout = circuitBreakerInterval // Short timeout for testing
	config.Interval = circuitBreakerShortInterval
	manager := NewCircuitBreakerManagerWithConfig(config)

	// Trip the circuit
	for i := 0; i < 5; i++ {
		_, err := manager.Execute("test-service", func() (interface{}, error) {
			return nil, errors.New("failure")
		})
		require.Error(t, err)
	}
	assert.Equal(t, gobreaker.StateOpen, manager.GetState("test-service"))

	// Wait for timeout period
	time.Sleep(circuitBreakerOpenWait)

	// Next request should transition to half-open
	_, err := manager.Execute("test-service", func() (interface{}, error) {
		return testResultSuccess, nil
	})

	require.NoError(t, err)
	// After successful request in half-open, it should close
	assert.Equal(t, gobreaker.StateClosed, manager.GetState("test-service"))
}

func TestCircuitBreakerManager_ExecuteWithContext_Success(t *testing.T) {
	manager := NewCircuitBreakerManager()
	ctx := context.Background()

	result, err := manager.ExecuteWithContext(ctx, "test-service", func() (interface{}, error) {
		return testResultSuccess, nil
	})

	require.NoError(t, err)
	assert.Equal(t, testResultSuccess, result)
}

func TestCircuitBreakerManager_ExecuteWithContext_CancelledContext(t *testing.T) {
	manager := NewCircuitBreakerManager()
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	_, err := manager.ExecuteWithContext(ctx, "test-service", func() (interface{}, error) {
		return testResultSuccess, nil
	})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "context cancelled")
}

func TestCircuitBreakerManager_ExecuteWithContext_Timeout(t *testing.T) {
	manager := NewCircuitBreakerManager()
	ctx, cancel := context.WithTimeout(context.Background(), circuitBreakerCtxTimeout)
	defer cancel()

	_, err := manager.ExecuteWithContext(ctx, "test-service", func() (interface{}, error) {
		time.Sleep(circuitBreakerCtxSleep) // Sleep longer than context timeout
		return testResultSuccess, nil
	})

	require.Error(t, err)
	assert.Contains(t, err.Error(), "context")
}

func TestCircuitBreakerManager_GetAllStates(t *testing.T) {
	manager := NewCircuitBreakerManager()

	manager.GetOrCreateBreaker("service1")
	manager.GetOrCreateBreaker("service2")

	states := manager.GetAllStates()

	assert.Len(t, states, 2)
	assert.Equal(t, gobreaker.StateClosed, states["service1"])
	assert.Equal(t, gobreaker.StateClosed, states["service2"])
}

func TestCircuitBreakerManager_IsHealthy(t *testing.T) {
	config := DefaultCircuitBreakerConfig()
	manager := NewCircuitBreakerManagerWithConfig(config)

	// All circuits closed = healthy
	manager.GetOrCreateBreaker("service1")
	manager.GetOrCreateBreaker("service2")
	assert.True(t, manager.IsHealthy())

	// Trip one circuit
	for i := 0; i < 5; i++ {
		_, err := manager.Execute("service1", func() (interface{}, error) {
			return nil, errors.New("failure")
		})
		require.Error(t, err)
	}

	// Should now be unhealthy
	assert.False(t, manager.IsHealthy())
}

func TestCircuitBreakerManager_GetCounts(t *testing.T) {
	manager := NewCircuitBreakerManager()

	// Execute some requests
	_, err := manager.Execute("test-service", func() (interface{}, error) {
		return testResultSuccess, nil
	})
	require.NoError(t, err)
	_, err = manager.Execute("test-service", func() (interface{}, error) {
		return nil, errors.New("failure")
	})
	require.Error(t, err)

	counts := manager.GetCounts("test-service")
	assert.Equal(t, uint32(2), counts.Requests)
	assert.Equal(t, uint32(1), counts.TotalSuccesses)
	assert.Equal(t, uint32(1), counts.TotalFailures)
}

func TestDefaultCircuitBreakerConfig(t *testing.T) {
	config := DefaultCircuitBreakerConfig()

	assert.Equal(t, uint32(1), config.MaxRequests)
	assert.Equal(t, 10*time.Second, config.Interval)
	assert.Equal(t, 30*time.Second, config.Timeout)
	assert.NotNil(t, config.ReadyToTrip)
	assert.NotNil(t, config.OnStateChange)
}

func TestDefaultCircuitBreakerConfig_ReadyToTrip(t *testing.T) {
	config := DefaultCircuitBreakerConfig()

	tests := []struct {
		name     string
		counts   gobreaker.Counts
		expected bool
	}{
		{
			name: "5 consecutive failures should trip",
			counts: gobreaker.Counts{
				ConsecutiveFailures: 5,
				TotalFailures:       5,
				Requests:            5,
			},
			expected: true,
		},
		{
			name: "5 failures with >50% failure rate should trip",
			counts: gobreaker.Counts{
				ConsecutiveFailures: 2,
				TotalFailures:       5,
				Requests:            8,
			},
			expected: true,
		},
		{
			name: "4 consecutive failures should not trip",
			counts: gobreaker.Counts{
				ConsecutiveFailures: 4,
				TotalFailures:       4,
				Requests:            4,
			},
			expected: false,
		},
		{
			name: "5 failures with <50% failure rate should not trip",
			counts: gobreaker.Counts{
				ConsecutiveFailures: 2,
				TotalFailures:       5,
				Requests:            20,
			},
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := config.ReadyToTrip(tt.counts)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestGlobalManager(t *testing.T) {
	manager1 := GetGlobalManager()
	manager2 := GetGlobalManager()

	assert.Same(t, manager1, manager2, "should return same global instance")
}

func TestConvenienceFunctions(t *testing.T) {
	// Test Execute convenience function
	result, err := Execute("test-service", func() (interface{}, error) {
		return testResultSuccess, nil
	})

	require.NoError(t, err)
	assert.Equal(t, testResultSuccess, result)

	// Test ExecuteWithContext convenience function
	ctx := context.Background()
	result, err = ExecuteWithContext(ctx, "test-service-2", func() (interface{}, error) {
		return testResultSuccess, nil
	})

	require.NoError(t, err)
	assert.Equal(t, testResultSuccess, result)
}
