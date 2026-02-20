from typing import Any

"""Integration tests for NATS event flow between Go and Python backends - Simple Mock Version."""

import asyncio

import pytest
import pytest_asyncio


class MockNATSClient:
    """Mock NATS client for testing."""

    def __init__(self, nats_url: str) -> None:
        self.nats_url = nats_url
        self.connected = False
        self.published_messages: list[dict] = []
        self.subscriptions: dict[str, list] = {}

    async def connect(self) -> None:
        """Simulate NATS connection."""
        self.connected = True

    async def close(self) -> None:
        """Simulate NATS disconnection."""
        self.connected = False

    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected

    async def publish(self, subject: str, data: dict) -> None:
        """Mock publish - store message for verification."""
        self.published_messages.append({"subject": subject, "data": data, "timestamp": asyncio.get_event_loop().time()})

    async def subscribe(self, subject: str, consumer_name: str, handler: Any) -> None:
        """Mock subscribe - register handler."""
        if subject not in self.subscriptions:
            self.subscriptions[subject] = []
        self.subscriptions[subject].append({"consumer": consumer_name, "handler": handler})

    async def trigger_subscription(self, subject: str, data: dict) -> None:
        """Manually trigger subscription handlers (for testing)."""
        if subject in self.subscriptions:
            for sub in self.subscriptions[subject]:
                await sub["handler"](data)


class MockEventBus:
    """Mock Event Bus for testing."""

    def __init__(self, nats_client: MockNATSClient) -> None:
        self.nats = nats_client

    async def publish(self, event_type: str, project_id: str, entity_id: str, entity_type: str, payload: dict) -> None:
        """Publish event to NATS."""
        subject = f"tracertm.events.{entity_type}.{event_type}"
        data = {
            "event_type": event_type,
            "project_id": project_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "payload": payload,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await self.nats.publish(subject, data)


@pytest_asyncio.fixture
async def nats_client() -> None:
    """Provide a mock NATS client."""
    client = MockNATSClient("nats://localhost:4222")
    await client.connect()
    yield client
    await client.close()


@pytest_asyncio.fixture
async def event_bus(nats_client: Any) -> None:
    """Provide a mock Event Bus."""
    return MockEventBus(nats_client)


@pytest.mark.asyncio
async def test_python_to_nats_flow(nats_client: MockNATSClient, event_bus: MockEventBus) -> None:
    """Test Python publishes event to NATS."""
    await event_bus.publish(
        event_type="analyzed",
        project_id="proj-123",
        entity_id="spec-456",
        entity_type="specification",
        payload={"result": "compliant", "score": 95},
    )

    assert len(nats_client.published_messages) == 1
    message = nats_client.published_messages[0]

    assert message["subject"] == "tracertm.events.specification.analyzed"
    assert message["data"]["project_id"] == "proj-123"
    assert message["data"]["entity_id"] == "spec-456"
    assert message["data"]["payload"]["result"] == "compliant"


@pytest.mark.asyncio
async def test_nats_subscription(nats_client: MockNATSClient) -> None:
    """Test Python receives events from NATS."""
    received_events = []

    async def handler(event: dict) -> None:
        received_events.append(event)

    await nats_client.subscribe("tracertm.bridge.go.*.item.created", "test-consumer", handler)

    event_data = {
        "event_type": "item.created",
        "project_id": "proj-123",
        "item_id": "item-789",
        "item_type": "requirement",
        "payload": {"name": "New Requirement", "priority": "high"},
    }

    await nats_client.trigger_subscription("tracertm.bridge.go.*.item.created", event_data)
    await asyncio.sleep(0.1)

    assert len(received_events) == 1
    assert received_events[0]["item_id"] == "item-789"


@pytest.mark.asyncio
async def test_event_format_validation(event_bus: MockEventBus, nats_client: MockNATSClient) -> None:
    """Test event payload matches schema."""
    await event_bus.publish(
        event_type="created",
        project_id="proj-123",
        entity_id="item-456",
        entity_type="item",
        payload={"name": "Test Item", "type": "requirement"},
    )

    assert len(nats_client.published_messages) == 1
    message = nats_client.published_messages[0]

    assert "subject" in message
    assert "data" in message

    data = message["data"]
    assert all(k in data for k in ["event_type", "project_id", "entity_id", "entity_type", "payload", "timestamp"])
    assert isinstance(data["payload"], dict)


@pytest.mark.asyncio
async def test_bidirectional_flow(nats_client: MockNATSClient, event_bus: MockEventBus) -> None:
    """Test bidirectional event flow between Go and Python."""
    go_events_received = []
    python_events_received = []

    async def handle_go_event(event: dict) -> None:
        go_events_received.append(event)

    async def handle_python_event(event: dict) -> None:
        python_events_received.append(event)

    await nats_client.subscribe("tracertm.bridge.go.*.item.updated", "python-consumer", handle_go_event)
    await nats_client.subscribe("tracertm.events.specification.analyzed", "go-consumer", handle_python_event)

    await event_bus.publish(
        event_type="analyzed",
        project_id="proj-123",
        entity_id="spec-789",
        entity_type="specification",
        payload={"compliant": True},
    )

    go_event = {
        "event_type": "item.updated",
        "project_id": "proj-123",
        "item_id": "item-456",
        "changes": {"status": "approved"},
    }
    await nats_client.trigger_subscription("tracertm.bridge.go.*.item.updated", go_event)
    await nats_client.trigger_subscription(
        "tracertm.events.specification.analyzed",
        nats_client.published_messages[0]["data"],
    )
    await asyncio.sleep(0.1)

    assert len(go_events_received) == 1
    assert len(python_events_received) == 1
    assert go_events_received[0]["item_id"] == "item-456"
    assert python_events_received[0]["entity_id"] == "spec-789"
