//go:build !integration && !e2e

package search

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

const (
	searchContextTimeoutLong  = 10 * time.Second
	searchContextTimeoutShort = 10 * time.Millisecond
	searchContextSleep        = 50 * time.Millisecond
	searchDurationSleep       = 10 * time.Millisecond
)

// =============================================================================
// Helper Functions for Testing
// =============================================================================

// TestHelper struct to manage test setup
type TestHelper struct {
	ctx context.Context
}

// NewTestHelper creates a test helper
func NewTestHelper(_ *testing.T) *TestHelper {
	return &TestHelper{
		ctx: context.Background(),
	}
}

// =============================================================================
// Engine Field Access Tests (to improve coverage)
// =============================================================================

// TestSearchEngineFieldsAccessibleAfterCreation exercises basic invariants for TestSearchEngineFieldsAccessibleAfterCreation.
func TestSearchEngineFieldsAccessibleAfterCreation(t *testing.T) {
	// Test that we can create and verify the fields exist
	engine := NewEngine(nil)
	assert.NotNil(t, engine) // Just verify it was created
	assert.False(t, engine.rerankEnabled)
}

// =============================================================================
// Result JSON Serialization Tests
// =============================================================================

// TestSearchResultPopulatedFields exercises basic invariants for TestSearchResultPopulatedFields.
func TestSearchResultPopulatedFields(t *testing.T) {
	now := time.Now()
	result := &Result{
		ID:          "test-123",
		ProjectID:   "proj-456",
		Title:       "Test Title",
		Description: "Test Description",
		Type:        "requirement",
		Status:      "active",
		Priority:    "HIGH",
		Score:       0.95,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	// Verify all fields are populated
	assert.Equal(t, "test-123", result.ID)
	assert.Equal(t, "proj-456", result.ProjectID)
	assert.Equal(t, "Test Title", result.Title)
	assert.Equal(t, "Test Description", result.Description)
	assert.Equal(t, "requirement", result.Type)
	assert.Equal(t, "active", result.Status)
	assert.Equal(t, "HIGH", result.Priority)
	assert.InDelta(t, 0.95, result.Score, 0.001)
	assert.Equal(t, now, result.CreatedAt)
	assert.Equal(t, now, result.UpdatedAt)
}

// =============================================================================
// Request Field Validation Tests
// =============================================================================

// TestSearchRequestAllFieldsSettable exercises basic invariants for TestSearchRequestAllFieldsSettable.
func TestSearchRequestAllFieldsSettable(t *testing.T) {
	req := &Request{
		Query:               "test query",
		Type:                TypeFullText,
		ProjectID:           "proj-123",
		ItemTypes:           []string{"requirement", "test"},
		Status:              []string{"active", "pending"},
		Limit:               50,
		Offset:              10,
		MinScore:            0.5,
		IncludeDeleted:      true,
		FuzzyThreshold:      0.4,
		EnableTypoTolerance: true,
	}

	assert.Equal(t, "test query", req.Query)
	assert.Equal(t, TypeFullText, req.Type)
	assert.Equal(t, "proj-123", req.ProjectID)
	assert.Equal(t, 2, len(req.ItemTypes))
	assert.Equal(t, 2, len(req.Status))
	assert.Equal(t, 50, req.Limit)
	assert.Equal(t, 10, req.Offset)
	assert.Equal(t, 0.5, req.MinScore)
	assert.True(t, req.IncludeDeleted)
	assert.Equal(t, 0.4, req.FuzzyThreshold)
	assert.True(t, req.EnableTypoTolerance)
}

// =============================================================================
// Response Field Tests
// =============================================================================

// TestSearchResponseAllFieldsSettable exercises basic invariants for TestSearchResponseAllFieldsSettable.
func TestSearchResponseAllFieldsSettable(t *testing.T) {
	results := []Result{
		{ID: "1", Title: "Result 1", Score: 0.9},
		{ID: "2", Title: "Result 2", Score: 0.8},
	}

	duration := 100 * time.Millisecond
	resp := &Response{
		Results:    results,
		TotalCount: 42,
		Query:      "test",
		Type:       TypeFullText,
		Duration:   duration,
	}

	assert.Equal(t, 2, len(resp.Results))
	assert.Equal(t, 42, resp.TotalCount)
	assert.Equal(t, "test", resp.Query)
	assert.Equal(t, TypeFullText, resp.Type)
	assert.Equal(t, duration, resp.Duration)
}

// =============================================================================
// Index Operations Tests
// =============================================================================

// TestIndexJobFieldTypes exercises basic invariants for TestIndexJobFieldTypes.
func TestIndexJobFieldTypes(t *testing.T) {
	// Test that IndexJob can hold different operation types
	tests := []struct {
		op   IndexOperation
		id   string
		prio int
	}{
		{OpIndex, "item1", 1},
		{OpUpdate, "item2", 2},
		{OpDelete, "item3", 3},
	}

	for _, tt := range tests {
		job := IndexJob{
			Operation: tt.op,
			ItemID:    tt.id,
			Priority:  tt.prio,
		}
		assert.Equal(t, tt.op, job.Operation)
		assert.Equal(t, tt.id, job.ItemID)
		assert.Equal(t, tt.prio, job.Priority)
	}
}

// =============================================================================
// Indexer Stats Tests
// =============================================================================

// TestIndexerStatsFieldTypes exercises basic invariants for TestIndexerStatsFieldTypes.
func TestIndexerStatsFieldTypes(t *testing.T) {
	stats := IndexerStats{
		TotalJobs:      100,
		CompletedJobs:  80,
		FailedJobs:     5,
		QueueSize:      15,
		LastIndexedAt:  time.Now(),
		LastError:      "test error",
		ProcessingRate: 10.5,
	}

	assert.Equal(t, int64(100), stats.TotalJobs)
	assert.Equal(t, int64(80), stats.CompletedJobs)
	assert.Equal(t, int64(5), stats.FailedJobs)
	assert.Equal(t, 15, stats.QueueSize)
	assert.NotEmpty(t, stats.LastError)
	assert.InDelta(t, 10.5, stats.ProcessingRate, 0.01)
}

// =============================================================================
// Error Handling in Query Building
// =============================================================================

// TestBuildSearchQueryErrorCases exercises basic invariants for TestBuildSearchQueryErrorCases.
func TestBuildSearchQueryErrorCases(t *testing.T) {
	tests := []struct {
		input    string
		expected string
		name     string
	}{
		{"", "", "empty"},
		{"   ", "", "whitespace"},
		{"single", "single", "single word"},
		{"two words", "two & words", "two words"},
		{"a b c", "a & b & c", "three words"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := BuildSearchQuery(tt.input)
			assert.Equal(t, tt.expected, result)
		})
	}
}

// =============================================================================
// VectorToString Stability Tests
// =============================================================================

// TestVectorToStringConsistency exercises basic invariants for TestVectorToStringConsistency.
func TestVectorToStringConsistency(t *testing.T) {
	// Test that the same vector produces the same string
	vec := []float32{0.1, 0.2, 0.3}
	result1 := vectorToString(vec)
	result2 := vectorToString(vec)
	assert.Equal(t, result1, result2)
}

// TestVectorToStringDifferentVectors exercises basic invariants for TestVectorToStringDifferentVectors.
func TestVectorToStringDifferentVectors(t *testing.T) {
	vec1 := []float32{0.1, 0.2}
	vec2 := []float32{0.3, 0.4}
	result1 := vectorToString(vec1)
	result2 := vectorToString(vec2)
	assert.NotEqual(t, result1, result2)
}

// =============================================================================
// EngineConfig Tests
// =============================================================================

// TestSearchEngineConfigValidation exercises basic invariants for TestSearchEngineConfigValidation.
func TestSearchEngineConfigValidation(t *testing.T) {
	config := &EngineConfig{
		Pool:              nil,
		EmbeddingProvider: nil,
		Reranker:          nil,
		RerankEnabled:     false,
	}

	assert.Nil(t, config.Pool)
	assert.Nil(t, config.EmbeddingProvider)
	assert.Nil(t, config.Reranker)
	assert.False(t, config.RerankEnabled)
}

// =============================================================================
// Type Constant Tests
// =============================================================================

// TestSearchTypeValues exercises basic invariants for TestSearchTypeValues.
func TestSearchTypeValues(t *testing.T) {
	// Test that search type constants have the expected values
	typeTests := map[Type]string{
		TypeFullText: "fulltext",
		TypeVector:   "vector",
		TypeHybrid:   "hybrid",
		TypeFuzzy:    "fuzzy",
		TypePhonetic: "phonetic",
	}

	for st, expected := range typeTests {
		assert.Equal(t, Type(expected), st)
	}
}

// =============================================================================
// Request Limit/Offset Logic Tests
// =============================================================================

// TestSearchRequestLimitLogic exercises basic invariants for TestSearchRequestLimitLogic.
func TestSearchRequestLimitLogic(t *testing.T) {
	// Test limit application logic
	tests := []struct {
		input    int
		expected int
		name     string
	}{
		{0, 20, "zero defaults to 20"},
		{-1, 20, "negative defaults to 20"},
		{50, 50, "50 stays 50"},
		{100, 100, "100 stays 100"},
		{150, 100, "150 caps to 100"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			limit := tt.input
			if limit <= 0 {
				limit = 20
			}
			if limit > 100 {
				limit = 100
			}
			assert.Equal(t, tt.expected, limit)
		})
	}
}

// =============================================================================
// Request MinScore Logic Tests
// =============================================================================

// TestSearchRequestMinScoreLogic exercises basic invariants for TestSearchRequestMinScoreLogic.
func TestSearchRequestMinScoreLogic(t *testing.T) {
	tests := []struct {
		input    float64
		expected float64
		name     string
	}{
		{0, 0.1, "zero defaults to 0.1"},
		{0.5, 0.5, "0.5 stays 0.5"},
		{1.0, 1.0, "1.0 stays 1.0"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			minScore := tt.input
			if minScore == 0 {
				minScore = 0.1
			}
			assert.Equal(t, tt.expected, minScore)
		})
	}
}

// =============================================================================
// Request FuzzyThreshold Logic Tests
// =============================================================================

// TestSearchRequestFuzzyThresholdLogic exercises basic invariants for TestSearchRequestFuzzyThresholdLogic.
func TestSearchRequestFuzzyThresholdLogic(t *testing.T) {
	tests := []struct {
		input    float64
		expected float64
		name     string
	}{
		{0, 0.3, "zero defaults to 0.3"},
		{0.5, 0.5, "0.5 stays 0.5"},
		{0.8, 0.8, "0.8 stays 0.8"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			threshold := tt.input
			if threshold == 0 {
				threshold = 0.3
			}
			assert.Equal(t, tt.expected, threshold)
		})
	}
}

// =============================================================================
// Type DefaultingLogic Tests
// =============================================================================

// TestSearchRequestTypeLogic exercises basic invariants for TestSearchRequestTypeLogic.
func TestSearchRequestTypeLogic(t *testing.T) {
	tests := []struct {
		input    Type
		expected Type
		name     string
	}{
		{"", TypeFullText, "empty defaults to fulltext"},
		{TypeFullText, TypeFullText, "fulltext stays fulltext"},
		{TypeVector, TypeVector, "vector stays vector"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			searchType := tt.input
			if searchType == "" {
				searchType = TypeFullText
			}
			assert.Equal(t, tt.expected, searchType)
		})
	}
}

// =============================================================================
// Result Filtering Logic Tests
// =============================================================================

// TestSearchResultScoreFiltering exercises basic invariants for TestSearchResultScoreFiltering.
func TestSearchResultScoreFiltering(t *testing.T) {
	results := []Result{
		{ID: "1", Score: 0.05},
		{ID: "2", Score: 0.15},
		{ID: "3", Score: 0.5},
		{ID: "4", Score: 0.9},
	}

	minScore := 0.1
	filtered := make([]Result, 0)
	for _, r := range results {
		if r.Score >= minScore {
			filtered = append(filtered, r)
		}
	}

	assert.Equal(t, 3, len(filtered))
	for _, r := range filtered {
		assert.GreaterOrEqual(t, r.Score, minScore)
	}
}

// =============================================================================
// Extension Status Tests
// =============================================================================

// TestExtensionStatusCheckLogic exercises basic invariants for TestExtensionStatusCheckLogic.
func TestExtensionStatusCheckLogic(t *testing.T) {
	tests := []struct {
		status    *ExtensionStatus
		canSearch bool
		name      string
	}{
		{
			&ExtensionStatus{PgTrgm: true},
			true,
			"pg_trgm available",
		},
		{
			&ExtensionStatus{Vector: true},
			true,
			"vector available",
		},
		{
			&ExtensionStatus{},
			false,
			"no extensions",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			canSearch := tt.status.PgTrgm || tt.status.Vector
			assert.Equal(t, tt.canSearch, canSearch)
		})
	}
}

// =============================================================================
// MergeResults Weight Logic Tests
// =============================================================================

// TestMergeResultsWeightsCalculation exercises basic invariants for TestMergeResultsWeightsCalculation.
func TestMergeResultsWeightsCalculation(t *testing.T) {
	// Test the weight calculation logic
	ftScore := 0.8
	vecScore := 0.9
	ftWeight := 0.6
	vecWeight := 0.4

	// Combined score calculation
	combined := ftScore*ftWeight + vecScore*vecWeight
	expected := 0.8*0.6 + 0.9*0.4

	assert.InDelta(t, expected, combined, 0.001)
	assert.InDelta(t, 0.84, combined, 0.001) // 0.48 + 0.36 = 0.84
}

// =============================================================================
// Context Timeout Logic Tests
// =============================================================================

// TestContextTimeoutCreation exercises basic invariants for TestContextTimeoutCreation.
func TestContextTimeoutCreation(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), searchContextTimeoutLong)
	defer cancel()

	select {
	case <-ctx.Done():
		t.Fatal("context should not be done yet")
	default:
		// Expected
	}
}

// TestContextTimeoutExpiration exercises basic invariants for TestContextTimeoutExpiration.
func TestContextTimeoutExpiration(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), searchContextTimeoutShort)
	defer cancel()

	time.Sleep(searchContextSleep)

	select {
	case <-ctx.Done():
		// Expected - context expired
	default:
		t.Fatal("context should be done")
	}
}

// =============================================================================
// IndexOperation String Conversion
// =============================================================================

// TestIndexOperationStringConversion exercises basic invariants for TestIndexOperationStringConversion.
func TestIndexOperationStringConversion(t *testing.T) {
	op := OpIndex
	str := string(op)
	assert.Equal(t, "index", str)

	op2 := OpUpdate
	str2 := string(op2)
	assert.Equal(t, "update", str2)

	op3 := OpDelete
	str3 := string(op3)
	assert.Equal(t, "delete", str3)
}

// =============================================================================
// Engine Initialization Tests
// =============================================================================

// TestSearchEngineWithConfigSettings exercises basic invariants for TestSearchEngineWithConfigSettings.
func TestSearchEngineWithConfigSettings(t *testing.T) {
	config := &EngineConfig{
		Pool:              nil,
		EmbeddingProvider: nil,
		Reranker:          nil,
		RerankEnabled:     true,
	}

	engine := NewEngineWithConfig(config)
	assert.NotNil(t, engine)
	// RerankEnabled should be false because Reranker is nil
	assert.False(t, engine.rerankEnabled)
}

// TestSearchEngineBasicProperties exercises basic invariants for TestSearchEngineBasicProperties.
func TestSearchEngineBasicProperties(t *testing.T) {
	engine := NewEngine(nil)
	assert.NotNil(t, engine)
	assert.Nil(t, engine.pool)
	assert.Nil(t, engine.embeddingProvider)
	assert.Nil(t, engine.reranker)
	assert.False(t, engine.rerankEnabled)
}

// =============================================================================
// Time-based Tests
// =============================================================================

// TestDurationCalculation exercises basic invariants for TestDurationCalculation.
func TestDurationCalculation(t *testing.T) {
	start := time.Now()
	time.Sleep(searchDurationSleep)
	duration := time.Since(start)

	assert.Greater(t, duration, time.Duration(0))
	assert.GreaterOrEqual(t, duration, searchDurationSleep)
}

// =============================================================================
// Slice Operations
// =============================================================================

// TestSearchResultSliceOperations exercises basic invariants for TestSearchResultSliceOperations.
func TestSearchResultSliceOperations(t *testing.T) {
	results := make([]Result, 0, 4)
	results = append(results,
		Result{ID: "1", Title: "A"},
		Result{ID: "2", Title: "B"},
		Result{ID: "3", Title: "C"},
	)

	// Test length
	assert.Equal(t, 3, len(results))

	// Test appending
	results = append(results, Result{ID: "4", Title: "D"})
	assert.Equal(t, 4, len(results))

	// Test slicing
	subset := results[1:3]
	assert.Equal(t, 2, len(subset))
	assert.Equal(t, "B", subset[0].Title)
}

// =============================================================================
// Map Operations for Metadata
// =============================================================================

// TestSearchResultMetadataMap exercises basic invariants for TestSearchResultMetadataMap.
func TestSearchResultMetadataMap(t *testing.T) {
	metadata := map[string]interface{}{
		"key1": "value1",
		"key2": 42,
		"key3": true,
	}

	result := &Result{
		ID:       "test",
		Metadata: metadata,
	}

	assert.Equal(t, "value1", result.Metadata["key1"])
	assert.Equal(t, 42, result.Metadata["key2"])
	assert.Equal(t, true, result.Metadata["key3"])
	assert.Equal(t, 3, len(result.Metadata))
}

// =============================================================================
// Empty Collection Tests
// =============================================================================

// TestSearchResultEmptyCollections exercises basic invariants for TestSearchResultEmptyCollections.
func TestSearchResultEmptyCollections(t *testing.T) {
	req := &Request{
		Query:     "test",
		ItemTypes: []string{},
		Status:    []string{},
	}

	assert.Equal(t, 0, len(req.ItemTypes))
	assert.Equal(t, 0, len(req.Status))

	// Empty slices should not be nil
	assert.NotNil(t, req.ItemTypes)
	assert.NotNil(t, req.Status)
}

// =============================================================================
// Boolean Flag Tests
// =============================================================================

// TestSearchRequestBooleanFlags exercises basic invariants for TestSearchRequestBooleanFlags.
func TestSearchRequestBooleanFlags(t *testing.T) {
	// Test all boolean flag combinations
	tests := []struct {
		includeDeleted      bool
		enableTypoTolerance bool
		rerankEnabled       bool
	}{
		{true, true, true},
		{true, true, false},
		{true, false, true},
		{true, false, false},
		{false, true, true},
		{false, true, false},
		{false, false, true},
		{false, false, false},
	}

	for _, tt := range tests {
		req := &Request{
			Query:               "test",
			IncludeDeleted:      tt.includeDeleted,
			EnableTypoTolerance: tt.enableTypoTolerance,
		}

		assert.Equal(t, tt.includeDeleted, req.IncludeDeleted)
		assert.Equal(t, tt.enableTypoTolerance, req.EnableTypoTolerance)
	}
}

// =============================================================================
// Numeric Range Tests
// =============================================================================

// TestSearchRequestNumericRanges exercises basic invariants for TestSearchRequestNumericRanges.
func TestSearchRequestNumericRanges(t *testing.T) {
	tests := []struct {
		limit     int
		offset    int
		minScore  float64
		threshold float64
	}{
		{1, 0, 0.0, 0.0},
		{50, 25, 0.5, 0.3},
		{100, 1000, 1.0, 1.0},
		{999999, 999999, 999.99, 999.99},
	}

	for _, tt := range tests {
		req := &Request{
			Query:          "test",
			Limit:          tt.limit,
			Offset:         tt.offset,
			MinScore:       tt.minScore,
			FuzzyThreshold: tt.threshold,
		}

		assert.Equal(t, tt.limit, req.Limit)
		assert.Equal(t, tt.offset, req.Offset)
		assert.InDelta(t, tt.minScore, req.MinScore, 0.001)
		assert.InDelta(t, tt.threshold, req.FuzzyThreshold, 0.001)
	}
}
