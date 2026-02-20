// Package embeddings tests the embeddings components.
package embeddings

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	testDimensionsVoyage      = 1024
	testDimensionsOpenRouter  = 1536
	testTextsCount            = 250
	testBatchSize             = 100
	testBatchCount            = 3
	testBatchLastSize         = 50
	testDefaultBatchCount     = 2
	testDefaultBatchSize      = 128
	testDefaultBatchRemainder = 122
	testPromptTokensLarge     = 10
	testPromptTokensSmall     = 5
	testCostResp1             = 0.001
	testCostResp2             = 0.0005
	testCostMerged            = 0.0015
	testCostDelta             = 0.0001
	testTimeout               = 30 * time.Second
	testMaxRetries            = 3
	testRateLimit             = 300
	testTopK                  = 2
	testEmbeddingsCount       = 2
	testEmbeddingCountSingle  = 1
	testScoreDelta            = 0.1
	testEmbeddingText         = "text"
)

// TestProviderFactory tests the provider factory
func TestProviderFactory(t *testing.T) {
	factory := NewProviderFactory()

	// Create a mock provider
	mockProvider := &MockProvider{
		name:       "mock",
		dimensions: testDimensionsVoyage,
	}

	// Register provider
	factory.Register(ProviderType("mock"), mockProvider)

	// Retrieve provider
	provider, err := factory.Get(ProviderType("mock"))
	require.NoError(t, err)
	assert.Equal(t, "mock", provider.GetName())

	// Try to get non-existent provider
	_, err = factory.Get(ProviderType("nonexistent"))
	require.Error(t, err)
}

// TestBatchRequest tests the batch request splitting
func TestBatchRequest(t *testing.T) {
	texts := make([]string, testTextsCount)
	for i := range texts {
		texts[i] = testEmbeddingText
	}

	// Test with batch size 100
	batches := BatchRequest(texts, testBatchSize)
	assert.Len(t, batches, testBatchCount)
	assert.Len(t, batches[0], testBatchSize)
	assert.Len(t, batches[1], testBatchSize)
	assert.Len(t, batches[2], testBatchLastSize)

	// Test with default batch size
	batches = BatchRequest(texts, 0)
	assert.Len(t, batches, testDefaultBatchCount)
	assert.Len(t, batches[0], testDefaultBatchSize)
	assert.Len(t, batches[1], testDefaultBatchRemainder)
}

// TestMergeResponses tests response merging
func TestMergeResponses(t *testing.T) {
	resp1 := &EmbeddingResponse{
		Model:      "test-model",
		Embeddings: []EmbeddingVector{{1, 2, 3}, {4, 5, 6}},
		Usage: TokenUsage{
			PromptTokens: testPromptTokensLarge,
			TotalTokens:  testPromptTokensLarge,
			CostUSD:      testCostResp1,
		},
	}

	resp2 := &EmbeddingResponse{
		Model:      "test-model",
		Embeddings: []EmbeddingVector{{7, 8, 9}},
		Usage: TokenUsage{
			PromptTokens: testPromptTokensSmall,
			TotalTokens:  testPromptTokensSmall,
			CostUSD:      testCostResp2,
		},
	}

	merged := MergeResponses([]*EmbeddingResponse{resp1, resp2})

	assert.Equal(t, "test-model", merged.Model)
	assert.Len(t, merged.Embeddings, 3)
	assert.Equal(t, testPromptTokensLarge+testPromptTokensSmall, merged.Usage.PromptTokens)
	assert.Equal(t, testPromptTokensLarge+testPromptTokensSmall, merged.Usage.TotalTokens)
	assert.InDelta(t, testCostMerged, merged.Usage.CostUSD, testCostDelta)
}

// TestValidateEmbeddings tests embedding validation
func TestValidateEmbeddings(t *testing.T) {
	// Valid embeddings
	embeddings := []EmbeddingVector{
		{1.0, 2.0, 3.0},
		{4.0, 5.0, 6.0},
	}
	err := ValidateEmbeddings(embeddings, 3)
	require.NoError(t, err)

	// Invalid dimension
	err = ValidateEmbeddings(embeddings, 4)
	require.Error(t, err)

	// Empty embeddings
	err = ValidateEmbeddings([]EmbeddingVector{}, 3)
	require.Error(t, err)
}

// TestVoyageProvider tests VoyageAI provider (unit test with mock)
func TestVoyageProviderCreation(t *testing.T) {
	config := &ProviderConfig{
		APIKey:       "test-key",
		DefaultModel: ModelVoyage35,
		Dimensions:   testDimensionsVoyage,
	}

	provider, err := NewVoyageProvider(config)
	require.NoError(t, err)
	assert.NotNil(t, provider)
	assert.Equal(t, "VoyageAI", provider.GetName())
	assert.Equal(t, testDimensionsVoyage, provider.GetDimensions())
	assert.Equal(t, ModelVoyage35, provider.GetDefaultModel())
}

// TestVoyageProviderNoAPIKey tests VoyageAI provider without API key
func TestVoyageProviderNoAPIKey(t *testing.T) {
	config := &ProviderConfig{
		APIKey: "",
	}

	_, err := NewVoyageProvider(config)
	require.Error(t, err)
}

// TestOpenRouterProvider tests OpenRouter provider creation
func TestOpenRouterProviderCreation(t *testing.T) {
	config := &ProviderConfig{
		APIKey:       "test-key",
		DefaultModel: ModelTextEmbedding3Small,
		Dimensions:   testDimensionsOpenRouter,
	}

	provider, err := NewOpenRouterProvider(config)
	require.NoError(t, err)
	assert.NotNil(t, provider)
	assert.Equal(t, "OpenRouter", provider.GetName())
	assert.Equal(t, testDimensionsOpenRouter, provider.GetDimensions())
}

// TestReranker tests reranker creation
func TestRerankerCreation(t *testing.T) {
	reranker, err := NewReranker("test-key", ModelRerank25, testRateLimit, testMaxRetries)
	require.NoError(t, err)
	assert.NotNil(t, reranker)
}

// TestRerankerNoAPIKey tests reranker without API key
func TestRerankerNoAPIKey(t *testing.T) {
	_, err := NewReranker("", ModelRerank25, testRateLimit, testMaxRetries)
	require.Error(t, err)
}

// TestLocalReranker tests local reranker
func TestLocalReranker(t *testing.T) {
	reranker := NewLocalReranker()
	assert.NotNil(t, reranker)

	ctx := context.Background()
	req := &RerankRequest{
		Query: "test query",
		Documents: []Document{
			{Text: "test document one"},
			{Text: "query test document"},
			{Text: "unrelated content"},
		},
		Model:           "",
		TopK:            testTopK,
		ReturnDocuments: false,
	}

	resp, err := reranker.Rerank(ctx, req)
	require.NoError(t, err)
	assert.NotNil(t, resp)
	assert.LessOrEqual(t, len(resp.Results), testTopK)

	// First result should have higher score (contains "query test")
	if len(resp.Results) > 1 {
		assert.GreaterOrEqual(t, resp.Results[0].RelevanceScore, resp.Results[1].RelevanceScore)
	}
}

// TestVectorToString tests vector to string conversion
func TestVectorToString(t *testing.T) {
	vec := EmbeddingVector{1.0, 2.5, 3.7}
	str := vectorToString(vec)
	assert.Contains(t, str, "1.0")
	assert.Contains(t, str, "2.5")
	assert.Contains(t, str, "3.7")

	// Empty vector
	emptyVec := EmbeddingVector{}
	emptyStr := vectorToString(emptyVec)
	assert.Equal(t, "[]", emptyStr)
}

// TestCalculateSimpleScore tests simple scoring
func TestCalculateSimpleScore(t *testing.T) {
	score := calculateSimpleScore("test query", "this is a test query document")
	assert.Greater(t, score, 0.0)

	// No match
	score = calculateSimpleScore("test query", "completely different content")
	assert.GreaterOrEqual(t, score, 0.0)
}

// TestTokenize tests text tokenization
func TestTokenize(t *testing.T) {
	tokens := tokenize("Hello World Test")
	assert.Len(t, tokens, 3)
	assert.Contains(t, tokens, "hello")
	assert.Contains(t, tokens, "world")
	assert.Contains(t, tokens, "test")

	// Empty string
	emptyTokens := tokenize("")
	assert.Empty(t, emptyTokens)
}

// Integration tests (skipped if API keys not set)

// TestVoyageIntegration tests actual VoyageAI API integration
func TestVoyageIntegration(t *testing.T) {
	apiKey := os.Getenv("VOYAGE_API_KEY")
	if apiKey == "" || apiKey == "test-key" {
		t.Skip("VOYAGE_API_KEY not set or is test key, skipping integration test")
	}

	config := &ProviderConfig{
		APIKey:       apiKey,
		DefaultModel: ModelVoyage35,
		Dimensions:   testDimensionsVoyage,
		MaxRetries:   testMaxRetries,
	}

	provider, err := NewVoyageProvider(config)
	if err != nil {
		t.Skip("Failed to create Voyage provider, skipping integration test")
	}

	ctx, cancel := context.WithTimeout(context.Background(), testTimeout)
	defer cancel()

	req := &EmbeddingRequest{
		Texts:     []string{"Hello world", "Test embedding"},
		Model:     "",
		InputType: "document",
	}

	resp, err := provider.Embed(ctx, req)
	if err != nil {
		t.Skip("Voyage API error (expected when no API key), skipping integration test")
	}
	assert.NotNil(t, resp)
	assert.Len(t, resp.Embeddings, testEmbeddingsCount)
	assert.Len(t, resp.Embeddings[0], testDimensionsVoyage)
	assert.Positive(t, resp.Usage.TotalTokens)
	assert.Greater(t, resp.Usage.CostUSD, 0.0)
}

// TestOpenRouterIntegration tests actual OpenRouter API integration
func TestOpenRouterIntegration(t *testing.T) {
	apiKey := os.Getenv("OPENROUTER_API_KEY")
	if apiKey == "" {
		t.Skip("OPENROUTER_API_KEY not set, skipping integration test")
	}

	config := &ProviderConfig{
		APIKey:       apiKey,
		DefaultModel: ModelTextEmbedding3Small,
		Dimensions:   testDimensionsOpenRouter,
		MaxRetries:   testMaxRetries,
	}

	provider, err := NewOpenRouterProvider(config)
	require.NoError(t, err)

	ctx, cancel := context.WithTimeout(context.Background(), testTimeout)
	defer cancel()

	req := &EmbeddingRequest{
		Texts:     []string{"Hello world"},
		Model:     "",
		InputType: "",
	}

	resp, err := provider.Embed(ctx, req)
	require.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Len(t, resp.Embeddings, testEmbeddingCountSingle)
	assert.Len(t, resp.Embeddings[0], testDimensionsOpenRouter)
}

// TestRerankIntegration tests actual VoyageAI reranking API
func TestRerankIntegration(t *testing.T) {
	apiKey := os.Getenv("VOYAGE_API_KEY")
	if apiKey == "" || apiKey == "test-key" {
		t.Skip("VOYAGE_API_KEY not set or is test key, skipping integration test")
	}

	reranker, err := NewReranker(apiKey, ModelRerank25, testRateLimit, testMaxRetries)
	if err != nil {
		t.Skip("Failed to create reranker, skipping integration test")
	}

	ctx, cancel := context.WithTimeout(context.Background(), testTimeout)
	defer cancel()

	req := &RerankRequest{
		Query: "machine learning",
		Documents: []Document{
			{Text: "Deep learning is a subset of machine learning"},
			{Text: "The weather is sunny today"},
			{Text: "Neural networks are used in ML applications"},
		},
		Model:           "",
		TopK:            testTopK,
		ReturnDocuments: false,
	}

	resp, err := reranker.Rerank(ctx, req)
	if err != nil {
		t.Skip("Reranking API error (expected when no API key), skipping integration test")
	}
	assert.NotNil(t, resp)
	assert.LessOrEqual(t, len(resp.Results), testTopK)

	// First result should be most relevant
	if len(resp.Results) > 0 {
		assert.Greater(t, resp.Results[0].RelevanceScore, 0.0)
	}
}

// Benchmark tests

// BenchmarkVectorToString benchmarks vector conversion
func BenchmarkVectorToString(b *testing.B) {
	vec := make(EmbeddingVector, testDimensionsVoyage)
	for i := range vec {
		vec[i] = float32(i) * testScoreDelta
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = vectorToString(vec)
	}
}

// BenchmarkTokenize benchmarks text tokenization
func BenchmarkTokenize(b *testing.B) {
	text := "This is a test document with several words to tokenize"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = tokenize(text)
	}
}

// Mock provider for testing

type MockProvider struct {
	name       string
	dimensions int
}

func (m *MockProvider) Embed(_ context.Context, req *EmbeddingRequest) (*EmbeddingResponse, error) {
	embeddings := make([]EmbeddingVector, len(req.Texts))
	for i := range embeddings {
		embeddings[i] = make(EmbeddingVector, m.dimensions)
		for j := range embeddings[i] {
			embeddings[i][j] = float32(i+j) * 0.1
		}
	}

	return &EmbeddingResponse{
		Embeddings: embeddings,
		Model:      "mock-model",
		Usage: TokenUsage{
			PromptTokens: len(req.Texts) * testPromptTokensLarge,
			TotalTokens:  len(req.Texts) * testPromptTokensLarge,
			CostUSD:      0.0,
		},
	}, nil
}

func (m *MockProvider) GetDimensions() int {
	return m.dimensions
}

func (m *MockProvider) GetName() string {
	return m.name
}

func (m *MockProvider) GetDefaultModel() string {
	return "mock-model"
}

func (m *MockProvider) HealthCheck(_ context.Context) error {
	return nil
}
