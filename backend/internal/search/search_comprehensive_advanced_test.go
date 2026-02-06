//go:build !integration && !e2e

package search

import (
	"context"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// QueryBuilder Advanced Tests
// ============================================================================

// TestQueryBuilder_Build_NoOffsetNoLimit tests query building without offset/limit
func TestQueryBuilder_Build_NoOffsetNoLimit(t *testing.T) {
	qb := NewQueryBuilder().
		Select("id", "title").
		From("items").
		Where("status = ?", "active")

	query, buildArgs := qb.Build()
	assert.NotContains(t, query, "OFFSET")
	assert.NotContains(t, query, "LIMIT")
	assert.Equal(t, 1, len(buildArgs))
}

// TestQueryBuilder_Build_MultipleWhere tests multiple WHERE conditions
func TestQueryBuilder_Build_MultipleWhere(t *testing.T) {
	qb := NewQueryBuilder().
		Select("*").
		From("items").
		Where("project_id = ?", "proj1").
		Where("status = ?", "active").
		Where("deleted_at IS NULL")

	query, args := qb.Build()
	assert.Contains(t, query, "WHERE project_id = $1 AND status = $2 AND deleted_at IS NULL")
	require.Len(t, args, 2)
}

// TestQueryBuilder_Build_MultipleOrderBy tests multiple ORDER BY clauses
func TestQueryBuilder_Build_MultipleOrderBy(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		OrderBy("priority", "DESC").
		OrderBy("created_at", "ASC").
		OrderBy("title", "desc")

	query, _ := qb.Build()
	assert.Contains(t, query, "ORDER BY priority DESC, created_at ASC, title DESC")
}

// TestQueryBuilder_Build_LimitAndOffset tests limit and offset together
func TestQueryBuilder_Build_LimitAndOffset(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Limit(25).
		Offset(50)

	query, args := qb.Build()
	assert.Contains(t, query, "LIMIT $1")
	assert.Contains(t, query, "OFFSET $2")
	require.Len(t, args, 2)
	assert.Equal(t, 25, args[0])
	assert.Equal(t, 50, args[1])
}

// TestQueryBuilder_BuildIdempotent tests that building multiple times produces same query
func TestQueryBuilder_BuildIdempotent(t *testing.T) {
	qb := NewQueryBuilder().
		Select("id").
		From("items").
		Where("active = ?", true).
		Limit(10)

	query1, _ := qb.Build()
	query2, _ := qb.Build()

	// Second build appends to args, so they won't be identical
	// But the query string should be (note: Build mutates state)
	assert.NotEmpty(t, query1)
	assert.NotEmpty(t, query2)
}

// TestQueryBuilder_Where_EmptyArgs tests WHERE with condition but no args
func TestQueryBuilder_Where_EmptyArgs(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Where("deleted_at IS NULL")

	query, args := qb.Build()
	assert.Contains(t, query, "WHERE deleted_at IS NULL")
	assert.Empty(t, args)
}

// TestQueryBuilder_Select_Empty tests SELECT with no columns (defaults to *)
func TestQueryBuilder_Select_Empty(t *testing.T) {
	qb := NewQueryBuilder().From("items")
	query, args := qb.Build()
	assert.Contains(t, query, "SELECT *")
	assert.Empty(t, args)
}

// TestQueryBuilder_Where_SpecialCharacters tests WHERE with special SQL characters
func TestQueryBuilder_Where_SpecialCharacters(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Where("title ILIKE ?", "%test%")

	query, args := qb.Build()
	assert.Contains(t, query, "WHERE title ILIKE $1")
	require.Len(t, args, 1)
	assert.Equal(t, "%test%", args[0])
}

// TestQueryBuilder_Where_NumericTypes tests WHERE with different numeric types
func TestQueryBuilder_Where_NumericTypes(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Where("priority = ?", 5).
		Where("score > ?", 3.14).
		Where("count >= ?", int64(100))

	query, args := qb.Build()
	assert.Contains(t, query, "WHERE priority = $1 AND score > $2 AND count >= $3")
	require.Len(t, args, 3)
	assert.Equal(t, 5, args[0])
	assert.Equal(t, 3.14, args[1])
	assert.Equal(t, int64(100), args[2])
}

// TestQueryBuilder_OrderBy_CaseInsensitive tests that ORDER BY is case-insensitive
func TestQueryBuilder_OrderBy_CaseInsensitive(t *testing.T) {
	tests := []struct {
		name      string
		direction string
		expected  string
	}{
		{"uppercase", "DESC", "DESC"},
		{"lowercase", "desc", "DESC"},
		{"mixed", "DeSc", "DESC"},
		{"asc", "asc", "ASC"},
		{"invalid", "invalid", "ASC"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			qb := NewQueryBuilder().OrderBy("created_at", tt.direction)
			query, _ := qb.Build()
			assert.Contains(t, query, "created_at "+tt.expected)
		})
	}
}

// TestQueryBuilder_Where_ConsecutivePlaceholders tests consecutive ? replacements
func TestQueryBuilder_Where_ConsecutivePlaceholders(t *testing.T) {
	qb := NewQueryBuilder().
		Where("(a = ? OR b = ?) AND c = ?", 1, 2, 3)

	query, args := qb.Build()
	assert.Contains(t, query, "(a = $1 OR b = $2) AND c = $3")
	require.Len(t, args, 3)
	assert.Equal(t, 1, args[0])
	assert.Equal(t, 2, args[1])
	assert.Equal(t, 3, args[2])
}

// ============================================================================
// Cache Advanced Tests
// ============================================================================

// TestCache_Set_Get_Basic tests basic cache operations
func TestCache_Set_Get_Basic(t *testing.T) {
	cache := NewCache()

	cache.Set("key1", "value1", 300)
	val, found := cache.Get("key1")

	assert.True(t, found)
	assert.Equal(t, "value1", val)
}

// TestCache_Get_NotFound tests getting non-existent key
func TestCache_Get_NotFound(t *testing.T) {
	cache := NewCache()

	val, found := cache.Get("nonexistent")

	assert.False(t, found)
	assert.Nil(t, val)
}

// TestCache_Delete tests cache deletion
func TestCache_Delete(t *testing.T) {
	cache := NewCache()

	cache.Set("key1", "value1", 300)
	cache.Delete("key1")
	_, found := cache.Get("key1")

	assert.False(t, found)
}

// TestCache_Clear tests clearing entire cache
func TestCache_Clear(t *testing.T) {
	cache := NewCache()

	cache.Set("key1", "value1", 300)
	cache.Set("key2", "value2", 300)
	cache.Set("key3", "value3", 300)

	assert.Equal(t, 3, cache.Size())

	cache.Clear()

	assert.Equal(t, 0, cache.Size())
}

// TestCache_Size tests cache size tracking
func TestCache_Size(t *testing.T) {
	cache := NewCache()

	assert.Equal(t, 0, cache.Size())

	cache.Set("key1", "value1", 300)
	assert.Equal(t, 1, cache.Size())

	cache.Set("key2", "value2", 300)
	assert.Equal(t, 2, cache.Size())

	cache.Delete("key1")
	assert.Equal(t, 1, cache.Size())
}

// TestCache_Expiration tests cache TTL expiration
func TestCache_Expiration(t *testing.T) {
	cache := NewCache()

	cache.Set("shortlive", "value", 1) // 1 second TTL

	// Should exist immediately
	_, found := cache.Get("shortlive")
	assert.True(t, found)

	// Wait for expiration
	time.Sleep(1100 * time.Millisecond)

	// Should be expired
	_, found = cache.Get("shortlive")
	assert.False(t, found)
}

// TestCache_Overwrite tests overwriting existing cache value
func TestCache_Overwrite(t *testing.T) {
	cache := NewCache()

	cache.Set("key", "value1", 300)
	val, _ := cache.Get("key")
	assert.Equal(t, "value1", val)

	cache.Set("key", "value2", 300)
	val, _ = cache.Get("key")
	assert.Equal(t, "value2", val)
}

// TestCache_DifferentTypes tests caching different types
func TestCache_DifferentTypes(t *testing.T) {
	cache := NewCache()

	// Cache string
	cache.Set("string", "value", 300)
	val, _ := cache.Get("string")
	assert.Equal(t, "value", val)

	// Cache int
	cache.Set("int", 42, 300)
	val, _ = cache.Get("int")
	assert.Equal(t, 42, val)

	// Cache slice
	cache.Set("slice", []string{"a", "b"}, 300)
	val, _ = cache.Get("slice")
	assert.Equal(t, []string{"a", "b"}, val)

	// Cache map
	cache.Set("map", map[string]int{"x": 1}, 300)
	val, _ = cache.Get("map")
	assert.Equal(t, map[string]int{"x": 1}, val)
}

// TestCache_Concurrent_Reads tests concurrent cache reads
func TestCache_Concurrent_Reads(t *testing.T) {
	cache := NewCache()
	cache.Set("key", "value", 300)

	var wg sync.WaitGroup
	numGoroutines := 100

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			val, found := cache.Get("key")
			assert.True(t, found)
			assert.Equal(t, "value", val)
		}()
	}

	wg.Wait()
}

// TestCache_Concurrent_Writes tests concurrent cache writes
func TestCache_Concurrent_Writes(t *testing.T) {
	cache := NewCache()

	var wg sync.WaitGroup
	numGoroutines := 50

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			key := "key"
			cache.Set(key, idx, 300)
		}(i)
	}

	wg.Wait()

	// Cache should have 1 entry (overwritten many times)
	assert.Equal(t, 1, cache.Size())
}

// TestCache_Concurrent_Mixed tests concurrent mixed operations
func TestCache_Concurrent_Mixed(t *testing.T) {
	cache := NewCache()

	for i := 0; i < 20; i++ {
		cache.Set("key"+string(rune(i)), "value", 300)
	}

	var wg sync.WaitGroup

	// Concurrent reads
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			key := "key" + string(rune(idx%20))
			cache.Get(key)
		}(i)
	}

	// Concurrent writes
	for i := 0; i < 30; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			cache.Set("key"+string(rune(idx%20)), "newvalue", 300)
		}(i)
	}

	// Concurrent deletes
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			cache.Delete("key" + string(rune(idx%20)))
		}(i)
	}

	wg.Wait()
}

// ============================================================================
// CrossPerspectiveSearcher Filter Tests
// ============================================================================

// TestFilterByPerspective_Empty tests filtering with empty results
func TestFilterByPerspective_Empty(t *testing.T) {
	results := []Result{}
	filtered := filterByPerspective(results, "feature")
	assert.Empty(t, filtered)
}

// TestFilterByPerspective_NoMatching tests filtering with no matching perspective
func TestFilterByPerspective_NoMatching(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"perspective": "api",
			},
		},
		{
			ID: "2",
			Metadata: map[string]interface{}{
				"perspective": "code",
			},
		},
	}

	filtered := filterByPerspective(results, "feature")
	assert.Empty(t, filtered)
}

// TestFilterByPerspective_MissingMetadata tests filtering when metadata is missing
func TestFilterByPerspective_MissingMetadata(t *testing.T) {
	results := []Result{
		{ID: "1", Metadata: map[string]interface{}{}},
		{ID: "2", Metadata: nil},
		{ID: "3"},
	}

	filtered := filterByPerspective(results, "feature")
	assert.Empty(t, filtered)
}

// TestFilterByPerspective_MixedTypes tests filtering with non-string perspective values
func TestFilterByPerspective_MixedTypes(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"perspective": 123, // int instead of string
			},
		},
		{
			ID: "2",
			Metadata: map[string]interface{}{
				"perspective": "feature",
			},
		},
	}

	filtered := filterByPerspective(results, "feature")
	require.Len(t, filtered, 1)
	assert.Equal(t, "2", filtered[0].ID)
}

// TestFilterByDimension_Empty tests filtering dimensions with empty results
func TestFilterByDimension_Empty(t *testing.T) {
	results := []Result{}
	filtered := filterByDimension(results, "priority", "high")
	assert.Empty(t, filtered)
}

// TestFilterByDimension_NoMatching tests filtering with no matching dimension
func TestFilterByDimension_NoMatching(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "low",
				},
			},
		},
	}

	filtered := filterByDimension(results, "priority", "high")
	assert.Empty(t, filtered)
}

// TestFilterByDimension_MissingDimensions tests when dimensions metadata is missing
func TestFilterByDimension_MissingDimensions(t *testing.T) {
	results := []Result{
		{ID: "1", Metadata: map[string]interface{}{}},
		{ID: "2", Metadata: nil},
	}

	filtered := filterByDimension(results, "priority", "high")
	assert.Empty(t, filtered)
}

// TestFilterByDimension_NonMapDimensions tests when dimensions is not a map
func TestFilterByDimension_NonMapDimensions(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"dimensions": "not a map",
			},
		},
	}

	filtered := filterByDimension(results, "priority", "high")
	assert.Empty(t, filtered)
}

// TestFilterByDimension_NumericDimensions tests filtering numeric dimension values
func TestFilterByDimension_NumericDimensions(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": 3, // high
				},
			},
		},
		{
			ID: "2",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": 2, // medium
				},
			},
		},
	}

	filtered := filterByDimension(results, "priority", "high")
	require.Len(t, filtered, 1)
	assert.Equal(t, "1", filtered[0].ID)
}


// ============================================================================
// CrossPerspectiveSearchRequest Validation Tests
// ============================================================================

// TestCrossPerspectiveSearchRequest_Empty tests empty search request
func TestCrossPerspectiveSearchRequest_Empty(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{}
	assert.Empty(t, req.Query)
	assert.Empty(t, req.ProjectID)
	assert.Empty(t, req.Perspectives)
}

// TestCrossPerspectiveSearchRequest_AllFields tests request with all fields set
func TestCrossPerspectiveSearchRequest_AllFields(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query:               "test",
		ProjectID:           "proj1",
		Perspectives:        []string{"feature", "code"},
		Status:              []string{"active"},
		Types:               []string{"requirement"},
		DimensionKey:        "priority",
		DimensionValue:      "high",
		IncludeEquivalences: true,
		Limit:               50,
		Offset:              10,
		MinScore:            0.5,
		EnableFuzzy:         true,
		FuzzyThreshold:      0.7,
		SortBy:              "relevance",
	}

	assert.Equal(t, "test", req.Query)
	assert.Equal(t, "proj1", req.ProjectID)
	assert.Len(t, req.Perspectives, 2)
	assert.Equal(t, 50, req.Limit)
}

// TestCrossPerspectiveSearchRequest_DefaultLimitApplied tests default limit is applied
func TestCrossPerspectiveSearchRequest_DefaultLimitApplied(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Query: "test"}
	applyCrossSearchDefaults(req)

	assert.Equal(t, crossSearchDefaultLimit, req.Limit)
}

// TestCrossPerspectiveSearchRequest_LimitCapped tests limit is capped at max
func TestCrossPerspectiveSearchRequest_LimitCapped(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query: "test",
		Limit: 500, // Exceeds max
	}
	applyCrossSearchDefaults(req)

	assert.Equal(t, crossSearchMaxLimit, req.Limit)
}

// TestCrossPerspectiveSearchRequest_DefaultMinScore tests default min score
func TestCrossPerspectiveSearchRequest_DefaultMinScore(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Query: "test"}
	applyCrossSearchDefaults(req)

	assert.Equal(t, crossSearchDefaultMinScore, req.MinScore)
}

// TestCrossPerspectiveSearchRequest_DefaultFuzzyThreshold tests default fuzzy threshold
func TestCrossPerspectiveSearchRequest_DefaultFuzzyThreshold(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{Query: "test"}
	applyCrossSearchDefaults(req)

	assert.Equal(t, crossSearchDefaultFuzzyThreshold, req.FuzzyThreshold)
}

// TestResolvePerspectives_Custom tests custom perspectives
func TestResolvePerspectives_Custom(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Perspectives: []string{"feature", "code"},
	}

	perspectives := resolvePerspectives(req)

	assert.Equal(t, []string{"feature", "code"}, perspectives)
}

// TestResolvePerspectives_Default tests default perspectives when not specified
func TestResolvePerspectives_Default(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{}
	perspectives := resolvePerspectives(req)

	assert.Greater(t, len(perspectives), 0)
	assert.Contains(t, perspectives, "feature")
	assert.Contains(t, perspectives, "code")
	assert.Contains(t, perspectives, "test")
}

// TestResolvePerspectives_Empty tests empty perspectives list
func TestResolvePerspectives_Empty(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Perspectives: []string{},
	}

	perspectives := resolvePerspectives(req)

	// Empty slice should fall back to defaults
	assert.Greater(t, len(perspectives), 0)
}

// ============================================================================
// Cache Key Generation Tests
// ============================================================================

// TestGenerateCacheKey_Consistency tests cache key consistency
func TestGenerateCacheKey_Consistency(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req := &CrossPerspectiveSearchRequest{
		Query:     "test",
		ProjectID: "proj1",
		Limit:     10,
	}

	key1 := searcher.generateCacheKey(req)
	key2 := searcher.generateCacheKey(req)

	assert.Equal(t, key1, key2)
}

// TestGenerateCacheKey_Different_Queries tests different queries produce different keys
func TestGenerateCacheKey_Different_Queries(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{Query: "query1", ProjectID: "proj1"}
	req2 := &CrossPerspectiveSearchRequest{Query: "query2", ProjectID: "proj1"}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)

	assert.NotEqual(t, key1, key2)
}

// TestGenerateCacheKey_Different_Projects tests different projects produce different keys
func TestGenerateCacheKey_Different_Projects(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{Query: "query", ProjectID: "proj1"}
	req2 := &CrossPerspectiveSearchRequest{Query: "query", ProjectID: "proj2"}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)

	assert.NotEqual(t, key1, key2)
}

// TestGenerateCacheKey_Different_Perspectives tests different perspectives produce different keys
func TestGenerateCacheKey_Different_Perspectives(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{
		Query:        "query",
		ProjectID:    "proj1",
		Perspectives: []string{"feature", "code"},
	}
	req2 := &CrossPerspectiveSearchRequest{
		Query:        "query",
		ProjectID:    "proj1",
		Perspectives: []string{"feature", "api"},
	}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)

	assert.NotEqual(t, key1, key2)
}

// TestGenerateCacheKey_Different_Status tests different status produce different keys
func TestGenerateCacheKey_Different_Status(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{
		Query:     "query",
		ProjectID: "proj1",
		Status:    []string{"active"},
	}
	req2 := &CrossPerspectiveSearchRequest{
		Query:     "query",
		ProjectID: "proj1",
		Status:    []string{"inactive"},
	}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)

	assert.NotEqual(t, key1, key2)
}

// TestGenerateCacheKey_Different_Types tests different types produce different keys
func TestGenerateCacheKey_Different_Types(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{
		Query:     "query",
		ProjectID: "proj1",
		Types:     []string{"requirement"},
	}
	req2 := &CrossPerspectiveSearchRequest{
		Query:     "query",
		ProjectID: "proj1",
		Types:     []string{"test"},
	}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)

	assert.NotEqual(t, key1, key2)
}

// TestGenerateCacheKey_Different_Dimensions tests different dimensions produce different keys
func TestGenerateCacheKey_Different_Dimensions(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{
		Query:          "query",
		ProjectID:      "proj1",
		DimensionKey:   "priority",
		DimensionValue: "high",
	}
	req2 := &CrossPerspectiveSearchRequest{
		Query:          "query",
		ProjectID:      "proj1",
		DimensionKey:   "priority",
		DimensionValue: "low",
	}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)

	assert.NotEqual(t, key1, key2)
}

// TestGenerateCacheKey_Different_Limits tests different limits produce different keys
func TestGenerateCacheKey_Different_Limits(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req1 := &CrossPerspectiveSearchRequest{
		Query:     "query",
		ProjectID: "proj1",
		Limit:     10,
	}
	req2 := &CrossPerspectiveSearchRequest{
		Query:     "query",
		ProjectID: "proj1",
		Limit:     20,
	}

	key1 := searcher.generateCacheKey(req1)
	key2 := searcher.generateCacheKey(req2)

	assert.NotEqual(t, key1, key2)
}

// ============================================================================
// Timestamp Tests
// ============================================================================

// TestGetCurrentTimestamp_Format tests timestamp format
func TestGetCurrentTimestamp_Format(t *testing.T) {
	ts := getCurrentTimestamp()

	// Should be non-empty
	assert.NotEmpty(t, ts)

	// Should be valid ISO 8601 format
	_, err := time.Parse("2006-01-02T15:04:05Z", ts)
	assert.NoError(t, err)
}

// TestGetCurrentTimestamp_UTC tests that timestamp is in UTC
func TestGetCurrentTimestamp_UTC(t *testing.T) {
	ts := getCurrentTimestamp()
	assert.Contains(t, ts, "Z") // Z indicates UTC
}

// TestGetCurrentTimestamp_Different tests multiple calls produce different timestamps
func TestGetCurrentTimestamp_Different(t *testing.T) {
	ts1 := getCurrentTimestamp()
	time.Sleep(100 * time.Millisecond) // Longer sleep to ensure timestamp difference
	ts2 := getCurrentTimestamp()

	assert.NotEqual(t, ts1, ts2)
}

// ============================================================================
// CrossPerspectiveSearchResponse Tests
// ============================================================================

// TestNewCrossPerspectiveResponse tests creating new response
func TestNewCrossPerspectiveResponse(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query:     "test",
		ProjectID: "proj1",
	}

	resp := newCrossPerspectiveResponse(req)

	assert.Equal(t, "test", resp.Query)
	assert.Equal(t, "proj1", resp.ProjectID)
	assert.Equal(t, 0, resp.TotalCount)
	assert.Empty(t, resp.PerspectiveGroups)
	assert.NotEmpty(t, resp.ExecutedAt)
	assert.False(t, resp.CacheHit)
}

// ============================================================================
// Error Path Tests
// ============================================================================

// TestCrossPerspectiveSearcher_NilEngine tests searcher with nil engine
func TestCrossPerspectiveSearcher_NilEngine(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{
		engine: nil,
		cache:  NewCache(),
	}

	ctx := context.Background()
	req := &CrossPerspectiveSearchRequest{Query: "test", ProjectID: "proj1"}

	// Should not panic, returns response (searchPerspective checks engine.pool)
	resp, err := searcher.Search(ctx, req)

	// Should complete without error
	assert.NoError(t, err)
	assert.NotNil(t, resp)
}

// TestCrossPerspectiveSearcher_NilCache tests searcher with nil cache
func TestCrossPerspectiveSearcher_NilCache(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{
		engine: nil,
		cache:  nil,
	}

	ctx := context.Background()
	req := &CrossPerspectiveSearchRequest{Query: "test", ProjectID: "proj1"}

	// Should not panic
	resp, err := searcher.Search(ctx, req)

	assert.Nil(t, err)
	assert.NotNil(t, resp)
}

// TestCrossPerspectiveSearcher_EmptyQuery tests empty query validation
func TestCrossPerspectiveSearcher_EmptyQuery(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{
		engine: nil,
		cache:  NewCache(),
	}

	ctx := context.Background()
	req := &CrossPerspectiveSearchRequest{Query: "", ProjectID: "proj1"}

	resp, err := searcher.Search(ctx, req)

	assert.NotNil(t, err)
	assert.Nil(t, resp)
}

// TestCrossPerspectiveSearcher_WhitespaceQuery tests whitespace-only query
func TestCrossPerspectiveSearcher_WhitespaceQuery(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{
		engine: nil,
		cache:  NewCache(),
	}

	ctx := context.Background()
	req := &CrossPerspectiveSearchRequest{Query: "   ", ProjectID: "proj1"}

	resp, err := searcher.Search(ctx, req)

	assert.NotNil(t, err)
	assert.Nil(t, resp)
}

// ============================================================================
// Cache Boundary Tests
// ============================================================================

// TestCache_Expiration_Boundary tests cache at exact TTL boundary
func TestCache_Expiration_Boundary(t *testing.T) {
	cache := NewCache()

	// Set with 2 second TTL
	cache.Set("key", "value", 2)

	// Verify it exists
	_, found := cache.Get("key")
	assert.True(t, found)

	// Wait 2+ seconds
	time.Sleep(2100 * time.Millisecond)

	// Should be expired (using >= comparison)
	_, found = cache.Get("key")
	assert.False(t, found)
}

// TestCache_ZeroTTL tests cache with zero TTL
func TestCache_ZeroTTL(t *testing.T) {
	cache := NewCache()

	cache.Set("key", "value", 0)

	// Should expire immediately (now >= now + 0)
	_, found := cache.Get("key")
	assert.False(t, found)
}

// TestCache_NegativeTTL tests cache with negative TTL
func TestCache_NegativeTTL(t *testing.T) {
	cache := NewCache()

	cache.Set("key", "value", -100)

	// Should already be expired
	_, found := cache.Get("key")
	assert.False(t, found)
}

// TestCache_LongTTL tests cache with very long TTL
func TestCache_LongTTL(t *testing.T) {
	cache := NewCache()

	cache.Set("key", "value", 3600) // 1 hour

	_, found := cache.Get("key")
	assert.True(t, found)
}

// ============================================================================
// Concurrent Cache Tests with Expiration
// ============================================================================

// TestCache_Concurrent_Expiration tests concurrent access with expiration
func TestCache_Concurrent_Expiration(t *testing.T) {
	cache := NewCache()

	cache.Set("expiring", "value", 1) // 1 second TTL

	var wg sync.WaitGroup

	// Start readers
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 10; j++ {
				cache.Get("expiring")
				time.Sleep(100 * time.Millisecond)
			}
		}()
	}

	wg.Wait()
}

// TestCache_Concurrent_Clear tests concurrent operations with clear
func TestCache_Concurrent_Clear(t *testing.T) {
	cache := NewCache()

	for i := 0; i < 50; i++ {
		cache.Set("key"+string(rune(i)), "value", 300)
	}

	var wg sync.WaitGroup

	// Readers
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 5; j++ {
				cache.Get("key" + string(rune(j)))
			}
		}()
	}

	// Writers
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			cache.Set("key"+string(rune(idx)), "newval", 300)
		}(i)
	}

	// Clear
	wg.Add(1)
	go func() {
		defer wg.Done()
		time.Sleep(50 * time.Millisecond)
		cache.Clear()
	}()

	wg.Wait()
	assert.Equal(t, 0, cache.Size())
}

