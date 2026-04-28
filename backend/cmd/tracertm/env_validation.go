package main

import (
	"errors"
	"fmt"
	"net/url"
	"os"
	"strconv"
	"strings"
)

// loadFromEnv loads and validates environment variables
func (cfg *EnvConfig) loadFromEnv() error {
	var errs []string

	cfg.validateServer(&errs)
	cfg.validateDatabase(&errs)
	cfg.validateSecurity(&errs)
	cfg.validateRedis(&errs)
	cfg.validateNats(&errs)
	cfg.validateTemporal(&errs)
	cfg.validateExternalServices(&errs)
	cfg.validateAIKeys(&errs)

	if len(errs) > 0 {
		return errors.New(strings.Join(errs, "\n"))
	}

	return nil
}

func (cfg *EnvConfig) validateServer(errs *[]string) {
	cfg.validatePort(errs)
	cfg.validateEnv(errs)
}

func (cfg *EnvConfig) validatePort(errs *[]string) {
	portStr := os.Getenv("PORT")
	if portStr == "" {
		portStr = "8080"
	}
	port, err := strconv.Atoi(portStr)
	if err != nil {
		*errs = append(*errs, "PORT must be a valid integer, got: "+portStr)
	}
	if port < 1 || port > 65535 {
		*errs = append(*errs, fmt.Sprintf("PORT must be between 1 and 65535, got: %d", port))
	}
	cfg.Port = port

	grpcPortStr := os.Getenv("GRPC_PORT")
	if grpcPortStr == "" {
		grpcPortStr = "9090"
	}
	grpcPort, err := strconv.Atoi(grpcPortStr)
	if err != nil {
		*errs = append(*errs, "GRPC_PORT must be a valid integer, got: "+grpcPortStr)
	}
	if grpcPort < 1 || grpcPort > 65535 {
		*errs = append(*errs, fmt.Sprintf("GRPC_PORT must be between 1 and 65535, got: %d", grpcPort))
	}
	cfg.GRPCPort = grpcPort
}

func (cfg *EnvConfig) validateEnv(errs *[]string) {
	cfg.Env = os.Getenv("ENV")
	if cfg.Env == "" {
		cfg.Env = os.Getenv("GO_ENV")
	}
	if cfg.Env == "" {
		cfg.Env = "development"
	}
	if !isValidEnv(cfg.Env) {
		*errs = append(*errs, "ENV must be one of: development, staging, production; got: "+cfg.Env)
	}
}

func (cfg *EnvConfig) validateDatabase(errs *[]string) {
	cfg.DatabaseURL = os.Getenv("DATABASE_URL")
	if cfg.DatabaseURL == "" {
		*errs = append(*errs, "DATABASE_URL is required (format: postgres://user:password@host:port/dbname)")
	} else if !isValidDatabaseURL(cfg.DatabaseURL) {
		*errs = append(*errs, "DATABASE_URL has invalid format: "+cfg.DatabaseURL)
	}
}

func (cfg *EnvConfig) validateSecurity(errs *[]string) {
	cfg.JWTSecret = os.Getenv("JWT_SECRET")
	if cfg.JWTSecret == "" {
		*errs = append(*errs, "JWT_SECRET is required (generate with: openssl rand -hex 32)")
	} else if len(cfg.JWTSecret) < 32 {
		*errs = append(*errs, fmt.Sprintf("JWT_SECRET must be at least 32 characters, got %d", len(cfg.JWTSecret)))
	}

	cfg.CSRFSecret = os.Getenv("CSRF_SECRET")
	if cfg.CSRFSecret == "" {
		*errs = append(*errs, "CSRF_SECRET is required (generate with: openssl rand -hex 32)")
	} else if len(cfg.CSRFSecret) < 32 {
		*errs = append(*errs, fmt.Sprintf("CSRF_SECRET must be at least 32 characters, got %d", len(cfg.CSRFSecret)))
	}
}

func (cfg *EnvConfig) validateRedis(errs *[]string) {
	cfg.RedisURL = os.Getenv("REDIS_URL")
	if cfg.RedisURL == "" {
		cfg.RedisURL = "redis://localhost:6379"
	}
	if !isValidRedisURL(cfg.RedisURL) {
		*errs = append(*errs, "REDIS_URL has invalid format (expected redis://host:port): "+cfg.RedisURL)
	}
}

func (cfg *EnvConfig) validateNats(errs *[]string) {
	cfg.NatsURL = os.Getenv("NATS_URL")
	if cfg.NatsURL == "" {
		cfg.NatsURL = "nats://localhost:4222"
	}
	if !isValidNatsURL(cfg.NatsURL) {
		*errs = append(*errs, fmt.Sprintf("NATS_URL has invalid format: %s (expected: nats://host:port)", cfg.NatsURL))
	}
}

func (cfg *EnvConfig) validateTemporal(errs *[]string) {
	cfg.TemporalHost = os.Getenv("TEMPORAL_HOST")
	if cfg.TemporalHost == "" {
		*errs = append(*errs, "TEMPORAL_HOST is required (format: host:port, e.g., localhost:7233)")
	} else if !isValidHostPort(cfg.TemporalHost) {
		*errs = append(*errs, "TEMPORAL_HOST has invalid format: "+cfg.TemporalHost)
	}
}

func (cfg *EnvConfig) validateExternalServices(errs *[]string) {
	cfg.PythonBackendURL = os.Getenv("PYTHON_BACKEND_URL")
	if cfg.PythonBackendURL == "" {
		cfg.PythonBackendURL = "http://localhost:8000"
	}
	if !isValidURL(cfg.PythonBackendURL) {
		*errs = append(*errs, "PYTHON_BACKEND_URL has invalid format: "+cfg.PythonBackendURL)
	}

	cfg.CorsAllowedOrigins = os.Getenv("CORS_ALLOWED_ORIGINS")
	if cfg.CorsAllowedOrigins == "" {
		cfg.CorsAllowedOrigins = "http://localhost:3000,http://localhost:5173"
	}

	cfg.WorkosClientID = os.Getenv("WORKOS_CLIENT_ID")
	cfg.WorkosAPIKey = os.Getenv("WORKOS_API_KEY")
	if cfg.Env == "production" {
		if cfg.WorkosClientID == "" {
			*errs = append(*errs, "WORKOS_CLIENT_ID is required in production")
		}
		if cfg.WorkosAPIKey == "" {
			*errs = append(*errs, "WORKOS_API_KEY is required in production")
		}
	}
}

func (cfg *EnvConfig) validateAIKeys(errs *[]string) {
	cfg.OpenAIAPIKey = os.Getenv("OPENAI_API_KEY")
	cfg.AnthropicAPIKey = os.Getenv("ANTHROPIC_API_KEY")
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
