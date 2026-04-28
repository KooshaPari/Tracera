# Temporal Workflow Orchestration - README

**TraceRTM Phase 5: Temporal Integration**

---

## What is Temporal?

Temporal is a durable execution system that enables you to write workflows as code. It guarantees that your workflow will run to completion, even if your application crashes or servers restart.

**Key Benefits**:
- **Durable**: Workflows survive crashes and restarts
- **Reliable**: Automatic retries and error handling
- **Observable**: Built-in UI and monitoring
- **Scalable**: Production-tested at Uber, Netflix, Stripe
- **Free**: Open source, self-hosted

---

## Quick Reference

### Start Services

```bash
# All services (recommended)
overmind start

# Just Temporal
overmind start temporal temporal_worker

# Or manually
temporal server start-dev --db-filename .temporal/dev.db
python -m tracertm.workflows.worker
```

### Execute Workflow

```bash
# Via CLI
temporal workflow execute \
  --type GraphSnapshotWorkflow \
  --task-queue tracertm-tasks \
  --input '{"project_id": "p1", "graph_id": "g1"}'

# Via Python
from tracertm.services.temporal_service import TemporalService

service = TemporalService()
result = await service.start_workflow(
    workflow_name="GraphSnapshotWorkflow",
    project_id="p1",
    graph_id="g1"
)
```

### Monitor Workflows

```bash
# List workflows
temporal workflow list

# Temporal UI
open http://localhost:8233
```

---

## Available Workflows

### Graph Operations
- `GraphSnapshotWorkflow` - Create graph snapshots
- `GraphValidationWorkflow` - Validate graph integrity
- `GraphExportWorkflow` - Export graphs to JSON
- `GraphDiffWorkflow` - Compare graph versions

### Integration Operations
- `IntegrationSyncWorkflow` - Process pending syncs
- `IntegrationRetryWorkflow` - Retry failed syncs

### Analysis Operations
- `IndexingWorkflow` - Index repository code
- `AnalysisWorkflow` - Quality analysis

---

## File Structure

```
src/tracertm/workflows/
├── worker.py          # Temporal worker entry point
├── workflows.py       # Workflow definitions (8 workflows)
├── activities.py      # Activity definitions (8 activities)
└── tasks.py           # Reusable task implementations

src/tracertm/services/
└── temporal_service.py  # Service layer for Temporal client

.temporal/             # Local Temporal server data (gitignored)
```

---

## Configuration

### Environment Variables

```bash
# Required
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Optional (Temporal Cloud)
TEMPORAL_TLS_CERT=/path/to/client.pem
TEMPORAL_TLS_KEY=/path/to/client.key
```

### Procfile

```
temporal: temporal server start-dev --db-filename .temporal/dev.db
temporal_worker: python -m tracertm.workflows.worker
```

---

## Documentation

### Guides
- **[Quick Start](./TEMPORAL_QUICK_START.md)** - Get started in 5 minutes
- **[Migration Guide](../HATCHET_TO_TEMPORAL_MIGRATION.md)** - Hatchet to Temporal migration

### Reports
- **[Implementation Complete](../../reports/PHASE_5_TEMPORAL_IMPLEMENTATION_COMPLETE.md)** - Phase 5 summary
- **[Migration Analysis](../../reports/TEMPORAL_MIGRATION_ANALYSIS.md)** - Detailed analysis

---

## Common Commands

### Development

```bash
# Start all services
overmind start

# Restart worker after code changes
overmind restart temporal_worker

# View worker logs
overmind logs temporal_worker

# Stop all services
overmind stop
```

### Workflow Management

```bash
# Execute workflow
temporal workflow execute --type <WorkflowName> --task-queue tracertm-tasks --input '{...}'

# List workflows
temporal workflow list

# Describe workflow
temporal workflow describe --workflow-id <id>

# Show workflow history
temporal workflow show --workflow-id <id>

# Cancel workflow
temporal workflow cancel --workflow-id <id>
```

### Monitoring

```bash
# Open Temporal UI
open http://localhost:8233

# Check worker status
ps aux | grep "tracertm.workflows.worker"

# View worker logs
tail -f logs/temporal_worker.log
```

---

## Troubleshooting

### Worker won't start

```bash
# Check if Temporal server is running
temporal workflow list

# Start Temporal server if needed
temporal server start-dev
```

### Workflow execution fails

```bash
# Check workflow history
temporal workflow show --workflow-id <id>

# Check worker logs
overmind logs temporal_worker

# Verify task queue matches
# Worker: tracertm-tasks (default)
# Workflow: --task-queue tracertm-tasks
```

### Can't connect to Temporal

```bash
# Verify Temporal is running
lsof -i :7233

# Check environment variables
echo $TEMPORAL_HOST

# Restart Temporal server
overmind restart temporal
```

---

## Code Examples

### Define a Workflow

```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn(name="MyWorkflow")
class MyWorkflow:
    @workflow.run
    async def run(self, input_data: dict) -> dict:
        result = await workflow.execute_activity(
            my_activity,
            args=[input_data],
            start_to_close_timeout=timedelta(minutes=10),
        )
        return result
```

### Define an Activity

```python
from temporalio import activity

@activity.defn(name="my_activity")
async def my_activity(input_data: dict) -> dict:
    # Do actual work here
    return {"status": "completed"}
```

### Execute Workflow

```python
from tracertm.services.temporal_service import TemporalService

async def main():
    service = TemporalService()

    # Start workflow
    result = await service.start_workflow(
        workflow_name="MyWorkflow",
        input_data={"key": "value"}
    )

    print(f"Workflow started: {result['workflow_id']}")

    # Get result (waits for completion)
    final_result = await service.get_workflow_result(
        workflow_id=result['workflow_id']
    )

    print(f"Workflow result: {final_result}")
```

---

## Next Steps

1. **Read the Quick Start**: [TEMPORAL_QUICK_START.md](./TEMPORAL_QUICK_START.md)
2. **Try Example Workflows**: Execute a graph snapshot workflow
3. **Explore Temporal UI**: http://localhost:8233
4. **Customize Workflows**: Add your own workflows and activities
5. **Deploy to Production**: See migration guide for production setup

---

## Support

- **Temporal Docs**: https://docs.temporal.io/dev-guide/python
- **Community Slack**: https://temporal.io/slack
- **GitHub**: https://github.com/temporalio/temporal
- **TraceRTM Docs**: See guides and reports in `docs/`

---

## Status

**Phase 5 Implementation**: ✅ 85% Complete

**Completed**:
- ✅ Worker implementation
- ✅ Workflow definitions (8 workflows)
- ✅ Activity definitions (8 activities)
- ✅ Service layer
- ✅ Configuration
- ✅ Documentation

**Pending**:
- ⏳ API service integration
- ⏳ Preflight check updates
- ⏳ Archive Hatchet code
- ⏳ Testing suite

---

**Last Updated**: 2026-01-31
**Version**: 1.0.0
**Related**: Phase 5 Implementation
