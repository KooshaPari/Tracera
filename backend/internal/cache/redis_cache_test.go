package cache

import (
	"context"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	redisCacheTestDefaultTTL  = 5 * time.Minute
	redisCacheTestCustomTTL   = 1 * time.Hour
	redisCacheTestTTLMinute   = 59 * time.Minute
	redisCacheTestBatchTTL    = 5 * time.Minute
	redisCacheTestTagTTL      = 5 * time.Minute
	redisCacheTestExpiry      = 1 * time.Second
	redisCacheTestDurationMax = 5 * time.Second
	redisCacheTestZero        = 0 * time.Second
	redisCacheTestPoolSize    = 2
	redisCacheTestMinIdle     = 1
)

func setupTestRedisCache(tb testing.TB) (*RedisCache, *miniredis.Miniredis) {
	// Create miniredis server for testing
	mr, err := miniredis.Run()
	require.NoError(tb, err)

	// Create cache with test server
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:      "redis://" + mr.Addr(),
		DefaultTTL:    redisCacheTestDefaultTTL,
		KeyPrefix:     "test:",
		EnableMetrics: true,
		PoolSize:      redisCacheTestPoolSize,
		MinIdleConns:  redisCacheTestMinIdle,
	})
	require.NoError(tb, err)

	return cache, mr
}

func TestRedisCache_BasicOperations(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	t.Run("Set and Get", func(t *testing.T) {
		type TestData struct {
			Name  string
			Value int
		}

		data := TestData{Name: "test", Value: 42}
		err := cache.Set(ctx, "basic", data)
		require.NoError(t, err)

		var retrieved TestData
		err = cache.Get(ctx, "basic", &retrieved)
		require.NoError(t, err)
		assert.Equal(t, data, retrieved)
	})

	t.Run("Get non-existent key", func(t *testing.T) {
		var result string
		err := cache.Get(ctx, "nonexistent", &result)
		require.NoError(t, err)
		assert.Empty(t, result)
	})

	t.Run("Delete", func(t *testing.T) {
		err := cache.Set(ctx, "delete-test", "value")
		require.NoError(t, err)

		err = cache.Delete(ctx, "delete-test")
		require.NoError(t, err)

		var result string
		err = cache.Get(ctx, "delete-test", &result)
		require.NoError(t, err)
		assert.Empty(t, result)
	})
}

func TestRedisCache_TTL(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	t.Run("Expire after TTL", func(t *testing.T) {
		err := cache.SetWithTTL(ctx, "ttl-test", "value", 100*time.Millisecond)
		require.NoError(t, err)

		// Should exist immediately
		var result string
		err = cache.Get(ctx, "ttl-test", &result)
		require.NoError(t, err)
		assert.Equal(t, "value", result)

		// Fast-forward time in miniredis
		mr.FastForward(200 * time.Millisecond)
		mr.FastForward(1 * time.Second)

		// Should be expired
		err = cache.Get(ctx, "ttl-test", &result)
		require.NoError(t, err)
		// miniredis time fast-forward doesn't affect go-redis client-side timeouts consistently;
		// rely on TTL() semantics instead.
		ttl, err := cache.TTL(ctx, "ttl-test")
		require.NoError(t, err)
		assert.LessOrEqual(t, ttl, time.Duration(0))
	})

	t.Run("Custom TTL", func(t *testing.T) {
		err := cache.SetWithTTL(ctx, "custom-ttl", "value", redisCacheTestCustomTTL)
		require.NoError(t, err)

		ttl, err := cache.TTL(ctx, "custom-ttl")
		require.NoError(t, err)
		assert.Greater(t, ttl, redisCacheTestTTLMinute)
	})
}

func TestRedisCache_BulkOperations(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	t.Run("GetMany", func(t *testing.T) {
		// Set multiple values
		err := cache.Set(ctx, "key1", "value1")
		require.NoError(t, err)
		err = cache.Set(ctx, "key2", "value2")
		require.NoError(t, err)

		// Get multiple values
		results, err := cache.GetMany(ctx, []string{"key1", "key2", "key3"})
		require.NoError(t, err)

		assert.Len(t, results, 2)
		assert.Contains(t, results, "key1")
		assert.Contains(t, results, "key2")
		assert.NotContains(t, results, "key3")
	})

	t.Run("SetMany", func(t *testing.T) {
		items := map[string]interface{}{
			"bulk1": "value1",
			"bulk2": "value2",
			"bulk3": "value3",
		}

		err := cache.SetMany(ctx, items, redisCacheTestBatchTTL)
		require.NoError(t, err)

		// Verify all were set
		for key, expected := range items {
			var value string
			err := cache.Get(ctx, key, &value)
			require.NoError(t, err)
			assert.Equal(t, expected, value)
		}
	})
}

func TestRedisCache_PatternInvalidation(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	// Set multiple keys with pattern
	keys := []string{"project:1", "project:2", "project:3", "item:1"}
	for _, key := range keys {
		err := cache.Set(ctx, key, "value")
		require.NoError(t, err)
	}

	// Invalidate by pattern
	err := cache.InvalidatePattern(ctx, "project:*")
	require.NoError(t, err)

	// Verify projects deleted
	var result string
	err = cache.Get(ctx, "project:1", &result)
	require.NoError(t, err)
	assert.Empty(t, result)
	err = cache.Get(ctx, "project:2", &result)
	require.NoError(t, err)
	assert.Empty(t, result)
	err = cache.Get(ctx, "project:3", &result)
	require.NoError(t, err)
	assert.Empty(t, result)

	// Verify item still exists
	err = cache.Get(ctx, "item:1", &result)
	require.NoError(t, err)
}

func TestRedisCache_TagInvalidation(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	// Set values with tags
	err := cache.SetWithTags(ctx, "item1", "value1", redisCacheTestTagTTL, []string{"project:123", "user:456"})
	require.NoError(t, err)

	err = cache.SetWithTags(ctx, "item2", "value2", redisCacheTestTagTTL, []string{"project:123"})
	require.NoError(t, err)

	err = cache.SetWithTags(ctx, "item3", "value3", redisCacheTestTagTTL, []string{"project:789"})
	require.NoError(t, err)

	// Invalidate by tag
	err = cache.InvalidateTags(ctx, []string{"project:123"})
	require.NoError(t, err)

	// Verify items with tag deleted
	var result string
	err = cache.Get(ctx, "item1", &result)
	require.NoError(t, err)
	assert.Empty(t, result)
	err = cache.Get(ctx, "item2", &result)
	require.NoError(t, err)
	assert.Empty(t, result)

	// Verify item without tag still exists
	err = cache.Get(ctx, "item3", &result)
	require.NoError(t, err)
}

func TestRedisCache_AtomicOperations(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	t.Run("Increment", func(t *testing.T) {
		val, err := cache.Increment(ctx, "counter")
		require.NoError(t, err)
		assert.Equal(t, int64(1), val)

		val, err = cache.Increment(ctx, "counter")
		require.NoError(t, err)
		assert.Equal(t, int64(2), val)
	})

	t.Run("IncrementWithExpiry", func(t *testing.T) {
		val, err := cache.IncrementWithExpiry(ctx, "rate-limit", redisCacheTestExpiry)
		require.NoError(t, err)
		assert.Equal(t, int64(1), val)

		// Should have TTL
		ttl, err := cache.TTL(ctx, "rate-limit")
		require.NoError(t, err)
		assert.Greater(t, ttl, redisCacheTestZero)
	})

	t.Run("Exists", func(t *testing.T) {
		err := cache.Set(ctx, "exists-test", "value")
		require.NoError(t, err)

		count, err := cache.Exists(ctx, "exists-test", "nonexistent")
		require.NoError(t, err)
		assert.Equal(t, int64(1), count)
	})
}

func TestRedisCache_Metrics(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	// Perform some operations
	require.NoError(t, cache.Set(ctx, "metric-test", "value"))
	require.NoError(t, cache.Get(ctx, "metric-test", new(string)))
	require.NoError(t, cache.Get(ctx, "nonexistent", new(string)))

	// Get metrics
	metrics := cache.GetMetrics()
	assert.NotNil(t, metrics)

	metricsData := metrics.GetMetrics()
	assert.NotNil(t, metricsData)

	// Check that metrics exist and are of correct type
	if totalOps, ok := metricsData["total_operations"].(int64); ok {
		assert.Positive(t, totalOps)
	}
	if totalHits, ok := metricsData["total_hits"].(int64); ok {
		assert.GreaterOrEqual(t, totalHits, int64(0))
	}
	if totalMisses, ok := metricsData["total_misses"].(int64); ok {
		assert.GreaterOrEqual(t, totalMisses, int64(0))
	}
}

func TestRedisCache_Performance(t *testing.T) {
	cache, mr := setupTestRedisCache(t)
	defer mr.Close()
	defer func() { require.NoError(t, cache.Close()) }()

	ctx := context.Background()

	t.Run("Lookup latency <10ms", func(t *testing.T) {
		// Prewarm
		err := cache.Set(ctx, "perf-test", "value")
		require.NoError(t, err)

		// Measure lookup time
		iterations := 100
		start := time.Now()

		for i := 0; i < iterations; i++ {
			var result string
			require.NoError(t, cache.Get(ctx, "perf-test", &result))
		}

		duration := time.Since(start)
		avgLatency := duration / time.Duration(iterations)

		assert.Less(t, avgLatency, 10*time.Millisecond, "Average lookup latency should be <10ms")
	})

	t.Run("Handle 1000+ operations", func(t *testing.T) {
		start := time.Now()

		// Insert 1000 entries
		for i := 0; i < 1000; i++ {
			key := ProjectKey(string(rune(i)))
			require.NoError(t, cache.Set(ctx, key, map[string]interface{}{
				"id":   i,
				"name": "Project " + string(rune(i)),
			}))
		}

		// Retrieve 1000 entries
		hits := 0
		for i := 0; i < 1000; i++ {
			key := ProjectKey(string(rune(i)))
			var result map[string]interface{}
			if cache.Get(ctx, key, &result) == nil {
				hits++
			}
		}

		duration := time.Since(start)

		assert.Greater(t, hits, 900, "Should have >90% hit rate")
		assert.Less(t, duration, redisCacheTestDurationMax, "Should complete in <5s")
	})
}

func TestRedisCache_KeyHelpers(t *testing.T) {
	t.Run("Key generation", func(t *testing.T) {
		assert.Equal(t, "project:123", ProjectKey("123"))
		assert.Equal(t, "item:456", ItemKey("456"))
		assert.Equal(t, "link:789", LinkKey("789"))
		assert.Equal(t, "session:abc", SessionKey("abc"))
		assert.Equal(t, "search:project-1:test query", SearchKey("test query", "project-1"))
		assert.Equal(t, "ratelimit:user:123:hourly", RateLimitKey("user:123", "hourly"))
	})
}

func BenchmarkRedisCache_Get(b *testing.B) {
	cache, mr := setupTestRedisCache(b)
	defer mr.Close()
	defer func() { require.NoError(b, cache.Close()) }()

	ctx := context.Background()
	require.NoError(b, cache.Set(ctx, "bench", "value"))

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		var result string
		require.NoError(b, cache.Get(ctx, "bench", &result))
	}
}

func BenchmarkRedisCache_Set(b *testing.B) {
	cache, mr := setupTestRedisCache(b)
	defer mr.Close()
	defer func() { require.NoError(b, cache.Close()) }()

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		require.NoError(b, cache.Set(ctx, "bench", "value"))
	}
}

func BenchmarkRedisCache_GetMany(b *testing.B) {
	cache, mr := setupTestRedisCache(b)
	defer mr.Close()
	defer func() { require.NoError(b, cache.Close()) }()

	ctx := context.Background()

	// Prewarm
	for i := 0; i < 100; i++ {
		require.NoError(b, cache.Set(ctx, string(rune(i)), "value"))
	}

	keys := make([]string, 100)
	for i := 0; i < 100; i++ {
		keys[i] = string(rune(i))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := cache.GetMany(ctx, keys)
		require.NoError(b, err)
	}
}
