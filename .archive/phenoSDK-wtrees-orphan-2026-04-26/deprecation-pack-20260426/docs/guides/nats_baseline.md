# NATS + JetStream Baseline

This guide shows how to use the NATS-based messaging utilities:
- NATSConnectionFactory to connect and get JetStream
- JetStream helpers to declare streams/consumers/work queues
- NATS-backed event bus (publish/subscribe)
- Webhook delivery via NATS + httpx with DLQ

## Requirements

- nats-py and httpx are now required dependencies of event-kit.

## Connect to NATS and JetStream

```python
from event_kit.nats_factory import NATSConnectionFactory

factory = NATSConnectionFactory(servers=["nats://127.0.0.1:4222"], name="demo-service")
async with factory as nc:
    js = factory.jetstream(nc)
    await js.publish("events.demo", b"hello")
```

## Declare a stream and consumer

```python
from event_kit.jetstream_utils import ensure_stream, ensure_consumer

await ensure_stream(js, name="EVENTS", subjects=["events.*"])
await ensure_consumer(js, stream="EVENTS", durable="demo", filter_subject="events.demo")
```

## Event bus (NATS-backed)

```python
from event_kit.nats_factory import NATSConnectionFactory
from event_kit.nats_bus import NatsEventBus

factory = NATSConnectionFactory()
async with factory as nc:
    js = factory.jetstream(nc)
    bus = NatsEventBus(nc=nc, js=js, subject_prefix="events.")

    await bus.publish("user.created", {"id": 1})

    async def handle_user_created(evt: dict):
        print("got event", evt)

    await bus.subscribe("user.created", handle_user_created, durable="users-consumer")
```

## Webhook delivery via NATS + httpx

```python
from event_kit.webhooks.nats_delivery import enqueue_webhook, run_webhook_worker

await enqueue_webhook(js, subject="webhooks.deliveries", url="https://httpbin.org/post", body={"ok": True})

# In a worker
await run_webhook_worker(js, source_subject="webhooks.deliveries", dlq_subject="webhooks.dlq", concurrency=2)
```

Notes:
- This is opt-in and does not replace the default in-memory bus unless adopted.
- Durable consumption requires JetStream; the simple subscribe path uses core NATS (best effort).
- For local dev, you can run NATS via Docker (example):
  docker run -p 4222:4222 nats:2.10 -js
