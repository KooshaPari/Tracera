# Enhanced Architecture Research - TraceRTM Full Stack

**Date**: 2025-11-22
**Research Scope**: Deep dive into backend optimization, frontend architecture, offline-first sync, real-time coordination, and 100% test coverage strategies

---

## 1. BACKEND OPTIMIZATION (FastAPI + PostgreSQL)

### 1.1 Real-Time Architecture
**Current State**: FastAPI with async support ✓
**Enhancement**: WebSocket + Event Sourcing

**Implementation Pattern**:
```python
# FastAPI WebSocket with connection pooling
@app.websocket("/ws/project/{project_id}")
async def websocket_endpoint(ws: WebSocket, project_id: str):
    await ws.accept()
    # Subscribe to project events via NATS
    # Broadcast changes to all connected clients
```

**Key Findings**:
- Use **Socket.io** for fallback (HTTP polling) + WebSocket
- Implement **connection pooling** for 1000+ concurrent agents
- Use **NATS** for pub/sub (scales better than Redis for this use case)
- Heartbeat every 30s to detect stale connections

### 1.2 Event Sourcing + CQRS
**Pattern**: All state changes → Event Log → Materialized Views

**Benefits**:
- Complete audit trail (compliance requirement)
- Time-travel queries (point-in-time state)
- Conflict resolution for concurrent agents
- Replay capability for debugging

**Implementation**:
```sql
-- Event log table (immutable)
CREATE TABLE events (
    id UUID PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100),
    event_data JSONB,
    version INT,
    created_at TIMESTAMP,
    agent_id UUID
);

-- Materialized views refresh incrementally
CREATE MATERIALIZED VIEW item_state AS
SELECT aggregate_id, (event_data->>'state')::JSON as state
FROM events
WHERE event_type = 'ItemUpdated'
ORDER BY version DESC;
```

### 1.3 Optimistic Locking (Already Implemented ✓)
**Current**: Version column on Item model
**Enhancement**: Add conflict detection + resolution strategy

**Conflict Resolution**:
- **Last-Write-Wins**: Simple, suitable for non-critical fields
- **Merge Strategy**: For structured data (use JSON merge)
- **Manual Resolution**: For critical conflicts (notify user)

### 1.4 Connection Pooling Tuning
**SQLAlchemy Async Configuration**:
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,  # Base connections
    max_overflow=40,  # Additional connections under load
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections hourly
)
```

**Rationale**:
- `pool_size=20`: Handles 20 concurrent requests
- `max_overflow=40`: Burst capacity for 1000 agents
- `pool_pre_ping=True`: Prevents "connection lost" errors
- `pool_recycle=3600`: PostgreSQL default idle timeout

---

## 2. FRONTEND ARCHITECTURE (React 19 + Offline-First)

### 2.1 Offline-First State Management
**Recommended Stack**: Legend State + TanStack Query + IndexedDB

**Why Legend State over Zustand**:
- Built-in sync/offline support
- Automatic conflict resolution (CRDT-like)
- Minimal boilerplate
- Better performance (fine-grained reactivity)

**Architecture**:
```typescript
// Local-first state
const projectState = observable({
  items: [],
  links: [],
  agents: [],
  lastSync: null,
  syncQueue: [],
});

// Sync strategy
const syncManager = {
  // Queue mutations when offline
  queueMutation: (mutation) => projectState.syncQueue.push(mutation),

  // Flush queue when online
  flushQueue: async () => {
    for (const mutation of projectState.syncQueue) {
      await api.mutate(mutation);
    }
    projectState.syncQueue = [];
  },

  // Conflict resolution
  resolveConflict: (local, remote) => {
    // Merge strategy: remote wins for timestamps, local for user edits
    return { ...remote, ...local };
  }
};
```

### 2.2 Real-Time Sync with Conflict Resolution
**Pattern**: Operational Transformation (OT) for text, CRDT for structured data

**Implementation**:
- **Text Fields**: Use Yjs (CRDT library) for collaborative editing
- **Structured Data**: Event-based merge with version vectors
- **Conflict UI**: Show conflicts, let user choose resolution

### 2.3 TanStack Query v5 Optimizations
**Key Features**:
- Automatic background refetching
- Stale-while-revalidate pattern
- Optimistic updates with rollback
- Offline mutation queuing

```typescript
const mutation = useMutation({
  mutationFn: updateItem,
  onMutate: async (newData) => {
    // Optimistic update
    await queryClient.cancelQueries({ queryKey: ['items'] });
    const previous = queryClient.getQueryData(['items']);
    queryClient.setQueryData(['items'], old => [...old, newData]);
    return { previous };
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(['items'], context.previous);
  },
});
```

### 2.4 IndexedDB Schema Design
**Multi-Store Approach**:
```javascript
const dbSchema = {
  items: { keyPath: 'id', indexes: ['projectId', 'view', 'status'] },
  links: { keyPath: 'id', indexes: ['sourceId', 'targetId'] },
  events: { keyPath: 'id', indexes: ['timestamp', 'agentId'] },
  syncQueue: { keyPath: 'id', indexes: ['status', 'createdAt'] },
};
```

**Sync Strategy**:
- Store all mutations in `syncQueue` when offline
- Batch sync (max 50 mutations per request)
- Exponential backoff on sync failures
- Conflict detection via version vectors

---

## 3. MONOREPO STRUCTURE & TYPE SAFETY

### 3.1 Monorepo Layout
```
tracertm/
├── backend/
│   ├── src/tracertm/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── web/          (React web + PWA)
│   ├── desktop/      (Electron wrapper)
│   ├── mobile/       (React Native)
│   └── package.json
├── shared/
│   ├── types/        (Generated from OpenAPI)
│   └── api-client/   (Auto-generated SDK)
└── docs/
```

### 3.2 OpenAPI Code Generation
**Tool**: `openapi-typescript` + `openapi-fetch`

**Workflow**:
1. FastAPI generates OpenAPI spec
2. TypeScript generates types from spec
3. Frontend imports types automatically
4. Type safety across API boundary

```bash
# Generate types
npx openapi-typescript http://localhost:8000/openapi.json -o shared/types/api.ts

# Generate client
npx openapi-fetch --input shared/types/api.ts --output shared/api-client/index.ts
```

---

## 4. TESTING STRATEGY FOR 100% COVERAGE

### 4.1 Testing Pyramid (Inverted for Frontend)
**Recommended Distribution**:
- **Unit Tests**: 30% (Vitest)
- **Integration Tests**: 40% (Playwright)
- **E2E Tests**: 30% (Playwright)

**Why Inverted**: UI testing is cheap with Playwright, unit tests are expensive

### 4.2 Vitest Configuration
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 100,
      functions: 100,
      branches: 100,
      statements: 100,
    },
  },
});
```

### 4.3 Playwright Component Testing
```typescript
// Component test
test('Item card renders with correct data', async ({ mount }) => {
  const component = await mount(ItemCard, {
    props: { item: mockItem },
  });

  await expect(component.locator('h2')).toContainText(mockItem.title);
  await expect(component.locator('[data-testid="status"]')).toHaveText('active');
});
```

### 4.4 E2E Test Scenarios
**Critical Paths**:
1. Create project → Add items → Link items → Export
2. Go offline → Edit items → Sync → Verify no conflicts
3. Real-time: Agent A updates item → Agent B sees update instantly
4. Performance: Load 10K items → Query < 500ms

---

## 5. ELECTRON ARCHITECTURE

### 5.1 IPC Security Pattern
**Preload Script** (Secure Bridge):
```javascript
// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  invoke: (channel, ...args) => {
    const validChannels = ['get-project', 'update-item'];
    if (validChannels.includes(channel)) {
      return ipcRenderer.invoke(channel, ...args);
    }
  },
});
```

**Main Process** (Trusted):
```javascript
ipcMain.handle('get-project', async (event, projectId) => {
  // Validate projectId
  // Query database
  return project;
});
```

### 5.2 Auto-Update Strategy
- Use `electron-updater`
- Delta updates (only changed files)
- Staged rollout (10% → 50% → 100%)

---

## 6. REACT NATIVE + EXPO OFFLINE-FIRST

### 6.1 Recommended Stack
- **State**: Legend State (same as web)
- **Storage**: WatermelonDB (SQLite wrapper)
- **Sync**: Same sync manager as web

### 6.2 Platform-Specific Considerations
- **iOS**: Use `NSURLSession` for background sync
- **Android**: Use `WorkManager` for background sync
- **Both**: Implement push notifications for agent activity

---

## 7. PERFORMANCE TARGETS & MONITORING

### 7.1 Performance Benchmarks
| Operation | Target | Current |
|-----------|--------|---------|
| List 10K items | < 500ms | ? |
| Create item | < 100ms | ? |
| Sync 100 mutations | < 2s | ? |
| WebSocket latency | < 100ms | ? |
| Offline query | < 50ms | ? |

### 7.2 Monitoring Stack
- **Backend**: OpenTelemetry + Prometheus
- **Frontend**: Web Vitals + Custom metrics
- **Database**: PostgreSQL slow query log

---

## 8. SECURITY CONSIDERATIONS

### 8.1 API Security
- JWT tokens with 15min expiry + refresh tokens
- CORS: Restrict to known origins
- Rate limiting: 100 req/min per agent
- Input validation: Pydantic on backend

### 8.2 Data Security
- Encrypt sensitive fields (passwords, API keys)
- Audit log all mutations
- Soft deletes (never hard delete)

---

## 9. DEPLOYMENT ARCHITECTURE

### 9.1 Backend Deployment
- **Container**: Docker + Kubernetes
- **Database**: PostgreSQL managed service
- **Cache**: Redis for session management
- **Message Queue**: NATS for pub/sub

### 9.2 Frontend Deployment
- **Web**: Vercel or Netlify (auto-deploy on push)
- **PWA**: Service worker caching strategy
- **Desktop**: GitHub Releases + auto-update
- **Mobile**: App Store + Play Store

---

## 10. NEXT STEPS

1. **Implement Event Sourcing** in backend
2. **Add WebSocket** support with NATS
3. **Build Offline-First** frontend with Legend State
4. **Set up OpenAPI** code generation
5. **Create E2E tests** with Playwright
6. **Deploy** to staging environment
7. **Load test** with 1000 concurrent agents


