# Event Flow Diagram

**Phase 1.4: Python Event Handlers**

---

## Event Processing Flow

```
┌─────────────────┐
│   Go Backend    │
│   (Creates      │
│   Item/Link)    │
└────────┬────────┘
         │
         │ Publishes Event
         ▼
┌─────────────────────────────────────┐
│            NATS Server              │
│  Subject: tracertm.bridge.go.       │
│           {project_id}.             │
│           {event_type}              │
└────────┬────────────────────────────┘
         │
         │ Event Subscription
         ▼
┌─────────────────────────────────────┐
│        Python EventBus              │
│   (Receives Event via NATS)         │
└────────┬────────────────────────────┘
         │
         │ Routes to Handler
         ▼
┌─────────────────────────────────────┐
│      Event Handler Function         │
│   • handle_item_created()           │
│   • handle_link_created()           │
│   • etc.                            │
└────┬───────────────────┬────────────┘
     │                   │
     │ Invalidates       │ Triggers
     │ Caches            │ Workflows
     ▼                   ▼
┌──────────────┐  ┌──────────────┐
│ Cache Service│  │   Hatchet    │
│   (Redis)    │  │  Workflows   │
│              │  │  (Future)    │
└──────────────┘  └──────────────┘
```

---

## Event Types & Handlers

### Item Events

```
item.created
    ↓
handle_item_created()
    ↓
┌─────────────────────────────────┐
│ Cache Invalidation              │
├─────────────────────────────────┤
│ • items:{project_id}            │
│ • graph:{project_id}            │
│ • project:{project_id}          │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Workflow Trigger (if requirement│
│ "Ready for AI analysis"         │
└─────────────────────────────────┘
```

```
item.updated
    ↓
handle_item_updated()
    ↓
┌─────────────────────────────────┐
│ Cache Invalidation              │
├─────────────────────────────────┤
│ • items:{project_id}            │
│ • graph:{project_id}            │
│ • impact:{project_id}           │
│ • project:{project_id}          │
└─────────────────────────────────┘
```

```
item.deleted
    ↓
handle_item_deleted()
    ↓
┌─────────────────────────────────┐
│ Cache Invalidation              │
├─────────────────────────────────┤
│ • items:{project_id}            │
│ • graph:{project_id}            │
│ • links:{project_id}            │
│ • project:{project_id}          │
└─────────────────────────────────┘
```

### Link Events

```
link.created / link.deleted
    ↓
handle_link_created() / handle_link_deleted()
    ↓
┌─────────────────────────────────┐
│ Cache Invalidation (Extensive)  │
├─────────────────────────────────┤
│ • links:{project_id}            │
│ • graph:{project_id}            │
│ • ancestors:{project_id}        │
│ • descendants:{project_id}      │
│ • impact:{project_id}           │
└─────────────────────────────────┘
```

### Project Events

```
project.updated / project.deleted
    ↓
handle_project_updated() / handle_project_deleted()
    ↓
┌─────────────────────────────────┐
│ Comprehensive Invalidation      │
├─────────────────────────────────┤
│ • invalidate_project(project_id)│
│   - All project-related caches  │
│ • projects list cache           │
└─────────────────────────────────┘
```

---

## Error Handling Flow

```
Event Received
    ↓
Extract event data
    ↓
┌─────────────────┐
│ Validate Data   │
│ • project_id?   │
│ • entity_id?    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   Try Cache Operations  │
└────┬──────────────┬─────┘
     │              │
  Success         Error
     │              │
     ▼              ▼
┌─────────┐   ┌──────────────┐
│  Log    │   │ Log Error    │
│ Success │   │ Continue     │
│         │   │ Processing   │
└─────────┘   └──────────────┘
     │              │
     └──────┬───────┘
            │
            ▼
    Handler Completes
  (No exceptions raised)
```

---

## Cache Invalidation Strategy

### Why Different Caches for Different Events?

| Cache Type | Invalidated By | Reason |
|------------|---------------|--------|
| `items:{project_id}` | Item events | Item list changed |
| `graph:{project_id}` | Item & Link events | Graph structure changed |
| `links:{project_id}` | Link & Item-delete events | Link list or orphans created |
| `ancestors:{project_id}` | Link events | Traversal path changed |
| `descendants:{project_id}` | Link events | Traversal path changed |
| `impact:{project_id}` | Item-update & Link events | Dependencies changed |
| `project:{project_id}` | Item & Project events | Metadata or summary changed |
| `projects` | Project-update/delete | Project list changed |

### Cache Invalidation Levels

```
┌─────────────────────────────────────┐
│     Level 1: Targeted               │
│   Single cache type/project         │
│   Example: items:{project_id}       │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│     Level 2: Related                │
│   Multiple related cache types      │
│   Example: items + graph + impact   │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│     Level 3: Comprehensive          │
│   All project caches                │
│   Uses: invalidate_project()        │
└─────────────────────────────────────┘
```

---

## Event Data Structure

### Standard Event Format

```json
{
  "event_type": "item.created",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "entity_id": "660e8400-e29b-41d4-a716-446655440000",
  "entity_type": "requirement",
  "source": "go",
  "timestamp": "2026-01-30T12:34:56Z",
  "data": {
    "title": "User Authentication",
    "type": "requirement",
    "status": "active"
  }
}
```

### Handler Data Extraction

```python
# Extract from event
entity_id = event.get('entity_id')      # Required
project_id = event.get('project_id')    # Required for cache ops
entity_type = event.get('entity_type')  # Optional (for filtering)
data = event.get('data', {})            # Optional (payload)
```

---

## Timing Diagram

```
Time →

Go Backend    │  Publishes event (1ms)
              ├──────────────────────────►

NATS          │  Routes event (5ms)
              ├──────────────────────────►

Python        │  Receives event (1ms)
EventBus      ├──────────────────────────►

Event         │  Extracts data (0.1ms)
Handler       │  Invalidates caches (10-50ms)
              │  Logs result (1ms)
              ├──────────────────────────►

Cache         │  Clears Redis keys (10-50ms)
Service       ├──────────────────────────►

Total: 27-108ms (typical: 50ms)
```

---

## Subscription Setup

### Initialization (Startup)

```python
# 1. Connect to NATS
nats_client = NATSClient(url=nats_url, creds_path=nats_creds)
await nats_client.connect()

# 2. Create EventBus
event_bus = EventBus(nats_client)

# 3. Get CacheService
cache_service = get_cache_service()

# 4. Define handlers (closures with access to cache_service)
async def handle_item_created(event: dict) -> None:
    ...

# 5. Subscribe to events
await event_bus.subscribe(EventBus.EVENT_ITEM_CREATED, handle_item_created)

# 6. Store in app state
app.state.event_bus = event_bus
```

### Subject Pattern Matching

```
Published: tracertm.bridge.go.{project_id}.{event_type}
           Example: tracertm.bridge.go.proj-123.item.created

Subscribe: tracertm.bridge.go.*.{event_type}
           Example: tracertm.bridge.go.*.item.created
           Matches:  All projects for this event type

Wildcard:  tracertm.bridge.go.>
           Matches:  All events from Go backend
```

---

## Monitoring & Debugging

### Log Messages

```
[INFO] Received item.created event: abc-123 (type: requirement, project: proj-456)
  ↓ Processing
[DEBUG] Invalidated caches for project proj-456 after item creation
  ↓ Workflow check
[INFO] Requirement created: abc-123, ready for AI analysis workflow
  ↓ Success
```

### Error Scenario

```
[INFO] Received link.created event: link-789 (project: proj-456)
  ↓ Processing
[ERROR] Failed to invalidate cache for link.created: Redis connection timeout
  ↓ Continue (graceful degradation)
Handler completes without exception
```

### Debug Commands

```bash
# View event logs
docker logs tracertm-python | grep "Received.*event"

# Monitor NATS messages
nats sub "tracertm.bridge.go.>"

# Check Redis keys
docker exec tracertm-redis redis-cli KEYS "tracertm:*"

# View cache stats
curl http://localhost:8000/api/v1/cache/stats
```

---

## Performance Optimization

### Parallel Cache Operations

```python
# Sequential (slower)
await cache_service.clear_prefix(f"items:{project_id}")
await cache_service.clear_prefix(f"graph:{project_id}")
await cache_service.clear_prefix(f"links:{project_id}")

# Parallel (faster) - Future enhancement
await asyncio.gather(
    cache_service.clear_prefix(f"items:{project_id}"),
    cache_service.clear_prefix(f"graph:{project_id}"),
    cache_service.clear_prefix(f"links:{project_id}")
)
```

### Batching Strategy

```python
# Current: Process each event individually
for event in events:
    await handle_event(event)

# Future: Batch invalidations
project_ids = {event['project_id'] for event in events}
for project_id in project_ids:
    await cache_service.invalidate_project(project_id)
```

---

## Testing Strategy

### Unit Test Flow

```
Mock Cache Service
    ↓
Create Handler
    ↓
Pass Test Event
    ↓
Verify Cache Calls
    ↓
Assert Call Counts
```

### Integration Test Flow

```
Start Python Backend
    ↓
Start NATS Server
    ↓
Publish Test Event
    ↓
Wait for Processing
    ↓
Verify Cache State
    ↓
Check Logs
```

---

**Last Updated**: 2026-01-30
**Version**: 1.0
