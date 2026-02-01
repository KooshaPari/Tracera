# Phase 3: Temporal Workflows - Quick Reference

## Quick Start

### Start Agent with Checkpointing

```python
from tracertm.services.temporal_service import TemporalService

temporal = TemporalService()

result = await temporal.start_workflow(
    workflow_name="AgentExecutionWorkflow",
    session_id="my-session-123",
    initial_messages=[{"role": "user", "content": "Hello"}],
    max_turns=50,
    checkpoint_interval=5,
)
```

### Resume from Checkpoint

```python
result = await temporal.start_workflow(
    workflow_name="AgentExecutionResumeWorkflow",
    session_id="my-session-123",
)
```

### Create Sandbox Snapshot

```python
result = await temporal.start_workflow(
    workflow_name="SandboxSnapshotWorkflow",
    session_id="my-session-123",
    compression="gzip",
    retention_days=30,
)
```

## Workflows

| Workflow | Purpose | Key Parameters |
|----------|---------|----------------|
| `AgentExecutionWorkflow` | Durable agent execution | `session_id`, `checkpoint_interval`, `max_turns` |
| `AgentExecutionResumeWorkflow` | Resume from checkpoint | `session_id`, `checkpoint_turn` |
| `SandboxSnapshotWorkflow` | Create sandbox snapshot | `session_id`, `compression`, `retention_days` |
| `BulkSnapshotWorkflow` | Bulk snapshot creation | `session_ids`, `max_concurrent` |
| `SnapshotCleanupWorkflow` | Cleanup old snapshots | `retention_days`, `dry_run` |

## Checkpoint Service

```python
from tracertm.services.checkpoint_service import get_checkpoint_service

service = get_checkpoint_service()

# Create checkpoint
checkpoint = await service.create_checkpoint(
    session_id="my-session",
    turn_number=5,
    state_snapshot={"messages": [...]},
)

# Load latest
latest = await service.load_latest_checkpoint("my-session")

# Load specific turn
checkpoint = await service.load_checkpoint_by_turn("my-session", 5)

# List all
checkpoints = await service.list_checkpoints("my-session")

# Get stats
stats = await service.get_checkpoint_stats("my-session")

# Cleanup old (keep 10)
deleted = await service.cleanup_old_checkpoints("my-session", keep_count=10)
```

## Checkpoint Activities

| Activity | Purpose | Parameters |
|----------|---------|------------|
| `create_checkpoint` | Save conversation state | `session_id`, `turn_number`, `state_snapshot` |
| `load_latest_checkpoint` | Load most recent | `session_id` |
| `load_checkpoint_by_turn` | Load specific turn | `session_id`, `turn_number` |
| `execute_ai_turn` | Run AI with tools | `session_id`, `messages`, `model` |
| `create_sandbox_snapshot` | Archive sandbox | `session_id`, `snapshot_name`, `compression` |
| `update_session_snapshot_ref` | Update S3 reference | `session_id`, `s3_key` |
| `list_active_sessions` | List all sessions | - |
| `cleanup_old_snapshots` | Remove old snapshots | `retention_days`, `dry_run` |

## Configuration

### Environment Variables

```bash
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=tracertm-tasks
DATABASE_URL=postgresql://user:pass@localhost/tracertm
```

### Default Settings

- **Checkpoint Interval**: 5 turns
- **Heartbeat Timeout**: 30 seconds
- **Max Retry Attempts**: 3
- **Max Turns**: 50
- **Snapshot Compression**: gzip
- **Retention Days**: 30

## Database Schema

### agent_checkpoints Table

```sql
CREATE TABLE agent_checkpoints (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    turn_number INTEGER NOT NULL,
    state_snapshot JSONB NOT NULL,
    sandbox_snapshot_s3_key VARCHAR(1024),
    checkpoint_metadata JSONB,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(session_id, turn_number)
);
```

## Testing

```bash
# Run all checkpoint tests
pytest tests/workflows/test_agent_execution_workflow.py -v

# Run specific test
pytest tests/workflows/test_agent_execution_workflow.py::TestCheckpointService::test_create_checkpoint
```

## Temporal Worker

### Start Worker

```bash
python -m tracertm.workflows.worker
```

### Worker Configuration

The worker automatically registers:
- 5 agent execution workflows
- 8 checkpoint activities
- Task queue: `tracertm-tasks`

## Monitoring

### Temporal UI

```
http://localhost:8233
```

### Get Workflow Status

```python
result = await temporal.get_workflow_result("workflow-id")
print(f"Status: {result['status']}")
```

### Checkpoint Statistics

```python
stats = await service.get_checkpoint_stats("session-id")
# Returns: total_checkpoints, latest_turn, oldest_turn, latest_checkpoint_at
```

## Common Patterns

### 1. Long-Running Agent Task

```python
# Start with checkpointing
result = await temporal.start_workflow(
    workflow_name="AgentExecutionWorkflow",
    session_id="build-project-123",
    initial_messages=[
        {"role": "user", "content": "Build a complete Python API"}
    ],
    max_turns=100,  # Allow many iterations
    checkpoint_interval=5,  # Checkpoint frequently
)
```

### 2. Scheduled Snapshots

```python
# Daily snapshots at 2 AM
await temporal.create_schedule(
    schedule_id="daily-backup",
    workflow_name="BulkSnapshotWorkflow",
    args=[None, 10, "gzip", 30],
    cron_expressions=["0 2 * * *"],
)
```

### 3. Error Recovery

```python
# If workflow fails, resume from checkpoint
result = await temporal.start_workflow(
    workflow_name="AgentExecutionResumeWorkflow",
    session_id="failed-session-123",
    max_additional_turns=50,
)
```

### 4. Cleanup Old Data

```python
# Remove snapshots older than 7 days
result = await temporal.start_workflow(
    workflow_name="SnapshotCleanupWorkflow",
    retention_days=7,
    dry_run=False,
)
```

## Error Handling

### Non-Retryable Errors

- `ValueError`: Invalid parameters
- `FileNotFoundError`: Sandbox doesn't exist
- `PermissionError`: Access denied

### Retryable Errors

- Network failures (3 retries with backoff)
- Temporary database issues
- Transient Temporal errors

## File Locations

| Component | Location |
|-----------|----------|
| Workflows | `/src/tracertm/workflows/agent_execution.py` |
| Snapshot Workflows | `/src/tracertm/workflows/sandbox_snapshot.py` |
| Activities | `/src/tracertm/workflows/checkpoint_activities.py` |
| Service | `/src/tracertm/services/checkpoint_service.py` |
| Worker | `/src/tracertm/workflows/worker.py` |
| Tests | `/tests/workflows/test_agent_execution_workflow.py` |
| Models | `/src/tracertm/models/agent_checkpoint.py` |

## Next Steps

**Phase 4**: MinIO Snapshot Service
- Actual S3/MinIO upload implementation
- Snapshot download and restore
- Storage cleanup and management

**Phase 5**: NATS Event Streaming
- Checkpoint creation events
- Snapshot completion events
- Real-time monitoring

## Support

See full documentation:
- `/docs/guides/PHASE_3_TEMPORAL_WORKFLOWS_GUIDE.md`
- Temporal docs: https://docs.temporal.io/
