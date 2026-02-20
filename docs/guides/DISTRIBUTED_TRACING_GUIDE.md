# Distributed Tracing with Jaeger - Implementation Guide

## Overview

This guide documents the implementation of distributed tracing using OpenTelemetry and Jaeger in the TraceRTM Go backend. Distributed tracing helps you monitor and debug complex microservice architectures by tracking requests across service boundaries.

## Architecture

### Components

1. **OpenTelemetry SDK** - Industry-standard tracing instrumentation
2. **Jaeger** - Open-source distributed tracing platform
3. **OTLP Exporter** - Exports traces to Jaeger using OTLP protocol
4. **Auto-instrumentation** - Echo middleware for automatic HTTP tracing
5. **Custom Spans** - Manual instrumentation for critical operations

### Data Flow

```
HTTP Request → Echo Middleware → OpenTelemetry → OTLP Exporter → Jaeger → UI
                                      ↓
                              Custom Spans (DB, Cache, NATS, etc.)
```

## Installation

### 1. Install Jaeger

**macOS (Homebrew):**
```bash
brew install jaegertracing/jaeger/jaeger
```

**Linux/Docker:**
```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

### 2. Configure Environment

Add to `backend/.env`:
```env
# Distributed Tracing
TRACING_ENABLED=true
JAEGER_ENDPOINT=localhost:4317
TRACING_ENVIRONMENT=development
```

### 3. Start Services

Using process-compose:
```bash
make dev
# or
make dev-tui
```

The `jaeger` process will start automatically and be available at:
- **Jaeger UI**: http://localhost:16686
- **OTLP gRPC**: localhost:4317
- **OTLP HTTP**: localhost:4318

## Usage

### Automatic HTTP Tracing

All HTTP requests are automatically traced via the Echo middleware:

```go
// internal/server/server.go
func (s *Server) setupMiddleware() {
    // OpenTelemetry tracing middleware
    if s.infra.TracerProvider != nil {
        s.echo.Use(tracing.Middleware())
    }
    // ... other middleware
}
```

This creates a span for every HTTP request with:
- HTTP method and path
- Request/response headers
- Status code
- Duration
- Error information (if any)

### Custom Spans for Critical Operations

#### Database Operations

```go
import "github.com/kooshapari/tracertm-backend/internal/tracing"

func (r *Repository) GetUser(ctx context.Context, userID string) (*User, error) {
    // Create database span
    ctx, span := tracing.DatabaseSpan(ctx, "SELECT", "users")
    defer span.End()

    // Add custom attributes
    tracing.SetAttributes(span,
        attribute.String("user.id", userID),
    )

    // Execute query
    user, err := r.db.GetUser(ctx, userID)
    if err != nil {
        tracing.RecordError(span, err)
        return nil, err
    }

    // Record event
    tracing.AddEvent(span, "user_loaded")

    return user, nil
}
```

#### Cache Operations

```go
func (c *CacheService) Get(ctx context.Context, key string) (string, error) {
    ctx, span := tracing.CacheSpan(ctx, "GET", key)
    defer span.End()

    value, err := c.redis.Get(ctx, key).Result()
    if err != nil {
        if err == redis.Nil {
            // Cache miss
            tracing.SetAttributes(span, attribute.Bool("cache.hit", false))
        } else {
            tracing.RecordError(span, err)
        }
        return "", err
    }

    tracing.SetAttributes(span, attribute.Bool("cache.hit", true))
    return value, nil
}
```

#### NATS Event Publishing

```go
func (p *Publisher) Publish(ctx context.Context, subject string, data []byte) error {
    ctx, span := tracing.NATSSpan(ctx, "PUBLISH", subject)
    defer span.End()

    tracing.SetAttributes(span,
        attribute.Int("message.size", len(data)),
    )

    err := p.nats.Publish(subject, data)
    if err != nil {
        tracing.RecordError(span, err)
        return err
    }

    return nil
}
```

#### Graph Database Operations

```go
func (g *GraphService) Query(ctx context.Context, cypher string) error {
    ctx, span := tracing.GraphSpan(ctx, "QUERY", cypher)
    defer span.End()

    result, err := g.neo4j.Run(ctx, cypher, nil)
    if err != nil {
        tracing.RecordError(span, err)
        return err
    }

    tracing.AddEvent(span, "query_executed",
        attribute.Int("records", result.Len()),
    )

    return nil
}
```

#### AI Agent Operations

```go
func (a *AIService) Generate(ctx context.Context, agentType string, prompt string) (string, error) {
    ctx, span := tracing.AIAgentSpan(ctx, agentType, "generate")
    defer span.End()

    tracing.SetAttributes(span,
        attribute.String("ai.prompt", prompt),
        attribute.Int("ai.prompt_length", len(prompt)),
    )

    response, err := a.client.Generate(ctx, prompt)
    if err != nil {
        tracing.RecordError(span, err)
        return "", err
    }

    tracing.SetAttributes(span,
        attribute.Int("ai.response_length", len(response)),
    )

    return response, nil
}
```

### Nested Spans for Complex Operations

```go
func (s *Service) ComplexOperation(ctx context.Context, projectID string) error {
    // Parent span
    ctx, parentSpan := tracing.StartSpan(ctx, "create_project")
    defer parentSpan.End()

    tracing.SetProjectID(parentSpan, projectID)

    // Database operation
    {
        ctx, dbSpan := tracing.DatabaseSpan(ctx, "INSERT", "projects")
        defer dbSpan.End()

        if err := s.repo.Create(ctx, projectID); err != nil {
            tracing.RecordError(dbSpan, err)
            return err
        }
    }

    // Cache update
    {
        ctx, cacheSpan := tracing.CacheSpan(ctx, "SET", fmt.Sprintf("project:%s", projectID))
        defer cacheSpan.End()

        s.cache.Set(ctx, projectID, data)
    }

    // Event publishing
    {
        _, eventSpan := tracing.NATSSpan(ctx, "PUBLISH", "project.created")
        defer eventSpan.End()

        s.events.Publish(ctx, "project.created", data)
    }

    return nil
}
```

## Viewing Traces

### Jaeger UI

1. Open http://localhost:16686 in your browser
2. Select **tracertm-backend** from the service dropdown
3. Click **Find Traces** to see recent traces

### Key Features

- **Service Map**: Visualize service dependencies
- **Trace Timeline**: See request flow through your system
- **Span Details**: Examine individual operations
- **Search**: Filter traces by tags, duration, errors
- **Comparison**: Compare multiple traces side-by-side

### Search Examples

**Find slow requests:**
```
minDuration=1s
```

**Find errors:**
```
error=true
```

**Find specific user:**
```
user.id=12345
```

**Find database operations:**
```
span.kind=client db.system=postgresql
```

## Helper Functions Reference

### Span Creation

```go
// Generic span
ctx, span := tracing.StartSpan(ctx, "operation_name")

// Database span
ctx, span := tracing.DatabaseSpan(ctx, "SELECT", "users")

// HTTP span
ctx, span := tracing.HTTPSpan(ctx, "GET", "/api/v1/users")

// Cache span
ctx, span := tracing.CacheSpan(ctx, "GET", "user:123")

// NATS span
ctx, span := tracing.NATSSpan(ctx, "PUBLISH", "user.created")

// Graph span
ctx, span := tracing.GraphSpan(ctx, "QUERY", "MATCH (n) RETURN n")

// Temporal span
ctx, span := tracing.TemporalSpan(ctx, "MyWorkflow", "workflow-123")

// AI agent span
ctx, span := tracing.AIAgentSpan(ctx, "code-generator", "generate")
```

### Span Attributes

```go
// Set attributes
tracing.SetAttributes(span,
    attribute.String("key", "value"),
    attribute.Int("count", 42),
    attribute.Bool("success", true),
)

// Set HTTP status
tracing.SetHTTPStatus(span, 200)

// Set user ID
tracing.SetUserID(span, "user-123")

// Set project ID
tracing.SetProjectID(span, "project-456")
```

### Events and Errors

```go
// Add event
tracing.AddEvent(span, "cache_invalidated",
    attribute.String("reason", "user_updated"),
)

// Record error
tracing.RecordError(span, err)
```

## Best Practices

### 1. Always Use Context

Pass `context.Context` through your call chain to propagate trace context:

```go
// ✅ Good
func (s *Service) Process(ctx context.Context) error {
    return s.repo.Save(ctx, data)
}

// ❌ Bad
func (s *Service) Process() error {
    return s.repo.Save(context.Background(), data)
}
```

### 2. Defer span.End()

Always defer `span.End()` immediately after creating a span:

```go
ctx, span := tracing.StartSpan(ctx, "operation")
defer span.End()  // ✅ Ensures span is always ended
```

### 3. Record Meaningful Attributes

Add attributes that help debug issues:

```go
tracing.SetAttributes(span,
    attribute.String("user.id", userID),
    attribute.String("user.email", email),
    attribute.Int("items.count", len(items)),
)
```

### 4. Record Errors Properly

Always record errors on spans:

```go
if err != nil {
    tracing.RecordError(span, err)
    return err
}
```

### 5. Use Semantic Conventions

Follow OpenTelemetry semantic conventions for common operations:
- Database: `db.system`, `db.operation`, `db.table`
- HTTP: `http.method`, `http.target`, `http.status_code`
- Messaging: `messaging.system`, `messaging.destination`

## Performance Considerations

### Sampling

The current configuration samples **100% of traces** in development:

```go
// internal/tracing/tracer.go
sdktrace.WithSampler(sdktrace.AlwaysSample())
```

For production, consider adjusting the sample rate:

```go
// Sample 10% of traces
sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1))
```

### Batch Processing

Spans are batched before export for efficiency:

```go
sdktrace.WithBatcher(exporter,
    sdktrace.WithMaxExportBatchSize(512),
    sdktrace.WithBatchTimeout(5*time.Second),
    sdktrace.WithMaxQueueSize(2048),
)
```

### Resource Usage

- **Memory**: ~1-2MB per 1000 spans in queue
- **CPU**: Minimal overhead (<1% for typical workloads)
- **Network**: Batched exports reduce network overhead

## Troubleshooting

### No traces in Jaeger

1. **Check Jaeger is running:**
   ```bash
   lsof -i :16686  # UI
   lsof -i :4317   # OTLP gRPC
   ```

2. **Check environment variables:**
   ```bash
   echo $TRACING_ENABLED
   echo $JAEGER_ENDPOINT
   ```

3. **Check logs:**
   ```bash
   tail -f .process-compose/logs/go-backend.log | grep -i tracing
   tail -f .process-compose/logs/jaeger.log
   ```

### Spans not appearing

1. **Verify context propagation:**
   - Ensure you're passing `ctx` through your call chain
   - Don't use `context.Background()` in handlers

2. **Check span ending:**
   - Ensure `defer span.End()` is called
   - Check for early returns that skip `defer`

3. **Verify exporter connection:**
   - Check network connectivity to Jaeger
   - Ensure OTLP port (4317) is accessible

### High memory usage

1. **Reduce batch size:**
   ```go
   sdktrace.WithMaxQueueSize(1024)  // Reduce from 2048
   ```

2. **Increase batch timeout:**
   ```go
   sdktrace.WithBatchTimeout(10*time.Second)  // Export more frequently
   ```

3. **Adjust sampling rate:**
   ```go
   sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1))  // Sample 10%
   ```

## Production Deployment

### Environment Configuration

```env
# Production settings
TRACING_ENABLED=true
JAEGER_ENDPOINT=jaeger-collector.monitoring.svc.cluster.local:4317
TRACING_ENVIRONMENT=production
```

### Kubernetes Deployment

**Jaeger (All-in-one for testing):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:latest
        env:
        - name: COLLECTOR_OTLP_ENABLED
          value: "true"
        ports:
        - containerPort: 16686  # UI
        - containerPort: 4317   # OTLP gRPC
```

For production, use **Jaeger Operator** or **distributed deployment**.

### Security

1. **Enable TLS for OTLP:**
   ```go
   otlptracegrpc.WithTLSCredentials(credentials.NewClientTLSFromCert(certPool, ""))
   ```

2. **Use authentication:**
   ```go
   otlptracegrpc.WithHeaders(map[string]string{
       "Authorization": "Bearer " + token,
   })
   ```

3. **Network policies:**
   - Restrict access to Jaeger collector
   - Use service mesh for mTLS

## Integration with Other Tools

### Grafana

Jaeger can be configured as a data source in Grafana for unified dashboards.

### Prometheus

Combine metrics from Prometheus with traces from Jaeger using trace IDs.

### Alerting

Set up alerts based on trace metrics:
- Error rate
- P99 latency
- Service availability

## References

- [OpenTelemetry Go Documentation](https://opentelemetry.io/docs/instrumentation/go/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OTLP Specification](https://opentelemetry.io/docs/reference/specification/protocol/otlp/)
- [Semantic Conventions](https://opentelemetry.io/docs/reference/specification/trace/semantic_conventions/)

## File Structure

```
backend/
├── internal/
│   └── tracing/
│       ├── tracer.go       # Tracer initialization
│       ├── helpers.go      # Helper functions for creating spans
│       ├── middleware.go   # Echo middleware
│       └── examples.go     # Usage examples
├── scripts/
│   └── jaeger-if-not-running.sh  # Jaeger startup script
└── .env.example            # Environment configuration
```

## Next Steps

1. ✅ **Jaeger installed and configured**
2. ✅ **OpenTelemetry SDK integrated**
3. ✅ **HTTP auto-instrumentation enabled**
4. ✅ **Helper functions for custom spans**
5. 🔲 **Add custom spans to critical operations**
6. 🔲 **Configure sampling for production**
7. 🔲 **Set up alerts and dashboards**
8. 🔲 **Integrate with service mesh (if applicable)**
