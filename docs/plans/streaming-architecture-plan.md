# TraceRTM Streaming Architecture Plan

**Document Type:** Implementation Roadmap
**Status:** Planning
**Target Completion:** Q2 2026
**Last Updated:** 2026-02-01

---

## Executive Summary

This document outlines the comprehensive streaming architecture strategy for TraceRTM, focusing on handling large datasets efficiently while maintaining real-time capabilities.

**Current State:**
- ✅ WebSocket implemented for real-time collaboration
- ✅ Virtual scrolling in 2 views (@tanstack/react-virtual)
- ❌ No SSE for one-way notifications
- ❌ Offset-based pagination only (no cursor-based)
- ❌ No NDJSON streaming for exports

**Goals:**
1. Add SSE endpoints for all one-way real-time updates
2. Implement cursor-based pagination across all list endpoints
3. Add NDJSON streaming for large exports
4. Extend virtual scrolling to all large list views
5. Achieve <50ms latency for real-time updates
6. Support 10,000+ items without performance degradation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        TraceRTM Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │   SSE Hook   │  │  WebSocket   │  │  Virtual Scroller   │  │
│  │              │  │   Manager    │  │  (@tanstack/react-  │  │
│  │ Notifications│  │              │  │       virtual)      │  │
│  │   Metrics    │  │ Collaboration│  │                     │  │
│  │   Progress   │  │    Chat      │  │  Infinite Scroll    │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬───────────┘  │
│         │                 │                     │              │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          │ EventSource     │ WebSocket           │ fetch()
          │                 │                     │
┌─────────┼─────────────────┼─────────────────────┼──────────────┐
│         │                 │                     │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌─────────▼───────────┐  │
│  │   SSE        │  │  WebSocket   │  │  REST API           │  │
│  │  Endpoints   │  │   Handler    │  │                     │  │
│  │              │  │              │  │  Cursor Pagination  │  │
│  │ /events/     │  │  /ws         │  │  NDJSON Export      │  │
│  │  stream      │  │              │  │                     │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬───────────┘  │
│         │                 │                     │              │
│         │        ┌────────▼─────────┐          │              │
│         │        │   NATS PubSub    │          │              │
│         │        │                  │          │              │
│         │        │  project.*       │          │              │
│         └────────►  notification.*  │          │              │
│                  │  metrics.*       │          │              │
│                  └──────────────────┘          │              │
│                                                │              │
│                  ┌──────────────────┐          │              │
│                  │   PostgreSQL     │◄─────────┘              │
│                  │                  │                         │
│                  │  Cursor Indexes  │                         │
│                  │  LISTEN/NOTIFY   │                         │
│                  └──────────────────┘                         │
│                                                                │
│                     Go Backend (Echo)                         │
└────────────────────────────────────────────────────────────────┘
```

---

## Feature-by-Feature Recommendations

### 1. Live Notifications

**Technology:** Server-Sent Events (SSE)

**Why:**
- One-way communication (server → client)
- Automatic reconnection
- Simple to implement
- Low overhead

**Implementation:**

**Backend:**
```
Endpoint: GET /api/v1/projects/:projectId/events/stream
Headers: text/event-stream
Events: notification, mention, assignment
```

**Frontend:**
```typescript
// Live toast notifications
useSSE(`/api/v1/projects/${projectId}/events/stream`, {
    onMessage: (event) => {
        if (event.type === 'notification') {
            toast(event.data.title, { description: event.data.message });
        }
    }
});
```

**Priority:** 🔴 High - User-facing feature
**Effort:** 🟢 Low (2-3 days)
**Impact:** 🔵 High - Improves UX significantly

---

### 2. Dashboard Metrics

**Technology:** Server-Sent Events (SSE)

**Why:**
- Live metric updates without polling
- Lower server load than WebSocket
- Simple implementation

**Implementation:**

**Backend:**
```
Endpoint: GET /api/v1/projects/:projectId/metrics/stream
Events: cpu_usage, memory_usage, active_users, test_status
Update Frequency: Every 5 seconds
```

**Frontend:**
```typescript
// Live dashboard charts
useTypedSSE<MetricUpdate>(
    `/api/v1/projects/${projectId}/metrics/stream`,
    'metric_update',
    (data) => {
        updateChart(data.metric_name, data.value);
    }
);
```

**Priority:** 🟡 Medium - Nice to have
**Effort:** 🟢 Low (2 days)
**Impact:** 🟡 Medium - Enhances dashboard

---

### 3. Test Run Progress

**Technology:** Server-Sent Events (SSE)

**Why:**
- Structured progress events
- Resume from last event ID
- Simple client implementation

**Implementation:**

**Backend:**
```
Endpoint: GET /api/v1/test-runs/:runId/progress/stream
Events: test_started, test_completed, test_failed, run_completed
```

**Frontend:**
```typescript
// Progress bar and live logs
useTypedSSE<TestProgress>(
    `/api/v1/test-runs/${runId}/progress/stream`,
    'test_progress',
    (data) => {
        setProgress(data.completed / data.total);
        appendLog(data.log_message);
    }
);
```

**Priority:** 🔴 High - Critical feature
**Effort:** 🟡 Medium (3-4 days)
**Impact:** 🔵 High - Core functionality

---

### 4. Real-time Collaboration

**Technology:** WebSocket (Already Implemented)

**Why:**
- Bidirectional communication needed
- Low latency required
- Complex state synchronization

**Current Status:** ✅ Already implemented

**Enhancements:**
- Add presence indicators (who's viewing)
- Add cursor tracking for multi-user editing
- Add optimistic UI updates with conflict resolution

**Priority:** 🟡 Medium - Enhancement
**Effort:** 🟡 Medium (4-5 days)
**Impact:** 🟡 Medium - Improves collaboration

---

### 5. Large Dataset Export

**Technology:** Streaming JSON (NDJSON)

**Why:**
- Memory efficient for large datasets
- Incremental parsing
- Resume support with Range headers

**Implementation:**

**Backend:**
```go
// Stream 100,000+ items as NDJSON
GET /api/v1/projects/:projectId/items/stream
Content-Type: application/x-ndjson
Transfer-Encoding: chunked
```

**Frontend:**
```typescript
// Progressive export with progress bar
async function exportItems(projectId: string) {
    const items = [];
    let count = 0;

    for await (const item of streamNDJSON(`/api/v1/projects/${projectId}/items/stream`)) {
        items.push(item);
        count++;
        setProgress((count / estimatedTotal) * 100);
    }

    downloadJSON(items);
}
```

**Priority:** 🟡 Medium - Power user feature
**Effort:** 🟢 Low (2-3 days)
**Impact:** 🟡 Medium - Enables large exports

---

### 6. Infinite Scroll Lists

**Technology:** Virtual Scrolling + Cursor Pagination

**Why:**
- Handles 10,000+ items smoothly
- Consistent results during data changes
- Better performance than offset pagination

**Implementation:**

**Backend:**
```go
// Cursor-based pagination for all list endpoints
GET /api/v1/projects/:projectId/items?cursor=base64&limit=50
Response:
{
    "items": [...],
    "next_cursor": "base64_encoded_cursor",
    "has_more": true
}
```

**Frontend:**
```typescript
// Virtual scrolling with infinite scroll
import { useVirtualizer } from '@tanstack/react-virtual';
import { useInfiniteQuery } from '@tanstack/react-query';

// Automatic pagination as user scrolls
```

**Views to Update:**
- ✅ Items List (Already has virtual scrolling, add cursor pagination)
- 🔧 Test Cases List
- 🔧 Requirements List
- 🔧 Test Runs List
- 🔧 Audit Logs

**Priority:** 🔴 High - Performance critical
**Effort:** 🟡 Medium (5-7 days for all views)
**Impact:** 🔵 High - Core performance

---

### 7. Live Graph Updates

**Technology:** WebSocket (Already Implemented)

**Current Status:** ✅ Already implemented via NATS

**Enhancements:**
- Add delta updates (only changed nodes)
- Add batch updates to reduce message count
- Add compression for large graph updates

**Priority:** 🟢 Low - Already functional
**Effort:** 🟡 Medium (3-4 days)
**Impact:** 🟡 Medium - Optimization

---

### 8. Chat/Comments

**Technology:** WebSocket (Already Implemented)

**Current Status:** Partially implemented

**Enhancements:**
- Add typing indicators
- Add read receipts
- Add message delivery confirmation

**Priority:** 🟡 Medium - Nice to have
**Effort:** 🟢 Low (2-3 days)
**Impact:** 🟡 Medium - UX improvement

---

### 9. Build/Test Logs

**Technology:** SSE or NDJSON

**Why:**
- Large volume of data
- One-way stream
- Resume from last line

**Implementation:**

**Option A: SSE for live logs**
```
GET /api/v1/test-runs/:runId/logs/stream
Event stream of log lines
```

**Option B: NDJSON for historical logs**
```
GET /api/v1/test-runs/:runId/logs/export
NDJSON stream of all logs
```

**Recommendation:** Use both
- SSE for live logs during test run
- NDJSON for downloading historical logs

**Priority:** 🟡 Medium - Developer experience
**Effort:** 🟡 Medium (3-4 days)
**Impact:** 🟡 Medium - Better debugging

---

## Priority Matrix

| Feature | Priority | Effort | Impact | Timeline |
|---------|----------|--------|--------|----------|
| Test Run Progress | 🔴 High | 🟡 Medium | 🔵 High | Week 1-2 |
| Infinite Scroll + Cursor Pagination | 🔴 High | 🟡 Medium | 🔵 High | Week 2-4 |
| Live Notifications | 🔴 High | 🟢 Low | 🔵 High | Week 5 |
| Large Dataset Export | 🟡 Medium | 🟢 Low | 🟡 Medium | Week 6 |
| Dashboard Metrics | 🟡 Medium | 🟢 Low | 🟡 Medium | Week 7 |
| Build/Test Logs | 🟡 Medium | 🟡 Medium | 🟡 Medium | Week 8-9 |
| Collaboration Enhancements | 🟡 Medium | 🟡 Medium | 🟡 Medium | Week 10-11 |
| Chat Enhancements | 🟡 Medium | 🟢 Low | 🟡 Medium | Week 12 |
| Graph Update Optimization | 🟢 Low | 🟡 Medium | 🟡 Medium | Future |

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4) - Q1 2026

**Goals:**
- Add cursor-based pagination to backend
- Implement SSE infrastructure
- Extend virtual scrolling to all views

**Tasks:**

**Week 1-2: Backend Cursor Pagination**
- [ ] Add `EncodeCursor/DecodeCursor` utility functions
- [ ] Update Items API to support cursor pagination
- [ ] Update Test Cases API to support cursor pagination
- [ ] Update Requirements API to support cursor pagination
- [ ] Add database indexes for cursor fields (created_at, id)
- [ ] Write unit tests for cursor pagination

**Week 3-4: Frontend Infinite Scroll**
- [ ] Create reusable `useInfiniteQuery` hook with cursor support
- [ ] Update ItemsTableView to use cursor pagination
- [ ] Add virtual scrolling to TestCasesView
- [ ] Add virtual scrolling to RequirementsView
- [ ] Add virtual scrolling to TestRunsView
- [ ] Write E2E tests for infinite scroll

**Deliverables:**
- ✅ All list views support cursor pagination
- ✅ All large lists use virtual scrolling
- ✅ Performance target: 10,000 items smooth scrolling

---

### Phase 2: Real-time Streaming (Weeks 5-7) - Q2 2026

**Goals:**
- Implement SSE endpoints
- Add live notifications
- Add dashboard metrics streaming

**Tasks:**

**Week 5: SSE Infrastructure**
- [ ] Create SSE handler utility (`StreamEvents`)
- [ ] Add NATS → SSE bridge
- [ ] Create frontend `useSSE` hook
- [ ] Add SSE authentication middleware
- [ ] Write SSE integration tests

**Week 6: Notifications & Progress**
- [ ] Implement `/events/stream` endpoint
- [ ] Implement `/test-runs/:id/progress/stream` endpoint
- [ ] Add NotificationService for publishing events
- [ ] Create LiveNotifications component
- [ ] Create TestRunProgress component

**Week 7: Dashboard Metrics**
- [ ] Implement `/metrics/stream` endpoint
- [ ] Add metric collection service
- [ ] Create LiveMetrics component
- [ ] Add dashboard charts with live updates

**Deliverables:**
- ✅ SSE endpoints for notifications, progress, metrics
- ✅ Live UI updates without polling
- ✅ Performance target: <50ms event latency

---

### Phase 3: Export & Logs (Weeks 8-9) - Q2 2026

**Goals:**
- Implement NDJSON streaming
- Add large export functionality
- Add log streaming

**Tasks:**

**Week 8: NDJSON Export**
- [ ] Create NDJSON handler utility
- [ ] Implement `/items/stream` endpoint
- [ ] Implement `/test-runs/:id/logs/export` endpoint
- [ ] Create frontend NDJSON consumer
- [ ] Add export UI with progress bar

**Week 9: Live Logs**
- [ ] Implement `/test-runs/:id/logs/stream` SSE endpoint
- [ ] Create LogViewer component with auto-scroll
- [ ] Add log search and filtering
- [ ] Add log download functionality

**Deliverables:**
- ✅ Export 100,000+ items without memory issues
- ✅ Stream logs in real-time
- ✅ Performance target: Handle 1MB/sec log throughput

---

### Phase 4: Enhancements (Weeks 10-12) - Q2 2026

**Goals:**
- Enhance collaboration features
- Optimize WebSocket usage
- Add advanced features

**Tasks:**

**Week 10-11: Collaboration**
- [ ] Add presence indicators (who's viewing)
- [ ] Add cursor tracking for multi-user editing
- [ ] Add typing indicators for chat
- [ ] Add read receipts

**Week 12: Optimization**
- [ ] Add WebSocket message compression
- [ ] Add delta updates for graphs
- [ ] Add batch message sending
- [ ] Performance profiling and optimization

**Deliverables:**
- ✅ Enhanced real-time collaboration
- ✅ Optimized WebSocket performance
- ✅ Performance target: 1,000 concurrent connections per server

---

## Database Schema Changes

### Cursor Pagination Indexes

```sql
-- Items table (already exists, add index if missing)
CREATE INDEX IF NOT EXISTS idx_items_cursor
ON items(project_id, created_at DESC, id DESC);

-- Test cases table
CREATE INDEX IF NOT EXISTS idx_test_cases_cursor
ON test_cases(project_id, created_at DESC, id DESC);

-- Requirements table
CREATE INDEX IF NOT EXISTS idx_requirements_cursor
ON requirements(project_id, created_at DESC, id DESC);

-- Test runs table
CREATE INDEX IF NOT EXISTS idx_test_runs_cursor
ON test_runs(project_id, created_at DESC, id DESC);

-- Audit logs table
CREATE INDEX IF NOT EXISTS idx_audit_logs_cursor
ON audit_logs(project_id, created_at DESC, id DESC);
```

### NATS Event Schema

```go
// Standard event envelope
type Event struct {
    ID        string    `json:"id"`
    Type      string    `json:"type"`
    ProjectID string    `json:"project_id"`
    UserID    string    `json:"user_id"`
    Data      any       `json:"data"`
    Timestamp time.Time `json:"timestamp"`
}

// Event types
const (
    EventTypeNotification  = "notification"
    EventTypeItemCreated   = "item.created"
    EventTypeItemUpdated   = "item.updated"
    EventTypeTestStarted   = "test.started"
    EventTypeTestCompleted = "test.completed"
    EventTypeMetric        = "metric"
)
```

---

## API Endpoints Summary

### SSE Endpoints (New)

| Endpoint | Description | Events |
|----------|-------------|--------|
| `GET /api/v1/projects/:id/events/stream` | Project-wide events | notification, mention, assignment |
| `GET /api/v1/test-runs/:id/progress/stream` | Test run progress | test_started, test_completed, run_completed |
| `GET /api/v1/test-runs/:id/logs/stream` | Live test logs | log_line |
| `GET /api/v1/projects/:id/metrics/stream` | Live metrics | cpu, memory, active_users |

### REST Endpoints (Enhanced)

| Endpoint | Enhancement | Response |
|----------|-------------|----------|
| `GET /api/v1/projects/:id/items` | Add cursor param | `{ items, next_cursor, has_more }` |
| `GET /api/v1/projects/:id/test-cases` | Add cursor param | `{ items, next_cursor, has_more }` |
| `GET /api/v1/projects/:id/items/stream` | NDJSON export | Stream of NDJSON items |
| `GET /api/v1/test-runs/:id/logs/export` | NDJSON export | Stream of NDJSON logs |

### WebSocket Endpoints (Existing)

| Endpoint | Description | Messages |
|----------|-------------|----------|
| `WS /api/v1/ws` | Real-time collaboration | graph_update, chat_message, presence |

---

## Performance Targets

### Latency

| Operation | Target | Current | Improvement |
|-----------|--------|---------|-------------|
| SSE Event Delivery | <50ms | N/A (new) | - |
| WebSocket Message | <10ms | ~15ms | 🟡 Optimize |
| Cursor Pagination Query | <100ms | ~200ms (offset) | 🔵 2x faster |
| Virtual Scroll Render | 60fps | 60fps | ✅ Maintained |
| NDJSON Streaming | 10MB/s | N/A (new) | - |

### Scalability

| Metric | Target | Notes |
|--------|--------|-------|
| **SSE Connections** | 1,000/server | With keepalive |
| **WebSocket Connections** | 10,000/server | With compression |
| **Concurrent Streams** | 500/server | NDJSON exports |
| **Items per List** | 100,000+ | With virtual scrolling |
| **Message Throughput** | 10,000/sec | Per server |

### Memory

| Component | Target | Current |
|-----------|--------|---------|
| Virtual List (10k items) | <20MB | ~15MB ✅ |
| SSE Connection | <50KB | N/A (new) |
| WebSocket Connection | <100KB | ~120KB 🟡 |
| NDJSON Stream | <10MB | N/A (new) |

---

## Monitoring & Observability

### Metrics to Track

**SSE Metrics:**
- Active SSE connections count
- Events sent per second
- Event delivery latency (p50, p95, p99)
- Connection errors/disconnections

**WebSocket Metrics:**
- Active WebSocket connections count
- Messages sent/received per second
- Message delivery latency
- Connection errors/reconnections

**Pagination Metrics:**
- Cursor query execution time
- Items fetched per request
- Cache hit rate (if implemented)

**Virtual Scrolling Metrics:**
- Scroll FPS
- Virtual items rendered
- Memory usage

### Prometheus Queries

```promql
# SSE connections
sum(sse_connections_active{project=~".*"})

# SSE event latency
histogram_quantile(0.95, rate(sse_event_duration_seconds_bucket[5m]))

# WebSocket message rate
rate(websocket_messages_sent_total[1m])

# Cursor query latency
histogram_quantile(0.95, rate(db_cursor_query_duration_seconds_bucket[5m]))
```

### Grafana Dashboards

**Dashboard: Real-time Streaming**
- SSE connections over time
- WebSocket connections over time
- Event delivery latency (p50, p95, p99)
- Message throughput

**Dashboard: List Performance**
- Virtual scroll FPS
- Cursor query latency
- Items loaded per view
- Memory usage per component

---

## Testing Strategy

### Unit Tests

```go
// Backend: Cursor pagination
func TestCursorPagination(t *testing.T) {
    // Test forward pagination
    // Test backward pagination
    // Test invalid cursor handling
    // Test limit enforcement
}

// Backend: SSE streaming
func TestSSEStream(t *testing.T) {
    // Test event delivery
    // Test keepalive
    // Test client disconnect
}
```

```typescript
// Frontend: Virtual scrolling
test('renders 10,000 items smoothly', () => {
    // Measure FPS
    // Check memory usage
    // Verify only visible items rendered
});

// Frontend: Infinite scroll
test('fetches next page when scrolling near bottom', () => {
    // Mock API
    // Scroll to bottom
    // Verify fetchNextPage called
});
```

### Integration Tests

```typescript
// E2E: Infinite scroll
test('loads all items via infinite scroll', async () => {
    await page.goto('/projects/123/items');
    await page.waitForSelector('[data-testid="item-row"]');

    // Scroll to bottom multiple times
    for (let i = 0; i < 5; i++) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(500);
    }

    // Verify items loaded
    const items = await page.$$('[data-testid="item-row"]');
    expect(items.length).toBeGreaterThan(100);
});

// E2E: SSE notifications
test('receives live notifications', async () => {
    const notifications: string[] = [];

    await page.exposeFunction('captureNotification', (msg: string) => {
        notifications.push(msg);
    });

    await page.evaluate(() => {
        const es = new EventSource('/api/v1/projects/123/events/stream');
        es.addEventListener('notification', (e) => {
            window.captureNotification(e.data);
        });
    });

    // Trigger notification on backend
    // Wait for notification
    await page.waitForFunction(() => notifications.length > 0, { timeout: 5000 });

    expect(notifications[0]).toContain('New item created');
});
```

### Load Tests

```bash
# SSE load test (1,000 concurrent connections)
./load-test-sse.sh

# WebSocket load test (10,000 concurrent connections)
./load-test-websocket.sh

# Cursor pagination load test (10,000 items)
./load-test-cursor.sh
```

---

## Migration Plan

### Breaking Changes

**None.** All changes are backward compatible:
- Cursor pagination added as optional query param
- SSE endpoints are new
- NDJSON endpoints are new
- Virtual scrolling is client-side only

### Gradual Rollout

**Week 1-2:** Backend cursor pagination (optional, offset still supported)
**Week 3-4:** Frontend infinite scroll (graceful degradation if backend not ready)
**Week 5-6:** SSE endpoints (progressive enhancement)
**Week 7-8:** NDJSON exports (new feature, no migration)

### Rollback Plan

All features can be disabled via feature flags:
```go
// Feature flags
const (
    FeatureCursorPagination = "cursor_pagination"
    FeatureSSE              = "sse_streaming"
    FeatureNDJSON           = "ndjson_export"
)

// Check feature flag
if config.IsFeatureEnabled(FeatureSSE) {
    router.GET("/events/stream", handler.StreamEvents)
}
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SSE not supported in some proxies | Low | Medium | Fallback to polling |
| Cursor pagination slower for large offsets | Medium | Low | Use database indexes |
| Memory leak in long-lived SSE connections | Medium | High | Add connection timeout, monitoring |
| NDJSON parsing errors on client | Low | Medium | Add error handling, retry logic |
| WebSocket scaling issues | Low | High | Use Redis Pub/Sub for multi-server |

---

## Success Criteria

### Phase 1 (Weeks 1-4)
- ✅ All list views support 10,000+ items without lag
- ✅ Cursor pagination 2x faster than offset pagination
- ✅ Virtual scrolling maintains 60fps

### Phase 2 (Weeks 5-7)
- ✅ Live notifications arrive within 50ms
- ✅ Dashboard metrics update in real-time
- ✅ Test run progress streams without polling

### Phase 3 (Weeks 8-9)
- ✅ Export 100,000 items without memory issues
- ✅ Stream logs at 1MB/sec throughput
- ✅ NDJSON parsing works in all browsers

### Phase 4 (Weeks 10-12)
- ✅ Presence indicators show active users
- ✅ WebSocket handles 10,000 concurrent connections
- ✅ Overall system handles 1,000 requests/sec

---

## Next Steps

1. **Review and approve this plan** (1 day)
2. **Set up feature flags** (1 day)
3. **Create database migration for indexes** (1 day)
4. **Begin Phase 1 implementation** (Week 1)

---

## Appendix

### Additional Resources

- [Streaming Technologies Comparison](/docs/research/streaming-technologies-comparison.md)
- [Virtual Scrolling Evaluation](/docs/research/virtual-scrolling-evaluation.md)
- [Streaming Implementation Patterns](/docs/guides/streaming-implementation-patterns.md)

### Code Examples

See `/docs/guides/streaming-implementation-patterns.md` for:
- Complete SSE handler implementation
- WebSocket backpressure handling
- NDJSON streaming producer/consumer
- Cursor pagination queries
- React hooks for all streaming types

### Performance Benchmarks

See `/docs/research/streaming-technologies-comparison.md` for:
- Latency comparison
- Memory usage comparison
- Throughput comparison
- Browser compatibility matrix
