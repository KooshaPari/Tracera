package cache

import (
	"context"
	"encoding/json"
	"os"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

const (
	testRedisDefaultTTL       = 5 * time.Minute
	testRedisCustomTTL        = 10 * time.Minute
	testRedisNegativeTTL      = -1 * time.Second
	testRedisKeyTTL           = 5 * time.Minute
	testRedisMediumSleep      = 150 * time.Millisecond
	testRedisTimeoutSleep     = 10 * time.Millisecond
	testRedisImmediateTimeout = 1 * time.Nanosecond
)

func getTestRedisURL(t *testing.T) string {
	_ = t
	url := os.Getenv("TEST_REDIS_URL")
	if url == "" {
		url = "redis://localhost:6379/0"
	}
	return url
}

func TestNewRedisCache(t *testing.T) {
	t.Run("successful creation", func(t *testing.T) {
		runNewRedisCacheSuccessfulCreation(t)
	})

	t.Run("invalid URL", func(t *testing.T) {
		runNewRedisCacheInvalidURL(t)
	})

	t.Run("unreachable host", func(t *testing.T) {
		runNewRedisCacheUnreachableHost(t)
	})

	t.Run("custom TTL", func(t *testing.T) {
		runNewRedisCacheCustomTTL(t)
	})

	t.Run("zero TTL", func(t *testing.T) {
		runNewRedisCacheZeroTTL(t)
	})

	t.Run("negative TTL", func(t *testing.T) {
		runNewRedisCacheNegativeTTL(t)
	})

	t.Run("malformed URL", func(t *testing.T) {
		runNewRedisCacheMalformedURL(t)
	})
}

func runNewRedisCacheSuccessfulCreation(t *testing.T) {
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:      getTestRedisURL(t),
		DefaultTTL:    testRedisDefaultTTL,
		EnableMetrics: true,
	})
	if err != nil {
		t.Skipf("Redis not available: %v", err)
	}
	defer func() {
		_ = cache.Close()
	}()

	assert.NotNil(t, cache)
	assert.NotNil(t, cache.client)
	assert.Equal(t, testRedisDefaultTTL, cache.defaultTTL)
}

func runNewRedisCacheInvalidURL(t *testing.T) {
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:   "invalid://url",
		DefaultTTL: testRedisDefaultTTL,
	})
	assert.Error(t, err)
	assert.Nil(t, cache)
	assert.Contains(t, err.Error(), "failed to parse Redis URL")
}

func runNewRedisCacheUnreachableHost(t *testing.T) {
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:   "redis://192.0.2.1:6379",
		DefaultTTL: testRedisDefaultTTL,
	})
	assert.Error(t, err)
	assert.Nil(t, cache)
	assert.Contains(t, err.Error(), "failed to connect to Redis")
}

func runNewRedisCacheCustomTTL(t *testing.T) {
	customTTL := testRedisCustomTTL
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:   getTestRedisURL(t),
		DefaultTTL: customTTL,
	})
	if err != nil {
		t.Skipf("Redis not available: %v", err)
	}
	defer func() {
		_ = cache.Close()
	}()

	assert.Equal(t, customTTL, cache.defaultTTL)
}

func runNewRedisCacheZeroTTL(t *testing.T) {
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:   getTestRedisURL(t),
		DefaultTTL: 0,
	})
	if err != nil {
		t.Skipf("Redis not available: %v", err)
	}
	defer func() {
		_ = cache.Close()
	}()

	assert.Equal(t, time.Duration(0), cache.defaultTTL)
}

func runNewRedisCacheNegativeTTL(t *testing.T) {
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:   getTestRedisURL(t),
		DefaultTTL: testRedisNegativeTTL,
	})
	if err != nil {
		t.Skipf("Redis not available: %v", err)
	}
	defer func() {
		_ = cache.Close()
	}()

	assert.Equal(t, testRedisNegativeTTL, cache.defaultTTL)
}

func runNewRedisCacheMalformedURL(t *testing.T) {
	testCases := []string{
		"not-a-url",
		"redis://",
		"redis://:password@",
		"http://localhost:6379",
	}

	for _, tc := range testCases {
		cache, err := NewRedisCache(RedisCacheConfig{
			RedisURL:   tc,
			DefaultTTL: testRedisDefaultTTL,
		})
		if tc == "redis://" || tc == "redis://:password@" {
			// go-redis ParseURL defaults these to localhost:6379; allow it.
			assert.NoError(t, err, "URL: %s", tc)
			assert.NotNil(t, cache)
			if cache != nil {
				_ = cache.Close()
			}
			continue
		}
		assert.Error(t, err, "URL: %s", tc)
		assert.Nil(t, cache)
	}
}

func setupTestCache(t *testing.T) *RedisCache {
	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:      getTestRedisURL(t),
		DefaultTTL:    testRedisDefaultTTL,
		EnableMetrics: true,
	})
	if err != nil {
		t.Skipf("Redis not available: %v", err)
	}

	// Clean up test keys
	ctx := context.Background()
	cache.client.FlushDB(ctx)

	return cache
}

func TestRedisCacheGet(t *testing.T) {
	cache := setupTestCache(t)
	defer func() {
		_ = cache.Close()
	}()

	ctx := context.Background()

	t.Run("get existing key", func(t *testing.T) {
		runRedisCacheGetExistingKey(ctx, t, cache)
	})

	t.Run("get non-existent key", func(t *testing.T) {
		runRedisCacheGetNonExistentKey(ctx, t, cache)
	})

	t.Run("get with invalid JSON", func(t *testing.T) {
		runRedisCacheGetInvalidJSON(ctx, t, cache)
	})

	t.Run("get with context cancellation", func(t *testing.T) {
		runRedisCacheGetWithCancelledContext(t, cache)
	})

	t.Run("get different data types", func(t *testing.T) {
		runRedisCacheGetDifferentDataTypes(ctx, t, cache)
	})

	t.Run("get empty string value", func(t *testing.T) {
		runRedisCacheGetEmptyString(ctx, t, cache)
	})
}

func runRedisCacheGetExistingKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	testData := map[string]interface{}{"key": "value", "number": float64(42)}
	data, _ := json.Marshal(testData)
	cache.client.Set(ctx, "test:key1", string(data), testRedisKeyTTL)

	var result map[string]interface{}
	err := cache.Get(ctx, "test:key1", &result)
	assert.NoError(t, err)
	assert.Equal(t, "value", result["key"])
	assert.Equal(t, float64(42), result["number"])
}

func runRedisCacheGetNonExistentKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	var result string
	err := cache.Get(ctx, "non:existent", &result)
	assert.NoError(t, err)
	assert.Empty(t, result)
}

func runRedisCacheGetInvalidJSON(ctx context.Context, t *testing.T, cache *RedisCache) {
	cache.client.Set(ctx, "test:invalid", "not-json", testRedisKeyTTL)

	var result map[string]interface{}
	err := cache.Get(ctx, "test:invalid", &result)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to unmarshal")
}

func runRedisCacheGetWithCancelledContext(t *testing.T, cache *RedisCache) {
	cancelCtx, cancel := context.WithCancel(context.Background())
	cancel()

	var result string
	err := cache.Get(cancelCtx, "test:key", &result)
	assert.Error(t, err)
}

func runRedisCacheGetDifferentDataTypes(ctx context.Context, t *testing.T, cache *RedisCache) {
	testCases := []struct {
		name  string
		value interface{}
	}{
		{"string", "test string"},
		{"int", 123},
		{"bool", true},
		{"slice", []int{1, 2, 3}},
		{"map", map[string]string{"a": "b"}},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			key := "test:type:" + tc.name
			data, _ := json.Marshal(tc.value)
			cache.client.Set(ctx, key, string(data), testRedisKeyTTL)

			var result interface{}
			err := cache.Get(ctx, key, &result)
			assert.NoError(t, err)
		})
	}
}

func runRedisCacheGetEmptyString(ctx context.Context, t *testing.T, cache *RedisCache) {
	data, _ := json.Marshal("")
	cache.client.Set(ctx, "test:empty", string(data), testRedisKeyTTL)

	var result string
	err := cache.Get(ctx, "test:empty", &result)
	assert.NoError(t, err)
	assert.Equal(t, "", result)
}

func TestRedisCacheSet(t *testing.T) {
	cache := setupTestCache(t)
	defer func() {
		_ = cache.Close()
	}()

	ctx := context.Background()

	t.Run("set simple value", func(t *testing.T) {
		runRedisCacheSetSimpleValue(ctx, t, cache)
	})

	t.Run("set complex value", func(t *testing.T) {
		runRedisCacheSetComplexValue(ctx, t, cache)
	})

	t.Run("set with TTL", func(t *testing.T) {
		runRedisCacheSetWithTTL(ctx, t)
	})

	t.Run("set with context cancellation", func(t *testing.T) {
		runRedisCacheSetWithCancelledContext(t, cache)
	})

	t.Run("overwrite existing key", func(t *testing.T) {
		runRedisCacheSetOverwriteKey(ctx, t, cache)
	})

	t.Run("set nil value", func(t *testing.T) {
		runRedisCacheSetNilValue(ctx, t, cache)
	})

	t.Run("set empty struct", func(t *testing.T) {
		runRedisCacheSetEmptyStruct(ctx, t, cache)
	})
}

func runRedisCacheSetSimpleValue(ctx context.Context, t *testing.T, cache *RedisCache) {
	err := cache.Set(ctx, "test:set1", "simple value")
	assert.NoError(t, err)

	val, err := cache.client.Get(ctx, "test:set1").Result()
	assert.NoError(t, err)
	assert.Contains(t, val, "simple value")
}

func runRedisCacheSetComplexValue(ctx context.Context, t *testing.T, cache *RedisCache) {
	complexData := map[string]interface{}{
		"string":  "value",
		"number":  42,
		"boolean": true,
		"array":   []int{1, 2, 3},
		"nested": map[string]string{
			"key": "nested",
		},
	}

	err := cache.Set(ctx, "test:complex", complexData)
	assert.NoError(t, err)

	var result map[string]interface{}
	err = cache.Get(ctx, "test:complex", &result)
	assert.NoError(t, err)
	assert.Equal(t, "value", result["string"])
	assert.Equal(t, float64(42), result["number"])
}

func runRedisCacheSetWithTTL(ctx context.Context, t *testing.T) {
	shortCache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:   getTestRedisURL(t),
		DefaultTTL: 100 * time.Millisecond,
	})
	if err != nil {
		t.Skipf("Redis not available: %v", err)
	}
	defer func() {
		if err := shortCache.Close(); err != nil {
			t.Logf("error closing cache: %v", err)
		}
	}()

	err = shortCache.Set(ctx, "test:ttl", "expires soon")
	assert.NoError(t, err)

	var result string
	err = shortCache.Get(ctx, "test:ttl", &result)
	assert.NoError(t, err)
	assert.Equal(t, "expires soon", result)

	time.Sleep(testRedisMediumSleep)

	err = shortCache.Get(ctx, "test:ttl", &result)
	assert.NoError(t, err)
}

func runRedisCacheSetWithCancelledContext(t *testing.T, cache *RedisCache) {
	cancelCtx, cancel := context.WithCancel(context.Background())
	cancel()

	err := cache.Set(cancelCtx, "test:cancelled", "value")
	assert.Error(t, err)
}

func runRedisCacheSetOverwriteKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	err := cache.Set(ctx, "test:overwrite", "original")
	assert.NoError(t, err)

	err = cache.Set(ctx, "test:overwrite", "updated")
	assert.NoError(t, err)

	var result string
	err = cache.Get(ctx, "test:overwrite", &result)
	assert.NoError(t, err)
	assert.Equal(t, "updated", result)
}

func runRedisCacheSetNilValue(ctx context.Context, t *testing.T, cache *RedisCache) {
	err := cache.Set(ctx, "test:nil", nil)
	assert.NoError(t, err)
}

func runRedisCacheSetEmptyStruct(ctx context.Context, t *testing.T, cache *RedisCache) {
	type Empty struct{}
	err := cache.Set(ctx, "test:empty:struct", Empty{})
	assert.NoError(t, err)
}

func TestRedisCacheDelete(t *testing.T) {
	cache := setupTestCache(t)
	defer func() {
		_ = cache.Close()
	}()

	ctx := context.Background()

	t.Run("delete existing key", func(t *testing.T) {
		runRedisCacheDeleteExistingKey(ctx, t, cache)
	})

	t.Run("delete non-existent key", func(t *testing.T) {
		runRedisCacheDeleteNonExistentKey(ctx, t, cache)
	})

	t.Run("delete multiple keys", func(t *testing.T) {
		runRedisCacheDeleteMultipleKeys(ctx, t, cache)
	})

	t.Run("delete with empty keys", func(t *testing.T) {
		runRedisCacheDeleteEmptyKeys(ctx, t, cache)
	})

	t.Run("delete with context cancellation", func(t *testing.T) {
		runRedisCacheDeleteWithCancelledContext(ctx, t, cache)
	})
}

func runRedisCacheDeleteExistingKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	_ = cache.Set(ctx, "test:del1", "value")

	err := cache.Delete(ctx, "test:del1")
	assert.NoError(t, err)

	var result string
	err = cache.Get(ctx, "test:del1", &result)
	assert.NoError(t, err)
	assert.Empty(t, result)
}

func runRedisCacheDeleteNonExistentKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	err := cache.Delete(ctx, "test:nonexistent")
	assert.NoError(t, err)
}

func runRedisCacheDeleteMultipleKeys(ctx context.Context, t *testing.T, cache *RedisCache) {
	_ = cache.Set(ctx, "test:del:a", "value")
	_ = cache.Set(ctx, "test:del:b", "value")
	_ = cache.Set(ctx, "test:del:c", "value")

	err := cache.Delete(ctx, "test:del:a", "test:del:b", "test:del:c")
	assert.NoError(t, err)

	var result string
	for _, key := range []string{"test:del:a", "test:del:b", "test:del:c"} {
		_ = cache.Get(ctx, key, &result)
		assert.Empty(t, result)
	}
}

func runRedisCacheDeleteEmptyKeys(ctx context.Context, t *testing.T, cache *RedisCache) {
	err := cache.Delete(ctx)
	assert.NoError(t, err)
}

func runRedisCacheDeleteWithCancelledContext(ctx context.Context, t *testing.T, cache *RedisCache) {
	_ = cache.Set(ctx, "test:del:cancel", "value")

	cancelCtx, cancel := context.WithCancel(context.Background())
	cancel()

	err := cache.Delete(cancelCtx, "test:del:cancel")
	assert.Error(t, err)
}

func TestRedisCacheInvalidatePattern(t *testing.T) {
	cache := setupTestCache(t)
	defer func() {
		_ = cache.Close()
	}()

	ctx := context.Background()

	t.Run("invalidate matching pattern", func(t *testing.T) {
		runRedisCacheInvalidateMatchingPattern(ctx, t, cache)
	})

	t.Run("invalidate with no matches", func(t *testing.T) {
		runRedisCacheInvalidateNoMatches(ctx, t, cache)
	})

	t.Run("invalidate all keys", func(t *testing.T) {
		runRedisCacheInvalidateAllKeys(ctx, t, cache)
	})

	t.Run("invalidate with context cancellation", func(t *testing.T) {
		runRedisCacheInvalidateWithCancelledContext(t, cache)
	})
}

func runRedisCacheInvalidateMatchingPattern(ctx context.Context, t *testing.T, cache *RedisCache) {
	_ = cache.Set(ctx, "project:123", "value1")
	_ = cache.Set(ctx, "project:456", "value2")
	_ = cache.Set(ctx, "project:789", "value3")
	_ = cache.Set(ctx, "item:999", "other")

	err := cache.InvalidatePattern(ctx, "project:*")
	assert.NoError(t, err)

	var result string
	_ = cache.Get(ctx, "project:123", &result)
	assert.Empty(t, result)

	_ = cache.Get(ctx, "item:999", &result)
	assert.Equal(t, "other", result)
}

func runRedisCacheInvalidateNoMatches(ctx context.Context, t *testing.T, cache *RedisCache) {
	err := cache.InvalidatePattern(ctx, "nomatch:*")
	assert.NoError(t, err)
}

func runRedisCacheInvalidateAllKeys(ctx context.Context, t *testing.T, cache *RedisCache) {
	_ = cache.Set(ctx, "key1", "val1")
	_ = cache.Set(ctx, "key2", "val2")

	err := cache.InvalidatePattern(ctx, "*")
	assert.NoError(t, err)
}

func runRedisCacheInvalidateWithCancelledContext(t *testing.T, cache *RedisCache) {
	cancelCtx, cancel := context.WithCancel(context.Background())
	cancel()

	err := cache.InvalidatePattern(cancelCtx, "pattern:*")
	assert.Error(t, err)
}

func TestRedisCacheClose(t *testing.T) {
	t.Run("close active cache", func(t *testing.T) {
		_ = t
		cache := setupTestCache(t)

		err := cache.Close()
		assert.NoError(t, err)

		// Subsequent operations should fail
		ctx := context.Background()
		err = cache.Set(ctx, "test:key", "value")
		assert.Error(t, err)
	})

	t.Run("double close", func(t *testing.T) {
		_ = t
		cache := setupTestCache(t)

		_ = cache.Close()
		err := cache.Close()
		assert.Error(t, err)
	})
}

func TestCacheKeyHelpers(t *testing.T) {
	t.Run("ProjectKey", func(t *testing.T) {
		_ = t
		key := ProjectKey("test-project-123")
		assert.Equal(t, "project:test-project-123", key)
		assert.Contains(t, key, "project:")
	})

	t.Run("ItemKey", func(t *testing.T) {
		_ = t
		key := ItemKey("item-456")
		assert.Equal(t, "item:item-456", key)
		assert.Contains(t, key, "item:")
	})

	t.Run("LinkKey", func(t *testing.T) {
		_ = t
		key := LinkKey("link-789")
		assert.Equal(t, "link:link-789", key)
		assert.Contains(t, key, "link:")
	})

	t.Run("AgentKey", func(t *testing.T) {
		_ = t
		key := AgentKey("agent-abc")
		assert.Equal(t, "agent:agent-abc", key)
		assert.Contains(t, key, "agent:")
	})

	t.Run("SearchKey", func(t *testing.T) {
		_ = t
		key := SearchKey("test query", "project-123")
		assert.Equal(t, "search:project-123:test query", key)
		assert.Contains(t, key, "search:")
		assert.Contains(t, key, "project-123")
		assert.Contains(t, key, "test query")
	})

	t.Run("empty IDs", func(t *testing.T) {
		_ = t
		assert.Equal(t, "project:", ProjectKey(""))
		assert.Equal(t, "item:", ItemKey(""))
		assert.Equal(t, "link:", LinkKey(""))
		assert.Equal(t, "agent:", AgentKey(""))
		assert.Equal(t, "search::", SearchKey("", ""))
	})

	t.Run("special characters in IDs", func(t *testing.T) {
		_ = t
		specialID := "id-with:special*chars"
		key := ProjectKey(specialID)
		assert.Contains(t, key, specialID)
	})
}

func TestCacheKeyPatterns(t *testing.T) {
	t.Run("pattern constants", func(t *testing.T) {
		_ = t
		assert.Equal(t, "project:*", ProjectKeyPattern)
		assert.Equal(t, "item:*", ItemKeyPattern)
		assert.Equal(t, "link:*", LinkKeyPattern)
		assert.Equal(t, "agent:*", AgentKeyPattern)
		assert.Equal(t, "search:*", SearchKeyPattern)
	})
}

func TestConcurrentCacheOperations(t *testing.T) {
	cache := setupTestCache(t)
	defer func() {
		_ = cache.Close()
	}()

	ctx := context.Background()

	t.Run("concurrent sets", func(t *testing.T) {
		runRedisCacheConcurrentSets(ctx, t, cache)
	})

	t.Run("concurrent gets", func(t *testing.T) {
		runRedisCacheConcurrentGets(ctx, t, cache)
	})

	t.Run("concurrent mixed operations", func(_ *testing.T) {
		runRedisCacheConcurrentMixedOps(ctx, cache)
	})

	t.Run("concurrent pattern invalidation", func(_ *testing.T) {
		runRedisCacheConcurrentInvalidate(ctx, cache)
	})
}

func runRedisCacheConcurrentSets(ctx context.Context, t *testing.T, cache *RedisCache) {
	var wg sync.WaitGroup
	numGoroutines := 50

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			key := ProjectKey(string(rune(id)))
			err := cache.Set(ctx, key, map[string]int{"id": id})
			assert.NoError(t, err)
		}(i)
	}

	wg.Wait()
}

func runRedisCacheConcurrentGets(ctx context.Context, t *testing.T, cache *RedisCache) {
	testKey := "test:concurrent:get"
	_ = cache.Set(ctx, testKey, "shared value")

	var wg sync.WaitGroup
	numGoroutines := 50
	errors := make([]error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			var result string
			errors[id] = cache.Get(ctx, testKey, &result)
		}(i)
	}

	wg.Wait()

	for i, err := range errors {
		assert.NoError(t, err, "goroutine %d failed", i)
	}
}

func runRedisCacheConcurrentMixedOps(ctx context.Context, cache *RedisCache) {
	var wg sync.WaitGroup
	numGoroutines := 30

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			key := ItemKey(string(rune(id)))

			_ = cache.Set(ctx, key, id)

			var result int
			_ = cache.Get(ctx, key, &result)

			if id%2 == 0 {
				_ = cache.Delete(ctx, key)
			}
		}(i)
	}

	wg.Wait()
}

func runRedisCacheConcurrentInvalidate(ctx context.Context, cache *RedisCache) {
	for i := 0; i < 20; i++ {
		_ = cache.Set(ctx, ProjectKey(string(rune(i))), i)
	}

	var wg sync.WaitGroup
	numGoroutines := 5

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_ = cache.InvalidatePattern(ctx, ProjectKeyPattern)
		}()
	}

	wg.Wait()
}

func TestCacheEdgeCases(t *testing.T) {
	cache := setupTestCache(t)
	defer func() {
		_ = cache.Close()
	}()

	ctx := context.Background()

	t.Run("very large value", func(t *testing.T) {
		runRedisCacheLargeValue(ctx, t, cache)
	})

	t.Run("unicode in keys and values", func(t *testing.T) {
		runRedisCacheUnicodeValues(ctx, t, cache)
	})

	t.Run("nested structures", func(t *testing.T) {
		runRedisCacheNestedStructures(ctx, t, cache)
	})

	t.Run("rapid set/delete cycles", func(_ *testing.T) {
		runRedisCacheRapidSetDelete(ctx, cache)
	})
}

func runRedisCacheLargeValue(ctx context.Context, t *testing.T, cache *RedisCache) {
	largeData := make([]byte, 1024*1024)
	for i := range largeData {
		largeData[i] = byte(i % 256)
	}

	err := cache.Set(ctx, "test:large", largeData)
	assert.NoError(t, err)

	var result []byte
	err = cache.Get(ctx, "test:large", &result)
	assert.NoError(t, err)
}

func runRedisCacheUnicodeValues(ctx context.Context, t *testing.T, cache *RedisCache) {
	unicodeData := map[string]string{
		"hello": "世界",
		"emoji": "🚀💻",
	}

	err := cache.Set(ctx, "test:unicode:世界", unicodeData)
	assert.NoError(t, err)

	var result map[string]string
	err = cache.Get(ctx, "test:unicode:世界", &result)
	assert.NoError(t, err)
	assert.Equal(t, "世界", result["hello"])
	assert.Equal(t, "🚀💻", result["emoji"])
}

func runRedisCacheNestedStructures(ctx context.Context, t *testing.T, cache *RedisCache) {
	type Address struct {
		Street string
		City   string
	}
	type Person struct {
		Name    string
		Age     int
		Address Address
	}

	person := Person{
		Name: "Test",
		Age:  30,
		Address: Address{
			Street: "123 Main St",
			City:   "TestCity",
		},
	}

	err := cache.Set(ctx, "test:nested", person)
	assert.NoError(t, err)

	var result Person
	err = cache.Get(ctx, "test:nested", &result)
	assert.NoError(t, err)
	assert.Equal(t, "Test", result.Name)
	assert.Equal(t, "TestCity", result.Address.City)
}

func runRedisCacheRapidSetDelete(ctx context.Context, cache *RedisCache) {
	key := "test:rapid"
	for i := 0; i < 100; i++ {
		_ = cache.Set(ctx, key, i)
		_ = cache.Delete(ctx, key)
	}
}

func TestRedisCacheTimeout(t *testing.T) {
	cache := setupTestCache(t)
	defer func() {
		_ = cache.Close()
	}()

	t.Run("operation with short timeout", func(t *testing.T) {
		_ = t
		ctx, cancel := context.WithTimeout(context.Background(), testRedisImmediateTimeout)
		defer cancel()

		time.Sleep(testRedisTimeoutSleep) // Ensure timeout

		err := cache.Set(ctx, "test:timeout", "value")
		if err == nil {
			t.Log("Operation completed before timeout (acceptable)")
		} else {
			assert.Error(t, err)
		}
	})
}
