package observability

import (
	"testing"

	"github.com/kooshapari/tracera/backend/internal/config"
)

func TestFromConfigBuildsCollectorContract(t *testing.T) {
	cfg := &config.Config{
		CollectorEndpoint:     "  collector:4317 ",
		CollectorHTTPEndpoint: " http://collector:4318 ",
		TracingEnabled:        true,
		TracingEnvironment:    " production ",
		TracingServiceName:    " tracera-api ",
	}

	otel := FromConfig(cfg)
	if !otel.Enabled || otel.ServiceName != "tracera-api" || otel.Environment != "production" {
		t.Fatalf("unexpected collector metadata: %#v", otel)
	}
	if otel.GRPCEndpoint != "collector:4317" || otel.HTTPEndpoint != "http://collector:4318" {
		t.Fatalf("unexpected collector endpoints: %#v", otel)
	}
}

func TestCollectorEnvUsesStandardOTELKeys(t *testing.T) {
	otel := OTELCollectorConfig{
		Enabled:      true,
		ServiceName:  "tracera-live-backend",
		Environment:  "staging",
		GRPCEndpoint: "otel-collector:4317",
		HTTPEndpoint: "http://otel-collector:4318",
	}

	env := otel.Env()
	assertEnv(t, env, "OTEL_SDK_DISABLED", "false")
	assertEnv(t, env, "OTEL_SERVICE_NAME", "tracera-live-backend")
	assertEnv(t, env, "OTEL_RESOURCE_ATTRIBUTES", "deployment.environment=staging")
	assertEnv(t, env, "OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector:4317")
	assertEnv(t, env, "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "otel-collector:4317")
	assertEnv(t, env, "OTEL_EXPORTER_OTLP_HTTP_ENDPOINT", "http://otel-collector:4318")
}

func TestDisabledCollectorDisablesSDK(t *testing.T) {
	env := (OTELCollectorConfig{Enabled: false}).Env()
	if len(env) != 1 {
		t.Fatalf("disabled env should only contain SDK flag: %#v", env)
	}
	assertEnv(t, env, "OTEL_SDK_DISABLED", "true")
}

func assertEnv(t *testing.T, env map[string]string, key string, want string) {
	t.Helper()
	if got := env[key]; got != want {
		t.Fatalf("%s = %q, want %q", key, got, want)
	}
}
