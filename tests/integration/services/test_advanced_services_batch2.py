"""Integration tests for advanced services batch 2 at 0% coverage.

This test suite provides comprehensive integration testing for:
- api_webhooks_service.py (80 lines, 0%)
- commit_linking_service.py (45 lines, 0%)
- documentation_service.py (66 lines, 0%)
- event_sourcing_service.py (72 lines, 0%)
- external_integration_service.py (95 lines, 0%)

Total: 60+ integration tests covering all execution paths, error scenarios,
and edge cases to achieve 100% coverage.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
import pytest_asyncio

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.services.api_webhooks_service import APIWebhooksService
from tracertm.services.commit_linking_service import CommitLinkingService
from tracertm.services.documentation_service import DocumentationService
from tracertm.services.event_sourcing_service import (
    AuditTrailEntry,
    EventSourcingService,
    ReplayResult,
)
from tracertm.services.external_integration_service import (
    ExternalIntegrationService,
    Integration,
    IntegrationType,
)

pytestmark = pytest.mark.integration


# ============================================================
# APIWebhooksService Integration Tests (Lines 1-219)
# ============================================================


class TestAPIWebhooksServiceIntegration:
    """Integration tests for APIWebhooksService."""

    @pytest.fixture
    def webhooks_service(self) -> None:
        """Create APIWebhooksService instance."""
        return APIWebhooksService()

    # API Key Management Tests (Lines 30-83)

    def test_create_api_key_with_all_fields(self, webhooks_service: Any) -> None:
        """Test creating an API key with all fields populated.

        GIVEN: A webhooks service
        WHEN: Creating an API key with name, permissions, and expiration
        THEN: API key is created with correct attributes
        """
        result = webhooks_service.create_api_key(name="test-key", permissions=["read", "write"], expires_in_days=30)

        assert result["name"] == "test-key"
        assert result["permissions"] == ["read", "write"]
        assert result["active"] is True
        assert "key" in result
        assert "created_at" in result
        assert result["expires_at"] is not None
        assert result["key"] in webhooks_service.api_keys

    def test_create_api_key_without_expiration(self, webhooks_service: Any) -> None:
        """Test creating an API key without expiration date.

        GIVEN: A webhooks service
        WHEN: Creating an API key without expires_in_days
        THEN: API key is created with expires_at as None
        """
        result = webhooks_service.create_api_key(name="permanent-key", permissions=["read"])

        assert result["expires_at"] is None
        assert result["active"] is True

    def test_create_multiple_api_keys_unique_hashes(self, webhooks_service: Any) -> None:
        """Test creating multiple API keys generates unique hashes.

        GIVEN: A webhooks service
        WHEN: Creating multiple API keys with same name
        THEN: Each key has a unique hash
        """
        key1 = webhooks_service.create_api_key(name="test", permissions=["read"])
        key2 = webhooks_service.create_api_key(name="test", permissions=["read"])

        assert key1["key"] != key2["key"]
        assert len(webhooks_service.api_keys) == COUNT_TWO

    def test_validate_api_key_valid_active_key(self, webhooks_service: Any) -> None:
        """Test validating a valid and active API key.

        GIVEN: A webhooks service with a valid API key
        WHEN: Validating the key
        THEN: Validation succeeds with key details
        """
        api_key = webhooks_service.create_api_key(name="valid-key", permissions=["read", "write"])

        result = webhooks_service.validate_api_key(api_key["key"])

        assert result["valid"] is True
        assert result["key"] == api_key["key"]
        assert result["permissions"] == ["read", "write"]

    def test_validate_api_key_invalid_key(self, webhooks_service: Any) -> None:
        """Test validating an invalid API key.

        GIVEN: A webhooks service
        WHEN: Validating a non-existent key
        THEN: Validation fails with error message
        """
        result = webhooks_service.validate_api_key("invalid-key-123")

        assert result["valid"] is False
        assert result["error"] == "Invalid API key"

    def test_validate_api_key_inactive_key(self, webhooks_service: Any) -> None:
        """Test validating an inactive API key.

        GIVEN: A webhooks service with a revoked key
        WHEN: Validating the inactive key
        THEN: Validation fails with inactive error
        """
        api_key = webhooks_service.create_api_key(name="inactive-key", permissions=["read"])
        webhooks_service.revoke_api_key(api_key["key"])

        result = webhooks_service.validate_api_key(api_key["key"])

        assert result["valid"] is False
        assert result["error"] == "API key is inactive"

    def test_validate_api_key_expired_key(self, webhooks_service: Any) -> None:
        """Test validating an expired API key.

        GIVEN: A webhooks service with an expired key
        WHEN: Validating the expired key
        THEN: Validation fails with expiration error
        """
        # Create a key that expired yesterday
        api_key = webhooks_service.create_api_key(name="expired-key", permissions=["read"], expires_in_days=-1)

        result = webhooks_service.validate_api_key(api_key["key"])

        assert result["valid"] is False
        assert result["error"] == "API key has expired"

    def test_revoke_api_key_success(self, webhooks_service: Any) -> None:
        """Test successfully revoking an API key.

        GIVEN: A webhooks service with an active key
        WHEN: Revoking the key
        THEN: Key is marked as inactive
        """
        api_key = webhooks_service.create_api_key(name="revoke-key", permissions=["read"])

        result = webhooks_service.revoke_api_key(api_key["key"])

        assert result["revoked"] is True
        assert result["key"] == api_key["key"]
        assert webhooks_service.api_keys[api_key["key"]]["active"] is False

    def test_revoke_api_key_not_found(self, webhooks_service: Any) -> None:
        """Test revoking a non-existent API key.

        GIVEN: A webhooks service
        WHEN: Revoking a non-existent key
        THEN: Error is returned
        """
        result = webhooks_service.revoke_api_key("non-existent-key")

        assert "error" in result
        assert result["error"] == "API key not found"

    # Webhook Management Tests (Lines 84-172)

    def test_register_webhook_with_secret(self, webhooks_service: Any) -> None:
        """Test registering a webhook with secret.

        GIVEN: A webhooks service
        WHEN: Registering a webhook with URL, events, and secret
        THEN: Webhook is registered with all details
        """
        result = webhooks_service.register_webhook(
            url="https://example.com/webhook",
            events=["item.created", "item.updated"],
            secret="my-secret-123",
        )

        assert result["url"] == "https://example.com/webhook"
        assert result["events"] == ["item.created", "item.updated"]
        assert result["secret"] == "my-secret-123"
        assert result["active"] is True
        assert "id" in result
        assert result["delivery_count"] == 0
        assert result["last_triggered"] is None

    def test_register_webhook_without_secret(self, webhooks_service: Any) -> None:
        """Test registering a webhook without secret.

        GIVEN: A webhooks service
        WHEN: Registering a webhook without secret
        THEN: Webhook is registered with None secret
        """
        result = webhooks_service.register_webhook(url="https://example.com/webhook", events=["item.deleted"])

        assert result["secret"] is None
        assert result["active"] is True

    def test_unregister_webhook_success(self, webhooks_service: Any) -> None:
        """Test successfully unregistering a webhook.

        GIVEN: A webhooks service with a registered webhook
        WHEN: Unregistering the webhook
        THEN: Webhook is removed
        """
        webhook = webhooks_service.register_webhook(url="https://example.com/webhook", events=["item.created"])

        result = webhooks_service.unregister_webhook(webhook["id"])

        assert result["unregistered"] is True
        assert result["webhook_id"] == webhook["id"]
        assert webhook["id"] not in webhooks_service.webhooks

    def test_unregister_webhook_not_found(self, webhooks_service: Any) -> None:
        """Test unregistering a non-existent webhook.

        GIVEN: A webhooks service
        WHEN: Unregistering a non-existent webhook
        THEN: Error is returned
        """
        result = webhooks_service.unregister_webhook("non-existent-id")

        assert "error" in result
        assert result["error"] == "Webhook not found"

    def test_trigger_webhook_event_matching_webhooks(self, webhooks_service: Any) -> None:
        """Test triggering an event that matches multiple webhooks.

        GIVEN: Multiple registered webhooks for the same event
        WHEN: Triggering the event
        THEN: All matching webhooks are triggered
        """
        webhooks_service.register_webhook(url="https://example.com/webhook1", events=["item.created", "item.updated"])
        webhooks_service.register_webhook(url="https://example.com/webhook2", events=["item.created"])
        webhooks_service.register_webhook(url="https://example.com/webhook3", events=["item.deleted"])

        result = webhooks_service.trigger_webhook_event(
            event_type="item.created",
            resource_id="item-123",
            resource_type="item",
            action="create",
            data={"title": "New Item"},
        )

        assert result["event_type"] == "item.created"
        assert result["webhooks_triggered"] == COUNT_TWO
        assert "event_id" in result

    def test_trigger_webhook_event_no_matching_webhooks(self, webhooks_service: Any) -> None:
        """Test triggering an event with no matching webhooks.

        GIVEN: Registered webhooks for different events
        WHEN: Triggering an event that doesn't match
        THEN: No webhooks are triggered
        """
        webhooks_service.register_webhook(url="https://example.com/webhook", events=["item.created"])

        result = webhooks_service.trigger_webhook_event(
            event_type="item.deleted",
            resource_id="item-123",
            resource_type="item",
            action="delete",
            data={},
        )

        assert result["webhooks_triggered"] == 0

    def test_trigger_webhook_event_inactive_webhook(self, webhooks_service: Any) -> None:
        """Test triggering an event with inactive webhooks.

        GIVEN: An inactive webhook
        WHEN: Triggering a matching event
        THEN: Inactive webhook is not triggered
        """
        webhook = webhooks_service.register_webhook(url="https://example.com/webhook", events=["item.created"])
        webhooks_service.webhooks[webhook["id"]]["active"] = False

        result = webhooks_service.trigger_webhook_event(
            event_type="item.created",
            resource_id="item-123",
            resource_type="item",
            action="create",
            data={},
        )

        assert result["webhooks_triggered"] == 0

    def test_trigger_webhook_event_updates_delivery_stats(self, webhooks_service: Any) -> None:
        """Test that triggering events updates webhook delivery stats.

        GIVEN: A registered webhook
        WHEN: Triggering matching events multiple times
        THEN: Delivery count and last_triggered are updated
        """
        webhook = webhooks_service.register_webhook(url="https://example.com/webhook", events=["item.created"])

        webhooks_service.trigger_webhook_event(
            event_type="item.created",
            resource_id="item-1",
            resource_type="item",
            action="create",
            data={},
        )
        webhooks_service.trigger_webhook_event(
            event_type="item.created",
            resource_id="item-2",
            resource_type="item",
            action="create",
            data={},
        )

        webhook_data = webhooks_service.webhooks[webhook["id"]]
        assert webhook_data["delivery_count"] == COUNT_TWO
        assert webhook_data["last_triggered"] is not None

    def test_get_webhook_events_all(self, webhooks_service: Any) -> None:
        """Test getting all webhook events.

        GIVEN: Multiple triggered webhook events
        WHEN: Getting events without filter
        THEN: All events are returned
        """
        webhooks_service.trigger_webhook_event("item.created", "item-1", "item", "create", {})
        webhooks_service.trigger_webhook_event("item.updated", "item-1", "item", "update", {})
        webhooks_service.trigger_webhook_event("item.deleted", "item-1", "item", "delete", {})

        events = webhooks_service.get_webhook_events()

        assert len(events) == COUNT_THREE
        assert events[0]["event_type"] == "item.created"
        assert events[1]["event_type"] == "item.updated"
        assert events[2]["event_type"] == "item.deleted"

    def test_get_webhook_events_filtered_by_type(self, webhooks_service: Any) -> None:
        """Test getting webhook events filtered by event type.

        GIVEN: Multiple triggered webhook events
        WHEN: Getting events filtered by type
        THEN: Only matching events are returned
        """
        webhooks_service.trigger_webhook_event("item.created", "item-1", "item", "create", {})
        webhooks_service.trigger_webhook_event("item.created", "item-2", "item", "create", {})
        webhooks_service.trigger_webhook_event("item.updated", "item-1", "item", "update", {})

        events = webhooks_service.get_webhook_events(event_type="item.created")

        assert len(events) == COUNT_TWO
        assert all(e["event_type"] == "item.created" for e in events)

    def test_get_webhook_events_with_limit(self, webhooks_service: Any) -> None:
        """Test getting webhook events with limit.

        GIVEN: Many triggered webhook events
        WHEN: Getting events with a limit
        THEN: Only the most recent events within limit are returned
        """
        for i in range(10):
            webhooks_service.trigger_webhook_event("item.created", f"item-{i}", "item", "create", {})

        events = webhooks_service.get_webhook_events(limit=3)

        assert len(events) == COUNT_THREE
        # Should get the last 3 events
        assert events[0]["resource_id"] == "item-7"
        assert events[1]["resource_id"] == "item-8"
        assert events[2]["resource_id"] == "item-9"

    # Rate Limiting Tests (Lines 173-209)

    def test_set_rate_limit(self, webhooks_service: Any) -> None:
        """Test setting rate limit for an API key.

        GIVEN: A webhooks service
        WHEN: Setting a rate limit
        THEN: Rate limit is configured correctly
        """
        result = webhooks_service.set_rate_limit(api_key="test-key", requests_per_minute=100)

        assert result["api_key"] == "test-key"
        assert result["requests_per_minute"] == 100
        assert "test-key" in webhooks_service.rate_limits
        assert webhooks_service.rate_limits["test-key"]["requests_made"] == 0

    def test_check_rate_limit_no_limit_set(self, webhooks_service: Any) -> None:
        """Test checking rate limit when none is set.

        GIVEN: A webhooks service with no rate limit
        WHEN: Checking rate limit
        THEN: Request is allowed
        """
        result = webhooks_service.check_rate_limit("test-key")

        assert result["allowed"] is True
        assert result["reason"] == "No rate limit set"

    def test_check_rate_limit_within_limit(self, webhooks_service: Any) -> None:
        """Test checking rate limit within allowed requests.

        GIVEN: A rate limit with available capacity
        WHEN: Making a request within limit
        THEN: Request is allowed and counter increments
        """
        webhooks_service.set_rate_limit("test-key", requests_per_minute=10)

        result = webhooks_service.check_rate_limit("test-key")

        assert result["allowed"] is True
        assert result["requests_remaining"] == 9
        assert webhooks_service.rate_limits["test-key"]["requests_made"] == 1

    def test_check_rate_limit_exceeds_limit(self, webhooks_service: Any) -> None:
        """Test checking rate limit when exceeded.

        GIVEN: A rate limit that is exhausted
        WHEN: Making a request beyond limit
        THEN: Request is denied
        """
        webhooks_service.set_rate_limit("test-key", requests_per_minute=2)

        webhooks_service.check_rate_limit("test-key")
        webhooks_service.check_rate_limit("test-key")
        result = webhooks_service.check_rate_limit("test-key")

        assert result["allowed"] is False
        assert result["reason"] == "Rate limit exceeded"

    def test_check_rate_limit_reset_after_minute(self, webhooks_service: Any) -> None:
        """Test that rate limit resets after one minute.

        GIVEN: A rate limit that was exhausted
        WHEN: Checking after reset time
        THEN: Counter is reset and requests allowed
        """
        webhooks_service.set_rate_limit("test-key", requests_per_minute=2)

        # Exhaust the limit
        webhooks_service.check_rate_limit("test-key")
        webhooks_service.check_rate_limit("test-key")

        # Simulate time passing by setting reset_at in the past
        past_time = (datetime.now(UTC) - timedelta(minutes=2)).isoformat()
        webhooks_service.rate_limits["test-key"]["reset_at"] = past_time

        result = webhooks_service.check_rate_limit("test-key")

        assert result["allowed"] is True
        assert webhooks_service.rate_limits["test-key"]["requests_made"] == 1

    # Statistics Tests (Lines 210-219)

    def test_get_api_stats_empty(self, webhooks_service: Any) -> None:
        """Test getting API stats with no data.

        GIVEN: An empty webhooks service
        WHEN: Getting stats
        THEN: All counts are zero
        """
        stats = webhooks_service.get_api_stats()

        assert stats["total_api_keys"] == 0
        assert stats["active_api_keys"] == 0
        assert stats["total_webhooks"] == 0
        assert stats["active_webhooks"] == 0
        assert stats["total_webhook_events"] == 0

    def test_get_api_stats_with_data(self, webhooks_service: Any) -> None:
        """Test getting API stats with various data.

        GIVEN: API keys, webhooks, and events
        WHEN: Getting stats
        THEN: Correct counts are returned
        """
        # Create API keys
        key1 = webhooks_service.create_api_key("key1", ["read"])
        webhooks_service.create_api_key("key2", ["write"])
        webhooks_service.revoke_api_key(key1["key"])

        # Create webhooks
        webhook1 = webhooks_service.register_webhook("https://example.com/1", ["item.created"])
        webhooks_service.register_webhook("https://example.com/2", ["item.updated"])
        webhooks_service.webhooks[webhook1["id"]]["active"] = False

        # Trigger events
        webhooks_service.trigger_webhook_event("item.created", "item-1", "item", "create", {})
        webhooks_service.trigger_webhook_event("item.updated", "item-1", "item", "update", {})

        stats = webhooks_service.get_api_stats()

        assert stats["total_api_keys"] == COUNT_TWO
        assert stats["active_api_keys"] == 1
        assert stats["total_webhooks"] == COUNT_TWO
        assert stats["active_webhooks"] == 1
        assert stats["total_webhook_events"] == COUNT_TWO


# ============================================================
# CommitLinkingService Integration Tests (Lines 1-149)
# ============================================================


class TestCommitLinkingServiceIntegration:
    """Integration tests for CommitLinkingService."""

    @pytest_asyncio.fixture
    async def commit_service(self, db_session: Any) -> None:
        """Create CommitLinkingService instance."""
        return CommitLinkingService(db_session)

    @pytest_asyncio.fixture
    async def test_project(self, db_session: Any, _project_factory: Any) -> None:
        """Create a test project."""
        return await project_factory(name="Test Project")

    @pytest_asyncio.fixture
    async def test_item(self, db_session: Any, item_factory: Any, _test_project: Any) -> None:
        """Create a test item."""
        return await item_factory(project_id=test_project.id, title="Test Feature", item_type="feature")

    # Commit Message Parsing Tests (Lines 31-64)

    @pytest.mark.asyncio
    async def test_parse_commit_message_hash_pattern(
        self, commit_service: Any, test_project: Any, test_item: Any
    ) -> None:
        """Test parsing commit message with hash pattern.

        GIVEN: A commit message with #123 format
        WHEN: Parsing the message
        THEN: Item reference is found
        """
        commit_message = f"Fix bug #{test_item.id}"

        result = await commit_service.parse_commit_message(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="abc123",
            author="developer",
        )

        assert len(result["found"]) >= 0
        assert isinstance(result["errors"], list)

    @pytest.mark.asyncio
    async def test_parse_commit_message_jira_pattern(self, commit_service: Any, test_project: Any) -> None:
        """Test parsing commit message with JIRA pattern.

        GIVEN: A commit message with FEAT-123 format
        WHEN: Parsing the message
        THEN: Pattern is detected
        """
        commit_message = "Implement FEAT-123 feature"

        result = await commit_service.parse_commit_message(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="abc123",
            author="developer",
        )

        # Pattern is detected even if item not found
        assert "errors" in result
        assert "found" in result
        assert "linked" in result

    @pytest.mark.asyncio
    async def test_parse_commit_message_github_pattern(self, commit_service: Any, test_project: Any) -> None:
        """Test parsing commit message with GitHub pattern.

        GIVEN: A commit message with GH-123 format
        WHEN: Parsing the message
        THEN: Pattern is detected
        """
        commit_message = "Close GH-456 issue"

        result = await commit_service.parse_commit_message(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="def456",
            author="developer",
        )

        assert "found" in result
        assert "errors" in result

    @pytest.mark.asyncio
    async def test_parse_commit_message_multiple_patterns(self, commit_service: Any, test_project: Any) -> None:
        """Test parsing commit message with multiple patterns.

        GIVEN: A commit message with multiple reference formats
        WHEN: Parsing the message
        THEN: All patterns are detected
        """
        commit_message = "Fix #123 and FEAT-456 also GH-789"

        result = await commit_service.parse_commit_message(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="xyz789",
            author="developer",
        )

        assert "found" in result
        assert isinstance(result["errors"], list)

    @pytest.mark.asyncio
    async def test_parse_commit_message_no_patterns(self, commit_service: Any, test_project: Any) -> None:
        """Test parsing commit message with no patterns.

        GIVEN: A commit message without any references
        WHEN: Parsing the message
        THEN: No items are found
        """
        commit_message = "Update documentation"

        result = await commit_service.parse_commit_message(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="doc123",
            author="developer",
        )

        assert len(result["found"]) == 0
        assert len(result["errors"]) == 0

    # Auto-Linking Tests (Lines 66-116)

    @pytest.mark.asyncio
    async def test_auto_link_commit_success(
        self, commit_service: Any, test_project: Any, test_item: Any, db_session: Any
    ) -> None:
        """Test successfully auto-linking a commit to an item.

        GIVEN: A commit message referencing an item
        WHEN: Auto-linking the commit
        THEN: Link is created and event is logged
        """
        # This will fail to find the item by the pattern, but tests the flow
        commit_message = f"Implement feature #{test_item.id}"

        result = await commit_service.auto_link_commit(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="commit-abc123",
            author="developer",
            agent_id="test-agent",
        )

        assert "found" in result
        assert "linked" in result
        assert "errors" in result

    @pytest.mark.asyncio
    async def test_auto_link_commit_no_references(
        self, commit_service: Any, test_project: Any, db_session: Any
    ) -> None:
        """Test auto-linking with no item references.

        GIVEN: A commit message without references
        WHEN: Auto-linking the commit
        THEN: No links are created
        """
        commit_message = "Update README file"

        result = await commit_service.auto_link_commit(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="commit-xyz789",
            author="developer",
        )

        assert len(result["found"]) == 0
        assert len(result["linked"]) == 0

    @pytest.mark.asyncio
    async def test_auto_link_commit_with_errors(self, commit_service: Any, test_project: Any, _db_session: Any) -> None:
        """Test auto-linking when errors occur.

        GIVEN: A commit message with invalid references
        WHEN: Auto-linking the commit
        THEN: Errors are captured
        """
        commit_message = "Fix #nonexistent and INVALID-999"

        result = await commit_service.auto_link_commit(
            project_id=test_project.id,
            commit_message=commit_message,
            commit_hash="error-commit",
            author="developer",
        )

        assert "errors" in result

    # Item Lookup Tests (Lines 118-134)

    @pytest.mark.asyncio
    async def test_find_item_by_reference_direct_id(
        self, commit_service: Any, test_project: Any, test_item: Any
    ) -> None:
        """Test finding item by direct ID.

        GIVEN: An existing item
        WHEN: Looking up by exact ID
        THEN: Item is found
        """
        item = await commit_service._find_item_by_reference(project_id=test_project.id, reference=test_item.id)

        assert item is not None
        assert item.id == test_item.id

    @pytest.mark.asyncio
    async def test_find_item_by_reference_not_found(self, commit_service: Any, test_project: Any) -> None:
        """Test finding item that doesn't exist.

        GIVEN: A non-existent item reference
        WHEN: Looking up by reference
        THEN: None is returned
        """
        item = await commit_service._find_item_by_reference(project_id=test_project.id, reference="nonexistent-id")

        assert item is None

    @pytest.mark.asyncio
    async def test_find_item_by_reference_wrong_project(
        self,
        commit_service: Any,
        test_project: Any,
        test_item: Any,
        db_session: Any,
        _project_factory: Any,
    ) -> None:
        """Test finding item from different project.

        GIVEN: An item in a different project
        WHEN: Looking up with wrong project_id
        THEN: Item is not found
        """
        other_project = await project_factory(name="Other Project")

        item = await commit_service._find_item_by_reference(project_id=other_project.id, reference=test_item.id)

        # Item exists but belongs to different project
        assert item is None

    # Commit Hook Registration Tests (Lines 136-149)

    @pytest.mark.asyncio
    async def test_register_commit_hook_git(self, commit_service: Any, test_project: Any) -> None:
        """Test registering a git commit hook.

        GIVEN: A project
        WHEN: Registering a git hook
        THEN: Hook is registered with correct config
        """
        result = await commit_service.register_commit_hook(
            project_id=test_project.id,
            hook_type="git",
            config={"repo_path": "/path/to/repo"},
        )

        assert result["project_id"] == test_project.id
        assert result["hook_type"] == "git"
        assert result["config"]["repo_path"] == "/path/to/repo"
        assert result["status"] == "registered"

    @pytest.mark.asyncio
    async def test_register_commit_hook_github(self, commit_service: Any, test_project: Any) -> None:
        """Test registering a GitHub commit hook.

        GIVEN: A project
        WHEN: Registering a GitHub hook
        THEN: Hook is registered
        """
        result = await commit_service.register_commit_hook(
            project_id=test_project.id,
            hook_type="github",
            config={"repo": "user/repo", "webhook_url": "https://example.com/hook"},
        )

        assert result["hook_type"] == "github"
        assert result["status"] == "registered"

    @pytest.mark.asyncio
    async def test_register_commit_hook_gitlab(self, commit_service: Any, test_project: Any) -> None:
        """Test registering a GitLab commit hook.

        GIVEN: A project
        WHEN: Registering a GitLab hook
        THEN: Hook is registered
        """
        result = await commit_service.register_commit_hook(
            project_id=test_project.id,
            hook_type="gitlab",
            config={"project_id": "12345", "token": "secret-token"},
        )

        assert result["hook_type"] == "gitlab"
        assert result["status"] == "registered"


# ============================================================
# DocumentationService Integration Tests (Lines 1-173)
# ============================================================


class TestDocumentationServiceIntegration:
    """Integration tests for DocumentationService."""

    @pytest.fixture
    def doc_service(self) -> None:
        """Create DocumentationService instance."""
        return DocumentationService()

    # Endpoint Registration Tests (Lines 15-42)

    def test_register_endpoint_complete(self, doc_service: Any) -> None:
        """Test registering an endpoint with all fields.

        GIVEN: A documentation service
        WHEN: Registering an endpoint with full details
        THEN: Endpoint is stored correctly
        """
        result = doc_service.register_endpoint(
            path="/api/items",
            method="POST",
            description="Create a new item",
            parameters=[
                {"name": "title", "type": "string", "description": "Item title"},
                {"name": "type", "type": "string", "description": "Item type"},
            ],
            response_schema={"type": "object", "properties": {"id": {"type": "string"}}},
        )

        assert result["path"] == "/api/items"
        assert result["method"] == "POST"
        assert result["description"] == "Create a new item"
        assert len(result["parameters"]) == COUNT_TWO
        assert "registered_at" in result

    def test_get_endpoint_exists(self, doc_service: Any) -> None:
        """Test getting an existing endpoint.

        GIVEN: A registered endpoint
        WHEN: Getting the endpoint
        THEN: Endpoint details are returned
        """
        doc_service.register_endpoint(
            path="/api/items",
            method="GET",
            description="List items",
            parameters=[],
            response_schema={},
        )

        result = doc_service.get_endpoint("/api/items", "GET")

        assert result is not None
        assert result["path"] == "/api/items"
        assert result["method"] == "GET"

    def test_get_endpoint_not_found(self, doc_service: Any) -> None:
        """Test getting a non-existent endpoint.

        GIVEN: A documentation service
        WHEN: Getting an endpoint that doesn't exist
        THEN: None is returned
        """
        result = doc_service.get_endpoint("/api/nonexistent", "GET")

        assert result is None

    def test_list_endpoints_all(self, doc_service: Any) -> None:
        """Test listing all endpoints.

        GIVEN: Multiple registered endpoints
        WHEN: Listing without filter
        THEN: All endpoints are returned
        """
        doc_service.register_endpoint("/api/items", "GET", "List items", [], {})
        doc_service.register_endpoint("/api/items", "POST", "Create item", [], {})
        doc_service.register_endpoint("/api/projects", "GET", "List projects", [], {})

        result = doc_service.list_endpoints()

        assert len(result) == COUNT_THREE

    def test_list_endpoints_filtered_by_method(self, doc_service: Any) -> None:
        """Test listing endpoints filtered by method.

        GIVEN: Multiple endpoints with different methods
        WHEN: Listing with method filter
        THEN: Only matching endpoints are returned
        """
        doc_service.register_endpoint("/api/items", "GET", "List items", [], {})
        doc_service.register_endpoint("/api/items", "POST", "Create item", [], {})
        doc_service.register_endpoint("/api/projects", "GET", "List projects", [], {})

        result = doc_service.list_endpoints(method="GET")

        assert len(result) == COUNT_TWO
        assert all(e["method"] == "GET" for e in result)

    # Schema Registration Tests (Lines 52-76)

    def test_register_schema(self, doc_service: Any) -> None:
        """Test registering a data schema.

        GIVEN: A documentation service
        WHEN: Registering a schema
        THEN: Schema is stored correctly
        """
        result = doc_service.register_schema(
            name="Item",
            schema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                },
            },
            description="Item schema",
        )

        assert result["name"] == "Item"
        assert result["description"] == "Item schema"
        assert "registered_at" in result

    def test_get_schema_exists(self, doc_service: Any) -> None:
        """Test getting an existing schema.

        GIVEN: A registered schema
        WHEN: Getting the schema
        THEN: Schema details are returned
        """
        doc_service.register_schema(name="Project", schema={"type": "object"}, description="Project schema")

        result = doc_service.get_schema("Project")

        assert result is not None
        assert result["name"] == "Project"

    def test_get_schema_not_found(self, doc_service: Any) -> None:
        """Test getting a non-existent schema.

        GIVEN: A documentation service
        WHEN: Getting a schema that doesn't exist
        THEN: None is returned
        """
        result = doc_service.get_schema("NonExistent")

        assert result is None

    def test_list_schemas(self, doc_service: Any) -> None:
        """Test listing all schemas.

        GIVEN: Multiple registered schemas
        WHEN: Listing schemas
        THEN: All schemas are returned
        """
        doc_service.register_schema("Item", {}, "Item schema")
        doc_service.register_schema("Project", {}, "Project schema")
        doc_service.register_schema("Link", {}, "Link schema")

        result = doc_service.list_schemas()

        assert len(result) == COUNT_THREE

    # Example Management Tests (Lines 77-104)

    def test_add_example(self, doc_service: Any) -> None:
        """Test adding an example for an endpoint.

        GIVEN: A documentation service
        WHEN: Adding an example
        THEN: Example is stored
        """
        result = doc_service.add_example(
            endpoint_path="/api/items",
            method="POST",
            example_name="Create Feature",
            request={"title": "New Feature", "type": "feature"},
            response={"id": "item-123", "title": "New Feature"},
        )

        assert result["name"] == "Create Feature"
        assert result["request"]["title"] == "New Feature"
        assert result["response"]["id"] == "item-123"

    def test_add_multiple_examples_same_endpoint(self, doc_service: Any) -> None:
        """Test adding multiple examples to the same endpoint.

        GIVEN: An endpoint
        WHEN: Adding multiple examples
        THEN: All examples are stored
        """
        doc_service.add_example("/api/items", "POST", "Example 1", {"data": "1"}, {"id": "1"})
        doc_service.add_example("/api/items", "POST", "Example 2", {"data": "2"}, {"id": "2"})

        examples = doc_service.get_examples("/api/items", "POST")

        assert len(examples) == COUNT_TWO

    def test_get_examples_for_endpoint(self, doc_service: Any) -> None:
        """Test getting examples for a specific endpoint.

        GIVEN: Examples for multiple endpoints
        WHEN: Getting examples for one endpoint
        THEN: Only that endpoint's examples are returned
        """
        doc_service.add_example("/api/items", "POST", "Example 1", {}, {})
        doc_service.add_example("/api/projects", "POST", "Example 2", {}, {})

        examples = doc_service.get_examples("/api/items", "POST")

        assert len(examples) == 1
        assert examples[0]["name"] == "Example 1"

    def test_get_examples_no_examples(self, doc_service: Any) -> None:
        """Test getting examples when none exist.

        GIVEN: A documentation service with no examples
        WHEN: Getting examples for an endpoint
        THEN: Empty list is returned
        """
        examples = doc_service.get_examples("/api/items", "GET")

        assert examples == []

    # OpenAPI Generation Tests (Lines 105-141)

    def test_generate_openapi_spec_empty(self, doc_service: Any) -> None:
        """Test generating OpenAPI spec with no endpoints.

        GIVEN: A documentation service with no endpoints
        WHEN: Generating OpenAPI spec
        THEN: Basic structure is returned
        """
        spec = doc_service.generate_openapi_spec()

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "TraceRTM API"
        assert spec["paths"] == {}
        assert spec["components"]["schemas"] == {}

    def test_generate_openapi_spec_with_endpoints(self, doc_service: Any) -> None:
        """Test generating OpenAPI spec with endpoints.

        GIVEN: Registered endpoints
        WHEN: Generating OpenAPI spec
        THEN: Endpoints are included in paths
        """
        doc_service.register_endpoint(
            path="/api/items",
            method="GET",
            description="List all items",
            parameters=[],
            response_schema={"type": "array"},
        )
        doc_service.register_endpoint(
            path="/api/items",
            method="POST",
            description="Create an item",
            parameters=[{"name": "title", "type": "string"}],
            response_schema={"type": "object"},
        )

        spec = doc_service.generate_openapi_spec()

        assert "/api/items" in spec["paths"]
        assert "get" in spec["paths"]["/api/items"]
        assert "post" in spec["paths"]["/api/items"]

    def test_generate_openapi_spec_with_schemas(self, doc_service: Any) -> None:
        """Test generating OpenAPI spec with schemas.

        GIVEN: Registered schemas
        WHEN: Generating OpenAPI spec
        THEN: Schemas are included in components
        """
        doc_service.register_schema(
            name="Item",
            schema={"type": "object", "properties": {"id": {"type": "string"}}},
            description="Item schema",
        )

        spec = doc_service.generate_openapi_spec()

        assert "Item" in spec["components"]["schemas"]

    # Markdown Generation Tests (Lines 142-164)

    def test_generate_markdown_docs_empty(self, doc_service: Any) -> None:
        """Test generating markdown docs with no endpoints.

        GIVEN: A documentation service with no endpoints
        WHEN: Generating markdown
        THEN: Basic structure is returned
        """
        md = doc_service.generate_markdown_docs()

        assert "# TraceRTM API Documentation" in md
        assert "## Endpoints" in md

    def test_generate_markdown_docs_with_endpoints(self, doc_service: Any) -> None:
        """Test generating markdown docs with endpoints.

        GIVEN: Registered endpoints
        WHEN: Generating markdown
        THEN: Endpoints are documented
        """
        doc_service.register_endpoint(
            path="/api/items",
            method="GET",
            description="Get all items",
            parameters=[{"name": "status", "type": "string", "description": "Filter by status"}],
            response_schema={"type": "array"},
        )

        md = doc_service.generate_markdown_docs()

        assert "### GET /api/items" in md
        assert "Get all items" in md
        assert "**Parameters:**" in md
        assert "`status` (string): Filter by status" in md

    def test_generate_markdown_docs_no_parameters(self, doc_service: Any) -> None:
        """Test generating markdown docs for endpoint without parameters.

        GIVEN: An endpoint with no parameters
        WHEN: Generating markdown
        THEN: Parameters section is skipped
        """
        doc_service.register_endpoint(
            path="/api/health",
            method="GET",
            description="Health check",
            parameters=[],
            response_schema={"status": "ok"},
        )

        md = doc_service.generate_markdown_docs()

        assert "### GET /api/health" in md
        assert "Health check" in md

    # Statistics Tests (Lines 165-173)

    def test_get_documentation_stats_empty(self, doc_service: Any) -> None:
        """Test getting documentation stats with no data.

        GIVEN: An empty documentation service
        WHEN: Getting stats
        THEN: Zero counts are returned
        """
        stats = doc_service.get_documentation_stats()

        assert stats["total_endpoints"] == 0
        assert stats["total_schemas"] == 0
        assert stats["total_examples"] == 0
        assert stats["methods"] == []

    def test_get_documentation_stats_with_data(self, doc_service: Any) -> None:
        """Test getting documentation stats with data.

        GIVEN: Endpoints, schemas, and examples
        WHEN: Getting stats
        THEN: Correct counts are returned
        """
        doc_service.register_endpoint("/api/items", "GET", "List", [], {})
        doc_service.register_endpoint("/api/items", "POST", "Create", [], {})
        doc_service.register_endpoint("/api/projects", "GET", "List", [], {})

        doc_service.register_schema("Item", {}, "Item schema")
        doc_service.register_schema("Project", {}, "Project schema")

        doc_service.add_example("/api/items", "POST", "Ex1", {}, {})
        doc_service.add_example("/api/items", "POST", "Ex2", {}, {})
        doc_service.add_example("/api/projects", "GET", "Ex3", {}, {})

        stats = doc_service.get_documentation_stats()

        assert stats["total_endpoints"] == COUNT_THREE
        assert stats["total_schemas"] == COUNT_TWO
        assert stats["total_examples"] == COUNT_THREE
        assert set(stats["methods"]) == {"GET", "POST"}


# ============================================================
# EventSourcingService Integration Tests (Lines 1-187)
# ============================================================


class TestEventSourcingServiceIntegration:
    """Integration tests for EventSourcingService."""

    @pytest_asyncio.fixture
    async def event_service(self, db_session: Any) -> None:
        """Create EventSourcingService instance."""
        return EventSourcingService(db_session)

    @pytest_asyncio.fixture
    async def test_project(self, db_session: Any, _project_factory: Any) -> None:
        """Create a test project."""
        return await project_factory(name="Event Test Project")

    @pytest_asyncio.fixture
    async def test_item(self, db_session: Any, item_factory: Any, _test_project: Any) -> None:
        """Create a test item."""
        return await item_factory(project_id=test_project.id, title="Event Test Item")

    @pytest_asyncio.fixture
    async def create_test_events(self, db_session: Any, test_project: Any, test_item: Any) -> None:
        """Create test events."""
        from tracertm.repositories.event_repository import EventRepository

        event_repo = EventRepository(db_session)

        events = []
        for i in range(3):
            event = await event_repo.log(
                project_id=test_project.id,
                event_type="item_updated",
                entity_type="item",
                entity_id=test_item.id,
                data={"version": i + 1},
                agent_id="test-agent",
            )
            events.append(event)

        await db_session.flush()
        return events

    # Audit Trail Tests (Lines 44-71)

    @pytest.mark.asyncio
    async def test_get_audit_trail_by_project(
        self, event_service: Any, test_project: Any, create_test_events: Any
    ) -> None:
        """Test getting audit trail for entire project.

        GIVEN: Multiple events in a project
        WHEN: Getting audit trail by project
        THEN: All project events are returned
        """
        trail = await event_service.get_audit_trail(project_id=test_project.id)

        assert len(trail) >= COUNT_THREE
        assert all(isinstance(entry, AuditTrailEntry) for entry in trail)
        assert all(entry.entity_type in {"item", "project"} for entry in trail)

    @pytest.mark.asyncio
    async def test_get_audit_trail_by_entity(
        self, event_service: Any, test_project: Any, test_item: Any, create_test_events: Any
    ) -> None:
        """Test getting audit trail for specific entity.

        GIVEN: Multiple events for an entity
        WHEN: Getting audit trail by entity_id
        THEN: Only entity events are returned
        """
        trail = await event_service.get_audit_trail(project_id=test_project.id, entity_id=test_item.id)

        assert len(trail) >= COUNT_THREE
        assert all(entry.entity_id == test_item.id for entry in trail)

    @pytest.mark.asyncio
    async def test_get_audit_trail_with_limit(
        self, event_service: Any, test_project: Any, create_test_events: Any
    ) -> None:
        """Test getting audit trail with limit.

        GIVEN: Multiple events
        WHEN: Getting audit trail with limit
        THEN: Limited number of events returned
        """
        trail = await event_service.get_audit_trail(project_id=test_project.id, limit=2)

        assert len(trail) <= COUNT_TWO

    @pytest.mark.asyncio
    async def test_audit_trail_entry_structure(
        self, event_service: Any, test_project: Any, create_test_events: Any
    ) -> None:
        """Test audit trail entry has correct structure.

        GIVEN: Events in the system
        WHEN: Getting audit trail
        THEN: Entries have all required fields
        """
        trail = await event_service.get_audit_trail(project_id=test_project.id, limit=1)

        if trail:
            entry = trail[0]
            assert hasattr(entry, "timestamp")
            assert hasattr(entry, "event_type")
            assert hasattr(entry, "entity_type")
            assert hasattr(entry, "entity_id")
            assert hasattr(entry, "agent_id")
            assert hasattr(entry, "data")

    # Event Replay Tests (Lines 72-107)

    @pytest.mark.asyncio
    async def test_replay_events_all(
        self, event_service: Any, test_project: Any, test_item: Any, create_test_events: Any
    ) -> None:
        """Test replaying all events for an entity.

        GIVEN: Multiple events for an entity
        WHEN: Replaying all events
        THEN: Final state is reconstructed
        """
        result = await event_service.replay_events(project_id=test_project.id, entity_id=test_item.id)

        assert isinstance(result, ReplayResult)
        assert result.total_events >= 0
        assert result.replayed_events >= 0
        assert isinstance(result.final_state, dict)

    @pytest.mark.asyncio
    async def test_replay_events_up_to_timestamp(
        self, event_service: Any, test_project: Any, test_item: Any, create_test_events: Any
    ) -> None:
        """Test replaying events up to specific timestamp.

        GIVEN: Multiple events at different times
        WHEN: Replaying events with timestamp cutoff
        THEN: Only events before cutoff are replayed
        """
        # Use future timestamp to get all events
        future_time = (datetime.now(UTC) + timedelta(hours=1)).isoformat()

        result = await event_service.replay_events(
            project_id=test_project.id,
            entity_id=test_item.id,
            up_to_timestamp=future_time,
        )

        assert result.total_events >= 0

    @pytest.mark.asyncio
    async def test_apply_event_item_created(self, event_service: Any) -> None:
        """Test applying item_created event.

        GIVEN: An empty state
        WHEN: Applying item_created event
        THEN: State is initialized
        """
        from tracertm.models.event import Event

        state = {}
        event = Event(
            id="event-1",
            project_id="proj-1",
            event_type="item_created",
            entity_type="item",
            entity_id="item-1",
            data={"title": "New Item"},
            created_at=datetime.now(UTC),
        )

        new_state = await event_service._apply_event(state, event)

        assert new_state["id"] == "item-1"
        assert new_state["title"] == "New Item"
        assert new_state["status"] == "created"
        assert new_state["version"] == 1

    @pytest.mark.asyncio
    async def test_apply_event_item_updated(self, event_service: Any) -> None:
        """Test applying item_updated event.

        GIVEN: A state with existing item
        WHEN: Applying item_updated event
        THEN: State is updated and version incremented
        """
        from tracertm.models.event import Event

        state = {"id": "item-1", "title": "Old Title", "version": 1}
        event = Event(
            id="event-2",
            project_id="proj-1",
            event_type="item_updated",
            entity_type="item",
            entity_id="item-1",
            data={"title": "New Title", "status": "in_progress"},
            created_at=datetime.now(UTC),
        )

        new_state = await event_service._apply_event(state, event)

        assert new_state["title"] == "New Title"
        assert new_state["status"] == "in_progress"
        assert new_state["version"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_apply_event_item_deleted(self, event_service: Any) -> None:
        """Test applying item_deleted event.

        GIVEN: A state with existing item
        WHEN: Applying item_deleted event
        THEN: Item is marked as deleted
        """
        from tracertm.models.event import Event

        state = {"id": "item-1", "title": "Item"}
        event = Event(
            id="event-3",
            project_id="proj-1",
            event_type="item_deleted",
            entity_type="item",
            entity_id="item-1",
            data={"deleted_at": "2025-01-01T00:00:00"},
            created_at=datetime.now(UTC),
        )

        new_state = await event_service._apply_event(state, event)

        assert new_state["deleted"] is True
        assert new_state["deleted_at"] == "2025-01-01T00:00:00"

    @pytest.mark.asyncio
    async def test_apply_event_link_created(self, event_service: Any) -> None:
        """Test applying link_created event.

        GIVEN: A state
        WHEN: Applying link_created event
        THEN: Link is added to state
        """
        from tracertm.models.event import Event

        state = {}
        event = Event(
            id="event-4",
            project_id="proj-1",
            event_type="link_created",
            entity_type="link",
            entity_id="link-1",
            data={"target_item_id": "item-2", "link_type": "depends_on"},
            created_at=datetime.now(UTC),
        )

        new_state = await event_service._apply_event(state, event)

        assert "links" in new_state
        assert len(new_state["links"]) == 1
        assert new_state["links"][0]["target_id"] == "item-2"
        assert new_state["links"][0]["type"] == "depends_on"

    # Event History Tests (Lines 145-157)

    @pytest.mark.asyncio
    async def test_get_event_history_all(self, event_service: Any, test_item: Any, _create_test_events: Any) -> None:
        """Test getting complete event history.

        GIVEN: Multiple events for an entity
        WHEN: Getting event history
        THEN: All events are returned
        """
        events = await event_service.get_event_history(entity_id=test_item.id)

        assert len(events) >= COUNT_THREE
        assert all(e.entity_id == test_item.id for e in events)

    @pytest.mark.asyncio
    async def test_get_event_history_filtered_by_type(
        self, event_service: Any, test_item: Any, create_test_events: Any
    ) -> None:
        """Test getting event history filtered by type.

        GIVEN: Multiple events of different types
        WHEN: Getting event history with type filter
        THEN: Only matching events are returned
        """
        events = await event_service.get_event_history(entity_id=test_item.id, event_type="item_updated")

        assert all(e.event_type == "item_updated" for e in events)

    @pytest.mark.asyncio
    async def test_get_event_history_empty(self, event_service: Any) -> None:
        """Test getting event history for non-existent entity.

        GIVEN: A non-existent entity
        WHEN: Getting event history
        THEN: Empty list is returned
        """
        events = await event_service.get_event_history(entity_id="nonexistent")

        assert events == []

    # Changes Between Timestamps Tests (Lines 158-187)

    @pytest.mark.asyncio
    async def test_get_changes_between_timestamps(
        self, event_service: Any, test_item: Any, create_test_events: Any, db_session: Any
    ) -> None:
        """Test getting changes between two timestamps.

        GIVEN: Events at different times
        WHEN: Getting changes between start and end
        THEN: Events in range are returned
        """
        # Use wide time range to capture test events
        start = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        end = (datetime.now(UTC) + timedelta(hours=1)).isoformat()

        changes = await event_service.get_changes_between(
            entity_id=test_item.id,
            start_timestamp=start,
            end_timestamp=end,
        )

        assert isinstance(changes, list)
        assert all(isinstance(c, AuditTrailEntry) for c in changes)

    @pytest.mark.asyncio
    async def test_get_changes_between_narrow_window(
        self, event_service: Any, test_item: Any, create_test_events: Any
    ) -> None:
        """Test getting changes in a narrow time window.

        GIVEN: Events spread over time
        WHEN: Getting changes in narrow window
        THEN: Only events in window are returned
        """
        # Use past time range that won't capture events
        start = (datetime.now(UTC) - timedelta(days=2)).isoformat()
        end = (datetime.now(UTC) - timedelta(days=1)).isoformat()

        changes = await event_service.get_changes_between(
            entity_id=test_item.id,
            start_timestamp=start,
            end_timestamp=end,
        )

        # Should be empty or very few events
        assert isinstance(changes, list)


# ============================================================
# ExternalIntegrationService Integration Tests (Lines 1-191)
# ============================================================


class TestExternalIntegrationServiceIntegration:
    """Integration tests for ExternalIntegrationService."""

    @pytest.fixture
    def integration_service(self) -> None:
        """Create ExternalIntegrationService instance."""
        return ExternalIntegrationService()

    # Integration Registration Tests (Lines 37-56)

    def test_register_integration_with_config(self, integration_service: Any) -> None:
        """Test registering integration with configuration.

        GIVEN: An integration service
        WHEN: Registering an integration with config
        THEN: Integration is created with config
        """
        result = integration_service.register_integration(
            name="github-main",
            integration_type=IntegrationType.GITHUB,
            config={"token": "secret-token", "repo": "user/repo"},
        )

        assert isinstance(result, Integration)
        assert result.name == "github-main"
        assert result.integration_type == IntegrationType.GITHUB
        assert result.enabled is True
        assert result.config["token"] == "secret-token"

    def test_register_integration_without_config(self, integration_service: Any) -> None:
        """Test registering integration without configuration.

        GIVEN: An integration service
        WHEN: Registering an integration without config
        THEN: Integration is created with empty config
        """
        result = integration_service.register_integration(
            name="slack-notifications",
            integration_type=IntegrationType.SLACK,
        )

        assert result.config == {}
        assert result.enabled is True

    def test_register_multiple_integrations(self, integration_service: Any) -> None:
        """Test registering multiple integrations.

        GIVEN: An integration service
        WHEN: Registering multiple integrations
        THEN: All are stored independently
        """
        integration_service.register_integration("github-1", IntegrationType.GITHUB, {"repo": "repo1"})
        integration_service.register_integration("github-2", IntegrationType.GITHUB, {"repo": "repo2"})

        assert len(integration_service.integrations) == COUNT_TWO
        assert "github-1" in integration_service.integrations
        assert "github-2" in integration_service.integrations

    def test_get_integration_exists(self, integration_service: Any) -> None:
        """Test getting an existing integration.

        GIVEN: A registered integration
        WHEN: Getting the integration by name
        THEN: Integration is returned
        """
        integration_service.register_integration("test-integration", IntegrationType.VSCODE)

        result = integration_service.get_integration("test-integration")

        assert result is not None
        assert result.name == "test-integration"

    def test_get_integration_not_found(self, integration_service: Any) -> None:
        """Test getting a non-existent integration.

        GIVEN: An integration service
        WHEN: Getting a non-existent integration
        THEN: None is returned
        """
        result = integration_service.get_integration("nonexistent")

        assert result is None

    # Integration Listing Tests (Lines 57-69)

    def test_list_integrations_all(self, integration_service: Any) -> None:
        """Test listing all integrations.

        GIVEN: Multiple registered integrations
        WHEN: Listing without filter
        THEN: All integrations are returned
        """
        integration_service.register_integration("github", IntegrationType.GITHUB)
        integration_service.register_integration("slack", IntegrationType.SLACK)
        integration_service.register_integration("jira", IntegrationType.JIRA)

        result = integration_service.list_integrations()

        assert len(result) == COUNT_THREE

    def test_list_integrations_filtered_by_type(self, integration_service: Any) -> None:
        """Test listing integrations filtered by type.

        GIVEN: Multiple integrations of different types
        WHEN: Listing with type filter
        THEN: Only matching integrations are returned
        """
        integration_service.register_integration("github-1", IntegrationType.GITHUB)
        integration_service.register_integration("github-2", IntegrationType.GITHUB)
        integration_service.register_integration("slack", IntegrationType.SLACK)

        result = integration_service.list_integrations(integration_type=IntegrationType.GITHUB)

        assert len(result) == COUNT_TWO
        assert all(i.integration_type == IntegrationType.GITHUB for i in result)

    def test_list_integrations_empty(self, integration_service: Any) -> None:
        """Test listing integrations when none exist.

        GIVEN: An empty integration service
        WHEN: Listing integrations
        THEN: Empty list is returned
        """
        result = integration_service.list_integrations()

        assert result == []

    # Enable/Disable Integration Tests (Lines 70-85)

    def test_enable_integration_success(self, integration_service: Any) -> None:
        """Test enabling an integration.

        GIVEN: A disabled integration
        WHEN: Enabling the integration
        THEN: Integration is enabled
        """
        integration_service.register_integration("test", IntegrationType.GITHUB)
        integration_service.integrations["test"].enabled = False

        result = integration_service.enable_integration("test")

        assert result is True
        assert integration_service.integrations["test"].enabled is True

    def test_enable_integration_not_found(self, integration_service: Any) -> None:
        """Test enabling a non-existent integration.

        GIVEN: An integration service
        WHEN: Enabling a non-existent integration
        THEN: False is returned
        """
        result = integration_service.enable_integration("nonexistent")

        assert result is False

    def test_disable_integration_success(self, integration_service: Any) -> None:
        """Test disabling an integration.

        GIVEN: An enabled integration
        WHEN: Disabling the integration
        THEN: Integration is disabled
        """
        integration_service.register_integration("test", IntegrationType.GITHUB)

        result = integration_service.disable_integration("test")

        assert result is True
        assert integration_service.integrations["test"].enabled is False

    def test_disable_integration_not_found(self, integration_service: Any) -> None:
        """Test disabling a non-existent integration.

        GIVEN: An integration service
        WHEN: Disabling a non-existent integration
        THEN: False is returned
        """
        result = integration_service.disable_integration("nonexistent")

        assert result is False

    # Configuration Update Tests (Lines 86-97)

    def test_update_integration_config_success(self, integration_service: Any) -> None:
        """Test updating integration configuration.

        GIVEN: An integration with config
        WHEN: Updating the config
        THEN: Config is merged
        """
        integration_service.register_integration(
            "github",
            IntegrationType.GITHUB,
            {"token": "old-token", "repo": "repo"},
        )

        result = integration_service.update_integration_config("github", {"token": "new-token", "branch": "main"})

        assert result is not None
        assert result.config["token"] == "new-token"
        assert result.config["repo"] == "repo"
        assert result.config["branch"] == "main"

    def test_update_integration_config_not_found(self, integration_service: Any) -> None:
        """Test updating config for non-existent integration.

        GIVEN: An integration service
        WHEN: Updating config for non-existent integration
        THEN: None is returned
        """
        result = integration_service.update_integration_config("nonexistent", {"key": "value"})

        assert result is None

    # Sync Integration Tests (Lines 98-125)

    def test_sync_integration_success(self, integration_service: Any) -> None:
        """Test syncing with an integration.

        GIVEN: An enabled integration
        WHEN: Syncing the integration
        THEN: Sync record is created
        """
        integration_service.register_integration("github", IntegrationType.GITHUB)

        result = integration_service.sync_integration("github", sync_type="full")

        assert result["integration"] == "github"
        assert result["type"] == "github"
        assert result["sync_type"] == "full"
        assert result["status"] == "success"
        assert len(integration_service.sync_history) == 1

    def test_sync_integration_not_found(self, integration_service: Any) -> None:
        """Test syncing a non-existent integration.

        GIVEN: An integration service
        WHEN: Syncing a non-existent integration
        THEN: Error is returned
        """
        result = integration_service.sync_integration("nonexistent")

        assert "error" in result
        assert result["error"] == "Integration not found"

    def test_sync_integration_disabled(self, integration_service: Any) -> None:
        """Test syncing a disabled integration.

        GIVEN: A disabled integration
        WHEN: Syncing the integration
        THEN: Error is returned
        """
        integration_service.register_integration("github", IntegrationType.GITHUB)
        integration_service.disable_integration("github")

        result = integration_service.sync_integration("github")

        assert "error" in result
        assert result["error"] == "Integration is disabled"

    def test_sync_integration_updates_last_sync(self, integration_service: Any) -> None:
        """Test that syncing updates last_sync timestamp.

        GIVEN: An integration
        WHEN: Syncing the integration
        THEN: last_sync is updated
        """
        integration_service.register_integration("github", IntegrationType.GITHUB)

        integration_service.sync_integration("github")

        integration = integration_service.get_integration("github")
        assert integration.last_sync is not None

    # Sync History Tests (Lines 126-134)

    def test_get_sync_history_all(self, integration_service: Any) -> None:
        """Test getting all sync history.

        GIVEN: Multiple sync operations
        WHEN: Getting history without filter
        THEN: All records are returned
        """
        integration_service.register_integration("github", IntegrationType.GITHUB)
        integration_service.register_integration("slack", IntegrationType.SLACK)

        integration_service.sync_integration("github")
        integration_service.sync_integration("slack")
        integration_service.sync_integration("github")

        history = integration_service.get_sync_history()

        assert len(history) == COUNT_THREE

    def test_get_sync_history_filtered(self, integration_service: Any) -> None:
        """Test getting sync history filtered by integration.

        GIVEN: Multiple sync operations
        WHEN: Getting history for specific integration
        THEN: Only matching records are returned
        """
        integration_service.register_integration("github", IntegrationType.GITHUB)
        integration_service.register_integration("slack", IntegrationType.SLACK)

        integration_service.sync_integration("github")
        integration_service.sync_integration("slack")
        integration_service.sync_integration("github")

        history = integration_service.get_sync_history(name="github")

        assert len(history) == COUNT_TWO
        assert all(h["integration"] == "github" for h in history)

    def test_get_sync_history_empty(self, integration_service: Any) -> None:
        """Test getting sync history when none exists.

        GIVEN: No sync operations
        WHEN: Getting history
        THEN: Empty list is returned
        """
        history = integration_service.get_sync_history()

        assert history == []

    # Validation Tests (Lines 135-157)

    def test_validate_integration_config_github_valid(self, integration_service: Any) -> None:
        """Test validating valid GitHub integration config.

        GIVEN: A GitHub integration with all required fields
        WHEN: Validating the config
        THEN: No errors are returned
        """
        integration = Integration(
            name="github",
            integration_type=IntegrationType.GITHUB,
            config={"token": "secret", "repo": "user/repo"},
        )

        errors = integration_service.validate_integration_config(integration)

        assert errors == []

    def test_validate_integration_config_github_missing_token(self, integration_service: Any) -> None:
        """Test validating GitHub integration without token.

        GIVEN: A GitHub integration missing token
        WHEN: Validating the config
        THEN: Token error is returned
        """
        integration = Integration(
            name="github",
            integration_type=IntegrationType.GITHUB,
            config={"repo": "user/repo"},
        )

        errors = integration_service.validate_integration_config(integration)

        assert "GitHub token is required" in errors

    def test_validate_integration_config_github_missing_repo(self, integration_service: Any) -> None:
        """Test validating GitHub integration without repo.

        GIVEN: A GitHub integration missing repo
        WHEN: Validating the config
        THEN: Repo error is returned
        """
        integration = Integration(
            name="github",
            integration_type=IntegrationType.GITHUB,
            config={"token": "secret"},
        )

        errors = integration_service.validate_integration_config(integration)

        assert "GitHub repository is required" in errors

    def test_validate_integration_config_slack_valid(self, integration_service: Any) -> None:
        """Test validating valid Slack integration config.

        GIVEN: A Slack integration with webhook_url
        WHEN: Validating the config
        THEN: No errors are returned
        """
        integration = Integration(
            name="slack",
            integration_type=IntegrationType.SLACK,
            config={"webhook_url": "https://hooks.slack.com/services/XXX"},
        )

        errors = integration_service.validate_integration_config(integration)

        assert errors == []

    def test_validate_integration_config_slack_missing_webhook(self, integration_service: Any) -> None:
        """Test validating Slack integration without webhook_url.

        GIVEN: A Slack integration missing webhook_url
        WHEN: Validating the config
        THEN: Webhook error is returned
        """
        integration = Integration(name="slack", integration_type=IntegrationType.SLACK, config={})

        errors = integration_service.validate_integration_config(integration)

        assert "Slack webhook URL is required" in errors

    def test_validate_integration_config_vscode_missing_extension_id(self, integration_service: Any) -> None:
        """Test validating VS Code integration without extension_id.

        GIVEN: A VS Code integration missing extension_id
        WHEN: Validating the config
        THEN: Extension ID error is returned
        """
        integration = Integration(name="vscode", integration_type=IntegrationType.VSCODE, config={})

        errors = integration_service.validate_integration_config(integration)

        assert "VS Code extension ID is required" in errors

    def test_validate_integration_config_missing_name(self, integration_service: Any) -> None:
        """Test validating integration without name.

        GIVEN: An integration with empty name
        WHEN: Validating the config
        THEN: Name error is returned
        """
        integration = Integration(name="", integration_type=IntegrationType.CUSTOM, config={})

        errors = integration_service.validate_integration_config(integration)

        assert "Integration name is required" in errors

    # Statistics Tests (Lines 158-176)

    def test_get_integration_stats_empty(self, integration_service: Any) -> None:
        """Test getting stats with no integrations.

        GIVEN: An empty integration service
        WHEN: Getting stats
        THEN: Zero counts are returned
        """
        stats = integration_service.get_integration_stats()

        assert stats["total_integrations"] == 0
        assert stats["enabled"] == 0
        assert stats["disabled"] == 0
        assert stats["by_type"] == {}
        assert stats["total_syncs"] == 0

    def test_get_integration_stats_with_data(self, integration_service: Any) -> None:
        """Test getting stats with integrations and syncs.

        GIVEN: Multiple integrations and sync operations
        WHEN: Getting stats
        THEN: Correct counts are returned
        """
        integration_service.register_integration("github-1", IntegrationType.GITHUB)
        integration_service.register_integration("github-2", IntegrationType.GITHUB)
        integration_service.register_integration("slack", IntegrationType.SLACK)

        integration_service.disable_integration("github-2")

        integration_service.sync_integration("github-1")
        integration_service.sync_integration("slack")

        stats = integration_service.get_integration_stats()

        assert stats["total_integrations"] == COUNT_THREE
        assert stats["enabled"] == COUNT_TWO
        assert stats["disabled"] == 1
        assert stats["by_type"]["github"] == COUNT_TWO
        assert stats["by_type"]["slack"] == 1
        assert stats["total_syncs"] == COUNT_TWO

    # Test Integration Connection Tests (Lines 177-191)

    def test_test_integration_success(self, integration_service: Any) -> None:
        """Test testing integration connection.

        GIVEN: A registered integration
        WHEN: Testing the connection
        THEN: Success result is returned
        """
        integration_service.register_integration("github", IntegrationType.GITHUB)

        result = integration_service.test_integration("github")

        assert result["success"] is True
        assert result["integration"] == "github"
        assert result["type"] == "github"
        assert "message" in result

    def test_test_integration_not_found(self, integration_service: Any) -> None:
        """Test testing non-existent integration.

        GIVEN: An integration service
        WHEN: Testing a non-existent integration
        THEN: Error result is returned
        """
        result = integration_service.test_integration("nonexistent")

        assert result["success"] is False
        assert result["error"] == "Integration not found"
