# NATS Event Publishing Quick Reference

Quick reference for publishing events in TraceRTM.

## Go Backend

### Import
```go
import "github.com/kooshapari/tracertm-backend/internal/nats"
```

### Publish Event (Fire-and-Forget)
```go
nats.SafePublish(
    h.pythonBridge,
    "item.created",           // event type
    projectID,                // project UUID
    entityID,                 // entity UUID
    "item",                   // entity type
    map[string]interface{}{   // event data
        "id": entityID,
        "title": "Example",
    },
)
```

### Publish Event (With Retry)
```go
nats.SafePublishWithRetry(
    h.pythonBridge,
    "item.updated",
    projectID,
    entityID,
    "item",
    eventData,
    3, // max retries
)
```

### Event Types
```go
const (
    EventItemCreated    = "item.created"
    EventItemUpdated    = "item.updated"
    EventItemDeleted    = "item.deleted"
    EventLinkCreated    = "link.created"
    EventLinkDeleted    = "link.deleted"
    EventProjectCreated = "project.created"
    EventProjectUpdated = "project.updated"
    EventProjectDeleted = "project.deleted"
)
```

## Python Backend

### Import
```python
from tracertm.infrastructure.event_bus import EventBus
from tracertm.infrastructure.event_publisher_utils import safe_publish
from tracertm.api.deps import get_event_bus
from fastapi import Depends
```

### Publish Event (Fire-and-Forget)
```python
if event_bus:
    await safe_publish(
        event_bus,
        EventBus.EVENT_SPEC_CREATED,  # event type constant
        project_id,                    # project UUID string
        entity_id,                     # entity UUID string
        "adr",                         # entity type
        {                              # event data dict
            "id": entity_id,
            "title": "Example",
        },
    )
```

### Publish Event (With Retry)
```python
await safe_publish_with_retry(
    event_bus,
    EventBus.EVENT_SPEC_UPDATED,
    project_id,
    entity_id,
    "contract",
    event_data,
    max_retries=3,
)
```

### Add Dependency to Endpoint
```python
@router.post("/specifications/adrs")
async def create_adr(
    adr: ADRCreate,
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),  # Add this
):
    # ... endpoint logic ...
```

### Event Type Constants
```python
EventBus.EVENT_SPEC_CREATED           # "spec.created"
EventBus.EVENT_SPEC_UPDATED           # "spec.updated"
EventBus.EVENT_SPEC_DELETED           # "spec.deleted"
EventBus.EVENT_AI_ANALYSIS_COMPLETE   # "ai.analysis.complete"
EventBus.EVENT_EXECUTION_COMPLETED    # "execution.completed"
EventBus.EVENT_EXECUTION_FAILED       # "execution.failed"
EventBus.EVENT_WORKFLOW_COMPLETED     # "workflow.completed"
```

## Best Practices

### ✅ DO
- Use `SafePublish` or `safe_publish` for fire-and-forget
- Publish events asynchronously (Go: use `go`)
- Always check if `event_bus` or `pythonBridge` is not nil
- Keep event payloads lightweight
- Log publishing errors
- Use event type constants

### ❌ DON'T
- Don't fail requests if event publishing fails
- Don't publish synchronously in request handlers
- Don't include large data in event payloads
- Don't use hardcoded event type strings
- Don't block on event publishing

## Subject Pattern

All events follow:
```
tracertm.bridge.{source}.{project_id}.{event_type}
```

Examples:
```
tracertm.bridge.go.abc-123.item.created
tracertm.bridge.python.xyz-789.spec.updated
```

## Event Payload Format

```json
{
  "type": "item.created",
  "project_id": "project-uuid",
  "entity_id": "entity-uuid",
  "entity_type": "item",
  "data": {
    "id": "entity-uuid",
    "title": "Example",
    "custom_field": "value"
  },
  "source": "go"
}
```

## Testing

### Monitor Events (CLI)
```bash
# All events
nats sub "tracertm.bridge.>"

# Go events only
nats sub "tracertm.bridge.go.>"

# Python events only
nats sub "tracertm.bridge.python.>"

# Specific event type
nats sub "tracertm.bridge.*.*.item.created"
```

### Check NATS Status
```bash
# Stream info
nats stream info TRACERTM_BRIDGE

# Consumer list
nats consumer list TRACERTM_BRIDGE

# Health check
nats account info
```

## Common Patterns

### After Create Operation
```python
# Python
created_entity = await service.create_entity(...)

if event_bus:
    await safe_publish(
        event_bus,
        EventBus.EVENT_SPEC_CREATED,
        project_id,
        str(created_entity.id),
        "entity_type",
        {"id": str(created_entity.id), "title": created_entity.title},
    )

return created_entity
```

### After Update Operation
```go
// Go
updatedItem, err := h.queries.UpdateItem(ctx, params)
if err != nil {
    return err
}

nats.SafePublish(
    h.pythonBridge,
    "item.updated",
    updatedItem.ProjectID.String(),
    updatedItem.ID.String(),
    "item",
    updatedItem,
)

return c.JSON(http.StatusOK, updatedItem)
```

### After Delete Operation
```python
# Python
# Get entity before deletion to access project_id
entity = await service.get_entity(entity_id)
if not entity:
    raise HTTPException(status_code=404)

project_id = entity.project_id
await service.delete_entity(entity_id)

if event_bus:
    await safe_publish(
        event_bus,
        EventBus.EVENT_SPEC_DELETED,
        project_id,
        entity_id,
        "entity_type",
        {"id": entity_id},
    )
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Events not published | Check NATS connection, verify bridge/event_bus not nil |
| Events not received | Verify subscriber pattern, check consumer status |
| Slow requests | Use async publishing, avoid blocking on events |
| Missing events | Check retention policy, verify delivery acknowledgments |

## Environment Setup

```bash
# Start NATS locally
nats-server -js

# Set environment variables
export NATS_URL=nats://localhost:4222
export NATS_CREDS_PATH=/path/to/creds.jwt  # Optional
```

## More Information

- Full Guide: `docs/integration/event_publishing_guide.md`
- Implementation Summary: `NATS_EVENT_PUBLISHING_IMPLEMENTATION.md`
- Tests: `tests/integration/test_event_flow.py` (Python)
- Tests: `backend/tests/integration/event_flow_test.go` (Go)
