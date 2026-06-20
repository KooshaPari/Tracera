//go:build !integration && !e2e

package search

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// QueryBuilder Edge Cases and Error Paths
// ============================================================================

// TestQueryBuilder_VeryLargeLimit tests QueryBuilder with very large limit values
func TestQueryBuilder_VeryLargeLimit(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Limit(999999999)

	query, args := qb.Build()
	assert.Contains(t, query, "LIMIT $1")
	assert.Equal(t, 999999999, args[0])
}

// TestQueryBuilder_VeryLargeOffset tests QueryBuilder with very large offset values
func TestQueryBuilder_VeryLargeOffset(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Limit(10).
		Offset(999999999)

	query, args := qb.Build()
	assert.Contains(t, query, "OFFSET $2")
	require.Len(t, args, 2)
	assert.Equal(t, 999999999, args[1])
}

// TestQueryBuilder_ZeroLimit tests QueryBuilder with zero limit (should not add LIMIT)
func TestQueryBuilder_ZeroLimit(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Limit(0)

	query, _ := qb.Build()
	assert.NotContains(t, query, "LIMIT")
}

// TestQueryBuilder_NegativeLimit tests QueryBuilder with negative limit
func TestQueryBuilder_NegativeLimit(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Limit(-5)

	query, _ := qb.Build()
	assert.NotContains(t, query, "LIMIT")
}

// TestQueryBuilder_NegativeOffset tests QueryBuilder with negative offset
func TestQueryBuilder_NegativeOffset(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Offset(-5)

	query, _ := qb.Build()
	// Negative offset is added (offsetVal > 0 condition in Build)
	// but -5 is not > 0, so it won't add OFFSET unless Limit is also set
	assert.NotContains(t, query, "OFFSET")
}

// TestQueryBuilder_EmptyFromTable tests QueryBuilder with empty FROM clause
func TestQueryBuilder_EmptyFromTable(t *testing.T) {
	qb := NewQueryBuilder().
		Select("*").
		From("")

	query, _ := qb.Build()
	assert.Equal(t, "SELECT *", query)
}

// TestQueryBuilder_ComplexWhereConditions tests QueryBuilder with complex WHERE
func TestQueryBuilder_ComplexWhereConditions(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Where("(a = ? OR b = ?) AND (c = ? OR d IS NULL)", 1, 2, 3)

	query, args := qb.Build()
	assert.Contains(t, query, "(a = $1 OR b = $2) AND (c = $3 OR d IS NULL)")
	require.Len(t, args, 3)
}

// TestQueryBuilder_Where_SamePlaceholderCount tests placeholder replacement accuracy
func TestQueryBuilder_Where_SamePlaceholderCount(t *testing.T) {
	qb := NewQueryBuilder().
		Where("x = ? AND y = ? AND z = ?", "a", "b", "c")

	query, args := qb.Build()
	assert.Contains(t, query, "x = $1 AND y = $2 AND z = $3")
	require.Len(t, args, 3)
	assert.Equal(t, "a", args[0])
	assert.Equal(t, "b", args[1])
	assert.Equal(t, "c", args[2])
}

// TestQueryBuilder_Select_MultipleColumnsWithSpaces tests SELECT with various column formats
func TestQueryBuilder_Select_MultipleColumnsWithSpaces(t *testing.T) {
	qb := NewQueryBuilder().
		Select("id", "title", "description").
		From("items")

	query, _ := qb.Build()
	assert.Contains(t, query, "SELECT id, title, description")
}

// TestQueryBuilder_OrderBy_MultipleFields tests multiple ORDER BY with mixed directions
func TestQueryBuilder_OrderBy_MultipleFields(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		OrderBy("priority", "DESC").
		OrderBy("title", "ASC").
		OrderBy("created_at", "desc").
		OrderBy("status", "asc")

	query, _ := qb.Build()
	assert.Contains(t, query, "ORDER BY priority DESC, title ASC, created_at DESC, status ASC")
}

// TestQueryBuilder_SelectEmpty tests with empty select call
func TestQueryBuilder_SelectEmpty(t *testing.T) {
	qb := NewQueryBuilder().Select().From("items")
	query, _ := qb.Build()
	assert.Contains(t, query, "SELECT *")
}

// TestQueryBuilder_RealWorldEcommerce tests realistic e-commerce query
func TestQueryBuilder_RealWorldEcommerce(t *testing.T) {
	qb := NewQueryBuilder().
		Select("id", "product_name", "price", "inventory").
		From("products").
		Where("category = ?", "electronics").
		Where("price > ?", 100).
		Where("inventory > ?", 0).
		Where("deleted_at IS NULL").
		OrderBy("price", "ASC").
		OrderBy("inventory", "DESC").
		Limit(50).
		Offset(100)

	query, args := qb.Build()
	assert.Contains(t, query, "SELECT id, product_name, price, inventory")
	assert.Contains(t, query, "FROM products")
	assert.Contains(t, query, "WHERE")
	assert.Contains(t, query, "category = $1")
	assert.Contains(t, query, "price > $2")
	assert.Contains(t, query, "inventory > $3")
	assert.Contains(t, query, "ORDER BY price ASC, inventory DESC")
	assert.Contains(t, query, "LIMIT $4")
	assert.Contains(t, query, "OFFSET $5")
	require.Len(t, args, 5)
}

// TestQueryBuilder_StringWithSQLInjection tests that placeholders prevent injection
func TestQueryBuilder_StringWithSQLInjection(t *testing.T) {
	qb := NewQueryBuilder().
		From("items").
		Where("title = ?", "'; DROP TABLE items; --")

	query, args := qb.Build()
	// The injection string should be in args, not in query
	assert.NotContains(t, query, "DROP TABLE")
	require.Len(t, args, 1)
	assert.Equal(t, "'; DROP TABLE items; --", args[0])
}

// ============================================================================
// Cache Edge Cases
// ============================================================================

// TestCache_VeryLongKey tests cache with extremely long key
func TestCache_VeryLongKey(t *testing.T) {
	cache := NewCache()
	longKey := strings.Repeat("k", 10000)

	cache.Set(longKey, "value", 300)
	val, found := cache.Get(longKey)

	assert.True(t, found)
	assert.Equal(t, "value", val)
}

// TestCache_VeryLongValue tests cache with extremely long value
func TestCache_VeryLongValue(t *testing.T) {
	cache := NewCache()
	longValue := strings.Repeat("v", 100000)

	cache.Set("key", longValue, 300)
	val, found := cache.Get("key")

	assert.True(t, found)
	assert.Equal(t, longValue, val)
}

// TestCache_SpecialCharactersKey tests cache with special characters in key
func TestCache_SpecialCharactersKey(t *testing.T) {
	cache := NewCache()
	specialKey := "key:with:colons:and_underscores-dashes"

	cache.Set(specialKey, "value", 300)
	val, found := cache.Get(specialKey)

	assert.True(t, found)
	assert.Equal(t, "value", val)
}

// TestCache_UnicodeKey tests cache with unicode characters
func TestCache_UnicodeKey(t *testing.T) {
	cache := NewCache()
	unicodeKey := "key_with_émojis_🚀_and_中文"

	cache.Set(unicodeKey, "value", 300)
	val, found := cache.Get(unicodeKey)

	assert.True(t, found)
	assert.Equal(t, "value", val)
}

// TestCache_NilValue tests cache with nil value
func TestCache_NilValue(t *testing.T) {
	cache := NewCache()

	cache.Set("key", nil, 300)
	val, found := cache.Get("key")

	assert.True(t, found)
	assert.Nil(t, val)
}

// TestCache_ZeroValue tests cache with zero value
func TestCache_ZeroValue(t *testing.T) {
	cache := NewCache()

	cache.Set("key", 0, 300)
	val, found := cache.Get("key")

	assert.True(t, found)
	assert.Equal(t, 0, val)
}

// TestCache_EmptyStringValue tests cache with empty string
func TestCache_EmptyStringValue(t *testing.T) {
	cache := NewCache()

	cache.Set("key", "", 300)
	val, found := cache.Get("key")

	assert.True(t, found)
	assert.Empty(t, val)
}

// TestCache_ComplexNestedStructure tests cache with complex nested data
func TestCache_ComplexNestedStructure(t *testing.T) {
	cache := NewCache()

	complexValue := map[string]interface{}{
		"level1": map[string]interface{}{
			"level2": map[string]interface{}{
				"level3": []interface{}{1, 2, 3, "four"},
			},
		},
	}

	cache.Set("complex", complexValue, 300)
	val, found := cache.Get("complex")

	assert.True(t, found)
	assert.Equal(t, complexValue, val)
}

// TestCache_DeletionNonexistent tests deleting non-existent key (should not panic)
func TestCache_DeletionNonexistent(t *testing.T) {
	cache := NewCache()

	// Should not panic
	cache.Delete("nonexistent")
	cache.Delete("also_nonexistent")
}

// TestCache_GetAfterExpiration_MultipleReads tests multiple reads after expiration
func TestCache_GetAfterExpiration_MultipleReads(t *testing.T) {
	cache := NewCache()

	cache.Set("key", "value", 1)
	time.Sleep(1200 * time.Millisecond) // Longer sleep to ensure expiration

	for i := 0; i < 3; i++ {
		_, found := cache.Get("key")
		assert.False(t, found, "cache should be expired on read %d", i)
	}
}

// TestCache_ClearEmpty tests clearing an empty cache
func TestCache_ClearEmpty(t *testing.T) {
	cache := NewCache()
	cache.Clear()
	assert.Equal(t, 0, cache.Size())
}

// ============================================================================
// Filter Function Edge Cases
// ============================================================================

// TestFilterByPerspective_NilResults tests filtering nil results slice
func TestFilterByPerspective_NilResults(t *testing.T) {
	var results []Result
	filtered := filterByPerspective(results, "feature")
	assert.Empty(t, filtered)
}

// TestFilterByPerspective_AllMatch tests filtering when all match
func TestFilterByPerspective_AllMatch(t *testing.T) {
	results := []Result{
		{ID: "1", Metadata: map[string]interface{}{"perspective": "feature"}},
		{ID: "2", Metadata: map[string]interface{}{"perspective": "feature"}},
		{ID: "3", Metadata: map[string]interface{}{"perspective": "feature"}},
	}

	filtered := filterByPerspective(results, "feature")
	assert.Len(t, filtered, 3)
}

// TestFilterByPerspective_CaseSensitive tests that perspective filtering is case-sensitive
func TestFilterByPerspective_CaseSensitive(t *testing.T) {
	results := []Result{
		{ID: "1", Metadata: map[string]interface{}{"perspective": "Feature"}},
	}

	filtered := filterByPerspective(results, "feature")
	assert.Empty(t, filtered) // Should not match due to case difference
}

// TestFilterByDimension_AllMatch tests dimension filtering when all match
func TestFilterByDimension_AllMatch(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{"priority": "high"},
			},
		},
		{
			ID: "2",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{"priority": "high"},
			},
		},
	}

	filtered := filterByDimension(results, "priority", "high")
	assert.Len(t, filtered, 2)
}

// TestFilterByDimension_CaseSensitive tests that dimension filtering is case-sensitive
func TestFilterByDimension_CaseSensitive(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{"priority": "High"},
			},
		},
	}

	filtered := filterByDimension(results, "priority", "high")
	assert.Empty(t, filtered) // Case mismatch
}

// TestFilterByDimension_MultipleFilters tests dimension filtering with multiple values
func TestFilterByDimension_MultipleFilters(t *testing.T) {
	results := []Result{
		{
			ID: "1",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "high",
					"team":     "frontend",
				},
			},
		},
		{
			ID: "2",
			Metadata: map[string]interface{}{
				"dimensions": map[string]interface{}{
					"priority": "low",
					"team":     "frontend",
				},
			},
		},
	}

	filtered := filterByDimension(results, "priority", "high")
	assert.Len(t, filtered, 1)
	assert.Equal(t, "1", filtered[0].ID)
}

// ============================================================================
// Request Validation Edge Cases
// ============================================================================

// TestCrossPerspectiveSearchRequest_VeryLongQuery tests request with very long query
func TestCrossPerspectiveSearchRequest_VeryLongQuery(t *testing.T) {
	longQuery := strings.Repeat("word ", 1000)

	req := &CrossPerspectiveSearchRequest{
		Query: longQuery,
	}

	assert.Equal(t, longQuery, req.Query)
}

// TestCrossPerspectiveSearchRequest_ManyPerspectives tests request with many perspectives
func TestCrossPerspectiveSearchRequest_ManyPerspectives(t *testing.T) {
	perspectives := make([]string, 100)
	for i := 0; i < 100; i++ {
		perspectives[i] = "perspective_" + string(rune(i))
	}

	req := &CrossPerspectiveSearchRequest{
		Query:        "test",
		Perspectives: perspectives,
	}

	assert.Len(t, req.Perspectives, 100)
}

// TestCrossPerspectiveSearchRequest_ManyStatuses tests request with many statuses
func TestCrossPerspectiveSearchRequest_ManyStatuses(t *testing.T) {
	statuses := []string{"active", "inactive", "pending", "done", "archived", "review"}

	req := &CrossPerspectiveSearchRequest{
		Query:  "test",
		Status: statuses,
	}

	assert.Len(t, req.Status, 6)
}

// TestCrossPerspectiveSearchRequest_ZeroLimit tests with zero limit
func TestCrossPerspectiveSearchRequest_ZeroLimit(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query: "test",
		Limit: 0,
	}

	applyCrossSearchDefaults(req)

	// Should be set to default
	assert.Equal(t, crossSearchDefaultLimit, req.Limit)
}

// TestCrossPerspectiveSearchRequest_PreservesNonZeroLimit tests that non-zero limit is preserved
func TestCrossPerspectiveSearchRequest_PreservesNonZeroLimit(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query: "test",
		Limit: 15,
	}

	applyCrossSearchDefaults(req)

	assert.Equal(t, 15, req.Limit)
}

// TestCrossPerspectiveSearchRequest_PreservesMinScore tests that non-zero min score is preserved
func TestCrossPerspectiveSearchRequest_PreservesMinScore(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query:    "test",
		MinScore: 0.5,
	}

	applyCrossSearchDefaults(req)

	assert.InEpsilon(t, 0.5, req.MinScore, 1e-9)
}

// TestCrossPerspectiveSearchRequest_PreservesFuzzyThreshold tests that non-zero threshold is preserved
func TestCrossPerspectiveSearchRequest_PreservesFuzzyThreshold(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query:          "test",
		FuzzyThreshold: 0.8,
	}

	applyCrossSearchDefaults(req)

	assert.InEpsilon(t, 0.8, req.FuzzyThreshold, 1e-9)
}

// TestResolvePerspectives_PreservesOrder tests that custom perspectives maintain order
func TestResolvePerspectives_PreservesOrder(t *testing.T) {
	perspectives := []string{"z", "a", "m"}
	req := &CrossPerspectiveSearchRequest{
		Perspectives: perspectives,
	}

	resolved := resolvePerspectives(req)

	assert.Equal(t, perspectives, resolved)
}

// ============================================================================
// Searcher Initialization Tests
// ============================================================================

// TestNewCrossPerspectiveSearcher_WithBoth tests creating searcher with engine and cache
func TestNewCrossPerspectiveSearcher_WithBoth(t *testing.T) {
	engine := &Engine{}
	cache := NewCache()

	searcher := NewCrossPerspectiveSearcher(engine, cache)

	assert.NotNil(t, searcher)
	assert.Equal(t, engine, searcher.engine)
	assert.Equal(t, cache, searcher.cache)
}

// TestNewCrossPerspectiveSearcher_WithoutEngine tests creating searcher without engine
func TestNewCrossPerspectiveSearcher_WithoutEngine(t *testing.T) {
	cache := NewCache()

	searcher := NewCrossPerspectiveSearcher(nil, cache)

	assert.NotNil(t, searcher)
	assert.Nil(t, searcher.engine)
	assert.Equal(t, cache, searcher.cache)
}

// TestNewCrossPerspectiveSearcher_WithoutCache tests creating searcher without cache
func TestNewCrossPerspectiveSearcher_WithoutCache(t *testing.T) {
	engine := &Engine{}

	searcher := NewCrossPerspectiveSearcher(engine, nil)

	assert.NotNil(t, searcher)
	assert.Equal(t, engine, searcher.engine)
	assert.Nil(t, searcher.cache)
}

// ============================================================================
// Cache Key Generation with Special Cases
// ============================================================================

// TestGenerateCacheKey_WithEmptyPerspectives tests cache key with empty perspectives
func TestGenerateCacheKey_WithEmptyPerspectives(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req := &CrossPerspectiveSearchRequest{
		Query:        "test",
		ProjectID:    "proj1",
		Perspectives: []string{},
	}

	key := searcher.generateCacheKey(req)
	assert.NotEmpty(t, key)
	assert.Contains(t, key, "cross_search:")
}

// TestGenerateCacheKey_WithSpecialCharacters tests cache key with special characters
func TestGenerateCacheKey_WithSpecialCharacters(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req := &CrossPerspectiveSearchRequest{
		Query:     "test: query with special chars & symbols",
		ProjectID: "proj-1:special",
	}

	key := searcher.generateCacheKey(req)
	assert.NotEmpty(t, key)
}

// TestGenerateCacheKey_ConsistentFormatting tests cache key format consistency
func TestGenerateCacheKey_ConsistentFormatting(t *testing.T) {
	searcher := &CrossPerspectiveSearcher{}

	req := &CrossPerspectiveSearchRequest{
		Query:        "test",
		ProjectID:    "proj1",
		Limit:        10,
		Perspectives: []string{"a", "b"},
		Status:       []string{"x", "y"},
		Types:        []string{"t1", "t2"},
	}

	key := searcher.generateCacheKey(req)

	// Should contain all main components
	assert.Contains(t, key, "cross_search:")
	assert.Contains(t, key, "proj1")
	assert.Contains(t, key, "test")
	assert.Contains(t, key, "a,b") // perspectives joined with comma
}

// ============================================================================
// Context Handling Tests
// ============================================================================

// TestSearch_ContextCancellation tests search with cancelled context
func TestSearch_ContextCancellation(t *testing.T) {
	searcher := NewCrossPerspectiveSearcher(nil, NewCache())

	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	req := &CrossPerspectiveSearchRequest{Query: "test", ProjectID: "proj1"}

	resp, err := searcher.Search(ctx, req)

	// Should handle cancelled context gracefully
	require.NoError(t, err)
	assert.NotNil(t, resp)
}

// TestSearch_ContextWithTimeout tests search with timeout context
func TestSearch_ContextWithTimeout(t *testing.T) {
	searcher := NewCrossPerspectiveSearcher(nil, NewCache())

	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()

	req := &CrossPerspectiveSearchRequest{Query: "test", ProjectID: "proj1"}

	resp, err := searcher.Search(ctx, req)

	// Should handle timeout gracefully
	require.NoError(t, err)
	assert.NotNil(t, resp)
}

// ============================================================================
// Response Metadata Tests
// ============================================================================

// TestNewCrossPerspectiveResponse_AllFields tests response field initialization
func TestNewCrossPerspectiveResponse_AllFields(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query:     "test",
		ProjectID: "proj1",
	}

	resp := newCrossPerspectiveResponse(req)

	assert.Equal(t, "test", resp.Query)
	assert.Equal(t, "proj1", resp.ProjectID)
	assert.Equal(t, 0, resp.TotalCount)
	assert.Equal(t, 0, resp.PerspectivesSearched)
	assert.Empty(t, resp.PerspectiveGroups)
	assert.False(t, resp.CacheHit)
	assert.NotEmpty(t, resp.ExecutedAt)
	assert.Empty(t, resp.Duration)
}

// ============================================================================
// Constants Validation Tests
// ============================================================================

// TestConstants_DefaultValues tests that constants have expected values
func TestConstants_DefaultValues(t *testing.T) {
	assert.Equal(t, 10, crossSearchDefaultLimit)
	assert.Equal(t, 100, crossSearchMaxLimit)
	assert.InEpsilon(t, 0.1, crossSearchDefaultMinScore, 1e-9)
	assert.InEpsilon(t, 0.3, crossSearchDefaultFuzzyThreshold, 1e-9)
	assert.Equal(t, 10, crossSearchSuggestionDefaultLimit)
	assert.Equal(t, 50, crossSearchSuggestionMaxLimit)
	assert.Equal(t, 300, cacheTTL)
}

// ============================================================================
// Boundary Condition Tests
// ============================================================================

// TestLimitBoundary_AtMax tests request at exact max limit
func TestLimitBoundary_AtMax(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query: "test",
		Limit: crossSearchMaxLimit,
	}

	applyCrossSearchDefaults(req)

	assert.Equal(t, crossSearchMaxLimit, req.Limit)
}

// TestLimitBoundary_JustBelowMax tests request just below max limit
func TestLimitBoundary_JustBelowMax(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query: "test",
		Limit: crossSearchMaxLimit - 1,
	}

	applyCrossSearchDefaults(req)

	assert.Equal(t, crossSearchMaxLimit-1, req.Limit)
}

// TestLimitBoundary_JustAboveMax tests request just above max limit
func TestLimitBoundary_JustAboveMax(t *testing.T) {
	req := &CrossPerspectiveSearchRequest{
		Query: "test",
		Limit: crossSearchMaxLimit + 1,
	}

	applyCrossSearchDefaults(req)

	assert.Equal(t, crossSearchMaxLimit, req.Limit)
}

// TestMinScoreBoundary tests various min score values
func TestMinScoreBoundary(t *testing.T) {
	tests := []struct {
		name     string
		input    float64
		expected float64
	}{
		{"zero_uses_default", 0, crossSearchDefaultMinScore},
		{"small_positive", 0.05, 0.05},
		{"half", 0.5, 0.5},
		{"high", 0.95, 0.95},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := &CrossPerspectiveSearchRequest{
				Query:    "test",
				MinScore: tt.input,
			}

			applyCrossSearchDefaults(req)

			assert.InEpsilon(t, tt.expected, req.MinScore, 1e-9)
		})
	}
}
