# Temporal Quick Reference

Fast reference for common Temporal operations in TraceRTM.

---

## Common CLI Commands

### Server Management

```bash
# Start dev server
temporal server start-dev --db-filename .temporal/dev.db

# Check server health
temporal operator cluster health

# List namespaces
temporal operator namespace list
```

### Workflow Operations

```bash
# Execute workflow
temporal workflow execute \
  --type WorkflowName \
  --task-queue tracertm-tasks \
  --input '{"key": "value"}'

# List workflows
temporal workflow list

# List by status
temporal workflow list --query 'ExecutionStatus="Running"'
temporal workflow list --query 'ExecutionStatus="Failed"'

# Describe workflow
temporal workflow describe --workflow-id <id>

# Show workflow history
temporal workflow show --workflow-id <id>

# Cancel workflow
temporal workflow cancel --workflow-id <id>

# Terminate workflow
temporal workflow terminate --workflow-id <id> --reason "reason"
```

### Worker Management

```bash
# Start worker (via Procfile)
overmind start temporal_worker

# Manual start
python -m tracertm.workflows.worker
```

---

## Python API Examples

### Start Workflow

```python
from tracertm.services.temporal_service import TemporalService

service = TemporalService()

result = await service.start_workflow(
    workflow_name="GraphSnapshotWorkflow",
    project_id="proj-123",
    graph_id="graph-456"
)

print(f"Workflow ID: {result['workflow_id']}")
```

### Get Workflow Result

```python
result = await service.get_workflow_result(
    workflow_id="workflow-id-here"
)

print(f"Status: {result['status']}")
print(f"Result: {result.get('result')}")
```

### Check Service Health

```python
health = await service.health_check()
print(f"Temporal enabled: {health['enabled']}")
print(f"Status: {health['status']}")
```

---

## REST API Examples

### Start Workflow

```bash
curl -X POST http://localhost:4000/api/workflows/start \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "GraphSnapshotWorkflow",
    "project_id": "proj-123",
    "graph_id": "graph-456"
  }'
```

### Get Workflow Status

```bash
curl http://localhost:4000/api/workflows/<workflow-id>/status
```

---

## Available Workflows

### Graph Operations

| Workflow | Purpose | Input |
|----------|---------|-------|
| `GraphSnapshotWorkflow` | Create graph snapshot | `project_id`, `graph_id`, `created_by?`, `description?` |
| `GraphValidationWorkflow` | Validate graph structure | `project_id`, `graph_id` |
| `GraphExportWorkflow` | Export graph to JSON | `project_id` |
| `GraphDiffWorkflow` | Diff two graph versions | `project_id`, `graph_id`, `from_version`, `to_version` |

### Integration Operations

| Workflow | Purpose | Input |
|----------|---------|-------|
| `IntegrationSyncWorkflow` | Sync pending integrations | `limit?` (default: 50) |
| `IntegrationRetryWorkflow` | Retry failed integrations | `limit?` (default: 50) |

### Analysis Operations

| Workflow | Purpose | Input |
|----------|---------|-------|
| `IndexingWorkflow` | Index repository code | `repository_url`, `branch?` |
| `AnalysisWorkflow` | Quality analysis | `project_id`, `analysis_type?` |

---

## Workflow Definition Template

```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn(name="MyWorkflow")
class MyWorkflow:
    @workflow.run
    async def run(self, param1: str, param2: int = 10) -> dict:
        """Workflow implementation."""
        result = await workflow.execute_activity(
            my_activity,
            args=[param1, param2],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=workflow.RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )
        return result
```

---

## Activity Definition Template

```python
from temporalio import activity
import logging

logger = logging.getLogger(__name__)

@activity.defn(name="my_activity")
async def my_activity(param1: str, param2: int) -> dict:
    """Activity implementation."""
    activity_info = activity.info()
    logger.info(f"Activity {activity_info.activity_id}: Processing {param1}")

    # Your logic here

    return {
        "status": "completed",
        "result": "success"
    }
```

---

## Environment Variables

```bash
# Required
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Optional
TEMPORAL_TIMEOUT=20

# Temporal Cloud (if using)
TEMPORAL_TLS_CERT=/path/to/client.pem
TEMPORAL_TLS_KEY=/path/to/client.key
```

---

## Task Queue

All TraceRTM workflows use the same task queue:

```python
TASK_QUEUE = "tracertm-tasks"
```

---

## Common Patterns

### Execute Activity with Retry

```python
result = await workflow.execute_activity(
    my_activity,
    args=[data],
    start_to_close_timeout=timedelta(minutes=10),
    retry_policy=workflow.RetryPolicy(
        maximum_attempts=3,
        initial_interval=timedelta(seconds=1),
        maximum_interval=timedelta(seconds=60),
        backoff_coefficient=2.0,
    ),
)
```

### Execute Multiple Activities in Sequence

```python
result1 = await workflow.execute_activity(activity1, ...)
result2 = await workflow.execute_activity(activity2, args=[result1], ...)
result3 = await workflow.execute_activity(activity3, args=[result2], ...)
```

### Execute Activities in Parallel

```python
import asyncio

results = await asyncio.gather(
    workflow.execute_activity(activity1, ...),
    workflow.execute_activity(activity2, ...),
    workflow.execute_activity(activity3, ...),
)
```

### Activity Heartbeats (Long-Running)

```python
@activity.defn
async def long_running_activity():
    for i in range(100):
        # Report progress
        activity.heartbeat(f"Processing item {i}/100")
        # Do work
        await process_item(i)
```

---

## Monitoring

### Temporal UI

```bash
# Open UI in browser
open http://localhost:8233
```

### Metrics Endpoint

```bash
# Prometheus metrics
curl http://localhost:52936/metrics
```

### Worker Logs

```bash
# Via Overmind
overmind connect temporal_worker

# Direct
python -m tracertm.workflows.worker
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Worker can't connect | Check `TEMPORAL_HOST`, ensure server running |
| Workflow not found | Restart worker, check registration |
| Activity timeout | Increase timeout or add heartbeats |
| Database locked (SQLite) | Use PostgreSQL or single worker |

---

## Useful Queries

### List Failed Workflows (Last 24h)

```bash
temporal workflow list \
  --query 'ExecutionStatus="Failed" AND StartTime > "2026-01-30T00:00:00Z"'
```

### List Workflows by Type

```bash
temporal workflow list \
  --query 'WorkflowType="GraphSnapshotWorkflow"'
```

### List Long-Running Workflows

```bash
temporal workflow list \
  --query 'ExecutionStatus="Running" AND ExecutionDuration > "1h"'
```

---

## Next Steps

- **Full Setup Guide**: [TEMPORAL_SETUP.md](../guides/TEMPORAL_SETUP.md)
- **Migration Guide**: [HATCHET_TO_TEMPORAL_MIGRATION.md](../guides/HATCHET_TO_TEMPORAL_MIGRATION.md)
- **Official Docs**: https://docs.temporal.io/dev-guide/python

---

**Last Updated**: 2026-01-31
**Version**: 1.0
