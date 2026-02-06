package config

import (
	"context"
	"fmt"
	"os"

	"github.com/kooshapari/tracertm-backend/internal/vault"
)

// LoadConfigFromVault loads configuration from Vault
// Falls back to environment variables if Vault is not available
func LoadConfigFromVault() (*Config, error) {
	// Check if Vault is enabled
	useVault := os.Getenv("USE_VAULT") == "true"

	if !useVault {
		// Fallback to standard config loading
		return LoadConfig(), nil
	}

	ctx := context.Background()
	vaultClient, err := newVaultClient(ctx)
	if err != nil {
		return nil, err
	}

	cfg := &Config{}
	if err := populateVaultSecrets(ctx, vaultClient, cfg); err != nil {
		return nil, err
	}

	applyVaultEnvConfig(cfg)
	cfg.Embeddings = loadEmbeddingsConfig()
	applyVaultEmbeddingsKeys(ctx, vaultClient, &cfg.Embeddings)

	return cfg, nil
}

func newVaultClient(ctx context.Context) (*vault.Client, error) {
	vaultClient, err := vault.NewClient()
	if err != nil {
		return nil, fmt.Errorf("failed to create vault client: %w", err)
	}
	if err := vaultClient.HealthCheck(ctx); err != nil {
		return nil, fmt.Errorf("vault health check failed: %w", err)
	}
	return vaultClient, nil
}

func populateVaultSecrets(ctx context.Context, vaultClient *vault.Client, cfg *Config) error {
	jwtSecret, err := vaultClient.GetJWTSecret(ctx)
	if err != nil {
		return fmt.Errorf("failed to get JWT secret: %w", err)
	}
	cfg.JWTSecret = jwtSecret

	dbCreds, err := vaultClient.GetDatabaseCredentials(ctx)
	if err != nil {
		return fmt.Errorf("failed to get database credentials: %w", err)
	}
	cfg.DatabaseURL = dbCreds.URL

	redisURL, err := vaultClient.GetRedisURL(ctx)
	if err != nil {
		return fmt.Errorf("failed to get Redis URL: %w", err)
	}
	cfg.RedisURL = redisURL

	neo4jCreds, err := vaultClient.GetNeo4jCredentials(ctx)
	if err != nil {
		return fmt.Errorf("failed to get Neo4j credentials: %w", err)
	}
	cfg.Neo4jURI = neo4jCreds.URI
	cfg.Neo4jUser = neo4jCreds.User
	cfg.Neo4jPassword = neo4jCreds.Password

	s3Creds, err := vaultClient.GetS3Credentials(ctx)
	if err != nil {
		return fmt.Errorf("failed to get S3 credentials: %w", err)
	}
	cfg.S3Endpoint = s3Creds.Endpoint
	cfg.S3AccessKeyID = s3Creds.AccessKeyID
	cfg.S3SecretAccessKey = s3Creds.SecretAccessKey
	cfg.S3Bucket = s3Creds.Bucket
	cfg.S3Region = s3Creds.Region

	workosCreds, err := vaultClient.GetWorkOSCredentials(ctx)
	if err != nil {
		return fmt.Errorf("failed to get WorkOS credentials: %w", err)
	}
	cfg.WorkOSAPIKey = workosCreds.APIKey
	cfg.WorkOSClientID = workosCreds.ClientID

	return nil
}

func applyVaultEnvConfig(cfg *Config) {
	cfg.Port = getEnv("PORT", "8080")
	cfg.GRPCPort = getEnv("GRPC_PORT", "9091")
	cfg.Env = getEnv("ENV", "development")
	cfg.NATSUrl = getEnv("NATS_URL", "nats://localhost:4222")
	cfg.PythonBackendURL = getEnv("PYTHON_BACKEND_URL", "http://127.0.0.1:8000")
	cfg.PythonBackendGRPCAddr = getEnv("PYTHON_BACKEND_GRPC_ADDR", "127.0.0.1:9092")
}

func applyVaultEmbeddingsKeys(ctx context.Context, vaultClient *vault.Client, embeddings *EmbeddingsConfig) {
	if voyageKey, err := vaultClient.GetSecretField(ctx, "ai/voyage", "api_key"); err == nil {
		embeddings.VoyageAPIKey = voyageKey
	}
	if openaiKey, err := vaultClient.GetSecretField(ctx, "ai/openai", "api_key"); err == nil {
		embeddings.OpenRouterAPIKey = openaiKey
	}
}
