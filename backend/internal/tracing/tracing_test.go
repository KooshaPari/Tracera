//go:build !integration

package tracing

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.opentelemetry.io/otel/trace"
	"go.opentelemetry.io/otel/trace/noop"
)

func TestStartSpan(t *testing.T) {
	ctx := context.Background()
	newCtx, span := StartSpan(ctx, "test-span")

	require.NotNil(t, span)
	require.NotNil(t, newCtx)
	defer span.End()
}

func TestRecordError_WithError(t *testing.T) {
	_, span := noop.NewTracerProvider().Tracer("test").Start(context.Background(), "test")
	defer span.End()

	// Should not panic
	assert.NotPanics(t, func() {
		RecordError(span, errors.New("test error"))
	})
}

func TestRecordError_NilError(t *testing.T) {
	_, span := noop.NewTracerProvider().Tracer("test").Start(context.Background(), "test")
	defer span.End()

	assert.NotPanics(t, func() {
		RecordError(span, nil)
	})
}

func TestSetAttributes(t *testing.T) {
	_, span := noop.NewTracerProvider().Tracer("test").Start(context.Background(), "test")
	defer span.End()

	assert.NotPanics(t, func() {
		SetAttributes(span)
	})
}

func TestAddEvent(t *testing.T) {
	_, span := noop.NewTracerProvider().Tracer("test").Start(context.Background(), "test")
	defer span.End()

	assert.NotPanics(t, func() {
		AddEvent(span, "test-event")
	})
}

func TestDatabaseSpan(t *testing.T) {
	ctx, span := DatabaseSpan(context.Background(), "SELECT", "items")
	require.NotNil(t, ctx)
	require.NotNil(t, span)
	defer span.End()
}

func TestHTTPSpan(t *testing.T) {
	ctx, span := HTTPSpan(context.Background(), "GET", "/api/items")
	require.NotNil(t, ctx)
	require.NotNil(t, span)
	defer span.End()
}

func TestCacheSpan(t *testing.T) {
	ctx, span := CacheSpan(context.Background(), "GET", "items:123")
	require.NotNil(t, ctx)
	require.NotNil(t, span)
	defer span.End()
}

func TestNATSSpan(t *testing.T) {
	ctx, span := NATSSpan(context.Background(), "publish", "events.items")
	require.NotNil(t, ctx)
	require.NotNil(t, span)
	defer span.End()
}

func TestGraphSpan(t *testing.T) {
	ctx, span := GraphSpan(context.Background(), "query", "MATCH (n) RETURN n")
	require.NotNil(t, ctx)
	require.NotNil(t, span)
	defer span.End()
}

func TestTemporalSpan(t *testing.T) {
	ctx, span := TemporalSpan(context.Background(), "analysis", "wf-123")
	require.NotNil(t, ctx)
	require.NotNil(t, span)
	defer span.End()
}

func TestAIAgentSpan(t *testing.T) {
	ctx, span := AIAgentSpan(context.Background(), "code_analysis", "analyze")
	require.NotNil(t, ctx)
	require.NotNil(t, span)
	defer span.End()
}

func TestSetHTTPStatus(t *testing.T) {
	tests := []struct {
		name       string
		statusCode int
	}{
		{"ok", 200},
		{"created", 201},
		{"redirect", 302},
		{"bad request", 400},
		{"unauthorized", 401},
		{"not found", 404},
		{"server error", 500},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, span := noop.NewTracerProvider().Tracer("test").Start(context.Background(), "test")
			assert.NotPanics(t, func() {
				SetHTTPStatus(span, tt.statusCode)
			})
			span.End()
		})
	}
}

func TestSetUserID(t *testing.T) {
	_, span := noop.NewTracerProvider().Tracer("test").Start(context.Background(), "test")
	defer span.End()

	assert.NotPanics(t, func() {
		SetUserID(span, "user-123")
	})

	assert.NotPanics(t, func() {
		SetUserID(span, "") // empty should be handled
	})
}

func TestSetProjectID(t *testing.T) {
	_, span := noop.NewTracerProvider().Tracer("test").Start(context.Background(), "test")
	defer span.End()

	assert.NotPanics(t, func() {
		SetProjectID(span, "proj-456")
	})

	assert.NotPanics(t, func() {
		SetProjectID(span, "") // empty should be handled
	})
}

func TestHTTPStatusErrorThreshold(t *testing.T) {
	assert.Equal(t, 400, httpStatusErrorThreshold)
}

// --- database.go tests ---

func TestNormalizeDBOperation(t *testing.T) {
	tests := []struct {
		input string
		want  string
	}{
		{"select", "SELECT"},
		{"SELECT", "SELECT"},
		{"  insert  ", "INSERT"},
		{"UPDATE", "UPDATE"},
		{"delete", "DELETE"},
		{"upsert", "QUERY"},
		{"", "QUERY"},
		{"merge", "QUERY"},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got := normalizeDBOperation(tt.input)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestStartDBSpan(t *testing.T) {
	ctx, dbSpan := StartDBSpan(context.Background(), "SELECT", "items")
	require.NotNil(t, ctx)
	require.NotNil(t, dbSpan)
	dbSpan.End()
}

func TestStartDBSpan_EmptyTable(t *testing.T) {
	ctx, dbSpan := StartDBSpan(context.Background(), "query", "")
	require.NotNil(t, ctx)
	require.NotNil(t, dbSpan)
	dbSpan.End()
}

func TestDBSpan_SetQuery(t *testing.T) {
	_, dbSpan := StartDBSpan(context.Background(), "SELECT", "items")
	defer dbSpan.End()

	assert.NotPanics(t, func() {
		dbSpan.SetQuery("SELECT * FROM items WHERE id = $1")
	})
}

func TestDBSpan_SetQuery_LongQuery(t *testing.T) {
	_, dbSpan := StartDBSpan(context.Background(), "SELECT", "items")
	defer dbSpan.End()

	longQuery := strings.Repeat("x", 2000)
	assert.NotPanics(t, func() {
		dbSpan.SetQuery(longQuery)
	})
}

func TestDBSpan_SetRowsAffected(t *testing.T) {
	_, dbSpan := StartDBSpan(context.Background(), "INSERT", "items")
	defer dbSpan.End()

	assert.NotPanics(t, func() {
		dbSpan.SetRowsAffected(5)
	})
}

func TestDBSpan_RecordError(t *testing.T) {
	_, dbSpan := StartDBSpan(context.Background(), "DELETE", "items")
	defer dbSpan.End()

	assert.NotPanics(t, func() {
		dbSpan.RecordError(errors.New("constraint violation"))
	})

	assert.NotPanics(t, func() {
		dbSpan.RecordError(nil)
	})
}

func TestDBSpan_EndWithError(t *testing.T) {
	_, dbSpan := StartDBSpan(context.Background(), "UPDATE", "items")

	assert.NotPanics(t, func() {
		dbSpan.EndWithError(errors.New("timeout"))
	})
}

func TestDBSpan_NilSpan(t *testing.T) {
	dbSpan := &DBSpan{span: nil}

	assert.NotPanics(t, func() {
		dbSpan.SetQuery("SELECT 1")
		dbSpan.SetRowsAffected(0)
		dbSpan.RecordError(errors.New("err"))
		dbSpan.End()
	})
}

func TestTraceDBQuery_Success(t *testing.T) {
	err := TraceDBQuery(context.Background(), "SELECT", "items", "SELECT * FROM items", func() (int64, error) {
		return 5, nil
	})
	assert.NoError(t, err)
}

func TestTraceDBQuery_Error(t *testing.T) {
	expectedErr := errors.New("db error")
	err := TraceDBQuery(context.Background(), "INSERT", "items", "INSERT INTO items VALUES ($1)", func() (int64, error) {
		return 0, expectedErr
	})
	assert.Equal(t, expectedErr, err)
}

// --- TracerProvider tests ---

func TestTracerProvider_Shutdown_Nil(t *testing.T) {
	tp := &TracerProvider{provider: nil}
	err := tp.Shutdown(context.Background())
	assert.NoError(t, err)
}

func TestTracerProvider_ForceFlush_Nil(t *testing.T) {
	tp := &TracerProvider{provider: nil}
	err := tp.ForceFlush(context.Background())
	assert.NoError(t, err)
}

// --- Middleware test ---
func TestMiddleware(t *testing.T) {
	m := Middleware()
	assert.NotNil(t, m)
}

// Ensure interface compliance at compile time
var _ trace.Span = (noop.Span{})
