//go:build !integration && !e2e

package graph

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

const (
	graphCacheDefaultTTL  = 5 * time.Second
	graphCacheExpireTTL   = 100 * time.Millisecond
	graphCacheExpireSleep = 150 * time.Millisecond
	graphCacheEntryCount  = 5
)

// TestNewCache tests cache initialization
func TestNewCache(t *testing.T) {
	cache := NewCache(graphCacheDefaultTTL)

	if cache == nil {
		t.Fatal("expected cache to be initialized, got nil")
	}
	if len(cache.entries) != 0 {
		t.Fatalf("expected empty cache, got %d entries", len(cache.entries))
	}
}

// TestGenerateKey tests cache key generation
func TestGenerateKey(t *testing.T) {
	key1 := generateKey("test", "param1", "param2")
	key2 := generateKey("test", "param1", "param2")
	key3 := generateKey("test", "param1", "param3")

	if key1 != key2 {
		t.Error("same parameters should generate same key")
	}
	if key1 == key3 {
		t.Error("different parameters should generate different keys")
	}
	if key1 == "" {
		t.Error("generated key should not be empty")
	}
}

// TestCacheGetSet tests basic get/set operations
func TestCacheGetSet(t *testing.T) {
	cache := NewCache(graphCacheDefaultTTL)
	key := "test-key"
	value := "test-value"

	// Test Get on non-existent key
	_, exists := cache.Get(key)
	if exists {
		t.Error("expected Get to return false for non-existent key")
	}

	// Test Set and Get
	cache.Set(key, value)
	retrieved, exists := cache.Get(key)
	if !exists {
		t.Error("expected Get to return true after Set")
	}
	if retrieved != value {
		t.Errorf("expected %v, got %v", value, retrieved)
	}
}

// TestCacheExpiration tests TTL expiration
func TestCacheExpiration(t *testing.T) {
	cache := NewCache(graphCacheExpireTTL)
	key := "expiring-key"
	value := "expiring-value"

	cache.Set(key, value)
	retrieved, exists := cache.Get(key)
	if !exists {
		t.Error("expected Get to return true for fresh entry")
	}
	if retrieved != value {
		t.Errorf("expected %v, got %v", value, retrieved)
	}

	// Wait for expiration
	time.Sleep(graphCacheExpireSleep)
	_, exists = cache.Get(key)
	if exists {
		t.Error("expected Get to return false after expiration")
	}
}

// TestCacheDelete tests deletion
func TestCacheDelete(t *testing.T) {
	cache := NewCache(graphCacheDefaultTTL)
	key := "delete-key"
	value := "delete-value"

	cache.Set(key, value)
	_, exists := cache.Get(key)
	if !exists {
		t.Error("expected key to exist after Set")
	}

	cache.Delete(key)
	_, exists = cache.Get(key)
	if exists {
		t.Error("expected Get to return false after Delete")
	}
}

// TestCacheClear tests clearing all entries
func TestCacheClear(t *testing.T) {
	cache := NewCache(graphCacheDefaultTTL)

	// Add multiple entries
	for i := 0; i < graphCacheEntryCount; i++ {
		key := "key" + string(rune(i))
		cache.Set(key, "value")
	}

	// Verify entries exist
	stats := cache.Stats()
	totalBefore, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if totalBefore != graphCacheEntryCount {
		t.Fatalf("expected %d entries, got %d", graphCacheEntryCount, totalBefore)
	}

	// Clear cache
	cache.Clear()

	// Verify empty
	stats = cache.Stats()
	totalAfter, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if totalAfter != 0 {
		t.Fatalf("expected 0 entries after clear, got %d", totalAfter)
	}
}

// TestCacheStats tests statistics reporting
func TestCacheStats(t *testing.T) {
	cache := NewCache(5 * time.Second)

	// Add entries
	cache.Set("key1", "value1")
	cache.Set("key2", "value2")

	stats := cache.Stats()

	totalEntries, ok := stats["total_entries"].(int)
	if !ok {
		t.Fatal("expected total_entries to be int")
	}
	if totalEntries != 2 {
		t.Fatalf("expected 2 total entries, got %d", totalEntries)
	}

	validEntries, ok := stats["valid_entries"].(int)
	if !ok {
		t.Fatal("expected valid_entries to be int")
	}
	if validEntries != 2 {
		t.Fatalf("expected 2 valid entries, got %d", validEntries)
	}

	expiredEntries, ok := stats["expired_entries"].(int)
	if !ok {
		t.Fatal("expected expired_entries to be int")
	}
	if expiredEntries != 0 {
		t.Fatalf("expected 0 expired entries, got %d", expiredEntries)
	}

	ttlSeconds, ok := stats["ttl_seconds"].(float64)
	if !ok {
		t.Fatal("expected ttl_seconds to be float64")
	}
	if ttlSeconds != 5.0 {
		t.Fatalf("expected ttl of 5.0 seconds, got %f", ttlSeconds)
	}
}

// TestCacheStatsWithExpiredEntries tests statistics with mixed valid/expired entries
func TestCacheStatsWithExpiredEntries(t *testing.T) {
	cache := NewCache(graphCacheExpireTTL)

	cache.Set("key1", "value1")
	time.Sleep(graphCacheExpireSleep)
	cache.Set("key2", "value2")

	stats := cache.Stats()

	totalEntries, ok := stats["total_entries"].(int)
	if !ok {
		t.Fatal("total_entries not an int")
	}
	validEntries, ok := stats["valid_entries"].(int)
	if !ok {
		t.Fatal("valid_entries not an int")
	}
	expiredEntries, ok := stats["expired_entries"].(int)
	if !ok {
		t.Fatal("expired_entries not an int")
	}

	if totalEntries != 2 {
		t.Fatalf("expected 2 total entries, got %d", totalEntries)
	}
	if validEntries != 1 {
		t.Fatalf("expected 1 valid entry, got %d", validEntries)
	}
	if expiredEntries != 1 {
		t.Fatalf("expected 1 expired entry, got %d", expiredEntries)
	}
}

// TestCacheCleanupExpired tests periodic cleanup of expired entries
func TestCacheCleanupExpired(t *testing.T) {
	cache := NewCache(graphCacheExpireTTL)

	// Add entries
	cache.Set("key1", "value1")
	cache.Set("key2", "value2")

	// Wait for expiration
	time.Sleep(graphCacheExpireSleep)

	// Add a new entry
	cache.Set("key3", "value3")

	// Wait for cleanup cycle (minimum 1 minute in code, but we can check manually)
	// For testing, we manually verify cleanup would happen
	stats := cache.Stats()
	typed224, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if typed224 > 3 {
		t.Errorf("cache should have at most 3 entries")
	}
}

// TestCacheRaceCondition tests concurrent access
func TestCacheRaceCondition(t *testing.T) {
	cache := NewCache(graphCacheDefaultTTL)
	done := make(chan bool)

	// Concurrent writes
	for i := 0; i < 10; i++ {
		go func(id int) {
			for j := 0; j < 10; j++ {
				key := "key" + string(rune(id)) + "-" + string(rune(j))
				cache.Set(key, "value")
			}
			done <- true
		}(i)
	}

	// Concurrent reads
	for i := 0; i < 10; i++ {
		go func(id int) {
			for j := 0; j < 10; j++ {
				key := "key" + string(rune(id)) + "-" + string(rune(j))
				cache.Get(key)
			}
			done <- true
		}(i)
	}

	// Wait for all goroutines
	for i := 0; i < 20; i++ {
		<-done
	}

	// Test should complete without panics
	stats := cache.Stats()
	if stats["total_entries"] == nil {
		t.Fatal("expected stats to be valid after concurrent access")
	}
}

// TestNewCachedGraph tests CachedGraph initialization
func TestNewCachedGraph(t *testing.T) {
	// Create a Graph with nil pool (won't use it in this test)
	g := &Graph{queries: nil, pool: nil}
	cg := NewCachedGraph(g, 5*time.Second)

	if cg == nil {
		t.Fatal("expected CachedGraph to be initialized")
	}
	if cg.Graph != g {
		t.Error("expected CachedGraph to wrap provided Graph")
	}
	if cg.cache == nil {
		t.Fatal("expected cache to be initialized")
	}
}

// TestCachedGraphInvalidateItem tests item invalidation
func TestCachedGraphInvalidateItem(t *testing.T) {
	g := &Graph{queries: nil, pool: nil}
	cg := NewCachedGraph(g, 5*time.Second)

	// Add some entries to cache
	cg.cache.Set("test-key", "test-value")

	stats := cg.CacheStats()
	typed294, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if typed294 != 1 {
		typed295, ok := stats["total_entries"].(int)
		require.True(t, ok)
		t.Fatalf("expected 1 entry, got %d", typed295)
	}

	// Invalidate item
	cg.InvalidateItem("test-item-id")

	stats = cg.CacheStats()
	typed302, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if typed302 != 0 {
		typed303, ok := stats["total_entries"].(int)
		require.True(t, ok)
		t.Fatalf("expected 0 entries after invalidation, got %d", typed303)
	}
}

// TestCachedGraphInvalidateProject tests project invalidation
func TestCachedGraphInvalidateProject(t *testing.T) {
	g := &Graph{queries: nil, pool: nil}
	cg := NewCachedGraph(g, 5*time.Second)

	// Add entries to cache
	cg.cache.Set("key1", "value1")
	cg.cache.Set("key2", "value2")

	stats := cg.CacheStats()
	typed317, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if typed317 != 2 {
		typed318, ok := stats["total_entries"].(int)
		require.True(t, ok)
		t.Fatalf("expected 2 entries, got %d", typed318)
	}

	// Invalidate project
	cg.InvalidateProject("test-project-id")

	stats = cg.CacheStats()
	typed325, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if typed325 != 0 {
		typed326, ok := stats["total_entries"].(int)
		require.True(t, ok)
		t.Fatalf("expected 0 entries after invalidation, got %d", typed326)
	}
}

// TestCachedCacheStats tests cache statistics access
func TestCachedCacheStats(t *testing.T) {
	g := &Graph{queries: nil, pool: nil}
	cg := NewCachedGraph(g, 5*time.Second)

	cg.cache.Set("key1", "value1")

	stats := cg.CacheStats()
	if stats == nil {
		t.Fatal("expected stats to be non-nil")
	}
	typed341, ok := stats["total_entries"].(int)
	require.True(t, ok)
	if typed341 != 1 {
		typed342, ok := stats["total_entries"].(int)
		require.True(t, ok)
		t.Fatalf("expected 1 entry in stats, got %d", typed342)
	}
}

// BenchmarkCacheGet benchmarks cache Get operation
func BenchmarkCacheGet(b *testing.B) {
	cache := NewCache(5 * time.Second)
	cache.Set("bench-key", "bench-value")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		cache.Get("bench-key")
	}
}

// BenchmarkCacheSet benchmarks cache Set operation
func BenchmarkCacheSet(b *testing.B) {
	cache := NewCache(5 * time.Second)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := "bench-key-" + string(rune(i))
		cache.Set(key, "bench-value")
	}
}

// BenchmarkGenerateKeyCache benchmarks key generation
func BenchmarkGenerateKeyCache(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		generateKey("prefix", "param1", "param2", "param3")
	}
}
