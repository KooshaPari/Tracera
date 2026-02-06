package ratelimit

import (
	"context"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
	"github.com/sony/gobreaker"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	throttleQueueReleaseDelay      = 200 * time.Millisecond
	throttleQueueCompletionTimeout = 3 * time.Second
	throttleCircuitOpenDelay       = 100 * time.Millisecond
	throttleLoadDetectDelay        = 100 * time.Millisecond
	throttleQueueFillDelay         = 50 * time.Millisecond
)

func setupThrottlerRedis(t *testing.T) (*redis.Client, func()) {
	mr, err := miniredis.Run()
	require.NoError(t, err)

	client := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})

	cleanup := func() {
		require.NoError(t, client.Close())
		mr.Close()
	}

	return client, cleanup
}

func TestAdaptiveThrottler_BasicAcquire(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   5 * time.Second,
		MaxConcurrent: 10,
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	// Should acquire immediately when no load
	timeout, release, err := throttler.Acquire(ctx, PriorityNormal)
	assert.NoError(t, err)
	assert.NotNil(t, release)
	assert.Greater(t, timeout, time.Duration(0))

	// Clean up
	release()
}

func TestAdaptiveThrottler_PriorityQueuing(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   3 * time.Second, // Increased to allow for queuing delay
		MaxConcurrent: 2,               // Very small to force queuing
		QueueSizes: map[PriorityLevel]int{
			PriorityLow:    2,
			PriorityNormal: 2,
			PriorityHigh:   2,
			PriorityAdmin:  2,
		},
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	// Acquire all available slots
	releases := make([]func(), 0)
	for i := 0; i < 2; i++ {
		_, release, err := throttler.Acquire(ctx, PriorityNormal)
		assert.NoError(t, err)
		releases = append(releases, release)
	}

	// Next acquire should queue
	done := make(chan bool)
	var queuedRelease func()
	go func() {
		_, release, err := throttler.Acquire(ctx, PriorityHigh)
		if err == nil {
			queuedRelease = release
		}
		done <- true
	}()

	// Release one slot after a delay
	time.Sleep(throttleQueueReleaseDelay)
	if len(releases) > 0 && releases[0] != nil {
		releases[0]()
	}

	// Should complete
	select {
	case <-done:
		// Success - clean up the queued release
		if queuedRelease != nil {
			queuedRelease()
		}
	case <-time.After(throttleQueueCompletionTimeout):
		t.Fatal("Queued request did not complete")
	}

	// Clean up remaining
	for _, release := range releases[1:] {
		if release != nil {
			release()
		}
	}
}

func TestAdaptiveThrottler_CircuitBreakerIntegration(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
		Name:        "test-cb",
		MaxRequests: 1,
		Interval:    1 * time.Second,
		Timeout:     1 * time.Second,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			return counts.ConsecutiveFailures > 2
		},
	})

	config := ThrottleConfig{
		Redis:          client,
		CircuitBreaker: cb,
		BaseTimeout:    1 * time.Second,
		MaxConcurrent:  10,
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	// Should work when circuit is closed
	_, release, err := throttler.Acquire(ctx, PriorityNormal)
	assert.NoError(t, err)
	release()

	// Trip the circuit breaker
	for i := 0; i < 3; i++ {
		_, err := cb.Execute(func() (interface{}, error) {
			return nil, assert.AnError
		})
		assert.Error(t, err)
	}

	// Wait for circuit to open
	time.Sleep(throttleCircuitOpenDelay)

	// Should reject when circuit is open
	_, _, err = throttler.Acquire(ctx, PriorityNormal)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "circuit breaker")
}

func TestAdaptiveThrottler_LoadBasedThrottling(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	config := ThrottleConfig{
		Redis:          client,
		BaseTimeout:    10 * time.Second,
		MaxConcurrent:  10,
		LoadThreshold:  0.8,
		ThrottleFactor: 0.5,
	}

	throttler := NewAdaptiveThrottler(config)

	// Simulate high load by acquiring most slots
	releases := make([]func(), 0)
	ctx := context.Background()
	for i := 0; i < 9; i++ {
		_, release, _ := throttler.Acquire(ctx, PriorityNormal)
		releases = append(releases, release)
	}

	// Give monitor time to detect high load
	time.Sleep(throttleLoadDetectDelay)

	// Timeout should be reduced due to high load
	timeout, release, err := throttler.Acquire(ctx, PriorityNormal)
	assert.NoError(t, err)
	assert.Less(t, timeout, config.BaseTimeout)
	release()

	// Clean up
	for _, rel := range releases {
		rel()
	}
}

func TestAdaptiveThrottler_QueueOverflow(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   100 * time.Millisecond,
		MaxConcurrent: 1,
		QueueSizes: map[PriorityLevel]int{
			PriorityNormal: 1, // Very small queue
		},
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	// Acquire the slot
	_, release, _ := throttler.Acquire(ctx, PriorityNormal)

	// Fill the queue
	go func() {
		_, _, err := throttler.Acquire(ctx, PriorityNormal)
		if err != nil {
			return
		}
	}()

	time.Sleep(throttleQueueFillDelay)

	// Next request should fail (queue full)
	_, _, err := throttler.Acquire(ctx, PriorityNormal)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "queue full")

	release()
}

func TestAdaptiveThrottler_Metrics(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   1 * time.Second,
		MaxConcurrent: 5,
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	// Make some requests
	_, release1, _ := throttler.Acquire(ctx, PriorityNormal)
	_, release2, _ := throttler.Acquire(ctx, PriorityHigh)

	metrics := throttler.GetMetrics()

	assert.NotNil(t, metrics)
	assert.Contains(t, metrics, "total_requests")
	assert.Contains(t, metrics, "current_load")
	assert.Contains(t, metrics, "circuit_state")

	totalRequests := metrics["total_requests"].(int64)
	assert.GreaterOrEqual(t, totalRequests, int64(2))

	release1()
	release2()
}

func TestAdaptiveThrottler_TimeoutCalculation(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   10 * time.Second,
		MaxConcurrent: 10,
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	// Admin priority should get longer timeout
	timeoutAdmin, releaseAdmin, _ := throttler.Acquire(ctx, PriorityAdmin)
	timeoutNormal, releaseNormal, _ := throttler.Acquire(ctx, PriorityNormal)
	timeoutLow, releaseLow, _ := throttler.Acquire(ctx, PriorityLow)

	assert.Greater(t, timeoutAdmin, timeoutNormal)
	assert.Greater(t, timeoutNormal, timeoutLow)

	releaseAdmin()
	releaseNormal()
	releaseLow()
}

func TestAdaptiveThrottler_ContextCancellation(t *testing.T) {
	client, cleanup := setupThrottlerRedis(t)
	defer cleanup()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   5 * time.Second,
		MaxConcurrent: 1,
	}

	throttler := NewAdaptiveThrottler(config)

	// Acquire the only slot
	_, release, _ := throttler.Acquire(context.Background(), PriorityNormal)

	// Try to acquire with cancelled context
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	_, _, err := throttler.Acquire(ctx, PriorityNormal)
	assert.Error(t, err)

	release()
}

func BenchmarkAdaptiveThrottler_Acquire(b *testing.B) {
	mr, _ := miniredis.Run()
	defer mr.Close()

	client := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer func() {
		require.NoError(b, client.Close())
	}()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   1 * time.Second,
		MaxConcurrent: 1000,
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, release, err := throttler.Acquire(ctx, PriorityNormal)
		if err == nil && release != nil {
			release()
		}
	}
}

func BenchmarkAdaptiveThrottler_AcquireParallel(b *testing.B) {
	mr, _ := miniredis.Run()
	defer func() {
		mr.Close()
	}()

	client := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer func() {
		require.NoError(b, client.Close())
	}()

	config := ThrottleConfig{
		Redis:         client,
		BaseTimeout:   1 * time.Second,
		MaxConcurrent: 1000,
	}

	throttler := NewAdaptiveThrottler(config)
	ctx := context.Background()

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			_, release, err := throttler.Acquire(ctx, PriorityNormal)
			if err == nil && release != nil {
				release()
			}
		}
	})
}
