//go:build !integration

package tracing

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.opentelemetry.io/otel/baggage"
)

func TestPropagateContext(t *testing.T) {
	sourceCtx := context.Background()
	newCtx := PropagateContext(sourceCtx)

	assert.NotNil(t, newCtx)
	// Context should be created without error
}

func TestWithTraceID(t *testing.T) {
	ctx := context.Background()
	traceID := "abc123"

	newCtx, err := WithTraceID(ctx, traceID)
	require.NoError(t, err)
	require.NotNil(t, newCtx)

	// Verify baggage contains trace ID
	bag := baggage.FromContext(newCtx)
	member := bag.Member("trace.id")
	assert.Equal(t, traceID, member.Value())
}

func TestWithUserID(t *testing.T) {
	ctx := context.Background()
	userID := "user123"

	newCtx, err := WithUserID(ctx, userID)
	require.NoError(t, err)
	require.NotNil(t, newCtx)

	// Verify baggage contains user ID
	bag := baggage.FromContext(newCtx)
	member := bag.Member("user.id")
	assert.Equal(t, userID, member.Value())
}

func TestWithProjectID(t *testing.T) {
	ctx := context.Background()
	projectID := "proj456"

	newCtx, err := WithProjectID(ctx, projectID)
	require.NoError(t, err)
	require.NotNil(t, newCtx)

	// Verify baggage contains project ID
	bag := baggage.FromContext(newCtx)
	member := bag.Member("project.id")
	assert.Equal(t, projectID, member.Value())
}

func TestWithMultipleBaggage(t *testing.T) {
	ctx := context.Background()

	// Add multiple baggage items
	ctx, err := WithTraceID(ctx, "trace123")
	require.NoError(t, err)

	ctx, err = WithUserID(ctx, "user456")
	require.NoError(t, err)

	ctx, err = WithProjectID(ctx, "proj789")
	require.NoError(t, err)

	// Verify all baggage items are present
	bag := baggage.FromContext(ctx)

	assert.Equal(t, "trace123", bag.Member("trace.id").Value())
	assert.Equal(t, "user456", bag.Member("user.id").Value())
	assert.Equal(t, "proj789", bag.Member("project.id").Value())
}

func TestGetTraceID_NoTrace(t *testing.T) {
	ctx := context.Background()
	traceID := GetTraceID(ctx)

	// Should return empty string if no active trace
	assert.Empty(t, traceID)
}

func TestGetSpanID_NoTrace(t *testing.T) {
	ctx := context.Background()
	spanID := GetSpanID(ctx)

	// Should return empty string if no active trace
	assert.Empty(t, spanID)
}

func TestIsTraceActive_Inactive(t *testing.T) {
	ctx := context.Background()
	active := IsTraceActive(ctx)

	assert.False(t, active)
}

func TestWrapAsync(t *testing.T) {
	sourceCtx := context.Background()
	asyncCtx := WrapAsync(sourceCtx)

	assert.NotNil(t, asyncCtx)
	// Context should be properly propagated
}

func TestWrapAsync_WithBaggage(t *testing.T) {
	ctx := context.Background()

	// Add baggage to source context
	ctx, err := WithUserID(ctx, "user123")
	require.NoError(t, err)

	// Wrap for async operation
	asyncCtx := WrapAsync(ctx)
	assert.NotNil(t, asyncCtx)
}

func TestBaggageChaining(t *testing.T) {
	ctx := context.Background()

	// Chain multiple baggage additions
	newCtx, err := WithTraceID(ctx, "trace1")
	require.NoError(t, err)

	newCtx, err = WithUserID(newCtx, "user1")
	require.NoError(t, err)

	newCtx, err = WithProjectID(newCtx, "proj1")
	require.NoError(t, err)

	// All should be present
	bag := baggage.FromContext(newCtx)
	assert.NotEmpty(t, bag.Member("trace.id").Value())
	assert.NotEmpty(t, bag.Member("user.id").Value())
	assert.NotEmpty(t, bag.Member("project.id").Value())
}
