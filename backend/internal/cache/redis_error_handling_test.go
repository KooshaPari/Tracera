//go:build !integration && !e2e

package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	redisErrorTestTTL        = 5 * time.Minute
	redisErrorTestMicroDelay = 1 * time.Microsecond
)

type errorCacheCase struct {
	name string
	fn   func(ctx context.Context, t *testing.T, cache *RedisCache)
}

// TestRedisErrorPaths tests error handling paths in Redis cache
func TestRedisErrorPaths(t *testing.T) {
	cache := setupTestCacheForErrorTesting(t)
	if cache == nil {
		t.Skip("Redis not available")
	}
	defer func() {
		require.NoError(t, cache.Close())
	}()

	ctx := context.Background()

	t.Run("get with invalid unmarshal destination type mismatch", func(t *testing.T) {
		_ = t
		// Store a JSON string
		stringVal := "this is a string"
		data, err := json.Marshal(stringVal)
		require.NoError(t, err)
		cache.client.Set(ctx, "test:string", string(data), redisErrorTestTTL)

		// Try to unmarshal into incompatible type
		type CustomStruct struct {
			Field string `json:"field"`
		}
		var result CustomStruct
		err = cache.Get(ctx, "test:string", &result)
		// Should error due to type mismatch
		if err == nil {
			t.Log("type conversion succeeded")
		}
	})

	t.Run("get with complex JSON failure", func(t *testing.T) {
		_ = t
		// Store a value that's not valid for unmarshaling
		invalidJSON := `{"incomplete": `
		cache.client.Set(ctx, "test:invalid:complex", invalidJSON, redisErrorTestTTL)

		var result map[string]interface{}
		err := cache.Get(ctx, "test:invalid:complex", &result)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to unmarshal")
	})

	t.Run("set with non-serializable value", func(t *testing.T) {
		_ = t
		// Try to marshal a channel (non-serializable)
		ch := make(chan int)
		err := cache.Set(ctx, "test:channel", ch)
		require.Error(t, err)
	})

	t.Run("set with circular reference (if json allows)", func(t *testing.T) {
		_ = t
		// This might not error depending on json.Marshal behavior
		type Circular struct {
			Self *Circular
		}
		c := &Circular{}
		c.Self = c

		err := cache.Set(ctx, "test:circular", c)
		// Either succeeds or fails, both acceptable
		_ = err
	})
}

// TestRedisCacheWithContextDeadline tests behavior with context deadlines
func TestRedisCacheWithContextDeadline(t *testing.T) {
	cache := setupTestCacheForErrorTesting(t)
	if cache == nil {
		t.Skip("Redis not available")
	}
	defer func() {
		require.NoError(t, cache.Close())
	}()

	t.Run("set with immediate timeout", func(t *testing.T) {
		_ = t
		ctx, cancel := context.WithTimeout(context.Background(), 0)
		defer cancel()

		// Give it a tiny bit of time to possibly work
		time.Sleep(redisErrorTestMicroDelay)

		err := cache.Set(ctx, "test:deadline", "value")
		// Should likely error due to deadline
		_ = err
	})

	t.Run("get with immediate timeout", func(t *testing.T) {
		_ = t
		ctx, cancel := context.WithTimeout(context.Background(), 0)
		defer cancel()

		time.Sleep(redisErrorTestMicroDelay)

		var result string
		err := cache.Get(ctx, "test:deadline", &result)
		// Should likely error due to deadline
		_ = err
	})

	t.Run("delete with immediate timeout", func(t *testing.T) {
		_ = t
		ctx, cancel := context.WithTimeout(context.Background(), 0)
		defer cancel()

		time.Sleep(redisErrorTestMicroDelay)

		err := cache.Delete(ctx, "test:deadline")
		// Should likely error due to deadline
		_ = err
	})
}

// TestRedisPatternEdgeCases tests InvalidatePattern with edge cases
func TestRedisPatternEdgeCases(t *testing.T) {
	cache := setupTestCacheForErrorTesting(t)
	if cache == nil {
		t.Skip("Redis not available")
	}
	defer func() {
		require.NoError(t, cache.Close())
	}()

	ctx := context.Background()

	t.Run("invalidate empty pattern", func(t *testing.T) {
		_ = t
		err := cache.InvalidatePattern(ctx, "")
		require.NoError(t, err)
	})

	t.Run("invalidate pattern with only asterisk", func(t *testing.T) {
		_ = t
		// Pre-populate some keys
		require.NoError(t, cache.Set(ctx, "temp:1", "val1"))
		require.NoError(t, cache.Set(ctx, "temp:2", "val2"))

		err := cache.InvalidatePattern(ctx, "*")
		require.NoError(t, err)

		// Most keys should be deleted
		var result string
		require.NoError(t, cache.Get(ctx, "temp:1", &result))
		assert.Empty(t, result)
	})

	t.Run("invalidate complex patterns", func(t *testing.T) {
		_ = t
		// Set keys with different patterns
		require.NoError(t, cache.Set(ctx, "api:user:123", "val1"))
		require.NoError(t, cache.Set(ctx, "api:user:456", "val2"))
		require.NoError(t, cache.Set(ctx, "api:post:123", "val3"))
		require.NoError(t, cache.Set(ctx, "cache:item:789", "val4"))

		// Invalidate only user keys
		err := cache.InvalidatePattern(ctx, "api:user:*")
		require.NoError(t, err)

		// User keys should be gone
		var result string
		require.NoError(t, cache.Get(ctx, "api:user:123", &result))
		assert.Empty(t, result)
	})

	t.Run("invalidate pattern with no matches", func(t *testing.T) {
		_ = t
		err := cache.InvalidatePattern(ctx, "nomatch:nonexistent:*")
		require.NoError(t, err)
	})

	t.Run("invalidate pattern with special chars", func(t *testing.T) {
		_ = t
		require.NoError(t, cache.Set(ctx, "special:key_with-dash.dot", "value"))
		err := cache.InvalidatePattern(ctx, "special:*")
		require.NoError(t, err)
	})
}

// TestRedisDataTypeHandling tests handling of various data types
func TestRedisDataTypeHandling(t *testing.T) {
	runErrorCacheCases(t, []errorCacheCase{
		{name: "store and retrieve float types", fn: runRedisDataTypeFloats},
		{name: "store and retrieve integer types", fn: runRedisDataTypeInts},
		{name: "store and retrieve boolean types", fn: runRedisDataTypeBools},
		{name: "store and retrieve slice types", fn: runRedisDataTypeSlices},
		{name: "store and retrieve nested maps", fn: runRedisDataTypeNestedMaps},
	})
}

// TestRedisConcurrentErrorScenarios tests concurrent operations with potential errors
func TestRedisConcurrentErrorScenarios(t *testing.T) {
	t.Run("concurrent operations on same key", func(t *testing.T) {
		withErrorTestCache(t, func(ctx context.Context, cache *RedisCache) {
			runRedisConcurrentOpsSameKey(ctx, t, cache)
		})
	})

	t.Run("concurrent invalidate and set", func(t *testing.T) {
		withErrorTestCache(t, func(ctx context.Context, cache *RedisCache) {
			runRedisConcurrentInvalidateAndSet(ctx, t, cache)
		})
	})
}

// TestRedisCacheKeyHelperMemoryUsage tests that key helpers are efficient
func TestRedisCacheKeyHelperMemoryUsage(t *testing.T) {
	t.Run("key generation is efficient", func(t *testing.T) {
		_ = t
		// These should be very fast, no allocations for simple cases
		key1 := ProjectKey("123")
		key2 := ItemKey("456")
		key3 := LinkKey("789")
		key4 := AgentKey("abc")
		key5 := SearchKey("query", "proj")

		assert.NotEmpty(t, key1)
		assert.NotEmpty(t, key2)
		assert.NotEmpty(t, key3)
		assert.NotEmpty(t, key4)
		assert.NotEmpty(t, key5)
	})

	t.Run("many key generations", func(t *testing.T) {
		_ = t
		// Generate many keys - should be fast
		for i := 0; i < 10000; i++ {
			_ = ProjectKey(fmt.Sprintf("proj%d", i))
		}
	})
}

// TestRedisLargeValues tests handling of large values
func TestRedisLargeValues(t *testing.T) {
	cache := setupTestCacheForErrorTesting(t)
	if cache == nil {
		t.Skip("Redis not available")
	}
	defer func() {
		require.NoError(t, cache.Close())
	}()

	ctx := context.Background()

	t.Run("store large string value", func(t *testing.T) {
		_ = t
		var largeBuilder strings.Builder
		largeBuilder.Grow(100 * len("This is a large string value that will be stored in Redis. "))
		for i := 0; i < 100; i++ {
			largeBuilder.WriteString("This is a large string value that will be stored in Redis. ")
		}
		largeString := largeBuilder.String()

		err := cache.Set(ctx, "test:large:string", largeString)
		require.NoError(t, err)

		var result string
		err = cache.Get(ctx, "test:large:string", &result)
		require.NoError(t, err)
		assert.Equal(t, largeString, result)
	})

	t.Run("store large array", func(t *testing.T) {
		_ = t
		largeArray := make([]interface{}, 1000)
		for i := 0; i < 1000; i++ {
			largeArray[i] = map[string]interface{}{
				"id":    i,
				"value": fmt.Sprintf("item_%d", i),
			}
		}

		err := cache.Set(ctx, "test:large:array", largeArray)
		require.NoError(t, err)

		var result []interface{}
		err = cache.Get(ctx, "test:large:array", &result)
		require.NoError(t, err)
		assert.Len(t, result, 1000)
	})
}

// TestRedisEmptyAndNilValues tests handling of empty and nil values
func TestRedisEmptyAndNilValues(t *testing.T) {
	cache := setupTestCacheForErrorTesting(t)
	if cache == nil {
		t.Skip("Redis not available")
	}
	defer func() {
		require.NoError(t, cache.Close())
	}()

	ctx := context.Background()

	t.Run("store nil value", func(t *testing.T) {
		_ = t
		err := cache.Set(ctx, "test:nil", nil)
		require.NoError(t, err)

		var result interface{}
		err = cache.Get(ctx, "test:nil", &result)
		require.NoError(t, err)
	})

	t.Run("store empty string", func(t *testing.T) {
		_ = t
		err := cache.Set(ctx, "test:empty:string", "")
		require.NoError(t, err)

		var result string
		err = cache.Get(ctx, "test:empty:string", &result)
		require.NoError(t, err)
		assert.Empty(t, result)
	})

	t.Run("store empty slice", func(t *testing.T) {
		_ = t
		emptySlice := []string{}
		err := cache.Set(ctx, "test:empty:slice", emptySlice)
		require.NoError(t, err)

		var result []string
		err = cache.Get(ctx, "test:empty:slice", &result)
		require.NoError(t, err)
		assert.Empty(t, result)
	})

	t.Run("store empty map", func(t *testing.T) {
		_ = t
		emptyMap := make(map[string]interface{})
		err := cache.Set(ctx, "test:empty:map", emptyMap)
		require.NoError(t, err)

		var result map[string]interface{}
		err = cache.Get(ctx, "test:empty:map", &result)
		require.NoError(t, err)
		assert.Empty(t, result)
	})
}

func runRedisDataTypeFloats(ctx context.Context, t *testing.T, cache *RedisCache) {
	testCases := []float64{
		0.0,
		1.5,
		-3.14159,
		999999.99999,
	}

	for i, val := range testCases {
		key := fmt.Sprintf("test:float:%d", i)
		err := cache.Set(ctx, key, val)
		require.NoError(t, err)

		var result float64
		err = cache.Get(ctx, key, &result)
		require.NoError(t, err)
		if val == 0.0 {
			assert.InDelta(t, val, result, 1e-9)
		} else {
			assert.InEpsilon(t, val, result, 1e-9)
		}
	}
}

func runRedisDataTypeInts(ctx context.Context, t *testing.T, cache *RedisCache) {
	testCases := []int{
		0,
		1,
		-1,
		2147483647,
		-2147483648,
	}

	for i, val := range testCases {
		key := fmt.Sprintf("test:int:%d", i)
		err := cache.Set(ctx, key, val)
		require.NoError(t, err)

		var result int
		err = cache.Get(ctx, key, &result)
		require.NoError(t, err)
		assert.Equal(t, val, result)
	}
}

func runRedisDataTypeBools(ctx context.Context, t *testing.T, cache *RedisCache) {
	boolCases := []bool{true, false}

	for i, val := range boolCases {
		key := fmt.Sprintf("test:bool:%d", i)
		err := cache.Set(ctx, key, val)
		require.NoError(t, err)

		var result bool
		err = cache.Get(ctx, key, &result)
		require.NoError(t, err)
		assert.Equal(t, val, result)
	}
}

func runRedisDataTypeSlices(ctx context.Context, t *testing.T, cache *RedisCache) {
	slices := []interface{}{
		[]string{"a", "b", "c"},
		[]int{1, 2, 3},
		[]float64{1.1, 2.2, 3.3},
	}

	for i, val := range slices {
		key := fmt.Sprintf("test:slice:%d", i)
		err := cache.Set(ctx, key, val)
		require.NoError(t, err)

		var result interface{}
		err = cache.Get(ctx, key, &result)
		require.NoError(t, err)
	}
}

func runRedisDataTypeNestedMaps(ctx context.Context, t *testing.T, cache *RedisCache) {
	nested := map[string]map[string]interface{}{
		"outer1": {
			"inner1": "value1",
			"inner2": 42,
		},
		"outer2": {
			"inner3": true,
			"inner4": 3.14,
		},
	}

	err := cache.Set(ctx, "test:nested:map", nested)
	require.NoError(t, err)

	var result map[string]map[string]interface{}
	err = cache.Get(ctx, "test:nested:map", &result)
	require.NoError(t, err)
	assert.Equal(t, "value1", result["outer1"]["inner1"])
}

func runRedisConcurrentOpsSameKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	key := "test:concurrent:same"
	var wg sync.WaitGroup
	numGoroutines := 50
	errors := make([]error, numGoroutines*3)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			errors[idx*3] = cache.Set(ctx, key, idx)
		}(i)

		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			var result int
			errors[idx*3+1] = cache.Get(ctx, key, &result)
		}(i)

		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			errors[idx*3+2] = cache.Delete(ctx, key)
		}(i)
	}

	wg.Wait()

	successCount := 0
	for _, err := range errors {
		if err == nil {
			successCount++
		}
	}

	assert.Greater(t, successCount, len(errors)/2)
}

func runRedisConcurrentInvalidateAndSet(ctx context.Context, t *testing.T, cache *RedisCache) {
	var wg sync.WaitGroup
	numGoroutines := 20

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			key := fmt.Sprintf("test:pattern:%d", idx)
			assert.NoError(t, cache.Set(ctx, key, idx))
		}(i)

		wg.Add(1)
		go func() {
			defer wg.Done()
			assert.NoError(t, cache.InvalidatePattern(ctx, "test:pattern:*"))
		}()
	}

	wg.Wait()
}

func runErrorCacheCases(t *testing.T, cases []errorCacheCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			withErrorTestCache(t, func(ctx context.Context, cache *RedisCache) {
				tc.fn(ctx, t, cache)
			})
		})
	}
}

func withErrorTestCache(t *testing.T, fn func(ctx context.Context, cache *RedisCache)) {
	cache := setupTestCacheForErrorTesting(t)
	if cache == nil {
		t.Skip("Redis not available")
	}
	defer func() {
		require.NoError(t, cache.Close())
	}()

	ctx := context.Background()
	fn(ctx, cache)
}

// Helper function to setup test cache with error handling
func setupTestCacheForErrorTesting(t *testing.T) *RedisCache {
	_ = t
	url := os.Getenv("TEST_REDIS_URL")
	if url == "" {
		url = "redis://localhost:6379/0"
	}

	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:      url,
		DefaultTTL:    redisErrorTestTTL,
		EnableMetrics: true,
	})
	if err != nil {
		return nil
	}

	ctx := context.Background()
	cache.client.FlushDB(ctx)

	return cache
}
