# NATS Bridge Quick Start Guide

## Overview

This guide helps you get started with the NATS event bridge for bidirectional communication between Go and Python backends.

## Prerequisites

1. **NATS Server with JetStream**
   - Local development: NATS server running on `localhost:4222`
   - Docker: `docker run -p 4222:4222 nats:latest -js`

2. **Dependencies Installed**
   - Go: `github.com/nats-io/nats.go`
   - Python: `nats-py>=2.8.0`, `nkeys>=0.1.0`

## Installation

### Python Dependencies

```bash
# Install NATS dependencies
pip install nats-py>=2.8.0 nkeys>=0.1.0

# Or using requirements.txt
pip install -r requirements.txt
```

### Go Dependencies

```bash
# Dependencies already in go.mod
go mod download
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Enable NATS Bridge
NATS_BRIDGE_ENABLED=true
NATS_URL=nats://localhost:4222

# Optional: For production with authentication
# NATS_CREDS_PATH=/path/to/nats.creds
```

### Start NATS Server

**Option 1: Docker (Recommended)**
```bash
docker run -d --name nats-js -p 4222:4222 nats:latest -js
```

**Option 2: Binary**
```bash
# Install nats-server
brew install nats-server  # macOS
# or download from https://github.com/nats-io/nats-server/releases

# Run with JetStream enabled
nats-server -js
```

## Usage

### Python: Publishing Events

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/api/v1/specifications")
async def create_specification(request: Request):
    # Create specification...
    spec = create_spec(...)

    # Publish event to Go backend
    if hasattr(request.app.state, "event_bus"):
        await request.app.state.event_bus.publish(
            event_type="spec.created",
            project_id=spec.project_id,
            entity_id=spec.id,
            entity_type="specification",
            data={
                "title": spec.title,
                "type": spec.type,
                "status": spec.status,
            }
        )

    return spec
```

### Python: Subscribing to Go Events

Events are automatically subscribed on startup (see `src/tracertm/api/main.py`):

```python
@app.on_event("startup")
async def startup_event():
    # ... NATS setup ...

    async def handle_item_created(event: dict) -> None:
        logger.info(f"Item created: {event['entity_id']}")
        # Update cache, trigger workflows, etc.

    await event_bus.subscribe("item.created", handle_item_created)
```

### Go: Publishing Events

```go
import (
    "github.com/kooshapari/tracertm-backend/internal/nats"
)

// Initialize bridge (typically in main.go)
natsConn, _ := nats.NewNATSClient(natsURL, credsPath)
bridge, _ := nats.NewPythonBridge(natsConn.GetConnection())

// Publish item created event
func CreateItem(item *Item) error {
    // Save item to database...

    // Publish event to Python
    err := bridge.PublishItemEvent(
        nats.SubjectItemCreated,
        item.ProjectID,
        item.ID,
        map[string]interface{}{
            "title": item.Title,
            "status": item.Status,
        },
    )

    return err
}
```

### Go: Subscribing to Python Events

```go
// Subscribe to spec.created events
err := bridge.SubscribeToEventType(
    nats.SubjectSpecCreated,
    func(event *nats.BridgeEvent) {
        log.Printf("Spec created: %s", event.EntityID)
        // Update traceability graph, etc.
    },
)
```

## Testing

### Run Integration Tests

**Python:**
```bash
# Set NATS_URL if not using default
export NATS_URL=nats://localhost:4222

# Run NATS integration tests
pytest tests/integration/test_nats_flow.py -v

# Run with markers
pytest -m integration tests/integration/test_nats_flow.py
```

**Go:**
```bash
# Run NATS tests
cd backend
go test -v ./internal/nats/...
```

### Manual Testing

**Terminal 1: Start NATS**
```bash
docker run -p 4222:4222 nats:latest -js
```

**Terminal 2: Start Python Backend**
```bash
# Set environment
export NATS_BRIDGE_ENABLED=true
export NATS_URL=nats://localhost:4222

# Start server
uvicorn tracertm.api.main:app --reload
```

**Terminal 3: Start Go Backend**
```bash
cd backend
export NATS_URL=nats://localhost:4222
go run cmd/server/main.go
```

**Terminal 4: Test Event Flow**
```bash
# Create item in Go backend (should publish event to Python)
curl -X POST http://localhost:8080/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Item", "project_id": "550e8400-e29b-41d4-a716-446655440000"}'

# Create spec in Python backend (should publish event to Go)
curl -X POST http://localhost:4000/api/v1/specifications \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Spec", "project_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

## Monitoring

### Check NATS Connection

**Python:**
```bash
curl http://localhost:4000/health
```

**Go:**
```bash
curl http://localhost:8080/health
```

### View NATS Stream

```bash
# Install NATS CLI
brew install nats-io/nats-tools/nats

# View stream info
nats stream info TRACERTM_BRIDGE

# View consumers
nats consumer list TRACERTM_BRIDGE

# Monitor events
nats sub "tracertm.bridge.>"
```

## Troubleshooting

### Connection Refused

**Problem:** `Failed to connect to NATS: connection refused`

**Solution:**
1. Verify NATS server is running: `docker ps` or `ps aux | grep nats-server`
2. Check port 4222 is accessible: `nc -zv localhost 4222`
3. Verify NATS_URL environment variable

### Events Not Received

**Problem:** Published events not reaching subscribers

**Solution:**
1. Check subscriber is running: Review startup logs
2. Verify subject pattern: Ensure subscription matches published subject
3. Check NATS stream: `nats stream info TRACERTM_BRIDGE`
4. Monitor events: `nats sub "tracertm.bridge.>"`

### Authentication Errors

**Problem:** `authentication error` or `authorization violation`

**Solution:**
1. For local dev: Don't set NATS_CREDS_PATH (use anonymous access)
2. For production: Verify credentials file exists and is readable
3. Check NATS_USER_JWT and NATS_USER_NKEY_SEED if using JWT auth

### Stream Already Exists

**Problem:** `stream name already in use`

**Solution:**
This is normal - the bridge updates existing stream configuration. No action needed.

## Next Steps

1. **Read Full Documentation**: See [nats_events.md](./nats_events.md)
2. **Review Event Types**: Check available event types and payload structures
3. **Implement Handlers**: Add custom event handlers for your use case
4. **Monitor Production**: Set up monitoring and alerting for NATS health
5. **Enable Authentication**: Configure NATS credentials for production

## Common Patterns

### Cache Invalidation

```python
# Python: Invalidate cache when Go creates/updates item
async def handle_item_updated(event: dict) -> None:
    cache_key = f"item:{event['entity_id']}"
    await redis.delete(cache_key)
```

### Workflow Triggering

```python
# Python: Trigger Hatchet workflow when Go creates link
async def handle_link_created(event: dict) -> None:
    workflow_input = {
        "link_id": event["entity_id"],
        "project_id": event["project_id"],
    }
    await hatchet.trigger("analyze-impact", workflow_input)
```

### Graph Update

```go
// Go: Update Neo4j graph when Python creates spec
func handleSpecCreated(event *nats.BridgeEvent) {
    // Add spec node to graph
    graphClient.CreateNode("Specification", event.EntityID, event.Data)

    // Create relationships
    graphClient.CreateRelationship(event.ProjectID, event.EntityID, "HAS_SPEC")
}
```

## Resources

- [NATS Documentation](https://docs.nats.io/)
- [JetStream Guide](https://docs.nats.io/nats-concepts/jetstream)
- [nats-py Documentation](https://github.com/nats-io/nats.py)
- [nats.go Documentation](https://github.com/nats-io/nats.go)
