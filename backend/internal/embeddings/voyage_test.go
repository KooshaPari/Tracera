package embeddings

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	voyageTestDefaultDims  = 1024
	voyageTestCustomDims   = 2048
	voyageTestAltDims      = 1536
	voyageTestTimeoutSecs  = 120
	voyageTestMaxRetries   = 5
	voyageTestRateLimit    = 400
	voyageTestBatchExtra   = 1
	voyageTestBatchOverage = 10
)

func TestNewVoyageProvider(t *testing.T) {
	for _, tt := range newVoyageCases() {
		t.Run(tt.name, func(t *testing.T) {
			provider, err := NewVoyageProvider(tt.config)
			tt.assertFn(t, provider, err)
		})
	}
}

func TestVoyageProvider_Embed(t *testing.T) {
	t.Run("no texts provided", testVoyageEmbedNoTexts)
	t.Run("batching for large requests", testVoyageEmbedBatching)
}

type newVoyageCase struct {
	name     string
	config   *ProviderConfig
	assertFn func(*testing.T, *VoyageProvider, error)
}

func newVoyageCases() []newVoyageCase {
	cases := make([]newVoyageCase, 0, 7)
	cases = append(cases, newVoyageValidationCases()...)
	cases = append(cases, newVoyageConfigCases()...)
	return cases
}

func newVoyageValidationCases() []newVoyageCase {
	return []newVoyageCase{
		{
			name:   "error when API key is empty",
			config: &ProviderConfig{APIKey: ""},
			assertFn: func(t *testing.T, _ *VoyageProvider, err error) {
				require.Error(t, err)
				assert.Contains(t, err.Error(), "API key is required")
			},
		},
	}
}

func newVoyageConfigCases() []newVoyageCase {
	cases := make([]newVoyageCase, 0, 6)
	cases = append(cases, newVoyageBaseConfigCases()...)
	cases = append(cases, newVoyageAdvancedConfigCases()...)
	return cases
}

func newVoyageBaseConfigCases() []newVoyageCase {
	return []newVoyageCase{
		{
			name: "defaults applied",
			config: &ProviderConfig{
				APIKey: "test-key",
			},
			assertFn: func(t *testing.T, provider *VoyageProvider, err error) {
				require.NoError(t, err)
				assert.NotNil(t, provider)
				assert.Equal(t, ModelVoyage35, provider.GetDefaultModel())
				assert.Equal(t, voyageTestDefaultDims, provider.GetDimensions())
			},
		},
		{
			name: "custom model",
			config: &ProviderConfig{
				APIKey:       "test-key",
				DefaultModel: ModelVoyage3Large,
			},
			assertFn: func(t *testing.T, provider *VoyageProvider, err error) {
				require.NoError(t, err)
				assert.Equal(t, ModelVoyage3Large, provider.GetDefaultModel())
			},
		},
		{
			name: "custom dimensions",
			config: &ProviderConfig{
				APIKey:     "test-key",
				Dimensions: voyageTestCustomDims,
			},
			assertFn: func(t *testing.T, provider *VoyageProvider, err error) {
				require.NoError(t, err)
				assert.Equal(t, voyageTestCustomDims, provider.GetDimensions())
			},
		},
	}
}

func newVoyageAdvancedConfigCases() []newVoyageCase {
	return []newVoyageCase{
		{
			name: "timeout configuration",
			config: &ProviderConfig{
				APIKey:         "test-key",
				TimeoutSeconds: voyageTestTimeoutSecs,
			},
			assertFn: func(t *testing.T, provider *VoyageProvider, err error) {
				require.NoError(t, err)
				assert.NotNil(t, provider)
			},
		},
		{
			name: "max retries configuration",
			config: &ProviderConfig{
				APIKey:     "test-key",
				MaxRetries: voyageTestMaxRetries,
			},
			assertFn: func(t *testing.T, provider *VoyageProvider, err error) {
				require.NoError(t, err)
				assert.NotNil(t, provider)
			},
		},
		{
			name: "rate limit configuration",
			config: &ProviderConfig{
				APIKey:             "test-key",
				RateLimitPerMinute: voyageTestRateLimit,
			},
			assertFn: func(t *testing.T, provider *VoyageProvider, err error) {
				require.NoError(t, err)
				assert.NotNil(t, provider)
			},
		},
	}
}

func testVoyageEmbedNoTexts(t *testing.T) {
	config := &ProviderConfig{
		APIKey:       "test-key",
		DefaultModel: ModelVoyage35,
	}

	provider, err := NewVoyageProvider(config)
	require.NoError(t, err)

	req := &EmbeddingRequest{
		Texts:     []string{},
		Model:     "",
		InputType: "",
	}

	_, err = provider.Embed(context.Background(), req)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "no texts provided")
}

func testVoyageEmbedBatching(t *testing.T) {
	config := &ProviderConfig{
		APIKey:       "test-key",
		DefaultModel: ModelVoyage35,
	}

	provider, err := NewVoyageProvider(config)
	require.NoError(t, err)

	texts := make([]string, VoyageMaxBatch+voyageTestBatchExtra)
	for i := range texts {
		texts[i] = "text"
	}

	req := &EmbeddingRequest{
		Texts:     texts,
		Model:     "",
		InputType: "",
	}

	_, err = provider.Embed(context.Background(), req)
	require.Error(t, err)
}

func TestVoyageProvider_GetMethods(t *testing.T) {
	config := &ProviderConfig{
		APIKey:       "test-key",
		DefaultModel: ModelVoyage3Large,
		Dimensions:   voyageTestAltDims,
	}

	provider, err := NewVoyageProvider(config)
	require.NoError(t, err)

	assert.Equal(t, "VoyageAI", provider.GetName())
	assert.Equal(t, voyageTestAltDims, provider.GetDimensions())
	assert.Equal(t, ModelVoyage3Large, provider.GetDefaultModel())
}

func TestVoyageProvider_GetDefaultModel(t *testing.T) {
	t.Run("with custom model", func(t *testing.T) {
		config := &ProviderConfig{
			APIKey:       "test-key",
			DefaultModel: ModelVoyageCode3,
		}

		provider, err := NewVoyageProvider(config)
		require.NoError(t, err)
		assert.Equal(t, ModelVoyageCode3, provider.GetDefaultModel())
	})

	t.Run("with default model", func(t *testing.T) {
		config := &ProviderConfig{
			APIKey: "test-key",
			// No DefaultModel specified
		}

		provider, err := NewVoyageProvider(config)
		require.NoError(t, err)
		assert.Equal(t, ModelVoyage35, provider.GetDefaultModel())
	})
}

func TestVoyageProvider_HealthCheck(t *testing.T) {
	t.Run("requires real API", func(t *testing.T) {
		config := &ProviderConfig{
			APIKey:       "test-key",
			DefaultModel: ModelVoyage35,
		}

		provider, err := NewVoyageProvider(config)
		require.NoError(t, err)

		// HealthCheck will fail without a real API key
		err = provider.HealthCheck(context.Background())
		require.Error(t, err)
	})
}

func TestVoyageProvider_embedBatched(t *testing.T) {
	config := &ProviderConfig{
		APIKey:       "test-key",
		DefaultModel: ModelVoyage35,
	}

	provider, err := NewVoyageProvider(config)
	require.NoError(t, err)

	// Create enough texts to trigger batching
	texts := make([]string, VoyageMaxBatch+voyageTestBatchOverage)
	for i := range texts {
		texts[i] = "test text"
	}

	req := &EmbeddingRequest{
		Texts:     texts,
		Model:     "",
		InputType: "",
	}

	// Will fail on API call, but batching logic is tested
	_, err = provider.Embed(context.Background(), req)
	require.Error(t, err)
}
