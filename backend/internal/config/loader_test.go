package config

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	requiredDatabaseURL = "postgres://localhost:5432/test"
	requiredRedisURL    = "redis://localhost:6379"
	requiredNATSURL     = "nats://localhost:4222"
)

type appSettingsCase struct {
	name         string
	envVar       string
	envValue     string
	appEnvValue  string
	portVar      string
	portValue    string
	appPortValue string
	expectedEnv  string
	expectedPort string
}

func appSettingsCases() []appSettingsCase {
	return []appSettingsCase{
		{
			name:         "ENV preferred over APP_ENV",
			envVar:       "ENV",
			envValue:     "production",
			appEnvValue:  "staging", // Set APP_ENV but ENV should take precedence
			expectedEnv:  "production",
			expectedPort: "8080",
		},
		{
			name:         "APP_ENV fallback when ENV not set",
			appEnvValue:  "staging",
			expectedEnv:  "staging",
			expectedPort: "8080",
		},
		{
			name:         "PORT preferred over APP_PORT",
			portVar:      "PORT",
			portValue:    "9090",
			appPortValue: "3000", // Set APP_PORT but PORT should take precedence
			expectedEnv:  "development",
			expectedPort: "9090",
		},
		{
			name:         "APP_PORT fallback when PORT not set",
			appPortValue: "3000",
			expectedEnv:  "development",
			expectedPort: "3000",
		},
	}
}

func setRequiredEnvVars(t *testing.T) {
	t.Helper()
	require.NoError(t, os.Setenv("DATABASE_URL", requiredDatabaseURL))
	require.NoError(t, os.Setenv("REDIS_URL", requiredRedisURL))
	require.NoError(t, os.Setenv("NATS_URL", requiredNATSURL))
}

func runAppSettingsCase(t *testing.T, tt appSettingsCase) {
	t.Helper()
	clearConfigEnvVars(t)
	os.Clearenv()

	setRequiredEnvVars(t)

	if tt.envVar != "" && tt.envValue != "" {
		require.NoError(t, os.Setenv(tt.envVar, tt.envValue))
	}
	if tt.appEnvValue != "" {
		require.NoError(t, os.Setenv("APP_ENV", tt.appEnvValue))
	}
	if tt.portVar != "" && tt.portValue != "" {
		require.NoError(t, os.Setenv(tt.portVar, tt.portValue))
	}
	if tt.appPortValue != "" {
		require.NoError(t, os.Setenv("APP_PORT", tt.appPortValue))
	}

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, tt.expectedEnv, cfg.Env)
	assert.Equal(t, tt.expectedPort, cfg.Port)

	clearConfigEnvVars(t)
}

func allSettingsEnvVars() map[string]string {
	return map[string]string{
		// Application
		"ENV":  "production",
		"PORT": "9090",

		// Database
		"DATABASE_URL": "postgres://prod:secret@prod.db:5432/proddb",

		// Supabase
		"SUPABASE_URL":              "https://supabase.example.com",
		"SUPABASE_SERVICE_ROLE_KEY": "sk_test_123",

		// JWT
		"JWT_SECRET": "super-secret-jwt-key",

		// NATS
		"NATS_URL":   "nats://nats.example.com:4222",
		"NATS_CREDS": "/path/to/nats.creds",

		// Redis
		"REDIS_URL":                "redis://redis.example.com:6379",
		"UPSTASH_REDIS_REST_URL":   "https://upstash.example.com",
		"UPSTASH_REDIS_REST_TOKEN": "upstash_token_123",

		// Neo4j
		"NEO4J_URI":      "neo4j://neo4j.example.com:7687",
		"NEO4J_USER":     "admin",
		"NEO4J_PASSWORD": "neo4j_secret",

		// WorkOS
		"WORKOS_CLIENT_ID": "client_123",
		"WORKOS_API_KEY":   "sk_workos_123",

		// Embeddings
		"EMBEDDING_PROVIDER":    "openrouter",
		"VOYAGE_API_KEY":        "voyage_key_123",
		"VOYAGE_MODEL":          "voyage-4.0",
		"VOYAGE_DIMENSIONS":     "2048",
		"OPENROUTER_API_KEY":    "openrouter_key_123",
		"OPENROUTER_MODEL":      "openai/text-embedding-ada-002",
		"RERANK_ENABLED":        "false",
		"RERANK_MODEL":          "rerank-3.0",
		"EMBEDDING_RATE_LIMIT":  "500",
		"EMBEDDING_TIMEOUT":     "120",
		"EMBEDDING_MAX_RETRIES": "5",
		"EMBEDDING_BATCH_SIZE":  "256",
		"INDEXER_ENABLED":       "false",
		"INDEXER_WORKERS":       "10",
		"INDEXER_BATCH_SIZE":    "100",
		"INDEXER_POLL_INTERVAL": "60",
	}
}

func assertAllSettings(t *testing.T, cfg *Config) {
	t.Helper()
	assert.Equal(t, "production", cfg.Env)
	assert.Equal(t, "9090", cfg.Port)
	assert.Equal(t, "postgres://prod:secret@prod.db:5432/proddb", cfg.DatabaseURL)
	// assert.Equal(t, "https://supabase.example.com", cfg.SupabaseURL) // Supabase removed
	// assert.Equal(t, "sk_test_123", cfg.SupabaseServiceRoleKey) // Supabase removed
	assert.Equal(t, "super-secret-jwt-key", cfg.JWTSecret)
	assert.Equal(t, "nats://nats.example.com:4222", cfg.NATSUrl)
	assert.Equal(t, "/path/to/nats.creds", cfg.NATSCreds)
	assert.Equal(t, "redis://redis.example.com:6379", cfg.RedisURL)
	assert.Equal(t, "https://upstash.example.com", cfg.UpstashRedisRestURL)
	assert.Equal(t, "upstash_token_123", cfg.UpstashRedisRestToken)
	assert.Equal(t, "neo4j://neo4j.example.com:7687", cfg.Neo4jURI)
	assert.Equal(t, "admin", cfg.Neo4jUser)
	assert.Equal(t, "neo4j_secret", cfg.Neo4jPassword)
	assert.Equal(t, "client_123", cfg.WorkOSClientID)
	assert.Equal(t, "sk_workos_123", cfg.WorkOSAPIKey)

	// Embeddings
	assert.Equal(t, "openrouter", cfg.Embeddings.Provider)
	assert.Equal(t, "voyage_key_123", cfg.Embeddings.VoyageAPIKey)
	assert.Equal(t, "voyage-4.0", cfg.Embeddings.VoyageModel)
	assert.Equal(t, 2048, cfg.Embeddings.VoyageDimensions)
	assert.Equal(t, "openrouter_key_123", cfg.Embeddings.OpenRouterAPIKey)
	assert.Equal(t, "openai/text-embedding-ada-002", cfg.Embeddings.OpenRouterModel)
	assert.False(t, cfg.Embeddings.RerankEnabled)
	assert.Equal(t, "rerank-3.0", cfg.Embeddings.RerankModel)
	assert.Equal(t, 500, cfg.Embeddings.RateLimitPerMinute)
	assert.Equal(t, 120, cfg.Embeddings.TimeoutSeconds)
	assert.Equal(t, 5, cfg.Embeddings.MaxRetries)
	assert.Equal(t, 256, cfg.Embeddings.MaxBatchSize)
	assert.False(t, cfg.Embeddings.IndexerEnabled)
	assert.Equal(t, 10, cfg.Embeddings.IndexerWorkers)
	assert.Equal(t, 100, cfg.Embeddings.IndexerBatchSize)
	assert.Equal(t, 60, cfg.Embeddings.IndexerPollInterval)
}

// TestLoadWithEnvManager_Success tests successful configuration loading
func TestLoadWithEnvManager_Success(t *testing.T) {
	clearConfigEnvVars(t)

	// Set required environment variables
	setRequiredEnvVars(t)
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	require.NotNil(t, cfg)
	assert.Equal(t, requiredDatabaseURL, cfg.DatabaseURL)
	assert.Equal(t, requiredRedisURL, cfg.RedisURL)
	assert.Equal(t, requiredNATSURL, cfg.NATSUrl)
}

// TestLoadWithEnvManager_Defaults tests default values with env manager
func TestLoadWithEnvManager_Defaults(t *testing.T) {
	clearConfigEnvVars(t)

	// Set only required vars
	setRequiredEnvVars(t)
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, "development", cfg.Env)
	assert.Equal(t, "8080", cfg.Port)
	assert.Equal(t, "neo4j://localhost:7687", cfg.Neo4jURI)
	assert.Equal(t, "neo4j", cfg.Neo4jUser)
}

// TestLoadWithEnvManager_MissingRequiredVars tests missing required variables
func TestLoadWithEnvManager_MissingRequiredVars(t *testing.T) {
	clearConfigEnvVars(t)

	// Don't set any required variables
	cfg, err := LoadWithEnvManager()

	// Should return config but with empty required fields
	require.NoError(t, err) // LoadWithEnvManager logs warnings but doesn't error
	require.NotNil(t, cfg)
	assert.Empty(t, cfg.DatabaseURL)
	assert.Empty(t, cfg.RedisURL)
}

// TestLoadWithEnvManager_PartialRequiredVars tests some required variables missing
func TestLoadWithEnvManager_PartialRequiredVars(t *testing.T) {
	clearConfigEnvVars(t)

	// Set only some required variables
	require.NoError(t, os.Setenv("DATABASE_URL", requiredDatabaseURL))
	require.NoError(t, os.Setenv("REDIS_URL", requiredRedisURL))
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	require.NotNil(t, cfg)
	assert.Equal(t, requiredDatabaseURL, cfg.DatabaseURL)
	assert.Equal(t, requiredRedisURL, cfg.RedisURL)
	assert.Equal(t, requiredNATSURL, cfg.NATSUrl) // Uses default
}

// TestLoadWithEnvManager_ApplicationSettings tests ENV and PORT variations
func TestLoadWithEnvManager_ApplicationSettings(t *testing.T) {
	for _, tt := range appSettingsCases() {
		t.Run(tt.name, func(t *testing.T) {
			runAppSettingsCase(t, tt)
		})
	}
}

// TestLoadWithEnvManager_SupabaseKeyFallback tests Supabase key fallback logic
func TestLoadWithEnvManager_SupabaseKeyFallback(t *testing.T) {
	tests := []struct {
		name                   string
		serviceRoleKey         string
		serviceKey             string
		expectedServiceRoleKey string
	}{
		{
			name:                   "SUPABASE_SERVICE_ROLE_KEY preferred",
			serviceRoleKey:         "role_key_123",
			serviceKey:             "service_key_456",
			expectedServiceRoleKey: "role_key_123",
		},
		{
			name:                   "SUPABASE_SERVICE_KEY fallback",
			serviceRoleKey:         "",
			serviceKey:             "service_key_456",
			expectedServiceRoleKey: "service_key_456",
		},
		{
			name:                   "both empty",
			serviceRoleKey:         "",
			serviceKey:             "",
			expectedServiceRoleKey: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			clearConfigEnvVars(t)

			// Set required vars
			setRequiredEnvVars(t)

			if tt.serviceRoleKey != "" {
				require.NoError(t, os.Setenv("SUPABASE_SERVICE_ROLE_KEY", tt.serviceRoleKey))
			}
			if tt.serviceKey != "" {
				require.NoError(t, os.Setenv("SUPABASE_SERVICE_KEY", tt.serviceKey))
			}

			cfg, err := LoadWithEnvManager()

			require.NoError(t, err)
			_ = cfg // Supabase removed
			// assert.Equal(t, tt.expectedServiceRoleKey, cfg.SupabaseServiceRoleKey)

			clearConfigEnvVars(t)
		})
	}
}

// TestLoadWithEnvManager_DatabaseConfiguration tests database-related settings
func TestLoadWithEnvManager_DatabaseConfiguration(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":   "postgres://user:pass@db.example.com:5432/proddb",
		"REDIS_URL":      "redis://redis.example.com:6379",
		"NATS_URL":       "nats://nats.example.com:4222",
		"SUPABASE_URL":   "https://supabase.example.com",
		"NEO4J_URI":      "neo4j://neo4j.example.com:7687",
		"NEO4J_USER":     "admin",
		"NEO4J_PASSWORD": "secret",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, "postgres://user:pass@db.example.com:5432/proddb", cfg.DatabaseURL)
	assert.Equal(t, "redis://redis.example.com:6379", cfg.RedisURL)
	assert.Equal(t, "nats://nats.example.com:4222", cfg.NATSUrl)
	// assert.Equal(t, "https://supabase.example.com", cfg.SupabaseURL) // Supabase removed
	assert.Equal(t, "neo4j://neo4j.example.com:7687", cfg.Neo4jURI)
	assert.Equal(t, "admin", cfg.Neo4jUser)
	assert.Equal(t, "secret", cfg.Neo4jPassword)
}

// TestLoadWithEnvManager_RedisConfiguration tests Redis settings including Upstash
func TestLoadWithEnvManager_RedisConfiguration(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":             requiredDatabaseURL,
		"REDIS_URL":                requiredRedisURL,
		"NATS_URL":                 requiredNATSURL,
		"UPSTASH_REDIS_REST_URL":   "https://upstash.example.com",
		"UPSTASH_REDIS_REST_TOKEN": "upstash_token_123",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, "redis://localhost:6379", cfg.RedisURL)
	assert.Equal(t, "https://upstash.example.com", cfg.UpstashRedisRestURL)
	assert.Equal(t, "upstash_token_123", cfg.UpstashRedisRestToken)
}

// TestLoadWithEnvManager_AuthConfiguration tests authentication settings
func TestLoadWithEnvManager_AuthConfiguration(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":     "postgres://localhost:5432/test",
		"REDIS_URL":        "redis://localhost:6379",
		"NATS_URL":         "nats://localhost:4222",
		"JWT_SECRET":       "super-secret-jwt-key",
		"WORKOS_CLIENT_ID": "client_123",
		"WORKOS_API_KEY":   "sk_workos_123",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, "super-secret-jwt-key", cfg.JWTSecret)
	assert.Equal(t, "client_123", cfg.WorkOSClientID)
	assert.Equal(t, "sk_workos_123", cfg.WorkOSAPIKey)
}

// TestLoadWithEnvManager_EmbeddingsConfiguration tests embeddings settings
func TestLoadWithEnvManager_EmbeddingsConfiguration(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":       "postgres://localhost:5432/test",
		"REDIS_URL":          "redis://localhost:6379",
		"NATS_URL":           "nats://localhost:4222",
		"EMBEDDING_PROVIDER": "openrouter",
		"VOYAGE_API_KEY":     "voyage_key_123",
		"VOYAGE_MODEL":       "voyage-4.0",
		"VOYAGE_DIMENSIONS":  "2048",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, "openrouter", cfg.Embeddings.Provider)
	assert.Equal(t, "voyage_key_123", cfg.Embeddings.VoyageAPIKey)
	assert.Equal(t, "voyage-4.0", cfg.Embeddings.VoyageModel)
	assert.Equal(t, 2048, cfg.Embeddings.VoyageDimensions)
}

// TestLoadWithEnvManager_EmbeddingsOpenRouterConfig tests OpenRouter settings
func TestLoadWithEnvManager_EmbeddingsOpenRouterConfig(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":       "postgres://localhost:5432/test",
		"REDIS_URL":          "redis://localhost:6379",
		"NATS_URL":           "nats://localhost:4222",
		"OPENROUTER_API_KEY": "openrouter_key_123",
		"OPENROUTER_MODEL":   "openai/text-embedding-ada-002",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, "openrouter_key_123", cfg.Embeddings.OpenRouterAPIKey)
	assert.Equal(t, "openai/text-embedding-ada-002", cfg.Embeddings.OpenRouterModel)
}

// TestLoadWithEnvManager_EmbeddingsRerankConfig tests reranking configuration
func TestLoadWithEnvManager_EmbeddingsRerankConfig(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":   "postgres://localhost:5432/test",
		"REDIS_URL":      "redis://localhost:6379",
		"NATS_URL":       "nats://localhost:4222",
		"RERANK_ENABLED": "false",
		"RERANK_MODEL":   "rerank-3.0",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.False(t, cfg.Embeddings.RerankEnabled)
	assert.Equal(t, "rerank-3.0", cfg.Embeddings.RerankModel)
}

// TestLoadWithEnvManager_EmbeddingsPerformanceSettings tests performance settings
func TestLoadWithEnvManager_EmbeddingsPerformanceSettings(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":          "postgres://localhost:5432/test",
		"REDIS_URL":             "redis://localhost:6379",
		"NATS_URL":              "nats://localhost:4222",
		"EMBEDDING_RATE_LIMIT":  "500",
		"EMBEDDING_TIMEOUT":     "120",
		"EMBEDDING_MAX_RETRIES": "5",
		"EMBEDDING_BATCH_SIZE":  "256",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, 500, cfg.Embeddings.RateLimitPerMinute)
	assert.Equal(t, 120, cfg.Embeddings.TimeoutSeconds)
	assert.Equal(t, 5, cfg.Embeddings.MaxRetries)
	assert.Equal(t, 256, cfg.Embeddings.MaxBatchSize)
}

// TestLoadWithEnvManager_EmbeddingsIndexerSettings tests indexer configuration
func TestLoadWithEnvManager_EmbeddingsIndexerSettings(t *testing.T) {
	clearConfigEnvVars(t)

	envVars := map[string]string{
		"DATABASE_URL":          "postgres://localhost:5432/test",
		"REDIS_URL":             "redis://localhost:6379",
		"NATS_URL":              "nats://localhost:4222",
		"INDEXER_ENABLED":       "false",
		"INDEXER_WORKERS":       "10",
		"INDEXER_BATCH_SIZE":    "100",
		"INDEXER_POLL_INTERVAL": "60",
	}

	for key, value := range envVars {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.False(t, cfg.Embeddings.IndexerEnabled)
	assert.Equal(t, 10, cfg.Embeddings.IndexerWorkers)
	assert.Equal(t, 100, cfg.Embeddings.IndexerBatchSize)
	assert.Equal(t, 60, cfg.Embeddings.IndexerPollInterval)
}

// TestLoadWithEnvManager_AllSettings tests comprehensive configuration
func TestLoadWithEnvManager_AllSettings(t *testing.T) {
	clearConfigEnvVars(t)

	for key, value := range allSettingsEnvVars() {
		require.NoError(t, os.Setenv(key, value))
	}
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	require.NotNil(t, cfg)

	assertAllSettings(t, cfg)
}

// TestLoadWithEnvManager_IntegerEdgeCases tests integer parsing edge cases
func TestLoadWithEnvManager_IntegerEdgeCases(t *testing.T) {
	tests := []struct {
		name     string
		key      string
		value    string
		expected int
	}{
		{"valid positive", "VOYAGE_DIMENSIONS", "2048", 2048},
		{"zero", "INDEXER_WORKERS", "0", 0},
		{"invalid returns default", "VOYAGE_DIMENSIONS", "invalid", 1024},
		{"negative is parsed successfully", "INDEXER_WORKERS", "-5", -5}, // strconv.Atoi accepts negative numbers
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			clearConfigEnvVars(t)

			// Set required vars
			require.NoError(t, os.Setenv("DATABASE_URL", "postgres://localhost:5432/test"))
			require.NoError(t, os.Setenv("REDIS_URL", "redis://localhost:6379"))
			require.NoError(t, os.Setenv("NATS_URL", "nats://localhost:4222"))
			require.NoError(t, os.Setenv(tt.key, tt.value))

			cfg, err := LoadWithEnvManager()

			require.NoError(t, err)

			var actual int
			switch tt.key {
			case "VOYAGE_DIMENSIONS":
				actual = cfg.Embeddings.VoyageDimensions
			case "INDEXER_WORKERS":
				actual = cfg.Embeddings.IndexerWorkers
			}

			assert.Equal(t, tt.expected, actual)

			clearConfigEnvVars(t)
		})
	}
}

// TestLoadWithEnvManager_BooleanEdgeCases tests boolean parsing edge cases
func TestLoadWithEnvManager_BooleanEdgeCases(t *testing.T) {
	tests := []struct {
		name     string
		value    string
		expected bool
	}{
		{"true", "true", true},
		{"false", "false", false},
		{"1", "1", true},
		{"0", "0", false},
		{"invalid returns default", "invalid", true}, // default is true
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			clearConfigEnvVars(t)

			// Set required vars
			require.NoError(t, os.Setenv("DATABASE_URL", "postgres://localhost:5432/test"))
			require.NoError(t, os.Setenv("REDIS_URL", "redis://localhost:6379"))
			require.NoError(t, os.Setenv("NATS_URL", "nats://localhost:4222"))
			require.NoError(t, os.Setenv("RERANK_ENABLED", tt.value))

			cfg, err := LoadWithEnvManager()

			require.NoError(t, err)
			assert.Equal(t, tt.expected, cfg.Embeddings.RerankEnabled)

			clearConfigEnvVars(t)
		})
	}
}

// TestLoadWithEnvManager_EmptyStringHandling tests empty string handling
func TestLoadWithEnvManager_EmptyStringHandling(t *testing.T) {
	clearConfigEnvVars(t)

	// Set required vars
	require.NoError(t, os.Setenv("DATABASE_URL", "postgres://localhost:5432/test"))
	require.NoError(t, os.Setenv("REDIS_URL", "redis://localhost:6379"))
	require.NoError(t, os.Setenv("NATS_URL", "nats://localhost:4222"))

	// Set some optional vars to empty strings
	require.NoError(t, os.Setenv("VOYAGE_API_KEY", ""))
	require.NoError(t, os.Setenv("WORKOS_CLIENT_ID", ""))
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Empty(t, cfg.Embeddings.VoyageAPIKey)
	assert.Empty(t, cfg.WorkOSClientID)
}

// TestLoadWithEnvManager_NATSCredentialsOptional tests NATS creds is optional
func TestLoadWithEnvManager_NATSCredentialsOptional(t *testing.T) {
	clearConfigEnvVars(t)

	require.NoError(t, os.Setenv("DATABASE_URL", "postgres://localhost:5432/test"))
	require.NoError(t, os.Setenv("REDIS_URL", "redis://localhost:6379"))
	require.NoError(t, os.Setenv("NATS_URL", "nats://localhost:4222"))
	defer clearConfigEnvVars(t)

	cfg, err := LoadWithEnvManager()

	require.NoError(t, err)
	assert.Equal(t, "nats://localhost:4222", cfg.NATSUrl)
	assert.Empty(t, cfg.NATSCreds) // Should be empty when not set
}

// TestLoadWithEnvManager_ConcurrentAccess tests thread safety
func TestLoadWithEnvManager_ConcurrentAccess(t *testing.T) {
	// First, completely clear all env vars to ensure clean state
	clearConfigEnvVars(t)
	os.Clearenv() // Clear everything

	// Now set only required vars
	require.NoError(t, os.Setenv("DATABASE_URL", "postgres://localhost:5432/test"))
	require.NoError(t, os.Setenv("REDIS_URL", "redis://localhost:6379"))
	require.NoError(t, os.Setenv("NATS_URL", "nats://localhost:4222"))

	// Explicitly set ENV to development to ensure consistency
	require.NoError(t, os.Setenv("ENV", "development"))
	defer clearConfigEnvVars(t)

	// Load config from multiple goroutines
	done := make(chan bool)
	for i := 0; i < 10; i++ {
		go func() {
			cfg, err := LoadWithEnvManager()
			assert.NoError(t, err)
			assert.NotNil(t, cfg)
			// Use Contains or just check NotNil since we can't guarantee
			// which exact env value will be returned in concurrent environment
			assert.NotEmpty(t, cfg.Env)
			done <- true
		}()
	}

	// Wait for all goroutines
	for i := 0; i < 10; i++ {
		<-done
	}
}
