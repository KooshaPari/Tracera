package equivalence

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

// MockEmbeddingProvider implements embeddings.Provider for testing
type MockEmbeddingProvider struct {
	mock.Mock
}

func (m *MockEmbeddingProvider) Embed(
	ctx context.Context,
	req *embeddings.EmbeddingRequest,
) (*embeddings.EmbeddingResponse, error) {
	args := m.Called(ctx, req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*embeddings.EmbeddingResponse)
	return val, args.Error(1)
}

func (m *MockEmbeddingProvider) GetDimensions() int {
	args := m.Called()
	return args.Int(0)
}

func (m *MockEmbeddingProvider) GetName() string {
	args := m.Called()
	return args.String(0)
}

func (m *MockEmbeddingProvider) GetDefaultModel() string {
	args := m.Called()
	return args.String(0)
}

func (m *MockEmbeddingProvider) HealthCheck(ctx context.Context) error {
	args := m.Called(ctx)
	return args.Error(0)
}

// TestSemanticStrategyName returns correct strategy type
func TestSemanticStrategyName(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	// Act
	name := strategy.Name()

	// Assert
	assert.Equal(t, StrategySemanticSimilarity, name)
}

// TestSemanticStrategyDefaultConfidence returns 0.6
func TestSemanticStrategyDefaultConfidence(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	// Act
	confidence := strategy.DefaultConfidence()

	// Assert
	assert.InEpsilon(t, 0.6, confidence, 1e-9)
}

// TestSemanticStrategyRequiresEmbeddings returns true
func TestSemanticStrategyRequiresEmbeddings(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	// Act
	requires := strategy.RequiresEmbeddings()

	// Assert
	assert.True(t, requires)
}

// TestSemanticDetectWithPrecomputedEmbeddings uses provided embeddings
func TestSemanticDetectWithPrecomputedEmbeddings(t *testing.T) {
	// Arrange
	provider := new(MockEmbeddingProvider)
	provider.On("GetDimensions").Return(1024)
	strategy := NewSemanticStrategy(provider)

	projectID := uuid.New()

	// Similar embeddings (high cosine similarity)
	sourceEmbedding := []float32{0.1, 0.2, 0.3, 0.4, 0.5}
	targetEmbedding := []float32{0.1, 0.2, 0.3, 0.4, 0.5}

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Authentication",
		Embedding: sourceEmbedding,
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Authentication",
		Embedding: targetEmbedding,
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, StrategySemanticSimilarity, result.Strategy)
	assert.Len(t, result.Links, 1)
	assert.InDelta(t, 0.8, result.Links[0].Confidence, 0.001) // 0.6 default * (1.0 similarity / 0.75 minSimilarity) = 0.8
}

// TestSemanticDetectGeneratesSourceEmbedding generates embedding if missing
func TestSemanticDetectGeneratesSourceEmbedding(t *testing.T) {
	// Arrange
	provider := new(MockEmbeddingProvider)
	provider.On("GetDimensions").Return(1024)
	provider.On("Embed", mock.Anything, mock.MatchedBy(func(req *embeddings.EmbeddingRequest) bool {
		return len(req.Texts) > 0
	})).Return(&embeddings.EmbeddingResponse{
		Embeddings: []embeddings.EmbeddingVector{
			{0.1, 0.2, 0.3, 0.4, 0.5},
		},
	}, nil)

	strategy := NewSemanticStrategy(provider)

	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Authentication",
		// No embedding provided
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Auth",
		Embedding: []float32{0.1, 0.2, 0.3, 0.4, 0.5},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, StrategySemanticSimilarity, result.Strategy)
	provider.AssertCalled(t, "Embed", mock.Anything, mock.Anything)
}

// TestSemanticDetectSkipsCandidatesWithoutEmbedding skips candidates without embeddings
func TestSemanticDetectSkipsCandidatesWithoutEmbedding(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.1, 0.2, 0.3, 0.4, 0.5},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		// No embedding
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links) // Should skip
}

// TestSemanticDetectHighSimilarity matches high-similarity embeddings
func TestSemanticDetectHighSimilarity(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	// Nearly identical embeddings
	embedding1 := []float32{0.1, 0.2, 0.3, 0.4, 0.5}
	embedding2 := []float32{0.10001, 0.20001, 0.30001, 0.40001, 0.50001}

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding1,
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding2,
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1)
	// Very high similarity should produce confidence near 0.6
	assert.Greater(t, result.Links[0].Confidence, 0.5)
}

// TestSemanticDetectLowSimilarity rejects low-similarity embeddings
func TestSemanticDetectLowSimilarity(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	// Very different embeddings
	embedding1 := []float32{1.0, 0.0, 0.0, 0.0, 0.0}
	embedding2 := []float32{0.0, 0.0, 0.0, 0.0, 1.0}

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding1,
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "Product Catalog",
		Embedding: embedding2,
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links) // No match due to low similarity
}

// TestSemanticDetectExcludesSelfMatch avoids self-matching
func TestSemanticDetectExcludesSelfMatch(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()
	itemID := uuid.New()

	embedding := []float32{0.1, 0.2, 0.3, 0.4, 0.5}

	sourceItem := &StrategyItemInfo{
		ID:        itemID,
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding,
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{sourceItem}, // Source in candidates
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Empty(t, result.Links)
}

// TestSemanticDetectContextCancellation handles cancelled context
func TestSemanticDetectContextCancellation(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.1, 0.2, 0.3},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.1, 0.2, 0.3},
	}

	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	_, err := strategy.Detect(ctx, req)

	// Assert
	require.Error(t, err)
	assert.Equal(t, context.Canceled, err)
}

// TestSemanticDetectNoEmbeddingProvider handles missing provider
func TestSemanticDetectNoEmbeddingProvider(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		// No embedding
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.1, 0.2, 0.3},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Contains(t, result.Error, "no embedding provider")
}

// TestSemanticDetectEmbeddingGenerationError handles provider errors
func TestSemanticDetectEmbeddingGenerationError(t *testing.T) {
	// Arrange
	provider := new(MockEmbeddingProvider)
	provider.On("GetDimensions").Return(1024)
	provider.On("Embed", mock.Anything, mock.Anything).Return(nil, assert.AnError)

	strategy := NewSemanticStrategy(provider)

	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		// No embedding
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.1, 0.2, 0.3},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.NotEmpty(t, result.Error)
}

// TestSemanticDetectMultipleCandidates scans all candidates
func TestSemanticDetectMultipleCandidates(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	sourceEmbedding := []float32{0.1, 0.2, 0.3, 0.4, 0.5}
	similarEmbedding := []float32{0.10001, 0.20001, 0.30001, 0.40001, 0.50001}
	differentEmbedding := []float32{1.0, 0.0, 0.0, 0.0, 0.0}

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: sourceEmbedding,
	}

	candidates := []*StrategyItemInfo{
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "User Service",
			Embedding: similarEmbedding,
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "Product Catalog",
			Embedding: differentEmbedding,
		},
		{
			ID:        uuid.New(),
			ProjectID: projectID,
			Title:     "Service",
			Embedding: similarEmbedding,
		},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: candidates,
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, 3, result.ItemsScanned)
	// Should match the two similar embeddings
	assert.Len(t, result.Links, 2)
}

// TestSemanticDetectZeroEmbedding handles zero embeddings
func TestSemanticDetectZeroEmbedding(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.0, 0.0, 0.0, 0.0},
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.0, 0.0, 0.0, 0.0},
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// Zero vectors have similarity 0 (undefined cosine similarity)
	assert.Empty(t, result.Links)
}

// TestSemanticDetectMismatchedDimensions handles dimension mismatch
func TestSemanticDetectMismatchedDimensions(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.1, 0.2, 0.3}, // 3D
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: []float32{0.1, 0.2, 0.3, 0.4, 0.5}, // 5D
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	// Dimension mismatch should result in no matches
	assert.Empty(t, result.Links)
}

// TestSemanticDetectEvidence validates evidence details
func TestSemanticDetectEvidence(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	embedding := []float32{0.1, 0.2, 0.3, 0.4, 0.5}

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding,
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding,
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1)

	link := result.Links[0]
	assert.NotEmpty(t, link.Evidence)
	assert.Equal(t, StrategySemanticSimilarity, link.Evidence[0].Strategy)
	assert.Contains(t, link.Evidence[0].Details, "cosine_similarity")
	assert.Contains(t, link.Evidence[0].Details, "threshold")
}

// TestCosineSimilarityIdentical vectors have similarity 1.0
func TestCosineSimilarityIdentical(t *testing.T) {
	// Arrange
	a := []float32{1.0, 0.0, 0.0}
	b := []float32{1.0, 0.0, 0.0}

	// Act
	similarity := cosineSimilarity(a, b)

	// Assert
	assert.InEpsilon(t, 1.0, similarity, 1e-9)
}

// TestCosineSimilarityOrthogonal orthogonal vectors have similarity 0.0
func TestCosineSimilarityOrthogonal(t *testing.T) {
	// Arrange
	a := []float32{1.0, 0.0, 0.0}
	b := []float32{0.0, 1.0, 0.0}

	// Act
	similarity := cosineSimilarity(a, b)

	// Assert
	assert.InDelta(t, 0.0, similarity, 1e-9)
}

// TestCosineSimilarityOpposite opposite vectors have similarity -1.0
func TestCosineSimilarityOpposite(t *testing.T) {
	// Arrange
	a := []float32{1.0, 0.0, 0.0}
	b := []float32{-1.0, 0.0, 0.0}

	// Act
	similarity := cosineSimilarity(a, b)

	// Assert
	assert.InEpsilon(t, -1.0, similarity, 1e-9)
}

// TestCosineSimilarityDimensionMismatch returns 0 for mismatched dimensions
func TestCosineSimilarityDimensionMismatch(t *testing.T) {
	// Arrange
	a := []float32{1.0, 0.0, 0.0}
	b := []float32{1.0, 0.0}

	// Act
	similarity := cosineSimilarity(a, b)

	// Assert
	assert.InDelta(t, 0.0, similarity, 1e-9)
}

// TestCosineSimilarityEmptyVector returns 0 for empty vectors
func TestCosineSimilarityEmptyVector(t *testing.T) {
	// Arrange
	a := []float32{}
	b := []float32{1.0, 0.0}

	// Act
	similarity := cosineSimilarity(a, b)

	// Assert
	assert.InDelta(t, 0.0, similarity, 1e-9)
}

// TestCosineSimilarityZeroNorm returns 0 when denominator is zero
func TestCosineSimilarityZeroNorm(t *testing.T) {
	// Arrange
	a := []float32{0.0, 0.0, 0.0}
	b := []float32{1.0, 0.0, 0.0}

	// Act
	similarity := cosineSimilarity(a, b)

	// Assert
	assert.InDelta(t, 0.0, similarity, 1e-9)
}

// TestSemanticDetectConfidenceCapping caps confidence at 0.95
func TestSemanticDetectConfidenceCapping(t *testing.T) {
	// Arrange
	strategy := NewSemanticStrategy(nil)

	projectID := uuid.New()

	// Identical embeddings
	embedding := []float32{0.1, 0.2, 0.3, 0.4, 0.5}

	sourceItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding,
	}

	targetItem := &StrategyItemInfo{
		ID:        uuid.New(),
		ProjectID: projectID,
		Title:     "User Service",
		Embedding: embedding,
	}

	req := &StrategyDetectionRequest{
		ProjectID:     projectID,
		SourceItem:    sourceItem,
		CandidatePool: []*StrategyItemInfo{targetItem},
	}

	// Act
	result, err := strategy.Detect(context.Background(), req)

	// Assert
	require.NoError(t, err)
	assert.Len(t, result.Links, 1)
	// Confidence should be capped at 0.95
	assert.LessOrEqual(t, result.Links[0].Confidence, 0.95)
}
