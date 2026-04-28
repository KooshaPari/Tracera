# Temporal Setup Guide

Complete guide for setting up Temporal workflow orchestration in TraceRTM.

**Date**: 2026-01-31
**Status**: Production Ready

---

## Overview

Temporal is a durable workflow orchestration platform that powers TraceRTM's background job processing, including graph snapshots, validation, exports, and integration syncing.

**Key Features**:
- Self-hosted workflow engine (no external dependencies)
- Durable execution with automatic retries
- Time-travel debugging for workflow inspection
- Comprehensive observability via Temporal UI
- Type-safe Python SDK

---

## Installation

### macOS (via Homebrew)

```bash
# Install Temporal CLI
brew install temporal

# Verify installation
temporal --version
```

### Linux/Windows

Download from [Temporal CLI Releases](https://github.com/temporalio/cli/releases):

```bash
# Linux
curl -sSf https://temporal.download/cli.sh | sh

# Windows (PowerShell)
iwr -useb https://temporal.download/cli.ps1 | iex
```

### Python SDK

Already included in TraceRTM dependencies:

```bash
# Check pyproject.toml
uv pip list | grep temporalio
```

---

## Starting Temporal Server

### Development Mode (SQLite Backend)

Start Temporal in dev mode with SQLite persistence:

```bash
# Start server (stores data in .temporal/dev.db)
temporal server start-dev --db-filename .temporal/dev.db
```

**Output**:
```
Server:  localhost:7233
UI:      http://localhost:8233
Metrics: http://localhost:52936/metrics
```

### Production Mode (PostgreSQL Backend)

For production deployments, use PostgreSQL:

1. **Configure PostgreSQL**:
   ```bash
   # Create Temporal database
   psql -U postgres -c "CREATE DATABASE temporal;"
   psql -U postgres -c "CREATE DATABASE temporal_visibility;"
   ```

2. **Create Configuration File** (`temporal-config.yaml`):
   ```yaml
   persistence:
     defaultStore: postgres
     visibilityStore: postgres
     numHistoryShards: 4
     datastores:
       postgres:
         sql:
           pluginName: "postgres12"
           databaseName: "temporal"
           connectAddr: "localhost:5432"
           connectProtocol: "tcp"
           user: "temporal_user"
           password: "temporal_password"
           maxConns: 20
           maxIdleConns: 20

   global:
     membership:
       maxJoinDuration: 30s
       broadcastAddress: "127.0.0.1"

   services:
     frontend:
       rpc:
         grpcPort: 7233
         membershipPort: 6933
         bindOnIP: "0.0.0.0"

     history:
       rpc:
         grpcPort: 7234
         membershipPort: 6934
         bindOnIP: "0.0.0.0"

     matching:
       rpc:
         grpcPort: 7235
         membershipPort: 6935
         bindOnIP: "0.0.0.0"

     worker:
       rpc:
         grpcPort: 7239
         membershipPort: 6939
         bindOnIP: "0.0.0.0"
   ```

3. **Start Server**:
   ```bash
   temporal server start --config temporal-config.yaml
   ```

---

## Environment Configuration

### Required Variables

Add to `.env`:

```bash
# Temporal server connection
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Optional: Timeout for workflow operations
TEMPORAL_TIMEOUT=20
```

### Temporal Cloud (Optional)

For managed Temporal Cloud:

```bash
# Temporal Cloud configuration
TEMPORAL_HOST=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace

# mTLS certificates
TEMPORAL_TLS_CERT=/path/to/client.pem
TEMPORAL_TLS_KEY=/path/to/client.key
```

---

## Starting the Temporal Worker

The worker connects to Temporal and executes workflow activities.

### Via Procfile (Recommended)

```bash
# Procfile already configured - just start with Overmind
overmind start

# Or start specific process
overmind start temporal_worker
```

### Manual Start

```bash
# From project root
python -m tracertm.workflows.worker
```

**Expected Output**:
```
2026-01-31 12:00:00 [INFO] tracertm.workflows.worker: Connecting to Temporal at localhost:7233 (namespace: default)
2026-01-31 12:00:00 [INFO] tracertm.workflows.worker: Connected to Temporal server at localhost:7233
2026-01-31 12:00:00 [INFO] tracertm.workflows.worker: Starting Temporal worker on task queue: tracertm-tasks
2026-01-31 12:00:00 [INFO] tracertm.workflows.worker: Registered workflows: IndexingWorkflow, AnalysisWorkflow, ...
2026-01-31 12:00:00 [INFO] tracertm.workflows.worker: Registered activities: index_repository, analyze_quality, ...
```

---

## Accessing Temporal UI

Temporal provides a web UI for monitoring and debugging workflows.

### Local Development

1. **Start Temporal Server** (if not already running):
   ```bash
   temporal server start-dev
   ```

2. **Open UI**:
   ```bash
   open http://localhost:8233
   ```

### Features

- **Workflows**: View all workflow executions
- **Task Queues**: Monitor worker status
- **Namespaces**: Manage isolated environments
- **Search**: Query workflows by ID, status, type
- **Stack Trace**: Debug workflow execution history
- **Event History**: View complete workflow timeline

---

## Creating Workflows

### Define Workflow Class

```python
# src/tracertm/workflows/workflows.py
from temporalio import workflow
from datetime import timedelta

@workflow.defn(name="MyWorkflow")
class MyWorkflow:
    @workflow.run
    async def run(self, input_data: str) -> dict:
        """Main workflow logic."""
        result = await workflow.execute_activity(
            my_activity,
            args=[input_data],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=workflow.RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
            ),
        )
        return result
```

### Define Activity

```python
# src/tracertm/workflows/activities.py
from temporalio import activity

@activity.defn(name="my_activity")
async def my_activity(input_data: str) -> dict:
    """Actual work implementation."""
    # Your logic here
    return {"status": "completed", "data": input_data}
```

### Register in Worker

```python
# src/tracertm/workflows/worker.py
worker = Worker(
    client,
    task_queue=TASK_QUEUE,
    workflows=[MyWorkflow],  # Add your workflow
    activities=[my_activity],  # Add your activity
)
```

---

## Testing Workflows

### Via Temporal CLI

```bash
# Execute workflow
temporal workflow execute \
  --type MyWorkflow \
  --task-queue tracertm-tasks \
  --input '"test data"'

# List all workflows
temporal workflow list

# Describe specific workflow
temporal workflow describe --workflow-id <workflow-id>

# Get workflow result
temporal workflow show --workflow-id <workflow-id>
```

### Via Python API

```python
from tracertm.services.temporal_service import TemporalService

async def test_workflow():
    service = TemporalService()

    # Start workflow
    result = await service.start_workflow(
        workflow_name="MyWorkflow",
        input_data="test"
    )

    print(f"Started workflow: {result['workflow_id']}")

    # Get result (waits for completion)
    workflow_result = await service.get_workflow_result(
        workflow_id=result['workflow_id']
    )

    print(f"Result: {workflow_result}")
```

### Via REST API

```bash
# Start workflow via API endpoint
curl -X POST http://localhost:4000/api/workflows/start \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "MyWorkflow",
    "input_data": "test"
  }'
```

---

## Debugging Workflows

### View Workflow History

```bash
# Get complete event history
temporal workflow show \
  --workflow-id <workflow-id> \
  --output json | jq
```

### Inspect Activity Failures

```bash
# Describe workflow to see failures
temporal workflow describe --workflow-id <workflow-id>
```

### Check Worker Logs

```bash
# View worker logs (via Overmind)
overmind connect temporal_worker

# Or direct Python logs
python -m tracertm.workflows.worker
```

### Time-Travel Debugging

In Temporal UI:
1. Navigate to workflow execution
2. Click "Event History"
3. Step through each event to see inputs/outputs
4. Inspect stack traces for failures

---

## Common Operations

### List All Workflows

```bash
temporal workflow list
```

### Filter by Status

```bash
# Running workflows
temporal workflow list --query 'ExecutionStatus="Running"'

# Failed workflows
temporal workflow list --query 'ExecutionStatus="Failed"'
```

### Cancel Workflow

```bash
temporal workflow cancel --workflow-id <workflow-id>
```

### Terminate Workflow

```bash
temporal workflow terminate --workflow-id <workflow-id> \
  --reason "Manual termination"
```

### Reset Workflow

```bash
# Reset to specific event
temporal workflow reset --workflow-id <workflow-id> \
  --event-id <event-id>
```

---

## Production Deployment

### Docker Compose

```yaml
# docker-compose.temporal.yml
version: '3.8'

services:
  postgresql:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: temporal
      POSTGRES_USER: temporal
    volumes:
      - temporal-postgres:/var/lib/postgresql/data

  temporal:
    image: temporalio/auto-setup:latest
    depends_on:
      - postgresql
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=postgresql
    ports:
      - "7233:7233"
      - "8233:8233"

  temporal-worker:
    build: .
    command: python -m tracertm.workflows.worker
    depends_on:
      - temporal
    environment:
      - TEMPORAL_HOST=temporal:7233

volumes:
  temporal-postgres:
```

### Kubernetes

See [Temporal Helm Charts](https://github.com/temporalio/helm-charts) for K8s deployment.

---

## Monitoring & Alerts

### Metrics

Temporal exposes Prometheus metrics on port 52936:

```bash
curl http://localhost:52936/metrics
```

### Key Metrics to Monitor

- `temporal_workflow_completed_total`: Completed workflows
- `temporal_workflow_failed_total`: Failed workflows
- `temporal_activity_execution_latency`: Activity execution time
- `temporal_request_latency`: Server request latency

### Grafana Dashboard

Import Temporal's official Grafana dashboards:
- [Temporal Server Metrics](https://github.com/temporalio/dashboards)

---

## Troubleshooting

### Worker Connection Failed

**Error**: `failed to connect to temporal server`

**Solution**:
1. Ensure Temporal server is running: `temporal workflow list`
2. Check `TEMPORAL_HOST` environment variable
3. Verify port 7233 is accessible: `nc -zv localhost 7233`

### Database Locked (SQLite)

**Error**: `database is locked`

**Solution**:
- Use PostgreSQL for production
- Ensure only one worker for SQLite dev mode
- Check for orphaned connections

### Activity Timeout

**Error**: `activity timeout`

**Solution**:
- Increase `start_to_close_timeout` in workflow
- Add activity heartbeats for long-running operations
- Check worker logs for actual errors

### Workflow Not Found

**Error**: `workflow type not registered`

**Solution**:
- Ensure workflow is registered in worker
- Restart worker to pick up new workflows
- Check workflow name matches exactly

---

## Performance Tuning

### Worker Configuration

```python
# Increase concurrent activities
worker = Worker(
    client,
    task_queue=TASK_QUEUE,
    workflows=workflows,
    activities=activities,
    max_concurrent_activities=100,  # Default: 100
    max_concurrent_workflows=50,     # Default: 100
)
```

### Database Optimization

For PostgreSQL:
- Use connection pooling
- Index workflow search attributes
- Regular vacuuming
- Monitor query performance

### Horizontal Scaling

Deploy multiple workers for load distribution:

```bash
# Worker 1
python -m tracertm.workflows.worker

# Worker 2
python -m tracertm.workflows.worker

# Worker 3
python -m tracertm.workflows.worker
```

Temporal automatically distributes work across all workers.

---

## Security

### Network Security

- Restrict Temporal server access to internal network
- Use firewall rules for port 7233
- Enable TLS for external connections

### Authentication

For production, enable authentication:

```yaml
# temporal-config.yaml
global:
  authorization:
    jwtKeyProvider:
      keySourceURIs:
        - "https://your-auth-server/.well-known/jwks.json"
```

### Secrets Management

Never hardcode secrets in workflows:

```python
# ❌ BAD
api_key = "sk-1234567890"

# ✅ GOOD
import os
api_key = os.getenv("API_KEY")
```

---

## Next Steps

1. **Review Migration Guide**: See [HATCHET_TO_TEMPORAL_MIGRATION.md](./HATCHET_TO_TEMPORAL_MIGRATION.md)
2. **Check Quick Reference**: See [TEMPORAL_QUICK_REFERENCE.md](../reference/TEMPORAL_QUICK_REFERENCE.md)
3. **Explore Examples**: Review existing workflows in `src/tracertm/workflows/`
4. **Read Best Practices**: [Temporal Python SDK Docs](https://docs.temporal.io/dev-guide/python)

---

## Resources

### Documentation

- [Temporal Python SDK](https://docs.temporal.io/dev-guide/python)
- [Temporal CLI Reference](https://docs.temporal.io/cli)
- [Workflow Development](https://docs.temporal.io/workflows)
- [Activity Development](https://docs.temporal.io/activities)

### Tools

- [Temporal UI](http://localhost:8233)
- [Temporal CLI](https://github.com/temporalio/cli)
- [Temporal Web](https://github.com/temporalio/ui)

### Community

- [Temporal Community Slack](https://temporal.io/slack)
- [GitHub Discussions](https://github.com/temporalio/temporal/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/temporal-workflow)

---

**Last Updated**: 2026-01-31
**Author**: TraceRTM Team
**Status**: Production Ready
