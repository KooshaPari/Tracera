# AI and Spec Analytics Delegation Guide

## Overview

This guide documents the Go HTTP clients that delegate to Python-only AI and SpecAnalyticsV2 services. These services will **ALWAYS** run in the Python backend and should never be reimplemented in Go.

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌────────────────┐
│  Go Backend │────────▶│  Python Backend  │────────▶│   Anthropic    │
│  (Gateway)  │         │   (AI Service)   │         │     Claude     │
└─────────────┘         └──────────────────┘         └────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │ SpecAnalyticsV2  │
                        │  - ISO 29148     │
                        │  - EARS Patterns │
                        │  - Formal Verify │
                        └──────────────────┘
```

### Why Python-Only?

1. **AIService**: Uses Anthropic Python SDK with streaming, tool use, and agentic loops
2. **SpecAnalyticsV2**: Complex NLP, formal verification, and standards compliance analysis

## Clients

### 1. AIClient (`internal/clients/ai_client.go`)

Handles AI-powered chat and analysis with streaming support.

#### Features

- **SSE Streaming**: Real-time streaming responses via Server-Sent Events
- **No Caching**: Always fresh responses (AI is non-deterministic)
- **Context Cancellation**: Proper cleanup when client disconnects
- **Error Handling**: Graceful stream interruption handling

#### Usage

```go
// Initialize
aiClient := clients.NewAIClient(pythonClient)

// Streaming Chat
req := clients.StreamChatRequest{
    Message:   "Analyze this requirement",
    Context:   map[string]interface{}{"domain": "authentication"},
    ProjectID: "proj-123",
    UserID:    "user-456",
}

eventChan, errChan := aiClient.StreamChat(ctx, req)

// Consume stream
for {
    select {
    case event := <-eventChan:
        switch event.Type {
        case "delta":
            fmt.Print(event.Delta)
        case "complete":
            fmt.Println("\n" + event.Content)
            return
        case "error":
            log.Error(event.Error)
            return
        }
    case err := <-errChan:
        log.Error(err)
        return
    }
}

// Non-Streaming Analysis
result, err := aiClient.Analyze(ctx, "User shall be authenticated", "proj-123")
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Analysis: %s (confidence: %.2f)\n", result.Analysis, result.Confidence)
```

#### SSE Event Types

| Type       | Description                          | Fields                |
|------------|--------------------------------------|-----------------------|
| `delta`    | Incremental content chunk            | `delta`               |
| `complete` | Stream completed successfully        | `content`             |
| `error`    | Error occurred during streaming      | `error`               |
| `metadata` | Additional context/metadata          | `data`                |

### 2. SpecAnalyticsClient (`internal/clients/spec_analytics_client.go`)

Handles specification analysis for compliance and quality.

#### Features

- **Caching**: 15-minute TTL to reduce expensive computations
- **Stale-on-Error**: Returns cached results if service unavailable
- **Parallel Batch**: Max 10 concurrent requests for batch analysis
- **Content-Based Cache**: Cache key includes content hash (detects changes)

#### Usage

```go
// Initialize
specAnalyticsClient := clients.NewSpecAnalyticsClient(pythonClient)

// Single Spec Analysis
req := clients.AnalyzeSpecRequest{
    SpecID:    "REQ-001",
    Content:   "The system shall authenticate users within 2 seconds",
    ProjectID: "proj-123",
}

result, err := specAnalyticsClient.AnalyzeSpec(ctx, req)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("ISO 29148 Compliant: %v\n", result.CompliantWithISO)
fmt.Printf("ODC Classification: %s\n", result.ODCClassification)
fmt.Printf("EARS Patterns: %+v\n", result.EARSPatterns)

// Batch Analysis (parallel)
requests := []clients.AnalyzeSpecRequest{
    {SpecID: "REQ-001", Content: "Content 1", ProjectID: "proj-123"},
    {SpecID: "REQ-002", Content: "Content 2", ProjectID: "proj-123"},
    // ... up to 100 specs
}

results, err := specAnalyticsClient.BatchAnalyzeSpecs(ctx, requests)
// Or use optimized Python batch endpoint:
results, err = specAnalyticsClient.BatchAnalyzeSpecsOptimized(ctx, requests)

// Helper Methods
compliant, recommendations, err := specAnalyticsClient.ValidateISO29148Compliance(
    ctx, "REQ-001", content, "proj-123",
)

patterns, err := specAnalyticsClient.GetEARSPatterns(
    ctx, "REQ-001", content, "proj-123",
)
```

#### EARS Pattern Types

| Type                  | Description                                    | Example                                          |
|-----------------------|------------------------------------------------|--------------------------------------------------|
| `UBIQUITOUS`          | Always active, no conditions                   | "The system shall log all transactions"          |
| `EVENT_DRIVEN`        | Triggered by specific events                   | "When user clicks login, system shall verify"    |
| `UNWANTED_BEHAVIOR`   | Defines what must NOT happen                   | "The system shall not expose passwords"          |
| `STATE_DRIVEN`        | Active only in certain states                  | "While in maintenance mode, reject new requests" |
| `OPTIONAL_FEATURE`    | Conditional/optional functionality             | "If premium tier, enable advanced features"      |

## Caching Strategy

### AIClient: No Caching

**Rationale**: AI responses are non-deterministic and context-dependent.

- Streaming: Never cached
- Analysis: Never cached
- Always fresh responses

### SpecAnalyticsClient: Aggressive Caching

**Rationale**: Expensive computation, deterministic results for same content.

| Strategy              | Implementation                                      |
|-----------------------|-----------------------------------------------------|
| **TTL**               | 15 minutes                                          |
| **Cache Key**         | Hash of `spec_id` + `content` + `project_id`       |
| **Invalidation**      | Automatic via content hash                          |
| **Stale-on-Error**    | Return expired cache if service unavailable        |
| **Batch Caching**     | Individual results cached, batch response not cached|

#### Stale-on-Error Example

```go
func (c *SpecAnalyticsClient) AnalyzeSpec(ctx, req) (*AnalysisResult, error) {
    cacheKey := c.generateCacheKey(req)

    err := c.pythonClient.DelegateRequest(ctx, ...)
    if err != nil {
        // Try to return stale cache on error
        if c.cache != nil {
            var cached AnalysisResult
            if cacheErr := c.cache.Get(ctx, cacheKey, &cached); cacheErr == nil {
                return &cached, nil  // Return stale data
            }
        }
        return nil, err  // No cache available
    }
    return &result, nil
}
```

## Error Handling

### AI Streaming Errors

```go
eventChan, errChan := aiClient.StreamChat(ctx, req)

for {
    select {
    case event := <-eventChan:
        if event.Type == "error" {
            // Stream-level error (continue or abort)
            handleStreamError(event.Error)
        }
    case err := <-errChan:
        // Fatal error (network, auth, etc.)
        handleFatalError(err)
        return
    case <-ctx.Done():
        // Client cancelled
        handleCancellation()
        return
    }
}
```

### Spec Analytics Errors

```go
result, err := specAnalyticsClient.AnalyzeSpec(ctx, req)
if err != nil {
    // Check if stale cache was used
    if result != nil {
        log.Warn("Using stale cache due to service error")
        return result, nil  // Accept stale data
    }

    // No fallback available
    return nil, fmt.Errorf("analysis failed: %w", err)
}
```

## Handler Integration

### AI Handler Example

```go
func (h *AIHandler) StreamChat(c echo.Context) error {
    var req StreamChatRequest
    if err := c.Bind(&req); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, "Invalid request")
    }

    clientReq := clients.StreamChatRequest{
        Message:   req.Message,
        Context:   req.Context,
        ProjectID: req.ProjectID,
        UserID:    req.UserID,
    }

    eventChan, errChan := h.infra.AIClient.StreamChat(c.Request().Context(), clientReq)

    // Set SSE headers
    c.Response().Header().Set("Content-Type", "text/event-stream")
    c.Response().Header().Set("Cache-Control", "no-cache")
    c.Response().Header().Set("Connection", "keep-alive")
    c.Response().WriteHeader(http.StatusOK)

    // Stream to client
    for {
        select {
        case event, ok := <-eventChan:
            if !ok {
                return nil
            }
            eventJSON, _ := json.Marshal(event)
            fmt.Fprintf(c.Response(), "data: %s\n\n", eventJSON)
            c.Response().Flush()

        case err := <-errChan:
            if err != nil {
                errorEvent := clients.SSEEvent{Type: "error", Error: err.Error()}
                errorJSON, _ := json.Marshal(errorEvent)
                fmt.Fprintf(c.Response(), "data: %s\n\n", errorJSON)
                c.Response().Flush()
            }
            return err

        case <-c.Request().Context().Done():
            return nil
        }
    }
}
```

### Spec Analytics Handler Example

```go
func (h *SpecAnalyticsHandler) AnalyzeSpec(c echo.Context) error {
    var req AnalyzeSpecRequest
    if err := c.Bind(&req); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, "Invalid request")
    }

    clientReq := clients.AnalyzeSpecRequest{
        SpecID:    req.SpecID,
        Content:   req.Content,
        ProjectID: req.ProjectID,
    }

    result, err := h.infra.SpecAnalyticsClient.AnalyzeSpec(c.Request().Context(), clientReq)
    if err != nil {
        return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
    }

    return c.JSON(http.StatusOK, result)
}
```

## Testing

### Integration Tests

Run tests:
```bash
cd backend/tests/integration/clients
go test -v -run TestAIClient
go test -v -run TestSpecAnalyticsClient
```

### Key Test Scenarios

**AIClient**:
- ✅ Streaming with multiple deltas
- ✅ Context cancellation
- ✅ Error events
- ✅ Non-streaming analysis

**SpecAnalyticsClient**:
- ✅ Single spec analysis
- ✅ Cache hit/miss behavior
- ✅ Stale-on-error fallback
- ✅ Batch parallel analysis (max 10 concurrent)
- ✅ Content-based cache invalidation

## API Endpoints

### AI Service

| Endpoint                    | Method | Description              | Streaming |
|-----------------------------|--------|--------------------------|-----------|
| `/api/v1/ai/stream-chat`    | POST   | Stream AI chat responses | Yes       |
| `/api/v1/ai/analyze`        | POST   | Analyze text             | No        |

### Spec Analytics Service

| Endpoint                                      | Method | Description                | Caching |
|-----------------------------------------------|--------|----------------------------|---------|
| `/api/v1/spec-analytics/analyze`              | POST   | Analyze single spec        | Yes     |
| `/api/v1/spec-analytics/batch-analyze`        | POST   | Batch analyze specs        | No*     |
| `/api/v1/spec-analytics/validate-iso29148`    | POST   | ISO 29148 compliance check | Yes     |
| `/api/v1/spec-analytics/ears-patterns`        | POST   | Extract EARS patterns      | Yes     |

*Individual results are cached, batch response is not.

## Performance Considerations

### AI Streaming

- **Timeout**: 10 minutes (long-running conversations)
- **No Retries**: Direct HTTP client (retries would break streaming)
- **Buffer Size**: Channel buffer of 10 events

### Spec Analytics Batch

- **Max Concurrent**: 10 requests in parallel
- **Max Batch Size**: 100 specs per request
- **Cache TTL**: 15 minutes
- **Timeout**: 30 seconds per request (inherited from PythonServiceClient)

## Monitoring

### Key Metrics

**AIClient**:
- Stream duration
- Events per stream
- Error rate
- Context cancellation rate

**SpecAnalyticsClient**:
- Cache hit ratio
- Stale-on-error frequency
- Batch analysis time
- Individual vs batch usage ratio

### Logging

```go
// AI streaming
log.Info("Starting AI stream", "project_id", req.ProjectID, "user_id", req.UserID)
log.Info("AI stream completed", "duration", duration, "events", eventCount)

// Spec analytics
log.Info("Spec analysis", "spec_id", req.SpecID, "cache_hit", cacheHit)
log.Warn("Using stale cache", "spec_id", req.SpecID, "cache_age", cacheAge)
```

## Best Practices

### Do's ✅

- Use streaming for interactive AI chat
- Cache spec analytics aggressively
- Handle context cancellation gracefully
- Accept stale cache on errors (spec analytics)
- Use batch analysis for multiple specs
- Validate ISO 29148 compliance before storage

### Don'ts ❌

- Don't cache AI responses
- Don't retry streaming requests
- Don't ignore context cancellation
- Don't bypass cache for repeated queries
- Don't implement AI/analytics in Go
- Don't batch more than 100 specs at once

## Troubleshooting

### AI Stream Hangs

**Symptom**: Stream starts but no events received

**Solution**:
1. Check Python service is running
2. Verify service token is valid
3. Check network connectivity
4. Increase timeout if needed

### Spec Analytics Cache Misses

**Symptom**: High cache miss rate despite repeated queries

**Solution**:
1. Verify cache is initialized
2. Check cache key generation (content hash)
3. Verify TTL is not too short
4. Check memory/Redis availability

### Batch Analysis Slow

**Symptom**: Batch takes longer than expected

**Solution**:
1. Use `BatchAnalyzeSpecsOptimized` (Python batch endpoint)
2. Reduce batch size
3. Check cache hit ratio
4. Verify max concurrent limit (should be 10)

## Future Enhancements

- [ ] Metrics collection (Prometheus)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Circuit breaker metrics dashboard
- [ ] Cache warming for common specs
- [ ] WebSocket alternative to SSE
- [ ] GraphQL subscriptions for streaming
