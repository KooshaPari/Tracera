"""Integration tests for NATS event flow between Go and Python backends."""

import asyncio
import json
import os
from typing import List
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

# Import NATS client - adjust import based on your actual structure
# from tracertm.infrastructure.nats_client import NATSClient
# from tracertm.infrastructure.event_bus import EventBus


class MockNATSClient:
    """Mock NATS client for testing."""

    def __init__(self, nats_url: str):
        self.nats_url = nats_url
        self.connected = False
        self.published_messages: List[dict] = []
        self.subscriptions: dict[str, list] = {}

    async def connect(self):
        """Simulate NATS connection."""
        self.connected = True

    async def close(self):
        """Simulate NATS disconnection."""
        self.connected = False

    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected

    async def publish(self, subject: str, data: dict):
        """Mock publish - store message for verification."""
        self.published_messages.append(
            {
                "subject": subject,
                "data": data,
                "timestamp": asyncio.get_event_loop().time(),
            }
        )

    async def subscribe(self, subject: str, consumer_name: str, handler):
        """Mock subscribe - register handler."""
        if subject not in self.subscriptions:
            self.subscriptions[subject] = []
        self.subscriptions[subject].append(
            {"consumer": consumer_name, "handler": handler}
        )

    async def trigger_subscription(self, subject: str, data: dict):
        """Manually trigger subscription handlers (for testing)."""
        if subject in self.subscriptions:
            for sub in self.subscriptions[subject]:
                await sub["handler"](data)


class MockEventBus:
    """Mock Event Bus for testing."""

    def __init__(self, nats_client: MockNATSClient):
        self.nats = nats_client

    async def publish(
        self,
        event_type: str,
        project_id: str,
        entity_id: str,
        entity_type: str,
        payload: dict,
    ):
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
async def nats_client():
    """Provide a mock NATS client."""
    client = MockNATSClient("nats://localhost:4222")
    await client.connect()
    yield client
    await client.close()


@pytest_asyncio.fixture
async def event_bus(nats_client):
    """Provide a mock Event Bus."""
    return MockEventBus(nats_client)


@pytest.mark.asyncio
async def test_python_to_nats_flow(nats_client: MockNATSClient, event_bus: MockEventBus):
    """Test Python publishes event to NATS."""
    # Publish event
    await event_bus.publish(
        event_type="analyzed",
        project_id="proj-123",
        entity_id="spec-456",
        entity_type="specification",
        payload={"result": "compliant", "score": 95},
    )

    # Verify event was published
    assert len(nats_client.published_messages) == 1
    message = nats_client.published_messages[0]

    assert message["subject"] == "tracertm.events.specification.analyzed"
    assert message["data"]["project_id"] == "proj-123"
    assert message["data"]["entity_id"] == "spec-456"
    assert message["data"]["payload"]["result"] == "compliant"

    async def test_subscribe_to_go_events(self, event_bus: EventBus, nats_client: NATSClient) -> None:
        """Test subscribing to events from Go backend."""
        received_events = []

        async def handler(event: dict[str, Any]) -> None:
            received_events.append(event)

        # Subscribe to item.created events
        await event_bus.subscribe(EventBus.EVENT_ITEM_CREATED, handler)

        # Simulate Go backend publishing an event
        await nats_client.publish(
            event_type="item.created",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="770e8400-e29b-41d4-a716-446655440002",
            entity_type="item",
            data={"title": "Test Item", "status": "open"},
            source="go",
        )

        # Wait for event to be processed
        await asyncio.sleep(0.5)

        # Verify event was received
        assert len(received_events) == 1
        assert received_events[0]["type"] == "item.created"
        assert received_events[0]["entity_type"] == "item"
        assert received_events[0]["source"] == "go"

    async def test_event_payload_structure(self, nats_client: NATSClient) -> None:
        """Test event payload matches expected structure."""
        # Publish event with all required fields
        await nats_client.publish(
            event_type="test.event",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="660e8400-e29b-41d4-a716-446655440001",
            entity_type="test",
            data={"key": "value"},
            source="python",
        )

        # Event should have all required fields
        # In production, this would be validated by Pydantic schemas

    async def test_durable_subscription(self, event_bus: EventBus, nats_client: NATSClient) -> None:
        """Test durable subscription survives reconnection."""
        received_events = []

        async def handler(event: dict[str, Any]) -> None:
            received_events.append(event)

        # Create durable subscription
        await event_bus.subscribe(EventBus.EVENT_LINK_CREATED, handler)

        # Publish event
        await nats_client.publish(
            event_type="link.created",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="880e8400-e29b-41d4-a716-446655440003",
            entity_type="link",
            data={"source_id": "123", "target_id": "456"},
            source="go",
        )

        # Wait for event
        await asyncio.sleep(0.5)

        # Verify event received
        assert len(received_events) == 1

    async def test_multiple_subscribers(self, nats_client: NATSClient) -> None:
        """Test multiple subscribers can receive the same event."""
        received_1 = []
        received_2 = []

        async def handler_1(event: dict[str, Any]) -> None:
            received_1.append(event)

        async def handler_2(event: dict[str, Any]) -> None:
            received_2.append(event)

        # Create two subscribers with different durable names
        subject = f"{nats_client.SUBJECT_PREFIX}.go.*.item.updated"
        await nats_client.subscribe(subject, "test-sub-1", handler_1)
        await nats_client.subscribe(subject, "test-sub-2", handler_2)

        # Publish event
        await nats_client.publish(
            event_type="item.updated",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="990e8400-e29b-41d4-a716-446655440004",
            entity_type="item",
            data={"status": "closed"},
            source="go",
        )

        # Wait for events
        await asyncio.sleep(0.5)

        # Both subscribers should receive the event
        assert len(received_1) == 1
        assert len(received_2) == 1

        # Clean up
        await nats_client.unsubscribe("test-sub-1")
        await nats_client.unsubscribe("test-sub-2")

    async def test_project_specific_subscription(self, event_bus: EventBus, nats_client: NATSClient) -> None:
        """Test subscribing to events for a specific project."""
        project_id = "550e8400-e29b-41d4-a716-446655440000"
        received_events = []

        async def handler(event: dict[str, Any]) -> None:
            received_events.append(event)

        # Subscribe to project-specific events
        await event_bus.subscribe_to_project(project_id, "item.deleted", handler)

        # Publish event for this project
        await nats_client.publish(
            event_type="item.deleted",
            project_id=project_id,
            entity_id="aa0e8400-e29b-41d4-a716-446655440005",
            entity_type="item",
            data={"reason": "test"},
            source="go",
        )

        # Wait for event
        await asyncio.sleep(0.5)

        # Verify event received
        assert len(received_events) == 1
        assert received_events[0]["project_id"] == project_id

    async def test_message_format_validation(self, event_bus: EventBus) -> None:
        """Test that message format is validated."""
        # Valid event should not raise
        await event_bus.publish(
            event_type="test.event",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="bb0e8400-e29b-41d4-a716-446655440006",
            entity_type="test",
            data={},
        )

        # Event with all required fields should succeed

    async def test_health_check(self, event_bus: EventBus) -> None:
        """Test event bus health check."""
        health = await event_bus.health_check()

        assert health["connected"] is True
        assert "subscriptions" in health
        assert "in_msgs" in health
        assert "out_msgs" in health

    async def test_error_handling(self, event_bus: EventBus, nats_client: NATSClient) -> None:
        """Test error handling in event processing."""
        error_count = 0
        success_count = 0

        async def failing_handler(event: dict[str, Any]) -> None:
            nonlocal error_count, success_count
            if error_count < 2:
                error_count += 1
                raise ValueError("Test error")
            success_count += 1

        # Subscribe with failing handler
        await event_bus.subscribe("test.error", failing_handler)

        # Publish event
        await nats_client.publish(
            event_type="test.error",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="cc0e8400-e29b-41d4-a716-446655440007",
            entity_type="test",
            data={},
            source="go",
        )

        # Wait for retries
        await asyncio.sleep(1)

        # Handler should have been retried
        assert error_count >= 1


@pytest.mark.integration
@pytest.mark.asyncio
class TestEventFlows:
    """Test complete event flows between backends."""

    async def test_item_creation_flow(self, event_bus: EventBus, nats_client: NATSClient) -> None:
        """Test complete item creation event flow."""
        received = []

        async def handler(event: dict[str, Any]) -> None:
            received.append(event)

        # Subscribe to item.created
        await event_bus.subscribe(EventBus.EVENT_ITEM_CREATED, handler)

        # Simulate Go creating an item
        await nats_client.publish(
            event_type="item.created",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="dd0e8400-e29b-41d4-a716-446655440008",
            entity_type="item",
            data={
                "title": "New Feature",
                "type": "feature",
                "status": "open",
                "priority": "high",
            },
            source="go",
        )

        # Wait for event
        await asyncio.sleep(0.5)

        # Verify flow
        assert len(received) == 1
        event = received[0]
        assert event["type"] == "item.created"
        assert event["entity_type"] == "item"
        assert event["data"]["title"] == "New Feature"

    async def test_spec_creation_flow(self, event_bus: EventBus) -> None:
        """Test specification creation and AI analysis flow."""
        # Python creates a specification
        await event_bus.publish(
            event_type=EventBus.EVENT_SPEC_CREATED,
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="ee0e8400-e29b-41d4-a716-446655440009",
            entity_type="specification",
            data={
                "title": "API Specification",
                "type": "contract",
                "content": "...",
            },
        )

        # Simulate AI analysis completion
        await event_bus.publish(
            event_type=EventBus.EVENT_AI_ANALYSIS_COMPLETE,
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="ee0e8400-e29b-41d4-a716-446655440009",
            entity_type="analysis",
            data={
                "spec_id": "ee0e8400-e29b-41d4-a716-446655440009",
                "insights": ["insight1", "insight2"],
                "confidence": 0.95,
            },
        )

        # Events should be published successfully


@pytest.mark.integration
@pytest.mark.asyncio
class TestNATSResilience:
    """Test NATS bridge resilience and error recovery."""

    async def test_connection_resilience(self) -> None:
        """Test connection handles temporary disconnections."""
        # This would require a test NATS server that can be stopped/started
        # For now, we verify connection can be established
        url = os.getenv("NATS_URL", "nats://localhost:4222")
        client = NATSClient(url=url)

        await client.connect()
        assert client.is_connected

        await client.close()
        assert not client.is_connected

    async def test_message_persistence(self, event_bus: EventBus) -> None:
        """Test messages persist across restarts (with durable subscriptions)."""
        # Publish message before subscriber exists
        await event_bus.publish(
            event_type="test.persistent",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            entity_id="ff0e8400-e29b-41d4-a716-446655440010",
            entity_type="test",
            data={"persistent": True},
        )

        # In production, subscriber would receive this message when it connects
        # even if it wasn't running when message was published
