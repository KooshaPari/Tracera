package tracing

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.27.0"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

const (
	serviceName    = "tracertm-backend"
	serviceVersion = "1.0.0"

	otlpExportTimeout        = 5 * time.Second
	batchExportTimeout       = 5 * time.Second
	tracerShutdownTimeout    = 10 * time.Second
	tracerFlushTimeout       = 5 * time.Second
	tracerMaxExportBatchSize = 512
	tracerMaxQueueSize       = 2048
)

// TracerProvider wraps the OpenTelemetry tracer provider for lifecycle management
type TracerProvider struct {
	provider *sdktrace.TracerProvider
}

// InitTracer initializes the OpenTelemetry tracer with the shared OTLP collector.
func InitTracer(ctx context.Context, collectorEndpoint string, environment string) (*TracerProvider, error) {
	// Set default endpoint if not provided
	if collectorEndpoint == "" {
		collectorEndpoint = "127.0.0.1:4317"
	}

	// Set default environment if not provided
	if environment == "" {
		environment = "development"
	}

	slog.Info(
		"🔍 Initializing distributed tracing",
		"collector_endpoint",
		collectorEndpoint,
		"environment",
		environment,
	)

	// Create OTLP/gRPC exporter for the shared collector.
	exporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(collectorEndpoint),
		otlptracegrpc.WithInsecure(), // Use insecure for native local development
		otlptracegrpc.WithDialOption(grpc.WithTransportCredentials(insecure.NewCredentials())),
		otlptracegrpc.WithTimeout(otlpExportTimeout),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create OTLP exporter: %w", err)
	}

	// Create resource with service information
	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceNameKey.String(serviceName),
			semconv.ServiceVersionKey.String(serviceVersion),
			attribute.String("deployment.environment", environment),
			attribute.String("library.language", "go"),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	// Create tracer provider with batch span processor
	// BatchSpanProcessor is more efficient than SimpleSpanProcessor for production
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter,
			sdktrace.WithMaxExportBatchSize(tracerMaxExportBatchSize),
			sdktrace.WithBatchTimeout(batchExportTimeout),
			sdktrace.WithMaxQueueSize(tracerMaxQueueSize),
		),
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.AlwaysSample()), // Sample all traces in development
	)

	// Register the tracer provider globally
	otel.SetTracerProvider(tp)

	// Set global propagator to tracecontext (W3C Trace Context)
	// This ensures trace context is propagated across service boundaries
	otel.SetTextMapPropagator(
		propagation.NewCompositeTextMapPropagator(
			propagation.TraceContext{},
			propagation.Baggage{},
		),
	)

	slog.Info("✅ Distributed tracing initialized successfully")

	return &TracerProvider{provider: tp}, nil
}

// Shutdown gracefully shuts down the tracer provider
func (tp *TracerProvider) Shutdown(ctx context.Context) error {
	if tp.provider == nil {
		return nil
	}

	slog.Debug("🔍 Shutting down tracer provider...")

	// Create a timeout context for shutdown
	shutdownCtx, cancel := context.WithTimeout(ctx, tracerShutdownTimeout)
	defer cancel()

	if err := tp.provider.Shutdown(shutdownCtx); err != nil {
		return fmt.Errorf("failed to shutdown tracer provider: %w", err)
	}

	slog.Debug("✅ Tracer provider shut down successfully")
	return nil
}

// ForceFlush forces all pending spans to be exported
func (tp *TracerProvider) ForceFlush(ctx context.Context) error {
	if tp.provider == nil {
		return nil
	}

	// Create a timeout context for flush
	flushCtx, cancel := context.WithTimeout(ctx, tracerFlushTimeout)
	defer cancel()

	if err := tp.provider.ForceFlush(flushCtx); err != nil {
		return fmt.Errorf("failed to flush tracer provider: %w", err)
	}

	return nil
}
