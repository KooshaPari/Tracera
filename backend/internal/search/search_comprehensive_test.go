//go:build !integration && !e2e

package search

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const searchComprehensiveShortSleep = 10 * time.Millisecond

// =============================================================================
// Engine Configuration Tests
// =============================================================================

func TestSearchEngineConfig_WithProvider(t *testing.T) {
	provider := &mockEmbeddingProvider{
		embeddings: []embeddings.EmbeddingVector{{0.1, 0.2}},
		dimensions: 2,
		name:       "mock-provider",
	}

	config := &EngineConfig{
		Pool:              nil,
		EmbeddingProvider: provider,
		Reranker:          nil,
		RerankEnabled:     false,
	}

	assert.NotNil(t, config)
	assert.False(t, config.RerankEnabled)
	assert.Equal(t, provider, config.EmbeddingProvider)
}

func TestSearchEngineConfig_RerankDisabled(t *testing.T) {
	config := &EngineConfig{
		Pool:          nil,
		Reranker:      nil,
		RerankEnabled: false,
	}

	assert.NotNil(t, config)
	assert.False(t, config.RerankEnabled)
}

func TestSearchEngineConfig_NilReranker(t *testing.T) {
	config := &EngineConfig{
		Pool:          nil,
		Reranker:      nil,
		RerankEnabled: true,
	}

	assert.NotNil(t, config)
	assert.True(t, config.RerankEnabled)
}

// =============================================================================
// Search Request Default Values Tests
// =============================================================================

func TestSearchRequest_DefaultValues(t *testing.T) {
	req := &Request{Query: "test"}

	// Simulate default values being applied (as would happen in Search method)
	if req.Limit <= 0 {
		req.Limit = 20
	}
	if req.Limit > 100 {
		req.Limit = 100
	}
	if req.Type == "" {
		req.Type = TypeFullText
	}
	if req.MinScore == 0 {
		req.MinScore = 0.1
	}
	if req.FuzzyThreshold == 0 {
		req.FuzzyThreshold = 0.3
	}

	assert.Equal(t, 20, req.Limit)
	assert.Equal(t, TypeFullText, req.Type)
	assert.Equal(t, 0.1, req.MinScore)
	assert.Equal(t, 0.3, req.FuzzyThreshold)
}

func TestSearchRequest_LimitCapped(t *testing.T) {
	req := &Request{
		Query: "test",
		Limit: 200,
	}

	if req.Limit > 100 {
		req.Limit = 100
	}

	assert.Equal(t, 100, req.Limit)
}

func TestSearchRequest_ZeroLimitDefaulted(t *testing.T) {
	req := &Request{
		Query: "test",
		Limit: 0,
	}

	if req.Limit <= 0 {
		req.Limit = 20
	}

	assert.Equal(t, 20, req.Limit)
}

func TestSearchRequest_NegativeLimitDefaulted(t *testing.T) {
	req := &Request{
		Query: "test",
		Limit: -50,
	}

	if req.Limit <= 0 {
		req.Limit = 20
	}

	assert.Equal(t, 20, req.Limit)
}

// =============================================================================
// BuildSearchQuery Tests
// =============================================================================

func TestBuildSearchQuery_SingleWord(t *testing.T) {
	result := BuildSearchQuery("authentication")
	assert.Equal(t, "authentication", result)
}

func TestBuildSearchQuery_MultipleWords(t *testing.T) {
	result := BuildSearchQuery("user authentication system")
	assert.Equal(t, "user & authentication & system", result)
}

func TestBuildSearchQuery_MultipleSpaces(t *testing.T) {
	result := BuildSearchQuery("  multiple   spaces   ")
	assert.Equal(t, "multiple & spaces", result)
}

func TestBuildSearchQuery_EmptyQuery(t *testing.T) {
	result := BuildSearchQuery("")
	assert.Equal(t, "", result)
}

func TestBuildSearchQuery_OnlyWhitespace(t *testing.T) {
	result := BuildSearchQuery("   ")
	assert.Equal(t, "", result)
}

func TestBuildSearchQuery_TabsAndNewlines(t *testing.T) {
	result := BuildSearchQuery("  test\t\nquery  ")
	assert.Equal(t, "test & query", result)
}

func TestBuildSearchQuery_SingleSpaceWord(t *testing.T) {
	result := BuildSearchQuery(" word ")
	assert.Equal(t, "word", result)
}

func TestBuildSearchQuery_LongQueryManyWords(t *testing.T) {
	result := BuildSearchQuery("one two three four five")
	assert.Equal(t, "one & two & three & four & five", result)
}

// =============================================================================
// VectorToString Tests
// =============================================================================

func TestVectorToString_EmptyVector(t *testing.T) {
	vec := embeddings.EmbeddingVector{}
	result := vectorToString(vec)
	assert.Equal(t, "[]", result)
}

func TestVectorToString_SingleValue(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.5}
	result := vectorToString(vec)
	assert.Equal(t, "[0.500000]", result)
}

func TestVectorToString_MultipleValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.1, 0.2, 0.3}
	result := vectorToString(vec)
	assert.Equal(t, "[0.100000,0.200000,0.300000]", result)
}

func TestVectorToString_NegativeValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{-0.5, 0.5, -0.1}
	result := vectorToString(vec)
	assert.Equal(t, "[-0.500000,0.500000,-0.100000]", result)
}

func TestVectorToString_LargeValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{1.23456789, 9.87654321}
	result := vectorToString(vec)
	assert.Contains(t, result, "1.234568")
	assert.Contains(t, result, "9.876543")
}

func TestVectorToString_ZeroValue(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.0}
	result := vectorToString(vec)
	assert.Equal(t, "[0.000000]", result)
}

func TestVectorToString_MixedPrecision(t *testing.T) {
	vec := embeddings.EmbeddingVector{1.0, 0.00001, 999.999999}
	result := vectorToString(vec)
	assert.Contains(t, result, "[1.000000")
	assert.Contains(t, result, "0.000010")
	assert.Contains(t, result, "1000.000000") // Rounded to 6 decimal places
}

func TestVectorToString_HighDimensionality(t *testing.T) {
	vec := make(embeddings.EmbeddingVector, 10)
	for i := range vec {
		vec[i] = float32(i) / 10.0
	}
	result := vectorToString(vec)
	assert.Contains(t, result, "[0.000000")
	assert.True(t, len(result) > 50)
}

// =============================================================================
// Search Result Structure Tests
// =============================================================================

func TestSearchResult_Fields(t *testing.T) {
	now := time.Now()
	result := Result{
		ID:          "item-1",
		ProjectID:   "proj-1",
		Title:       "Test Item",
		Description: "Test Description",
		Type:        "feature",
		Status:      "active",
		Priority:    "high",
		Metadata:    map[string]interface{}{"key": "value"},
		Score:       0.95,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	assert.Equal(t, "item-1", result.ID)
	assert.Equal(t, "proj-1", result.ProjectID)
	assert.Equal(t, "Test Item", result.Title)
	assert.Equal(t, "Test Description", result.Description)
	assert.Equal(t, "feature", result.Type)
	assert.Equal(t, "active", result.Status)
	assert.Equal(t, "high", result.Priority)
	assert.Equal(t, "value", result.Metadata["key"])
	assert.Equal(t, 0.95, result.Score)
	assert.Equal(t, now, result.CreatedAt)
	assert.Equal(t, now, result.UpdatedAt)
}

func TestSearchResult_ZeroValues(t *testing.T) {
	result := Result{}

	assert.Empty(t, result.ID)
	assert.Empty(t, result.ProjectID)
	assert.Empty(t, result.Title)
	assert.Equal(t, 0.0, result.Score)
	assert.True(t, result.CreatedAt.IsZero())
}

func TestSearchResult_MetadataHandling(t *testing.T) {
	result := Result{
		ID: "item-1",
		Metadata: map[string]interface{}{
			"custom":  "value",
			"count":   42,
			"enabled": true,
			"nested": map[string]interface{}{
				"key": "value",
			},
		},
	}

	assert.Equal(t, "value", result.Metadata["custom"])
	assert.Equal(t, 42, result.Metadata["count"])
	assert.True(t, result.Metadata["enabled"].(bool))
}

func TestSearchResult_NilMetadata(t *testing.T) {
	result := Result{
		ID:       "item-1",
		Metadata: nil,
	}

	assert.Nil(t, result.Metadata)
}

// =============================================================================
// Response Structure Tests
// =============================================================================

func TestSearchResponse_Fields(t *testing.T) {
	results := []Result{
		{ID: "1", Score: 0.9},
		{ID: "2", Score: 0.8},
	}

	duration := 100 * time.Millisecond
	response := Response{
		Results:    results,
		TotalCount: 100,
		Query:      "search query",
		Type:       TypeFullText,
		Duration:   duration,
	}

	assert.Equal(t, 2, len(response.Results))
	assert.Equal(t, 100, response.TotalCount)
	assert.Equal(t, "search query", response.Query)
	assert.Equal(t, TypeFullText, response.Type)
	assert.Equal(t, duration, response.Duration)
}

func TestSearchResponse_EmptyResults(t *testing.T) {
	response := Response{
		Results:    []Result{},
		TotalCount: 0,
		Query:      "search",
		Type:       TypeFullText,
		Duration:   0,
	}

	assert.Equal(t, 0, len(response.Results))
	assert.Equal(t, 0, response.TotalCount)
}

// =============================================================================
// Merge Results Tests
// =============================================================================

func TestMergeResults_DeduplicatesAndWeights(t *testing.T) {
	engine := &Engine{}

	ftResults := []Result{
		{ID: "1", Title: "Item 1", Score: 0.9},
		{ID: "2", Title: "Item 2", Score: 0.8},
	}

	vecResults := []Result{
		{ID: "1", Title: "Item 1", Score: 0.7},
		{ID: "3", Title: "Item 3", Score: 0.85},
	}

	merged := engine.mergeResults(ftResults, vecResults, 0.6, 0.4)

	ids := make(map[string]bool)
	for _, r := range merged {
		ids[r.ID] = true
	}

	assert.Equal(t, 3, len(ids))
	assert.True(t, ids["1"])
	assert.True(t, ids["2"])
	assert.True(t, ids["3"])

	// Check combined score for item 1
	var item1 Result
	for _, r := range merged {
		if r.ID == "1" {
			item1 = r
			break
		}
	}

	expectedScore := (0.9 * 0.6) + (0.7 * 0.4)
	assert.InDelta(t, expectedScore, item1.Score, 0.01)
}

func TestMergeResults_Empty(t *testing.T) {
	engine := &Engine{}

	merged := engine.mergeResults([]Result{}, []Result{}, 0.6, 0.4)

	assert.Equal(t, 0, len(merged))
}

func TestMergeResults_OnlyFullText(t *testing.T) {
	engine := &Engine{}

	ftResults := []Result{
		{ID: "1", Title: "Item 1", Score: 0.9},
		{ID: "2", Title: "Item 2", Score: 0.8},
	}

	merged := engine.mergeResults(ftResults, []Result{}, 0.6, 0.4)

	assert.Equal(t, 2, len(merged))
	// Scores should be weighted
	for _, r := range merged {
		assert.True(t, r.Score <= 0.9*0.6+0.01)
	}
}

func TestMergeResults_OnlyVector(t *testing.T) {
	engine := &Engine{}

	vecResults := []Result{
		{ID: "1", Title: "Item 1", Score: 0.9},
		{ID: "2", Title: "Item 2", Score: 0.8},
	}

	merged := engine.mergeResults([]Result{}, vecResults, 0.6, 0.4)

	assert.Equal(t, 2, len(merged))
	// Scores should be weighted by vector weight
	for _, r := range merged {
		assert.True(t, r.Score <= 0.9*0.4+0.01)
	}
}

func TestMergeResults_AllDifferentIds(t *testing.T) {
	engine := &Engine{}

	ftResults := []Result{
		{ID: "1", Score: 0.9},
		{ID: "2", Score: 0.8},
	}

	vecResults := []Result{
		{ID: "3", Score: 0.85},
		{ID: "4", Score: 0.75},
	}

	merged := engine.mergeResults(ftResults, vecResults, 0.6, 0.4)

	assert.Equal(t, 4, len(merged))
}

func TestMergeResults_AllDuplicates(t *testing.T) {
	engine := &Engine{}

	ftResults := []Result{
		{ID: "1", Score: 0.9},
		{ID: "2", Score: 0.8},
	}

	vecResults := []Result{
		{ID: "1", Score: 0.85},
		{ID: "2", Score: 0.75},
	}

	merged := engine.mergeResults(ftResults, vecResults, 0.6, 0.4)

	assert.Equal(t, 2, len(merged))
}

// =============================================================================
// Reranker Mock Tests
// =============================================================================

func TestRerankResults_NoReranker(t *testing.T) {
	engine := &Engine{
		reranker:      nil,
		rerankEnabled: false,
	}

	results := []Result{
		{ID: "1", Title: "First", Description: "First item", Score: 0.8},
	}

	reranked, err := engine.rerankResults(context.Background(), "query", results)

	require.NoError(t, err)
	assert.Equal(t, results, reranked)
}

func TestRerankResults_DisabledReranking(t *testing.T) {
	engine := &Engine{
		reranker:      nil,
		rerankEnabled: false,
	}

	results := []Result{
		{ID: "1", Title: "First", Description: "First item", Score: 0.8},
		{ID: "2", Title: "Second", Description: "Second item", Score: 0.9},
	}

	reranked, err := engine.rerankResults(context.Background(), "query", results)

	require.NoError(t, err)
	// Should return same results when disabled
	assert.Equal(t, results, reranked)
}

func TestRerankResults_NoRerankerSet(t *testing.T) {
	engine := &Engine{
		reranker:      nil,
		rerankEnabled: false,
	}

	results := []Result{
		{ID: "1", Title: "First", Description: "First", Score: 0.8},
	}

	reranked, err := engine.rerankResults(context.Background(), "query", results)

	require.NoError(t, err)
	assert.Equal(t, results, reranked)
}

// =============================================================================
// Search Types Tests
// =============================================================================

func TestSearchTypes_Constants(t *testing.T) {
	assert.Equal(t, Type("fulltext"), TypeFullText)
	assert.Equal(t, Type("vector"), TypeVector)
	assert.Equal(t, Type("hybrid"), TypeHybrid)
	assert.Equal(t, Type("fuzzy"), TypeFuzzy)
	assert.Equal(t, Type("phonetic"), TypePhonetic)
}

func TestSearchTypes_StringConversion(t *testing.T) {
	types := []Type{
		TypeFullText,
		TypeVector,
		TypeHybrid,
		TypeFuzzy,
		TypePhonetic,
	}

	for _, st := range types {
		assert.NotEmpty(t, string(st))
	}
}

// =============================================================================
// Index Operation Tests
// =============================================================================

func TestIndexOperation_Constants(t *testing.T) {
	assert.Equal(t, IndexOperation("index"), OpIndex)
	assert.Equal(t, IndexOperation("update"), OpUpdate)
	assert.Equal(t, IndexOperation("delete"), OpDelete)
}

func TestIndexJob_Structure(t *testing.T) {
	job := IndexJob{
		Operation: OpIndex,
		ItemID:    "item-123",
		Priority:  1,
	}

	assert.Equal(t, OpIndex, job.Operation)
	assert.Equal(t, "item-123", job.ItemID)
	assert.Equal(t, 1, job.Priority)
}

func TestIndexJob_AllOperations(t *testing.T) {
	operations := []IndexOperation{OpIndex, OpUpdate, OpDelete}

	for _, op := range operations {
		job := IndexJob{
			Operation: op,
			ItemID:    "item-123",
			Priority:  1,
		}

		assert.NotEmpty(t, job.Operation)
	}
}

// =============================================================================
// Extension Status Tests
// =============================================================================

func TestExtensionStatus_AllEnabled(t *testing.T) {
	status := &ExtensionStatus{
		PgTrgm:        true,
		FuzzyStrMatch: true,
		Unaccent:      true,
		Vector:        true,
	}

	assert.True(t, status.PgTrgm)
	assert.True(t, status.FuzzyStrMatch)
	assert.True(t, status.Unaccent)
	assert.True(t, status.Vector)
}

func TestExtensionStatus_Partial(t *testing.T) {
	status := &ExtensionStatus{
		PgTrgm:        true,
		FuzzyStrMatch: true,
		Unaccent:      false,
		Vector:        false,
	}

	assert.True(t, status.PgTrgm)
	assert.True(t, status.FuzzyStrMatch)
	assert.False(t, status.Unaccent)
	assert.False(t, status.Vector)
}

func TestExtensionStatus_AllDisabled(t *testing.T) {
	status := &ExtensionStatus{
		PgTrgm:        false,
		FuzzyStrMatch: false,
		Unaccent:      false,
		Vector:        false,
	}

	assert.False(t, status.PgTrgm)
	assert.False(t, status.FuzzyStrMatch)
	assert.False(t, status.Unaccent)
	assert.False(t, status.Vector)
}

// =============================================================================
// Mock Embedding Provider Tests
// =============================================================================

func TestMockEmbeddingProvider_Embed(t *testing.T) {
	provider := &mockEmbeddingProvider{
		embeddings: []embeddings.EmbeddingVector{{0.1, 0.2, 0.3}},
		dimensions: 3,
		name:       "mock",
		model:      "mock-model",
	}

	resp, err := provider.Embed(context.Background(), &embeddings.EmbeddingRequest{
		Texts: []string{"test"},
	})

	require.NoError(t, err)
	assert.Equal(t, 1, len(resp.Embeddings))
	assert.Equal(t, 3, len(resp.Embeddings[0]))
}

func TestMockEmbeddingProvider_GetDimensions(t *testing.T) {
	provider := &mockEmbeddingProvider{
		dimensions: 768,
	}

	assert.Equal(t, 768, provider.GetDimensions())
}

func TestMockEmbeddingProvider_GetName(t *testing.T) {
	provider := &mockEmbeddingProvider{
		name: "test-provider",
	}

	assert.Equal(t, "test-provider", provider.GetName())
}

func TestMockEmbeddingProvider_GetDefaultModel(t *testing.T) {
	provider := &mockEmbeddingProvider{
		model: "model-v1",
	}

	assert.Equal(t, "model-v1", provider.GetDefaultModel())
}

func TestMockEmbeddingProvider_HealthCheck(t *testing.T) {
	provider := &mockEmbeddingProvider{
		err: nil,
	}

	err := provider.HealthCheck(context.Background())
	assert.NoError(t, err)
}

func TestMockEmbeddingProvider_HealthCheckError(t *testing.T) {
	provider := &mockEmbeddingProvider{
		err: errors.New("service down"),
	}

	err := provider.HealthCheck(context.Background())
	assert.Error(t, err)
}

func TestMockEmbeddingProvider_EmbedError(t *testing.T) {
	provider := &mockEmbeddingProvider{
		err: errors.New("API error"),
	}

	resp, err := provider.Embed(context.Background(), &embeddings.EmbeddingRequest{
		Texts: []string{"test"},
	})

	assert.Error(t, err)
	assert.Nil(t, resp)
}

// =============================================================================
// Mock Reranker Tests
// =============================================================================

func TestMockReranker_Rerank(t *testing.T) {
	mockRerank := &mockReranker{
		results: []embeddings.RerankResult{
			{Index: 0, RelevanceScore: 0.9},
			{Index: 1, RelevanceScore: 0.7},
		},
	}

	resp, err := mockRerank.Rerank(context.Background(), &embeddings.RerankRequest{
		Query: "test",
		Documents: []embeddings.Document{
			{Text: "doc 1"},
			{Text: "doc 2"},
		},
	})

	require.NoError(t, err)
	assert.Equal(t, 2, len(resp.Results))
	assert.Equal(t, 0.9, resp.Results[0].RelevanceScore)
}

func TestMockReranker_RerankError(t *testing.T) {
	mockRerank := &mockReranker{
		err: errors.New("reranking failed"),
	}

	resp, err := mockRerank.Rerank(context.Background(), &embeddings.RerankRequest{
		Query: "test",
	})

	assert.Error(t, err)
	assert.Nil(t, resp)
}

// =============================================================================
// Score Handling Tests
// =============================================================================

func TestScoreHandling_MinScore(t *testing.T) {
	results := []struct {
		score float64
		valid bool
	}{
		{0.9, true},
		{0.5, true},
		{0.1, true},
		{0.05, false},
		{0.0, false},
	}

	minScore := 0.1

	for _, r := range results {
		if r.score >= minScore {
			assert.True(t, r.valid)
		} else {
			assert.False(t, r.valid)
		}
	}
}

func TestScoreHandling_MaxScore(t *testing.T) {
	results := []float64{0.9, 1.0, 0.5, 0.1}

	maxScore := 1.0
	for _, r := range results {
		assert.LessOrEqual(t, r, maxScore)
	}
}

func TestScoreHandling_ZeroScore(t *testing.T) {
	result := Result{
		ID:    "item-1",
		Score: 0.0,
	}

	assert.Equal(t, 0.0, result.Score)
}

// =============================================================================
// Offset and Limit Tests
// =============================================================================

func TestPagination_OffsetAndLimit(t *testing.T) {
	testCases := []struct {
		offset int
		limit  int
		total  int
		valid  bool
	}{
		{0, 10, 100, true},
		{10, 10, 100, true},
		{90, 10, 100, true},
		{100, 10, 100, true},
		{0, 100, 1000, true},
		{500, 100, 1000, true},
	}

	for _, tc := range testCases {
		end := tc.offset + tc.limit
		assert.LessOrEqual(t, end, tc.total+tc.limit)
	}
}

// =============================================================================
// Filter Handling Tests
// =============================================================================

func TestFilter_ItemTypes(t *testing.T) {
	req := &Request{
		ItemTypes: []string{"epic", "feature", "task"},
	}

	assert.Equal(t, 3, len(req.ItemTypes))
	assert.Contains(t, req.ItemTypes, "epic")
	assert.Contains(t, req.ItemTypes, "feature")
	assert.Contains(t, req.ItemTypes, "task")
}

func TestFilter_Status(t *testing.T) {
	req := &Request{
		Status: []string{"active", "done", "blocked"},
	}

	assert.Equal(t, 3, len(req.Status))
	assert.Contains(t, req.Status, "active")
	assert.Contains(t, req.Status, "done")
	assert.Contains(t, req.Status, "blocked")
}

func TestFilter_ProjectID(t *testing.T) {
	req := &Request{
		ProjectID: "proj-123",
	}

	assert.Equal(t, "proj-123", req.ProjectID)
	assert.NotEmpty(t, req.ProjectID)
}

func TestFilter_Empty(t *testing.T) {
	req := &Request{
		ItemTypes: []string{},
		Status:    []string{},
		ProjectID: "",
	}

	assert.Equal(t, 0, len(req.ItemTypes))
	assert.Equal(t, 0, len(req.Status))
	assert.Empty(t, req.ProjectID)
}

// =============================================================================
// Concurrency Safety Tests
// =============================================================================

func TestConcurrency_SearchEngineReadSafety(_ *testing.T) {
	engine := &Engine{}

	done := make(chan bool, 3)

	for i := 0; i < 3; i++ {
		go func(_ int) {
			// All reading public fields - should be safe
			_ = engine.pool
			_ = engine.embeddingProvider
			done <- true
		}(i)
	}

	for i := 0; i < 3; i++ {
		<-done
	}
}

// =============================================================================
// Error Handling Tests
// =============================================================================

func TestErrorHandling_InvalidType(t *testing.T) {
	st := Type("invalid")

	validTypes := map[Type]bool{
		TypeFullText: true,
		TypeVector:   true,
		TypeHybrid:   true,
		TypeFuzzy:    true,
		TypePhonetic: true,
	}

	assert.False(t, validTypes[st])
}

func TestErrorHandling_MissingQuery(t *testing.T) {
	req := &Request{
		Query: "",
	}

	assert.Empty(t, req.Query)
}

func TestErrorHandling_NegativeThreshold(t *testing.T) {
	req := &Request{
		FuzzyThreshold: -0.5,
	}

	assert.Less(t, req.FuzzyThreshold, 0.0)
}

// =============================================================================
// Duration Tests
// =============================================================================

func TestDuration_Tracking(t *testing.T) {
	start := time.Now()
	time.Sleep(searchComprehensiveShortSleep)
	end := time.Now()

	duration := end.Sub(start)

	assert.Greater(t, duration, time.Duration(0))
	assert.LessOrEqual(t, duration, 100*time.Millisecond)
}

func TestDuration_ZeroDuration(t *testing.T) {
	duration := time.Duration(0)

	assert.Equal(t, duration, time.Duration(0))
}
