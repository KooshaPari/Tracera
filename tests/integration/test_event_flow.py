from typing import Any

"""Integration tests for NATS event publishing across backends."""

import asyncio
from datetime import UTC, datetime

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN
from tracertm.infrastructure.event_bus import EventBus
from tracertm.infrastructure.nats_client import NATSClient


@pytest.fixture
async def nats_client() -> None:
    """Create and connect a NATS client for testing."""
    client = NATSClient(url="nats://localhost:4222")
    await client.connect()
    yield client
    await client.close()


@pytest.fixture
async def event_bus(nats_client: Any) -> None:
    """Create an EventBus instance for testing."""
    return EventBus(nats_client)


class EventCollector:
    """Helper class to collect events from subscriptions."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    async def handler(self, event: dict) -> None:
        """Event handler callback."""
        self.events.append(event)

    def clear(self) -> None:
        """Clear collected events."""
        self.events = []

    def wait_for_events(self, count: int = 1, timeout: float = 5.0) -> None:
        """Wait for a specific number of events."""

        async def _wait() -> None:
            start = asyncio.get_event_loop().time()
            while len(self.events) < count:
                if asyncio.get_event_loop().time() - start > timeout:
                    msg = f"Timeout waiting for {count} events"
                    raise TimeoutError(msg)
                await asyncio.sleep(0.1)

        return _wait()


@pytest.mark.asyncio
async def test_spec_created_event_published(event_bus: Any) -> None:
    """Test that creating a specification publishes an event."""
    # Setup event collector
    collector = EventCollector()
    await event_bus.subscribe("spec.created", collector.handler)

    # Give subscriber time to register
    await asyncio.sleep(0.5)

    # Publish a spec.created event
    await event_bus.publish(
        event_type=EventBus.EVENT_SPEC_CREATED,
        project_id="test-project-123",
        entity_id="test-adr-456",
        entity_type="adr",
        data={
            "id": "test-adr-456",
            "title": "Test ADR",
            "type": "adr",
            "status": "proposed",
        },
    )

    # Wait for event
    try:
        await collector.wait_for_events(count=1, timeout=5.0)
    except TimeoutError:
        pytest.fail("Event not received within timeout")

    # Verify event
    assert len(collector.events) == 1
    event = collector.events[0]
    assert event["type"] == "spec.created"
    assert event["project_id"] == "test-project-123"
    assert event["entity_id"] == "test-adr-456"
    assert event["entity_type"] == "adr"
    assert event["data"]["title"] == "Test ADR"


@pytest.mark.asyncio
async def test_spec_updated_event_published(event_bus: Any) -> None:
    """Test that updating a specification publishes an event."""
    collector = EventCollector()
    await event_bus.subscribe("spec.updated", collector.handler)
    await asyncio.sleep(0.5)

    await event_bus.publish(
        event_type=EventBus.EVENT_SPEC_UPDATED,
        project_id="test-project-123",
        entity_id="test-contract-789",
        entity_type="contract",
        data={
            "id": "test-contract-789",
            "title": "Updated Contract",
            "status": "active",
        },
    )

    try:
        await collector.wait_for_events(count=1, timeout=5.0)
    except TimeoutError:
        pytest.fail("Event not received within timeout")

    assert len(collector.events) == 1
    event = collector.events[0]
    assert event["type"] == "spec.updated"
    assert event["entity_type"] == "contract"


@pytest.mark.asyncio
async def test_spec_deleted_event_published(event_bus: Any) -> None:
    """Test that deleting a specification publishes an event."""
    collector = EventCollector()
    await event_bus.subscribe("spec.deleted", collector.handler)
    await asyncio.sleep(0.5)

    await event_bus.publish(
        event_type=EventBus.EVENT_SPEC_DELETED,
        project_id="test-project-123",
        entity_id="test-feature-101",
        entity_type="feature",
        data={"id": "test-feature-101"},
    )

    try:
        await collector.wait_for_events(count=1, timeout=5.0)
    except TimeoutError:
        pytest.fail("Event not received within timeout")

    assert len(collector.events) == 1
    event = collector.events[0]
    assert event["type"] == "spec.deleted"
    assert event["entity_type"] == "feature"


@pytest.mark.asyncio
async def test_project_specific_subscription(event_bus: Any) -> None:
    """Test subscribing to events for a specific project."""
    collector = EventCollector()

    # Subscribe to events for specific project
    await event_bus.subscribe_to_project(
        "project-alpha",
        "spec.created",
        collector.handler,
    )
    await asyncio.sleep(0.5)

    # Publish event for target project
    await event_bus.publish(
        event_type=EventBus.EVENT_SPEC_CREATED,
        project_id="project-alpha",
        entity_id="spec-1",
        entity_type="adr",
        data={"id": "spec-1", "title": "Alpha Spec"},
    )

    # Publish event for different project (should not be received)
    await event_bus.publish(
        event_type=EventBus.EVENT_SPEC_CREATED,
        project_id="project-beta",
        entity_id="spec-2",
        entity_type="adr",
        data={"id": "spec-2", "title": "Beta Spec"},
    )

    # Wait and verify only one event received
    await asyncio.sleep(1.0)
    assert len(collector.events) == 1
    assert collector.events[0]["project_id"] == "project-alpha"


@pytest.mark.asyncio
async def test_go_backend_events_received(event_bus: Any) -> None:
    """Test receiving events from Go backend."""
    collector = EventCollector()

    # Subscribe to all Go events
    await event_bus.subscribe_all_go_events(collector.handler)
    await asyncio.sleep(0.5)

    # Simulate Go backend publishing an item.created event
    # In real scenario, this would come from Go handlers
    await event_bus.nats.publish(
        event_type="item.created",
        project_id="test-project",
        entity_id="item-123",
        entity_type="item",
        data={
            "id": "item-123",
            "title": "Test Item",
            "type": "requirement",
        },
        source="go",
    )

    try:
        await collector.wait_for_events(count=1, timeout=5.0)
    except TimeoutError:
        pytest.fail("Go event not received within timeout")

    assert len(collector.events) == 1
    event = collector.events[0]
    assert event["source"] == "go"
    assert event["type"] == "item.created"
    assert event["entity_type"] == "item"


@pytest.mark.asyncio
async def test_event_health_check(event_bus: Any) -> None:
    """Test that event bus health check works."""
    health = await event_bus.health_check()

    assert health["connected"] is True
    assert "subscriptions" in health
    assert "in_msgs" in health
    assert "out_msgs" in health


@pytest.mark.asyncio
async def test_multiple_events_in_sequence(event_bus: Any) -> None:
    """Test publishing multiple events in sequence."""
    collector = EventCollector()
    await event_bus.subscribe("spec.created", collector.handler)
    await asyncio.sleep(0.5)

    # Publish multiple events
    for i in range(5):
        await event_bus.publish(
            event_type=EventBus.EVENT_SPEC_CREATED,
            project_id="test-project",
            entity_id=f"spec-{i}",
            entity_type="adr",
            data={"id": f"spec-{i}", "title": f"Spec {i}"},
        )

    try:
        await collector.wait_for_events(count=5, timeout=10.0)
    except TimeoutError:
        pytest.fail(f"Only received {len(collector.events)}/5 events within timeout")

    assert len(collector.events) == COUNT_FIVE
    for i, event in enumerate(collector.events):
        assert event["entity_id"] == f"spec-{i}"


@pytest.mark.asyncio
async def test_ai_analysis_complete_event(event_bus: Any) -> None:
    """Test publishing AI analysis completion event."""
    collector = EventCollector()
    await event_bus.subscribe("ai.analysis.complete", collector.handler)
    await asyncio.sleep(0.5)

    await event_bus.publish(
        event_type=EventBus.EVENT_AI_ANALYSIS_COMPLETE,
        project_id="test-project",
        entity_id="spec-123",
        entity_type="specification",
        data={
            "spec_id": "spec-123",
            "analysis": {
                "completeness": 85.5,
                "clarity": 90.0,
            },
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )

    try:
        await collector.wait_for_events(count=1, timeout=5.0)
    except TimeoutError:
        pytest.fail("AI analysis event not received within timeout")

    assert len(collector.events) == 1
    event = collector.events[0]
    assert event["type"] == "ai.analysis.complete"
    assert "analysis" in event["data"]


@pytest.mark.asyncio
async def test_execution_completed_event(event_bus: Any) -> None:
    """Test publishing execution completion event."""
    collector = EventCollector()
    await event_bus.subscribe("execution.completed", collector.handler)
    await asyncio.sleep(0.5)

    await event_bus.publish(
        event_type=EventBus.EVENT_EXECUTION_COMPLETED,
        project_id="test-project",
        entity_id="execution-456",
        entity_type="execution",
        data={
            "execution_id": "execution-456",
            "status": "success",
            "exit_code": 0,
            "duration_ms": 1234,
        },
    )

    try:
        await collector.wait_for_events(count=1, timeout=5.0)
    except TimeoutError:
        pytest.fail("Execution event not received within timeout")

    assert len(collector.events) == 1
    event = collector.events[0]
    assert event["type"] == "execution.completed"
    assert event["data"]["status"] == "success"


@pytest.mark.asyncio
async def test_workflow_completed_event(event_bus: Any) -> None:
    """Test publishing workflow completion event."""
    collector = EventCollector()
    await event_bus.subscribe("workflow.completed", collector.handler)
    await asyncio.sleep(0.5)

    await event_bus.publish(
        event_type=EventBus.EVENT_WORKFLOW_COMPLETED,
        project_id="test-project",
        entity_id="workflow-789",
        entity_type="workflow",
        data={
            "workflow_id": "workflow-789",
            "status": "completed",
            "steps_completed": 10,
        },
    )

    try:
        await collector.wait_for_events(count=1, timeout=5.0)
    except TimeoutError:
        pytest.fail("Workflow event not received within timeout")

    assert len(collector.events) == 1
    event = collector.events[0]
    assert event["type"] == "workflow.completed"
    assert event["data"]["steps_completed"] == COUNT_TEN
