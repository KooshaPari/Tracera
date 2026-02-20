package embeddings

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestCreateProvider(t *testing.T) {
	t.Run("voyage provider", func(t *testing.T) {
		config := &ProviderConfig{
			Type:   ProviderVoyage,
			APIKey: "test-key",
		}

		provider, err := CreateProvider(config)
		require.NoError(t, err)
		assert.NotNil(t, provider)
		assert.Equal(t, "VoyageAI", provider.GetName())
	})

	t.Run("openrouter provider", func(t *testing.T) {
		config := &ProviderConfig{
			Type:   ProviderOpenRouter,
			APIKey: "test-key",
		}

		provider, err := CreateProvider(config)
		require.NoError(t, err)
		assert.NotNil(t, provider)
		assert.Equal(t, "OpenRouter", provider.GetName())
	})

	t.Run("local provider not implemented", func(t *testing.T) {
		config := &ProviderConfig{
			Type:   ProviderLocal,
			APIKey: "test-key",
		}

		_, err := CreateProvider(config)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "not yet implemented")
	})

	t.Run("unsupported provider type", func(t *testing.T) {
		config := &ProviderConfig{
			Type:   ProviderType("unknown"),
			APIKey: "test-key",
		}

		_, err := CreateProvider(config)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "unsupported provider type")
	})
}

// Note: TestBatchRequest, TestMergeResponses, and TestValidateEmbeddings
// are already defined in embeddings_test.go, so we don't duplicate them here.

func TestProviderFactoryExtended(t *testing.T) {
	t.Run("register multiple providers", func(t *testing.T) {
		factory := NewProviderFactory()
		provider1 := &MockProvider{name: "provider1", dimensions: 512}
		provider2 := &MockProvider{name: "provider2", dimensions: 1024}

		factory.Register(ProviderType("p1"), provider1)
		factory.Register(ProviderType("p2"), provider2)

		p1, err := factory.Get(ProviderType("p1"))
		require.NoError(t, err)
		assert.Equal(t, provider1, p1)

		p2, err := factory.Get(ProviderType("p2"))
		require.NoError(t, err)
		assert.Equal(t, provider2, p2)
	})

	t.Run("override provider", func(t *testing.T) {
		factory := NewProviderFactory()
		provider1 := &MockProvider{name: "provider1", dimensions: 512}
		provider2 := &MockProvider{name: "provider2", dimensions: 1024}

		factory.Register(ProviderType("test"), provider1)
		factory.Register(ProviderType("test"), provider2) // Override

		provider, err := factory.Get(ProviderType("test"))
		require.NoError(t, err)
		assert.Equal(t, provider2, provider)
	})
}
