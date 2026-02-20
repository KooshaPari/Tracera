# Streaming Technologies Comparison

**Research Date:** 2026-02-01
**Status:** Comprehensive Analysis
**Scope:** Real-time streaming solutions for TraceRTM large dataset handling

---

## Executive Summary

This document compares four primary streaming technologies for handling large datasets in TraceRTM:
1. **Server-Sent Events (SSE)**
2. **WebSockets**
3. **GraphQL Subscriptions**
4. **Streaming JSON (NDJSON)**

**Current State:**
- ✅ WebSockets implemented (Go backend + React frontend)
- ✅ NATS message broker for event distribution
- ✅ SSE used for AI streaming responses
- ⚠️ No general SSE endpoints for data streaming
- ⚠️ Offset-based pagination only (no cursor-based)
- ⚠️ No NDJSON streaming for exports

---

## Technology Comparison Matrix

| Feature | SSE | WebSockets | GraphQL Subscriptions | Streaming JSON (NDJSON) |
|---------|-----|------------|----------------------|-------------------------|
| **Direction** | Server → Client | Bidirectional | Server → Client | Server → Client |
| **Protocol** | HTTP/1.1+ | TCP (Upgrade) | WebSocket/HTTP | HTTP |
| **Browser Support** | 98%+ (IE11+) | 98%+ (IE10+) | 98%+ | 100% |
| **Reconnection** | Automatic | Manual | Depends on lib | Manual |
| **Event ID** | Built-in | Custom | Custom | Custom |
| **Compression** | HTTP gzip | Per-message | Per-message | HTTP gzip |
| **Proxy Friendly** | Yes | Sometimes | Sometimes | Yes |
| **Firewall Friendly** | Yes | Sometimes | Sometimes | Yes |
| **Setup Complexity** | Low | Medium | High | Low |
| **Memory Overhead** | Low | Medium | Medium-High | Low |
| **Connection Limit** | ~6/domain (HTTP/1.1) | Unlimited | Unlimited | ~6/domain |
| **Text Format** | Text | Binary/Text | JSON | NDJSON |
| **Built-in Retry** | Yes | No | No | No |

---

## 1. Server-Sent Events (SSE)

### Overview
HTTP-based one-way streaming from server to client using `text/event-stream` content type.

### Browser Support
- ✅ All modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Polyfills available for older browsers
- ✅ EventSource API standardized

### Go Implementation Patterns

#### Standard Library Approach (Recommended)
```go
// SSE handler using Echo framework
func StreamItems(c echo.Context) error {
    c.Response().Header().Set("Content-Type", "text/event-stream")
    c.Response().Header().Set("Cache-Control", "no-cache")
    c.Response().Header().Set("Connection", "keep-alive")
    c.Response().Header().Set("X-Accel-Buffering", "no") // Disable nginx buffering

    flusher, ok := c.Response().Writer.(http.Flusher)
    if !ok {
        return echo.NewHTTPError(http.StatusInternalServerError, "Streaming not supported")
    }

    // Get project ID from query params
    projectID := c.QueryParam("project_id")

    // Create event channel
    eventChan := make(chan Event, 100)
    defer close(eventChan)

    // Subscribe to NATS events for this project
    subject := fmt.Sprintf("project.%s.*", projectID)
    sub, err := natsConn.ChanSubscribe(subject, eventChan)
    if err != nil {
        return err
    }
    defer sub.Unsubscribe()

    // Stream events to client
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case event := <-eventChan:
            data, _ := json.Marshal(event)
            fmt.Fprintf(c.Response().Writer, "event: %s\n", event.Type)
            fmt.Fprintf(c.Response().Writer, "data: %s\n\n", data)
            flusher.Flush()

        case <-ticker.C:
            // Keepalive comment
            fmt.Fprintf(c.Response().Writer, ": keepalive\n\n")
            flusher.Flush()

        case <-c.Request().Context().Done():
            return nil
        }
    }
}
```

#### Third-Party Libraries
- **r3labs/sse** - Full-featured SSE server
  - Pros: Built-in client management, event multiplexing
  - Cons: Additional dependency
- **Custom implementation** - Sufficient for most cases

### Frontend Consumption

```typescript
// React hook for SSE connection
function useSSE<T>(url: string, eventType: string) {
    const [data, setData] = useState<T | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [status, setStatus] = useState<'connecting' | 'open' | 'closed'>('connecting');

    useEffect(() => {
        const eventSource = new EventSource(url);

        eventSource.onopen = () => setStatus('open');

        eventSource.addEventListener(eventType, (event) => {
            try {
                const parsed = JSON.parse(event.data);
                setData(parsed);
            } catch (e) {
                setError(e as Error);
            }
        });

        eventSource.onerror = () => {
            setStatus('closed');
            setError(new Error('SSE connection failed'));
        };

        return () => {
            eventSource.close();
            setStatus('closed');
        };
    }, [url, eventType]);

    return { data, error, status };
}

// Usage in component
function LiveNotifications({ projectId }: { projectId: string }) {
    const { data, status } = useSSE<Notification>(
        `/api/v1/projects/${projectId}/events`,
        'notification'
    );

    return status === 'open' && data ? (
        <Toast>{data.message}</Toast>
    ) : null;
}
```

### Pros
- ✅ Simple to implement (native HTTP)
- ✅ Automatic reconnection with `EventSource`
- ✅ Built-in event IDs for resuming
- ✅ Works through most proxies/firewalls
- ✅ Efficient for one-way updates
- ✅ Lower memory footprint than WebSockets
- ✅ HTTP/2 multiplexing support

### Cons
- ❌ One-way only (server → client)
- ❌ Text-based (no binary)
- ❌ Limited to 6 connections per domain (HTTP/1.1)
- ❌ No built-in authentication (use query params or separate handshake)
- ❌ Less efficient for high-frequency updates

### Best Use Cases for TraceRTM
1. **Live Notifications** - User mentions, task assignments
2. **Progress Updates** - Import/export progress, test run status
3. **Dashboard Metrics** - Live metric updates (CPU, memory, active users)
4. **Build/Test Status** - CI/CD pipeline updates
5. **Audit Logs** - Real-time log streaming

### Anti-Patterns
- ❌ Bidirectional communication needs (use WebSocket)
- ❌ Binary data transfer (use WebSocket)
- ❌ High-frequency updates (>10/sec)

---

## 2. WebSockets

### Overview
Full-duplex bidirectional communication over a persistent TCP connection.

### Current Implementation in TraceRTM

**Backend (Go):**
```go
// Location: backend/internal/websocket/websocket.go
// Uses: golang.org/x/net/websocket
// Features:
// - Authentication via token message
// - NATS event propagation
// - Project-based subscriptions
// - Heartbeat/keepalive
// - Auto-reconnection handling
```

**Frontend (React):**
```typescript
// Location: frontend/apps/web/src/api/websocket.ts
// Features:
// - Singleton WebSocketManager
// - Token-based authentication
// - Channel subscriptions
// - Exponential backoff reconnection
// - Heartbeat every 30s
```

### Go Libraries Comparison

| Library | Stars | Last Update | Pros | Cons |
|---------|-------|-------------|------|------|
| **gorilla/websocket** | 22k+ | Active | Battle-tested, full API | Verbose API |
| **nhooyr/websocket** | 3k+ | Active | Modern, simpler API, context support | Smaller ecosystem |
| **golang.org/x/net/websocket** | Standard | Active | Stdlib, no deps | Basic features |
| **gobwas/ws** | 6k+ | Active | Zero-copy, high performance | Low-level, complex |

**Recommendation:** Migrate to **nhooyr/websocket** for better context support and cleaner API.

```go
// Modern WebSocket with nhooyr/websocket
import "nhooyr.io/websocket"

func HandleWebSocket(w http.ResponseWriter, r *http.Request) {
    conn, err := websocket.Accept(w, r, &websocket.AcceptOptions{
        CompressionMode: websocket.CompressionContextTakeover,
    })
    if err != nil {
        return
    }
    defer conn.Close(websocket.StatusNormalClosure, "")

    ctx := r.Context()

    // Read messages
    for {
        typ, msg, err := conn.Read(ctx)
        if err != nil {
            return
        }

        // Handle message
        response := processMessage(msg)

        // Write response
        err = conn.Write(ctx, typ, response)
        if err != nil {
            return
        }
    }
}
```

### Connection Lifecycle Management

**Scaling Considerations:**

1. **Sticky Sessions Required**
   - WebSocket connections must stay on same server
   - Use IP hash or cookie-based routing
   - TraceRTM uses single-server deployment currently

2. **Redis Pub/Sub for Multi-Server**
   ```go
   // Broadcast message across servers
   type WSHub struct {
       clients map[*Client]bool
       redisPubSub *redis.PubSub
   }

   func (h *WSHub) Broadcast(msg []byte) {
       // Publish to Redis
       h.redisClient.Publish(ctx, "ws:broadcast", msg)
   }

   func (h *WSHub) SubscribeToRedis() {
       for msg := range h.redisPubSub.Channel() {
           // Forward to local clients
           for client := range h.clients {
               client.Send <- msg.Payload
           }
       }
   }
   ```

### Pros
- ✅ Bidirectional communication
- ✅ Binary and text support
- ✅ Low latency
- ✅ Efficient for high-frequency updates
- ✅ Per-message compression
- ✅ No connection limits

### Cons
- ❌ Complex to implement correctly
- ❌ Manual reconnection logic required
- ❌ Proxy/firewall issues in some environments
- ❌ Requires sticky sessions for load balancing
- ❌ Higher memory overhead per connection

### Best Use Cases for TraceRTM
1. **✅ Real-time Collaboration** - Multi-user editing
2. **✅ Live Graph Updates** - Node position changes
3. **✅ Chat/Comments** - Real-time communication
4. **✅ Cursor Presence** - Show active users
5. **✅ Test Execution** - Live test runner output

### Anti-Patterns
- ❌ One-way notifications only (use SSE)
- ❌ Large file transfers (use HTTP streaming)
- ❌ Infrequent updates (<1/min, use polling)

---

## 3. GraphQL Subscriptions

### Overview
GraphQL subscriptions provide real-time updates using WebSocket transport (typically via graphql-ws protocol).

### Go Implementation

**Option 1: gqlgen (Recommended for GraphQL-first)**
```go
// schema.graphql
type Subscription {
    itemUpdated(projectID: ID!): Item!
    testRunProgress(runID: ID!): TestRunProgress!
}

// resolver.go
func (r *subscriptionResolver) ItemUpdated(ctx context.Context, projectID string) (<-chan *model.Item, error) {
    itemChan := make(chan *model.Item, 1)

    // Subscribe to NATS
    sub, err := r.natsConn.Subscribe(fmt.Sprintf("item.*.%s", projectID), func(msg *nats.Msg) {
        var item model.Item
        json.Unmarshal(msg.Data, &item)
        itemChan <- &item
    })

    // Cleanup on context cancellation
    go func() {
        <-ctx.Done()
        sub.Unsubscribe()
        close(itemChan)
    }()

    return itemChan, nil
}
```

**Option 2: Apollo Server (Node.js)**
- Requires separate Node.js service
- Better client ecosystem
- Not recommended for Go-first architecture

### Frontend Consumption

```typescript
import { useSubscription } from '@apollo/client';

const ITEM_UPDATED = gql`
    subscription ItemUpdated($projectID: ID!) {
        itemUpdated(projectID: $projectID) {
            id
            title
            status
            updatedAt
        }
    }
`;

function LiveItemList({ projectID }: { projectID: string }) {
    const { data, loading } = useSubscription(ITEM_UPDATED, {
        variables: { projectID }
    });

    // Automatically re-renders on updates
    return <ItemCard item={data?.itemUpdated} />;
}
```

### Pros
- ✅ Type-safe (GraphQL schema)
- ✅ Selective field updates (only request fields you need)
- ✅ Unified API with queries/mutations
- ✅ Great developer experience
- ✅ Strong client libraries (@apollo/client)

### Cons
- ❌ High complexity (GraphQL + WebSocket)
- ❌ Larger bundle size (Apollo Client ~50kb)
- ❌ Overhead if not using GraphQL for rest of API
- ❌ Additional learning curve
- ❌ More moving parts to maintain

### Best Use Cases for TraceRTM
- **Only if migrating entire API to GraphQL**
- Otherwise, SSE or WebSocket is simpler

### Current Recommendation
**⚠️ Not recommended** for TraceRTM given existing REST API. Would require significant refactoring.

---

## 4. Streaming JSON (NDJSON)

### Overview
Newline-Delimited JSON - stream JSON objects separated by newlines over HTTP.

### Go Implementation

```go
// Stream large list of items
func StreamItems(c echo.Context) error {
    c.Response().Header().Set("Content-Type", "application/x-ndjson")
    c.Response().WriteHeader(http.StatusOK)

    flusher, ok := c.Response().Writer.(http.Flusher)
    if !ok {
        return echo.NewHTTPError(http.StatusInternalServerError)
    }

    // Query items in batches
    encoder := json.NewEncoder(c.Response().Writer)
    offset := 0
    batchSize := 100

    for {
        items, err := db.QueryItems(offset, batchSize)
        if err != nil || len(items) == 0 {
            break
        }

        for _, item := range items {
            if err := encoder.Encode(item); err != nil {
                return err
            }
            flusher.Flush()
        }

        offset += batchSize
    }

    return nil
}
```

### Frontend Consumption (Fetch Streaming)

```typescript
async function* fetchNDJSON<T>(url: string): AsyncGenerator<T> {
    const response = await fetch(url);
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line

        for (const line of lines) {
            if (line.trim()) {
                yield JSON.parse(line);
            }
        }
    }
}

// Usage
async function loadItems() {
    for await (const item of fetchNDJSON<Item>('/api/v1/items/stream')) {
        // Process item incrementally
        addItemToUI(item);
    }
}
```

### Pros
- ✅ Simple protocol (just newlines)
- ✅ Works with standard HTTP
- ✅ Incremental parsing
- ✅ Memory efficient
- ✅ Perfect for large exports
- ✅ Resume support with Range headers

### Cons
- ❌ One-way only (server → client)
- ❌ No automatic reconnection
- ❌ Manual parsing required
- ❌ Less browser support for streaming

### Best Use Cases for TraceRTM
1. **Large Exports** - Export 10k+ items to file
2. **Bulk Data Transfer** - Initial load of large datasets
3. **Log Streaming** - Stream build/test logs
4. **Report Generation** - Progressive report rendering

---

## Recommendation Matrix by Use Case

| Use Case | Recommended | Alternative | Why |
|----------|-------------|-------------|-----|
| **Live Notifications** | SSE | WebSocket | One-way, auto-reconnect |
| **Dashboard Metrics** | SSE | WebSocket | One-way, low frequency |
| **Collaborative Editing** | WebSocket | SSE (polling fallback) | Bidirectional required |
| **Test Run Progress** | SSE | WebSocket | One-way, structured events |
| **Export Large Dataset** | NDJSON | HTTP streaming | Memory efficient, resumable |
| **Live Graph Updates** | WebSocket | SSE | Already implemented, high frequency |
| **Chat/Comments** | WebSocket | SSE + HTTP POST | Bidirectional, low latency |
| **Cursor Presence** | WebSocket | N/A | Real-time position updates |
| **Build Logs** | SSE or NDJSON | WebSocket | One-way, large volume |

---

## Performance Characteristics

### Latency Comparison (Typical)
```
WebSocket:      1-5ms    (after connection established)
SSE:            5-15ms   (after connection established)
GraphQL Sub:    5-15ms   (after connection established)
NDJSON:         10-50ms  (initial response latency)
HTTP Polling:   100ms+   (polling interval)
```

### Memory Usage (Per 1000 Connections)
```
WebSocket:      ~50-100 MB (with Go)
SSE:            ~30-50 MB  (with Go)
GraphQL Sub:    ~80-120 MB (with Apollo Server)
NDJSON:         ~10-20 MB  (short-lived connections)
```

### Throughput (Messages/Second, Single Server)
```
WebSocket:      10,000+  (binary, compressed)
SSE:            1,000-5,000 (text, gzipped)
GraphQL Sub:    1,000-3,000 (JSON over WebSocket)
NDJSON:         500-2,000  (depends on message size)
```

---

## Integration with TraceRTM Architecture

### Current Stack Compatibility

| Technology | Backend (Go) | Frontend (React) | NATS | PostgreSQL |
|------------|--------------|------------------|------|------------|
| **SSE** | ✅ Echo/stdlib | ✅ EventSource API | ✅ Subscribe | ✅ LISTEN/NOTIFY |
| **WebSocket** | ✅ Implemented | ✅ Implemented | ✅ Implemented | ✅ Via NATS |
| **GraphQL Sub** | ⚠️ gqlgen | ⚠️ Apollo Client | ⚠️ Manual | ⚠️ Manual |
| **NDJSON** | ✅ stdlib | ✅ Fetch API | ❌ N/A | ✅ Cursor query |

### Authentication Integration

**WebSocket (Current):**
```typescript
// Send token in first message
ws.send(JSON.stringify({ type: 'auth', token: accessToken }));
```

**SSE (Recommended):**
```typescript
// Send token as Authorization header via custom fetch
const eventSource = new EventSourcePolyfill('/api/v1/events', {
    headers: { Authorization: `Bearer ${accessToken}` }
});
```

**NDJSON:**
```typescript
// Standard bearer token
fetch('/api/v1/items/stream', {
    headers: { Authorization: `Bearer ${accessToken}` }
});
```

---

## Browser Compatibility Summary

| Feature | Chrome | Firefox | Safari | Edge | Mobile |
|---------|--------|---------|--------|------|--------|
| **SSE** | ✅ 6+ | ✅ 6+ | ✅ 5+ | ✅ 12+ | ✅ All |
| **WebSocket** | ✅ 16+ | ✅ 11+ | ✅ 6+ | ✅ 12+ | ✅ All |
| **GraphQL Sub** | ✅ 16+ | ✅ 11+ | ✅ 6+ | ✅ 12+ | ✅ All |
| **NDJSON Streaming** | ✅ 43+ | ✅ 57+ | ✅ 10.1+ | ✅ 14+ | ✅ iOS 10.3+, Android 5+ |

**Polyfills:**
- SSE: `event-source-polyfill` for auth headers
- Fetch Streaming: Built-in for modern browsers

---

## Scaling Considerations

### Horizontal Scaling

**WebSocket:**
```
Client → Load Balancer (sticky sessions) → Server 1, 2, 3...
                                              ↓
                                          Redis Pub/Sub
```

**SSE:**
```
Client → Load Balancer (no sticky needed) → Server 1, 2, 3...
                                              ↓
                                          NATS/Redis
```

**NDJSON:**
```
Client → Load Balancer (round-robin) → Server 1, 2, 3...
                                         ↓
                                     Shared Database
```

### Connection Limits

| Technology | Per-Server Limit | Notes |
|------------|------------------|-------|
| **WebSocket** | ~64,000 | Limited by file descriptors |
| **SSE** | ~64,000 | Same as WebSocket |
| **NDJSON** | N/A | Short-lived connections |

**TraceRTM Current:** Single server, ~100 concurrent users expected → All options viable

---

## Implementation Priorities for TraceRTM

### Phase 1: Immediate (Q1 2026)
1. ✅ Keep existing WebSocket for real-time collaboration
2. ✅ Add SSE endpoints for notifications
3. ✅ Implement NDJSON export for large datasets

### Phase 2: Enhancement (Q2 2026)
1. Add SSE for dashboard metrics
2. Add SSE for test run progress
3. Optimize WebSocket message compression

### Phase 3: Advanced (Q3 2026)
1. Evaluate GraphQL migration (if needed)
2. Implement cursor-based pagination
3. Add WebSocket scaling with Redis Pub/Sub

---

## Security Considerations

### Authentication

| Technology | Method | Security Level |
|------------|--------|----------------|
| **SSE** | Bearer token in custom header | ✅ High (HTTPS) |
| **WebSocket** | Token in first message | ✅ High (WSS) |
| **GraphQL Sub** | Token in connection params | ✅ High (WSS) |
| **NDJSON** | Bearer token header | ✅ High (HTTPS) |

### Rate Limiting

```go
// Rate limit WebSocket messages per client
type RateLimiter struct {
    clients map[string]*rate.Limiter
    mu      sync.Mutex
}

func (rl *RateLimiter) Allow(clientID string) bool {
    rl.mu.Lock()
    defer rl.mu.Unlock()

    limiter, exists := rl.clients[clientID]
    if !exists {
        limiter = rate.NewLimiter(rate.Limit(10), 20) // 10 msg/sec, burst 20
        rl.clients[clientID] = limiter
    }

    return limiter.Allow()
}
```

---

## Conclusion

**Primary Recommendations:**

1. **Keep WebSocket** for real-time collaboration (already implemented well)
2. **Add SSE** for one-way updates (notifications, metrics, progress)
3. **Add NDJSON** for large exports (items, test results, logs)
4. **Skip GraphQL Subscriptions** (too complex for current architecture)

**Next Steps:**
1. Review virtual scrolling implementation (see separate doc)
2. Review database pagination patterns (see implementation patterns doc)
3. Create streaming architecture plan (see plans doc)
