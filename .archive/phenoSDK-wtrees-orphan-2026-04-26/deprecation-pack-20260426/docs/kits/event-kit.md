# Event Kit

## At a Glance
- **Purpose:** Provide event bus, event sourcing, and webhook orchestration primitives.
- **Best For:** Building event-driven services, integrating external systems, and ensuring reliable webhook delivery.
- **Key Building Blocks:** `EventBus`, `EventStore`, `WebhookManager`, subscription filters, monitoring hooks.

## Core Capabilities
- Async pub/sub bus with topic wildcards and middleware.
- Event store with append-only streams, snapshots, and replay utilities.
- Idempotency and retry management for webhooks with signed payloads.
- Monitoring integrations for metrics and logging.
- Schema registry for event payload validation.

## Getting Started

### Installation
```
pip install event-kit
```

### Minimal Example
```python
from event_kit import EventBus

bus = EventBus()

@bus.on("user.created")
async def on_user_created(event):
    print("welcome", event.data["email"])

await bus.publish("user.created", {"email": "user@example.com"})
```

## How It Works
- The bus (`event_kit.bus.EventBus`) manages subscriptions and dispatches events asynchronously.
- Middleware can wrap publishing/subscription to add observability or filtering.
- The event store persists events using pluggable backends (in-memory, db-kit, etc.) and supports replay.
- `WebhookManager` queues deliveries, signs payloads via HMAC, and retries failed attempts with exponential backoff.

## Usage Recipes
- Persist events and replay them:
  ```python
  from event_kit import EventStore

  store = EventStore()
  await store.append(event_type="OrderPlaced", aggregate_id="order-123", data={"total": 42})
  await store.replay("order-123", handler=process_order)
  ```
- Combine with workflow-kit to trigger compensations when events fail to process.
- Expose webhooks for external partners by registering endpoints with `WebhookManager` and verifying signatures via `verify_signature`.
- Use stream-kit to stream events in real time to UI clients.

## Interoperability
- Works alongside db-kit for durable event storage.
- Observability-kit metrics capture event throughput and webhook success rates.
- Adapter-kit container injects event bus and managers into your services.
- Integrate with orchestrator-kit to coordinate multi-step event pipelines.

## Operations & Observability
- Record metrics: `events_published_total`, `events_failed_total`, `webhook_deliveries_total`.
- Enable structured logging of event metadata for audit trails.
- Configure dead-letter queues or compensation workflows when maximal retries fail.

## Testing & QA
- Use in-memory bus and store for fast unit tests.
- Mock webhook HTTP responses with `aiohttp` or `respx` fixtures.
- Assert that event schemas match expected payloads via the schema registry.

## Troubleshooting
- **Missing subscribers:** ensure subscription decorators run during module import (import order matters).
- **Duplicate processing:** enable idempotency keys on events or use event store concurrency checks.
- **Webhook signature mismatch:** confirm shared secret and hashing algorithm align with receivers.

## Primary API Surface
- `EventBus(on_error=None)` / `@bus.on(topic)` / `bus.publish(topic, data, *, metadata)`
- `EventStore(adapter=None)` / `append` / `get_stream` / `replay`
- `WebhookManager(secret, delivery_backend)` / `deliver` / `process_pending`
- `event_kit.schemas.schema` decorator for payload validation

## Additional Resources
- Examples: `event-kit/examples/`
- Tests: `event-kit/tests/`
- Related concepts: [Patterns](../concepts/patterns.md), [Operations](../guides/operations.md)
