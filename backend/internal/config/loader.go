package config

import (
	"log/slog"

	"github.com/joho/godotenv"

	"github.com/kooshapari/tracertm-backend/internal/env"
)

// LoadWithEnvManager loads configuration using the environment manager
func LoadWithEnvManager() (*Config, error) {
	// Load .env file if it exists
	if err := godotenv.Load(); err != nil {
		slog.Warn("⚠️ Warning", "error", err)
	}

	// Create environment manager
	envMgr := env.New()
	envMgr.Load()

	// Validate required variables
	requiredVars := []string{
		"DATABASE_URL",
		"REDIS_URL",
		"NATS_URL",
	}
	if err := envMgr.Validate(requiredVars); err != nil {
		slog.Warn("⚠️ Warning", "error", err)
	}

	// Load configuration into the shared Config struct used by the backend.
	// This keeps the env-manager path consistent with LoadConfig().
	cfg := &Config{
		// Application
		Env:  envMgr.GetOrDefault("ENV", envMgr.GetOrDefault("APP_ENV", "development")),
		Port: envMgr.GetOrDefault("PORT", envMgr.GetOrDefault("APP_PORT", "8080")),

		// Database
		DatabaseURL: envMgr.GetOrDefault("DATABASE_URL", ""),

		// JWT
		JWTSecret: envMgr.GetOrDefault("JWT_SECRET", ""),

		// NATS
		NATSUrl:   envMgr.GetOrDefault("NATS_URL", "nats://localhost:4222"),
		NATSCreds: envMgr.GetOrDefault("NATS_CREDS", ""),

		// Redis
		RedisURL:              envMgr.GetOrDefault("REDIS_URL", ""),
		UpstashRedisRestURL:   envMgr.GetOrDefault("UPSTASH_REDIS_REST_URL", ""),
		UpstashRedisRestToken: envMgr.GetOrDefault("UPSTASH_REDIS_REST_TOKEN", ""),

		// Neo4j
		Neo4jURI:      envMgr.GetOrDefault("NEO4J_URI", "neo4j://localhost:7687"),
		Neo4jUser:     envMgr.GetOrDefault("NEO4J_USER", "neo4j"),
		Neo4jPassword: envMgr.GetOrDefault("NEO4J_PASSWORD", ""),

		// WorkOS
		WorkOSClientID: envMgr.GetOrDefault("WORKOS_CLIENT_ID", ""),
		WorkOSAPIKey:   envMgr.GetOrDefault("WORKOS_API_KEY", ""),

		// Embeddings
		Embeddings: EmbeddingsConfig{
			Provider:            envMgr.GetOrDefault("EMBEDDING_PROVIDER", "voyage"),
			VoyageAPIKey:        envMgr.GetOrDefault("VOYAGE_API_KEY", ""),
			VoyageModel:         envMgr.GetOrDefault("VOYAGE_MODEL", "voyage-3.5"),
			VoyageDimensions:    envMgr.GetIntOrDefault("VOYAGE_DIMENSIONS", defaultVoyageDimensions),
			OpenRouterAPIKey:    envMgr.GetOrDefault("OPENROUTER_API_KEY", ""),
			OpenRouterModel:     envMgr.GetOrDefault("OPENROUTER_MODEL", "openai/text-embedding-3-small"),
			RerankEnabled:       envMgr.GetBoolOrDefault("RERANK_ENABLED", true),
			RerankModel:         envMgr.GetOrDefault("RERANK_MODEL", "rerank-2.5"),
			RateLimitPerMinute:  envMgr.GetIntOrDefault("EMBEDDING_RATE_LIMIT", defaultEmbeddingRateLimit),
			TimeoutSeconds:      envMgr.GetIntOrDefault("EMBEDDING_TIMEOUT", defaultEmbeddingTimeout),
			MaxRetries:          envMgr.GetIntOrDefault("EMBEDDING_MAX_RETRIES", defaultEmbeddingMaxRetries),
			MaxBatchSize:        envMgr.GetIntOrDefault("EMBEDDING_BATCH_SIZE", defaultEmbeddingBatchSize),
			IndexerEnabled:      envMgr.GetBoolOrDefault("INDEXER_ENABLED", true),
			IndexerWorkers:      envMgr.GetIntOrDefault("INDEXER_WORKERS", defaultIndexerWorkers),
			IndexerBatchSize:    envMgr.GetIntOrDefault("INDEXER_BATCH_SIZE", defaultIndexerBatchSize),
			IndexerPollInterval: envMgr.GetIntOrDefault("INDEXER_POLL_INTERVAL", defaultIndexerPollInterval),
		},
	}

	return cfg, nil
}
