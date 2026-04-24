package embeddings

import (
	"context"
	"errors"
	"fmt"
)

// EmbeddingVector represents a single embedding vector
type EmbeddingVector []float32

// EmbeddingRequest represents a request to generate embeddings
type EmbeddingRequest struct {
	Texts     []string // Input texts to embed
	Model     string   // Model to use (optional, uses default if empty)
	InputType string   // Input type hint: "document", "query", etc.
}

// EmbeddingResponse represents the response from an embedding API
type EmbeddingResponse struct {
	Embeddings []EmbeddingVector // Generated embeddings
	Model      string            // Model used
	Usage      TokenUsage        // Token usage statistics
}

// TokenUsage represents token usage statistics
type TokenUsage struct {
	PromptTokens int     // Number of input tokens
	TotalTokens  int     // Total tokens processed
	CostUSD      float64 // Estimated cost in USD
}

// Provider defines the interface for embedding providers
type Provider interface {
	// Embed generates embeddings for the given texts
	Embed(ctx context.Context, req *EmbeddingRequest) (*EmbeddingResponse, error)

	// GetDimensions returns the dimensionality of embeddings produced by this provider
	GetDimensions() int

	// GetName returns the name of this provider
	GetName() string

	// GetDefaultModel returns the default model for this provider
	GetDefaultModel() string

	// HealthCheck verifies the provider is accessible
	HealthCheck(ctx context.Context) error
}

// ProviderType represents the type of embedding provider
type ProviderType string

// Provider type identifiers.
const (
	ProviderVoyage     ProviderType = "voyage"
	ProviderOpenRouter ProviderType = "openrouter"
	ProviderLocal      ProviderType = "local"
)

// ProviderConfig holds configuration for embedding providers
type ProviderConfig struct {
	Type               ProviderType
	APIKey             string
	DefaultModel       string
	Dimensions         int
	RateLimitPerMinute int
	TimeoutSeconds     int
	MaxRetries         int
	MaxBatchSize       int
}

// ProviderFactory creates embedding providers based on configuration
type ProviderFactory struct {
	providers map[ProviderType]Provider
}

// NewProviderFactory creates a new provider factory
func NewProviderFactory() *ProviderFactory {
	return &ProviderFactory{
		providers: make(map[ProviderType]Provider),
	}
}

// Register registers a provider with the factory
func (f *ProviderFactory) Register(providerType ProviderType, provider Provider) {
	f.providers[providerType] = provider
}

// Get retrieves a provider by type
func (f *ProviderFactory) Get(providerType ProviderType) (Provider, error) {
	provider, ok := f.providers[providerType]
	if !ok {
		return nil, fmt.Errorf("provider type %s not registered", providerType)
	}
	return provider, nil
}

// CreateProvider creates a provider based on configuration
func CreateProvider(config *ProviderConfig) (Provider, error) {
	switch config.Type {
	case ProviderVoyage:
		return NewVoyageProvider(config)
	case ProviderOpenRouter:
		return NewOpenRouterProvider(config)
	case ProviderLocal:
		return nil, errors.New("local provider not yet implemented")
	default:
		return nil, fmt.Errorf("unsupported provider type: %s", config.Type)
	}
}

// BatchRequest splits a large embedding request into batches
func BatchRequest(texts []string, batchSize int) [][]string {
	if batchSize <= 0 {
		batchSize = 128 // Default batch size
	}

	var batches [][]string
	for i := 0; i < len(texts); i += batchSize {
		end := i + batchSize
		if end > len(texts) {
			end = len(texts)
		}
		batches = append(batches, texts[i:end])
	}
	return batches
}

// MergeResponses merges multiple embedding responses into one
func MergeResponses(responses []*EmbeddingResponse) *EmbeddingResponse {
	if len(responses) == 0 {
		return &EmbeddingResponse{
			Embeddings: nil,
			Model:      "",
			Usage:      TokenUsage{},
		}
	}

	merged := &EmbeddingResponse{
		Embeddings: make([]EmbeddingVector, 0),
		Model:      responses[0].Model,
		Usage:      TokenUsage{},
	}

	for _, resp := range responses {
		merged.Embeddings = append(merged.Embeddings, resp.Embeddings...)
		merged.Usage.PromptTokens += resp.Usage.PromptTokens
		merged.Usage.TotalTokens += resp.Usage.TotalTokens
		merged.Usage.CostUSD += resp.Usage.CostUSD
	}

	return merged
}

// ValidateEmbeddings checks if embeddings are valid
func ValidateEmbeddings(embeddings []EmbeddingVector, expectedDim int) error {
	if len(embeddings) == 0 {
		return errors.New("no embeddings provided")
	}

	for i, emb := range embeddings {
		if len(emb) != expectedDim {
			return fmt.Errorf("embedding %d has dimension %d, expected %d", i, len(emb), expectedDim)
		}

		// Check for NaN or Inf values
		for j, val := range emb {
			if val != val { // NaN check
				return fmt.Errorf("embedding %d contains NaN at position %d", i, j)
			}
		}
	}

	return nil
}
