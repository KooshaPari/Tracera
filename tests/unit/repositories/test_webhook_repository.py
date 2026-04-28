"""Tests for WebhookRepository.

Comprehensive tests covering webhook integration CRUD operations, rate limiting,
request logging, and statistics.

Functional Requirements Coverage:
    - FR-DISC-005: Webhook Ingestion
    - FR-COLLAB-001: External Tool Integration

Epics:
    - EPIC-001: External Integration

Tests verify webhook creation, provider configuration, rate limiting,
request logging, delivery tracking, and webhook statistics.
"""

# ==================== Fixtures ====================
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO, HTTP_OK
from tracertm.models.webhook_integration import WebhookProvider, WebhookStatus
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.webhook_repository import WebhookRepository


@pytest_asyncio.fixture
async def project_setup(db_session: AsyncSession) -> None:
    """Create a project for webhook tests."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(
        name="Test Project",
        description="Project for webhook tests",
    )
    return {"project": project, "session": db_session}


@pytest_asyncio.fixture
async def webhook_setup(project_setup: Any) -> None:
    """Create a project with a webhook for testing."""
    session = project_setup["session"]
    project = project_setup["project"]
    repo = WebhookRepository(session)

    webhook = await repo.create(
        project_id=str(project.id),
        name="Test Webhook",
        description="Test webhook for unit tests",
        provider="custom",
        callback_url="https://example.com/webhook",
    )

    return {
        "project": project,
        "webhook": webhook,
        "repo": repo,
        "session": session,
    }


# ==================== Create Tests ====================


class TestWebhookCreate:
    """Tests for WebhookRepository.create."""

    @pytest.mark.asyncio
    async def test_create_minimal(self, project_setup: Any) -> None:
        """Test creating a webhook with minimal fields."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        webhook = await repo.create(
            project_id=str(project.id),
            name="Minimal Webhook",
        )

        assert webhook is not None
        assert webhook.id is not None
        assert webhook.project_id == project.id
        assert webhook.name == "Minimal Webhook"
        assert webhook.status == WebhookStatus.ACTIVE
        assert webhook.provider == WebhookProvider.CUSTOM

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, project_setup: Any) -> None:
        """Test creating a webhook with all fields."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        webhook = await repo.create(
            project_id=str(project.id),
            name="Full Webhook",
            description="Webhook with all fields",
            provider="github_actions",
            enabled_events=["push", "pull_request"],
            event_filters={"branches": ["main"]},
            callback_url="https://example.com/callback",
            callback_headers={"X-Custom-Header": "value"},
            rate_limit_per_minute=100,
            auto_create_run=True,
            auto_complete_run=False,
            verify_signatures=True,
            metadata={"key": "value"},
        )

        assert webhook.name == "Full Webhook"
        assert webhook.description == "Webhook with all fields"
        assert webhook.provider == WebhookProvider.GITHUB_ACTIONS
        assert webhook.enabled_events == ["push", "pull_request"]
        assert webhook.event_filters == {"branches": ["main"]}
        assert webhook.callback_url == "https://example.com/callback"
        assert webhook.callback_headers == {"X-Custom-Header": "value"}
        assert webhook.rate_limit_per_minute == 100
        assert webhook.auto_create_run is True
        assert webhook.auto_complete_run is False
        assert webhook.verify_signatures is True
        assert webhook.webhook_metadata == {"key": "value"}

    @pytest.mark.asyncio
    async def test_create_different_providers(self, project_setup: Any) -> None:
        """Test creating webhooks with different providers."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        providers = ["custom", "github_actions", "gitlab_ci", "jenkins", "azure_devops", "circleci", "travis_ci"]
        for provider_name in providers:
            webhook = await repo.create(
                project_id=str(project.id),
                name=f"{provider_name} Webhook",
                provider=provider_name,
            )
            assert webhook.provider == WebhookProvider(provider_name)

    @pytest.mark.asyncio
    async def test_create_generates_uuid(self, project_setup: Any) -> None:
        """Test that create generates a valid UUID."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        webhook = await repo.create(
            project_id=str(project.id),
            name="UUID Test Webhook",
        )

        # Verify it's a valid UUID format
        assert len(webhook.id) == 36
        assert webhook.id.count("-") == COUNT_FOUR

    @pytest.mark.asyncio
    async def test_create_default_enabled_events(self, project_setup: Any) -> None:
        """Test that default enabled events are set."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        webhook = await repo.create(
            project_id=str(project.id),
            name="Default Events Webhook",
        )

        events = webhook.enabled_events or []
        assert "test_run_start" in events
        assert "test_run_complete" in events
        assert "test_result_submit" in events
        assert "bulk_results" in events


# ==================== Get Tests ====================


class TestWebhookGet:
    """Tests for WebhookRepository.get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, webhook_setup: Any) -> None:
        """Test getting a webhook by ID."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        result = await repo.get_by_id(webhook.id)

        assert result is not None
        assert result.id == webhook.id
        assert result.name == webhook.name

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, webhook_setup: Any) -> None:
        """Test getting a non-existent webhook."""
        repo = webhook_setup["repo"]

        result = await repo.get_by_id(str(uuid4()))

        assert result is None


# ==================== List Tests ====================


class TestWebhookList:
    """Tests for WebhookRepository.list_by_project."""

    @pytest.mark.asyncio
    async def test_list_by_project_empty(self, project_setup: Any) -> None:
        """Test listing webhooks for project with no webhooks."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        webhooks, total = await repo.list_by_project(str(project.id))

        assert webhooks == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_by_project_multiple(self, project_setup: Any) -> None:
        """Test listing multiple webhooks."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        # Create multiple webhooks
        for i in range(5):
            await repo.create(
                project_id=str(project.id),
                name=f"Webhook {i}",
            )

        webhooks, total = await repo.list_by_project(str(project.id))

        assert len(webhooks) == COUNT_FIVE
        assert total == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_list_by_project_filter_provider(self, project_setup: Any) -> None:
        """Test filtering webhooks by provider."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        # Create webhooks with different providers
        await repo.create(project_id=str(project.id), name="Custom 1", provider="custom")
        await repo.create(project_id=str(project.id), name="GitHub 1", provider="github_actions")
        await repo.create(project_id=str(project.id), name="Custom 2", provider="custom")

        webhooks, total = await repo.list_by_project(str(project.id), provider=WebhookProvider.CUSTOM)

        assert len(webhooks) == COUNT_TWO
        assert total == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_by_project_filter_status(self, project_setup: Any) -> None:
        """Test filtering webhooks by status."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        # Create webhooks and change some statuses
        await repo.create(project_id=str(project.id), name="Active")
        wh2 = await repo.create(project_id=str(project.id), name="Paused")
        await repo.set_status(wh2.id, "paused")

        webhooks, _total = await repo.list_by_project(str(project.id), status=WebhookStatus.ACTIVE)

        assert len(webhooks) == 1
        assert webhooks[0].name == "Active"

    @pytest.mark.asyncio
    async def test_list_by_project_pagination(self, project_setup: Any) -> None:
        """Test pagination of webhook list."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        # Create 10 webhooks
        for i in range(10):
            await repo.create(project_id=str(project.id), name=f"Webhook {i}")

        # Get first page
        page1, total = await repo.list_by_project(str(project.id), skip=0, limit=3)
        assert len(page1) == COUNT_THREE
        assert total == COUNT_TEN

        # Get second page
        page2, _ = await repo.list_by_project(str(project.id), skip=3, limit=3)
        assert len(page2) == COUNT_THREE

        # Ensure different results
        page1_ids = {w.id for w in page1}
        page2_ids = {w.id for w in page2}
        assert page1_ids.isdisjoint(page2_ids)


# ==================== Update Tests ====================


class TestWebhookUpdate:
    """Tests for WebhookRepository.update."""

    @pytest.mark.asyncio
    async def test_update_name(self, webhook_setup: Any) -> None:
        """Test updating webhook name."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        result = await repo.update(webhook.id, name="Updated Name")

        assert result is not None
        assert result.name == "Updated Name"
        assert result.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self, webhook_setup: Any) -> None:
        """Test updating multiple fields."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        result = await repo.update(
            webhook.id,
            name="New Name",
            description="New Description",
            callback_url="https://new.example.com",
            rate_limit_per_minute=200,
        )

        assert result.name == "New Name"
        assert result.description == "New Description"
        assert result.callback_url == "https://new.example.com"
        assert result.rate_limit_per_minute == HTTP_OK

    @pytest.mark.asyncio
    async def test_update_not_found(self, webhook_setup: Any) -> None:
        """Test updating a non-existent webhook."""
        repo = webhook_setup["repo"]

        result = await repo.update(str(uuid4()), name="New Name")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_increments_version(self, webhook_setup: Any) -> None:
        """Test that update increments version."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        initial_version = webhook.version

        await repo.update(webhook.id, name="V2")
        await repo.update(webhook.id, name="V3")
        await repo.update(webhook.id, name="V4")

        result = await repo.get_by_id(webhook.id)
        assert result.version == initial_version + 3


# ==================== Set Status Tests ====================


class TestWebhookSetStatus:
    """Tests for WebhookRepository.set_status."""

    @pytest.mark.asyncio
    async def test_set_status_paused(self, webhook_setup: Any) -> None:
        """Test pausing a webhook."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        result = await repo.set_status(webhook.id, "paused")

        assert result is not None
        assert result.status == WebhookStatus.PAUSED

    @pytest.mark.asyncio
    async def test_set_status_disabled(self, webhook_setup: Any) -> None:
        """Test disabling a webhook."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        result = await repo.set_status(webhook.id, "disabled")

        assert result.status == WebhookStatus.DISABLED

    @pytest.mark.asyncio
    async def test_set_status_active(self, webhook_setup: Any) -> None:
        """Test reactivating a webhook."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        # First pause
        await repo.set_status(webhook.id, "paused")
        # Then reactivate
        result = await repo.set_status(webhook.id, "active")

        assert result.status == WebhookStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_set_status_not_found(self, webhook_setup: Any) -> None:
        """Test setting status on non-existent webhook."""
        repo = webhook_setup["repo"]

        result = await repo.set_status(str(uuid4()), "paused")

        assert result is None


# ==================== Regenerate Secret Tests ====================


class TestWebhookRegenerateSecret:
    """Tests for WebhookRepository.regenerate_secret."""

    @pytest.mark.asyncio
    async def test_regenerate_secret(self, webhook_setup: Any) -> None:
        """Test regenerating webhook secret."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        original_secret = webhook.webhook_secret

        result = await repo.regenerate_secret(webhook.id)

        assert result is not None
        assert result.webhook_secret != original_secret
        assert len(result.webhook_secret) > 20  # Should be a long token

    @pytest.mark.asyncio
    async def test_regenerate_secret_not_found(self, webhook_setup: Any) -> None:
        """Test regenerating secret for non-existent webhook."""
        repo = webhook_setup["repo"]

        result = await repo.regenerate_secret(str(uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_regenerate_secret_increments_version(self, webhook_setup: Any) -> None:
        """Test that regenerating secret increments version."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        initial_version = webhook.version

        await repo.regenerate_secret(webhook.id)

        result = await repo.get_by_id(webhook.id)
        assert result.version == initial_version + 1


# ==================== Delete Tests ====================


class TestWebhookDelete:
    """Tests for WebhookRepository.delete."""

    @pytest.mark.asyncio
    async def test_delete_success(self, webhook_setup: Any) -> None:
        """Test deleting a webhook."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        result = await repo.delete(webhook.id)

        assert result is True

        # Verify deleted
        fetched = await repo.get_by_id(webhook.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, webhook_setup: Any) -> None:
        """Test deleting a non-existent webhook."""
        repo = webhook_setup["repo"]

        result = await repo.delete(str(uuid4()))

        assert result is False


# ==================== Rate Limit Tests ====================


class TestWebhookRateLimit:
    """Tests for WebhookRepository.check_rate_limit."""

    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self, webhook_setup: Any) -> None:
        """Test rate limit when allowed."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        allowed, remaining = await repo.check_rate_limit(webhook.id)

        assert allowed is True
        assert remaining >= 0

    @pytest.mark.asyncio
    async def test_check_rate_limit_exhausted(self, project_setup: Any) -> None:
        """Test rate limit when exhausted."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        # Create webhook with low rate limit
        webhook = await repo.create(
            project_id=str(project.id),
            name="Low Limit Webhook",
            rate_limit_per_minute=3,
        )

        # Exhaust the rate limit
        for _ in range(3):
            await repo.check_rate_limit(webhook.id)

        # Next request should be denied
        allowed, remaining = await repo.check_rate_limit(webhook.id)

        assert allowed is False
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_check_rate_limit_not_found(self, webhook_setup: Any) -> None:
        """Test rate limit check for non-existent webhook."""
        repo = webhook_setup["repo"]

        allowed, remaining = await repo.check_rate_limit(str(uuid4()))

        assert allowed is False
        assert remaining == 0


# ==================== Record Request Tests ====================


class TestWebhookRecordRequest:
    """Tests for WebhookRepository.record_request."""

    @pytest.mark.asyncio
    async def test_record_successful_request(self, webhook_setup: Any) -> None:
        """Test recording a successful request."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        await repo.record_request(webhook.id, success=True)

        result = await repo.get_by_id(webhook.id)
        assert result.total_requests == 1
        assert result.successful_requests == 1
        assert result.failed_requests == 0
        assert result.last_success_at is not None

    @pytest.mark.asyncio
    async def test_record_failed_request(self, webhook_setup: Any) -> None:
        """Test recording a failed request."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        await repo.record_request(webhook.id, success=False, error_message="Connection timeout")

        result = await repo.get_by_id(webhook.id)
        assert result.total_requests == 1
        assert result.successful_requests == 0
        assert result.failed_requests == 1
        assert result.last_failure_at is not None
        assert result.last_error_message == "Connection timeout"

    @pytest.mark.asyncio
    async def test_record_multiple_requests(self, webhook_setup: Any) -> None:
        """Test recording multiple requests."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        await repo.record_request(webhook.id, success=True)
        await repo.record_request(webhook.id, success=True)
        await repo.record_request(webhook.id, success=False)

        result = await repo.get_by_id(webhook.id)
        assert result.total_requests == COUNT_THREE
        assert result.successful_requests == COUNT_TWO
        assert result.failed_requests == 1

    @pytest.mark.asyncio
    async def test_record_request_not_found(self, webhook_setup: Any) -> None:
        """Test recording request for non-existent webhook (no error)."""
        repo = webhook_setup["repo"]

        # Should not raise an error
        await repo.record_request(str(uuid4()), success=True)


# ==================== Log Tests ====================


class TestWebhookLogs:
    """Tests for WebhookRepository log operations."""

    @pytest.mark.asyncio
    async def test_create_log(self, webhook_setup: Any) -> None:
        """Test creating a webhook log."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        log = await repo.create_log(
            webhook_id=webhook.id,
            event_type="test_run_complete",
            http_method="POST",
            source_ip="192.168.1.1",
            success=True,
            status_code=200,
        )

        assert log is not None
        assert log.webhook_id == webhook.id
        assert log.event_type == "test_run_complete"
        assert log.http_method == "POST"
        assert log.source_ip == "192.168.1.1"
        assert log.success is True
        assert log.status_code == HTTP_OK

    @pytest.mark.asyncio
    async def test_create_log_with_all_fields(self, webhook_setup: Any) -> None:
        """Test creating a log with all fields."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        log = await repo.create_log(
            webhook_id=webhook.id,
            event_type="bulk_results",
            http_method="POST",
            source_ip="10.0.0.1",
            user_agent="TestRunner/1.0",
            request_headers={"Content-Type": "application/json"},
            request_body_preview='{"results": [...]}',
            payload_size_bytes=1024,
            success=True,
            status_code=201,
            processing_time_ms=150,
            test_run_id=str(uuid4()),
            results_submitted=50,
        )

        assert log.user_agent == "TestRunner/1.0"
        assert log.request_headers == {"Content-Type": "application/json"}
        assert log.payload_size_bytes == 1024
        assert log.processing_time_ms == 150
        assert log.results_submitted == 50

    @pytest.mark.asyncio
    async def test_get_logs_empty(self, webhook_setup: Any) -> None:
        """Test getting logs when none exist."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        logs, total = await repo.get_logs(webhook.id)

        assert logs == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_logs_multiple(self, webhook_setup: Any) -> None:
        """Test getting multiple logs."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        # Create multiple logs
        for i in range(5):
            await repo.create_log(
                webhook_id=webhook.id,
                event_type=f"event_{i}",
                success=True,
            )

        logs, total = await repo.get_logs(webhook.id)

        assert len(logs) == COUNT_FIVE
        assert total == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_get_logs_filter_success(self, webhook_setup: Any) -> None:
        """Test filtering logs by success status."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        await repo.create_log(webhook_id=webhook.id, success=True)
        await repo.create_log(webhook_id=webhook.id, success=False)
        await repo.create_log(webhook_id=webhook.id, success=True)

        logs, total = await repo.get_logs(webhook.id, success=True)

        assert len(logs) == COUNT_TWO
        assert total == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_logs_filter_event_type(self, webhook_setup: Any) -> None:
        """Test filtering logs by event type."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        await repo.create_log(webhook_id=webhook.id, event_type="push")
        await repo.create_log(webhook_id=webhook.id, event_type="pull_request")
        await repo.create_log(webhook_id=webhook.id, event_type="push")

        logs, total = await repo.get_logs(webhook.id, event_type="push")

        assert len(logs) == COUNT_TWO
        assert total == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_logs_pagination(self, webhook_setup: Any) -> None:
        """Test log pagination."""
        repo = webhook_setup["repo"]
        webhook = webhook_setup["webhook"]

        for i in range(10):
            await repo.create_log(webhook_id=webhook.id, event_type=f"event_{i}")

        page1, total = await repo.get_logs(webhook.id, skip=0, limit=3)
        page2, _ = await repo.get_logs(webhook.id, skip=3, limit=3)

        assert len(page1) == COUNT_THREE
        assert len(page2) == COUNT_THREE
        assert total == COUNT_TEN


# ==================== Stats Tests ====================


class TestWebhookStats:
    """Tests for WebhookRepository.get_stats."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, project_setup: Any) -> None:
        """Test getting stats for project with no webhooks."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        stats = await repo.get_stats(str(project.id))

        assert stats["project_id"] == project.id
        assert stats["total"] == 0
        assert stats["total_requests"] == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_webhooks(self, project_setup: Any) -> None:
        """Test getting stats with multiple webhooks."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        # Create webhooks with different providers and statuses
        wh1 = await repo.create(project_id=str(project.id), name="WH1", provider="github_actions")
        wh2 = await repo.create(project_id=str(project.id), name="WH2", provider="github_actions")
        await repo.create(project_id=str(project.id), name="WH3", provider="custom")

        # Record some requests
        await repo.record_request(wh1.id, success=True)
        await repo.record_request(wh1.id, success=True)
        await repo.record_request(wh2.id, success=False)

        stats = await repo.get_stats(str(project.id))

        assert stats["total"] == COUNT_THREE
        assert stats["by_provider"]["github_actions"] == COUNT_TWO
        assert stats["by_provider"]["custom"] == 1
        assert stats["total_requests"] == COUNT_THREE
        assert stats["successful_requests"] == COUNT_TWO
        assert stats["failed_requests"] == 1

    @pytest.mark.asyncio
    async def test_get_stats_by_status(self, project_setup: Any) -> None:
        """Test stats grouped by status."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = WebhookRepository(session)

        await repo.create(project_id=str(project.id), name="Active1")
        wh2 = await repo.create(project_id=str(project.id), name="Paused1")
        await repo.create(project_id=str(project.id), name="Active2")

        await repo.set_status(wh2.id, "paused")

        stats = await repo.get_stats(str(project.id))

        assert stats["by_status"]["active"] == COUNT_TWO
        assert stats["by_status"]["paused"] == 1
