# Delegation Clients - Quick Start Guide

## What Was Built

Go clients for delegating work to Python backend services:
- **ExecutionClient**: Docker/Native/Playwright/VHS execution
- **HatchetClient**: Durable workflow orchestration
- **ChaosClient**: Zombie detection and impact analysis

## Quick Examples

### 1. Run Tests in Docker

```go
// Start execution
exec, err := infra.ExecutionClient.StartExecution(ctx, clients.StartExecutionRequest{
    ProjectID:     "my-project",
    ExecutionType: "docker",
    Command:       "pytest tests/ -v",
})

// Wait for completion (blocks)
status, err := infra.ExecutionClient.WaitForCompletion(ctx, exec.ExecutionID, 30*time.Minute)

// Or poll manually
for {
    status, _ := infra.ExecutionClient.GetStatus(ctx, exec.ExecutionID)
    if status.Status == "completed" || status.Status == "failed" {
        break
    }
    time.Sleep(5 * time.Second)
}

// Get output
output, err := infra.ExecutionClient.GetOutput(ctx, exec.ExecutionID)
```

### 2. Record UI Test with Playwright

```go
exec, err := infra.ExecutionClient.StartExecution(ctx, clients.StartExecutionRequest{
    ProjectID:     "my-project",
    ExecutionType: "playwright",
    Script:        "tests/ui/login.spec.ts",
    RecordingOpts: &clients.RecordingOptions{
        OutputPath: "/recordings/login.mp4",
        Format:     "mp4",
        Width:      1920,
        Height:     1080,
    },
})

// Wait for completion
status, err := infra.ExecutionClient.WaitForCompletion(ctx, exec.ExecutionID, 10*time.Minute)

// Download recording
recording, err := infra.ExecutionClient.GetRecording(ctx, exec.ExecutionID)
// Save to file or stream to client
```

### 3. Trigger Workflow

```go
run, err := infra.HatchetClient.TriggerWorkflow(ctx, clients.WorkflowTriggerRequest{
    WorkflowName: "daily_report",
    ProjectID:    "my-project",
    Input: map[string]interface{}{
        "report_type": "weekly",
        "recipients":  []string{"team@example.com"},
    },
})

// Check status later
status, err := infra.HatchetClient.GetWorkflowRun(ctx, run.RunID)

// Or list all workflows
runs, err := infra.HatchetClient.ListWorkflowRuns(ctx, "my-project", 50)
```

### 4. Detect Zombie Items

```go
report, err := infra.ChaosClient.DetectZombies(ctx, clients.DetectZombiesRequest{
    ProjectID: "my-project",
})

for _, zombie := range report.ZombieItems {
    fmt.Printf("Zombie: %s (%s) - %s\n",
        zombie.ItemID,
        zombie.ItemType,
        zombie.Reason,
    )
}

// Analyze impact before deleting
analysis, err := infra.ChaosClient.AnalyzeImpact(ctx, "item-123")
if analysis.RiskLevel == "high" {
    fmt.Printf("Warning: Affects %d items!\n", analysis.TotalImpact)
}
```

### 5. HTTP Handler Example

```go
func (h *ExecutionHandler) RunTests(c echo.Context) error {
    var req StartExecutionRequest
    if err := c.Bind(&req); err != nil {
        return echo.NewHTTPError(http.StatusBadRequest, "invalid request")
    }

    // Start execution
    exec, err := h.infra.ExecutionClient.StartExecution(c.Request().Context(),
        clients.StartExecutionRequest{
            ProjectID:     req.ProjectID,
            ExecutionType: req.ExecutionType,
            Command:       req.Command,
        },
    )
    if err != nil {
        return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
    }

    // Publish NATS event
    h.infra.NATS.Publish("execution.started", exec.ProjectID, exec.ExecutionID, "execution", exec)

    // Wait for completion in background
    go func() {
        status, _ := h.infra.ExecutionClient.WaitForCompletion(
            context.Background(),
            exec.ExecutionID,
            30*time.Minute,
        )
        h.infra.NATS.Publish("execution.completed", status.ProjectID, status.ExecutionID, "execution", status)
    }()

    return c.JSON(http.StatusAccepted, map[string]interface{}{
        "execution_id": exec.ExecutionID,
        "status":       exec.Status,
    })
}
```

## Execution Types

| Type | Use For | Recording |
|------|---------|-----------|
| `docker` | Tests, builds in containers | ✓ |
| `native` | Local processes | ✓ |
| `playwright` | Browser automation | ✓ Video |
| `vhs` | Terminal demos | ✓ GIF/MP4 |

## Caching

| Operation | Cache | Why |
|-----------|-------|-----|
| GetStatus() | 5s | Reduce polling load |
| GetOutput() | 1m | Doesn't change |
| DetectZombies() | 10m | Expensive analysis |
| AnalyzeImpact() | 10m | Expensive traversal |
| Workflows | None | State changes |

## NATS Events

Automatically published:
- `execution.started` - Execution begins
- `execution.completed` - Execution finishes
- `workflow.triggered` - Workflow starts
- `workflow.completed` - Workflow finishes (from Python)

Subscribe to events:
```go
nats.Subscribe("execution.completed", func(event *BridgeEvent) {
    // Handle completion
})
```

## Error Handling

```go
if err != nil {
    switch {
    case strings.Contains(err.Error(), "circuit breaker"):
        // Python service down - retry later
    case strings.Contains(err.Error(), "timeout"):
        // Operation timed out - increase timeout
    case strings.Contains(err.Error(), "status 404"):
        // Resource not found
    case strings.Contains(err.Error(), "status 500"):
        // Python error - check logs
    }
}
```

## Testing

Run tests:
```bash
cd backend
go test ./internal/clients/... -v
```

All tests use mock HTTP servers - no Python backend needed.

## Files Reference

**Clients:**
- `/backend/internal/clients/execution_client.go`
- `/backend/internal/clients/hatchet_client.go`
- `/backend/internal/clients/chaos_client.go`

**Handlers:**
- `/backend/internal/handlers/execution_handler.go`
- `/backend/internal/handlers/workflow_handler.go`
- `/backend/internal/handlers/chaos_handler.go`

**Tests:**
- `/backend/internal/clients/*_test.go`

**Docs:**
- `/docs/integration/execution_workflow_delegation.md` (Full guide)

## Infrastructure Access

Clients are available in infrastructure:
```go
type Infrastructure struct {
    ExecutionClient *clients.ExecutionClient
    HatchetClient   *clients.HatchetClient
    ChaosClient     *clients.ChaosClient
}
```

Access in handlers:
```go
h.infra.ExecutionClient.StartExecution(...)
h.infra.HatchetClient.TriggerWorkflow(...)
h.infra.ChaosClient.DetectZombies(...)
```

## Common Patterns

### Background Execution
```go
exec, _ := executionClient.StartExecution(ctx, req)
go func() {
    status, _ := executionClient.WaitForCompletion(ctx, exec.ExecutionID, timeout)
    nats.Publish("execution.completed", status.ProjectID, exec.ExecutionID, "execution", status)
}()
return exec  // Return immediately
```

### Polling with Timeout
```go
deadline := time.Now().Add(30 * time.Minute)
for time.Now().Before(deadline) {
    status, _ := executionClient.GetStatus(ctx, execID)
    if status.Status == "completed" {
        return status, nil
    }
    time.Sleep(5 * time.Second)
}
return nil, fmt.Errorf("timeout")
```

### Workflow Monitoring
```go
run, _ := hatchetClient.TriggerWorkflow(ctx, req)
// Don't wait - monitor via NATS
nats.Subscribe("workflow.completed", func(event *BridgeEvent) {
    if event.EntityID == run.RunID {
        // Handle completion
    }
})
```

## Configuration

Set in environment:
```bash
PYTHON_BACKEND_URL=https://python-api.example.com
SERVICE_TOKEN=your-service-token
```

## Next Steps

1. Read full docs: `/docs/integration/execution_workflow_delegation.md`
2. Review handler examples: `/backend/internal/handlers/execution_handler.go`
3. Run tests to see usage: `go test ./internal/clients/... -v`
4. Integrate into your routes and handlers
