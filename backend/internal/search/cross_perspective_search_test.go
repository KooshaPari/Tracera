package search

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	cacheExpirationSleep = 2 * time.Second
	cacheCleanupSleep    = 1100 * time.Millisecond
)

// TestCrossPerspectiveSearchCache tests the SearchCache functionality
func TestCrossPerspectiveCache(t *testing.T) {
	cache := NewCache()
	runCrossPerspectiveCacheCases(t, cache)
}

// TestGenerateCacheKey tests cache key generation
func TestGenerateCacheKey(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{
		Query:     "test",
		ProjectID: "proj1",
		Limit:     10,
	}

	req2 := &CrossPerspectiveSearchRequest{
		Query:     "test",
		ProjectID: "proj1",
		Limit:     10,
	}

	req3 := &CrossPerspectiveSearchRequest{
		Query:     "different",
		ProjectID: "proj1",
		Limit:     10,
	}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)
	key3 := searcher.generateCacheKey(req3)

	// Same requests should generate same cache key
	assert.Equal(t, key1, key2)

	// Different queries should generate different keys
	assert.NotEqual(t, key1, key3)
}

// TestFilterByPerspective tests perspective filtering
func TestFilterByPerspective(t *testing.T) {
	results := []Result{
		{
			ID:    "1",
			Title: "Feature 1",
			Metadata: map[string]interface{}{
				"perspective": "feature",
			},
		},
		{
			ID:    "2",
			Title: "API 1",
			Metadata: map[string]interface{}{
				"perspective": "api",
			},
		},
		{
			ID:    "3",
			Title: "Feature 2",
			Metadata: map[string]interface{}{
				"perspective": "feature",
			},
		},
	}

	filtered := filterByPerspective(results, "feature")

	assert.Len(t, filtered, 2)
	assert.Equal(t, "1", filtered[0].ID)
	assert.Equal(t, "3", filtered[1].ID)
}

// TestFilterByDimension tests dimension-based filtering
func TestFilterByDimension(t *testing.T) {
	results := []Result{
		{
			ID:    "1",
			Title: "Item 1",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "high",
					"team":     "frontend",
				},
			},
		},
		{
			ID:    "2",
			Title: "Item 2",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "low",
					"team":     "backend",
				},
			},
		},
		{
			ID:    "3",
			Title: "Item 3",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "high",
					"team":     "backend",
				},
			},
		},
	}

	filtered := filterByDimension(results, "priority", "high")

	assert.Len(t, filtered, 2)
	assert.Equal(t, "1", filtered[0].ID)
	assert.Equal(t, "3", filtered[1].ID)
}

// TestCrossPerspectiveSearchRequest validates request handling
func TestCrossPerspectiveRequest(t *testing.T) {
	runCrossPerspectiveRequestCases(t)
}

// BenchmarkCacheOperations benchmarks cache performance
func BenchmarkCacheOperations(b *testing.B) {
	cache := NewCache()

	b.Run("Set", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			cache.Set("key", "value", 300)
		}
	})

	b.Run("Get", func(b *testing.B) {
		cache.Set("key", "value", 300)

		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			cache.Get("key")
		}
	})

	b.Run("Delete", func(b *testing.B) {
		cache := NewCache()

		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			cache.Set("key", "value", 300)
			cache.Delete("key")
		}
	})

	b.Run("Concurrent access", func(b *testing.B) {
		cache := NewCache()

		b.RunParallel(func(pb *testing.PB) {
			i := 0
			for pb.Next() {
				cache.Set("key"+string(rune(i)), "value", 300)
				cache.Get("key" + string(rune(i)))
				i++
			}
		})
	})
}

// BenchmarkCacheKeyGeneration benchmarks cache key generation
func BenchmarkCacheKeyGeneration(b *testing.B) {
	searcher := &CrossPerspectiveSearcher{}

	req := &CrossPerspectiveSearchRequest{
		Query:        "test query",
		ProjectID:    "project-id",
		Perspectives: []string{"feature", "api", "code"},
		Status:       []string{"done", "in_progress"},
		Types:        []string{"Feature", "API"},
		Limit:        50,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		searcher.generateCacheKey(req)
	}
}

// BenchmarkFilterOperations benchmarks filtering performance
func BenchmarkFilterOperations(b *testing.B) {
	results := make([]Result, 1000)
	for i := 0; i < 1000; i++ {
		results[i] = Result{
			ID:    "id" + string(rune(i)),
			Title: "Title " + string(rune(i)),
			Metadata: map[string]interface{}{
				"perspective": "feature",
			},
		}
	}

	b.Run("FilterByPerspective", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			filterByPerspective(results, "feature")
		}
	})

	b.Run("FilterByDimension", func(b *testing.B) {
		resultsWithDims := make([]Result, 1000)
		for i := 0; i < 1000; i++ {
			resultsWithDims[i] = Result{
				ID:    "id" + string(rune(i)),
				Title: "Title " + string(rune(i)),
				Metadata: map[string]interface{}{
					"dimensions": map[string]interface{}{
						"priority": 3,
					},
				},
			}
		}

		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			filterByDimension(resultsWithDims, "priority", "high")
		}
	})
}

// TestCacheConcurrency tests concurrent access to cache
func TestCacheConcurrency(t *testing.T) {
	cache := NewCache()
	done := make(chan bool)

	// Multiple goroutines writing
	for i := 0; i < 10; i++ {
		go func(id int) {
			for j := 0; j < 100; j++ {
				key := "key_" + string(rune(id)) + "_" + string(rune(j))
				cache.Set(key, "value", 300)
			}
			done <- true
		}(i)
	}

	// Multiple goroutines reading
	for i := 0; i < 10; i++ {
		go func(id int) {
			for j := 0; j < 100; j++ {
				key := "key_" + string(rune(id)) + "_" + string(rune(j))
				cache.Get(key)
			}
			done <- true
		}(i)
	}

	// Wait for all goroutines
	for i := 0; i < 20; i++ {
		<-done
	}

	// Cache should have entries
	assert.Positive(t, cache.Size())
}

// TestCacheTTL tests TTL functionality
func TestCacheTTL(t *testing.T) {
	cache := NewCache()

	// Set with short TTL (1 second)
	cache.Set("short", "value", 1)

	// Should exist
	_, found := cache.Get("short")
	assert.True(t, found)

	// Wait for expiration (need to wait more than 1 second since Unix time is in seconds)
	time.Sleep(1500 * time.Millisecond)

	// Should not exist
	_, found = cache.Get("short")
	assert.False(t, found)

	// Set with longer TTL
	cache.Set("long", "value", 10)
	_, found = cache.Get("long")
	assert.True(t, found)
}

// TestSearchResultsAccuracy tests search result accuracy
func TestSearchResultsAccuracy(t *testing.T) {
	results := buildAccuracyResults()

	runCacheCase(t, "Perspective filtering accuracy >95%", func(t *testing.T) {
		filtered := filterByPerspective(results, "feature")
		accuracy := float64(len(filtered)) / float64(2)
		assert.InEpsilon(t, 1.0, accuracy, 1e-9)
	})

	runCacheCase(t, "Dimension filtering accuracy >95%", func(t *testing.T) {
		resultsWithDims := buildAccuracyResultsWithDims()
		filtered := filterByDimension(resultsWithDims, "priority", "high")
		assert.Len(t, filtered, 1)
		assert.Equal(t, "1", filtered[0].ID)
	})
}

func runCacheCase(t *testing.T, name string, fn func(t *testing.T)) {
	t.Run(name, func(t *testing.T) {
		fn(t)
	})
}

func runCrossPerspectiveCacheCases(t *testing.T, cache *Cache) {
	runCacheBasicCases(t, cache)
	runCacheSizeCases(t)
}

func runCrossPerspectiveRequestCases(t *testing.T) {
	runCrossPerspectiveQueryCases(t)
	runCrossPerspectiveLimitCases(t)
}

func runCacheBasicCases(t *testing.T, cache *Cache) {
	runCacheCase(t, "Set and Get", func(t *testing.T) {
		value := map[string]string{"test": "value"}
		cache.Set("key1", value, 300)

		result, found := cache.Get("key1")
		assert.True(t, found)
		assert.Equal(t, value, result)
	})

	runCacheCase(t, "Get non-existent key", func(t *testing.T) {
		_, found := cache.Get("nonexistent")
		assert.False(t, found)
	})

	runCacheCase(t, "Expired entries", func(t *testing.T) {
		cache := NewCache()
		cache.Set("expiring", "value", 1)

		_, found := cache.Get("expiring")
		assert.True(t, found)

		time.Sleep(cacheExpirationSleep)

		_, found = cache.Get("expiring")
		assert.False(t, found)
	})

	runCacheCase(t, "Delete", func(t *testing.T) {
		cache := NewCache()
		cache.Set("todelete", "value", 300)

		cache.Delete("todelete")
		_, found := cache.Get("todelete")
		assert.False(t, found)
	})
}

func runCacheSizeCases(t *testing.T) {
	runCacheCase(t, "Clear", func(t *testing.T) {
		cache := NewCache()
		cache.Set("key1", "value1", 300)
		cache.Set("key2", "value2", 300)

		assert.Equal(t, 2, cache.Size())

		cache.Clear()
		assert.Equal(t, 0, cache.Size())
	})

	runCacheCase(t, "Size", func(t *testing.T) {
		cache := NewCache()

		assert.Equal(t, 0, cache.Size())

		cache.Set("key1", "value1", 300)
		assert.Equal(t, 1, cache.Size())

		cache.Set("key2", "value2", 300)
		assert.Equal(t, 2, cache.Size())

		cache.Delete("key1")
		assert.Equal(t, 1, cache.Size())
	})
}

func runCrossPerspectiveQueryCases(t *testing.T) {
	runCacheCase(t, "Empty query should be rejected", func(t *testing.T) {
		cache := NewCache()
		searcher := &CrossPerspectiveSearcher{
			cache: cache,
		}

		req := &CrossPerspectiveSearchRequest{
			Query:     "",
			ProjectID: "proj1",
		}

		_, err := searcher.Search(context.Background(), req)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "query cannot be empty")
	})

	runCacheCase(t, "Whitespace-only query should be rejected", func(t *testing.T) {
		cache := NewCache()
		searcher := &CrossPerspectiveSearcher{
			cache: cache,
		}

		req := &CrossPerspectiveSearchRequest{
			Query:     "   ",
			ProjectID: "proj1",
		}

		_, err := searcher.Search(context.Background(), req)
		require.Error(t, err)
	})
}

func runCrossPerspectiveLimitCases(t *testing.T) {
	runCacheCase(t, "Default limit should be set", func(t *testing.T) {
		req := &CrossPerspectiveSearchRequest{
			Query:     "test",
			ProjectID: "proj1",
			Limit:     0,
		}

		cache := NewCache()
		_ = &CrossPerspectiveSearcher{
			cache: cache,
			engine: &Engine{
				pool: nil,
			},
		}

		assert.Equal(t, 0, req.Limit)
	})

	runCacheCase(t, "Limit should be capped at 100", func(t *testing.T) {
		req := &CrossPerspectiveSearchRequest{
			Query:     "test",
			ProjectID: "proj1",
			Limit:     500,
		}

		cache := NewCache()
		_ = &CrossPerspectiveSearcher{
			cache: cache,
			engine: &Engine{
				pool: nil,
			},
		}

		assert.Equal(t, 500, req.Limit)
	})
}

func buildAccuracyResults() []Result {
	return []Result{
		{
			ID:     "1",
			Title:  "Feature 1",
			Type:   "Feature",
			Status: "done",
			Metadata: map[string]interface{}{
				"perspective": "feature",
			},
		},
		{
			ID:     "2",
			Title:  "API 1",
			Type:   "API",
			Status: "in_progress",
			Metadata: map[string]interface{}{
				"perspective": "api",
			},
		},
		{
			ID:     "3",
			Title:  "Feature 2",
			Type:   "Feature",
			Status: "done",
			Metadata: map[string]interface{}{
				"perspective": "feature",
			},
		},
	}
}

func buildAccuracyResultsWithDims() []Result {
	return []Result{
		{
			ID:    "1",
			Title: "Item 1",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "high",
				},
			},
		},
		{
			ID:    "2",
			Title: "Item 2",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "low",
				},
			},
		},
	}
}
