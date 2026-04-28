# ADR-0008: Real-Time Collaboration Architecture

**Status:** Accepted
**Date:** 2026-02-03
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM supports multi-user collaboration on requirements, test cases, and traceability links. The system needs:

1. **Real-time updates:** Users see changes from others instantly (no manual refresh)
2. **Presence tracking:** "User X is editing Requirement Y"
3. **Conflict resolution:** Handle concurrent edits to same entity
4. **WebSocket connections:** Bidirectional communication (server → client)
5. **Scalability:** Support 100+ concurrent users per project

Collaboration scenarios:
- **Live editing:** Multiple users editing different requirements simultaneously
- **Link creation:** User A creates link while User B views traceability graph
- **Test execution:** Test results update in real-time for all viewers
- **Notifications:** "Requirement REQ-001 updated by Alice"

Technology constraints:
- **Frontend:** React 19, TanStack Query (for data fetching)
- **Backend:** FastAPI (WebSocket support), Go (message broker)
- **Database:** PostgreSQL (single source of truth)

## Decision

We will use **NATS** (messaging) + **WebSocket** (client connection) for real-time collaboration.

**Architecture:**
1. **Client ↔ Server:** WebSocket (bidirectional)
2. **Server ↔ Server:** NATS pub/sub (multi-instance scaling)
3. **Conflict resolution:** Operational Transformation (OT) OR Last-Write-Wins (LWW)

## Rationale

### Technology Stack

**From pyproject.toml:**
```toml
dependencies = [
    "fastapi>=0.115.0",        # WebSocket support
    "sse-starlette>=3.0.0",    # Server-Sent Events (SSE)
    "nats-py>=2.12.0",         # NATS messaging
    "nkeys>=0.2.1",            # NATS authentication
]
```

**From backend/go.mod:**
```go
require (
    github.com/nats-io/nats.go v1.48.0  // NATS client
    github.com/nats-io/nkeys v0.4.15    // NATS auth
)
```

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                   Client (React)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WebSocket Client                                    │  │
│  │  ├─ Presence tracker (user status)                   │  │
│  │  ├─ Event listener (requirement.updated)             │  │
│  │  └─ Conflict resolver (merge changes)                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                         │
                         │ WebSocket
                         ▼
┌────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WebSocket Handler                                   │  │
│  │  ├─ /ws/projects/{project_id}                        │  │
│  │  ├─ Authenticate connection (JWT)                    │  │
│  │  ├─ Subscribe to NATS topics                         │  │
│  │  └─ Broadcast updates to connected clients          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                         │
                         │ NATS pub/sub
                         ▼
┌────────────────────────────────────────────────────────────┐
│                  NATS Message Broker                        │
│  Topics:                                                    │
│    ├─ project.<id>.requirement.updated                    │
│    ├─ project.<id>.link.created                           │
│    ├─ project.<id>.presence.user_joined                   │
│    └─ project.<id>.test.result                            │
└────────────────────────────────────────────────────────────┘
                         │
                         │ Subscribe
                         ▼
┌────────────────────────────────────────────────────────────┐
│              Go Performance Layer (optional)                │
│  ├─ NATS subscriber (high-throughput events)              │
│  └─ WebSocket server (alternative to Python)              │
└────────────────────────────────────────────────────────────┘
```

### WebSocket Handler (FastAPI)

```python
from fastapi import WebSocket, WebSocketDisconnect
from nats.aio.client import Client as NATS

@app.websocket("/ws/projects/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await websocket.accept()

    # Authenticate
    token = websocket.query_params.get("token")
    user = verify_jwt(token)

    # Connect to NATS
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    # Subscribe to project events
    async def message_handler(msg):
        event = json.loads(msg.data.decode())
        await websocket.send_json(event)

    await nc.subscribe(f"project.{project_id}.*", cb=message_handler)

    # Send presence
    await nc.publish(f"project.{project_id}.presence.user_joined", json.dumps({
        "user_id": user.id,
        "user_name": user.name,
        "timestamp": datetime.utcnow().isoformat(),
    }).encode())

    try:
        while True:
            # Receive client messages (e.g., typing indicator)
            data = await websocket.receive_json()
            # Broadcast to NATS
            await nc.publish(f"project.{project_id}.{data['type']}", json.dumps(data).encode())
    except WebSocketDisconnect:
        await nc.publish(f"project.{project_id}.presence.user_left", json.dumps({
            "user_id": user.id,
        }).encode())
        await nc.close()
```

### Client (React Hooks)

```typescript
function useProjectWebSocket(projectId: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    const token = getAuthToken();
    const socket = new WebSocket(`wss://api.tracertm.com/ws/projects/${projectId}?token=${token}`);

    socket.onmessage = (msg) => {
      const event = JSON.parse(msg.data);
      setEvents((prev) => [...prev, event]);

      // Handle different event types
      if (event.type === 'requirement.updated') {
        queryClient.invalidateQueries(['requirements', event.data.id]);
      }
    };

    socket.onclose = () => {
      // Reconnect logic
      setTimeout(() => setWs(new WebSocket(...)), 1000);
    };

    setWs(socket);

    return () => socket.close();
  }, [projectId]);

  return { ws, events };
}
```

### Conflict Resolution Strategy

**Option A: Last-Write-Wins (LWW)**
```python
# Simple: latest timestamp wins
async def update_requirement(req_id: str, data: dict, version: int):
    current = await db.get(req_id)
    if data['version'] < current.version:
        raise ConflictError("Stale version")

    await db.update(req_id, data)
    await nats.publish(f"requirement.{req_id}.updated", data)
```

**Option B: Operational Transformation (OT)**
```python
# Complex: merge concurrent edits
def transform_edit(local_op, remote_op):
    # Transform operations to apply both changes
    if local_op.overlaps(remote_op):
        return merge_operations(local_op, remote_op)
    return local_op
```

**Decision: Last-Write-Wins for MVP, Operational Transformation for future**

## Alternatives Rejected

### Alternative 1: Polling (No WebSocket)

- **Description:** Clients poll `/api/changes?since=timestamp` every 5s
- **Pros:** Simple implementation, no persistent connections
- **Cons:** High latency (5s delay), increased server load (N clients × 1 req/5s)
- **Why Rejected:** Real-time collaboration requires <1s latency. Polling is too slow.

### Alternative 2: Server-Sent Events (SSE)

- **Description:** Server pushes updates via HTTP streaming
- **Pros:** Built-in HTTP, easier than WebSocket, auto-reconnect
- **Cons:** Unidirectional (server → client), client must use HTTP POST for commands
- **Why Rejected:** WebSocket is bidirectional (client can send presence, typing indicators). SSE insufficient for full collaboration.

### Alternative 3: Firebase Realtime Database

- **Description:** Use Firebase for real-time sync
- **Pros:** Managed service, offline support, simple SDK
- **Cons:** Vendor lock-in, expensive at scale, data duplication (Firebase + PostgreSQL)
- **Why Rejected:** TraceRTM uses PostgreSQL as source of truth. Firebase adds operational complexity without sufficient benefit.

### Alternative 4: Redis Pub/Sub

- **Description:** Use Redis instead of NATS for pub/sub
- **Pros:** Already using Redis (cache), simple pub/sub API
- **Cons:** No persistence (messages lost if subscriber offline), single-threaded
- **Why Rejected:** NATS provides message persistence (JetStream), clustering, and better performance for high-throughput messaging.

## Consequences

### Positive

- **Real-time updates:** <100ms latency from edit → broadcast
- **Scalability:** NATS handles 10M+ messages/sec, WebSocket scales horizontally
- **Presence tracking:** Know who's viewing/editing what
- **Conflict detection:** Warn users about concurrent edits
- **Offline support (future):** NATS JetStream can queue messages for offline clients

### Negative

- **Connection management:** WebSocket connections are stateful (requires sticky sessions or connection migration)
- **Infrastructure:** Requires NATS server (added operational complexity)
- **Reconnection logic:** Clients must handle WebSocket disconnects gracefully
- **Memory usage:** Each WebSocket connection uses ~10KB RAM (100 users = 1MB)

### Neutral

- **Authentication:** WebSocket uses same JWT as REST API
- **Rate limiting:** Per-connection rate limits (e.g., 10 messages/second)
- **Monitoring:** Track WebSocket connection count, message throughput

## Implementation

### Affected Components

- `src/tracertm/api/handlers/websocket.py` - WebSocket handlers
- `src/tracertm/infrastructure/nats_client.py` - NATS pub/sub client
- `frontend/packages/realtime/` - WebSocket hooks, event listeners
- `frontend/apps/web/src/hooks/useProjectWebSocket.ts` - React WebSocket hook
- `deploy/nats.yml` - NATS deployment config

### Migration Strategy

**Phase 1: WebSocket Infrastructure (Week 1)**
- Deploy NATS server (Fly.io or self-hosted)
- Implement WebSocket handler (FastAPI)
- Add authentication, reconnection logic

**Phase 2: Event Types (Week 2)**
- `requirement.updated`, `link.created`, `test.result`
- Presence tracking (`user_joined`, `user_left`, `typing`)
- Notification system

**Phase 3: Conflict Resolution (Week 3)**
- Version-based conflict detection
- Last-Write-Wins implementation
- Conflict UI (show warning, allow merge)

**Phase 4: Optimization (Week 4)**
- Connection pooling
- Message compression (zlib, brotli)
- Reconnection backoff

### Rollout Plan

- **Phase 1:** Read-only events (requirement updates broadcast, no editing)
- **Phase 2:** Full collaboration (edit, create, delete)
- **Phase 3:** Advanced features (presence, conflict resolution)

### Success Criteria

- [ ] 100+ concurrent WebSocket connections per server
- [ ] <100ms latency (edit → broadcast)
- [ ] Automatic reconnection on disconnect
- [ ] Presence tracking (who's online)
- [ ] Conflict detection (concurrent edits)
- [ ] Zero message loss (NATS JetStream)

## References

- [NATS Documentation](https://docs.nats.io/)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [React WebSocket Hook](https://www.npmjs.com/package/use-websocket)
- [ADR-0007: Database Architecture](ADR-0007-database-architecture.md)
- [ADR-0011: Frontend Framework](ADR-0011-frontend-framework-architecture.md)

---

**Notes:**
- **NATS vs Kafka:** NATS simpler for real-time use cases, Kafka better for event sourcing/analytics
- **WebSocket vs SSE:** WebSocket bidirectional, SSE unidirectional (server → client)
- **Conflict resolution:** LWW for MVP, OT/CRDT for collaborative editing in v2
- **Deployment:** NATS runs as sidecar on Fly.io (nats://localhost:4222)
