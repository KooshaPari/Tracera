package ratelimit

import (
	"context"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const slidingWindowSleep = 2100 * time.Millisecond

func setupTestRedis(t *testing.T) (*redis.Client, func()) {
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

func TestSlidingWindowLimiter_BasicLimit(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 5)
	ctx := context.Background()

	// Should allow first 5 requests
	for i := 0; i < 5; i++ {
		allowed, remaining, _, err := limiter.Allow(ctx, "test-key")
		require.NoError(t, err)
		assert.True(t, allowed, "Request %d should be allowed", i+1)
		assert.Equal(t, 4-i, remaining, "Remaining should be %d", 4-i)
	}

	// 6th request should be denied
	allowed, remaining, resetTime, err := limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	assert.False(t, allowed, "6th request should be denied")
	assert.Equal(t, 0, remaining)
	assert.True(t, resetTime.After(time.Now()))
}

func TestSlidingWindowLimiter_SlidingWindow(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	// Use a 2-second window for faster testing
	limiter := NewSlidingWindowLimiter(client, 2*time.Second, 3)
	ctx := context.Background()

	// Make 3 requests (use up the limit)
	for i := 0; i < 3; i++ {
		allowed, _, _, err := limiter.Allow(ctx, "test-key")
		require.NoError(t, err)
		assert.True(t, allowed)
	}

	// 4th request should be denied
	var allowed bool
	var err error
	allowed, _, _, err = limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	assert.False(t, allowed)

	// Wait for window to slide (2.1 seconds)
	time.Sleep(slidingWindowSleep)

	// Should allow requests again
	allowed, _, _, err = limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	assert.True(t, allowed, "Request should be allowed after window slides")
}

func TestSlidingWindowLimiter_MultipleKeys(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 2)
	ctx := context.Background()

	// Use up limit for key1
	allowed, _, _, err := limiter.Allow(ctx, "key1")
	require.NoError(t, err)
	assert.True(t, allowed)
	allowed, _, _, err = limiter.Allow(ctx, "key1")
	require.NoError(t, err)
	assert.True(t, allowed)
	allowed, _, _, err = limiter.Allow(ctx, "key1")
	require.NoError(t, err)
	assert.False(t, allowed)

	// key2 should still have its full quota
	allowed, _, _, err = limiter.Allow(ctx, "key2")
	require.NoError(t, err)
	assert.True(t, allowed)
	allowed, _, _, err = limiter.Allow(ctx, "key2")
	require.NoError(t, err)
	assert.True(t, allowed)
}

func TestSlidingWindowLimiter_AllowN(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 10)
	ctx := context.Background()

	// Request 5 slots at once
	allowed, remaining, _, err := limiter.AllowN(ctx, "test-key", 5)
	require.NoError(t, err)
	assert.True(t, allowed)
	assert.Equal(t, 5, remaining)

	// Request another 5 slots
	allowed, remaining, _, err = limiter.AllowN(ctx, "test-key", 5)
	require.NoError(t, err)
	assert.True(t, allowed)
	assert.Equal(t, 0, remaining)

	// Request 1 more should be denied
	allowed, _, _, err = limiter.AllowN(ctx, "test-key", 1)
	require.NoError(t, err)
	assert.False(t, allowed)
}

func TestSlidingWindowLimiter_GetUsage(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 10)
	ctx := context.Background()

	// Initial usage should be 0
	usage, err := limiter.GetUsage(ctx, "test-key")
	require.NoError(t, err)
	assert.Equal(t, int64(0), usage)

	// Make 3 requests
	for i := 0; i < 3; i++ {
		_, _, _, err = limiter.Allow(ctx, "test-key")
		require.NoError(t, err)
	}

	// Usage should be 3
	usage, err = limiter.GetUsage(ctx, "test-key")
	require.NoError(t, err)
	assert.Equal(t, int64(3), usage)
}

func TestSlidingWindowLimiter_Reset(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 2)
	ctx := context.Background()

	// Use up the limit
	_, _, _, err := limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	_, _, _, err = limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	allowed, _, _, err := limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	assert.False(t, allowed)

	// Reset the key
	err = limiter.Reset(ctx, "test-key")
	require.NoError(t, err)

	// Should allow requests again
	allowed, _, _, err = limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	assert.True(t, allowed)
}

func TestSlidingWindowLimiter_AccuracyUnderLoad(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 100)
	ctx := context.Background()

	// Make exactly 100 requests
	allowedCount := 0
	for i := 0; i < 100; i++ {
		allowed, _, _, err := limiter.Allow(ctx, "test-key")
		require.NoError(t, err)
		if allowed {
			allowedCount++
		}
	}

	assert.Equal(t, 100, allowedCount, "Should allow exactly 100 requests")

	// 101st request should be denied
	allowed, _, _, err := limiter.Allow(ctx, "test-key")
	require.NoError(t, err)
	assert.False(t, allowed)
}

func TestSlidingWindowLimiter_ConcurrentRequests(t *testing.T) {
	client, cleanup := setupTestRedis(t)
	defer cleanup()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 50)
	ctx := context.Background()

	// Make 100 concurrent requests
	results := make(chan bool, 100)
	for i := 0; i < 100; i++ {
		go func() {
			allowed, _, _, err := limiter.Allow(ctx, "concurrent-key")
			if err != nil {
				results <- false
				return
			}
			results <- allowed
		}()
	}

	// Count allowed requests
	allowedCount := 0
	for i := 0; i < 100; i++ {
		if <-results {
			allowedCount++
		}
	}

	// Should allow exactly 50 requests (within a small margin for race conditions)
	assert.InDelta(t, 50, allowedCount, 2, "Should allow approximately 50 requests")
}

func BenchmarkSlidingWindowLimiter_Allow(b *testing.B) {
	mr, err := miniredis.Run()
	require.NoError(b, err)
	defer mr.Close()

	client := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer func() {
		require.NoError(b, client.Close())
	}()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 10000)
	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _, _, err := limiter.Allow(ctx, "bench-key")
		if err != nil {
			b.Fatalf("Allow failed: %v", err)
		}
	}
}

func BenchmarkSlidingWindowLimiter_AllowParallel(b *testing.B) {
	mr, err := miniredis.Run()
	require.NoError(b, err)
	defer mr.Close()

	client := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer func() {
		require.NoError(b, client.Close())
	}()

	limiter := NewSlidingWindowLimiter(client, 1*time.Minute, 100000)
	ctx := context.Background()

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		for pb.Next() {
			_, _, _, err := limiter.Allow(ctx, "bench-parallel-key")
			if err != nil {
				b.Fatalf("Allow failed: %v", err)
			}
			i++
		}
	})
}
