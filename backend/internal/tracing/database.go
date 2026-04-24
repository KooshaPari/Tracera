// Package tracing provides OpenTelemetry-based tracing for database and cache operations.
// Package tracing contains tracing helpers for database operations.
package tracing

import (
	"context"
	"strings"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
)

const (
	// Database operation types
	dbOperationSelect = "SELECT"
	dbOperationInsert = "INSERT"
	dbOperationUpdate = "UPDATE"
	dbOperationDelete = "DELETE"
	dbOperationQuery  = "QUERY"

	// Maximum length for database query strings in traces
	dbMaxQueryLength = 1000
)

// DBSpan represents a database operation span
type DBSpan struct {
	span      trace.Span
	startTime time.Time
}

// StartDBSpan starts a new span for a database operation
func StartDBSpan(ctx context.Context, operation, table string) (context.Context, *DBSpan) {
	tracer := otel.Tracer("tracertm-backend")

	operation = normalizeDBOperation(operation)
	spanName := operation
	if table != "" {
		spanName = operation + " " + table
	}

	ctx, span := tracer.Start(ctx, spanName,
		trace.WithSpanKind(trace.SpanKindClient),
		trace.WithAttributes(
			attribute.String("db.system", "postgresql"),
			attribute.String("db.operation", operation),
			attribute.String("db.table", table),
		),
	)

	return ctx, &DBSpan{
		span:      span,
		startTime: time.Now(),
	}
}

func normalizeDBOperation(operation string) string {
	op := strings.ToUpper(strings.TrimSpace(operation))
	switch op {
	case dbOperationSelect, dbOperationInsert, dbOperationUpdate, dbOperationDelete:
		return op
	default:
		return dbOperationQuery
	}
}

// SetQuery sets the SQL query on the span (sanitized)
func (s *DBSpan) SetQuery(query string) {
	if s.span != nil {
		// Truncate very long queries
		if len(query) > dbMaxQueryLength {
			query = query[:dbMaxQueryLength] + "..."
		}
		s.span.SetAttributes(attribute.String("db.statement", query))
	}
}

// SetRowsAffected sets the number of rows affected
func (s *DBSpan) SetRowsAffected(count int64) {
	if s.span != nil {
		s.span.SetAttributes(attribute.Int64("db.rows_affected", count))
	}
}

// RecordError records an error on the span
func (s *DBSpan) RecordError(err error) {
	if s.span != nil && err != nil {
		s.span.RecordError(err)
		s.span.SetStatus(codes.Error, err.Error())
	}
}

// End ends the span
func (s *DBSpan) End() {
	if s.span != nil {
		duration := time.Since(s.startTime)
		s.span.SetAttributes(attribute.Int64("db.duration_ms", duration.Milliseconds()))
		s.span.End()
	}
}

// EndWithError ends the span with an error
func (s *DBSpan) EndWithError(err error) {
	s.RecordError(err)
	s.End()
}

// TraceDBQuery is a helper function to trace a database query execution
func TraceDBQuery(ctx context.Context, operation, table, query string, fn func() (int64, error)) error {
	_, dbSpan := StartDBSpan(ctx, operation, table)
	defer dbSpan.End()

	dbSpan.SetQuery(query)

	rowsAffected, err := fn()
	if err != nil {
		dbSpan.RecordError(err)
		return err
	}

	dbSpan.SetRowsAffected(rowsAffected)
	return nil
}
