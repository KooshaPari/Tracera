//go:build !integration && !e2e

package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const redisCoverageTestTTL = 5 * time.Minute

// Test constants
const (
	testRedisURL = "redis://localhost:6379/0"
)

// Test struct for JSON marshaling
type TestItem struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Value string `json:"value"`
}

type NestedAddress struct {
	Street string `json:"street"`
	City   string `json:"city"`
	ZIP    string `json:"zip"`
}

type NestedContact struct {
	Email string `json:"email"`
	Phone string `json:"phone"`
}

type NestedPerson struct {
	Name    string        `json:"name"`
	Age     int           `json:"age"`
	Address NestedAddress `json:"address"`
	Contact NestedContact `json:"contact"`
}

type redisCacheGetCoverageCase struct {
	name        string
	key         string
	storeValue  interface{}
	destFactory func() interface{}
	verify      func(t *testing.T, dest interface{})
}

type redisCacheSetCoverageCase struct {
	name        string
	key         string
	setValue    interface{}
	destFactory func() interface{}
	verify      func(t *testing.T, original, retrieved interface{})
}

type coverageCacheCase struct {
	name string
	fn   func(ctx context.Context, t *testing.T, cache *RedisCache)
}

type simpleTestCase struct {
	name string
	fn   func(t *testing.T)
}

// TestRedisCacheGet_Coverage tests for Get method edge cases
func TestRedisCacheGet_Coverage(t *testing.T) {
	for _, tt := range redisCacheGetCoverageCases() {
		t.Run(tt.name, func(t *testing.T) {
			withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
				jsonData, err := json.Marshal(tt.storeValue)
				require.NoError(t, err)
				_ = cache.client.Set(ctx, tt.key, string(jsonData), redisCoverageTestTTL)

				dest := tt.destFactory()
				err = cache.Get(ctx, tt.key, dest)
				require.NoError(t, err)
				tt.verify(t, dest)
			})
		})
	}
}

// TestRedisCacheSet_Coverage tests for Set method edge cases
func TestRedisCacheSet_Coverage(t *testing.T) {
	for _, tt := range redisCacheSetCoverageCases() {
		t.Run(tt.name, func(t *testing.T) {
			withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
				err := cache.Set(ctx, tt.key, tt.setValue)
				require.NoError(t, err)

				dest := tt.destFactory()
				err = cache.Get(ctx, tt.key, dest)
				require.NoError(t, err)
				tt.verify(t, tt.setValue, dest)
			})
		})
	}

	t.Run("set and overwrite multiple times", func(t *testing.T) {
		withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
			runRedisCacheSetOverwriteMultiple(ctx, t, cache)
		})
	})

	t.Run("set with very long key", func(t *testing.T) {
		withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
			runRedisCacheSetLongKey(ctx, t, cache)
		})
	})
}

// TestRedisCacheDelete_Coverage tests for Delete method edge cases
func TestRedisCacheDelete_Coverage(t *testing.T) {
	runCoverageCacheCases(t, []coverageCacheCase{
		{name: "delete single key", fn: runRedisCacheDeleteSingleKey},
		{name: "delete many keys sequentially", fn: runRedisCacheDeleteManyKeys},
		{name: "delete with mixed existing and non-existing keys", fn: runRedisCacheDeleteMixedKeys},
		{name: "delete with key containing special characters", fn: runRedisCacheDeleteSpecialKey},
	})
}

// TestRedisCacheInvalidatePattern_Coverage tests for InvalidatePattern edge cases
func TestRedisCacheInvalidatePattern_Coverage(t *testing.T) {
	runCoverageCacheCases(t, []coverageCacheCase{
		{name: "invalidate single key pattern", fn: runRedisCacheInvalidateSinglePattern},
		{name: "invalidate pattern with dots", fn: runRedisCacheInvalidateDots},
		{name: "invalidate with complex pattern", fn: runRedisCacheInvalidateComplex},
		{name: "invalidate pattern matching nothing", fn: runRedisCacheInvalidateNoMatch},
		{name: "invalidate all with asterisk", fn: runRedisCacheInvalidateAll},
	})
}

// TestKeyHelpers_Coverage provides comprehensive coverage for key generation functions
func TestKeyHelpers_Coverage(t *testing.T) {
	runSimpleTestCases(t, []simpleTestCase{
		{name: "ProjectKey with numeric ID", fn: runProjectKeyNumeric},
		{name: "ProjectKey with UUID-like ID", fn: runProjectKeyUUID},
		{name: "ItemKey variations", fn: runItemKeyVariations},
		{name: "LinkKey with hyphenated ID", fn: runLinkKeyHyphenated},
		{name: "AgentKey with various formats", fn: runAgentKeyFormats},
		{name: "SearchKey with different query and project combinations", fn: runSearchKeyVariations},
		{name: "all key patterns are defined", fn: runKeyPatternsDefined},
	})
}

// TestConcurrency_Coverage tests concurrent operations
func TestConcurrency_Coverage(t *testing.T) {
	runCoverageCacheCases(t, []coverageCacheCase{
		{name: "concurrent set and get on same key", fn: runRedisCacheConcurrentSameKey},
		{name: "concurrent delete operations", fn: runRedisCacheConcurrentDelete},
		{name: "concurrent pattern invalidation", fn: runRedisCacheConcurrentInvalidatePattern},
		{name: "high concurrency stress test", fn: runRedisCacheHighConcurrencyStress},
	})
}

// TestDataTypes_Coverage tests various data types
func TestDataTypes_Coverage(t *testing.T) {
	t.Run("store and retrieve JSON object", func(t *testing.T) {
		withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
			runRedisCacheDataTypeObject(ctx, t, cache)
		})
	})

	t.Run("store and retrieve JSON array", func(t *testing.T) {
		withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
			runRedisCacheDataTypeArray(ctx, t, cache)
		})
	})

	t.Run("store and retrieve map", func(t *testing.T) {
		withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
			runRedisCacheDataTypeMap(ctx, t, cache)
		})
	})
}

func redisCacheGetCoverageCases() []redisCacheGetCoverageCase {
	cases := make([]redisCacheGetCoverageCase, 0, 7)
	cases = append(cases,
		redisCacheGetPointerCase(),
		redisCacheGetArrayCase(),
	)
	cases = append(cases, redisCacheGetFloatCases()...)
	cases = append(cases, redisCacheGetBoolCases()...)
	cases = append(cases, redisCacheGetIntCases()...)
	return cases
}

func redisCacheSetCoverageCases() []redisCacheSetCoverageCase {
	cases := make([]redisCacheSetCoverageCase, 0, 5)
	cases = append(cases,
		redisCacheSetNestedStructCase(),
		redisCacheSetStringSliceCase(),
	)
	cases = append(cases, redisCacheSetMapCase())
	cases = append(cases, redisCacheSetBoolAndZeroCases()...)
	return cases
}

func redisCacheGetPointerCase() redisCacheGetCoverageCase {
	return redisCacheGetCoverageCase{
		name:       "get with pointer dest",
		key:        "test:ptr",
		storeValue: func() interface{} { v := "test value"; return &v }(),
		destFactory: func() interface{} {
			var r *string
			return &r
		},
		verify: func(t *testing.T, _ interface{}) {
			// Verification is implicit: successful deserialization is sufficient
		},
	}
}

func redisCacheGetFloatCases() []redisCacheGetCoverageCase {
	return []redisCacheGetCoverageCase{
		{
			name:       "get with float64 precision",
			key:        "test:float",
			storeValue: 3.14159265359,
			destFactory: func() interface{} {
				var r float64
				return &r
			},
			verify: func(t *testing.T, dest interface{}) {
				_ = dest
				typed, ok := dest.(*float64)
				require.True(t, ok)
				assert.InEpsilon(t, 3.14159265359, *typed, 1e-9)
			},
		},
	}
}

func redisCacheGetArrayCase() redisCacheGetCoverageCase {
	return redisCacheGetCoverageCase{
		name: "get with array of objects",
		key:  "test:array",
		storeValue: []TestItem{
			{ID: 1, Name: "item1", Value: "val1"},
			{ID: 2, Name: "item2", Value: "val2"},
			{ID: 3, Name: "item3", Value: "val3"},
		},
		destFactory: func() interface{} {
			var r []TestItem
			return &r
		},
		verify: func(t *testing.T, dest interface{}) {
			_ = dest
			typed, ok := dest.(*[]TestItem)
			require.True(t, ok)
			result := *typed
			assert.Len(t, result, 3)
			assert.Equal(t, "item2", result[1].Name)
		},
	}
}

func redisCacheGetBoolCases() []redisCacheGetCoverageCase {
	return []redisCacheGetCoverageCase{
		{
			name:       "get with boolean true",
			key:        "test:bool:true",
			storeValue: true,
			destFactory: func() interface{} {
				var r bool
				return &r
			},
			verify: func(t *testing.T, dest interface{}) {
				_ = dest
				typed, ok := dest.(*bool)
				require.True(t, ok)
				assert.True(t, *typed)
			},
		},
		{
			name:       "get with boolean false",
			key:        "test:bool:false",
			storeValue: false,
			destFactory: func() interface{} {
				var r bool
				return &r
			},
			verify: func(t *testing.T, dest interface{}) {
				_ = dest
				typed, ok := dest.(*bool)
				require.True(t, ok)
				assert.False(t, *typed)
			},
		},
	}
}

func redisCacheGetIntCases() []redisCacheGetCoverageCase {
	return []redisCacheGetCoverageCase{
		{
			name:       "get with negative integer",
			key:        "test:negative",
			storeValue: -12345,
			destFactory: func() interface{} {
				var r int
				return &r
			},
			verify: func(t *testing.T, dest interface{}) {
				_ = dest
				typed, ok := dest.(*int)
				require.True(t, ok)
				assert.Equal(t, -12345, *typed)
			},
		},
		{
			name:       "get with zero value",
			key:        "test:zero",
			storeValue: 0,
			destFactory: func() interface{} {
				var r int
				return &r
			},
			verify: func(t *testing.T, dest interface{}) {
				_ = dest
				typed, ok := dest.(*int)
				require.True(t, ok)
				assert.Equal(t, 0, *typed)
			},
		},
	}
}

func redisCacheSetNestedStructCase() redisCacheSetCoverageCase {
	return redisCacheSetCoverageCase{
		name: "set with nested struct",
		key:  "test:nested:person",
		setValue: NestedPerson{
			Name: "Jane Doe",
			Age:  28,
			Address: NestedAddress{
				Street: "456 Oak Ave",
				City:   "MetroCity",
				ZIP:    "54321",
			},
			Contact: NestedContact{
				Email: "jane@example.com",
				Phone: "+9876543210",
			},
		},
		destFactory: func() interface{} {
			var r NestedPerson
			return &r
		},
		verify: func(t *testing.T, original, retrieved interface{}) {
			_ = original
			_ = retrieved
			orig, ok := original.(NestedPerson)
			require.True(t, ok)
			retrPtr, ok := retrieved.(*NestedPerson)
			require.True(t, ok)
			retr := *retrPtr
			assert.Equal(t, orig.Name, retr.Name)
			assert.Equal(t, orig.Age, retr.Age)
			assert.Equal(t, orig.Address.City, retr.Address.City)
			assert.Equal(t, orig.Contact.Email, retr.Contact.Email)
		},
	}
}

func redisCacheSetStringSliceCase() redisCacheSetCoverageCase {
	return redisCacheSetCoverageCase{
		name:     "set with slice of strings",
		key:      "test:tags",
		setValue: []string{"golang", "redis", "cache", "testing"},
		destFactory: func() interface{} {
			var r []string
			return &r
		},
		verify: func(t *testing.T, original, retrieved interface{}) {
			_ = original
			_ = retrieved
			orig, ok := original.([]string)
			require.True(t, ok)
			retrPtr, ok := retrieved.(*[]string)
			require.True(t, ok)
			retr := *retrPtr
			assert.Len(t, retr, len(orig))
			assert.Equal(t, "testing", retr[3])
		},
	}
}

func redisCacheSetMapCase() redisCacheSetCoverageCase {
	return redisCacheSetCoverageCase{
		name: "set with map of strings",
		key:  "test:config",
		setValue: map[string]string{
			"env":    "production",
			"debug":  "false",
			"region": "us-west-2",
		},
		destFactory: func() interface{} {
			var r map[string]string
			return &r
		},
		verify: func(t *testing.T, original, retrieved interface{}) {
			_ = original
			_ = retrieved
			retrPtr, ok := retrieved.(*map[string]string)
			require.True(t, ok)
			retr := *retrPtr
			assert.Equal(t, "production", retr["env"])
		},
	}
}

func redisCacheSetBoolAndZeroCases() []redisCacheSetCoverageCase {
	return []redisCacheSetCoverageCase{
		{
			name:     "set with boolean value",
			key:      "test:bool",
			setValue: true,
			destFactory: func() interface{} {
				var r bool
				return &r
			},
			verify: func(t *testing.T, original, retrieved interface{}) {
				_ = original
				_ = retrieved
				retrPtr, ok := retrieved.(*bool)
				require.True(t, ok)
				retr := *retrPtr
				assert.True(t, retr)
			},
		},
		{
			name:     "set with zero value",
			key:      "test:zero",
			setValue: 0,
			destFactory: func() interface{} {
				var r int
				return &r
			},
			verify: func(t *testing.T, original, retrieved interface{}) {
				_ = original
				_ = retrieved
				retrPtr, ok := retrieved.(*int)
				require.True(t, ok)
				retr := *retrPtr
				assert.Equal(t, 0, retr)
			},
		},
	}
}

func runCoverageCacheCases(t *testing.T, cases []coverageCacheCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			withCoverageCache(t, func(ctx context.Context, cache *RedisCache) {
				tc.fn(ctx, t, cache)
			})
		})
	}
}

func runSimpleTestCases(t *testing.T, cases []simpleTestCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func runRedisCacheSetOverwriteMultiple(ctx context.Context, t *testing.T, cache *RedisCache) {
	key := "test:overwrite:multiple"
	for i := 0; i < 5; i++ {
		err := cache.Set(ctx, key, i)
		require.NoError(t, err)

		var retrieved int
		err = cache.Get(ctx, key, &retrieved)
		require.NoError(t, err)
		assert.Equal(t, i, retrieved)
	}
}

func runRedisCacheSetLongKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	var keyBuilder strings.Builder
	keyBuilder.Grow(100)
	keyBuilder.WriteString("test:")
	for idx := 0; idx < 95; idx++ {
		keyBuilder.WriteByte('a')
	}
	longKey := keyBuilder.String()

	err := cache.Set(ctx, longKey, "value")
	require.NoError(t, err)
}

func runRedisCacheDeleteSingleKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	require.NoError(t, cache.Set(ctx, "test:single", "value"))
	err := cache.Delete(ctx, "test:single")
	require.NoError(t, err)

	var retrieved string
	require.NoError(t, cache.Get(ctx, "test:single", &retrieved))
	assert.Empty(t, retrieved)
}

func runRedisCacheDeleteManyKeys(ctx context.Context, t *testing.T, cache *RedisCache) {
	numKeys := 20
	keys := make([]string, numKeys)
	for i := 0; i < numKeys; i++ {
		key := fmt.Sprintf("test:many:%d", i)
		keys[i] = key
		require.NoError(t, cache.Set(ctx, key, fmt.Sprintf("value-%d", i)))
	}

	err := cache.Delete(ctx, keys...)
	require.NoError(t, err)

	for _, key := range keys {
		var retrieved string
		require.NoError(t, cache.Get(ctx, key, &retrieved))
		assert.Empty(t, retrieved)
	}
}

func runRedisCacheDeleteMixedKeys(ctx context.Context, t *testing.T, cache *RedisCache) {
	require.NoError(t, cache.Set(ctx, "test:exists:1", "value1"))
	require.NoError(t, cache.Set(ctx, "test:exists:2", "value2"))

	err := cache.Delete(ctx,
		"test:exists:1",
		"test:nonexist:1",
		"test:exists:2",
		"test:nonexist:2",
	)
	require.NoError(t, err)
}

func runRedisCacheDeleteSpecialKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	specialKey := "test:special:*?[]{}"
	require.NoError(t, cache.Set(ctx, specialKey, "value"))
	err := cache.Delete(ctx, specialKey)
	require.NoError(t, err)
}

func runRedisCacheInvalidateSinglePattern(ctx context.Context, t *testing.T, cache *RedisCache) {
	require.NoError(t, cache.Set(ctx, "project:1", "val1"))
	require.NoError(t, cache.Set(ctx, "project:2", "val2"))

	err := cache.InvalidatePattern(ctx, "project:*")
	require.NoError(t, err)
}

func runRedisCacheInvalidateDots(ctx context.Context, t *testing.T, cache *RedisCache) {
	require.NoError(t, cache.Set(ctx, "search:user.email:query", "val1"))
	require.NoError(t, cache.Set(ctx, "search:user.name:query", "val2"))
	require.NoError(t, cache.Set(ctx, "item:123", "val3"))

	err := cache.InvalidatePattern(ctx, "search:*")
	require.NoError(t, err)
}

func runRedisCacheInvalidateComplex(ctx context.Context, t *testing.T, cache *RedisCache) {
	require.NoError(t, cache.Set(ctx, "agent:type:gpt4:1", "val1"))
	require.NoError(t, cache.Set(ctx, "agent:type:gpt4:2", "val2"))
	require.NoError(t, cache.Set(ctx, "agent:type:claude:1", "val3"))

	err := cache.InvalidatePattern(ctx, "agent:type:gpt4:*")
	require.NoError(t, err)
}

func runRedisCacheInvalidateNoMatch(ctx context.Context, t *testing.T, cache *RedisCache) {
	require.NoError(t, cache.Set(ctx, "project:1", "val1"))

	err := cache.InvalidatePattern(ctx, "nomatch:*")
	require.NoError(t, err)
}

func runRedisCacheInvalidateAll(ctx context.Context, t *testing.T, cache *RedisCache) {
	for i := 0; i < 5; i++ {
		require.NoError(t, cache.Set(ctx, fmt.Sprintf("key:%d", i), fmt.Sprintf("val-%d", i)))
	}

	err := cache.InvalidatePattern(ctx, "*")
	require.NoError(t, err)
}

func runProjectKeyNumeric(t *testing.T) {
	key := ProjectKey("123")
	assert.Equal(t, "project:123", key)
}

func runProjectKeyUUID(t *testing.T) {
	uuid := "550e8400-e29b-41d4-a716-446655440000"
	key := ProjectKey(uuid)
	assert.Equal(t, "project:"+uuid, key)
	assert.Contains(t, key, "project:")
}

func runItemKeyVariations(t *testing.T) {
	testCases := []string{"1", "abc-123", "item_456", "item.789"}
	for _, id := range testCases {
		key := ItemKey(id)
		assert.Equal(t, "item:"+id, key)
		assert.Greater(t, len(key), 5)
	}
}

func runLinkKeyHyphenated(t *testing.T) {
	key := LinkKey("link-123-456")
	assert.Equal(t, "link:link-123-456", key)
}

func runAgentKeyFormats(t *testing.T) {
	testCases := []struct {
		input    string
		expected string
	}{
		{"simple", "agent:simple"},
		{"with-dash", "agent:with-dash"},
		{"with_underscore", "agent:with_underscore"},
		{"123", "agent:123"},
	}

	for _, tc := range testCases {
		assert.Equal(t, tc.expected, AgentKey(tc.input))
	}
}

func runSearchKeyVariations(t *testing.T) {
	testCases := []struct {
		query         string
		projectID     string
		shouldContain []string
	}{
		{"test query", "proj-123", []string{"search:", "proj-123", "test query"}},
		{"", "proj", []string{"search:proj:"}},
		{"query", "", []string{"search::query"}},
	}

	for _, tc := range testCases {
		key := SearchKey(tc.query, tc.projectID)
		for _, substr := range tc.shouldContain {
			assert.Contains(t, key, substr)
		}
	}
}

func runKeyPatternsDefined(t *testing.T) {
	assert.NotEmpty(t, ProjectKeyPattern)
	assert.NotEmpty(t, ItemKeyPattern)
	assert.NotEmpty(t, LinkKeyPattern)
	assert.NotEmpty(t, AgentKeyPattern)
	assert.NotEmpty(t, SearchKeyPattern)

	assert.Equal(t, "project:*", ProjectKeyPattern)
	assert.Equal(t, "item:*", ItemKeyPattern)
	assert.Equal(t, "link:*", LinkKeyPattern)
	assert.Equal(t, "agent:*", AgentKeyPattern)
	assert.Equal(t, "search:*", SearchKeyPattern)
}

func runRedisCacheConcurrentSameKey(ctx context.Context, t *testing.T, cache *RedisCache) {
	key := "test:concurrent:same"
	var wg sync.WaitGroup
	numGoroutines := 30
	errors := make([]error, numGoroutines*2)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			err := cache.Set(ctx, key, idx)
			errors[idx] = err
		}(i)

		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			var result int
			err := cache.Get(ctx, key, &result)
			errors[numGoroutines+idx] = err
		}(i)
	}

	wg.Wait()

	for i, err := range errors {
		require.NoError(t, err, "goroutine %d failed", i)
	}
}

func runRedisCacheConcurrentDelete(ctx context.Context, t *testing.T, cache *RedisCache) {
	for i := 0; i < 50; i++ {
		require.NoError(t, cache.Set(ctx, fmt.Sprintf("test:del:%d", i), i))
	}

	var wg sync.WaitGroup
	numGoroutines := 50
	errors := make([]error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			key := fmt.Sprintf("test:del:%d", idx)
			errors[idx] = cache.Delete(ctx, key)
		}(i)
	}

	wg.Wait()

	for i, err := range errors {
		require.NoError(t, err, "goroutine %d failed", i)
	}
}

func runRedisCacheConcurrentInvalidatePattern(ctx context.Context, t *testing.T, cache *RedisCache) {
	for i := 0; i < 30; i++ {
		require.NoError(t, cache.Set(ctx, ProjectKey(strconv.Itoa(i)), i))
	}

	var wg sync.WaitGroup
	numGoroutines := 10
	errors := make([]error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			errors[idx] = cache.InvalidatePattern(ctx, ProjectKeyPattern)
		}(i)
	}

	wg.Wait()

	for i, err := range errors {
		require.NoError(t, err, "goroutine %d failed", i)
	}
}

func runRedisCacheHighConcurrencyStress(ctx context.Context, t *testing.T, cache *RedisCache) {
	var wg sync.WaitGroup
	numGoroutines := 100
	successCount := int32(0)
	errorCount := int32(0)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()

			key := fmt.Sprintf("stress:%d", idx%10)

			switch idx % 3 {
			case 0:
				if err := cache.Set(ctx, key, idx); err == nil {
					atomic.AddInt32(&successCount, 1)
				} else {
					atomic.AddInt32(&errorCount, 1)
				}
			case 1:
				var result int
				if err := cache.Get(ctx, key, &result); err == nil {
					atomic.AddInt32(&successCount, 1)
				} else {
					atomic.AddInt32(&errorCount, 1)
				}
			case 2:
				if err := cache.Delete(ctx, key); err == nil {
					atomic.AddInt32(&successCount, 1)
				} else {
					atomic.AddInt32(&errorCount, 1)
				}
			}
		}(i)
	}

	wg.Wait()

	assert.Positive(t, successCount)
}

func runRedisCacheDataTypeObject(ctx context.Context, t *testing.T, cache *RedisCache) {
	obj := TestItem{ID: 100, Name: "test", Value: "data"}
	err := cache.Set(ctx, "test:obj", obj)
	require.NoError(t, err)

	var retrieved TestItem
	err = cache.Get(ctx, "test:obj", &retrieved)
	require.NoError(t, err)
	assert.Equal(t, obj, retrieved)
}

func runRedisCacheDataTypeArray(ctx context.Context, t *testing.T, cache *RedisCache) {
	arr := []TestItem{
		{ID: 1, Name: "a", Value: "x"},
		{ID: 2, Name: "b", Value: "y"},
	}

	err := cache.Set(ctx, "test:arr", arr)
	require.NoError(t, err)

	var retrieved []TestItem
	err = cache.Get(ctx, "test:arr", &retrieved)
	require.NoError(t, err)
	assert.Len(t, retrieved, len(arr))
}

func runRedisCacheDataTypeMap(ctx context.Context, t *testing.T, cache *RedisCache) {
	metrics := map[string]interface{}{
		"string": "value",
		"number": 42.0,
		"bool":   true,
	}

	err := cache.Set(ctx, "test:map", metrics)
	require.NoError(t, err)

	var retrieved map[string]interface{}
	err = cache.Get(ctx, "test:map", &retrieved)
	require.NoError(t, err)
	assert.Len(t, retrieved, len(metrics))
}

func withCoverageCache(t *testing.T, fn func(ctx context.Context, cache *RedisCache)) {
	ctx := context.Background()
	cache := setupTestCacheMock(t)
	if cache == nil {
		t.Skip("Redis not available for coverage test")
	}
	defer func() {
		if err := cache.Close(); err != nil {
			t.Logf("error closing cache: %v", err)
		}
	}()

	fn(ctx, cache)
}

// Helper function to setup test cache
func setupTestCacheMock(t *testing.T) *RedisCache {
	_ = t
	url := os.Getenv("TEST_REDIS_URL")
	if url == "" {
		url = testRedisURL
	}

	cache, err := NewRedisCache(RedisCacheConfig{
		RedisURL:      url,
		DefaultTTL:    redisCoverageTestTTL,
		EnableMetrics: true,
	})
	if err != nil {
		// Return nil to signal skip if Redis not available
		return nil
	}

	ctx := context.Background()
	cache.client.FlushDB(ctx)

	return cache
}
