// Package config provides config functionality.
package config

import (
	"os"
	"strconv"
)

const (
	defaultSentryTracesSampleRate = 0.1
	defaultVoyageDimensions       = 1024
	defaultEmbeddingRateLimit     = 300
	defaultEmbeddingTimeout       = 60
	defaultEmbeddingMaxRetries    = 3
	defaultEmbeddingBatchSize     = 128
	defaultIndexerWorkers         = 3
	defaultIndexerBatchSize       = 50
	defaultIndexerPollInterval    = 30
)

// Config holds application configuration values.
type Config struct {
	// Server
	Port     string
	GRPCPort string
	Env      string

	// Database
	DatabaseURL string

	// JWT
	JWTSecret string

	// CSRF
	CSRFSecret string

	// NATS
	NATSUrl          string
	NATSCreds        string
	NATSUserJWT      string
	NATSUserNkeySeed string

	// Redis-compatible cache
	RedisURL string

	// Upstash Redis-compatible REST API fallback
	UpstashRedisRestURL   string
	UpstashRedisRestToken string

	// Neo4j
	Neo4jURI      string
	Neo4jUser     string
	Neo4jPassword string

	// WorkOS
	WorkOSClientID string
	WorkOSAPIKey   string

	// S3 Storage
	S3Endpoint        string
	S3AccessKeyID     string
	S3SecretAccessKey string
	S3Bucket          string
	S3Region          string

	// Cross-Backend Communication
	PythonBackendURL      string
	PythonBackendGRPCAddr string
	ServiceToken          string

	// Embeddings
	Embeddings EmbeddingsConfig

	// Tracing
	CollectorEndpoint  string
	TracingEnabled     bool
	TracingEnvironment string

	// Sentry Error Tracking
	SentryDSN              string
	SentryEnvironment      string
	SentryRelease          string
	SentryTracesSampleRate float64
	SentryDebug            bool
}

// EmbeddingsConfig holds configuration for embedding providers
type EmbeddingsConfig struct {
	// Provider selection
	Provider string // "voyage", "openrouter", "local"

	// VoyageAI configuration
	VoyageAPIKey     string
	VoyageModel      string // Default: "voyage-3.5"
	VoyageDimensions int    // Default: 1024

	// OpenRouter configuration
	OpenRouterAPIKey string
	OpenRouterModel  string // Default: "openai/text-embedding-3-small"

	// Reranking configuration
	RerankEnabled bool
	RerankModel   string // Default: "rerank-2.5"

	// Performance settings
	RateLimitPerMinute int // Requests per minute
	TimeoutSeconds     int // Request timeout
	MaxRetries         int // Max retry attempts
	MaxBatchSize       int // Max texts per batch

	// Indexer settings
	IndexerEnabled      bool
	IndexerWorkers      int // Number of concurrent workers
	IndexerBatchSize    int // Items per batch
	IndexerPollInterval int // Seconds between polls
}

// LoadConfig reads configuration from environment variables.
func LoadConfig() *Config {
	cfg := &Config{
		Port:                  getEnv("PORT", "8080"),
		GRPCPort:              getEnv("GRPC_PORT", "9091"),
		Env:                   getEnv("ENV", "development"),
		DatabaseURL:           getEnv("DATABASE_URL", "postgres://user:password@localhost:5432/tracertm"),
		JWTSecret:             getEnv("JWT_SECRET", "your-secret-key-change-in-production"),
		CSRFSecret:            getEnv("CSRF_SECRET", ""),
		NATSUrl:               getEnv("NATS_URL", "nats://localhost:4222"),
		NATSCreds:             getEnv("NATS_CREDS", ""),
		NATSUserJWT:           getEnv("NATS_USER_JWT", ""),
		NATSUserNkeySeed:      getEnv("NATS_USER_NKEY_SEED", ""),
		RedisURL:              getEnv("REDIS_URL", "redis://localhost:6379"),
		UpstashRedisRestURL:   getEnv("UPSTASH_REDIS_REST_URL", ""),
		UpstashRedisRestToken: getEnv("UPSTASH_REDIS_REST_TOKEN", ""),
		Neo4jURI:              getEnv("NEO4J_URI", "neo4j://localhost:7687"),
		Neo4jUser:             getEnv("NEO4J_USER", "neo4j"),
		Neo4jPassword:         getEnv("NEO4J_PASSWORD", "password"),
		WorkOSClientID:        getEnv("WORKOS_CLIENT_ID", ""),
		WorkOSAPIKey:          getEnv("WORKOS_API_KEY", ""),
		S3Endpoint:            getEnv("S3_ENDPOINT", ""),
		S3AccessKeyID:         getEnv("S3_ACCESS_KEY_ID", ""),
		S3SecretAccessKey:     getEnv("S3_SECRET_ACCESS_KEY", ""),
		S3Bucket:              getEnv("S3_BUCKET", ""),
		S3Region:              getEnv("S3_REGION", "us-east-1"),
		PythonBackendURL:      getEnv("PYTHON_BACKEND_URL", "http://127.0.0.1:8000"),
		PythonBackendGRPCAddr: getEnv("PYTHON_BACKEND_GRPC_ADDR", "127.0.0.1:9092"),
		ServiceToken:          getEnv("SERVICE_TOKEN", ""),

		CollectorEndpoint:  getEnv("PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT", getEnv("OTLP_ENDPOINT", "127.0.0.1:4317")),
		TracingEnabled:     getEnvBool("TRACING_ENABLED", true),
		TracingEnvironment: getEnv("TRACING_ENVIRONMENT", "development"),

		SentryDSN:              getEnv("SENTRY_DSN", ""),
		SentryEnvironment:      getEnv("SENTRY_ENVIRONMENT", getEnv("ENV", "development")),
		SentryRelease:          getEnv("SENTRY_RELEASE", "unknown"),
		SentryTracesSampleRate: getEnvFloat("SENTRY_TRACES_SAMPLE_RATE", defaultSentryTracesSampleRate),
		SentryDebug:            getEnvBool("SENTRY_DEBUG", false),
	}
	cfg.Embeddings = loadEmbeddingsConfig()
	return cfg
}

func loadEmbeddingsConfig() EmbeddingsConfig {
	return EmbeddingsConfig{
		// Provider selection
		Provider: getEnv("EMBEDDING_PROVIDER", "voyage"),

		// VoyageAI configuration
		VoyageAPIKey:     getEnv("VOYAGE_API_KEY", ""),
		VoyageModel:      getEnv("VOYAGE_MODEL", "voyage-3.5"),
		VoyageDimensions: getEnvInt("VOYAGE_DIMENSIONS", defaultVoyageDimensions),

		// OpenRouter configuration
		OpenRouterAPIKey: getEnv("OPENROUTER_API_KEY", ""),
		OpenRouterModel:  getEnv("OPENROUTER_MODEL", "openai/text-embedding-3-small"),

		// Reranking configuration
		RerankEnabled: getEnvBool("RERANK_ENABLED", true),
		RerankModel:   getEnv("RERANK_MODEL", "rerank-2.5"),

		// Performance settings
		RateLimitPerMinute: getEnvInt("EMBEDDING_RATE_LIMIT", defaultEmbeddingRateLimit),
		TimeoutSeconds:     getEnvInt("EMBEDDING_TIMEOUT", defaultEmbeddingTimeout),
		MaxRetries:         getEnvInt("EMBEDDING_MAX_RETRIES", defaultEmbeddingMaxRetries),
		MaxBatchSize:       getEnvInt("EMBEDDING_BATCH_SIZE", defaultEmbeddingBatchSize),

		// Indexer settings
		IndexerEnabled:      getEnvBool("INDEXER_ENABLED", true),
		IndexerWorkers:      getEnvInt("INDEXER_WORKERS", defaultIndexerWorkers),
		IndexerBatchSize:    getEnvInt("INDEXER_BATCH_SIZE", defaultIndexerBatchSize),
		IndexerPollInterval: getEnvInt("INDEXER_POLL_INTERVAL", defaultIndexerPollInterval),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intVal, err := strconv.Atoi(value); err == nil {
			return intVal
		}
	}
	return defaultValue
}

func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolVal, err := strconv.ParseBool(value); err == nil {
			return boolVal
		}
	}
	return defaultValue
}

func getEnvFloat(key string, defaultValue float64) float64 {
	if value := os.Getenv(key); value != "" {
		if floatVal, err := strconv.ParseFloat(value, 64); err == nil {
			return floatVal
		}
	}
	return defaultValue
}
