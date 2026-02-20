# Server-Sent Events (SSE) Notifications Implementation

## Overview

This document describes the Server-Sent Events (SSE) implementation for real-time notifications in TraceRTM. SSE provides a uni-directional, HTTP-based real-time communication channel from the server to the client.

## Architecture

### Backend Components

#### 1. Notification Service (`backend/internal/services/notification_service.go`)

The notification service handles:
- **CRUD operations** for notifications
- **Redis pub/sub** for broadcasting events across multiple server instances
- **In-memory subscription management** for SSE connections
- **Event broadcasting** to connected clients

Key features:
- Thread-safe subscription management
- Redis pub/sub for horizontal scaling
- Automatic cleanup of expired notifications
- Support for multiple event types (notification, read, read_all, delete)

#### 2. Notification Handler (`backend/internal/handlers/notification_handler.go`)

HTTP endpoints for notification management:
- `GET /api/v1/notifications` - List notifications
- `POST /api/v1/notifications/:id/read` - Mark as read
- `POST /api/v1/notifications/read-all` - Mark all as read
- `DELETE /api/v1/notifications/:id` - Delete notification
- **`GET /api/v1/notifications/stream`** - SSE stream endpoint
- `POST /api/v1/notifications` - Create notification (admin/system)

The SSE stream endpoint:
- Sets proper SSE headers
- Sends initial connection event
- Broadcasts real-time notification events
- Sends keep-alive pings every 30 seconds
- Handles client disconnections gracefully

#### 3. Database Schema

The `notifications` table stores:
```go
type Notification struct {
    ID        string           // Unique identifier
    UserID    string           // Owner user ID (indexed)
    Type      NotificationType // info, success, warning, error
    Title     string           // Short title
    Message   string           // Full message
    Link      *string          // Optional link
    ReadAt    *time.Time       // Read timestamp
    CreatedAt time.Time        // Creation timestamp (indexed)
    ExpiresAt *time.Time       // Optional expiration (indexed)
}
```

Auto-migrated via GORM in `infrastructure.go`.

### Frontend Components

#### 1. SSE Client (`frontend/apps/web/src/lib/sse-client.ts`)

Robust SSE client with:
- **Automatic reconnection** with exponential backoff
- **Configurable retry strategy** (max attempts, delays)
- **Event handling** for custom event types
- **Connection state management**
- **Graceful shutdown**

Features:
- Initial delay: 1 second
- Max delay: 30 seconds (exponential backoff)
- Configurable max reconnection attempts
- Support for custom event types (notification, read, delete, etc.)

#### 2. Notifications Hook (`frontend/apps/web/src/hooks/useNotifications.ts`)

React hook that:
- Fetches initial notifications via REST
- Establishes SSE connection for real-time updates
- Updates React Query cache automatically on events
- Provides mutations for marking as read/deleting
- Exposes connection status

Key features:
- Automatic cache updates from SSE events
- No polling (real-time only)
- Connection status indicator
- Optimistic updates support

## Implementation Details

### Event Flow

1. **New Notification Created**:
   ```
   Backend → Service.Create()
             → Database.Insert()
             → Redis.Publish(event)
             → All instances receive event
             → SSE.Broadcast(to subscribed clients)
             → Frontend receives event
             → React Query cache updated
   ```

2. **Mark as Read**:
   ```
   Frontend → HTTP POST /api/v1/notifications/:id/read
             → Service.MarkAsRead()
             → Database.Update()
             → Redis.Publish(event)
             → SSE.Broadcast(to subscribed clients)
             → Frontend receives event
             → Cache updated (optimistic)
   ```

### SSE Message Format

```javascript
// Event type
event: notification

// Data payload
data: {
  "type": "notification",
  "notification": {
    "id": "uuid",
    "user_id": "user-123",
    "type": "info",
    "title": "New Message",
    "message": "You have a new message",
    "link": "/messages/123",
    "created_at": "2026-02-01T12:00:00Z"
  },
  "user_id": "user-123",
  "timestamp": 1706788800
}
```

### Reconnection Strategy

The frontend uses exponential backoff for reconnections:

| Attempt | Delay   |
|---------|---------|
| 1       | 1s      |
| 2       | 2s      |
| 3       | 4s      |
| 4       | 8s      |
| 5       | 16s     |
| 6+      | 30s max |

After 10 failed attempts (default), the client gives up and closes.

## Authentication

SSE connections are authenticated using:
- **Query parameter**: `?token=<jwt>` (EventSource limitation - no custom headers)
- Token extracted from Authorization header by SSE client
- Middleware validates token and sets `user_id` in context

## Scaling Considerations

### Horizontal Scaling

- **Redis pub/sub** enables broadcasting across multiple server instances
- Each instance maintains its own SSE connections
- Events published to Redis are received by all instances
- Each instance broadcasts to its local subscribers only

### Performance

- **Buffered channels** (100 events) prevent blocking
- **Keep-alive pings** every 30 seconds maintain connection
- **Automatic cleanup** of expired notifications
- **Indexed queries** on `user_id`, `created_at`, `expires_at`

## Configuration

### Backend Environment Variables

```bash
# Redis (required for pub/sub)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database (notifications table)
DATABASE_URL=postgresql://...
```

### Frontend Environment Variables

```bash
# API endpoint
VITE_API_URL=http://localhost:4000
```

## Usage Examples

### Creating a Notification (Backend)

```go
import "github.com/kooshapari/tracertm-backend/internal/services"

// Get service from container
notificationService := serviceContainer.NotificationService()

// Create notification
link := "/items/123"
notification, err := notificationService.Create(
    ctx,
    "user-123",
    services.NotificationTypeInfo,
    "Item Updated",
    "Your item has been updated",
    &link,
)
```

### Using Notifications (Frontend)

```typescript
import { useNotifications } from '@/hooks/useNotifications';

function NotificationBell() {
  const {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllRead,
  } = useNotifications();

  return (
    <div>
      {/* Connection indicator */}
      <div className={isConnected ? 'connected' : 'disconnected'}>
        {isConnected ? '🟢' : '🔴'}
      </div>

      {/* Unread count */}
      {unreadCount > 0 && (
        <span className="badge">{unreadCount}</span>
      )}

      {/* Notification list */}
      {notifications.map(n => (
        <div key={n.id} onClick={() => markAsRead.mutate(n.id)}>
          <strong>{n.title}</strong>
          <p>{n.message}</p>
        </div>
      ))}
    </div>
  );
}
```

## Testing

### Manual Testing

1. **Start backend**:
   ```bash
   cd backend
   make run
   ```

2. **Create test notification** (via API):
   ```bash
   curl -X POST http://localhost:4000/api/v1/notifications \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user-123",
       "type": "info",
       "title": "Test",
       "message": "Test notification"
     }'
   ```

3. **Monitor SSE stream**:
   ```bash
   curl -N http://localhost:4000/api/v1/notifications/stream?token=$TOKEN
   ```

### Automated Testing

Unit tests are located in:
- `backend/internal/services/notification_service_test.go` (TODO)
- `backend/internal/handlers/notification_handler_test.go` (TODO)
- `frontend/apps/web/src/__tests__/lib/sse-client.test.ts` (TODO)

## Troubleshooting

### Client Not Receiving Events

1. **Check connection status**:
   ```typescript
   const { isConnected } = useNotifications();
   console.log('Connected:', isConnected);
   ```

2. **Check browser console** for errors

3. **Verify Redis** is running:
   ```bash
   redis-cli ping
   ```

4. **Check server logs** for pub/sub errors

### Events Received but Cache Not Updating

1. **Verify event format** matches `NotificationEvent` interface
2. **Check queryClient** is properly configured
3. **Ensure token** is valid and user_id matches

### Connection Drops Frequently

1. **Check keep-alive** settings (30s ping interval)
2. **Verify firewall/proxy** allows long-lived connections
3. **Check server logs** for errors
4. **Increase buffer size** if events are being dropped

## Future Enhancements

- [ ] WebSocket fallback for better bi-directional support
- [ ] Priority queues for critical notifications
- [ ] Notification preferences/filtering
- [ ] Browser push notifications integration
- [ ] Read receipts and delivery tracking
- [ ] Notification grouping/threading
- [ ] Rich media support (images, actions)
- [ ] Multi-device synchronization

## References

- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [Redis Pub/Sub](https://redis.io/topics/pubsub)
- [GORM Auto-Migration](https://gorm.io/docs/migration.html)

## Task Completion

✅ **Task #83: Phase 2 Real-Time - SSE Notifications Implementation**

Implemented:
1. ✅ Go backend notification service with Redis pub/sub
2. ✅ SSE endpoint with streaming response
3. ✅ Frontend SSE client with exponential backoff reconnection
4. ✅ React hook with automatic cache updates
5. ✅ Database table auto-migration
6. ✅ Authentication via query parameter
7. ✅ Keep-alive ping mechanism
8. ✅ Multi-server scaling support via Redis
