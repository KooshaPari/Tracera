package main

import (
	"fmt"
	"os"
)

// PreflightCheck validates all required environment variables and connectivity
func PreflightCheck() error {
	cfg := &EnvConfig{
		Port:               0,
		GRPCPort:           0,
		Env:                "",
		DatabaseURL:        "",
		JWTSecret:          "",
		CSRFSecret:         "",
		RedisURL:           "",
		NatsURL:            "",
		WorkosClientID:     "",
		WorkosAPIKey:       "",
		CorsAllowedOrigins: "",
		TemporalHost:       "",
		PythonBackendURL:   "",
		OpenAIAPIKey:       "",
		AnthropicAPIKey:    "",
	}

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
