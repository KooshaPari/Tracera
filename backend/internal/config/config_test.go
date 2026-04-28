package config

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func setEnv(t *testing.T, key, value string) {
	t.Helper()
	require.NoError(t, os.Setenv(key, value))
}

func unsetEnv(t *testing.T, key string) {
	t.Helper()
	require.NoError(t, os.Unsetenv(key))
}

const testBoolEnvKey = "TEST_BOOL"

type envBoolCase struct {
	name         string
	defaultValue bool
	envValue     string
	expected     bool
}

func envBoolCases() []envBoolCase {
	return []envBoolCase{
		{
			name:         "true string",
			defaultValue: false,
			envValue:     "true",
			expected:     true,
		},
		{
			name:         "false string",
			defaultValue: true,
			envValue:     "false",
			expected:     false,
		},
		{
			name:         "1 as true",
			defaultValue: false,
			envValue:     "1",
			expected:     true,
		},
		{
			name:         "0 as false",
			defaultValue: true,
			envValue:     "0",
			expected:     false,
		},
		{
			name:         "t as true",
			defaultValue: false,
			envValue:     "t",
			expected:     true,
		},
		{
			name:         "f as false",
			defaultValue: true,
			envValue:     "f",
			expected:     false,
		},
		{
			name:         "invalid - returns default",
			defaultValue: true,
			envValue:     "not_a_bool",
			expected:     true,
		},
		{
			name:         "not set - returns default",
			defaultValue: false,
			envValue:     "",
			expected:     false,
		},
	}
}

// TestLoadConfig_Defaults tests that LoadConfig returns correct default values
func TestLoadConfig_Defaults(t *testing.T) {
	// Clear all environment variables
	clearConfigEnvVars(t)

	cfg := LoadConfig()

	assert.NotNil(t, cfg)
	assert.Equal(t, "8080", cfg.Port)
	assert.Equal(t, "development", cfg.Env)
	assert.Equal(t, "postgres://user:password@localhost:5432/tracertm", cfg.DatabaseURL)
	assert.Equal(t, "your-secret-key-change-in-production", cfg.JWTSecret)
	assert.Equal(t, "nats://localhost:4222", cfg.NATSUrl)
	assert.Empty(t, cfg.NATSCreds)
	assert.Equal(t, "redis://localhost:6379", cfg.RedisURL)
	assert.Empty(t, cfg.UpstashRedisRestURL)
	assert.Empty(t, cfg.UpstashRedisRestToken)
	assert.Equal(t, "neo4j://localhost:7687", cfg.Neo4jURI)
	assert.Equal(t, "neo4j", cfg.Neo4jUser)
	assert.Equal(t, "password", cfg.Neo4jPassword)
	assert.Empty(t, cfg.WorkOSClientID)
	assert.Empty(t, cfg.WorkOSAPIKey)
}

// TestLoadConfig_EmbeddingsDefaults tests default embeddings configuration
func TestLoadConfig_EmbeddingsDefaults(t *testing.T) {
	clearConfigEnvVars(t)

	cfg := LoadConfig()

	assert.Equal(t, "voyage", cfg.Embeddings.Provider)
	assert.Empty(t, cfg.Embeddings.VoyageAPIKey)
	assert.Equal(t, "voyage-3.5", cfg.Embeddings.VoyageModel)
	assert.Equal(t, 1024, cfg.Embeddings.VoyageDimensions)
	assert.Empty(t, cfg.Embeddings.OpenRouterAPIKey)
	assert.Equal(t, "openai/text-embedding-3-small", cfg.Embeddings.OpenRouterModel)
	assert.True(t, cfg.Embeddings.RerankEnabled)
	assert.Equal(t, "rerank-2.5", cfg.Embeddings.RerankModel)
	assert.Equal(t, 300, cfg.Embeddings.RateLimitPerMinute)
	assert.Equal(t, 60, cfg.Embeddings.TimeoutSeconds)
	assert.Equal(t, 3, cfg.Embeddings.MaxRetries)
	assert.Equal(t, 128, cfg.Embeddings.MaxBatchSize)
	assert.True(t, cfg.Embeddings.IndexerEnabled)
	assert.Equal(t, 3, cfg.Embeddings.IndexerWorkers)
	assert.Equal(t, 50, cfg.Embeddings.IndexerBatchSize)
	assert.Equal(t, 30, cfg.Embeddings.IndexerPollInterval)
}

// TestLoadConfig_CustomValues tests loading from environment variables
func TestLoadConfig_CustomValues(t *testing.T) {
	// Set custom environment variables
	envVars := map[string]string{
		"PORT":                     "9090",
		"ENV":                      "production",
		"DATABASE_URL":             "postgres://prod:secret@prod.db:5432/proddb",
		"JWT_SECRET":               "super-secret-jwt-key",
		"NATS_URL":                 "nats://nats.example.com:4222",
		"NATS_CREDS":               "/path/to/nats.creds",
		"REDIS_URL":                "redis://redis.example.com:6379",
		"UPSTASH_REDIS_REST_URL":   "https://upstash.example.com",
		"UPSTASH_REDIS_REST_TOKEN": "upstash_token_123",
		"NEO4J_URI":                "neo4j://neo4j.example.com:7687",
		"NEO4J_USER":               "admin",
		"NEO4J_PASSWORD":           "neo4j_secret",
		"WORKOS_CLIENT_ID":         "client_123",
		"WORKOS_API_KEY":           "sk_workos_123",
	}

	for key, value := range envVars {
		setEnv(t, key, value)
	}
	defer clearConfigEnvVars(t)

	cfg := LoadConfig()

	assert.Equal(t, "9090", cfg.Port)
	assert.Equal(t, "production", cfg.Env)
	assert.Equal(t, "postgres://prod:secret@prod.db:5432/proddb", cfg.DatabaseURL)
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
}

// TestLoadConfig_SupabaseServiceRoleKeyFallback tests fallback behavior
// SKIPPED: Supabase has been removed from the application
func TestLoadConfig_SupabaseServiceRoleKeyFallback_SKIP(t *testing.T) {
	t.Skip("Supabase has been removed - test no longer applicable")
	tests := []struct {
		name                   string
		serviceRoleKey         string
		serviceKey             string
		expectedServiceRoleKey string
	}{
		{
			name:                   "both set - prefers SUPABASE_SERVICE_ROLE_KEY",
			serviceRoleKey:         "role_key_123",
			serviceKey:             "service_key_456",
			expectedServiceRoleKey: "role_key_123",
		},
		{
			name:                   "only SUPABASE_SERVICE_ROLE_KEY set",
			serviceRoleKey:         "role_key_123",
			serviceKey:             "",
			expectedServiceRoleKey: "role_key_123",
		},
		{
			name:                   "only SUPABASE_SERVICE_KEY set",
			serviceRoleKey:         "",
			serviceKey:             "service_key_456",
			expectedServiceRoleKey: "service_key_456",
		},
		{
			name:                   "neither set",
			serviceRoleKey:         "",
			serviceKey:             "",
			expectedServiceRoleKey: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			clearConfigEnvVars(t)

			if tt.serviceRoleKey != "" {
				setEnv(t, "SUPABASE_SERVICE_ROLE_KEY", tt.serviceRoleKey)
			}
			if tt.serviceKey != "" {
				setEnv(t, "SUPABASE_SERVICE_KEY", tt.serviceKey)
			}

			_ = LoadConfig()

			// assert.Equal(t, tt.expectedServiceRoleKey, cfg.SupabaseServiceRoleKey)

			clearConfigEnvVars(t)
		})
	}
}

// TestLoadConfig_EmbeddingsCustomValues tests custom embeddings configuration
func TestLoadConfig_EmbeddingsCustomValues(t *testing.T) {
	envVars := map[string]string{
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

	for key, value := range envVars {
		setEnv(t, key, value)
	}
	defer clearConfigEnvVars(t)

	cfg := LoadConfig()

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

// TestGetEnv tests the getEnv helper function
func TestGetEnv(t *testing.T) {
	tests := []struct {
		name         string
		key          string
		defaultValue string
		envValue     string
		expected     string
	}{
		{
			name:         "env var set",
			key:          "TEST_VAR",
			defaultValue: "default",
			envValue:     "custom",
			expected:     "custom",
		},
		{
			name:         "env var not set",
			key:          "TEST_VAR",
			defaultValue: "default",
			envValue:     "",
			expected:     "default",
		},
		{
			name:         "empty default",
			key:          "TEST_VAR",
			defaultValue: "",
			envValue:     "",
			expected:     "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			unsetEnv(t, tt.key)
			if tt.envValue != "" {
				setEnv(t, tt.key, tt.envValue)
			}

			result := getEnv(tt.key, tt.defaultValue)

			assert.Equal(t, tt.expected, result)

			unsetEnv(t, tt.key)
		})
	}
}

// TestGetEnvInt tests the getEnvInt helper function
func TestGetEnvInt(t *testing.T) {
	tests := []struct {
		name         string
		key          string
		defaultValue int
		envValue     string
		expected     int
	}{
		{
			name:         "valid integer",
			key:          "TEST_INT",
			defaultValue: 100,
			envValue:     "200",
			expected:     200,
		},
		{
			name:         "invalid integer - returns default",
			key:          "TEST_INT",
			defaultValue: 100,
			envValue:     "not_a_number",
			expected:     100,
		},
		{
			name:         "not set - returns default",
			key:          "TEST_INT",
			defaultValue: 100,
			envValue:     "",
			expected:     100,
		},
		{
			name:         "zero value",
			key:          "TEST_INT",
			defaultValue: 100,
			envValue:     "0",
			expected:     0,
		},
		{
			name:         "negative value",
			key:          "TEST_INT",
			defaultValue: 100,
			envValue:     "-50",
			expected:     -50,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			unsetEnv(t, tt.key)
			if tt.envValue != "" {
				setEnv(t, tt.key, tt.envValue)
			}

			result := getEnvInt(tt.key, tt.defaultValue)

			assert.Equal(t, tt.expected, result)

			unsetEnv(t, tt.key)
		})
	}
}

// TestGetEnvBool tests the getEnvBool helper function
func TestGetEnvBool(t *testing.T) {
	for _, tt := range envBoolCases() {
		t.Run(tt.name, func(t *testing.T) {
			unsetEnv(t, testBoolEnvKey)
			if tt.envValue != "" {
				setEnv(t, testBoolEnvKey, tt.envValue)
			}

			result := getEnvBool(testBoolEnvKey, tt.defaultValue)

			assert.Equal(t, tt.expected, result)

			unsetEnv(t, testBoolEnvKey)
		})
	}
}

// TestLoadConfig_EdgeCases tests edge cases
func TestLoadConfig_EdgeCases(t *testing.T) {
	t.Run("empty string env vars", func(t *testing.T) {
		clearConfigEnvVars(t)

		// Set empty strings explicitly
		setEnv(t, "PORT", "")
		setEnv(t, "ENV", "")
		setEnv(t, "DATABASE_URL", "")

		cfg := LoadConfig()

		// Empty strings should trigger defaults
		assert.Equal(t, "8080", cfg.Port)
		assert.Equal(t, "development", cfg.Env)
		assert.Equal(t, "postgres://user:password@localhost:5432/tracertm", cfg.DatabaseURL)

		clearConfigEnvVars(t)
	})

	t.Run("whitespace only env vars", func(t *testing.T) {
		clearConfigEnvVars(t)

		setEnv(t, "PORT", "   ")
		setEnv(t, "ENV", "\t\n")

		cfg := LoadConfig()

		// Whitespace is considered a value, not empty
		assert.Equal(t, "   ", cfg.Port)
		assert.Equal(t, "\t\n", cfg.Env)

		clearConfigEnvVars(t)
	})
}

// TestConfig_StructureComplete tests that all fields are properly initialized
func TestConfig_StructureComplete(t *testing.T) {
	clearConfigEnvVars(t)

	cfg := LoadConfig()

	// Ensure no nil pointers or uninitialized fields
	assert.NotNil(t, cfg)
	assert.NotEmpty(t, cfg.Port)
	assert.NotEmpty(t, cfg.Env)
	assert.NotEmpty(t, cfg.DatabaseURL)
	assert.NotEmpty(t, cfg.JWTSecret)
	assert.NotEmpty(t, cfg.NATSUrl)
	assert.NotEmpty(t, cfg.RedisURL)
	assert.NotEmpty(t, cfg.Neo4jURI)
	assert.NotEmpty(t, cfg.Neo4jUser)
	assert.NotEmpty(t, cfg.Neo4jPassword)

	// Embeddings config should be initialized
	assert.NotEmpty(t, cfg.Embeddings.Provider)
	assert.NotEmpty(t, cfg.Embeddings.VoyageModel)
	assert.NotEmpty(t, cfg.Embeddings.OpenRouterModel)
	assert.NotEmpty(t, cfg.Embeddings.RerankModel)
	assert.Positive(t, cfg.Embeddings.VoyageDimensions)
	assert.Positive(t, cfg.Embeddings.RateLimitPerMinute)
	assert.Positive(t, cfg.Embeddings.TimeoutSeconds)
	assert.Positive(t, cfg.Embeddings.MaxRetries)
	assert.Positive(t, cfg.Embeddings.MaxBatchSize)
	assert.Positive(t, cfg.Embeddings.IndexerWorkers)
	assert.Positive(t, cfg.Embeddings.IndexerBatchSize)
	assert.Positive(t, cfg.Embeddings.IndexerPollInterval)
}

// TestLoadConfig_ConcurrentAccess tests thread safety of LoadConfig
func TestLoadConfig_ConcurrentAccess(t *testing.T) {
	clearConfigEnvVars(t)

	// Load config from multiple goroutines
	done := make(chan bool)
	for i := 0; i < 10; i++ {
		go func() {
			cfg := LoadConfig()
			assert.NotNil(t, cfg)
			assert.Equal(t, "8080", cfg.Port)
			done <- true
		}()
	}

	// Wait for all goroutines
	for i := 0; i < 10; i++ {
		<-done
	}
}

// TestEmbeddingsConfig_ProviderVariations tests different provider configurations
func TestEmbeddingsConfig_ProviderVariations(t *testing.T) {
	providers := []string{"voyage", "openrouter", "local", "custom"}

	for _, provider := range providers {
		t.Run(provider, func(t *testing.T) {
			clearConfigEnvVars(t)
			setEnv(t, "EMBEDDING_PROVIDER", provider)

			cfg := LoadConfig()

			assert.Equal(t, provider, cfg.Embeddings.Provider)

			clearConfigEnvVars(t)
		})
	}
}

// TestLoadConfig_IntegerBoundaries tests integer boundary conditions
func TestLoadConfig_IntegerBoundaries(t *testing.T) {
	tests := []struct {
		name     string
		key      string
		value    string
		expected int
	}{
		{"max int", "EMBEDDING_RATE_LIMIT", "2147483647", 2147483647},
		{"zero", "EMBEDDING_RATE_LIMIT", "0", 0},
		{"large value", "EMBEDDING_BATCH_SIZE", "999999", 999999},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			clearConfigEnvVars(t)
			setEnv(t, tt.key, tt.value)

			cfg := LoadConfig()

			var actual int
			switch tt.key {
			case "EMBEDDING_RATE_LIMIT":
				actual = cfg.Embeddings.RateLimitPerMinute
			case "EMBEDDING_BATCH_SIZE":
				actual = cfg.Embeddings.MaxBatchSize
			}

			assert.Equal(t, tt.expected, actual)

			clearConfigEnvVars(t)
		})
	}
}

// TestLoadConfig_BooleanVariations tests various boolean representations
func TestLoadConfig_BooleanVariations(t *testing.T) {
	tests := []struct {
		value    string
		expected bool
	}{
		{"true", true},
		{"True", true},
		{"TRUE", true},
		{"1", true},
		{"t", true},
		{"T", true},
		{"false", false},
		{"False", false},
		{"FALSE", false},
		{"0", false},
		{"f", false},
		{"F", false},
	}

	for _, tt := range tests {
		t.Run(tt.value, func(t *testing.T) {
			clearConfigEnvVars(t)
			setEnv(t, "RERANK_ENABLED", tt.value)

			cfg := LoadConfig()

			assert.Equal(t, tt.expected, cfg.Embeddings.RerankEnabled)

			clearConfigEnvVars(t)
		})
	}
}

// clearConfigEnvVars clears all config-related environment variables
func clearConfigEnvVars(t *testing.T) {
	t.Helper()

	envVars := []string{
		"PORT", "ENV", "DATABASE_URL", "SUPABASE_URL",
		"SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY",
		"JWT_SECRET", "NATS_URL", "NATS_CREDS",
		"REDIS_URL", "UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN",
		"NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD",
		"WORKOS_CLIENT_ID", "WORKOS_API_KEY",
		"EMBEDDING_PROVIDER", "VOYAGE_API_KEY", "VOYAGE_MODEL", "VOYAGE_DIMENSIONS",
		"OPENROUTER_API_KEY", "OPENROUTER_MODEL",
		"RERANK_ENABLED", "RERANK_MODEL",
		"EMBEDDING_RATE_LIMIT", "EMBEDDING_TIMEOUT", "EMBEDDING_MAX_RETRIES",
		"EMBEDDING_BATCH_SIZE", "INDEXER_ENABLED", "INDEXER_WORKERS",
		"INDEXER_BATCH_SIZE", "INDEXER_POLL_INTERVAL",
	}

	for _, key := range envVars {
		unsetEnv(t, key)
	}
}
