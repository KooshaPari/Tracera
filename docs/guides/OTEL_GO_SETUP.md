# OpenTelemetry Go Backend Setup Guide

This guide explains how OpenTelemetry is configured in the TraceRTM Go backend and how to use it for distributed tracing.

## Overview

OpenTelemetry (OTel) provides distributed tracing for the TraceRTM backend, enabling:
- **Trace propagation**: Follow requests across HTTP and gRPC boundaries
- **Span instrumentation**: Automatic and manual span creation
- **Performance monitoring**: Identify bottlenecks and slow operations
- **Debugging**: Enhanced observability for troubleshooting

## Architecture

### Components

1. **Tracer Provider** (`internal/tracing/tracer.go`)
   - Initializes OpenTelemetry SDK
   - Configures OTLP/gRPC exporter for Jaeger
   - Sets up batch span processor
   - Manages tracer lifecycle

2. **HTTP Instrumentation** (`internal/tracing/middleware.go`)
   - Echo middleware for automatic HTTP span creation
   - Captures request/response metadata
   - Propagates trace context via HTTP headers

3. **gRPC Instrumentation** (`internal/tracing/grpc.go`)
   - Unary and streaming server interceptors
   - Unary and streaming client interceptors
   - Extracts metadata from gRPC headers
   - Tracks gRPC status codes

4. **Span Utilities** (`internal/tracing/helpers.go`, `internal/tracing/context.go`)
   - Domain-specific span factories (database, cache, NATS, etc.)
   - Context propagation helpers
   - Error handling and status management

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JAEGER_ENDPOINT` | `127.0.0.1:4317` | OTLP/gRPC endpoint for Jaeger |
| `TRACING_ENVIRONMENT` | `development` | Deployment environment label |

### Example Configuration

```bash
# Development (local Jaeger)
JAEGER_ENDPOINT=127.0.0.1:4317
TRACING_ENVIRONMENT=development

# Production (remote Jaeger)
JAEGER_ENDPOINT=jaeger.production.svc.cluster.local:4317
TRACING_ENVIRONMENT=production
```

## Integration Points

### 1. Application Startup

The tracer is initialized during infrastructure setup in `main()`:

```go
func initInfrastructure(ctx context.Context, cfg *config.Config) (*infrastructure.Infrastructure, error) {
    infra, err := infrastructure.InitializeInfrastructure(ctx, cfg)
    // TracerProvider is initialized here
    // Trace context is globally registered via otel.SetTracerProvider()
    return infra, err
}
```

### 2. HTTP Instrumentation

Register the Echo middleware in your server setup:

```go
// In server/server.go or handler setup
e := echo.New()

// Add tracing middleware
e.Use(tracing.Middleware())

// Other middleware and routes...
```

**Automatic Behavior:**
- Creates spans for each HTTP request
- Captures method, path, and status code
- Propagates W3C Trace Context headers
- Records errors and exceptions

**Example Trace:**
```
HTTP POST /api/v1/projects
├── Duration: 125ms
├── Status: 200
└── Attributes:
    - http.method: POST
    - http.target: /api/v1/projects
    - http.status_code: 200
```

### 3. gRPC Instrumentation

The gRPC server automatically includes OpenTelemetry interceptors:

```go
// In internal/grpc/server.go
grpcServer := grpc.NewServer(
    // ... other options
    grpc.UnaryInterceptor(tracing.UnaryServerInterceptor()),
    grpc.StreamInterceptor(tracing.StreamServerInterceptor()),
)
```

**Automatic Behavior:**
- Creates spans for each gRPC RPC call
- Captures service name, method name, and status
- Extracts user/project metadata from headers
- Tracks streaming vs unary RPCs

**Example Trace:**
```
GraphService/AnalyzeImpact
├── Duration: 342ms
├── Status: OK
└── Attributes:
    - grpc.service: GraphService
    - grpc.method: AnalyzeImpact
    - grpc.status_code: OK
```

## Manual Instrumentation

### Creating Spans for Custom Operations

#### HTTP Operations

```go
import "github.com/kooshapari/tracertm-backend/internal/tracing"

func MyHTTPHandler(c echo.Context) error {
    ctx, span := tracing.HTTPSpan(c.Request().Context(), "GET", "/custom/path")
    defer span.End()

    // Your handler logic...

    // Record status
    tracing.SetHTTPStatus(span, http.StatusOK)
    return c.JSON(http.StatusOK, result)
}
```

#### Database Operations

```go
func GetUser(ctx context.Context, userID string) (*User, error) {
    ctx, span := tracing.DatabaseSpan(ctx, "SELECT", "users")
    defer span.End()

    // Database query...

    if err != nil {
        tracing.RecordError(span, err)
        return nil, err
    }
    return user, nil
}
```

#### gRPC Operations

```go
func CallRemoteService(ctx context.Context) error {
    ctx, span := tracing.GRPCSpan(ctx, "RemoteService", "GetData")
    defer span.End()

    // gRPC call...

    if err != nil {
        tracing.RecordError(span, err)
        return err
    }
    return nil
}
```

#### Cache Operations

```go
func GetCached(ctx context.Context, key string) (string, error) {
    ctx, span := tracing.CacheSpan(ctx, "GET", key)
    defer span.End()

    // Redis operation...

    return value, nil
}
```

#### NATS Messaging

```go
func PublishEvent(ctx context.Context, subject string, event interface{}) error {
    ctx, span := tracing.NATSSpan(ctx, "PUBLISH", subject)
    defer span.End()

    // NATS publish...

    return nil
}
```

#### Temporal Workflows

```go
func ExecuteWorkflow(ctx context.Context, workflowID string) error {
    ctx, span := tracing.TemporalSpan(ctx, "MyWorkflow", workflowID)
    defer span.End()

    // Temporal execution...

    return nil
}
```

#### AI Agent Operations

```go
func RunAgent(ctx context.Context, agentType string) error {
    ctx, span := tracing.AIAgentSpan(ctx, agentType, "execute")
    defer span.End()

    // Agent logic...

    return nil
}
```

### Setting Span Attributes

```go
ctx, span := tracing.StartSpan(ctx, "my-operation")
defer span.End()

// Set single attribute
tracing.SetAttributes(span, attribute.String("user.id", userID))

// Set multiple attributes
tracing.SetAttributes(span,
    attribute.String("user.id", userID),
    attribute.Int("page", pageNum),
    attribute.Bool("is_admin", isAdmin),
)

// Set project context
tracing.SetProjectID(span, projectID)

// Set user context
tracing.SetUserID(span, userID)
```

### Recording Errors

```go
ctx, span := tracing.StartSpan(ctx, "risky-operation")
defer span.End()

result, err := riskyOperation()
if err != nil {
    tracing.RecordError(span, err)
    return err
}
```

### Adding Events

```go
ctx, span := tracing.StartSpan(ctx, "data-processing")
defer span.End()

tracing.AddEvent(span, "data.received",
    attribute.Int("record_count", 1000),
)

// Process data...

tracing.AddEvent(span, "data.processed",
    attribute.Int("successful", 998),
    attribute.Int("failed", 2),
)
```

### Context Propagation

For async operations (goroutines, queues), propagate trace context:

```go
// In main context
go func() {
    // Create a new context that preserves trace
    asyncCtx := tracing.WrapAsync(ctx)

    ctx, span := tracing.StartSpan(asyncCtx, "async-task")
    defer span.End()

    // Async work here - will be linked to original trace
}()
```

Or with user/project context:

```go
// Add user to context
ctx, _ = tracing.WithUserID(ctx, userID)

// Create span - will automatically include user.id
ctx, span := tracing.StartSpan(ctx, "user-operation")
defer span.End()
```

## Verifying Traces Are Generated

### 1. Check Jaeger UI

With local Jaeger running (`docker run -d -p 6831:6831/udp -p 16686:16686 jaegertracing/all-in-one`):

1. Open http://localhost:16686
2. Select "tracertm-backend" from the service dropdown
3. Click "Find Traces"
4. You should see traces from your HTTP and gRPC requests

### 2. Check Application Logs

Look for initialization messages:

```
🔍 Initializing distributed tracing (Jaeger endpoint: 127.0.0.1:4317, env: development)
✅ Distributed tracing initialized successfully
```

### 3. Verify with curl

```bash
# Make an API request
curl http://localhost:8080/api/v1/health -v

# Look for trace context headers in response:
# traceparent: 00-<trace_id>-<span_id>-01
```

### 4. Check gRPC Traces

If using grpcurl:

```bash
grpcurl -plaintext localhost:9091 tracertm.v1.GraphService/AnalyzeImpact
```

You should see corresponding traces in Jaeger.

## Performance Considerations

### Sampling Strategy

The backend uses `AlwaysSample()` in development. For production, adjust:

```go
// In tracer.go InitTracer function
// Development: sample all traces
sdktrace.WithSampler(sdktrace.AlwaysSample())

// Production: sample 10% of traces
sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1))

// Production: sample based on parent span
sdktrace.WithSampler(sdktrace.ParentBased(
    sdktrace.TraceIDRatioBased(0.1),
))
```

### Batch Processor Configuration

The batch processor buffers spans before export:

| Parameter | Value | Impact |
|-----------|-------|--------|
| `MaxExportBatchSize` | 512 | Smaller = more frequent exports |
| `BatchTimeout` | 5s | Larger = batches accumulate longer |
| `MaxQueueSize` | 2048 | Maximum buffered spans |

Adjust for your load:
- **High throughput**: Increase batch size and queue
- **Low latency**: Decrease batch timeout
- **Memory constrained**: Reduce queue size

## Troubleshooting

### Traces Not Appearing in Jaeger

1. **Verify Jaeger is running:**
   ```bash
   curl http://localhost:16686
   ```

2. **Check endpoint configuration:**
   ```bash
   echo $JAEGER_ENDPOINT  # Should be 127.0.0.1:4317
   ```

3. **Check application logs for errors:**
   ```bash
   grep -i "tracer\|otel\|jaeger" /path/to/logs/
   ```

4. **Verify gRPC connectivity:**
   ```bash
   grpcurl -plaintext -d '{}' localhost:4317 list
   ```

### High Memory Usage

- Reduce `MaxQueueSize` in tracer.go
- Increase `BatchTimeout` to flush less frequently
- Reduce sampling rate for production

### Missing Span Attributes

Ensure you're calling `SetAttributes()` or `RecordError()` before span ends:

```go
ctx, span := tracing.StartSpan(ctx, "operation")
// Set attributes BEFORE defer span.End()
tracing.SetAttributes(span, attribute.String("key", "value"))
defer span.End()
```

## Best Practices

### 1. Always Defer Span.End()

```go
ctx, span := tracing.StartSpan(ctx, "operation")
defer span.End()  // Ensures cleanup even if panic occurs

// Your code here
```

### 2. Use Appropriate Span Kinds

- `SpanKindServer`: HTTP handlers, gRPC servers
- `SpanKindClient`: Database, cache, external service calls
- `SpanKindInternal`: Internal functions, helpers
- `SpanKindProducer`: Message publication (NATS, Kafka)
- `SpanKindConsumer`: Message consumption

### 3. Include Relevant Context

```go
ctx, span := tracing.StartSpan(ctx, "create-item")
defer span.End()

tracing.SetAttributes(span,
    attribute.String("project.id", projectID),
    attribute.String("user.id", userID),
    attribute.String("item.type", itemType),
)
```

### 4. Propagate Context in Async Operations

```go
asyncCtx := tracing.WrapAsync(ctx)
go doAsync(asyncCtx)  // Preserves trace context
```

### 5. Record Domain-Specific Events

```go
ctx, span := tracing.StartSpan(ctx, "data-import")
defer span.End()

tracing.AddEvent(span, "validation.complete",
    attribute.Int("record_count", 100),
)

tracing.AddEvent(span, "sync.started",
    attribute.String("target", "database"),
)
```

## Files Reference

| File | Purpose |
|------|---------|
| `internal/tracing/tracer.go` | Core tracer initialization and lifecycle |
| `internal/tracing/middleware.go` | Echo HTTP instrumentation middleware |
| `internal/tracing/grpc.go` | gRPC server/client interceptors |
| `internal/tracing/helpers.go` | Span utility functions |
| `internal/tracing/context.go` | Context propagation utilities |
| `internal/tracing/examples.go` | Example instrumentation patterns |
| `internal/tracing/database.go` | Database-specific instrumentation |

## Related Documentation

- [OpenTelemetry Go Documentation](https://opentelemetry.io/docs/languages/go/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [OTEL Semantic Conventions](https://opentelemetry.io/docs/reference/specification/protocol/exporter/)

## Support

For issues or questions about tracing:

1. Check the application logs for OTel initialization messages
2. Verify Jaeger connectivity with `grpcurl`
3. Review existing spans in Jaeger UI to understand trace structure
4. Check this guide's troubleshooting section
