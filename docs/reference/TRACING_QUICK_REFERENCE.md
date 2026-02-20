# Distributed Tracing - Quick Reference

## Quick Start

### 1. Install Jaeger
```bash
brew install jaegertracing/jaeger/jaeger
```

### 2. Configure Environment
```env
TRACING_ENABLED=true
JAEGER_ENDPOINT=localhost:4317
TRACING_ENVIRONMENT=development
```

### 3. Start Services
```bash
make dev
```

### 4. View Traces
Open http://localhost:16686

## Common Patterns

### HTTP Handler with Tracing
```go
func (h *Handler) GetUser(c echo.Context) error {
    ctx := c.Request().Context()
    userID := c.Param("id")

    // HTTP span is auto-created by middleware
    // Add custom attributes to current span
    span := trace.SpanFromContext(ctx)
    tracing.SetUserID(span, userID)

    user, err := h.service.GetUser(ctx, userID)
    if err != nil {
        tracing.RecordError(span, err)
        return err
    }

    return c.JSON(200, user)
}
```

### Service Method with Database
```go
func (s *Service) GetUser(ctx context.Context, userID string) (*User, error) {
    ctx, span := tracing.DatabaseSpan(ctx, "SELECT", "users")
    defer span.End()

    tracing.SetAttributes(span,
        attribute.String("user.id", userID),
    )

    user, err := s.repo.FindByID(ctx, userID)
    if err != nil {
        tracing.RecordError(span, err)
        return nil, err
    }

    return user, nil
}
```

### Cache Operation
```go
func (c *Cache) Get(ctx context.Context, key string) (string, error) {
    ctx, span := tracing.CacheSpan(ctx, "GET", key)
    defer span.End()

    val, err := c.redis.Get(ctx, key).Result()
    if err == redis.Nil {
        tracing.SetAttributes(span, attribute.Bool("cache.hit", false))
        return "", ErrNotFound
    }

    tracing.SetAttributes(span, attribute.Bool("cache.hit", true))
    return val, nil
}
```

### Event Publishing
```go
func (p *Publisher) Publish(ctx context.Context, subject string, data []byte) error {
    ctx, span := tracing.NATSSpan(ctx, "PUBLISH", subject)
    defer span.End()

    err := p.nats.Publish(subject, data)
    if err != nil {
        tracing.RecordError(span, err)
    }
    return err
}
```

## Helper Functions

### Span Creation
```go
// Generic
ctx, span := tracing.StartSpan(ctx, "operation")

// Database
ctx, span := tracing.DatabaseSpan(ctx, "INSERT", "users")

// Cache
ctx, span := tracing.CacheSpan(ctx, "SET", "user:123")

// NATS
ctx, span := tracing.NATSSpan(ctx, "PUBLISH", "user.created")

// Graph DB
ctx, span := tracing.GraphSpan(ctx, "QUERY", "MATCH (n) RETURN n")

// AI Agent
ctx, span := tracing.AIAgentSpan(ctx, "code-gen", "generate")
```

### Attributes
```go
// Common attributes
tracing.SetUserID(span, "user-123")
tracing.SetProjectID(span, "project-456")
tracing.SetHTTPStatus(span, 200)

// Custom attributes
tracing.SetAttributes(span,
    attribute.String("key", "value"),
    attribute.Int("count", 42),
    attribute.Bool("success", true),
)
```

### Events & Errors
```go
// Add event
tracing.AddEvent(span, "cache_cleared")

// Record error
tracing.RecordError(span, err)
```

## Jaeger UI

### Access
- **URL**: http://localhost:16686
- **Service**: tracertm-backend

### Search Tips
```
# Find slow requests
minDuration=1s

# Find errors
error=true

# Find by user
user.id=12345

# Find database operations
db.system=postgresql
```

## Configuration

### Environment Variables
```env
# Enable/disable tracing
TRACING_ENABLED=true|false

# Jaeger endpoint
JAEGER_ENDPOINT=localhost:4317

# Environment name
TRACING_ENVIRONMENT=development|staging|production
```

### Ports
- **16686**: Jaeger UI
- **4317**: OTLP gRPC (for traces)
- **4318**: OTLP HTTP

## Troubleshooting

### No traces appearing
1. Check Jaeger is running: `lsof -i :16686`
2. Check environment: `echo $TRACING_ENABLED`
3. Check logs: `tail -f .process-compose/logs/jaeger.log`

### Context not propagating
```go
// ❌ Bad - creates new context
func Process() {
    ctx := context.Background()
    // ...
}

// ✅ Good - uses passed context
func Process(ctx context.Context) {
    // ...
}
```

### Span not ending
```go
// ❌ Bad - might not end on error
ctx, span := tracing.StartSpan(ctx, "op")
if err != nil {
    return err  // span never ends!
}
span.End()

// ✅ Good - always ends
ctx, span := tracing.StartSpan(ctx, "op")
defer span.End()
```

## Best Practices

1. **Always use context**: Pass `ctx` through your call chain
2. **Defer span.End()**: Always defer immediately after creation
3. **Record errors**: Use `tracing.RecordError(span, err)`
4. **Add meaningful attributes**: Help future debugging
5. **Use semantic names**: Follow OpenTelemetry conventions

## Files Reference

- `internal/tracing/tracer.go` - Tracer initialization
- `internal/tracing/helpers.go` - Helper functions
- `internal/tracing/middleware.go` - Echo middleware
- `internal/tracing/examples.go` - Usage examples
- `scripts/jaeger-if-not-running.sh` - Jaeger startup
- `docs/guides/DISTRIBUTED_TRACING_GUIDE.md` - Full guide
