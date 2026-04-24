package tracing

import (
	"context"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/baggage"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/trace"
)

// PropagateContext extracts trace context from one context and injects it into another.
// This is useful for cross-service or async operations where context needs to be preserved.
func PropagateContext(sourceCtx context.Context) context.Context {
	// Get the current propagator
	propagator := otel.GetTextMapPropagator()

	// Create a carrier to hold propagated values
	carrier := propagation.MapCarrier{}

	// Inject trace context into the carrier
	propagator.Inject(sourceCtx, carrier)

	// Create a new context with the carrier values
	newCtx := context.Background()
	return propagator.Extract(newCtx, carrier)
}

// WithTraceID adds a trace ID to the context baggage for logging and debugging.
// The trace ID will be automatically included in all spans created from this context.
func WithTraceID(ctx context.Context, traceID string) (context.Context, error) {
	member, err := baggage.NewMember("trace.id", traceID)
	if err != nil {
		return ctx, err
	}

	b, err := baggage.New(member)
	if err != nil {
		return ctx, err
	}

	return baggage.ContextWithBaggage(ctx, b), nil
}

// WithUserID adds a user ID to the context baggage.
// This is useful for correlating traces with specific users.
func WithUserID(ctx context.Context, userID string) (context.Context, error) {
	existingBag := baggage.FromContext(ctx)
	member, err := baggage.NewMember("user.id", userID)
	if err != nil {
		return ctx, err
	}

	newBag, err := existingBag.SetMember(member)
	if err != nil {
		return ctx, err
	}

	return baggage.ContextWithBaggage(ctx, newBag), nil
}

// WithProjectID adds a project ID to the context baggage.
func WithProjectID(ctx context.Context, projectID string) (context.Context, error) {
	existingBag := baggage.FromContext(ctx)
	member, err := baggage.NewMember("project.id", projectID)
	if err != nil {
		return ctx, err
	}

	newBag, err := existingBag.SetMember(member)
	if err != nil {
		return ctx, err
	}

	return baggage.ContextWithBaggage(ctx, newBag), nil
}

// GetTraceID extracts the trace ID from the current span context.
// Returns empty string if no trace is active.
func GetTraceID(ctx context.Context) string {
	span := trace.SpanFromContext(ctx)
	if !span.IsRecording() {
		return ""
	}
	return span.SpanContext().TraceID().String()
}

// GetSpanID extracts the span ID from the current span context.
// Returns empty string if no span is active.
func GetSpanID(ctx context.Context) string {
	span := trace.SpanFromContext(ctx)
	if !span.IsRecording() {
		return ""
	}
	return span.SpanContext().SpanID().String()
}

// IsTraceActive checks if a trace is currently active in the context.
func IsTraceActive(ctx context.Context) bool {
	span := trace.SpanFromContext(ctx)
	return span.IsRecording()
}

// WrapAsync wraps an async operation by propagating trace context to a new context.
// This is useful for goroutines and async tasks that need to maintain trace continuity.
func WrapAsync(ctx context.Context) context.Context {
	// Create a new context that preserves trace context
	return PropagateContext(ctx)
}
