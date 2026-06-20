# Phase 2: Database Integration - COMPLETE ✅

**Date:** 2026-01-31
**Status:** Completed
**Duration:** ~30 minutes

---

## Summary

Successfully implemented database integration layer for the agent system, providing:
1. **PostgreSQL** - Agent session persistence and checkpoint storage
2. **Neo4j** - Session graph relationships and lineage tracking
3. **Dual-write strategy** - Session data written to both databases

## Implementation Details

### Files Created

1. **`src/tracertm/models/agent_checkpoint.py`** (76 lines)
   - SQLAlchemy model for conversation state checkpoints
   - JSONB for state snapshots
   - S3 snapshot reference tracking
   - Composite unique index on (session_id, turn_number)
   - Checkpoint metadata storage

2. **`src/tracertm/agent/graph_session_store.py`** (318 lines)
   - Neo4j-backed session store extending `SessionSandboxStoreDB`
   - Session node creation with metadata
   - Project relationship linking
   - Session fork tracking (FORKED_FROM relationships)
   - Tool call tracking in graph
   - Session lineage queries
   - Related sessions discovery
   - Cascading delete from both databases

### Existing Infrastructure Leveraged

**PostgreSQL:**
- ✅ `agent_sessions` table (already existed)
- ✅ `SessionSandboxStoreDB` (already existed)
- ✅ Redis caching (already integrated)

**Neo4j:**
- ✅ Neo4j client (already initialized)
- ✅ Driver connection pool (already configured)

## Features Implemented

### PostgreSQL Features

#### AgentCheckpoint Model
```python
class AgentCheckpoint(Base, TimestampMixin):
    - id (UUID, PK)
    - session_id (FK to agent_sessions)
    - turn_number (Integer, indexed)
    - state_snapshot (JSONB) # Conversation state
    - sandbox_snapshot_s3_key (String) # MinIO reference
    - checkpoint_metadata (JSONB) # Model, tokens, duration
    - description (Text)
```

**Indexes:**
- `ix_agent_checkpoints_session_id` - Fast session lookups
- `ix_agent_checkpoints_turn_number` - Temporal ordering
- `ix_agent_checkpoints_session_turn` - Unique constraint

### Neo4j Features

#### Session Graph Schema
```cypher
// Session Node
(s:Session {
  session_id: string,
  sandbox_root: string,
  provider: string,  # "claude", "codex", "openai"
  model: string,
  status: string,    # "ACTIVE", "COMPLETED", "FAILED"
  created_at: datetime,
  updated_at: datetime
})

// Relationships
(Session)-[:BELONGS_TO]->(Project)
(Session)-[:FORKED_FROM {created_at}]->(Session)
(Session)-[:TOOL_CALL {tool_name, success, timestamp}]->(Session)
```

#### Graph Operations
- ✅ **Session Creation** - Create node + project link
- ✅ **Session Fork** - Track parent-child lineage
- ✅ **Tool Tracking** - Record all tool executions
- ✅ **Lineage Query** - Get ancestor chain
- ✅ **Related Sessions** - Find connected sessions
- ✅ **Status Updates** - Track session lifecycle
- ✅ **Cascading Delete** - Remove from both DBs

### Integration Architecture

```
┌────────────────────────────┐
│ AgentService               │
│  stream_chat_with_sandbox()│
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ GraphSessionStore          │
│  (extends SessionSandboxDB)│
└──────┬─────────────────────┘
       │
       ├─→ PostgreSQL (agent_sessions, agent_checkpoints)
       ├─→ Neo4j (Session graph, relationships)
       └─→ Redis (session cache, TTL=1h)
```

## Database Schemas

### PostgreSQL Schema

```sql
-- Existing: agent_sessions table
CREATE TABLE agent_sessions (
  id UUID PRIMARY KEY,
  session_id VARCHAR(255) UNIQUE NOT NULL,
  sandbox_root VARCHAR(1024) NOT NULL,
  project_id UUID REFERENCES projects(id),
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

-- New: agent_checkpoints table
CREATE TABLE agent_checkpoints (
  id UUID PRIMARY KEY,
  session_id VARCHAR(255) REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
  turn_number INTEGER NOT NULL,
  state_snapshot JSONB NOT NULL,
  sandbox_snapshot_s3_key VARCHAR(1024),
  checkpoint_metadata JSONB,
  description TEXT,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,

  UNIQUE(session_id, turn_number)
);

CREATE INDEX ix_agent_checkpoints_session_id ON agent_checkpoints(session_id);
CREATE INDEX ix_agent_checkpoints_turn_number ON agent_checkpoints(turn_number);
```

### Neo4j Schema

```cypher
// Constraints
CREATE CONSTRAINT session_id_unique IF NOT EXISTS
FOR (s:Session) REQUIRE s.session_id IS UNIQUE;

CREATE CONSTRAINT project_id_unique IF NOT EXISTS
FOR (p:Project) REQUIRE p.id IS UNIQUE;

// Indexes
CREATE INDEX session_created IF NOT EXISTS
FOR (s:Session) ON (s.created_at);

CREATE INDEX session_status IF NOT EXISTS
FOR (s:Session) ON (s.status);
```

## Usage Examples

### Creating a Session with Graph Tracking

```python
from tracertm.agent.graph_session_store import GraphSessionStore
from tracertm.agent.types import SandboxConfig

# Initialize with Neo4j client
store = GraphSessionStore(
    sandbox_provider=None,  # Uses default LocalFS
    cache_service=cache_service,
    neo4j_client=neo4j_client
)

# Create session (writes to PostgreSQL + Neo4j)
config = SandboxConfig(
    project_id=uuid.UUID("..."),
    provider="claude",
    model="claude-sonnet-4"
)

sandbox_root, created = await store.get_or_create(
    session_id="session_123",
    config=config,
    db_session=db
)

# PostgreSQL: Row in agent_sessions
# Neo4j: (Session)-[:BELONGS_TO]->(Project)
```

### Forking a Session

```python
# Create fork (new session inherits context from parent)
new_sandbox, created = await store.create_session_fork(
    new_session_id="session_456",
    parent_session_id="session_123",
    config=config,
    db_session=db
)

# Neo4j: (session_456)-[:FORKED_FROM]->(session_123)
```

### Tracking Tool Calls

```python
await store.track_tool_call(
    session_id="session_123",
    tool_name="code_search",
    input_data={"query": "find auth code"},
    output_data={"matches": 5},
    success=True
)

# Neo4j: (Session)-[:TOOL_CALL {tool_name, success, timestamp}]->(Session)
```

### Querying Session Lineage

```python
# Get all parent sessions
lineage = await store.get_session_lineage("session_456")
# Returns: [{session_id, created_at, provider, model}, ...]
```

### Finding Related Sessions

```python
# Get sessions with any relationship
related = await store.get_related_sessions("session_123")

# Get sessions with specific relationship type
forked = await store.get_related_sessions("session_123", "FORKED_FROM")
```

## Data Flow

### Session Creation Flow
```
1. AgentService.stream_chat_with_sandbox()
2. GraphSessionStore.get_or_create()
3. ├─ SessionSandboxStoreDB.get_or_create() (PostgreSQL)
   ├─ Redis cache check/set
   ├─ agent_sessions INSERT
   └─ GraphSessionStore._create_session_node() (Neo4j)
       ├─ CREATE (s:Session {...})
       └─ CREATE (s)-[:BELONGS_TO]->(p:Project)
```

### Checkpoint Creation Flow (Future - Phase 3)
```
1. Temporal CheckpointActivity
2. Create state snapshot (conversation history)
3. Create sandbox snapshot (MinIO)
4. INSERT INTO agent_checkpoints
   - session_id
   - turn_number
   - state_snapshot (JSONB)
   - sandbox_snapshot_s3_key
```

## Benefits Achieved

1. **Persistence** - Sessions survive backend restarts
2. **Lineage Tracking** - Understand session relationships
3. **Audit Trail** - Tool call history in graph
4. **Query Flexibility** - Graph queries for complex relationships
5. **Performance** - Redis cache reduces DB load
6. **Scalability** - JSONB for flexible checkpoint data

## Integration Points

### With Existing Systems

**AgentService** (src/tracertm/agent/agent_service.py):
- Already uses `SessionSandboxStore`
- Can be upgraded to `GraphSessionStore` with zero code changes
- Just swap dependency injection

**NATS Events** (already integrated):
- Publishes `agent.session.created` events
- Can add `agent.session.forked`, `agent.tool.executed` events

**Temporal** (Phase 3):
- Will use checkpoints for resumability
- Checkpoint activities will write to agent_checkpoints table

**MinIO** (Phase 4):
- Checkpoint references S3 keys
- Sandbox snapshots stored in MinIO
- Format: `sandboxes/{session_id}/snapshots/snapshot-{turn}.tar.gz`

## Next Steps (Phase 3)

Now that we have the database layer, Phase 3 will implement:

1. **Temporal Workflows**
   - `AgentExecutionWorkflow` - Durable chat execution
   - `SandboxSnapshotWorkflow` - Scheduled snapshots
   - Checkpoint activities

2. **Checkpoint Service**
   - Create checkpoints every N turns
   - Store conversation state to agent_checkpoints
   - Trigger sandbox snapshots to MinIO

3. **Session Resume**
   - Load latest checkpoint from DB
   - Restore sandbox from MinIO snapshot
   - Continue conversation from checkpoint state

## Verification

### PostgreSQL Verification
```python
# Check session exists
from tracertm.models.agent_session import AgentSession
session = await db.execute(
    select(AgentSession).where(AgentSession.session_id == "session_123")
)
assert session.scalar_one_or_none() is not None

# Check checkpoint exists
from tracertm.models.agent_checkpoint import AgentCheckpoint
checkpoint = await db.execute(
    select(AgentCheckpoint)
    .where(AgentCheckpoint.session_id == "session_123")
    .order_by(AgentCheckpoint.turn_number.desc())
)
latest = checkpoint.scalar_one_or_none()
assert latest is not None
assert latest.state_snapshot is not None
```

### Neo4j Verification
```cypher
// Check session node exists
MATCH (s:Session {session_id: "session_123"})
RETURN s

// Check project relationship
MATCH (s:Session {session_id: "session_123"})-[:BELONGS_TO]->(p:Project)
RETURN s, p

// Check fork relationship
MATCH (child:Session)-[:FORKED_FROM]->(parent:Session)
WHERE child.session_id = "session_456"
RETURN child, parent

// Check tool calls
MATCH (s:Session {session_id: "session_123"})-[t:TOOL_CALL]->(s)
RETURN t.tool_name, t.success, t.timestamp
ORDER BY t.timestamp DESC
```

## Known Limitations

1. **No Migration Script** - agent_checkpoints table needs Alembic migration (not created yet)
2. **No Resume Implementation** - Checkpoint loading logic not implemented (Phase 3)
3. **No Snapshot Integration** - MinIO snapshot service not implemented (Phase 4)
4. **Deprecated datetime.utcnow()** - Should use timezone-aware datetime (minor issue)

## Conclusion

Phase 2 successfully established the database foundation for the agent system with:
- ✅ PostgreSQL persistence (sessions + checkpoints)
- ✅ Neo4j graph relationships (lineage, tools, projects)
- ✅ Dual-write session store
- ✅ Comprehensive graph query capabilities
- ✅ Ready for Temporal integration (Phase 3)

**Ready for Phase 3: Temporal Workflows! 🚀**
