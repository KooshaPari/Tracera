# Phase 3: Temporal Workflows for Agent Execution - Implementation Guide

## Overview

Phase 3 implements durable agent execution workflows with automatic checkpoint management using Temporal. This enables long-running agent conversations with session resumability and crash recovery.

## Architecture

### Components

1. **Agent Execution Workflows**
   - `AgentExecutionWorkflow`: Main durable execution with checkpointing
   - `AgentExecutionResumeWorkflow`: Resume from checkpoint

2. **Snapshot Workflows**
   - `SandboxSnapshotWorkflow`: Create sandbox snapshots
   - `BulkSnapshotWorkflow`: Bulk snapshot operations
   - `SnapshotCleanupWorkflow`: Cleanup old snapshots

3. **Checkpoint Activities**
   - `create_checkpoint`: Save conversation state
   - `load_latest_checkpoint`: Resume from latest state
   - `execute_ai_turn`: Run AI with tools in sandbox
   - `create_sandbox_snapshot`: Archive sandbox state

4. **CheckpointService**
   - Database CRUD operations for checkpoints
   - Session resume capability
   - Checkpoint cleanup and statistics

## Implementation Details

### 1. Agent Execution Workflow

**File**: `/src/tracertm/workflows/agent_execution.py`

```python
# Start agent execution with checkpointing
workflow_result = await temporal_service.start_workflow(
    workflow_name="AgentExecutionWorkflow",
    session_id="my-session-123",
    initial_messages=[
        {"role": "user", "content": "Help me build a Python app"}
    ],
    max_turns=50,
    checkpoint_interval=5,  # Checkpoint every 5 turns
)
```

**Features**:
- Automatic checkpoint creation every 5 turns (configurable)
- Heartbeat monitoring with 30-second timeout
- Automatic retry on transient failures
- Session state persistence across restarts
- Resume from latest checkpoint if no initial messages provided

### 2. Sandbox Snapshot Workflow

**File**: `/src/tracertm/workflows/sandbox_snapshot.py`

```python
# Create snapshot of session sandbox
snapshot_result = await temporal_service.start_workflow(
    workflow_name="SandboxSnapshotWorkflow",
    session_id="my-session-123",
    compression="gzip",
    retention_days=30,
)
```

**Features**:
- Periodic sandbox backup (prepared for MinIO integration)
- Configurable compression (gzip, bzip2, none)
- Retention policy support
- Metadata tracking with S3 key references

### 3. Checkpoint Activities

**File**: `/src/tracertm/workflows/checkpoint_activities.py`

All activities are idempotent and handle database persistence:

- `create_checkpoint(session_id, turn_number, state_snapshot, metadata)`
- `load_latest_checkpoint(session_id)`
- `load_checkpoint_by_turn(session_id, turn_number)`
- `execute_ai_turn(session_id, messages, model, system_prompt)`
- `create_sandbox_snapshot(session_id, snapshot_name, ...)`

### 4. Checkpoint Service

**File**: `/src/tracertm/services/checkpoint_service.py`

Service layer for checkpoint management:

```python
from tracertm.services.checkpoint_service import get_checkpoint_service

checkpoint_service = get_checkpoint_service()

# Create checkpoint
checkpoint = await checkpoint_service.create_checkpoint(
    session_id="my-session-123",
    turn_number=5,
    state_snapshot={
        "messages": [...],
        "model": "claude-sonnet-4-20250514",
    },
)

# Load latest checkpoint
latest = await checkpoint_service.load_latest_checkpoint("my-session-123")

# List all checkpoints
checkpoints = await checkpoint_service.list_checkpoints("my-session-123")

# Cleanup old checkpoints (keep 10 most recent)
deleted = await checkpoint_service.cleanup_old_checkpoints(
    session_id="my-session-123",
    keep_count=10,
)
```

## Database Schema

### AgentCheckpoint Table

```sql
CREATE TABLE agent_checkpoints (
    id UUID PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES agent_sessions(session_id),
    turn_number INTEGER NOT NULL,
    state_snapshot JSONB NOT NULL,
    sandbox_snapshot_s3_key VARCHAR(1024),
    checkpoint_metadata JSONB,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, turn_number)
);

CREATE INDEX ix_agent_checkpoints_session_id ON agent_checkpoints(session_id);
CREATE INDEX ix_agent_checkpoints_turn_number ON agent_checkpoints(turn_number);
```

## Usage Examples

### Example 1: Start New Agent Session with Checkpointing

```python
from tracertm.services.temporal_service import TemporalService

temporal = TemporalService()

# Start agent execution
result = await temporal.start_workflow(
    workflow_name="AgentExecutionWorkflow",
    workflow_id="agent-session-abc123",
    session_id="my-session-abc123",
    initial_messages=[
        {"role": "user", "content": "Create a FastAPI service"}
    ],
    max_turns=50,
    checkpoint_interval=5,
    model="claude-sonnet-4-20250514",
)

print(f"Workflow started: {result['workflow_id']}")
```

### Example 2: Resume from Checkpoint

```python
# Resume from latest checkpoint
result = await temporal.start_workflow(
    workflow_name="AgentExecutionResumeWorkflow",
    workflow_id="agent-resume-abc123",
    session_id="my-session-abc123",
    max_additional_turns=25,
)
```

### Example 3: Create Scheduled Snapshots

```python
# Create recurring snapshot schedule
schedule_result = await temporal.create_schedule(
    schedule_id="daily-snapshots",
    workflow_name="BulkSnapshotWorkflow",
    args=[None, 10, "gzip", 30],  # All sessions, max 10 concurrent
    cron_expressions=["0 2 * * *"],  # Daily at 2 AM
)
```

### Example 4: Manual Checkpoint Management

```python
from tracertm.services.checkpoint_service import get_checkpoint_service

service = get_checkpoint_service()

# Get checkpoint statistics
stats = await service.get_checkpoint_stats("my-session-123")
print(f"Total checkpoints: {stats['total_checkpoints']}")
print(f"Latest turn: {stats['latest_turn']}")

# Load specific checkpoint
checkpoint = await service.load_checkpoint_by_turn(
    session_id="my-session-123",
    turn_number=15,
)
```

## Testing

Run the checkpoint service tests:

```bash
# From project root
pytest tests/workflows/test_agent_execution_workflow.py -v

# Specific test
pytest tests/workflows/test_agent_execution_workflow.py::TestCheckpointService::test_create_checkpoint -v
```

## Configuration

### Environment Variables

```bash
# Temporal configuration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=tracertm-tasks

# Database configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/tracertm
```

### Checkpoint Configuration

- **Checkpoint Interval**: Default 5 turns (configurable per workflow)
- **Heartbeat Timeout**: 30 seconds for long-running activities
- **Retry Policy**: 3 attempts with exponential backoff
- **Max Turns**: Default 50 (configurable per workflow)

## Integration with Existing Systems

### AgentService Integration

The workflows use the existing `AgentService` for sandbox resolution:

```python
from tracertm.agent import get_agent_service

agent_svc = get_agent_service()
sandbox_path, created = await agent_svc.get_or_create_session_sandbox(
    session_id="my-session-123"
)
```

### GraphSessionStore Integration

Checkpoint data integrates with Neo4j session tracking:

- Session nodes track checkpoint references
- Tool call tracking across checkpoints
- Session lineage and fork relationships

## MinIO Integration (Phase 4 Preparation)

Phase 3 includes placeholder S3 keys for snapshot storage:

```python
# Current placeholder
s3_key = f"sandboxes/{session_id}/snapshots/snapshot-turn-{turn_number}.tar.gz"

# Phase 4 will implement actual MinIO upload:
# - Upload tar.gz archive to MinIO
# - Update checkpoint with actual S3 key
# - Implement download/restore functionality
```

## Monitoring and Debugging

### Temporal UI

Access the Temporal UI to monitor workflows:

```
http://localhost:8233
```

### Workflow Status

```python
# Get workflow result
result = await temporal.get_workflow_result("agent-session-abc123")
print(f"Status: {result['status']}")
```

### Checkpoint Logs

Checkpoints include metadata for debugging:

```python
checkpoint_metadata = {
    "turn_count": 15,
    "workflow_id": "agent-session-abc123",
    "workflow_run_id": "abc123-def456",
    "checkpoint_reason": "interval",  # or "error"
}
```

## Error Handling

### Workflow-Level Errors

- Workflows create checkpoints on error for recovery
- Non-retryable errors: ValueError, PermissionError
- Retryable errors: Network issues, temporary failures

### Activity-Level Errors

- Activities return error results instead of raising
- Graceful degradation for checkpoint failures
- Heartbeat signals for long-running operations

## Performance Considerations

- **Checkpoint Size**: State snapshots stored as JSONB (efficient)
- **Snapshot Compression**: gzip reduces storage by ~70%
- **Concurrent Limits**: BulkSnapshotWorkflow limits to 5 concurrent snapshots
- **Database Indexes**: Optimized for session_id and turn_number queries

## Next Steps (Phase 4)

Phase 4 will implement MinIO snapshot storage:

1. **MinIO Upload**: Actual tar.gz upload to S3-compatible storage
2. **Snapshot Download**: Restore sandbox from snapshot
3. **Storage Management**: Cleanup old snapshots from MinIO
4. **Compression Options**: Support for multiple compression algorithms
5. **Snapshot Validation**: Verify snapshot integrity

## Troubleshooting

### Common Issues

**Checkpoint creation fails**:
- Check database connection
- Verify session exists in `agent_sessions` table
- Ensure unique constraint not violated

**Workflow hangs**:
- Check Temporal worker is running
- Verify task queue name matches
- Review activity timeout settings

**Resume from checkpoint fails**:
- Verify checkpoint exists for session
- Check turn_number is valid
- Ensure session sandbox still exists

## API Reference

See `/src/tracertm/workflows/` for complete API documentation:

- `agent_execution.py`: Workflow definitions
- `sandbox_snapshot.py`: Snapshot workflows
- `checkpoint_activities.py`: Activity implementations
- `/src/tracertm/services/checkpoint_service.py`: Service layer

## Summary

Phase 3 provides:

✅ Durable agent execution with automatic checkpointing
✅ Session resumability across crashes and restarts
✅ Comprehensive checkpoint management service
✅ Prepared for MinIO snapshot integration (Phase 4)
✅ Integration with existing AgentService and databases
✅ Production-ready error handling and retry logic

The implementation enables reliable long-running agent sessions with full conversation state persistence and recovery capabilities.
