# WebSocket Real-time Updates - Quick Start Guide

## Overview

This guide shows you how to enable real-time updates in your React components using the newly implemented WebSocket NATS event propagation system.

## 5-Minute Integration

### Step 1: Import the Hook

```typescript
import { useRealtimeUpdates } from '@/hooks';
```

### Step 2: Add to Your Component

```typescript
export function ProjectDashboard({ projectId }: { projectId: string }) {
  // Enable real-time updates - that's it!
  useRealtimeUpdates(projectId);

  // Your existing component code...
  return <div>...</div>;
}
```

### Step 3: Enjoy Real-time Updates

Your component will now automatically:
- ✅ Update when items are created, updated, or deleted
- ✅ Update when links are created or deleted
- ✅ Update when specifications are created or updated
- ✅ Show toast notifications for important events
- ✅ Reconnect automatically if connection is lost

## What Events Are Supported?

### From Go Backend
- `item.created` - New item created
- `item.updated` - Item modified
- `item.deleted` - Item removed
- `link.created` - New link created
- `link.deleted` - Link removed
- `project.updated` - Project modified

### From Python Backend
- `spec.created` - Specification created
- `spec.updated` - Specification modified
- `ai.analysis.complete` - AI analysis finished
- `execution.completed` - Test execution completed
- `execution.failed` - Test execution failed
- `workflow.completed` - Workflow completed

## Advanced Usage

### Custom Event Handling

```typescript
import { useRealtimeEvent } from '@/hooks';

export function SpecificationView() {
  // Listen for specific events
  useRealtimeEvent('ai.analysis.complete', (event) => {
    console.log('AI analysis finished:', event);
    // Custom handling here
  });

  return <div>...</div>;
}
```

### Listen to All Events

```typescript
import { useRealtime } from '@/hooks';

export function Dashboard({ projectId }: { projectId: string }) {
  const { isConnected } = useRealtime({
    projectId,
    onEvent: (event) => {
      console.log('Received event:', event);
    },
    enableToasts: true,
  });

  return (
    <div>
      {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
    </div>
  );
}
```

### Manual Control

```typescript
import { realtimeClient } from '@/lib/websocket';

// Connect manually
const token = 'your-auth-token';
realtimeClient.connect(token, 'project-123');

// Subscribe to events
const unsubscribe = realtimeClient.on('item.created', (event) => {
  console.log('Item created:', event);
});

// Later: unsubscribe
unsubscribe();

// Disconnect when done
realtimeClient.disconnect();
```

## Configuration

### Update Auth Token Source

Edit `/frontend/apps/web/src/hooks/useRealtime.ts`:

```typescript
// Replace this line:
const token = localStorage.getItem('auth_token') || '';

// With your actual auth system:
const token = useAuthStore(state => state.token);
// or
const { token } = useAuth();
```

### Customize Toast Notifications

Edit the event handlers in `useRealtimeUpdates`:

```typescript
realtimeClient.on('item.created', (event) => {
  queryClient.invalidateQueries({ queryKey: ['items', projectId] });

  // Customize toast
  toast.success(`New ${event.data.type}: ${event.data.title}`, {
    duration: 4000,
    action: {
      label: 'View',
      onClick: () => navigate(`/items/${event.entity_id}`),
    },
  });
});
```

## Testing

### Run Integration Tests

```bash
cd backend
go test ./tests/integration/websocket_nats_test.go -v
```

### Run E2E Tests

```bash
cd frontend/apps/web
bun run test:e2e e2e/realtime-updates.spec.ts
```

### Manual Testing

1. Open your app in two browser windows
2. Make a change in one window (create/update item)
3. Watch it appear in the other window in real-time!

## Monitoring

### Check Connection Status

In browser console:
```javascript
realtimeClient.getStatus()  // "connected" | "connecting" | "disconnected"
realtimeClient.isConnected()  // true | false
```

### Backend Statistics

```bash
curl http://localhost:8080/api/v1/ws/stats
```

Response:
```json
{
  "total_clients": 5,
  "projects": 2,
  "project_counts": {
    "project-a": 3,
    "project-b": 2
  }
}
```

## Troubleshooting

### Events Not Appearing

1. **Check connection status:**
   ```javascript
   realtimeClient.isConnected()  // Should be true
   ```

2. **Verify auth token:**
   ```javascript
   localStorage.getItem('auth_token')  // Should exist
   ```

3. **Check project ID:**
   - Ensure `projectId` matches the event's `project_id`

4. **Check browser console:**
   - Look for WebSocket errors or authentication failures

### Connection Keeps Dropping

1. Check network connectivity
2. Verify backend is running
3. Check for firewall/proxy issues
4. Increase ping interval in `websocket.ts` if needed

### Not Receiving Python Events

1. Verify Python backend is publishing to NATS
2. Check NATS subject format: `tracertm.bridge.python.{project_id}.{event_type}`
3. Check Go backend logs for subscription errors

## Performance Tips

### Disable Toasts in Production

```typescript
useRealtimeUpdates(projectId);  // Toasts disabled by default
```

### Only Subscribe to Needed Events

```typescript
// Instead of useRealtimeUpdates (all events)
// Subscribe to specific events:
useRealtimeEvent('item.created', handleItemCreated);
useRealtimeEvent('item.updated', handleItemUpdated);
```

### Debounce High-Frequency Updates

```typescript
import { debounce } from 'lodash';

const handleUpdate = debounce((event) => {
  queryClient.invalidateQueries(['items']);
}, 1000);

useRealtimeEvent('item.updated', handleUpdate);
```

## Next Steps

- Read full documentation: `/docs/integration/websocket_realtime.md`
- Check implementation details: `WEBSOCKET_NATS_IMPLEMENTATION.md`
- Explore examples in E2E tests: `/frontend/apps/web/e2e/realtime-updates.spec.ts`

## Common Patterns

### Dashboard with Real-time Updates

```typescript
export function Dashboard({ projectId }: { projectId: string }) {
  useRealtimeUpdates(projectId);

  const { data: items } = useQuery({
    queryKey: ['items', projectId],
    queryFn: () => fetchItems(projectId),
  });

  return <ItemList items={items} />;
}
```

### Item Detail with Real-time Updates

```typescript
export function ItemDetail({ itemId }: { itemId: string }) {
  const { data: item } = useQuery({
    queryKey: ['item', itemId],
    queryFn: () => fetchItem(itemId),
  });

  // Subscribe to item updates
  useRealtimeEvent('item.updated', (event) => {
    if (event.entity_id === itemId) {
      queryClient.invalidateQueries(['item', itemId]);
    }
  });

  return <ItemView item={item} />;
}
```

### Specification with AI Analysis

```typescript
export function SpecificationView({ specId }: { specId: string }) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useRealtimeEvent('ai.analysis.complete', (event) => {
    if (event.data.spec_id === specId) {
      setIsAnalyzing(false);
      queryClient.invalidateQueries(['specification', specId]);
      toast.success('AI analysis complete!');
    }
  });

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // Trigger AI analysis via API
  };

  return (
    <div>
      <button onClick={handleAnalyze} disabled={isAnalyzing}>
        {isAnalyzing ? 'Analyzing...' : 'Analyze'}
      </button>
    </div>
  );
}
```

## Support

For issues or questions:
- Check `/docs/integration/websocket_realtime.md`
- Review backend logs for WebSocket events
- Check browser console for connection errors
- Test with integration/E2E tests
