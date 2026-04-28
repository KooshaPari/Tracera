// Package vault provides HashiCorp Vault integration for secrets management.
// Package vault provides helpers for fetching secrets from Vault.
package vault

import (
	"context"
	"errors"
	"fmt"
	"os"

	vault "github.com/hashicorp/vault/api"
)

// Client wraps the Vault API client with TracerTM-specific helpers
type Client struct {
	client *vault.Client
	prefix string // e.g., "secret/data/tracertm"
}

// NewClient creates a new Vault client using environment variables
// Required env vars: VAULT_ADDR, VAULT_TOKEN
func NewClient() (*Client, error) {
	config := vault.DefaultConfig()

	vaultAddr := os.Getenv("VAULT_ADDR")
	if vaultAddr == "" {
		vaultAddr = "http://127.0.0.1:8200"
	}
	config.Address = vaultAddr

	client, err := vault.NewClient(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create vault client: %w", err)
	}

	// Set token from environment
	token := os.Getenv("VAULT_TOKEN")
	if token == "" {
		return nil, errors.New("VAULT_TOKEN environment variable not set")
	}
	client.SetToken(token)

	return &Client{
		client: client,
		prefix: "secret/data/tracertm", // KV v2 path prefix
	}, nil
}

// GetSecret retrieves a secret from Vault
// path should be relative to tracertm/ (e.g., "jwt", "database")
func (c *Client) GetSecret(ctx context.Context, path string) (map[string]interface{}, error) {
	fullPath := c.prefix + "/" + path

	secret, err := c.client.KVv2(c.prefix).Get(ctx, path)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret %s: %w", fullPath, err)
	}

	if secret == nil || secret.Data == nil {
		return nil, fmt.Errorf("secret not found: %s", fullPath)
	}

	return secret.Data, nil
}

// GetSecretField retrieves a specific field from a Vault secret
func (c *Client) GetSecretField(ctx context.Context, path, field string) (string, error) {
	data, err := c.GetSecret(ctx, path)
	if err != nil {
		return "", err
	}

	value, ok := data[field]
	if !ok {
		return "", fmt.Errorf("field %s not found in secret %s", field, path)
	}

	strValue, ok := value.(string)
	if !ok {
		return "", fmt.Errorf("field %s is not a string in secret %s", field, path)
	}

	return strValue, nil
}

// GetJWTSecret retrieves the JWT signing secret
func (c *Client) GetJWTSecret(ctx context.Context) (string, error) {
	return c.GetSecretField(ctx, "jwt", "secret")
}

// GetDatabaseURL retrieves the database connection URL
func (c *Client) GetDatabaseURL(ctx context.Context) (string, error) {
	return c.GetSecretField(ctx, "database", "url")
}

// GetDatabaseCredentials retrieves structured database credentials
func (c *Client) GetDatabaseCredentials(ctx context.Context) (*DatabaseCredentials, error) {
	data, err := c.GetSecret(ctx, "database")
	if err != nil {
		return nil, err
	}

	return &DatabaseCredentials{
		URL:      getStringField(data, "url"),
		Host:     getStringField(data, "host"),
		Port:     getStringField(data, "port"),
		User:     getStringField(data, "user"),
		Password: getStringField(data, "password"),
		Name:     getStringField(data, "name"),
	}, nil
}

// GetRedisURL retrieves the Redis connection URL
func (c *Client) GetRedisURL(ctx context.Context) (string, error) {
	return c.GetSecretField(ctx, "redis", "url")
}

// GetNeo4jCredentials retrieves Neo4j connection details
func (c *Client) GetNeo4jCredentials(ctx context.Context) (*Neo4jCredentials, error) {
	data, err := c.GetSecret(ctx, "neo4j")
	if err != nil {
		return nil, err
	}

	return &Neo4jCredentials{
		URI:      getStringField(data, "uri"),
		User:     getStringField(data, "user"),
		Password: getStringField(data, "password"),
		Auth:     getStringField(data, "auth"),
	}, nil
}

// GetS3Credentials retrieves S3/MinIO credentials
func (c *Client) GetS3Credentials(ctx context.Context) (*S3Credentials, error) {
	data, err := c.GetSecret(ctx, "s3")
	if err != nil {
		return nil, err
	}

	return &S3Credentials{
		Endpoint:        getStringField(data, "endpoint"),
		AccessKeyID:     getStringField(data, "access_key_id"),
		SecretAccessKey: getStringField(data, "secret_access_key"),
		Bucket:          getStringField(data, "bucket"),
		Region:          getStringField(data, "region"),
	}, nil
}

// GetWorkOSCredentials retrieves WorkOS authentication credentials
func (c *Client) GetWorkOSCredentials(ctx context.Context) (*WorkOSCredentials, error) {
	data, err := c.GetSecret(ctx, "workos")
	if err != nil {
		return &WorkOSCredentials{}, nil //nolint:nilerr // WorkOS is optional, return empty credentials if not found
	}

	return &WorkOSCredentials{
		APIKey:      getStringField(data, "api_key"),
		ClientID:    getStringField(data, "client_id"),
		RedirectURI: getStringField(data, "redirect_uri"),
	}, nil
}

// Helper function to safely extract string fields
func getStringField(data map[string]interface{}, field string) string {
	if value, ok := data[field]; ok {
		if str, ok := value.(string); ok {
			return str
		}
	}
	return ""
}

// DatabaseCredentials holds database connection credentials from Vault.
type DatabaseCredentials struct {
	URL      string
	Host     string
	Port     string
	User     string
	Password string
	Name     string
}

// Neo4jCredentials holds Neo4j connection credentials from Vault.
type Neo4jCredentials struct {
	URI      string
	User     string
	Password string
	Auth     string
}

// S3Credentials holds S3/MinIO credentials from Vault.
type S3Credentials struct {
	Endpoint        string
	AccessKeyID     string
	SecretAccessKey string
	Bucket          string
	Region          string
}

// WorkOSCredentials holds WorkOS auth credentials from Vault.
type WorkOSCredentials struct {
	APIKey      string
	ClientID    string
	RedirectURI string
}

// HealthCheck verifies Vault connectivity and authentication
func (c *Client) HealthCheck(_ context.Context) error {
	// Attempt to read a test path to verify connectivity
	_, err := c.client.Sys().Health()
	if err != nil {
		return fmt.Errorf("vault health check failed: %w", err)
	}

	return nil
}
