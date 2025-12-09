"""
Comprehensive tests for CriticalPathService and APIWebhooksService.

Full coverage of critical path calculation, API key management, webhook registration,
and rate limiting.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from tracertm.services.critical_path_service import (
    CriticalPathService,
    CriticalPathResult,
)
from tracertm.services.api_webhooks_service import (
    APIWebhooksService,
    WebhookEvent,
)


class TestCriticalPathService:
    """Test CriticalPathService."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = AsyncMock()
        service = CriticalPathService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_calculate_critical_path_simple(self, service):
        """Test critical path calculation with simple graph."""
        # Setup items
        items = [
            Mock(id="item-1"),
            Mock(id="item-2"),
            Mock(id="item-3"),
        ]
        service.items.get_by_project = AsyncMock(return_value=items)

        # Setup linear links: item-1 -> item-2 -> item-3
        links = [
            Mock(source_item_id="item-1", target_item_id="item-2", link_type="depends_on"),
            Mock(source_item_id="item-2", target_item_id="item-3", link_type="depends_on"),
        ]
        service.links.get_by_project = AsyncMock(return_value=links)

        # Execute
        result = await service.calculate_critical_path("proj-1")

        # Assert
        assert isinstance(result, CriticalPathResult)
        assert result.project_id == "proj-1"
        assert len(result.critical_path) > 0
        assert result.path_length > 0
        assert result.total_duration > 0

    @pytest.mark.asyncio
    async def test_calculate_critical_path_with_link_types(self, service):
        """Test filtering by link types."""
        items = [Mock(id=f"item-{i}") for i in range(3)]
        service.items.get_by_project = AsyncMock(return_value=items)

        links = [
            Mock(source_item_id="item-0", target_item_id="item-1", link_type="depends_on"),
            Mock(source_item_id="item-1", target_item_id="item-2", link_type="relates_to"),
        ]
        service.links.get_by_project = AsyncMock(return_value=links)

        # Execute with link type filter
        result = await service.calculate_critical_path(
            "proj-1",
            link_types=["depends_on"]
        )

        # Assert - should only follow depends_on links
        assert result.project_id == "proj-1"

    @pytest.mark.asyncio
    async def test_calculate_critical_path_slack_times(self, service):
        """Test slack time calculation."""
        items = [Mock(id=f"item-{i}") for i in range(4)]
        service.items.get_by_project = AsyncMock(return_value=items)

        # Create diamond graph: 0 -> 1 -> 3
        #                       0 -> 2 -> 3
        links = [
            Mock(source_item_id="item-0", target_item_id="item-1", link_type="depends_on"),
            Mock(source_item_id="item-0", target_item_id="item-2", link_type="depends_on"),
            Mock(source_item_id="item-1", target_item_id="item-3", link_type="depends_on"),
            Mock(source_item_id="item-2", target_item_id="item-3", link_type="depends_on"),
        ]
        service.links.get_by_project = AsyncMock(return_value=links)

        # Execute
        result = await service.calculate_critical_path("proj-1")

        # Assert slack times are calculated
        assert result.slack_times is not None
        assert len(result.slack_times) == 4

    @pytest.mark.asyncio
    async def test_calculate_critical_path_critical_items(self, service):
        """Test critical items identification (slack = 0)."""
        items = [Mock(id=f"item-{i}") for i in range(3)]
        service.items.get_by_project = AsyncMock(return_value=items)

        links = [
            Mock(source_item_id="item-0", target_item_id="item-1", link_type="depends_on"),
            Mock(source_item_id="item-1", target_item_id="item-2", link_type="depends_on"),
        ]
        service.links.get_by_project = AsyncMock(return_value=links)

        # Execute
        result = await service.calculate_critical_path("proj-1")

        # Assert critical items are identified
        assert len(result.critical_items) > 0

    @pytest.mark.asyncio
    async def test_calculate_critical_path_empty_project(self, service):
        """Test with empty project."""
        service.items.get_by_project = AsyncMock(return_value=[])
        service.links.get_by_project = AsyncMock(return_value=[])

        # Execute
        result = await service.calculate_critical_path("proj-1")

        # Assert
        assert result.path_length == 0
        assert result.total_duration == 0

    @pytest.mark.asyncio
    async def test_find_critical_path_helper(self, service):
        """Test _find_critical_path helper method."""
        adjacency_list = {
            "item-1": ["item-2"],
            "item-2": ["item-3"],
            "item-3": [],
        }
        critical_items = {"item-1", "item-2", "item-3"}
        topo_order = ["item-1", "item-2", "item-3"]

        # Execute
        path = service._find_critical_path(
            adjacency_list,
            critical_items,
            topo_order,
        )

        # Assert
        assert len(path) == 3
        assert path[0] == "item-1"
        assert path[-1] == "item-3"

    def test_find_critical_path_no_start_node(self, service):
        """Test when no start node exists."""
        adjacency_list = {"item-1": []}
        critical_items = set()
        topo_order = ["item-1"]

        path = service._find_critical_path(
            adjacency_list,
            critical_items,
            topo_order,
        )

        assert len(path) == 0


class TestAPIWebhooksService:
    """Test APIWebhooksService."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return APIWebhooksService()

    def test_create_api_key(self, service):
        """Test creating API key."""
        api_key = service.create_api_key(
            name="Test Key",
            permissions=["read", "write"],
            expires_in_days=30,
        )

        # Assert
        assert api_key["name"] == "Test Key"
        assert api_key["permissions"] == ["read", "write"]
        assert api_key["active"] is True
        assert api_key["expires_at"] is not None
        assert "key" in api_key

    def test_create_api_key_no_expiration(self, service):
        """Test creating API key without expiration."""
        api_key = service.create_api_key(
            name="Permanent Key",
            permissions=["read"],
        )

        # Assert
        assert api_key["expires_at"] is None

    def test_validate_api_key_valid(self, service):
        """Test validating a valid API key."""
        # Create key
        api_key = service.create_api_key(
            name="Test Key",
            permissions=["read", "write"],
        )

        # Validate
        result = service.validate_api_key(api_key["key"])

        # Assert
        assert result["valid"] is True
        assert result["permissions"] == ["read", "write"]

    def test_validate_api_key_invalid(self, service):
        """Test validating invalid API key."""
        result = service.validate_api_key("invalid-key")

        # Assert
        assert result["valid"] is False
        assert "error" in result

    def test_validate_api_key_inactive(self, service):
        """Test validating inactive API key."""
        # Create and revoke key
        api_key = service.create_api_key("Test Key", ["read"])
        service.revoke_api_key(api_key["key"])

        # Validate
        result = service.validate_api_key(api_key["key"])

        # Assert
        assert result["valid"] is False
        assert "inactive" in result["error"].lower()

    def test_validate_api_key_expired(self, service):
        """Test validating expired API key."""
        # Create key that expires in the past by directly manipulating the stored key
        api_key = service.create_api_key(
            "Test Key",
            ["read"],
            expires_in_days=1,
        )

        # Manually set expiration to past date
        past_date = datetime(2020, 1, 1, 12, 0, 0)
        service.api_keys[api_key["key"]]["expires_at"] = past_date.isoformat()

        # Validate
        result = service.validate_api_key(api_key["key"])

        # Assert
        assert result["valid"] is False
        assert "expired" in result["error"].lower()

    def test_revoke_api_key(self, service):
        """Test revoking API key."""
        # Create key
        api_key = service.create_api_key("Test Key", ["read"])

        # Revoke
        result = service.revoke_api_key(api_key["key"])

        # Assert
        assert result["revoked"] is True
        assert service.api_keys[api_key["key"]]["active"] is False

    def test_revoke_nonexistent_api_key(self, service):
        """Test revoking nonexistent API key."""
        result = service.revoke_api_key("nonexistent-key")

        # Assert
        assert "error" in result

    def test_register_webhook(self, service):
        """Test registering a webhook."""
        webhook = service.register_webhook(
            url="https://example.com/webhook",
            events=["item_created", "item_updated"],
            secret="my-secret",
        )

        # Assert
        assert webhook["url"] == "https://example.com/webhook"
        assert webhook["events"] == ["item_created", "item_updated"]
        assert webhook["secret"] == "my-secret"
        assert webhook["active"] is True
        assert "id" in webhook

    def test_unregister_webhook(self, service):
        """Test unregistering a webhook."""
        # Register webhook
        webhook = service.register_webhook(
            url="https://example.com/webhook",
            events=["item_created"],
        )

        # Unregister
        result = service.unregister_webhook(webhook["id"])

        # Assert
        assert result["unregistered"] is True
        assert webhook["id"] not in service.webhooks

    def test_unregister_nonexistent_webhook(self, service):
        """Test unregistering nonexistent webhook."""
        result = service.unregister_webhook("nonexistent-id")

        # Assert
        assert "error" in result

    def test_trigger_webhook_event(self, service):
        """Test triggering webhook event."""
        # Register webhooks
        webhook1 = service.register_webhook(
            url="https://example.com/webhook1",
            events=["item_created"],
        )
        webhook2 = service.register_webhook(
            url="https://example.com/webhook2",
            events=["item_created", "item_updated"],
        )

        # Trigger event
        result = service.trigger_webhook_event(
            event_type="item_created",
            resource_id="item-123",
            resource_type="item",
            action="created",
            data={"title": "New Item"},
        )

        # Assert
        assert result["event_type"] == "item_created"
        assert result["webhooks_triggered"] == 2  # Both webhooks

    def test_trigger_webhook_event_selective(self, service):
        """Test only matching webhooks are triggered."""
        # Register webhooks
        service.register_webhook(
            url="https://example.com/webhook1",
            events=["item_created"],
        )
        service.register_webhook(
            url="https://example.com/webhook2",
            events=["item_updated"],
        )

        # Trigger event
        result = service.trigger_webhook_event(
            event_type="item_created",
            resource_id="item-123",
            resource_type="item",
            action="created",
            data={},
        )

        # Assert only one webhook triggered
        assert result["webhooks_triggered"] == 1

    def test_trigger_webhook_inactive_not_triggered(self, service):
        """Test inactive webhooks are not triggered."""
        # Register webhook and unregister it
        webhook = service.register_webhook(
            url="https://example.com/webhook",
            events=["item_created"],
        )
        service.webhooks[webhook["id"]]["active"] = False

        # Trigger event
        result = service.trigger_webhook_event(
            event_type="item_created",
            resource_id="item-123",
            resource_type="item",
            action="created",
            data={},
        )

        # Assert no webhooks triggered
        assert result["webhooks_triggered"] == 0

    def test_get_webhook_events(self, service):
        """Test getting webhook events."""
        # Trigger some events
        service.trigger_webhook_event(
            "item_created", "item-1", "item", "created", {}
        )
        service.trigger_webhook_event(
            "item_updated", "item-1", "item", "updated", {}
        )

        # Get events
        events = service.get_webhook_events()

        # Assert
        assert len(events) == 2

    def test_get_webhook_events_filtered(self, service):
        """Test getting filtered webhook events."""
        # Trigger events
        service.trigger_webhook_event(
            "item_created", "item-1", "item", "created", {}
        )
        service.trigger_webhook_event(
            "item_updated", "item-1", "item", "updated", {}
        )
        service.trigger_webhook_event(
            "item_created", "item-2", "item", "created", {}
        )

        # Get filtered events
        events = service.get_webhook_events(event_type="item_created")

        # Assert
        assert len(events) == 2
        assert all(e["event_type"] == "item_created" for e in events)

    def test_get_webhook_events_limit(self, service):
        """Test event limit."""
        # Trigger many events
        for i in range(150):
            service.trigger_webhook_event(
                "item_created", f"item-{i}", "item", "created", {}
            )

        # Get events with limit
        events = service.get_webhook_events(limit=50)

        # Assert
        assert len(events) == 50

    def test_set_rate_limit(self, service):
        """Test setting rate limit."""
        # Create API key
        api_key = service.create_api_key("Test Key", ["read"])

        # Set rate limit
        result = service.set_rate_limit(
            api_key["key"],
            requests_per_minute=100,
        )

        # Assert
        assert result["requests_per_minute"] == 100
        assert api_key["key"] in service.rate_limits

    def test_check_rate_limit_allowed(self, service):
        """Test rate limit check when allowed."""
        # Create key and set rate limit
        api_key = service.create_api_key("Test Key", ["read"])
        service.set_rate_limit(api_key["key"], requests_per_minute=10)

        # Check rate limit
        result = service.check_rate_limit(api_key["key"])

        # Assert
        assert result["allowed"] is True
        assert "requests_remaining" in result

    def test_check_rate_limit_no_limit_set(self, service):
        """Test rate limit check when no limit is set."""
        result = service.check_rate_limit("any-key")

        # Assert
        assert result["allowed"] is True
        assert "No rate limit set" in result["reason"]

    def test_check_rate_limit_exceeded(self, service):
        """Test rate limit exceeded."""
        # Create key and set low rate limit
        api_key = service.create_api_key("Test Key", ["read"])
        service.set_rate_limit(api_key["key"], requests_per_minute=2)

        # Make requests to exceed limit
        service.check_rate_limit(api_key["key"])
        service.check_rate_limit(api_key["key"])
        result = service.check_rate_limit(api_key["key"])

        # Assert
        assert result["allowed"] is False
        assert "Rate limit exceeded" in result["reason"]

    @patch("tracertm.services.api_webhooks_service.datetime")
    def test_check_rate_limit_reset(self, mock_datetime, service):
        """Test rate limit resets after time window."""
        # Setup time
        current_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = current_time

        # Create key and set rate limit
        api_key = service.create_api_key("Test Key", ["read"])
        service.set_rate_limit(api_key["key"], requests_per_minute=1)

        # Exceed limit
        service.check_rate_limit(api_key["key"])
        result1 = service.check_rate_limit(api_key["key"])
        assert result1["allowed"] is False

        # Move time forward
        future_time = current_time + timedelta(minutes=2)
        mock_datetime.utcnow.return_value = future_time

        # Check again
        result2 = service.check_rate_limit(api_key["key"])
        assert result2["allowed"] is True

    def test_get_api_stats(self, service):
        """Test getting API statistics."""
        # Create some resources
        service.create_api_key("Key 1", ["read"])
        key2 = service.create_api_key("Key 2", ["write"])
        service.revoke_api_key(key2["key"])

        service.register_webhook("https://example.com/1", ["item_created"])
        webhook2 = service.register_webhook("https://example.com/2", ["item_updated"])
        service.unregister_webhook(webhook2["id"])

        service.trigger_webhook_event("item_created", "item-1", "item", "created", {})

        # Get stats
        stats = service.get_api_stats()

        # Assert
        assert stats["total_api_keys"] == 2
        assert stats["active_api_keys"] == 1
        assert stats["total_webhooks"] == 1
        assert stats["active_webhooks"] == 1
        assert stats["total_webhook_events"] == 1


class TestWebhookEvent:
    """Test WebhookEvent dataclass."""

    def test_create_webhook_event(self):
        """Test creating webhook event."""
        event = WebhookEvent(
            event_type="item_created",
            resource_id="item-123",
            resource_type="item",
            action="created",
            timestamp="2025-01-01T12:00:00",
            data={"title": "Test Item"},
        )

        # Assert
        assert event.event_type == "item_created"
        assert event.resource_id == "item-123"
        assert event.resource_type == "item"
        assert event.action == "created"
        assert event.data["title"] == "Test Item"


class TestCriticalPathResult:
    """Test CriticalPathResult dataclass."""

    def test_create_critical_path_result(self):
        """Test creating critical path result."""
        result = CriticalPathResult(
            project_id="proj-1",
            critical_path=["item-1", "item-2", "item-3"],
            path_length=3,
            total_duration=10,
            critical_items={"item-1", "item-2", "item-3"},
            slack_times={"item-1": 0, "item-2": 0, "item-3": 0, "item-4": 5},
        )

        # Assert
        assert result.project_id == "proj-1"
        assert len(result.critical_path) == 3
        assert result.path_length == 3
        assert result.total_duration == 10
        assert len(result.critical_items) == 3
        assert result.slack_times["item-4"] == 5
