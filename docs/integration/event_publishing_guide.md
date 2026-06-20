# Event Publishing Guide

This guide covers how to publish events across TraceRTM's Go and Python backends using NATS JetStream.

## Overview

TraceRTM uses NATS JetStream for reliable, bidirectional event communication between the Go and Python backends. Events are published whenever data changes, enabling real-time updates and cross-backend coordination.

## Event Flow Architecture

```
┌─────────────┐        NATS JetStream         ┌──────────────┐
│ Go Backend  │ ──────────────────────────▶   │ Python       │
│ (Items,     │   tracertm.bridge.go.*.event  │ (Subscribers)│
│  Links,     │                                │              │
│  Projects)  │                                │              │
└─────────────┘                                └──────────────┘
       ▲                                              │
       │                                              │
       │          tracertm.bridge.python.*.event     │
       │        ◀─────────────────────────────────────┘
       │
   ┌──────────────┐
   │ Python Backend│
   │ (Specs, AI,   │
   │  Execution)   │
   └──────────────┘
```

## Subject Naming Convention

All events follow the pattern:
```
tracertm.bridge.{source}.{project_id}.{event_type}
```

- **source**: `go` or `python`
- **project_id**: UUID of the project (or `*` for wildcard subscriptions)
- **event_type**: Specific event like `item.created`, `spec.updated`, etc.

## Event Types

### Go Backend Events

Published when items, links, or projects change:

- `item.created` - New item created
- `item.updated` - Item modified
- `item.deleted` - Item removed
- `link.created` - New link created
- `link.deleted` - Link removed
- `project.created` - New project created
- `project.updated` - Project modified
- `project.deleted` - Project removed

### Python Backend Events

Published for specifications, AI operations, and test execution:

- `spec.created` - New specification (ADR/Contract/Feature/Scenario) created
- `spec.updated` - Specification modified
- `spec.deleted` - Specification removed
- `ai.analysis.complete` - AI analysis finished
- `execution.completed` - Test execution completed successfully
- `execution.failed` - Test execution failed
- `workflow.completed` - Workflow execution completed

## Publishing Events

### From Go Handlers

Use the `PythonBridge` for cross-backend events:

```go
import (
    "github.com/kooshapari/tracertm-backend/internal/nats"
)

// In handler method
func (h *ItemHandler) CreateItem(c echo.Context) error {
    // ... create item logic ...

    // Publish event to Python backend
    if h.publisher != nil {
        eventData := map[string]interface{}{
            "id":       item.ID.String(),
            "title":    item.Title,
            "type":     item.Type,
            "status":   item.Status,
        }

        go nats.SafePublish(
            h.pythonBridge,
            "item.created",
            item.ProjectID.String(),
            item.ID.String(),
            "item",
            eventData,
        )
    }

    return c.JSON(http.StatusCreated, item)
}
```

**Best Practices:**

1. Use `SafePublish` or `SafePublishWithRetry` from `publisher_utils.go`
2. Publish asynchronously with `go` to avoid blocking the request
3. Never fail the request if event publishing fails
4. Log publishing errors for debugging

### From Python Routers

Use the `EventBus` dependency:

```python
from fastapi import Depends
from tracertm.infrastructure.event_bus import EventBus
from tracertm.infrastructure.event_publisher_utils import safe_publish
from tracertm.api.deps import get_event_bus

@router.post("/specifications/adrs", response_model=ADRResponse)
async def create_adr(
    adr: ADRCreate,
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
):
    # ... create ADR logic ...

    # Publish NATS event
    if event_bus:
        await safe_publish(
            event_bus,
            EventBus.EVENT_SPEC_CREATED,
            adr.project_id,
            str(created_adr.id),
            "adr",
            {
                "id": str(created_adr.id),
                "title": created_adr.title,
                "type": "adr",
                "status": created_adr.status,
            },
        )

    return created_adr
```

**Best Practices:**

1. Use `safe_publish` or `safe_publish_with_retry` from `event_publisher_utils.py`
2. Always check `if event_bus` to handle cases where NATS is unavailable
3. Use event type constants from `EventBus` class
4. Include minimal but meaningful event data

## Event Payload Structure

All events follow this JSON structure:

```json
{
  "type": "item.created",
  "project_id": "uuid-here",
  "entity_id": "entity-uuid-here",
  "entity_type": "item",
  "data": {
    "id": "entity-uuid-here",
    "title": "Example Item",
    "type": "requirement",
    "status": "active"
  },
  "source": "go"
}
```

**Fields:**

- `type`: Event type (matches subject's event_type component)
- `project_id`: UUID of the project
- `entity_id`: UUID of the entity that changed
- `entity_type`: Type of entity (item, link, project, adr, contract, etc.)
- `data`: Event-specific payload (keep lightweight)
- `source`: Origin backend ("go" or "python")

## Error Handling

### Go Error Handling

```go
import "github.com/kooshapari/tracertm-backend/internal/nats"

// Fire-and-forget (recommended for most cases)
nats.SafePublish(bridge, eventType, projectID, entityID, entityType, data)

// With retry logic
nats.SafePublishWithRetry(bridge, eventType, projectID, entityID, entityType, data, 3)

// Synchronous with error propagation (rare use case)
err := nats.PublishWithRetry(bridge, eventType, projectID, entityID, entityType, data, 3)
if err != nil {
    log.Printf("Critical: failed to publish event: %v", err)
    // Handle error appropriately
}
```

### Python Error Handling

```python
from tracertm.infrastructure.event_publisher_utils import (
    safe_publish,
    safe_publish_with_retry,
    publish_with_retry,
)

# Fire-and-forget (recommended for most cases)
await safe_publish(event_bus, event_type, project_id, entity_id, entity_type, data)

# With retry logic
await safe_publish_with_retry(event_bus, event_type, project_id, entity_id, entity_type, data, max_retries=3)

# Synchronous with error propagation (rare use case)
try:
    await publish_with_retry(event_bus, event_type, project_id, entity_id, entity_type, data, max_retries=3)
except Exception as e:
    logger.error(f"Critical: failed to publish event: {e}")
    # Handle error appropriately
```

## Testing Event Flow

### Integration Test Example (Python)

```python
import pytest
from tracertm.infrastructure.nats_client import NATSClient
from tracertm.infrastructure.event_bus import EventBus

@pytest.mark.asyncio
async def test_spec_create_publishes_event():
    """Verify that creating a specification publishes a NATS event."""
    # Setup NATS subscriber
    received_events = []

    async def handler(event):
        received_events.append(event)

    nats_client = NATSClient(url="nats://localhost:4222")
    await nats_client.connect()
    event_bus = EventBus(nats_client)

    await event_bus.subscribe("spec.created", handler)

    # Create specification via API
    response = await client.post("/api/v1/specifications/adrs", json={
        "project_id": "test-project-id",
        "title": "Test ADR",
        "context": "Test context",
        "decision": "Test decision",
        "consequences": "Test consequences",
    })

    # Wait for event
    await asyncio.sleep(1)

    # Verify event was received
    assert len(received_events) == 1
    assert received_events[0]["type"] == "spec.created"
    assert received_events[0]["entity_type"] == "adr"
```

### Integration Test Example (Go)

```go
func TestItemCreatePublishesEvent(t *testing.T) {
    // Setup Python bridge and subscriber
    eventChan := make(chan *nats.BridgeEvent, 10)

    bridge := setupPythonBridge(t)
    err := bridge.SubscribeToEventType("item.created", func(event *nats.BridgeEvent) {
        eventChan <- event
    })
    require.NoError(t, err)

    // Create item via API
    item := createTestItem(t, "test-project-id")

    // Wait for event
    select {
    case event := <-eventChan:
        assert.Equal(t, "item", event.EntityType)
        assert.Equal(t, item.ID, event.EntityID)
    case <-time.After(5 * time.Second):
        t.Fatal("Event not received within timeout")
    }
}
```

## Debugging

### Check NATS Connection

```bash
# Check if NATS is running
nats-server --version

# Monitor NATS stream
nats stream info TRACERTM_BRIDGE

# View messages in stream
nats stream view TRACERTM_BRIDGE
```

### View Events in Real-Time

```bash
# Subscribe to all Go events
nats sub "tracertm.bridge.go.>"

# Subscribe to Python events
nats sub "tracertm.bridge.python.>"

# Subscribe to specific event type
nats sub "tracertm.bridge.*.*.item.created"
```

### Common Issues

**Events not being published:**
- Check if NATS connection is established
- Verify `event_bus` or `pythonBridge` is not nil
- Check application logs for publishing errors

**Events not being received:**
- Verify subscriber pattern matches subject structure
- Check durable consumer name for conflicts
- Ensure JetStream stream exists

**Performance issues:**
- Use fire-and-forget publishing (SafePublish)
- Avoid synchronous publishing in request handlers
- Keep event payloads lightweight

## Configuration

### Environment Variables

**Go Backend:**
```bash
NATS_URL=nats://localhost:4222
NATS_CREDS_PATH=/path/to/creds.jwt  # Optional for authentication
```

**Python Backend:**
```bash
NATS_URL=nats://localhost:4222
NATS_CREDS_PATH=/path/to/creds.jwt  # Optional for authentication
```

### Production Considerations

1. **Use JetStream persistence** for guaranteed delivery
2. **Enable TLS** for secure communication
3. **Set up monitoring** for event throughput and errors
4. **Configure retention policies** based on event volume
5. **Use durable subscriptions** to prevent message loss
6. **Implement health checks** for NATS connectivity

## Summary

- **Always use safe publishing utilities** to prevent request failures
- **Keep event payloads lightweight** for performance
- **Use event type constants** for consistency
- **Test event flows** in integration tests
- **Monitor event delivery** in production
- **Handle NATS unavailability gracefully**
