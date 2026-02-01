# Temporal Quick Start Guide

**Get TraceRTM workflows running with Temporal in 5 minutes**

---

## Prerequisites

- Python 3.11+
- PostgreSQL or SQLite (for Temporal persistence)
- TraceRTM development environment set up

---

## 1. Install Temporal CLI

### macOS
```bash
brew install temporal
```

### Linux
```bash
curl -sSf https://temporal.download/cli.sh | sh
```

### Windows
```powershell
# Download from https://github.com/temporalio/cli/releases
# Extract and add to PATH
```

### Verify Installation
```bash
temporal --version
```

---

## 2. Install Python SDK

```bash
# Install Temporal Python SDK
pip install temporalio

# Or add to requirements.txt
echo "temporalio>=1.5.0" >> requirements.txt
pip install -r requirements.txt
```

---

## 3. Configure Environment

Add to `.env`:

```bash
# Temporal Configuration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
```

---

## 4. Start Temporal Server

### Development Mode (SQLite)

```bash
# Start Temporal dev server (includes UI)
temporal server start-dev --db-filename .temporal/dev.db
```

This starts:
- Temporal server on `localhost:7233`
- Temporal UI on `http://localhost:8233`

### Production Mode (PostgreSQL)

```bash
# Create PostgreSQL database
createdb temporal

# Start Temporal server with PostgreSQL
temporal server start \
  --db-filename temporal \
  --db-driver postgres \
  --db-host localhost \
  --db-port 5432
```

---

## 5. Start Temporal Worker

In a new terminal:

```bash
# Start the TraceRTM worker
python -m tracertm.workflows.worker
```

Expected output:
```
INFO [2026-01-31 12:00:00] Connecting to Temporal at localhost:7233
INFO [2026-01-31 12:00:00] Connected to Temporal server
INFO [2026-01-31 12:00:00] Starting Temporal worker on task queue: tracertm-tasks
INFO [2026-01-31 12:00:00] Registered workflows: ...
INFO [2026-01-31 12:00:00] Worker started
```

---

## 6. Run Using Overmind (Recommended)

Update your `Procfile` (already done):

```
temporal: temporal server start-dev --db-filename .temporal/dev.db
temporal_worker: python -m tracertm.workflows.worker
```

Start all services:

```bash
overmind start
```

Or start just Temporal services:

```bash
overmind start temporal temporal_worker
```

---

## 7. Execute a Workflow

### Via Temporal CLI

```bash
# Execute graph snapshot workflow
temporal workflow execute \
  --type GraphSnapshotWorkflow \
  --task-queue tracertm-tasks \
  --input '{
    "project_id": "test-project",
    "graph_id": "test-graph",
    "created_by": "admin",
    "description": "Test snapshot"
  }'
```

### Via Python API

```python
from tracertm.services.temporal_service import TemporalService

async def run_workflow():
    service = TemporalService()

    result = await service.start_workflow(
        workflow_name="GraphSnapshotWorkflow",
        project_id="test-project",
        graph_id="test-graph",
        created_by="admin",
        description="Test snapshot"
    )

    print(f"Workflow started: {result['workflow_id']}")

# Run it
import asyncio
asyncio.run(run_workflow())
```

### Via HTTP API (once integrated)

```bash
curl -X POST http://localhost:4000/api/workflows/start \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "GraphSnapshotWorkflow",
    "project_id": "test-project",
    "graph_id": "test-graph",
    "created_by": "admin",
    "description": "Test snapshot"
  }'
```

---

## 8. Monitor Workflows

### Temporal UI

Open browser to `http://localhost:8233`

Features:
- View all workflow executions
- Inspect workflow history
- See activity results
- Debug failed workflows

### Temporal CLI

```bash
# List all workflows
temporal workflow list

# Describe a specific workflow
temporal workflow describe --workflow-id <workflow-id>

# Show workflow execution history
temporal workflow show --workflow-id <workflow-id>

# Cancel a workflow
temporal workflow cancel --workflow-id <workflow-id>
```

---

## Available Workflows

### Graph Operations

| Workflow | Description | Example |
|----------|-------------|---------|
| `GraphSnapshotWorkflow` | Create graph snapshot | Version control |
| `GraphValidationWorkflow` | Validate graph integrity | Pre-commit check |
| `GraphExportWorkflow` | Export graph to JSON | Backup/migration |
| `GraphDiffWorkflow` | Compare graph versions | Code review |

### Integration Operations

| Workflow | Description | Example |
|----------|-------------|---------|
| `IntegrationSyncWorkflow` | Process pending syncs | GitHub integration |
| `IntegrationRetryWorkflow` | Retry failed syncs | Error recovery |

### Analysis Operations

| Workflow | Description | Example |
|----------|-------------|---------|
| `IndexingWorkflow` | Index repository code | New repo setup |
| `AnalysisWorkflow` | Quality analysis | CI/CD pipeline |

---

## Quick Examples

### 1. Create Graph Snapshot

```bash
temporal workflow execute \
  --type GraphSnapshotWorkflow \
  --task-queue tracertm-tasks \
  --input '{"project_id": "p1", "graph_id": "g1"}'
```

### 2. Validate Graph

```bash
temporal workflow execute \
  --type GraphValidationWorkflow \
  --task-queue tracertm-tasks \
  --input '{"project_id": "p1", "graph_id": "g1"}'
```

### 3. Export Graph

```bash
temporal workflow execute \
  --type GraphExportWorkflow \
  --task-queue tracertm-tasks \
  --input '{"project_id": "p1"}'
```

### 4. Process Integration Syncs

```bash
temporal workflow execute \
  --type IntegrationSyncWorkflow \
  --task-queue tracertm-tasks \
  --input '{"limit": 50}'
```

---

## Troubleshooting

### Worker Not Starting

**Error**: `Cannot connect to Temporal server`

**Solution**:
```bash
# Check if Temporal server is running
temporal workflow list

# If not, start it
temporal server start-dev
```

### Workflow Not Executing

**Error**: `No worker available`

**Solution**:
```bash
# Ensure worker is running
python -m tracertm.workflows.worker

# Check worker logs
```

### Database Locked (SQLite)

**Error**: `database is locked`

**Solution**:
- Use PostgreSQL for multi-worker setup
- Or run single worker for development

### Port Already in Use

**Error**: `Address already in use: 7233`

**Solution**:
```bash
# Kill existing Temporal server
pkill -f temporal

# Or use different port
temporal server start-dev --port 7234
```

---

## Development Workflow

1. **Start Services**
   ```bash
   overmind start
   ```

2. **Make Changes**
   - Edit workflows in `src/tracertm/workflows/workflows.py`
   - Edit activities in `src/tracertm/workflows/activities.py`

3. **Restart Worker** (hot reload not supported)
   ```bash
   overmind restart temporal_worker
   ```

4. **Test Workflow**
   ```bash
   temporal workflow execute --type YourWorkflow ...
   ```

5. **Monitor in UI**
   - Open `http://localhost:8233`
   - View execution history
   - Debug failures

---

## Next Steps

- 📖 Read [Hatchet to Temporal Migration Guide](./HATCHET_TO_TEMPORAL_MIGRATION.md)
- 🔧 Customize workflows for your use case
- 📊 Set up monitoring and alerts
- 🚀 Deploy to production

---

**Pro Tips**

1. **Use Workflow IDs**: Provide meaningful workflow IDs for easier debugging
2. **Set Timeouts**: Configure appropriate timeouts for activities
3. **Add Retries**: Use retry policies for transient failures
4. **Monitor UI**: Keep Temporal UI open during development
5. **Check Logs**: Worker logs show detailed execution info

---

**Last Updated**: 2026-01-31
**Related**: [HATCHET_TO_TEMPORAL_MIGRATION.md](./HATCHET_TO_TEMPORAL_MIGRATION.md)
