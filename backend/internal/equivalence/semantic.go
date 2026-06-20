package equivalence

import (
	"context"
	"math"
	"time"

	"github.com/google/uuid"

	"github.com/kooshapari/tracertm-backend/internal/embeddings"
)

const (
	semanticDefaultDimensions = 1024
	semanticMinSimilarity     = 0.75
	semanticDefaultConfidence = 0.6
	semanticConfidenceCap     = 0.95
)

// SemanticStrategy detects equivalences based on embedding similarity
type SemanticStrategy struct {
	provider      embeddings.Provider
	minSimilarity float64
	embeddingDim  int
}

// NewSemanticStrategy creates a new semantic similarity strategy
func NewSemanticStrategy(provider embeddings.Provider) *SemanticStrategy {
	dim := semanticDefaultDimensions // Default dimension
	if provider != nil {
		dim = provider.GetDimensions()
	}
	return &SemanticStrategy{
		provider:      provider,
		minSimilarity: semanticMinSimilarity, // Cosine similarity threshold
		embeddingDim:  dim,
	}
}

// Name returns the strategy identifier.
func (strategy *SemanticStrategy) Name() StrategyType {
	return StrategySemanticSimilarity
}

// DefaultConfidence returns the base confidence for semantic matchestrategy.
func (strategy *SemanticStrategy) DefaultConfidence() float64 {
	return semanticDefaultConfidence
}

// RequiresEmbeddings reports whether this strategy needs embeddings.
func (strategy *SemanticStrategy) RequiresEmbeddings() bool {
	return true
}

// Detect finds candidate links using embedding similarity.
func (strategy *SemanticStrategy) Detect(ctx context.Context, req *StrategyDetectionRequest) (*DetectionResult, error) {
	start := time.Now()
	result := newDetectionResult(strategy.Name())
	sourceEmbedding, errMsg := strategy.getSourceEmbedding(ctx, req)
	if errMsg != "" {
		result.Error = errMsg
		finalizeDetectionResult(result, start)
		// Swallow provider/embedding errors so other strategies can still run; surfaced via result.Error.
		return result, nil
	}
	if len(sourceEmbedding) == 0 {
		finalizeDetectionResult(result, start)
		return result, nil
	}

	for _, candidate := range req.CandidatePool {
		if err := checkContext(ctx, result); err != nil {
			return result, err
		}

		if candidate.ID == req.SourceItem.ID {
			continue
		}
		result.ItemsScanned++

		candidateEmbedding := candidate.Embedding
		if len(candidateEmbedding) == 0 {
			continue // Skip candidates without embeddings
		}

		similarity := cosineSimilarity(sourceEmbedding, candidateEmbedding)
		if similarity >= strategy.minSimilarity {
			result.Links = append(result.Links, strategy.buildLink(req, candidate, similarity))
		}
	}

	finalizeDetectionResult(result, start)
	return result, nil
}

func (strategy *SemanticStrategy) getSourceEmbedding(
	ctx context.Context,
	req *StrategyDetectionRequest,
) ([]float32, string) {
	if len(req.SourceItem.Embedding) > 0 {
		return req.SourceItem.Embedding, ""
	}
	if strategy.provider == nil {
		return nil, "no embedding provider available"
	}

	resp, err := strategy.provider.Embed(ctx, &embeddings.EmbeddingRequest{
		Texts:     []string{req.SourceItem.Title + " " + req.SourceItem.Description},
		Model:     "",
		InputType: "document",
	})
	if err != nil {
		return nil, err.Error()
	}
	if len(resp.Embeddings) == 0 {
		return nil, ""
	}

	return resp.Embeddings[0], ""
}

func (strategy *SemanticStrategy) buildLink(
	req *StrategyDetectionRequest,
	candidate *StrategyItemInfo,
	similarity float64,
) Link {
	confidence := strategy.computeConfidence(similarity)
	now := time.Now()

	return Link{
		ID:           uuid.New(),
		ProjectID:    req.ProjectID,
		SourceItemID: req.SourceItem.ID,
		TargetItemID: candidate.ID,
		LinkType:     "same_as",
		Confidence:   confidence,
		Provenance:   strategy.Name(),
		Status:       StatusSuggested,
		Evidence: []Evidence{{
			Strategy:    strategy.Name(),
			Confidence:  confidence,
			Description: "Semantic similarity detected via embeddings",
			Details: map[string]any{
				"cosine_similarity": similarity,
				"threshold":         strategy.minSimilarity,
			},
			DetectedAt: now,
		}},
		CreatedAt: now,
		UpdatedAt: now,
	}
}

func (strategy *SemanticStrategy) computeConfidence(similarity float64) float64 {
	confidence := strategy.DefaultConfidence() * (similarity / strategy.minSimilarity)
	if confidence > semanticConfidenceCap {
		return semanticConfidenceCap
	}

	return confidence
}

// cosineSimilarity calculates the cosine similarity between two vectors
func cosineSimilarity(vectorA, vectorB []float32) float64 {
	if len(vectorA) != len(vectorB) || len(vectorA) == 0 {
		return 0.0
	}

	var dotProduct, normA, normB float64
	for i := range vectorA {
		dotProduct += float64(vectorA[i]) * float64(vectorB[i])
		normA += float64(vectorA[i]) * float64(vectorA[i])
		normB += float64(vectorB[i]) * float64(vectorB[i])
	}

	if normA == 0 || normB == 0 {
		return 0.0
	}

	return dotProduct / (math.Sqrt(normA) * math.Sqrt(normB))
}
