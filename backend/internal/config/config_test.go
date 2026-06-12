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
