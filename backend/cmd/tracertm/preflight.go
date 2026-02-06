package main

import (
	"context"
	"database/sql"
	"fmt"
	"net/url"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

// EnvConfig holds all required environment variables for the application
type EnvConfig struct {
	// Server
	Port     int
	GRPCPort int
	Env      string

	// Database
	DatabaseURL string

	// Security
	JWTSecret  string
	CSRFSecret string

	// Redis
	RedisURL string

	// NATS
	NatsURL string

	// WorkOS
	WorkosClientID string
	WorkosAPIKey   string

	// CORS
	CorsAllowedOrigins string

	// Temporal
	TemporalHost string

	// Python Backend
	PythonBackendURL string

	// OpenAI/Anthropic
	OpenAIAPIKey    string
	AnthropicAPIKey string
}

// PreflightCheck validates all required environment variables and connectivity
func PreflightCheck() error {
	cfg := &EnvConfig{}

	// Parse and validate environment variables
	if err := cfg.loadFromEnv(); err != nil {
		return fmt.Errorf("environment validation failed: %w", err)
	}

	// Test connectivity to critical services
	if err := cfg.testConnectivity(); err != nil {
		return fmt.Errorf("service connectivity check failed: %w", err)
	}

	return nil
}

// loadFromEnv loads and validates environment variables
func (c *EnvConfig) loadFromEnv() error {
	var errs []string

	// Required: Port
	portStr := os.Getenv("PORT")
	if portStr == "" {
		portStr = "8080"
	}
	port, err := strconv.Atoi(portStr)
	if err != nil {
		errs = append(errs, fmt.Sprintf("PORT must be a valid integer, got: %s", portStr))
	}
	if port < 1 || port > 65535 {
		errs = append(errs, fmt.Sprintf("PORT must be between 1 and 65535, got: %d", port))
	}
	c.Port = port

	// Required: GRPC_PORT
	grpcPortStr := os.Getenv("GRPC_PORT")
	if grpcPortStr == "" {
		grpcPortStr = "9090"
	}
	grpcPort, err := strconv.Atoi(grpcPortStr)
	if err != nil {
		errs = append(errs, fmt.Sprintf("GRPC_PORT must be a valid integer, got: %s", grpcPortStr))
	}
	if grpcPort < 1 || grpcPort > 65535 {
		errs = append(errs, fmt.Sprintf("GRPC_PORT must be between 1 and 65535, got: %d", grpcPort))
	}
	c.GRPCPort = grpcPort

	// Required: ENV
	c.Env = os.Getenv("ENV")
	if c.Env == "" {
		c.Env = os.Getenv("GO_ENV")
	}
	if c.Env == "" {
		c.Env = "development"
	}
	if !isValidEnv(c.Env) {
		errs = append(errs, fmt.Sprintf("ENV must be one of: development, staging, production; got: %s", c.Env))
	}

	// Required: DATABASE_URL
	c.DatabaseURL = os.Getenv("DATABASE_URL")
	if c.DatabaseURL == "" {
		errs = append(errs, "DATABASE_URL is required (format: postgres://user:password@host:port/dbname?sslmode=disable)")
	} else if !isValidDatabaseURL(c.DatabaseURL) {
		errs = append(errs, fmt.Sprintf("DATABASE_URL has invalid format: %s (expected: postgres://user:password@host:port/dbname)", c.DatabaseURL))
	}

	// Required: JWT_SECRET
	c.JWTSecret = os.Getenv("JWT_SECRET")
	if c.JWTSecret == "" {
		errs = append(errs, "JWT_SECRET is required (generate with: openssl rand -hex 32)")
	} else if len(c.JWTSecret) < 32 {
		errs = append(errs, fmt.Sprintf("JWT_SECRET must be at least 32 characters, got %d characters", len(c.JWTSecret)))
	}

	// Required: CSRF_SECRET
	c.CSRFSecret = os.Getenv("CSRF_SECRET")
	if c.CSRFSecret == "" {
		errs = append(errs, "CSRF_SECRET is required (generate with: openssl rand -hex 32)")
	} else if len(c.CSRFSecret) < 32 {
		errs = append(errs, fmt.Sprintf("CSRF_SECRET must be at least 32 characters, got %d characters", len(c.CSRFSecret)))
	}

	// Required: REDIS_URL
	c.RedisURL = os.Getenv("REDIS_URL")
	if c.RedisURL == "" {
		c.RedisURL = "redis://localhost:6379"
	}
	if !isValidRedisURL(c.RedisURL) {
		errs = append(errs, fmt.Sprintf("REDIS_URL has invalid format: %s (expected: redis://host:port or rediss://host:port)", c.RedisURL))
	}

	// Required: NATS_URL
	c.NatsURL = os.Getenv("NATS_URL")
	if c.NatsURL == "" {
		c.NatsURL = "nats://localhost:4222"
	}
	if !isValidNatsURL(c.NatsURL) {
		errs = append(errs, fmt.Sprintf("NATS_URL has invalid format: %s (expected: nats://host:port)", c.NatsURL))
	}

	// Required: TEMPORAL_HOST
	c.TemporalHost = os.Getenv("TEMPORAL_HOST")
	if c.TemporalHost == "" {
		errs = append(errs, "TEMPORAL_HOST is required (format: host:port, e.g., localhost:7233)")
	} else if !isValidHostPort(c.TemporalHost) {
		errs = append(errs, fmt.Sprintf("TEMPORAL_HOST has invalid format: %s (expected: host:port)", c.TemporalHost))
	}

	// Optional: PYTHON_BACKEND_URL
	c.PythonBackendURL = os.Getenv("PYTHON_BACKEND_URL")
	if c.PythonBackendURL == "" {
		c.PythonBackendURL = "http://localhost:8000"
	}
	if !isValidURL(c.PythonBackendURL) {
		errs = append(errs, fmt.Sprintf("PYTHON_BACKEND_URL has invalid format: %s (expected: http://host:port)", c.PythonBackendURL))
	}

	// Optional: CORS_ALLOWED_ORIGINS
	c.CorsAllowedOrigins = os.Getenv("CORS_ALLOWED_ORIGINS")
	if c.CorsAllowedOrigins == "" {
		c.CorsAllowedOrigins = "http://localhost:3000,http://localhost:5173"
	}

	// Optional: WorkOS (but recommended for production)
	c.WorkosClientID = os.Getenv("WORKOS_CLIENT_ID")
	c.WorkosAPIKey = os.Getenv("WORKOS_API_KEY")
	if c.Env == "production" {
		if c.WorkosClientID == "" {
			errs = append(errs, "WORKOS_CLIENT_ID is required in production (get from https://dashboard.workos.com/)")
		}
		if c.WorkosAPIKey == "" {
			errs = append(errs, "WORKOS_API_KEY is required in production (get from https://dashboard.workos.com/)")
		}
	}

	// Optional: AI API Keys
	c.OpenAIAPIKey = os.Getenv("OPENAI_API_KEY")
	c.AnthropicAPIKey = os.Getenv("ANTHROPIC_API_KEY")

	if len(errs) > 0 {
		return fmt.Errorf(strings.Join(errs, "\n"))
	}

	return nil
}

// testConnectivity tests critical service connectivity
func (c *EnvConfig) testConnectivity() error {
	var errs []string
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Test Database
	dbCtx, dbCancel := context.WithTimeout(ctx, 5*time.Second)
	if err := testDatabaseConnection(dbCtx, c.DatabaseURL); err != nil {
		errs = append(errs, fmt.Sprintf("Database connectivity failed: %v (DATABASE_URL: %s)", err, c.DatabaseURL))
	}
	dbCancel()

	// Test Redis
	redisCtx, redisCancel := context.WithTimeout(ctx, 5*time.Second)
	if err := testRedisConnection(redisCtx, c.RedisURL); err != nil {
		errs = append(errs, fmt.Sprintf("Redis connectivity failed: %v (REDIS_URL: %s)", err, c.RedisURL))
	}
	redisCancel()

	// Test NATS
	natsCtx, natsCancel := context.WithTimeout(ctx, 5*time.Second)
	if err := testNatsConnection(natsCtx, c.NatsURL); err != nil {
		errs = append(errs, fmt.Sprintf("NATS connectivity failed: %v (NATS_URL: %s)", err, c.NatsURL))
	}
	natsCancel()

	if len(errs) > 0 {
		return fmt.Errorf(strings.Join(errs, "\n"))
	}

	return nil
}

// testDatabaseConnection verifies database connectivity
func testDatabaseConnection(ctx context.Context, databaseURL string) error {
	db, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return fmt.Errorf("failed to open database connection: %w", err)
	}
	defer db.Close()

	if err := db.PingContext(ctx); err != nil {
		return fmt.Errorf("database ping failed: %w", err)
	}

	return nil
}

// testRedisConnection verifies Redis connectivity
func testRedisConnection(ctx context.Context, redisURL string) error {
	client := redis.NewClient(&redis.Options{
		Addr: parseRedisURL(redisURL),
	})
	defer client.Close()

	if err := client.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("redis ping failed: %w", err)
	}

	return nil
}

// testNatsConnection verifies NATS connectivity
func testNatsConnection(ctx context.Context, natsURL string) error {
	// NATS connection is tested when initializing the client
	// For now, just validate the URL format
	if !isValidNatsURL(natsURL) {
		return fmt.Errorf("invalid NATS URL format: %s", natsURL)
	}
	return nil
}

// Validation helpers

func isValidEnv(env string) bool {
	switch env {
	case "development", "staging", "production":
		return true
	default:
		return false
	}
}

func isValidDatabaseURL(dbURL string) bool {
	if !strings.HasPrefix(dbURL, "postgres://") && !strings.HasPrefix(dbURL, "postgresql://") {
		return false
	}
	u, err := url.Parse(dbURL)
	return err == nil && u.Host != "" && u.Path != ""
}

func isValidRedisURL(redisURL string) bool {
	return strings.HasPrefix(redisURL, "redis://") || strings.HasPrefix(redisURL, "rediss://")
}

func isValidNatsURL(natsURL string) bool {
	return strings.HasPrefix(natsURL, "nats://")
}

func isValidHostPort(hostPort string) bool {
	parts := strings.Split(hostPort, ":")
	if len(parts) != 2 {
		return false
	}
	port, err := strconv.Atoi(parts[1])
	return err == nil && port > 0 && port < 65536
}

func isValidURL(urlStr string) bool {
	u, err := url.Parse(urlStr)
	return err == nil && u.Host != ""
}

func parseRedisURL(redisURL string) string {
	// Extract host:port from redis://host:port
	urlStr := strings.TrimPrefix(redisURL, "redis://")
	urlStr = strings.TrimPrefix(urlStr, "rediss://")
	return urlStr
}

// init runs preflight checks on startup
func init() {
	// Only run in actual program, not in tests
	if os.Getenv("SKIP_PREFLIGHT") != "true" {
		if err := PreflightCheck(); err != nil {
			fmt.Fprintf(os.Stderr, "FATAL: Preflight checks failed:\n%v\n", err)
			os.Exit(1)
		}
	}
}
