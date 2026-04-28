# NATS Event Bridge Documentation

## Overview

The NATS Event Bridge provides bidirectional event-driven communication between the Go and Python backends in TraceRTM. It uses NATS JetStream for reliable, persistent messaging with durable subscriptions.

## Architecture

### Subject Hierarchy

All bridge events follow a strict subject pattern:

```
tracertm.bridge.{source}.{project_id}.{event_type}
```

**Components:**
- `tracertm.bridge`: Base prefix for all bridge events
- `source`: Event source (`go` or `python`)
- `project_id`: UUID of the project the event relates to
- `event_type`: Specific event type (see Event Types below)

**Examples:**
```
tracertm.bridge.go.550e8400-e29b-41d4-a716-446655440000.item.created
tracertm.bridge.python.550e8400-e29b-41d4-a716-446655440000.spec.created
```

### Stream Configuration

**Stream Name:** `TRACERTM_BRIDGE`

**Configuration:**
- **Subjects:** `tracertm.bridge.>`
- **Retention:** Interest-based (messages deleted when no subscribers)
- **Storage:** File-based (persistent across restarts)
- **Max Age:** 7 days
- **Replicas:** 1

## Event Types

### Go-Originated Events

Events published by the Go backend and consumed by Python:

| Event Type | Description | Entity Type |
|------------|-------------|-------------|
| `item.created` | New item created | `item` |
| `item.updated` | Item updated | `item` |
| `item.deleted` | Item deleted | `item` |
| `link.created` | New traceability link created | `link` |
| `link.deleted` | Link deleted | `link` |
| `project.created` | New project created | `project` |
| `project.updated` | Project updated | `project` |
| `project.deleted` | Project deleted | `project` |

### Python-Originated Events

Events published by the Python backend and consumed by Go:

| Event Type | Description | Entity Type |
|------------|-------------|-------------|
| `spec.created` | New specification created | `specification` |
| `spec.updated` | Specification updated | `specification` |
| `spec.deleted` | Specification deleted | `specification` |
| `ai.analysis.complete` | AI analysis completed | `analysis` |
| `execution.completed` | Test execution completed | `execution` |
| `execution.failed` | Test execution failed | `execution` |
| `workflow.completed` | Workflow execution completed | `workflow` |

## Event Payload Structure

All events follow a standard JSON structure:

```json
{
  "type": "item.created",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "entity_id": "660e8400-e29b-41d4-a716-446655440001",
  "entity_type": "item",
  "source": "go",
  "data": {
    "title": "New Item",
    "status": "open",
    "custom_field": "value"
  }
}
```

### Field Descriptions

- **type** (string): Event type identifier
- **project_id** (string): UUID of the associated project
- **entity_id** (string): UUID of the entity that triggered the event
- **entity_type** (string): Type of entity (item, link, specification, etc.)
- **source** (string): Backend that published the event ("go" or "python")
- **data** (object): Event-specific payload data

## Pydantic Schemas

### Python Event Schemas

```python
from pydantic import BaseModel, Field
from typing import Any, Dict
from datetime import datetime

class BridgeEvent(BaseModel):
    """Base bridge event schema."""
    type: str = Field(..., description="Event type")
    project_id: str = Field(..., description="Project UUID")
    entity_id: str = Field(..., description="Entity UUID")
    entity_type: str = Field(..., description="Entity type")
    source: str = Field(..., description="Event source (go/python)")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")

class ItemCreatedEvent(BridgeEvent):
    """Item created event."""
    type: str = "item.created"
    entity_type: str = "item"
    data: Dict[str, Any]  # Contains item details

class SpecCreatedEvent(BridgeEvent):
    """Specification created event."""
    type: str = "spec.created"
    entity_type: str = "specification"
    data: Dict[str, Any]  # Contains spec details
```

### Go Event Structs

```go
// BridgeEvent represents a cross-backend event
type BridgeEvent struct {
    Type       string                 `json:"type"`
    ProjectID  string                 `json:"project_id"`
    EntityID   string                 `json:"entity_id"`
    EntityType string                 `json:"entity_type"`
    Data       map[string]interface{} `json:"data"`
    Source     string                 `json:"source"`
}
```

## Usage Examples

### Python: Publishing Events

```python
from tracertm.infrastructure import EventBus

# Get event bus from app state
event_bus = app.state.event_bus

# Publish specification created event
await event_bus.publish(
    event_type=EventBus.EVENT_SPEC_CREATED,
    project_id="550e8400-e29b-41d4-a716-446655440000",
    entity_id="660e8400-e29b-41d4-a716-446655440001",
    entity_type="specification",
    data={
        "title": "New Specification",
        "type": "feature",
        "status": "draft",
    }
)
```

### Python: Subscribing to Events

```python
from tracertm.infrastructure import EventBus

# Define handler
async def handle_item_created(event: dict) -> None:
    print(f"Item created: {event['entity_id']}")
    # Process event...

# Subscribe to event type
await event_bus.subscribe(
    event_type=EventBus.EVENT_ITEM_CREATED,
    handler=handle_item_created
)
```

### Go: Publishing Events

```go
import (
    "github.com/kooshapari/tracertm-backend/internal/nats"
)

// Initialize Python bridge
bridge, err := nats.NewPythonBridge(natsConn)
if err != nil {
    log.Fatal(err)
}

// Publish item created event
err = bridge.PublishItemEvent(
    nats.SubjectItemCreated,
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    map[string]interface{}{
        "title": "New Item",
        "status": "open",
    },
)
```

### Go: Subscribing to Events

```go
// Subscribe to Python events
err = bridge.SubscribeToPythonEvents(func(event *nats.BridgeEvent) {
    log.Printf("Received event: %s for %s", event.Type, event.EntityID)
    // Process event...
})

// Subscribe to specific event type
err = bridge.SubscribeToEventType(
    nats.SubjectSpecCreated,
    func(event *nats.BridgeEvent) {
        log.Printf("Spec created: %s", event.EntityID)
        // Process event...
    },
)
```

## Durable Subscriptions

All subscriptions are **durable**, meaning:

1. **Survive restarts**: Consumer state persists across application restarts
2. **Guaranteed delivery**: Messages are not lost if subscriber is temporarily down
3. **At-least-once delivery**: Messages acknowledged after processing
4. **Unique consumer names**: Each subscription has a unique durable name

### Python Durable Names

- All events from Go: `python-all-go-events`
- Specific event type: `python-{event_type}` (e.g., `python-item-created`)
- Project-specific: `python-{project_id}-{event_type}`

### Go Durable Names

- All events from Python: `go-python-events`
- Specific event type: `go-{event_type}` (e.g., `go-spec-created`)

## Retry and Error Handling

### Automatic Retries

NATS JetStream provides automatic retry capabilities:

1. **NAK (Negative Acknowledge)**: Requeue message for retry
2. **Exponential Backoff**: Configurable delay between retries
3. **Max Delivery**: Limit number of retry attempts

### Error Handling Strategy

**Python:**
```python
async def handle_event(event: dict) -> None:
    try:
        # Process event
        result = await process_event(event)
        # Message auto-acknowledged on success
    except RetryableError as e:
        # NAK message to retry
        logger.warning(f"Retryable error: {e}")
        raise  # Will trigger NAK
    except PermanentError as e:
        # ACK to avoid infinite retries
        logger.error(f"Permanent error: {e}")
        # Don't raise - message will be ACKed
```

**Go:**
```go
func handleEvent(event *nats.BridgeEvent) {
    if err := processEvent(event); err != nil {
        if isRetryable(err) {
            log.Printf("Retryable error: %v", err)
            // Don't ACK - message will retry
            return
        }
        log.Printf("Permanent error: %v", err)
    }
    // Message auto-acknowledged
}
```

### Dead Letter Queue (DLQ)

For messages that exceed max delivery attempts:

1. Configure max delivery count (e.g., 5 attempts)
2. Route to DLQ stream for manual inspection
3. Alert on DLQ messages

## Configuration

### Environment Variables

**Python:**
```bash
# Required
NATS_URL=nats://localhost:4222
NATS_BRIDGE_ENABLED=true

# Optional
NATS_CREDS_PATH=/path/to/nats.creds  # For production auth
```

**Go:**
```bash
# Required
NATS_URL=nats://localhost:4222

# Optional
NATS_CREDS_PATH=/path/to/nats.creds
NATS_JWT=...  # For cloud NATS
NATS_NKEY_SEED=...  # For cloud NATS
```

### Local Development

For local development without authentication:

```bash
# Start NATS server with JetStream
docker run -p 4222:4222 nats:latest -js

# Or using nats-server binary
nats-server -js
```

### Production Setup

For production with authentication:

```bash
# Generate user credentials
nsc add user -a account -n tracertm-python
nsc add user -a account -n tracertm-go

# Export credentials
nsc generate creds -a account -n tracertm-python > python.creds
nsc generate creds -a account -n tracertm-go > go.creds

# Set environment variables
export NATS_CREDS_PATH=/secure/path/python.creds
```

## Monitoring

### Health Checks

**Python:**
```python
health = await event_bus.health_check()
print(health)
# {
#   "connected": true,
#   "url": "nats://localhost:4222",
#   "subscriptions": 2,
#   "in_msgs": 1234,
#   "out_msgs": 5678
# }
```

**Go:**
```go
stats := bridge.GetStats()
// Returns connection statistics
```

### Metrics to Monitor

1. **Connection Status**: Is NATS connected?
2. **Message Throughput**: Messages published/consumed per second
3. **Subscription Count**: Number of active subscriptions
4. **Pending Messages**: Messages awaiting acknowledgment
5. **Error Rate**: Failed message processing rate

## Event Flow Examples

### Item Creation Flow

```
1. Go API receives HTTP POST /items
2. Go creates item in database
3. Go publishes item.created event
   Subject: tracertm.bridge.go.{project_id}.item.created
4. NATS persists event to stream
5. Python subscriber receives event
6. Python processes event (update cache, trigger AI analysis, etc.)
7. Python ACKs message
```

### Specification Analysis Flow

```
1. Python API creates specification
2. Python publishes spec.created event
   Subject: tracertm.bridge.python.{project_id}.spec.created
3. NATS persists event to stream
4. Go subscriber receives event
5. Go updates traceability graph
6. Go ACKs message
7. Python triggers AI analysis workflow
8. On completion, Python publishes ai.analysis.complete event
9. Go receives analysis results
```

## Troubleshooting

### Event Not Received

1. **Check NATS connection**: Verify both backends are connected
2. **Check subject pattern**: Ensure subscription pattern matches published subject
3. **Check durable consumer**: Verify consumer is active
4. **Check stream config**: Ensure stream subjects include event pattern

### Messages Stuck in Queue

1. **Check for errors in handler**: Review logs for processing errors
2. **Check acknowledgments**: Ensure messages are being ACKed
3. **Check max delivery**: Messages might be in DLQ after max retries

### Connection Issues

1. **Verify NATS server running**: `nats-server -js`
2. **Check credentials**: Ensure NATS_CREDS_PATH is correct
3. **Check network**: Verify port 4222 is accessible
4. **Review NATS logs**: Check for authentication/authorization errors

## Best Practices

1. **Idempotent Handlers**: Design event handlers to be idempotent (safe to run multiple times)
2. **Small Payloads**: Keep event data minimal, use IDs and fetch details as needed
3. **Versioning**: Include version field in events for schema evolution
4. **Correlation IDs**: Use correlation IDs to trace related events
5. **Monitoring**: Monitor message lag and error rates
6. **Testing**: Test event flows in integration tests
7. **Documentation**: Keep event schemas documented and up-to-date

## Security Considerations

1. **Authentication**: Use NATS credentials in production
2. **Authorization**: Configure subject-level permissions
3. **Encryption**: Use TLS for NATS connections in production
4. **Validation**: Validate event payloads before processing
5. **Rate Limiting**: Implement rate limiting to prevent event flooding

## Future Enhancements

1. **Event Schema Registry**: Centralized schema validation
2. **Event Versioning**: Support for multiple event schema versions
3. **Event Replay**: Ability to replay events for debugging
4. **Event Filtering**: Advanced filtering on event metadata
5. **Event Aggregation**: Aggregate related events for batch processing
