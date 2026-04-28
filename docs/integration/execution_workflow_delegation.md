# Execution and Workflow Delegation Guide

This guide explains how to use the execution and workflow delegation clients to orchestrate Python services from the Go backend.

## Overview

The delegation clients provide a unified interface to Python-based services for:
- **Execution Management**: Docker/Native orchestration, Playwright/VHS recording
- **Workflow Orchestration**: Durable workflow management via Hatchet
- **Chaos Engineering**: Zombie detection and impact analysis

## Architecture

```
┌─────────────────┐
│   Go Backend    │
│   (HTTP API)    │
└────────┬────────┘
         │
         │ Delegates via HTTP
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Python Services │─────▶│  NATS Events     │
│  (FastAPI)      │      │  (Async Updates) │
└─────────────────┘      └──────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│  Docker/Native  │      │  Go Backend      │
│  Playwright/VHS │      │  (Subscribers)   │
└─────────────────┘      └──────────────────┘
```

## Execution Client

### Execution Types

| Type | Use Case | Recording Support |
|------|----------|------------------|
| `docker` | Containerized tests/builds | ✓ |
| `native` | Local process execution | ✓ |
| `playwright` | Browser automation | ✓ (video) |
| `vhs` | Terminal recording | ✓ (GIF/MP4) |

### Example: Running Tests

```go
import (
    "context"
    "time"
    "github.com/kooshapari/tracertm-backend/internal/clients"
)

// Start a test execution
exec, err := infra.ExecutionClient.StartExecution(ctx, clients.StartExecutionRequest{
    ProjectID:     "proj-123",
    ExecutionType: "docker",
    Command:       "pytest tests/ -v",
    Environment: map[string]string{
        "DATABASE_URL": "postgresql://...",
    },
})

// Poll for status
status, err := infra.ExecutionClient.GetStatus(ctx, exec.ExecutionID)

// Or wait for completion (with timeout)
finalStatus, err := infra.ExecutionClient.WaitForCompletion(
    ctx,
    exec.ExecutionID,
    30*time.Minute,
)

// Get output
output, err := infra.ExecutionClient.GetOutput(ctx, exec.ExecutionID)
```

### Example: Recording UI Tests

```go
exec, err := infra.ExecutionClient.StartExecution(ctx, clients.StartExecutionRequest{
    ProjectID:     "proj-123",
    ExecutionType: "playwright",
    Script:        "tests/ui/login_flow.spec.ts",
    RecordingOpts: &clients.RecordingOptions{
        OutputPath: "/recordings/login_flow.mp4",
        Format:     "mp4",
        Width:      1920,
        Height:     1080,
    },
})

// Wait for completion
status, err := infra.ExecutionClient.WaitForCompletion(ctx, exec.ExecutionID, 10*time.Minute)

// Download recording
recording, err := infra.ExecutionClient.GetRecording(ctx, exec.ExecutionID)
// recording is []byte - save to file or stream to client
```

### Status Polling Best Practices

1. **Use WaitForCompletion for background tasks**:
   ```go
   go func() {
       status, err := executionClient.WaitForCompletion(ctx, execID, timeout)
       // Publish NATS event when complete
       nats.Publish("execution.completed", projectID, execID, "execution", status)
   }()
   ```

2. **Manual polling with caching**:
   - GetStatus() is cached for 5 seconds automatically
   - Poll interval: 2-5 seconds recommended
   - Always set a timeout context

3. **Cancel executions gracefully**:
   ```go
   if err := executionClient.CancelExecution(ctx, execID); err != nil {
       // Handle cancellation error
   }
   ```

## Workflow Client (Hatchet)

### Workflow Types

Common workflows:
- `daily_report`: Generate project status reports
- `webhook_retry`: Retry failed webhook deliveries
- `agent_task_queue`: Process AI agent tasks
- `data_sync`: Synchronize data across services

### Example: Triggering a Workflow

```go
run, err := infra.HatchetClient.TriggerWorkflow(ctx, clients.WorkflowTriggerRequest{
    WorkflowName: "daily_report",
    ProjectID:    "proj-123",
    Input: map[string]interface{}{
        "report_type": "weekly",
        "recipients":  []string{"team@example.com"},
    },
})

// Check status
status, err := infra.HatchetClient.GetWorkflowRun(ctx, run.RunID)

// List all runs for a project
runs, err := infra.HatchetClient.ListWorkflowRuns(ctx, "proj-123", 50)
```

### Workflow Patterns

1. **Fire-and-forget**:
   ```go
   run, err := hatchetClient.TriggerWorkflow(ctx, req)
   // Don't wait - workflow runs independently
   ```

2. **Monitor via NATS events**:
   ```go
   // Python service publishes workflow.completed event
   nats.Subscribe("workflow.completed", func(event *BridgeEvent) {
       // Handle completion
   })
   ```

3. **Long-running workflows**:
   - No timeout on Hatchet workflows
   - Use GetWorkflowRun() to check status periodically
   - Cancel if needed: `CancelWorkflowRun(ctx, runID)`

## Chaos Client

### Zombie Detection

Identifies "zombie" items that are:
- Orphaned (no links)
- Stale (no updates for 90+ days)
- Broken (invalid references)

```go
report, err := infra.ChaosClient.DetectZombies(ctx, clients.DetectZombiesRequest{
    ProjectID: "proj-123",
})

for _, zombie := range report.ZombieItems {
    fmt.Printf("Zombie: %s (%s) - %s\n",
        zombie.ItemID,
        zombie.ItemType,
        zombie.Reason,
    )
}

// Follow recommendations
for _, rec := range report.Recommendations {
    fmt.Println(rec)
}
```

### Impact Analysis

Analyzes the impact of deleting or modifying an item:

```go
analysis, err := infra.ChaosClient.AnalyzeImpact(ctx, "item-123")

fmt.Printf("Risk Level: %s\n", analysis.RiskLevel)
fmt.Printf("Direct Dependents: %d\n", analysis.DirectDependents)
fmt.Printf("Total Impact: %d items affected\n", analysis.TotalImpact)

// Review critical paths
for i, path := range analysis.CriticalPaths {
    fmt.Printf("Critical Path %d: %v\n", i+1, path)
}
```

## Caching Strategy

| Client | Cache TTL | Reason |
|--------|-----------|--------|
| ExecutionClient.GetStatus | 5s | Reduce polling load |
| ExecutionClient.GetOutput | 1m | Output doesn't change |
| HatchetClient | None | State changes frequently |
| ChaosClient.DetectZombies | 10m | Expensive graph analysis |
| ChaosClient.AnalyzeImpact | 10m | Expensive graph traversal |

## Error Handling

### Circuit Breaker

The Python client includes a circuit breaker that:
- Trips after 5 consecutive failures or 60% failure rate
- Opens for 30 seconds before trying again
- Protects against cascading failures

```go
// Check circuit breaker state
state := pythonClient.GetCircuitBreakerState()
// States: Closed (normal), Open (blocking), HalfOpen (testing)
```

### Retry Strategy

- 3 retries with exponential backoff
- 1s min wait, 5s max wait
- 30s request timeout

### Error Types

```go
if err != nil {
    switch {
    case strings.Contains(err.Error(), "circuit breaker"):
        // Circuit is open - Python service is down
    case strings.Contains(err.Error(), "timeout"):
        // Request timed out - increase timeout or check Python service
    case strings.Contains(err.Error(), "status 404"):
        // Resource not found
    case strings.Contains(err.Error(), "status 500"):
        // Python service error - check logs
    }
}
```

## Event Publishing

All delegation actions publish NATS events for real-time updates:

```go
// Execution events
execution.started     // When execution begins
execution.completed   // When execution finishes
execution.failed      // When execution fails

// Workflow events
workflow.triggered    // When workflow starts
workflow.completed    // When workflow finishes (from Python)
workflow.failed       // When workflow fails (from Python)
```

### Example Event Handler

```go
// In your handler
exec, err := executionClient.StartExecution(ctx, req)

// Publish event
nats.Publish("execution.started", exec.ProjectID, exec.ExecutionID, "execution", exec)

// Wait for completion in background
go func() {
    status, _ := executionClient.WaitForCompletion(ctx, exec.ExecutionID, timeout)
    nats.Publish("execution.completed", status.ProjectID, status.ExecutionID, "execution", status)
}()
```

## Testing

### Mock Servers

Use `httptest` to mock Python services:

```go
server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    // Mock response
    json.NewEncoder(w).Encode(mockResponse)
}))
defer server.Close()

pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
```

### Integration Tests

1. Start Python services locally
2. Configure `PYTHON_BACKEND_URL` in tests
3. Use real executions with short timeouts

## Performance Optimization

### For High-Frequency Polling

```go
// Use cached status checks
ticker := time.NewTicker(2 * time.Second)
defer ticker.Stop()

for {
    select {
    case <-ticker.C:
        status, _ := executionClient.GetStatus(ctx, execID)
        if status.Status == "completed" {
            return status, nil
        }
    case <-ctx.Done():
        return nil, ctx.Err()
    }
}
```

### For Large Outputs

Stream output instead of loading all at once:
```go
// Python service can support streaming with ?stream=true
// Implementation pending
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Circuit breaker open" | Python service is down - check health |
| Timeout waiting for execution | Increase timeout or check Python logs |
| Cache returning stale data | Cache TTL is intentional - wait or invalidate |
| Missing recording | Check RecordingOpts and Python service logs |
| Workflow not completing | Check Hatchet dashboard for workflow status |

## API Reference

See client files for full API documentation:
- `backend/internal/clients/execution_client.go`
- `backend/internal/clients/hatchet_client.go`
- `backend/internal/clients/chaos_client.go`
