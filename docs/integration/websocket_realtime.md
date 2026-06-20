# WebSocket Real-time Updates Implementation

## Overview

This document describes the WebSocket-based real-time update system that propagates NATS events from backend services to frontend clients.

## Architecture

```
Python Backend → NATS → Go Backend NATS Subscriber → WebSocket Hub → Frontend Clients
                   ↑
Go Backend Events ─┘
```

### Components

1. **NATS Event Bus**: Message broker for cross-backend communication
2. **Python Bridge**: Go service that subscribes to Python-originated NATS events
3. **WebSocket Hub**: Manages WebSocket connections and broadcasts events
4. **Frontend Client**: React/TypeScript WebSocket client with auto-reconnection

## Backend Implementation

### WebSocket Hub Enhancement

The WebSocket hub has been enhanced to handle NATS events:

**File**: `/backend/internal/websocket/websocket.go`

```go
type Hub struct {
    clients           map[string]map[*Client]bool
    entityClients     map[string]map[*Client]bool
    Register          chan *Client
    Unregister        chan *Client
    Broadcast         chan *Message
    BroadcastToEntity chan *EntityMessage
    NATSEventChannel  chan *NATSEvent  // New: NATS event channel
    mu                sync.RWMutex
}

type NATSEvent struct {
    EventType  string                 `json:"event_type"`
    ProjectID  string                 `json:"project_id"`
    EntityID   string                 `json:"entity_id"`
    EntityType string                 `json:"entity_type"`
    Data       map[string]interface{} `json:"data"`
    Timestamp  string                 `json:"timestamp"`
    Source     string                 `json:"source"` // "go" or "python"
}
```

### NATS Event Broadcasting

Events are broadcast to project-specific subscribers:

```go
func (h *Hub) HandleNATSEvent(event *NATSEvent) {
    select {
    case h.NATSEventChannel <- event:
        // Successfully queued
    default:
        log.Printf("NATS event channel full, dropping event")
    }
}

func (h *Hub) handleNATSEvent(event *NATSEvent) {
    clients, ok := h.clients[event.ProjectID]
    if !ok || len(clients) == 0 {
        return // No clients watching this project
    }

    message := &Message{
        Type: "nats_event",
        Data: map[string]interface{}{
            "event_type":  event.EventType,
            "project_id":  event.ProjectID,
            "entity_id":   event.EntityID,
            "entity_type": event.EntityType,
            "data":        event.Data,
            "timestamp":   event.Timestamp,
            "source":      event.Source,
        },
        Timestamp: time.Now(),
    }

    for client := range clients {
        select {
        case client.Send <- message:
        default:
            log.Printf("Client buffer full, skipping event")
        }
    }
}
```

### Client Subscription Management

Clients can dynamically subscribe to projects:

```go
// In ReadPump, handle subscription messages
case "subscribe_project":
    if projectID, ok := msg.Data["project_id"].(string); ok {
        c.Hub.Unregister <- c
        c.ProjectID = projectID
        c.Hub.Register <- c
    }

case "unsubscribe_project":
    c.Hub.Unregister <- c
    c.ProjectID = ""
```

### NATS to WebSocket Bridge Setup

**File**: `/backend/internal/server/server.go`

```go
func (s *Server) setupNATSToWebSocketBridge() {
    if s.infra.NATS == nil {
        return
    }

    // Create Python bridge
    bridge, err := nats.NewPythonBridge(s.infra.NATS.GetConnection())
    if err != nil {
        log.Printf("Failed to create Python bridge: %v", err)
        return
    }

    // Subscribe to ALL Python events
    bridge.SubscribeToPythonEvents(func(event *nats.BridgeEvent) {
        natsEvent := &websocket.NATSEvent{
            EventType:  event.Type,
            ProjectID:  event.ProjectID,
            EntityID:   event.EntityID,
            EntityType: event.EntityType,
            Data:       event.Data,
            Timestamp:  time.Now().Format(time.RFC3339),
            Source:     event.Source,
        }
        s.wsHub.HandleNATSEvent(natsEvent)
    })

    // Also subscribe to Go-originated events
    subscribeToEventPattern(conn, "tracertm.bridge.go.*.item.*", s.wsHub)
    subscribeToEventPattern(conn, "tracertm.bridge.go.*.link.*", s.wsHub)
    subscribeToEventPattern(conn, "tracertm.bridge.go.*.project.*", s.wsHub)
}
```

## Frontend Implementation

### WebSocket Client

**File**: `/frontend/apps/web/src/lib/websocket.ts`

```typescript
export class RealtimeClient {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private listeners = new Map<string, Set<EventListener>>();
  private currentProjectID: string | null = null;
  private token: string | null = null;

  connect(token: string, projectID?: string) {
    this.token = token;
    this.currentProjectID = projectID;

    const url = projectID
      ? `${this.url}?project_id=${projectID}`
      : `${this.url}?project_id=`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      // Send authentication message (token NOT in URL for security)
      this.send({ type: 'auth', token: this.token });
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      this.scheduleReconnect();
    };
  }

  on(eventType: string, callback: EventListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    return () => {
      this.listeners.get(eventType)?.delete(callback);
    };
  }
}

export const realtimeClient = new RealtimeClient();
```

### React Hook for Real-time Updates

**File**: `/frontend/apps/web/src/hooks/useRealtime.ts`

```typescript
export function useRealtimeUpdates(projectId?: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!projectId) return;

    const token = localStorage.getItem('auth_token') || '';
    realtimeClient.connect(token, projectId);

    // Subscribe to item events
    const unsubItem = realtimeClient.on('item.created', (event) => {
      queryClient.invalidateQueries({ queryKey: ['items', projectId] });
      toast.success(`New item created: ${event.data.title}`);
    });

    const unsubItemUpdate = realtimeClient.on('item.updated', (event) => {
      queryClient.invalidateQueries({ queryKey: ['items', projectId] });
      queryClient.invalidateQueries({ queryKey: ['item', event.entity_id] });
    });

    // Subscribe to AI analysis
    const unsubAI = realtimeClient.on('ai.analysis.complete', (event) => {
      queryClient.invalidateQueries({ queryKey: ['specification', event.data.spec_id] });
      toast.success('AI analysis complete');
    });

    return () => {
      unsubItem();
      unsubItemUpdate();
      unsubAI();
      realtimeClient.disconnect();
    };
  }, [projectId, queryClient]);
}
```

### Usage in Components

```typescript
export function ProjectDashboard({ projectId }: { projectId: string }) {
  // Auto-subscribes to project events and invalidates queries
  useRealtimeUpdates(projectId);

  // Your component logic
  return <div>...</div>;
}
```

## Event Types

### Go-originated Events

- `item.created` - New item created
- `item.updated` - Item modified
- `item.deleted` - Item removed
- `link.created` - New link/relationship created
- `link.deleted` - Link removed
- `project.created` - New project created
- `project.updated` - Project modified

### Python-originated Events

- `spec.created` - Specification created
- `spec.updated` - Specification modified
- `ai.analysis.complete` - AI analysis finished
- `execution.completed` - Test execution completed
- `execution.failed` - Test execution failed
- `workflow.completed` - Workflow completed

## WebSocket Message Protocol

### Authentication (First Message)

```json
{
  "type": "auth",
  "token": "Bearer eyJhbGciOiJIUzI1NiIs..."
}
```

### Authentication Response

```json
{
  "type": "auth_success",
  "message": ""
}
```

### Subscribe to Project

```json
{
  "type": "subscribe_project",
  "data": {
    "project_id": "project-123"
  }
}
```

### NATS Event Message

```json
{
  "type": "nats_event",
  "data": {
    "event_type": "item.created",
    "project_id": "project-123",
    "entity_id": "item-456",
    "entity_type": "item",
    "data": {
      "title": "New Requirement",
      "type": "requirement"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "go"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Ping/Pong (Keepalive)

```json
// Client → Server
{ "type": "ping" }

// Server → Client
{ "type": "pong", "timestamp": "2024-01-15T10:30:00Z" }
```

## Connection Lifecycle

1. **Connect**: Client connects with project_id query param
2. **Authenticate**: Client sends auth token in first message
3. **Subscribe**: Hub registers client for project events
4. **Receive**: Client receives NATS events in real-time
5. **Ping**: Periodic keepalive every 30 seconds
6. **Reconnect**: Auto-reconnect on disconnect with exponential backoff
7. **Disconnect**: Clean shutdown on page unload

## Security

- ✅ **Token in Message**: Authentication token sent in first message (NOT in URL)
- ✅ **Required Authentication**: Connections rejected without valid token
- ✅ **Project Isolation**: Clients only receive events for subscribed projects
- ✅ **Rate Limiting**: WebSocket connections rate-limited per IP
- ✅ **Timeout**: Unauthenticated connections closed after 5 seconds

## Performance Considerations

- **Buffered Channels**: NATS event channel buffered to 1000 events
- **Client Send Buffer**: 256 messages per client
- **Backpressure Handling**: Events dropped if client buffer full
- **Connection Cleanup**: Inactive connections cleaned up every minute
- **Project-specific Broadcasting**: Events only sent to relevant clients

## Testing

### Integration Tests

**File**: `/backend/tests/integration/websocket_nats_test.go`

- `TestNATSEventPropagationToWebSocket`: Verify NATS→WebSocket flow
- `TestProjectSpecificBroadcast`: Verify project isolation
- `TestMultipleClientsInSameProject`: Verify multi-client broadcasting

### E2E Tests

**File**: `/frontend/apps/web/e2e/realtime-updates.spec.ts`

- Item creation real-time update
- Item update real-time update
- Link creation notification
- Toast notifications
- Reconnection handling
- Project isolation

## Troubleshooting

### Client Not Receiving Events

1. Check WebSocket connection status in browser DevTools
2. Verify authentication token is valid
3. Confirm project_id matches event's project_id
4. Check backend logs for event broadcasting

### Connection Drops

1. Check network connectivity
2. Verify ping/pong interval (should be every 30s)
3. Check backend for connection cleanup logs
4. Ensure client auto-reconnect is working

### Events Not Propagating from Python

1. Verify Python backend is publishing to NATS
2. Check NATS subject format: `tracertm.bridge.python.{project_id}.{event_type}`
3. Confirm Go backend subscribed to Python events
4. Check bridge logs for errors

## Monitoring

### WebSocket Stats Endpoint

```bash
GET /api/v1/ws/stats
```

Response:
```json
{
  "total_clients": 15,
  "projects": 5,
  "project_counts": {
    "project-a": 8,
    "project-b": 7
  },
  "entity_subscriptions": 12
}
```

### Logs

Backend logs include:
- `Client registered: {id} (project: {project_id})`
- `Broadcast NATS event {type} to {count} clients in project {id}`
- `Client buffer full, skipping event` (backpressure)
- `WebSocket authenticated successfully`

## Future Enhancements

- [ ] Presence detection (who's viewing what)
- [ ] Collaborative cursor positions
- [ ] Message acknowledgments
- [ ] Event replay on reconnection
- [ ] WebSocket clustering for horizontal scaling
- [ ] Compression for large payloads
- [ ] Binary protocol for performance

## References

- [NATS JetStream Documentation](https://docs.nats.io/nats-concepts/jetstream)
- [WebSocket Protocol RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)
- [React Query Documentation](https://tanstack.com/query/latest)
