// Package observability prepares OpenTelemetry collector wiring for the live backend.
package observability

import (
	"strings"

	"github.com/kooshapari/tracera/backend/internal/config"
)

// OTELCollectorConfig is the backend-facing collector contract.
type OTELCollectorConfig struct {
	Enabled      bool
	ServiceName  string
	Environment  string
	GRPCEndpoint string
	HTTPEndpoint string
}

// FromConfig derives the OTel collector wiring from application config.
func FromConfig(cfg *config.Config) OTELCollectorConfig {
	if cfg == nil {
		return OTELCollectorConfig{}
	}
	return OTELCollectorConfig{
		Enabled:      cfg.TracingEnabled,
		ServiceName:  strings.TrimSpace(cfg.TracingServiceName),
		Environment:  strings.TrimSpace(cfg.TracingEnvironment),
		GRPCEndpoint: strings.TrimSpace(cfg.CollectorEndpoint),
		HTTPEndpoint: strings.TrimSpace(cfg.CollectorHTTPEndpoint),
	}
}

// Env returns standard OTEL environment values for processes launched by the backend.
func (c OTELCollectorConfig) Env() map[string]string {
	if !c.Enabled {
		return map[string]string{"OTEL_SDK_DISABLED": "true"}
	}

	env := map[string]string{
		"OTEL_SDK_DISABLED":        "false",
		"OTEL_SERVICE_NAME":        c.ServiceName,
		"OTEL_RESOURCE_ATTRIBUTES": "deployment.environment=" + c.Environment,
	}
	if c.GRPCEndpoint != "" {
		env["OTEL_EXPORTER_OTLP_ENDPOINT"] = c.GRPCEndpoint
		env["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = c.GRPCEndpoint
	}
	if c.HTTPEndpoint != "" {
		env["OTEL_EXPORTER_OTLP_HTTP_ENDPOINT"] = c.HTTPEndpoint
	}
	return env
}
