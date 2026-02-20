# SSE Notifications Quick Reference

## API Endpoints

### List Notifications
```http
GET /api/v1/notifications
Authorization: Bearer <token>
```

### Get SSE Stream
```http
GET /api/v1/notifications/stream
Authorization: Bearer <token>
```

### Mark as Read
```http
POST /api/v1/notifications/:id/read
Authorization: Bearer <token>
```

### Mark All as Read
```http
POST /api/v1/notifications/read-all
Authorization: Bearer <token>
```

### Delete Notification
```http
DELETE /api/v1/notifications/:id
Authorization: Bearer <token>
```

### Create Notification (Admin/System)
```http
POST /api/v1/notifications
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "string",
  "type": "info" | "success" | "warning" | "error",
  "title": "string",
  "message": "string",
  "link": "string (optional)"
}
```

## Frontend Usage

### Hook Usage
```typescript
import { useNotifications } from '@/hooks/useNotifications';

const {
  notifications,      // Notification[]
  isLoading,          // boolean
  unreadCount,        // number
  isConnected,        // boolean (SSE connection status)
  markAsRead,         // UseMutationResult
  markAllRead,        // UseMutationResult
  deleteNotification, // UseMutationResult
} = useNotifications();
```

### SSE Client Usage
```typescript
import { SSEClient, createNotificationSSEClient } from '@/lib/sse-client';

const client = createNotificationSSEClient(
  token,
  (data) => console.log('Notification:', data),
  (error) => console.error('Error:', error)
);

client.connect();
// Later: client.close();
```

## Backend Usage

### Service Container
```go
// Get notification service
notificationService := serviceContainer.NotificationService()

// Create notification
notification, err := notificationService.Create(
    ctx,
    "user-123",
    services.NotificationTypeInfo,
    "Title",
    "Message",
    &link, // optional
)

// List notifications
notifications, err := notificationService.List(
    ctx,
    "user-123",
    false, // unreadOnly
    50,    // limit
)

// Mark as read
err := notificationService.MarkAsRead(ctx, "user-123", "notif-id")

// Mark all as read
err := notificationService.MarkAllAsRead(ctx, "user-123")
```

## Event Types

### notification
New notification created
```json
{
  "type": "notification",
  "notification": { /* Notification object */ },
  "user_id": "user-123",
  "timestamp": 1706788800
}
```

### read
Notification marked as read
```json
{
  "type": "read",
  "notification": { "id": "notif-id", "read_at": "..." },
  "user_id": "user-123",
  "timestamp": 1706788800
}
```

### read_all
All notifications marked as read
```json
{
  "type": "read_all",
  "user_id": "user-123",
  "timestamp": 1706788800
}
```

### delete
Notification deleted
```json
{
  "type": "delete",
  "notification": { "id": "notif-id" },
  "user_id": "user-123",
  "timestamp": 1706788800
}
```

## Configuration

### Environment Variables
```bash
# Backend
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://...

# Frontend
VITE_API_URL=http://localhost:4000
```

## Connection Settings

### Reconnection
- **Initial delay**: 1 second
- **Max delay**: 30 seconds
- **Max attempts**: 10
- **Strategy**: Exponential backoff

### Keep-Alive
- **Interval**: 30 seconds
- **Event type**: `ping`

## Common Patterns

### React Component
```typescript
function NotificationCenter() {
  const { notifications, unreadCount, markAsRead } = useNotifications();

  return (
    <div>
      <Badge count={unreadCount} />
      {notifications.map(n => (
        <NotificationCard
          key={n.id}
          notification={n}
          onRead={() => markAsRead.mutate(n.id)}
        />
      ))}
    </div>
  );
}
```

### System Notification
```go
// In a service/handler
func (s *Service) notifyUserOfChange(ctx context.Context, userID, itemID string) error {
    link := fmt.Sprintf("/items/%s", itemID)
    _, err := s.notificationService.Create(
        ctx,
        userID,
        services.NotificationTypeInfo,
        "Item Updated",
        "Your item has been modified",
        &link,
    )
    return err
}
```

## Testing Commands

### Test SSE Stream
```bash
# With curl
curl -N "http://localhost:4000/api/v1/notifications/stream?token=$TOKEN"

# With EventSource (browser console)
const es = new EventSource('/api/v1/notifications/stream?token=YOUR_TOKEN');
es.onmessage = e => console.log(JSON.parse(e.data));
```

### Create Test Notification
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

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not receiving events | Check Redis connection, verify user_id |
| Connection drops | Check firewall, increase ping interval |
| Cache not updating | Verify queryClient configuration |
| Auth errors | Check token validity, query parameter format |

## Performance Tips

1. **Limit notifications**: Use pagination and cleanup
2. **Index frequently**: Ensure DB indexes on `user_id`, `created_at`
3. **Buffer size**: Adjust channel buffer if events are dropped
4. **Connection pooling**: Redis client manages this automatically
5. **Horizontal scaling**: Redis pub/sub enables multi-instance deployment
