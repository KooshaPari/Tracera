package config

import "testing"

func TestLoadConfigOTelCollectorDefaults(t *testing.T) {
	t.Setenv("DATABASE_URL", "postgres://example")
	t.Setenv("JWT_SECRET", "secret")
	t.Setenv("NEO4J_PASSWORD", "neo4j")
	t.Setenv("ENV", "production")

	cfg := LoadConfig()
	if cfg.CollectorEndpoint != "127.0.0.1:4317" {
		t.Fatalf("CollectorEndpoint = %q", cfg.CollectorEndpoint)
	}
	if cfg.CollectorHTTPEndpoint != "http://127.0.0.1:4318" {
		t.Fatalf("CollectorHTTPEndpoint = %q", cfg.CollectorHTTPEndpoint)
	}
	if cfg.TracingEnvironment != "production" {
		t.Fatalf("TracingEnvironment = %q", cfg.TracingEnvironment)
	}
	if cfg.TracingServiceName != "tracera-live-backend" {
		t.Fatalf("TracingServiceName = %q", cfg.TracingServiceName)
	}
}

func TestLoadConfigOTelCollectorOverrides(t *testing.T) {
	t.Setenv("DATABASE_URL", "postgres://example")
	t.Setenv("JWT_SECRET", "secret")
	t.Setenv("NEO4J_PASSWORD", "neo4j")
	t.Setenv("PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT", "collector:4317")
	t.Setenv("PHENO_OBSERVABILITY_OTLP_HTTP_ENDPOINT", "http://collector:4318")
	t.Setenv("TRACING_ENABLED", "false")
	t.Setenv("TRACING_ENVIRONMENT", "staging")
	t.Setenv("OTEL_SERVICE_NAME", "tracera-api")

	cfg := LoadConfig()
	if cfg.CollectorEndpoint != "collector:4317" {
		t.Fatalf("CollectorEndpoint = %q", cfg.CollectorEndpoint)
	}
	if cfg.CollectorHTTPEndpoint != "http://collector:4318" {
		t.Fatalf("CollectorHTTPEndpoint = %q", cfg.CollectorHTTPEndpoint)
	}
	if cfg.TracingEnabled {
		t.Fatal("TracingEnabled = true")
	}
	if cfg.TracingEnvironment != "staging" || cfg.TracingServiceName != "tracera-api" {
		t.Fatalf("unexpected tracing metadata: %#v", cfg)
	}
}

func TestLoadConfigPreflightDefaults(t *testing.T) {
	t.Setenv("DATABASE_URL", "postgres://example")
	t.Setenv("JWT_SECRET", "secret")
	t.Setenv("NEO4J_PASSWORD", "neo4j")

	cfg := LoadConfig()
	if cfg.PreflightCheckTimeout != 2 {
		t.Fatalf("PreflightCheckTimeout = %d, want 2", cfg.PreflightCheckTimeout)
	}
	if cfg.PreflightPythonTimeout != 5 {
		t.Fatalf("PreflightPythonTimeout = %d, want 5", cfg.PreflightPythonTimeout)
	}
	if cfg.WorkOSAPIBaseURL != "https://api.workos.com" {
		t.Fatalf("WorkOSAPIBaseURL = %q, want https://api.workos.com", cfg.WorkOSAPIBaseURL)
	}
	if cfg.TemporalHost != "localhost:7233" {
		t.Fatalf("TemporalHost = %q, want localhost:7233", cfg.TemporalHost)
	}
	if cfg.TemporalNamespace != "default" {
		t.Fatalf("TemporalNamespace = %q, want default", cfg.TemporalNamespace)
	}
}

func TestLoadConfigPreflightOverrides(t *testing.T) {
	t.Setenv("DATABASE_URL", "postgres://example")
	t.Setenv("JWT_SECRET", "secret")
	t.Setenv("NEO4J_PASSWORD", "neo4j")
	t.Setenv("PREFLIGHT_CHECK_TIMEOUT_SECONDS", "10")
	t.Setenv("PREFLIGHT_PYTHON_TIMEOUT_SECONDS", "15")
	t.Setenv("WORKOS_API_BASE_URL", "https://api.workos.test")
	t.Setenv("TEMPORAL_HOST", "temporal.internal:8233")
	t.Setenv("TEMPORAL_NAMESPACE", "production")
	t.Setenv("DEFAULT_POSTGRES_PORT", "5433")
	t.Setenv("DEFAULT_REDIS_PORT", "6380")

	cfg := LoadConfig()
	if cfg.PreflightCheckTimeout != 10 {
		t.Fatalf("PreflightCheckTimeout = %d, want 10", cfg.PreflightCheckTimeout)
	}
	if cfg.PreflightPythonTimeout != 15 {
		t.Fatalf("PreflightPythonTimeout = %d, want 15", cfg.PreflightPythonTimeout)
	}
	if cfg.WorkOSAPIBaseURL != "https://api.workos.test" {
		t.Fatalf("WorkOSAPIBaseURL = %q, want https://api.workos.test", cfg.WorkOSAPIBaseURL)
	}
	if cfg.TemporalHost != "temporal.internal:8233" {
		t.Fatalf("TemporalHost = %q, want temporal.internal:8233", cfg.TemporalHost)
	}
	if cfg.TemporalNamespace != "production" {
		t.Fatalf("TemporalNamespace = %q, want production", cfg.TemporalNamespace)
	}
	if cfg.DefaultPostgresPort != "5433" {
		t.Fatalf("DefaultPostgresPort = %q, want 5433", cfg.DefaultPostgresPort)
	}
	if cfg.DefaultRedisPort != "6380" {
		t.Fatalf("DefaultRedisPort = %q, want 6380", cfg.DefaultRedisPort)
	}
}
