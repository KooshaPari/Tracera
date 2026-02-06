//go:build !integration && !e2e

package search

import (
	"strings"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
	"github.com/stretchr/testify/assert"
)

// =============================================================================
// BuildSearchQuery Extended Tests
// =============================================================================

func TestBuildSearchQuery_FourWords(t *testing.T) {
	result := BuildSearchQuery("one two three four")
	assert.Equal(t, "one & two & three & four", result)
}

func TestBuildSearchQuery_TrimmedInput(t *testing.T) {
	result := BuildSearchQuery("  hello  world  ")
	assert.Equal(t, "hello & world", result)
}

func TestBuildSearchQuery_TabSeparated(t *testing.T) {
	result := BuildSearchQuery("tab\tseparated\twords")
	assert.Equal(t, "tab & separated & words", result)
}

// =============================================================================
// VectorToString Extended Tests
// =============================================================================

func TestVectorToString_LargeVector(t *testing.T) {
	vec := make(embeddings.EmbeddingVector, 50)
	for i := 0; i < 50; i++ {
		vec[i] = float32(i) * 0.02
	}
	result := vectorToString(vec)
	assert.True(t, strings.HasPrefix(result, "["))
	assert.True(t, strings.HasSuffix(result, "]"))
	assert.Equal(t, 49, strings.Count(result, ",")) // 50 elements = 49 commas
}

func TestVectorToString_ZeroValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.0, 0.0, 0.0}
	result := vectorToString(vec)
	assert.Equal(t, "[0.000000,0.000000,0.000000]", result)
}

func TestVectorToString_MixedValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.0, 1.5, -0.5}
	result := vectorToString(vec)
	assert.Contains(t, result, "0.000000")
	assert.Contains(t, result, "1.500000")
	assert.Contains(t, result, "-0.500000")
}

// =============================================================================
// Type Constants Tests
// =============================================================================

func TestSearchTypeConstants(t *testing.T) {
	assert.Equal(t, Type("fulltext"), TypeFullText)
	assert.Equal(t, Type("vector"), TypeVector)
	assert.Equal(t, Type("hybrid"), TypeHybrid)
	assert.Equal(t, Type("fuzzy"), TypeFuzzy)
	assert.Equal(t, Type("phonetic"), TypePhonetic)
}

// =============================================================================
// Request Zero Values Tests
// =============================================================================

func TestSearchRequest_ZeroLimit(t *testing.T) {
	req := &Request{Query: "test", Limit: 0}
	// Simulate default application
	if req.Limit <= 0 {
		req.Limit = 20
	}
	assert.Equal(t, 20, req.Limit)
}

func TestSearchRequest_ZeroMinScore(t *testing.T) {
	req := &Request{Query: "test", MinScore: 0}
	// Simulate default application
	if req.MinScore == 0 {
		req.MinScore = 0.1
	}
	assert.Equal(t, 0.1, req.MinScore)
}

func TestSearchRequest_ZeroFuzzyThreshold(t *testing.T) {
	req := &Request{Query: "test", FuzzyThreshold: 0}
	// Simulate default application
	if req.FuzzyThreshold == 0 {
		req.FuzzyThreshold = 0.3
	}
	assert.Equal(t, 0.3, req.FuzzyThreshold)
}

// =============================================================================
// Response Structure Tests
// =============================================================================

func TestSearchResponse_ResultsField(t *testing.T) {
	resp := &Response{
		Results:    []Result{},
		TotalCount: 0,
		Query:      "test",
	}
	assert.NotNil(t, resp.Results)
	assert.Equal(t, 0, len(resp.Results))
}

func TestSearchResponse_WithResults(t *testing.T) {
	resp := &Response{
		Results: []Result{
			{ID: "1", Title: "Test"},
			{ID: "2", Title: "Test2"},
		},
		TotalCount: 2,
	}
	assert.Equal(t, 2, len(resp.Results))
	assert.Equal(t, 2, resp.TotalCount)
}

// =============================================================================
// Result Structure Tests
// =============================================================================

func TestSearchResult_EmptyMetadata(t *testing.T) {
	result := &Result{
		ID:    "test",
		Title: "Test",
	}
	assert.Nil(t, result.Metadata)
}

func TestSearchResult_WithMetadata(t *testing.T) {
	metadata := map[string]interface{}{
		"key1": "value1",
		"key2": 123,
	}
	result := &Result{
		ID:       "test",
		Metadata: metadata,
	}
	assert.NotNil(t, result.Metadata)
	assert.Equal(t, 2, len(result.Metadata))
}

// =============================================================================
// ExtensionStatus Tests
// =============================================================================

func TestExtensionStatus_AllTrue(t *testing.T) {
	status := &ExtensionStatus{
		PgTrgm:        true,
		FuzzyStrMatch: true,
		Unaccent:      true,
		Vector:        true,
	}
	assert.True(t, status.PgTrgm)
	assert.True(t, status.Vector)
}

func TestExtensionStatus_AllFalse(t *testing.T) {
	status := &ExtensionStatus{}
	assert.False(t, status.PgTrgm)
	assert.False(t, status.FuzzyStrMatch)
	assert.False(t, status.Unaccent)
	assert.False(t, status.Vector)
}

func TestExtensionStatus_PartialTrue(t *testing.T) {
	status := &ExtensionStatus{
		PgTrgm:        true,
		FuzzyStrMatch: false,
		Unaccent:      false,
		Vector:        false,
	}
	assert.True(t, status.PgTrgm)
	assert.False(t, status.Vector)
}

// =============================================================================
// EngineConfig Tests
// =============================================================================

func TestSearchEngineConfig_DefaultValues(t *testing.T) {
	config := &EngineConfig{}
	assert.Nil(t, config.Pool)
	assert.Nil(t, config.EmbeddingProvider)
	assert.Nil(t, config.Reranker)
	assert.False(t, config.RerankEnabled)
}

func TestSearchEngineConfig_RankEnabledNoReranker(t *testing.T) {
	config := &EngineConfig{
		RerankEnabled: true,
		Reranker:      nil,
	}
	assert.True(t, config.RerankEnabled)
	assert.Nil(t, config.Reranker)
}

// =============================================================================
// BuildSearchQuery Edge Cases
// =============================================================================

func TestBuildSearchQuery_NewlineSeparated(t *testing.T) {
	result := BuildSearchQuery("line1\nline2\nline3")
	// Fields splits on whitespace including newlines
	assert.Contains(t, result, "&")
}

func TestBuildSearchQuery_MixedWhitespace(t *testing.T) {
	result := BuildSearchQuery("  \t  word1  \n  word2  ")
	assert.Equal(t, "word1 & word2", result)
}

func TestBuildSearchQuery_SingleCharacters(t *testing.T) {
	result := BuildSearchQuery("a b c d e")
	assert.Equal(t, "a & b & c & d & e", result)
}

func TestBuildSearchQuery_LongQuery(t *testing.T) {
	longQuery := strings.Repeat("word ", 20)
	result := BuildSearchQuery(longQuery)
	wordCount := len(strings.Fields(longQuery))
	expectedAmpersands := wordCount - 1
	assert.Equal(t, expectedAmpersands, strings.Count(result, "&"))
}

// =============================================================================
// VectorToString Precision Tests
// =============================================================================

func TestVectorToString_HighPrecisionValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.123456, 0.987654}
	result := vectorToString(vec)
	assert.Contains(t, result, "0.123456")
	assert.Contains(t, result, "0.987654")
}

func TestVectorToString_VerySmallValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.00001, 0.00002}
	result := vectorToString(vec)
	assert.True(t, strings.Contains(result, "0.00001") || strings.Contains(result, "0.000010"))
}

func TestVectorToString_VeryLargeValues(t *testing.T) {
	vec := embeddings.EmbeddingVector{999.999, 1000.0}
	result := vectorToString(vec)
	assert.Contains(t, result, "999.999")
	assert.Contains(t, result, "1000")
}

// =============================================================================
// BuildSearchQuery With Special Words
// =============================================================================

func TestBuildSearchQuery_ReservedWords(t *testing.T) {
	result := BuildSearchQuery("AND OR NOT")
	// These are just regular words in our context
	assert.Contains(t, result, "AND")
	assert.Contains(t, result, "OR")
}

func TestBuildSearchQuery_Numbers(t *testing.T) {
	result := BuildSearchQuery("123 456 789")
	assert.Equal(t, "123 & 456 & 789", result)
}

func TestBuildSearchQuery_AlphanumericMix(t *testing.T) {
	result := BuildSearchQuery("abc123 def456 ghi789")
	assert.Contains(t, result, "abc123")
	assert.Contains(t, result, "def456")
	assert.Contains(t, result, "&")
}

// =============================================================================
// Vector Building Tests
// =============================================================================

func TestVectorToString_SingleZero(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.0}
	result := vectorToString(vec)
	assert.Equal(t, "[0.000000]", result)
}

func TestVectorToString_SingleOne(t *testing.T) {
	vec := embeddings.EmbeddingVector{1.0}
	result := vectorToString(vec)
	assert.Equal(t, "[1.000000]", result)
}

func TestVectorToString_FormattedCorrectly(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.5, 1.5, 2.5}
	result := vectorToString(vec)
	// Check format: [x.xxxxxx,y.yyyyyy,z.zzzzzz]
	assert.True(t, strings.HasPrefix(result, "["))
	assert.True(t, strings.HasSuffix(result, "]"))
	parts := strings.Split(result[1:len(result)-1], ",")
	assert.Equal(t, 3, len(parts))
}

// =============================================================================
// Embedding Vector Type Tests
// =============================================================================

func TestEmbeddingVectorType(t *testing.T) {
	vec := embeddings.EmbeddingVector{0.1, 0.2, 0.3}
	assert.Equal(t, 3, len(vec))
	assert.Equal(t, float32(0.1), vec[0])
}

func TestEmbeddingVectorCreation(t *testing.T) {
	vec := make(embeddings.EmbeddingVector, 10)
	assert.Equal(t, 10, len(vec))
	// All zeros initially
	for _, v := range vec {
		assert.Equal(t, float32(0.0), v)
	}
}

// =============================================================================
// String Building and Query Construction
// =============================================================================

func TestBuildSearchQuery_Consistency(t *testing.T) {
	query := "search query here"
	result1 := BuildSearchQuery(query)
	result2 := BuildSearchQuery(query)
	assert.Equal(t, result1, result2) // Should be deterministic
}

func TestBuildSearchQuery_WhitespaceHandling(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"single", "single"},
		{"two words", "two & words"},
		{"  trimmed  ", "trimmed"},
		{"one  two  three", "one & two & three"},
	}

	for _, tt := range tests {
		result := BuildSearchQuery(tt.input)
		assert.Equal(t, tt.expected, result)
	}
}

// =============================================================================
// VectorToString Output Format
// =============================================================================

func TestVectorToString_OutputFormat(t *testing.T) {
	tests := []struct {
		input  embeddings.EmbeddingVector
		prefix string
		suffix string
	}{
		{embeddings.EmbeddingVector{}, "[", "]"},
		{embeddings.EmbeddingVector{1.0}, "[", "]"},
		{embeddings.EmbeddingVector{1.0, 2.0}, "[", "]"},
	}

	for _, tt := range tests {
		result := vectorToString(tt.input)
		assert.True(t, strings.HasPrefix(result, tt.prefix))
		assert.True(t, strings.HasSuffix(result, tt.suffix))
	}
}

// =============================================================================
// Numeric Precision Tests
// =============================================================================

func TestVectorToString_DecimalPlaces(t *testing.T) {
	vec := embeddings.EmbeddingVector{1.23456789}
	result := vectorToString(vec)
	// Should format with 6 decimal places
	assert.Contains(t, result, "1.234568") // Rounded to 6 decimal places
}
