# Hatchet to Temporal Migration Guide

## Overview

This guide documents the migration from Hatchet workflow orchestration to Temporal workflow orchestration in TraceRTM.

**Status**: Phase 5 Implementation Complete - Migration Ready

**Date**: 2026-01-31

---

## Why Migrate to Temporal?

### Temporal Advantages

1. **Open Source & Self-Hosted**: Full control over infrastructure, no vendor lock-in
2. **Production-Ready**: Battle-tested by Uber, Netflix, Stripe, and others
3. **Strong Consistency**: ACID guarantees for workflow state
4. **Advanced Features**:
   - Signals and queries for workflow interaction
   - Child workflows and continue-as-new
   - Activity heartbeats and cancellation
   - Cron workflows with better scheduling
5. **Better Development Experience**:
   - Type-safe Python SDK
   - Time-travel debugging
   - Comprehensive observability
6. **Cost**: Free for self-hosted deployments

### Hatchet Limitations

1. Cloud-based requiring API token
2. Limited self-hosting options
3. Less mature ecosystem
4. Fewer integrations and tooling

---

## Architecture Changes

### Before (Hatchet)

```
┌─────────────────────┐
│  Python FastAPI     │
│  ┌───────────────┐  │
│  │ HatchetService│  │
│  └───────┬───────┘  │
│          │ HTTP API │
└──────────┼──────────┘
           │
           ▼
  ┌─────────────────┐
  │  Hatchet Cloud  │
  │  (External SaaS)│
  └─────────────────┘
```

### After (Temporal)

```
┌─────────────────────┐       ┌──────────────────┐
│  Python FastAPI     │       │  Temporal Worker │
│  ┌────────────────┐ │       │  ┌─────────────┐ │
│  │TemporalService │◄┼───────┼─►│  Workflows  │ │
│  └────────────────┘ │       │  │  Activities │ │
└─────────────────────┘       │  └─────────────┘ │
                              └──────────────────┘
           │                           │
           ▼                           ▼
  ┌─────────────────────────────────────┐
  │     Temporal Server (Local)         │
  │     SQLite/PostgreSQL Backend       │
  └─────────────────────────────────────┘
```

---

## Files Changed

### New Files Created

1. **`src/tracertm/workflows/worker.py`**
   - Temporal worker implementation
   - Connects to Temporal server
   - Registers all workflows and activities

2. **`src/tracertm/workflows/activities.py`**
   - Temporal activity definitions
   - Wraps existing task implementations
   - Adds new sample activities (indexing, analysis)

3. **`src/tracertm/workflows/workflows.py`**
   - Temporal workflow definitions
   - Orchestrates activities with retry policies
   - Durable execution guarantees

4. **`src/tracertm/services/temporal_service.py`**
   - Service layer for Temporal client
   - Workflow execution management
   - Health checks and monitoring

### Files To Update (Not Yet Migrated)

These files still reference Hatchet and need migration:

1. **`src/tracertm/workflows/hatchet_worker.py`** → Archive or delete
2. **`src/tracertm/services/hatchet_service.py`** → Replace with temporal_service.py
3. **`src/tracertm/api/main.py`** → Update HatchetService import
4. **`src/tracertm/preflight.py`** → Update preflight checks

---

## Workflow Mapping

### Graph Operations

| Hatchet Workflow | Temporal Workflow | Status |
|-----------------|-------------------|--------|
| `graph.snapshot` | `GraphSnapshotWorkflow` | ✅ Migrated |
| `graph.validate` | `GraphValidationWorkflow` | ✅ Migrated |
| `graph.export` | `GraphExportWorkflow` | ✅ Migrated |
| `graph.diff` | `GraphDiffWorkflow` | ✅ Migrated |

### Integration Operations

| Hatchet Workflow | Temporal Workflow | Status |
|-----------------|-------------------|--------|
| `integrations.sync` | `IntegrationSyncWorkflow` | ✅ Migrated |
| `integrations.retry` | `IntegrationRetryWorkflow` | ✅ Migrated |

### New Workflows

| Workflow | Purpose |
|----------|---------|
| `IndexingWorkflow` | Repository code indexing |
| `AnalysisWorkflow` | Quality analysis automation |

---

## Environment Configuration

### Old Configuration (Hatchet)

```bash
# Remove these from .env
HATCHET_CLIENT_TOKEN=YOUR_HATCHET_TOKEN
HATCHET_API_URL=https://cloud.onhatchet.run
```

### New Configuration (Temporal)

```bash
# Add to .env
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# For Temporal Cloud (optional)
# TEMPORAL_HOST=your-namespace.tmprl.cloud:7233
# TEMPORAL_NAMESPACE=your-namespace
# TEMPORAL_TLS_CERT=/path/to/client.pem
# TEMPORAL_TLS_KEY=/path/to/client.key
```

---

## Migration Steps

### Phase 1: Infrastructure Setup ✅

1. **Install Temporal**
   ```bash
   # macOS
   brew install temporal

   # Or download from https://github.com/temporalio/cli/releases
   ```

2. **Start Temporal Server**
   ```bash
   temporal server start-dev --db-filename .temporal/dev.db
   ```

3. **Verify Installation**
   ```bash
   temporal workflow list
   ```

### Phase 2: Code Migration ✅

1. **Install Python SDK**
   ```bash
   pip install temporalio
   ```

2. **Create Workflows and Activities** ✅
   - See `src/tracertm/workflows/`

3. **Start Worker** ✅
   ```bash
   python -m tracertm.workflows.worker
   ```

### Phase 3: Service Integration (In Progress)

1. **Update API Service**
   - Replace `HatchetService` with `TemporalService`
   - Update route handlers
   - Update health checks

2. **Update Preflight Checks**
   - Remove Hatchet checks
   - Add Temporal server checks

3. **Test Workflow Execution**
   ```bash
   # From Python API
   POST /api/workflows/start
   {
     "workflow_name": "GraphSnapshotWorkflow",
     "project_id": "...",
     "graph_id": "..."
   }
   ```

### Phase 4: Testing (Pending)

1. **Unit Tests**
   - Test workflow logic
   - Test activity implementations
   - Mock Temporal client

2. **Integration Tests**
   - End-to-end workflow execution
   - Retry and error handling
   - Timeout scenarios

3. **Load Testing**
   - Concurrent workflow execution
   - Worker scaling
   - Database performance

### Phase 5: Deployment (Pending)

1. **Update Documentation**
   - Deployment guides
   - Operations runbooks
   - Troubleshooting guides

2. **Production Deployment**
   - Deploy Temporal server
   - Deploy workers
   - Migrate existing workflows

3. **Monitoring**
   - Set up Temporal UI
   - Configure alerts
   - Monitor metrics

---

## Key Differences

### Workflow Definition

**Hatchet**:
```python
@hatchet.task(name="graph.snapshot", input_validator=GraphSnapshotInput)
async def graph_snapshot_task(input: GraphSnapshotInput, context):
    # Implementation
    pass
```

**Temporal**:
```python
@workflow.defn(name="GraphSnapshotWorkflow")
class GraphSnapshotWorkflow:
    @workflow.run
    async def run(self, project_id: str, graph_id: str):
        result = await workflow.execute_activity(
            activities.create_graph_snapshot,
            args=[project_id, graph_id],
            start_to_close_timeout=timedelta(minutes=10),
        )
        return result
```

### Activity Definition

**Hatchet**: Activities are just functions decorated with `@hatchet.task`

**Temporal**: Activities are decorated with `@activity.defn` and can include:
- Heartbeats for long-running operations
- Cancellation handlers
- Custom retry policies
- Timeout configurations

### Starting Workflows

**Hatchet**:
```python
await hatchet_service.trigger_workflow(
    workflow_name="graph.snapshot",
    input_data={"project_id": "123", "graph_id": "456"}
)
```

**Temporal**:
```python
await temporal_service.start_workflow(
    workflow_name="GraphSnapshotWorkflow",
    project_id="123",
    graph_id="456"
)
```

---

## Testing Guide

### Local Development

1. **Start Services**
   ```bash
   # Terminal 1: Temporal server
   temporal server start-dev

   # Terminal 2: Worker
   python -m tracertm.workflows.worker

   # Terminal 3: API
   uvicorn src.tracertm.api.main:app --reload
   ```

2. **Execute Workflow**
   ```bash
   # Via Temporal CLI
   temporal workflow execute \
     --type GraphSnapshotWorkflow \
     --task-queue tracertm-tasks \
     --input '{"project_id": "test", "graph_id": "test"}'

   # Via API
   curl -X POST http://localhost:4000/api/workflows/start \
     -H "Content-Type: application/json" \
     -d '{
       "workflow_name": "GraphSnapshotWorkflow",
       "project_id": "test",
       "graph_id": "test"
     }'
   ```

3. **Monitor Workflows**
   ```bash
   # List running workflows
   temporal workflow list

   # Describe specific workflow
   temporal workflow describe --workflow-id <id>

   # View Temporal UI (if running)
   open http://localhost:8233
   ```

### Testing Activities Directly

```python
# test_activities.py
import asyncio
from tracertm.workflows import activities

async def test_snapshot():
    result = await activities.create_graph_snapshot(
        project_id="test",
        graph_id="test",
        created_by="test_user",
        description="Test snapshot"
    )
    print(result)

asyncio.run(test_snapshot())
```

---

## Rollback Plan

If migration fails, rollback steps:

1. **Restore Hatchet Configuration**
   ```bash
   # Restore .env
   HATCHET_CLIENT_TOKEN=<previous_token>
   HATCHET_API_URL=https://cloud.onhatchet.run
   ```

2. **Revert Code Changes**
   ```bash
   git revert <migration_commit>
   ```

3. **Restart Services**
   ```bash
   # Stop Temporal worker
   pkill -f "tracertm.workflows.worker"

   # Restart API with Hatchet
   uvicorn src.tracertm.api.main:app --reload
   ```

---

## Production Considerations

### Temporal Server Deployment

**Option 1: Self-Hosted**
- Run Temporal server on your infrastructure
- Use PostgreSQL for persistence
- Set up Elasticsearch for visibility

**Option 2: Temporal Cloud**
- Managed service by Temporal.io
- $25/month starter plan
- Automatic scaling and monitoring

### High Availability

1. **Database**: Use PostgreSQL with replication
2. **Workers**: Deploy multiple worker instances
3. **Monitoring**: Use Temporal UI + Prometheus/Grafana
4. **Backups**: Regular database backups

### Security

1. **TLS**: Enable mTLS for production
2. **Authentication**: Use namespace-level auth
3. **Secrets**: Store credentials in environment
4. **Network**: Restrict Temporal server access

---

## Resources

### Documentation

- [Temporal Python SDK](https://docs.temporal.io/dev-guide/python)
- [Temporal Architecture](https://docs.temporal.io/clusters)
- [Best Practices](https://docs.temporal.io/dev-guide/python/foundations)

### Tools

- [Temporal CLI](https://docs.temporal.io/cli)
- [Temporal UI](https://github.com/temporalio/ui)
- [tctl](https://docs.temporal.io/tctl-v1) (legacy CLI)

### Community

- [Temporal Community Slack](https://temporal.io/slack)
- [GitHub Discussions](https://github.com/temporalio/temporal/discussions)

---

## Support & Troubleshooting

### Common Issues

**Issue**: Worker fails to connect to Temporal server
```
Error: failed to connect to temporal server
```
**Solution**: Ensure Temporal server is running on correct host/port

**Issue**: Workflow execution timeout
```
Error: activity timeout
```
**Solution**: Increase `start_to_close_timeout` or add heartbeats

**Issue**: Database locked (SQLite)
```
Error: database is locked
```
**Solution**: Use PostgreSQL for production or single worker for dev

### Getting Help

1. Check Temporal UI for workflow history
2. Review worker logs for errors
3. Use `temporal workflow describe` for details
4. Consult Temporal documentation
5. Ask in Temporal community Slack

---

## 2026-01-31 Migration Notes

1. Added `workflow_schedules` table for Temporal schedule tracking.
2. Added schedule bootstrap endpoints for graph snapshots and integration retries.
3. Updated dev bootstrap to ensure Temporal namespace exists (`scripts/start-services.sh temporal`).
4. Added required MCP provider/monitoring envs to `.env` and `.env.example`.

## Next Steps

1. ✅ Complete Phase 5 implementation
2. 🔄 Update API service to use TemporalService
3. 🔄 Update preflight checks
4. ⏳ Add comprehensive tests
5. ⏳ Update production deployment scripts
6. ⏳ Create operations runbooks
7. ⏳ Archive Hatchet code

---

**Last Updated**: 2026-01-31
**Author**: TraceRTM Team
**Status**: Phase 5 Complete - Ready for Service Integration
