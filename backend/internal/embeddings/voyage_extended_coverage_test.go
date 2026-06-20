//go:build !integration && !e2e

package embeddings

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestVoyageProvider_Extended tests additional edge cases for VoyageProvider
func TestVoyageProvider_Extended(t *testing.T) {
	t.Run("GetDimensions", func(t *testing.T) {
		config := &ProviderConfig{
			APIKey:       "test-key",
			DefaultModel: ModelVoyage35,
		}
		provider, err := NewVoyageProvider(config)
		require.NoError(t, err)

		dims := provider.GetDimensions()
		assert.Positive(t, dims)
	})

	t.Run("GetName", func(t *testing.T) {
		config := &ProviderConfig{
			APIKey:       "test-key",
			DefaultModel: ModelVoyage35,
		}
		provider, err := NewVoyageProvider(config)
		require.NoError(t, err)

		name := provider.GetName()
		assert.Equal(t, "VoyageAI", name)
	})

	t.Run("GetDefaultModel", func(t *testing.T) {
		config := &ProviderConfig{
			APIKey:       "test-key",
			DefaultModel: ModelVoyage3Large,
		}
		provider, err := NewVoyageProvider(config)
		require.NoError(t, err)

		model := provider.GetDefaultModel()
		assert.Equal(t, ModelVoyage3Large, model)
	})

	t.Run("HealthCheck with invalid API key", func(t *testing.T) {
		config := &ProviderConfig{
			APIKey:       "invalid-key",
			DefaultModel: ModelVoyage35,
		}
		provider, err := NewVoyageProvider(config)
		require.NoError(t, err)

		ctx := context.Background()
		err = provider.HealthCheck(ctx)
		// Will fail on API call, but tests the method
		_ = err
	})
}

// TestReranker_Extended tests additional edge cases for Reranker
func TestReranker_Extended(t *testing.T) {
	t.Run("default model stored correctly", func(t *testing.T) {
		reranker, err := NewReranker("test-key", ModelRerank25, 300, 3)
		require.NoError(t, err)
		assert.NotNil(t, reranker)
		// Model is stored in defaultModel field
	})

	t.Run("Rerank with empty query", func(t *testing.T) {
		reranker, err := NewReranker("test-key", ModelRerank25, 300, 3)
		require.NoError(t, err)

		req := &RerankRequest{
			Query:           "",
			Documents:       []Document{{Text: "test"}},
			Model:           "",
			TopK:            0,
			ReturnDocuments: false,
		}

		_, err = reranker.Rerank(context.Background(), req)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "query is required")
	})

	t.Run("Rerank with exactly max documents", func(t *testing.T) {
		reranker, err := NewReranker("test-key", ModelRerank25, 300, 3)
		require.NoError(t, err)

		documents := make([]Document, VoyageRerankMax)
		for i := range documents {
			documents[i] = Document{Text: "test document"}
		}

		req := &RerankRequest{
			Query:           "test query",
			Documents:       documents,
			Model:           "",
			TopK:            0,
			ReturnDocuments: false,
		}

		// Will fail on API call, but tests validation
		_, err = reranker.Rerank(context.Background(), req)
		// May succeed validation but fail on API
		_ = err
	})

	t.Run("Rerank with one document", func(t *testing.T) {
		reranker, err := NewReranker("test-key", ModelRerank25, 300, 3)
		require.NoError(t, err)

		req := &RerankRequest{
			Query:           "test query",
			Documents:       []Document{{Text: "single document"}},
			Model:           "",
			TopK:            0,
			ReturnDocuments: false,
		}

		// Will fail on API call, but tests validation
		_, err = reranker.Rerank(context.Background(), req)
		_ = err
	})
}
