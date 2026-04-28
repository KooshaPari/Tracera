package embeddings

import (
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/kooshapari/tracertm-backend/internal/config"
)

const (
	indexerRetryDelay   = 5 * time.Second
	indexerMaxQueueSize = 1000
)

// InitializeFromConfig creates embedding provider and reranker from config
func InitializeFromConfig(cfg *config.Config) (Provider, *Reranker, error) {
	provider, err := newProviderFromConfig(cfg)
	if err != nil {
		return nil, nil, err
	}

	reranker, err := newRerankerFromConfig(cfg)
	if err != nil {
		return provider, nil, err
	}

	return provider, reranker, nil
}

func newProviderFromConfig(cfg *config.Config) (Provider, error) {
	switch cfg.Embeddings.Provider {
	case "voyage":
		if cfg.Embeddings.VoyageAPIKey == "" {
			return nil, errors.New("VOYAGE_API_KEY is required when using voyage provider")
		}

		providerConfig := &ProviderConfig{
			Type:               ProviderVoyage,
			APIKey:             cfg.Embeddings.VoyageAPIKey,
			DefaultModel:       cfg.Embeddings.VoyageModel,
			Dimensions:         cfg.Embeddings.VoyageDimensions,
			RateLimitPerMinute: cfg.Embeddings.RateLimitPerMinute,
			TimeoutSeconds:     cfg.Embeddings.TimeoutSeconds,
			MaxRetries:         cfg.Embeddings.MaxRetries,
			MaxBatchSize:       cfg.Embeddings.MaxBatchSize,
		}

		provider, err := NewVoyageProvider(providerConfig)
		if err != nil {
			return nil, fmt.Errorf("failed to create VoyageAI provider: %w", err)
		}

		return provider, nil

	case "openrouter":
		if cfg.Embeddings.OpenRouterAPIKey == "" {
			return nil, errors.New("OPENROUTER_API_KEY is required when using openrouter provider")
		}

		providerConfig := &ProviderConfig{
			Type:               ProviderOpenRouter,
			APIKey:             cfg.Embeddings.OpenRouterAPIKey,
			DefaultModel:       cfg.Embeddings.OpenRouterModel,
			RateLimitPerMinute: cfg.Embeddings.RateLimitPerMinute,
			TimeoutSeconds:     cfg.Embeddings.TimeoutSeconds,
			MaxRetries:         cfg.Embeddings.MaxRetries,
			MaxBatchSize:       cfg.Embeddings.MaxBatchSize,
		}

		provider, err := NewOpenRouterProvider(providerConfig)
		if err != nil {
			return nil, fmt.Errorf("failed to create OpenRouter provider: %w", err)
		}

		return provider, nil

	case "local":
		return nil, errors.New("local provider not yet implemented")

	default:
		return nil, fmt.Errorf("unsupported embedding provider: %s", cfg.Embeddings.Provider)
	}
}

func newRerankerFromConfig(cfg *config.Config) (*Reranker, error) {
	if !cfg.Embeddings.RerankEnabled {
		return nil, nil
	}

	if cfg.Embeddings.VoyageAPIKey == "" {
		return nil, errors.New("VOYAGE_API_KEY is required for reranking")
	}

	reranker, err := NewReranker(
		cfg.Embeddings.VoyageAPIKey,
		cfg.Embeddings.RerankModel,
		cfg.Embeddings.RateLimitPerMinute,
		cfg.Embeddings.MaxRetries,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create reranker: %w", err)
	}

	return reranker, nil
}

// InitializeIndexer creates and starts the background indexer
func InitializeIndexer(cfg *config.Config, pool *pgxpool.Pool, provider Provider) (*Indexer, error) {
	if !cfg.Embeddings.IndexerEnabled {
		return nil, nil // Indexer disabled
	}

	if provider == nil {
		return nil, errors.New("provider is required for indexer")
	}

	if pool == nil {
		return nil, errors.New("database pool is required for indexer")
	}

	indexerConfig := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     cfg.Embeddings.IndexerBatchSize,
		WorkerCount:   cfg.Embeddings.IndexerWorkers,
		PollInterval:  time.Duration(cfg.Embeddings.IndexerPollInterval) * time.Second,
		RetryAttempts: cfg.Embeddings.MaxRetries,
		RetryDelay:    indexerRetryDelay,
		MaxQueueSize:  indexerMaxQueueSize,
		EnableLogging: cfg.Env == "development",
	}

	indexer, err := NewIndexer(indexerConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create indexer: %w", err)
	}

	// Start indexer
	if err := indexer.Start(); err != nil {
		return nil, fmt.Errorf("failed to start indexer: %w", err)
	}

	return indexer, nil
}

// SetupEmbeddings is a convenience function to set up everything
func SetupEmbeddings(cfg *config.Config, pool *pgxpool.Pool) (Provider, *Reranker, *Indexer, error) {
	// Initialize provider and reranker
	provider, reranker, err := InitializeFromConfig(cfg)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to initialize embeddings: %w", err)
	}

	// Initialize indexer
	indexer, err := InitializeIndexer(cfg, pool, provider)
	if err != nil {
		return provider, reranker, nil, fmt.Errorf("failed to initialize indexer: %w", err)
	}

	return provider, reranker, indexer, nil
}
