// Package main provides preflight checks for the tracertm application.
package main

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
