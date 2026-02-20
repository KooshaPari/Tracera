package tracing

import (
	"context"
	"strconv"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
)

// HTTP status code threshold for error span status
const httpStatusErrorThreshold = 400

// tracer returns the OpenTelemetry tracer for this application.
func tracer() trace.Tracer {
	return otel.Tracer("tracertm-backend")
}

// StartSpan starts a new span with the given name and options
func StartSpan(ctx context.Context, spanName string, opts ...trace.SpanStartOption) (context.Context, trace.Span) {
	return tracer().Start(ctx, spanName, opts...)
}

// RecordError records an error on the span and sets the span status to error
func RecordError(span trace.Span, err error) {
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
	}
}

// SetAttributes sets multiple attributes on the span
func SetAttributes(span trace.Span, attrs ...attribute.KeyValue) {
	span.SetAttributes(attrs...)
}

// AddEvent adds an event to the span
func AddEvent(span trace.Span, name string, attrs ...attribute.KeyValue) {
	span.AddEvent(name, trace.WithAttributes(attrs...))
}

// DatabaseSpan creates a span for database operations
func DatabaseSpan(ctx context.Context, operation string, table string) (context.Context, trace.Span) {
	spanName := "db." + table + "." + operation
	ctx, span := StartSpan(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindClient),
	)

	SetAttributes(span,
		attribute.String("db.system", "postgresql"),
		attribute.String("db.operation", operation),
		attribute.String("db.table", table),
	)

	return ctx, span
}

// HTTPSpan creates a span for HTTP operations
func HTTPSpan(ctx context.Context, method string, path string) (context.Context, trace.Span) {
	spanName := "HTTP " + method + " " + path
	ctx, span := StartSpan(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindServer),
	)

	SetAttributes(span,
		attribute.String("http.method", method),
		attribute.String("http.target", path),
	)

	return ctx, span
}

// CacheSpan creates a span for cache operations
func CacheSpan(ctx context.Context, operation string, key string) (context.Context, trace.Span) {
	spanName := "cache." + operation
	ctx, span := StartSpan(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindClient),
	)

	SetAttributes(span,
		attribute.String("cache.system", "redis"),
		attribute.String("cache.operation", operation),
		attribute.String("cache.key", key),
	)

	return ctx, span
}

// NATSSpan creates a span for NATS operations
func NATSSpan(ctx context.Context, operation string, subject string) (context.Context, trace.Span) {
	spanName := "nats." + operation
	ctx, span := StartSpan(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindProducer),
	)

	SetAttributes(span,
		attribute.String("messaging.system", "nats"),
		attribute.String("messaging.operation", operation),
		attribute.String("messaging.destination", subject),
	)

	return ctx, span
}

// GraphSpan creates a span for graph database operations
func GraphSpan(ctx context.Context, operation string, query string) (context.Context, trace.Span) {
	spanName := "graph." + operation
	ctx, span := StartSpan(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindClient),
	)

	SetAttributes(span,
		attribute.String("db.system", "neo4j"),
		attribute.String("db.operation", operation),
		attribute.String("db.statement", query),
	)

	return ctx, span
}

// TemporalSpan creates a span for Temporal operations
func TemporalSpan(ctx context.Context, workflowType string, workflowID string) (context.Context, trace.Span) {
	spanName := "temporal.workflow." + workflowType
	ctx, span := StartSpan(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindClient),
	)

	SetAttributes(span,
		attribute.String("workflow.type", workflowType),
		attribute.String("workflow.id", workflowID),
	)

	return ctx, span
}

// AIAgentSpan creates a span for AI agent operations
func AIAgentSpan(ctx context.Context, agentType string, operation string) (context.Context, trace.Span) {
	spanName := "agent." + agentType + "." + operation
	ctx, span := StartSpan(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindInternal),
	)

	SetAttributes(span,
		attribute.String("agent.type", agentType),
		attribute.String("agent.operation", operation),
	)

	return ctx, span
}

// SetHTTPStatus sets HTTP status code on the span
func SetHTTPStatus(span trace.Span, statusCode int) {
	span.SetAttributes(attribute.Int("http.status_code", statusCode))

	// Set span status based on HTTP status code
	switch {
	case statusCode >= httpStatusErrorThreshold:
		span.SetStatus(codes.Error, "HTTP "+strconv.Itoa(statusCode))
	default:
		span.SetStatus(codes.Ok, "")
	}
}

// SetUserID sets user ID on the span for better debugging
func SetUserID(span trace.Span, userID string) {
	if userID != "" {
		span.SetAttributes(attribute.String("user.id", userID))
	}
}

// SetProjectID sets project ID on the span
func SetProjectID(span trace.Span, projectID string) {
	if projectID != "" {
		span.SetAttributes(attribute.String("project.id", projectID))
	}
}
