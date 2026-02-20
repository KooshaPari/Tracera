package embeddings

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/config"
)

func TestInitializeFromConfig(t *testing.T) {
	for _, tt := range initFromConfigCases() {
		t.Run(tt.name, func(t *testing.T) {
			provider, reranker, err := InitializeFromConfig(tt.cfg)
			tt.assertFn(t, provider, reranker, err)
		})
	}
}

type initFromConfigCase struct {
	name     string
	cfg      *config.Config
	assertFn func(*testing.T, Provider, *Reranker, error)
}

func initFromConfigCases() []initFromConfigCase {
	cases := make([]initFromConfigCase, 0, 8)
	cases = append(cases, voyageProviderCases()...)
	cases = append(cases, openRouterProviderCases()...)
	cases = append(cases, otherProviderCases()...)
	cases = append(cases, rerankerCases()...)
	return cases
}

func voyageProviderCases() []initFromConfigCase {
	return []initFromConfigCase{
		{
			name: "voyage provider",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider:         "voyage",
					VoyageAPIKey:     "test-key",
					VoyageModel:      ModelVoyage35,
					VoyageDimensions: 1024,
				},
			},
			assertFn: func(t *testing.T, provider Provider, reranker *Reranker, err error) {
				require.NoError(t, err)
				assert.NotNil(t, provider)
				assert.Nil(t, reranker)
				assert.Equal(t, "VoyageAI", provider.GetName())
			},
		},
		{
			name: "voyage provider without API key",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider: "voyage",
				},
			},
			assertFn: func(t *testing.T, _ Provider, _ *Reranker, err error) {
				require.Error(t, err)
				assert.Contains(t, err.Error(), "VOYAGE_API_KEY is required")
			},
		},
	}
}

func openRouterProviderCases() []initFromConfigCase {
	return []initFromConfigCase{
		{
			name: "openrouter provider",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider:         "openrouter",
					OpenRouterAPIKey: "test-key",
					OpenRouterModel:  ModelTextEmbedding3Small,
				},
			},
			assertFn: func(t *testing.T, provider Provider, reranker *Reranker, err error) {
				require.NoError(t, err)
				assert.NotNil(t, provider)
				assert.Nil(t, reranker)
				assert.Equal(t, "OpenRouter", provider.GetName())
			},
		},
		{
			name: "openrouter provider without API key",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider: "openrouter",
				},
			},
			assertFn: func(t *testing.T, _ Provider, _ *Reranker, err error) {
				require.Error(t, err)
				assert.Contains(t, err.Error(), "OPENROUTER_API_KEY is required")
			},
		},
	}
}

func otherProviderCases() []initFromConfigCase {
	return []initFromConfigCase{
		{
			name: "local provider not implemented",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider: "local",
				},
			},
			assertFn: func(t *testing.T, _ Provider, _ *Reranker, err error) {
				require.Error(t, err)
				assert.Contains(t, err.Error(), "not yet implemented")
			},
		},
		{
			name: "unsupported provider",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider: "unknown",
				},
			},
			assertFn: func(t *testing.T, _ Provider, _ *Reranker, err error) {
				require.Error(t, err)
				assert.Contains(t, err.Error(), "unsupported embedding provider")
			},
		},
	}
}

func rerankerCases() []initFromConfigCase {
	return []initFromConfigCase{
		{
			name: "with reranker enabled",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider:      "voyage",
					VoyageAPIKey:  "test-key",
					RerankEnabled: true,
					RerankModel:   ModelRerank25,
				},
			},
			assertFn: func(t *testing.T, provider Provider, reranker *Reranker, err error) {
				require.NoError(t, err)
				assert.NotNil(t, provider)
				assert.NotNil(t, reranker)
			},
		},
		{
			name: "reranker enabled without Voyage API key",
			cfg: &config.Config{
				Embeddings: config.EmbeddingsConfig{
					Provider:         "openrouter",
					OpenRouterAPIKey: "test-key",
					RerankEnabled:    true,
				},
			},
			assertFn: func(t *testing.T, provider Provider, reranker *Reranker, err error) {
				assert.NotNil(t, provider)
				assert.Nil(t, reranker)
				require.Error(t, err)
				assert.Contains(t, err.Error(), "VOYAGE_API_KEY is required for reranking")
			},
		},
	}
}

func TestInitializeIndexer(t *testing.T) {
	t.Run("indexer disabled", func(t *testing.T) {
		cfg := &config.Config{
			Embeddings: config.EmbeddingsConfig{
				IndexerEnabled: false,
			},
		}

		mockProvider := &MockProvider{
			name:       "test",
			dimensions: 1024,
		}

		indexer, err := InitializeIndexer(cfg, nil, mockProvider)
		require.NoError(t, err)
		assert.Nil(t, indexer) // Should return nil when disabled
	})

	t.Run("error when provider is nil", func(t *testing.T) {
		cfg := &config.Config{
			Embeddings: config.EmbeddingsConfig{
				IndexerEnabled: true,
			},
		}

		_, err := InitializeIndexer(cfg, nil, nil)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "provider is required")
	})

	t.Run("error when pool is nil", func(t *testing.T) {
		cfg := &config.Config{
			Embeddings: config.EmbeddingsConfig{
				IndexerEnabled: true,
			},
		}

		mockProvider := &MockProvider{
			name:       "test",
			dimensions: 1024,
		}

		_, err := InitializeIndexer(cfg, nil, mockProvider)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "database pool is required")
	})
}

func TestSetupEmbeddings(t *testing.T) {
	t.Run("full setup", func(t *testing.T) {
		cfg := &config.Config{
			Embeddings: config.EmbeddingsConfig{
				Provider:       "voyage",
				VoyageAPIKey:   "test-key",
				IndexerEnabled: false, // Disable indexer to avoid pool requirement
			},
		}

		provider, reranker, indexer, err := SetupEmbeddings(cfg, nil)
		require.NoError(t, err)
		assert.NotNil(t, provider)
		assert.Nil(t, reranker)
		assert.Nil(t, indexer) // Disabled
	})

	t.Run("error in provider initialization", func(t *testing.T) {
		cfg := &config.Config{
			Embeddings: config.EmbeddingsConfig{
				Provider: "unknown",
			},
		}

		_, _, _, err := SetupEmbeddings(cfg, nil)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to initialize embeddings")
	})

	t.Run("error in indexer initialization", func(t *testing.T) {
		cfg := &config.Config{
			Embeddings: config.EmbeddingsConfig{
				Provider:       "voyage",
				VoyageAPIKey:   "test-key",
				IndexerEnabled: true,
			},
		}

		// Will fail because pool is nil
		provider, reranker, indexer, err := SetupEmbeddings(cfg, nil)
		// Provider should be created, but indexer will fail
		assert.NotNil(t, provider)
		assert.Nil(t, reranker)
		assert.Nil(t, indexer)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "failed to initialize indexer")
	})
}
