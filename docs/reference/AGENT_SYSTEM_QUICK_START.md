# Agent System Quick Start Guide

**Last Updated:** 2026-01-31
**Status:** Production Ready
**For:** Developers, DevOps, System Administrators

**When used by AI agents:** Planner agents must never write code in documentation or plans; they equip engineer/executor agents or humans to create code or act on docs. Avoid stuffing docs/plans with code where not relevant.

---

## 🚀 5-Minute Quick Start

### Prerequisites

```bash
# Infrastructure services running
docker-compose up -d postgres neo4j redis minio nats temporal

# Environment configured
cp .env.example .env
# Edit: Add OAuth credentials, database URLs
```

### Start the System

```bash
# Terminal 1: Go backend (includes CLIProxy)
cd backend
go run main.go
# ✅ HTTP API: localhost:8080
# ✅ CLIProxy: localhost:8765
# ✅ gRPC: localhost:9090

# Terminal 2: Python backend
cd src
uvicorn tracertm.api.main:app --reload --port 8000
# ✅ FastAPI: localhost:8000

# Terminal 3: Temporal worker
python -m tracertm.workflows.worker
# ✅ Processes: AgentExecutionWorkflow, SandboxSnapshotWorkflow
```

### Test the System

```bash
# Health checks
curl http://localhost:8080/health  # Go backend
curl http://localhost:4000/health  # Python backend
curl http://localhost:8765/health  # CLIProxy

# Run integration tests
pytest tests/integration/ -v
# Expected: 58 passed, 8 skipped
```

---

## 📚 Core Concepts

### 1. Agent Session

**What:** Persistent conversation with dedicated sandbox directory

**Lifecycle:**
```
Create → Execute → Checkpoint → Resume → Complete
```

**Storage:**
- PostgreSQL: Metadata (session_id, sandbox_root, project_id)
- Neo4j: Graph (relationships, tool calls, lineage)
- Redis: Cache (1-hour TTL)
- MinIO: Snapshots (every 5 turns)

### 2. Checkpoint

**What:** Conversation state snapshot at specific turn

**Contains:**
- Message history
- Tool execution state
- Model configuration
- Sandbox snapshot reference (S3 key)

**Frequency:** Every 5 turns (configurable)

### 3. Sandbox Snapshot

**What:** Tar-compressed filesystem backup

**Storage:** `s3://tracertm/sandboxes/{session_id}/snapshots/snapshot-{turn}.tar.gz`

**Size:** ~10-20% of original (gzip compression)

### 4. Events

**What:** Real-time NATS messages for system events

**Types:** 9 event types (session, chat, snapshot)

**Subjects:** `tracertm.{category}.{session_id}.{event_type}`

---

## 🔧 Common Operations

### Create an Agent Session

```python
from tracertm.agent import get_agent_service
from tracertm.agent.types import SandboxConfig

agent = get_agent_service()

# Stream chat
async for chunk in agent.stream_chat_with_sandbox(
    messages=[{"role": "user", "content": "Hello!"}],
    session_id="session-123",
    provider="claude",
    model="claude-sonnet-4",
    sandbox_config=SandboxConfig(project_id=uuid.UUID("...")),
    db_session=db
):
    print(chunk, end="")
```

### Create a Checkpoint

```python
from tracertm.services.checkpoint_service import CheckpointService

checkpoint_svc = CheckpointService(db_session=db)

# Save checkpoint
checkpoint = await checkpoint_svc.create_checkpoint(
    session_id="session-123",
    turn_number=10,
    state_snapshot={
        "messages": [...],
        "tool_history": [...],
        "model": "claude-sonnet-4"
    },
    s3_key="sandboxes/session-123/snapshots/snapshot-10.tar.gz"
)
```

### Resume from Checkpoint

```python
# Load latest checkpoint
checkpoint = await checkpoint_svc.load_latest_checkpoint("session-123")

# Restore sandbox
from tracertm.agent.sandbox.snapshot import SandboxSnapshotService

snapshot_svc = SandboxSnapshotService(s3_storage)
await snapshot_svc.restore_snapshot(
    session_id="session-123",
    s3_key=checkpoint.sandbox_snapshot_s3_key,
    target_dir="/sandboxes/session-123"
)

# Continue conversation
messages = checkpoint.state_snapshot["messages"]
# ... continue chat from here
```

### Fork a Session

```python
from tracertm.agent import GraphSessionStore

store = GraphSessionStore(neo4j_client=neo4j)

# Create fork with lineage tracking
new_sandbox, created = await store.create_session_fork(
    new_session_id="session-456",
    parent_session_id="session-123",
    config=config,
    db_session=db
)

# Neo4j: (session-456)-[:FORKED_FROM]->(session-123)
```

### Track Tool Execution

```python
await store.track_tool_call(
    session_id="session-123",
    tool_name="code_search",
    input_data={"query": "auth implementation"},
    output_data={"matches": 5, "files": [...]},
    success=True,
    project_id="project-123"
)

# Results in:
# - Neo4j: TOOL_CALL relationship
# - NATS: chat.tool_use event
```

### Query Session Lineage

```python
# Get all parent sessions (fork chain)
lineage = await store.get_session_lineage("session-456")

# Returns:
# [
#   {session_id: "session-456", created_at: "...", provider: "claude"},
#   {session_id: "session-123", created_at: "...", provider: "claude"},
# ]
```

### Subscribe to Events

```python
from tracertm.agent.events import AgentEventPublisher

# Create event subscriber
async def handle_checkpoint(msg):
    data = json.loads(msg.data)
    print(f"Checkpoint created: turn {data['turn_number']}")

# Subscribe
await nats.subscribe(
    "tracertm.sessions.*.checkpoint",
    cb=handle_checkpoint
)
```

---

## 🗂️ File Locations

### Configuration
- `backend/configs/cliproxy.yaml` - CLIProxy OAuth config
- `.env` - All environment variables
- `docker-compose.yml` - Infrastructure services

### Go Backend (CLIProxy)
- `backend/internal/cliproxy/` - OAuth service implementation
- `backend/internal/infrastructure/infrastructure.go` - CLIProxy initialization

### Python Backend (Agent System)
- `src/tracertm/agent/` - Session management
- `src/tracertm/workflows/` - Temporal workflows
- `src/tracertm/services/checkpoint_service.py` - Checkpoint CRUD
- `src/tracertm/models/agent_checkpoint.py` - Database model

### Testing
- `tests/integration/` - Integration test suites (66 tests)
- `tests/workflows/` - Workflow tests

### Documentation
- `docs/guides/` - Implementation guides
- `docs/reference/` - Quick references (this file)
- `docs/reports/` - Completion reports
- `docs/testing/` - Testing guides

---

## 🐛 Troubleshooting

### CLIProxy not starting

```bash
# Check OAuth credentials
echo $CLAUDE_OAUTH_CLIENT_ID

# Verify config file
cat backend/configs/cliproxy.yaml

# Check logs
# Look for: "CLIProxy configuration invalid"
```

### Session not persisting

```bash
# Check PostgreSQL
psql $DATABASE_URL -c "SELECT * FROM agent_sessions;"

# Check Neo4j
echo "MATCH (s:Session) RETURN s LIMIT 5;" | cypher-shell

# Check Redis cache
redis-cli GET "tracertm:agent:session:{session_id}"
```

### Checkpoint creation failing

```bash
# Check database table exists
psql $DATABASE_URL -c "\d agent_checkpoints"

# Check Temporal worker running
# Look for: "Worker started successfully"

# Check S3 connectivity
mc ls local/tracertm/sandboxes/
```

### Events not publishing

```bash
# Check NATS connection
nats account info

# Check stream exists
nats stream info TRACERTM_BRIDGE

# Monitor events
nats sub "tracertm.>" --count 10
```

### Snapshot upload failing

```bash
# Check MinIO connection
mc ls local/tracertm

# Check bucket exists
mc ls local/tracertm/sandboxes

# Test manual upload
mc cp test.txt local/tracertm/test/
```

---

## 📊 Monitoring

### Health Checks

```bash
# All services
curl http://localhost:8080/health  # Go
curl http://localhost:4000/health  # Python
curl http://localhost:8765/health  # CLIProxy

# Infrastructure
docker-compose ps
```

### Temporal Monitoring

```bash
# Web UI
open http://localhost:8233

# List workflows
tctl workflow list

# Describe workflow
tctl workflow describe -w {workflow_id}
```

### NATS Monitoring

```bash
# Stream statistics
nats stream info TRACERTM_BRIDGE

# Consumer info
nats consumer info TRACERTM_BRIDGE {consumer_name}

# View events
nats sub "tracertm.>"
```

### MinIO Monitoring

```bash
# Web console
open http://localhost:9001

# CLI
mc ls local/tracertm/sandboxes/
mc du local/tracertm/sandboxes/
```

### Database Monitoring

```sql
-- PostgreSQL: Session count
SELECT COUNT(*) FROM agent_sessions;

-- PostgreSQL: Checkpoint count
SELECT session_id, COUNT(*)
FROM agent_checkpoints
GROUP BY session_id;

-- Neo4j: Session graph
MATCH (s:Session)-[r]->()
RETURN type(r), count(*)
```

---

## 🔗 API Reference

### CLIProxy Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/oauth/authorize` | Start OAuth flow |
| GET | `/oauth/callback` | Handle OAuth callback |
| POST | `/oauth/token` | Exchange code for token |
| POST | `/oauth/refresh` | Refresh expired token |
| POST | `/v1/messages` | Anthropic-compatible chat |
| POST | `/v1/chat/completions` | OpenAI-compatible chat |
| GET | `/health` | Health check |

### Python API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/chat/stream` | Stream chat with SSE |
| POST | `/api/v1/chat/resume` | Resume session |
| GET | `/api/v1/sessions/{id}` | Get session info |
| DELETE | `/api/v1/sessions/{id}` | Delete session |

### Temporal Workflows

| Workflow | Purpose | Triggers |
|----------|---------|----------|
| `AgentExecutionWorkflow` | Durable chat execution | Manual start |
| `AgentExecutionResumeWorkflow` | Resume from checkpoint | Session resume |
| `SandboxSnapshotWorkflow` | Create snapshot | Manual or scheduled |
| `BulkSnapshotWorkflow` | Batch snapshots | Admin operations |
| `SnapshotCleanupWorkflow` | Cleanup old snapshots | Scheduled (daily) |

---

## 📖 Further Reading

**Deep Dives:**
- [CLIProxy Implementation](../backend/internal/cliproxy/README.md)
- [Temporal Workflows Guide](../guides/PHASE_3_TEMPORAL_WORKFLOWS_GUIDE.md)
- [NATS Event Streaming](../guides/PHASE_5_NATS_EVENT_STREAMING.md)
- [E2E Testing Guide](../testing/E2E_TESTING_GUIDE.md)

**References:**
- [Agent Events Catalog](./AGENT_EVENTS_QUICK_REFERENCE.md)
- [Snapshot Service API](./SNAPSHOT_SERVICE_QUICK_REFERENCE.md)
- [Workflow Quick Reference](./PHASE_3_QUICK_REFERENCE.md)

**Reports:**
- [Final Implementation Report](../reports/AGENT_SYSTEM_COMPLETE_FINAL_REPORT.md)
- [Phase 6 Testing Results](../reports/PHASE_6_E2E_TESTING_COMPLETE.md)

---

**Need Help?**
- Check [Troubleshooting](#-troubleshooting) section above
- Review [E2E Testing Guide](../testing/E2E_TESTING_GUIDE.md)
- See [Complete Final Report](../reports/AGENT_SYSTEM_COMPLETE_FINAL_REPORT.md)

**Status:** ✅ Production Ready
