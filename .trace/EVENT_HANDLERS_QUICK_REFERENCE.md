# Event Handlers Quick Reference

**Location**: `/src/tracertm/api/main.py` (lines 411-560)

---

## Event Handler Summary

| Event Type | Handler | Caches Invalidated | Workflow Triggers |
|------------|---------|-------------------|-------------------|
| `item.created` | `handle_item_created` | items, graph, project | Requirement AI analysis |
| `item.updated` | `handle_item_updated` | items, graph, impact, project | None |
| `item.deleted` | `handle_item_deleted` | items, graph, links, project | None |
| `link.created` | `handle_link_created` | links, graph, ancestors, descendants, impact | None |
| `link.deleted` | `handle_link_deleted` | links, graph, ancestors, descendants, impact | None |
| `project.updated` | `handle_project_updated` | All project caches, projects list | None |
| `project.deleted` | `handle_project_deleted` | All project caches, projects list | None |

---

## Usage Examples

### Adding a New Event Handler

```python
# 1. Define the handler function
async def handle_my_event(event: dict) -> None:
    """Handle my.event events from NATS."""
    entity_id = event.get('entity_id')
    project_id = event.get('project_id')

    logger.info(f"Received my.event: {entity_id}")

    # Invalidate caches
    if project_id:
        try:
            await cache_service.clear_prefix(f"mycache:{project_id}")
            logger.debug(f"Invalidated caches for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")

# 2. Subscribe to the event
await event_bus.subscribe(EventBus.EVENT_MY_EVENT, handle_my_event)
```

### Testing Event Handlers

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_my_event_handler():
    """Test my event handler."""
    mock_cache = AsyncMock()

    # Create handler with mock
    async def handle_my_event(event: dict):
        project_id = event.get('project_id')
        if project_id:
            await mock_cache.clear_prefix(f"mycache:{project_id}")

    # Test
    await handle_my_event({'project_id': 'test-123'})

    # Verify
    mock_cache.clear_prefix.assert_called_once_with("mycache:test-123")
```

---

## Cache Invalidation Patterns

### Pattern 1: Item Changes
```python
# Items affect: item caches, graph, project summary
await cache_service.clear_prefix(f"items:{project_id}")
await cache_service.clear_prefix(f"graph:{project_id}")
await cache_service.invalidate("project", project_id=project_id)
```

### Pattern 2: Link Changes
```python
# Links affect: graph traversal, impact analysis
await cache_service.clear_prefix(f"links:{project_id}")
await cache_service.clear_prefix(f"graph:{project_id}")
await cache_service.clear_prefix(f"ancestors:{project_id}")
await cache_service.clear_prefix(f"descendants:{project_id}")
await cache_service.clear_prefix(f"impact:{project_id}")
```

### Pattern 3: Project Changes
```python
# Use comprehensive invalidation
await cache_service.invalidate_project(project_id)
await cache_service.clear_prefix("projects")
```

---

## Error Handling Best Practices

### Always Wrap Cache Operations
```python
try:
    await cache_service.clear_prefix(f"items:{project_id}")
except Exception as e:
    logger.error(f"Failed to invalidate cache: {e}")
    # Continue processing - don't re-raise
```

### Validate Input Data
```python
if not project_id:
    logger.warning("Event missing project_id, skipping cache invalidation")
    return
```

### Log at Appropriate Levels
```python
logger.info(f"Received {event_type} event: {entity_id}")  # Important events
logger.debug(f"Invalidated caches for project {project_id}")  # Details
logger.error(f"Failed to process event: {e}")  # Errors
```

---

## Common Issues & Solutions

### Issue: Cache Not Invalidating

**Problem**: Changes in Go backend not reflected in Python API

**Solution**:
1. Check NATS connection: `docker logs tracertm-nats`
2. Verify event subscription: Check startup logs for "Subscribed to..."
3. Check Redis connection: Test with `redis-cli PING`
4. Enable debug logging: `LOG_LEVEL=DEBUG`

### Issue: Events Not Being Received

**Problem**: Event handlers not being triggered

**Solution**:
1. Verify NATS configuration in `.env`:
   ```bash
   NATS_URL=nats://localhost:4222
   NATS_CREDS_PATH=/path/to/nats.creds
   ```
2. Check Go backend is publishing events
3. Verify subject patterns match: `tracertm.bridge.go.*.{event_type}`
4. Check durable subscriber status

### Issue: Performance Degradation

**Problem**: Event processing slowing down system

**Solution**:
1. Use prefix-based invalidation instead of iterating keys
2. Batch cache operations where possible
3. Consider async fire-and-forget for non-critical invalidations
4. Monitor Redis memory usage

---

## Monitoring

### Key Metrics to Track

```python
# Log event processing time
start = time.time()
await handle_item_created(event)
logger.info(f"Event processed in {time.time() - start:.3f}s")

# Track cache hit rates
stats = await cache_service.get_stats()
logger.info(f"Cache hit rate: {stats.hit_rate:.2f}%")

# Monitor event queue depth
health = await event_bus.health_check()
logger.info(f"NATS status: {health}")
```

### Logging Examples

**Successful Event Processing**:
```
INFO: Received item.created event: abc-123 (type: requirement, project: proj-456)
DEBUG: Invalidated caches for project proj-456 after item creation
INFO: Requirement created: abc-123, ready for AI analysis workflow
```

**Cache Error (Graceful Degradation)**:
```
INFO: Received link.created event: link-789 (project: proj-456)
ERROR: Failed to invalidate cache for link.created: Redis connection timeout
```

**NATS Initialization**:
```
INFO: NATS bridge initialized successfully at nats://localhost:4222
INFO: Subscribed to item.created events from Go backend
INFO: Subscribed to link.created events from Go backend
```

---

## Testing Checklist

- [ ] Unit tests pass for all handlers
- [ ] Cache invalidation verified
- [ ] Error handling tested
- [ ] Missing data handled gracefully
- [ ] Event subscriptions registered
- [ ] Logs readable and informative
- [ ] Performance acceptable (<100ms per event)
- [ ] Integration tests pass

---

## Quick Commands

### Run Event Handler Tests
```bash
pytest tests/unit/api/test_event_handlers.py -v
```

### Check Event Processing in Logs
```bash
docker logs tracertm-python | grep "Received.*event"
```

### Verify Cache Invalidation
```bash
docker exec -it tracertm-redis redis-cli KEYS "tracertm:*"
```

### Monitor NATS Messages
```bash
nats sub "tracertm.bridge.go.>"
```

---

## File Locations

- **Main Implementation**: `/src/tracertm/api/main.py:411-560`
- **Unit Tests**: `/tests/unit/api/test_event_handlers.py`
- **Event Bus**: `/src/tracertm/infrastructure/event_bus.py`
- **Cache Service**: `/src/tracertm/services/cache_service.py`

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Status**: Production Ready
