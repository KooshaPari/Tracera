package tracing

import (
	"context"
	"errors"

	"go.opentelemetry.io/otel/attribute"
)

// ExampleDatabaseOperation demonstrates how to instrument a database operation with tracing
func ExampleDatabaseOperation(ctx context.Context, userID, query string) error {
	// Start a database span
	_, span := DatabaseSpan(ctx, "SELECT", "users")
	defer span.End()

	// Add additional attributes
	SetAttributes(span,
		attribute.String("db.query", query),
		attribute.String("user.id", userID),
	)

	// Simulate database operation
	// ... actual database call here ...

	// Record an event
	AddEvent(span, "query_executed", attribute.Int("rows_affected", 1))

	return nil
}

// ExampleCacheOperation demonstrates how to instrument a cache operation with tracing
func ExampleCacheOperation(ctx context.Context, key string, _ interface{}) error {
	// Start a cache span
	_, span := CacheSpan(ctx, "GET", key)
	defer span.End()

	// Simulate cache operation
	// ... actual cache call here ...

	// Add cache hit/miss information
	SetAttributes(span, attribute.Bool("cache.hit", true))

	return nil
}

// ExampleNATSPublish demonstrates how to instrument NATS publishing with tracing
func ExampleNATSPublish(ctx context.Context, subject string, message []byte) error {
	// Start a NATS span
	_, span := NATSSpan(ctx, "PUBLISH", subject)
	defer span.End()

	// Add message metadata
	SetAttributes(span,
		attribute.Int("message.size", len(message)),
		attribute.String("message.subject", subject),
	)

	// Simulate NATS publish
	// ... actual NATS publish here ...

	return nil
}

// ExampleNestedOperations demonstrates how to create nested spans for complex operations
func ExampleNestedOperations(ctx context.Context, projectID string) error {
	// Parent span for the entire operation
	ctx, parentSpan := StartSpan(ctx, "complex_operation")
	defer parentSpan.End()

	SetProjectID(parentSpan, projectID)

	// Child span for database query
	{
		_, dbSpan := DatabaseSpan(ctx, "SELECT", "projects")
		defer dbSpan.End()

		// Database operation...
		AddEvent(dbSpan, "project_loaded")
	}

	// Child span for cache update
	{
		_, cacheSpan := CacheSpan(ctx, "SET", "project:"+projectID)
		defer cacheSpan.End()

		// Cache operation...
	}

	// Child span for NATS event
	{
		_, natsSpan := NATSSpan(ctx, "PUBLISH", "project.updated")
		defer natsSpan.End()

		// Event publish...
	}

	return nil
}

// ExampleErrorHandling demonstrates how to record errors in spans
func ExampleErrorHandling(ctx context.Context) error {
	_, span := StartSpan(ctx, "operation_with_error")
	defer span.End()

	// Simulate an error
	err := errors.New("something went wrong")
	if err != nil {
		// Record the error on the span
		RecordError(span, err)
		return err
	}

	return nil
}

// ExampleAIAgentOperation demonstrates how to instrument AI agent operations
func ExampleAIAgentOperation(ctx context.Context, agentType string, prompt string) (string, error) {
	// Start AI agent span
	_, span := AIAgentSpan(ctx, agentType, "generate")
	defer span.End()

	// Add prompt metadata
	SetAttributes(span,
		attribute.String("ai.prompt", prompt),
		attribute.Int("ai.prompt_length", len(prompt)),
	)

	// Simulate AI operation
	response := "AI generated response"

	// Add response metadata
	SetAttributes(span,
		attribute.String("ai.response", response),
		attribute.Int("ai.response_length", len(response)),
	)

	AddEvent(span, "ai_generation_complete")

	return response, nil
}
