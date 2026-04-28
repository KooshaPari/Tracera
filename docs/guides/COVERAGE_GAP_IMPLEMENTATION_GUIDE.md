# Test Coverage Gap Implementation Guide

This guide provides detailed test implementations for the identified coverage gaps in the Python backend test suite.

---

## Priority 1: Event Service Tests (CRITICAL)

### Gap Summary
- **Current:** 0 tests
- **Impact:** Event sourcing, audit trail, compliance
- **Required:** 25-30 comprehensive tests
- **Time Estimate:** 16 hours

### Implementation Guide

#### File: `tests/unit/services/test_event_service_comprehensive.py`

```python
"""
Comprehensive Event Service Tests

Tests for event sourcing, auditing, and domain events.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock, MagicMock

from tracertm.services.event_service import EventService
from tracertm.models.event import Event, EventType
from tracertm.repositories.event_repository import EventRepository


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventServiceCreation:
    """Tests for event creation functionality."""

    async def test_create_event_with_all_fields(self, event_service: EventService):
        """Test creating event with all required fields."""
        # Arrange
        event_type = EventType.ITEM_CREATED
        actor_id = "agent_123"
        entity_id = "item_456"
        metadata = {"priority": "high", "source": "api"}

        # Act
        event = await event_service.create_event(
            event_type=event_type,
            actor_id=actor_id,
            entity_id=entity_id,
            metadata=metadata
        )

        # Assert
        assert event.id is not None
        assert event.event_type == event_type
        assert event.actor_id == actor_id
        assert event.entity_id == entity_id
        assert event.metadata == metadata
        assert isinstance(event.timestamp, datetime)

    async def test_create_event_with_minimal_fields(self, event_service: EventService):
        """Test creating event with only required fields."""
        event = await event_service.create_event(
            event_type=EventType.ITEM_CREATED,
            actor_id="agent_1",
            entity_id="item_1"
        )

        assert event.id is not None
        assert event.metadata == {}

    async def test_create_event_with_none_metadata(self, event_service: EventService):
        """Test that None metadata converts to empty dict."""
        event = await event_service.create_event(
            event_type=EventType.ITEM_UPDATED,
            actor_id="agent_1",
            entity_id="item_1",
            metadata=None
        )

        assert event.metadata == {}

    async def test_create_event_with_empty_metadata(self, event_service: EventService):
        """Test creating event with empty metadata dict."""
        event = await event_service.create_event(
            event_type=EventType.LINK_CREATED,
            actor_id="agent_1",
            entity_id="link_1",
            metadata={}
        )

        assert event.metadata == {}

    async def test_create_event_with_complex_metadata(self, event_service: EventService):
        """Test event with nested and complex metadata."""
        metadata = {
            "changes": {
                "title": {"from": "Old", "to": "New"},
                "status": {"from": "pending", "to": "active"}
            },
            "tags": ["important", "urgent"],
            "nested": {
                "deep": {
                    "value": "test"
                }
            }
        }

        event = await event_service.create_event(
            event_type=EventType.ITEM_UPDATED,
            actor_id="agent_1",
            entity_id="item_1",
            metadata=metadata
        )

        assert event.metadata == metadata

    async def test_create_event_stores_in_repository(
        self, event_service: EventService, mock_event_repository: AsyncMock
    ):
        """Test that created event is stored in repository."""
        mock_event_repository.save.return_value = None

        event = await event_service.create_event(
            event_type=EventType.ITEM_CREATED,
            actor_id="agent_1",
            entity_id="item_1"
        )

        mock_event_repository.save.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventServiceRetrieval:
    """Tests for event retrieval and querying."""

    async def test_get_event_by_id(self, event_service: EventService, sample_event: Event):
        """Test retrieving event by ID."""
        event = await event_service.get_event(sample_event.id)

        assert event is not None
        assert event.id == sample_event.id

    async def test_get_nonexistent_event_returns_none(self, event_service: EventService):
        """Test that nonexistent event returns None."""
        event = await event_service.get_event("nonexistent_id")

        assert event is None

    async def test_get_events_by_entity(self, event_service: EventService):
        """Test retrieving all events for an entity."""
        # Create multiple events for same entity
        entity_id = "item_123"
        event_ids = []

        for i in range(5):
            event = await event_service.create_event(
                event_type=EventType.ITEM_CREATED if i == 0 else EventType.ITEM_UPDATED,
                actor_id=f"agent_{i}",
                entity_id=entity_id
            )
            event_ids.append(event.id)

        # Retrieve events
        events = await event_service.get_events_by_entity(entity_id)

        assert len(events) == 5
        assert all(e.entity_id == entity_id for e in events)

    async def test_get_events_by_actor(self, event_service: EventService):
        """Test retrieving all events by actor."""
        actor_id = "agent_001"

        for i in range(3):
            await event_service.create_event(
                event_type=EventType.ITEM_CREATED,
                actor_id=actor_id,
                entity_id=f"item_{i}"
            )

        events = await event_service.get_events_by_actor(actor_id)

        assert len(events) == 3
        assert all(e.actor_id == actor_id for e in events)

    async def test_get_events_by_type(self, event_service: EventService):
        """Test retrieving events by type."""
        event_type = EventType.ITEM_CREATED

        for i in range(3):
            await event_service.create_event(
                event_type=event_type,
                actor_id="agent_1",
                entity_id=f"item_{i}"
            )

        events = await event_service.get_events_by_type(event_type)

        assert len(events) >= 3
        assert all(e.event_type == event_type for e in events)

    async def test_get_events_by_date_range(self, event_service: EventService):
        """Test retrieving events within date range."""
        now = datetime.now()
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)

        event = await event_service.create_event(
            event_type=EventType.ITEM_CREATED,
            actor_id="agent_1",
            entity_id="item_1"
        )

        events = await event_service.get_events_by_date_range(start, end)

        assert len(events) > 0
        assert event.id in [e.id for e in events]


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventServiceFiltering:
    """Tests for event filtering and querying."""

    async def test_filter_events_by_multiple_criteria(
        self, event_service: EventService
    ):
        """Test filtering events with multiple criteria."""
        actor_id = "agent_1"
        entity_id = "item_1"

        await event_service.create_event(
            event_type=EventType.ITEM_CREATED,
            actor_id=actor_id,
            entity_id=entity_id
        )

        events = await event_service.filter_events(
            actor_id=actor_id,
            entity_id=entity_id
        )

        assert len(events) > 0
        assert all(e.actor_id == actor_id and e.entity_id == entity_id for e in events)

    async def test_filter_events_empty_result(self, event_service: EventService):
        """Test filtering that returns no results."""
        events = await event_service.filter_events(
            actor_id="nonexistent_agent"
        )

        assert events == []


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventServiceReplay:
    """Tests for event replay and state reconstruction."""

    async def test_replay_events_single_item(self, event_service: EventService):
        """Test replaying events to reconstruct item state."""
        entity_id = "item_123"

        # Create sequence of events
        events = []
        for event_type in [
            EventType.ITEM_CREATED,
            EventType.ITEM_UPDATED,
            EventType.ITEM_UPDATED
        ]:
            event = await event_service.create_event(
                event_type=event_type,
                actor_id="agent_1",
                entity_id=entity_id,
                metadata={"version": len(events) + 1}
            )
            events.append(event)

        # Replay events
        state = await event_service.replay_events(entity_id)

        assert state is not None
        assert state.get("version") == 3

    async def test_replay_events_from_timestamp(self, event_service: EventService):
        """Test replaying events from specific timestamp."""
        entity_id = "item_1"
        now = datetime.now()

        await event_service.create_event(
            event_type=EventType.ITEM_CREATED,
            actor_id="agent_1",
            entity_id=entity_id
        )

        future = now + timedelta(hours=1)

        await event_service.create_event(
            event_type=EventType.ITEM_UPDATED,
            actor_id="agent_1",
            entity_id=entity_id
        )

        # Replay from future time - should not include recent event
        state = await event_service.replay_events_from(entity_id, future)

        # State should not reflect the update
        assert state is not None


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventServiceConcurrency:
    """Tests for concurrent event handling."""

    async def test_concurrent_event_creation(self, event_service: EventService):
        """Test creating events concurrently."""
        tasks = [
            event_service.create_event(
                event_type=EventType.ITEM_CREATED,
                actor_id=f"agent_{i}",
                entity_id=f"item_{i}"
            )
            for i in range(100)
        ]

        events = await asyncio.gather(*tasks)

        assert len(events) == 100
        assert len(set(e.id for e in events)) == 100

    async def test_concurrent_events_for_same_entity(self, event_service: EventService):
        """Test concurrent events for same entity maintain order."""
        entity_id = "item_shared"
        event_count = 50

        tasks = [
            event_service.create_event(
                event_type=EventType.ITEM_UPDATED,
                actor_id=f"agent_{i}",
                entity_id=entity_id
            )
            for i in range(event_count)
        ]

        events = await asyncio.gather(*tasks)

        # All events created
        assert len(events) == event_count

        # Retrieve and verify order maintained
        stored_events = await event_service.get_events_by_entity(entity_id)

        assert len(stored_events) == event_count


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventServiceValidation:
    """Tests for event validation."""

    async def test_create_event_with_invalid_type(self, event_service: EventService):
        """Test that invalid event type raises error."""
        with pytest.raises(ValueError, match="Invalid event type"):
            await event_service.create_event(
                event_type="invalid_type",
                actor_id="agent_1",
                entity_id="item_1"
            )

    async def test_create_event_with_none_actor_id(self, event_service: EventService):
        """Test that None actor_id raises error."""
        with pytest.raises(ValueError, match="actor_id required"):
            await event_service.create_event(
                event_type=EventType.ITEM_CREATED,
                actor_id=None,
                entity_id="item_1"
            )

    async def test_create_event_with_empty_actor_id(self, event_service: EventService):
        """Test that empty actor_id raises error."""
        with pytest.raises(ValueError, match="actor_id cannot be empty"):
            await event_service.create_event(
                event_type=EventType.ITEM_CREATED,
                actor_id="",
                entity_id="item_1"
            )

    async def test_create_event_with_none_entity_id(self, event_service: EventService):
        """Test that None entity_id raises error."""
        with pytest.raises(ValueError, match="entity_id required"):
            await event_service.create_event(
                event_type=EventType.ITEM_CREATED,
                actor_id="agent_1",
                entity_id=None
            )

    async def test_metadata_with_invalid_json_types(self, event_service: EventService):
        """Test that non-JSON-serializable metadata raises error."""
        with pytest.raises(ValueError, match="non-serializable"):
            await event_service.create_event(
                event_type=EventType.ITEM_CREATED,
                actor_id="agent_1",
                entity_id="item_1",
                metadata={"func": lambda x: x}  # Not JSON serializable
            )


@pytest.mark.unit
@pytest.mark.asyncio
class TestEventServiceArchival:
    """Tests for event archival and cleanup."""

    async def test_archive_old_events(self, event_service: EventService):
        """Test archiving events older than specified date."""
        cutoff_date = datetime.now() - timedelta(days=30)

        # Create some events before cutoff (would need time manipulation)
        archived_count = await event_service.archive_events_before(cutoff_date)

        assert archived_count >= 0

    async def test_delete_archived_events(self, event_service: EventService):
        """Test deleting archived events."""
        deleted_count = await event_service.delete_archived_events()

        assert deleted_count >= 0

    async def test_cleanup_events_by_retention_policy(self, event_service: EventService):
        """Test cleanup based on retention policy."""
        # Create event and wait
        event = await event_service.create_event(
            event_type=EventType.ITEM_CREATED,
            actor_id="agent_1",
            entity_id="item_1"
        )

        # Cleanup with retention of 0 days
        deleted = await event_service.cleanup_expired_events(retention_days=0)

        # Event should be eligible for cleanup
        assert deleted >= 0


# Test Fixtures

@pytest.fixture
async def event_service(mock_event_repository):
    """Create event service with mocked repository."""
    service = EventService(repository=mock_event_repository)
    yield service


@pytest.fixture
def mock_event_repository():
    """Mock event repository."""
    repo = AsyncMock(spec=EventRepository)
    repo.save = AsyncMock(return_value=None)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_entity = AsyncMock(return_value=[])
    repo.get_by_actor = AsyncMock(return_value=[])
    repo.get_by_type = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def sample_event():
    """Create sample event for testing."""
    from tracertm.models.event import Event

    return Event(
        id="event_123",
        event_type=EventType.ITEM_CREATED,
        actor_id="agent_1",
        entity_id="item_1",
        metadata={"test": True},
        timestamp=datetime.now()
    )
```

---

## Priority 2: GitHub Integration Tests (CRITICAL)

### Gap Summary
- **Current:** 0 tests
- **Impact:** GitHub import workflows, authentication
- **Required:** 25-35 comprehensive tests
- **Time Estimate:** 16 hours

### Implementation Guide

#### File: `tests/integration/test_github_integration_comprehensive.py`

```python
"""
GitHub Integration Service Tests

Tests for GitHub repository import, authentication, and data sync.
"""
import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

from tracertm.services.github_import_service import GitHubImportService
from tracertm.models.item import Item
from tracertm.models.link import Link


@pytest.mark.integration
@pytest.mark.asyncio
class TestGitHubAuthenticationFlow:
    """Tests for GitHub API authentication."""

    async def test_authenticate_with_valid_token(
        self, github_service: GitHubImportService
    ):
        """Test successful authentication with valid GitHub token."""
        token = "ghp_valid_test_token_1234567890"

        with patch('github.Github') as mock_github:
            mock_github.return_value.get_user.return_value.login = "testuser"

            result = await github_service.authenticate(token)

            assert result.success is True
            assert result.user == "testuser"

    async def test_authenticate_with_invalid_token(
        self, github_service: GitHubImportService
    ):
        """Test authentication failure with invalid token."""
        token = "invalid_token"

        with patch('github.Github') as mock_github:
            from github import GithubException
            mock_github.return_value.get_user.side_effect = GithubException(
                401, {"message": "Bad credentials"}
            )

            with pytest.raises(AuthenticationError):
                await github_service.authenticate(token)

    async def test_authenticate_with_expired_token(
        self, github_service: GitHubImportService
    ):
        """Test authentication with expired token."""
        token = "ghp_expired_token"

        with patch('github.Github') as mock_github:
            from github import GithubException
            mock_github.return_value.get_user.side_effect = GithubException(
                401, {"message": "Token expired"}
            )

            with pytest.raises(AuthenticationError, match="Token expired"):
                await github_service.authenticate(token)

    async def test_authenticate_with_insufficient_permissions(
        self, github_service: GitHubImportService
    ):
        """Test authentication with insufficient scopes."""
        token = "ghp_limited_scopes_token"

        with patch('github.Github') as mock_github:
            mock_repo = MagicMock()
            mock_repo.get_issues.side_effect = PermissionError("Insufficient scopes")

            with pytest.raises(PermissionError, match="Insufficient scopes"):
                await github_service.authenticate(token)


@pytest.mark.integration
@pytest.mark.asyncio
class TestGitHubRepositoryImport:
    """Tests for importing GitHub repositories."""

    async def test_import_repository_creates_items(
        self, github_service: GitHubImportService, db_session
    ):
        """Test importing repository creates items for issues."""
        repo_path = "owner/repo"

        with patch('github.Github') as mock_github:
            # Mock repository
            mock_repo = MagicMock()
            mock_repo.full_name = repo_path
            mock_repo.description = "Test repository"
            mock_repo.stargazers_count = 100

            # Mock issues
            mock_issue1 = MagicMock()
            mock_issue1.number = 1
            mock_issue1.title = "First issue"
            mock_issue1.body = "Issue description"
            mock_issue1.state = "open"
            mock_issue1.created_at = datetime.now()

            mock_issue2 = MagicMock()
            mock_issue2.number = 2
            mock_issue2.title = "Second issue"
            mock_issue2.body = "Another issue"
            mock_issue2.state = "closed"

            mock_repo.get_issues.return_value = [mock_issue1, mock_issue2]

            mock_github.return_value.get_user.return_value.get_repo.return_value = mock_repo

            # Execute
            result = await github_service.import_repository(
                repo_path=repo_path,
                project_id="proj_1"
            )

            # Assert
            assert result.success is True
            assert result.imported_count == 2

            # Verify items created in database
            items = db_session.query(Item).all()
            assert len(items) >= 2

    async def test_import_repository_with_invalid_path(
        self, github_service: GitHubImportService
    ):
        """Test importing with invalid repository path."""
        with pytest.raises(ValueError, match="Invalid repository path"):
            await github_service.import_repository(
                repo_path="invalid_path",
                project_id="proj_1"
            )

    async def test_import_large_repository(
        self, github_service: GitHubImportService, db_session
    ):
        """Test importing large repository with pagination."""
        repo_path = "owner/large-repo"
        issue_count = 1000

        with patch('github.Github') as mock_github:
            mock_repo = MagicMock()
            mock_repo.full_name = repo_path

            # Mock paginated issues
            mock_issues = [
                MagicMock(
                    number=i,
                    title=f"Issue {i}",
                    body=f"Description {i}",
                    state="open"
                )
                for i in range(1, issue_count + 1)
            ]

            mock_repo.get_issues.return_value = mock_issues

            mock_github.return_value.get_user.return_value.get_repo.return_value = mock_repo

            result = await github_service.import_repository(
                repo_path=repo_path,
                project_id="proj_1"
            )

            assert result.imported_count == issue_count


@pytest.mark.integration
@pytest.mark.asyncio
class TestGitHubRateLimiting:
    """Tests for GitHub API rate limit handling."""

    async def test_handle_rate_limit_with_retry(
        self, github_service: GitHubImportService
    ):
        """Test handling rate limit errors with retry."""
        from github import RateLimitExceededException

        with patch('github.Github') as mock_github:
            # First call hits rate limit, second succeeds
            mock_repo = MagicMock()
            mock_repo.get_issues.side_effect = [
                RateLimitExceededException(403, {"message": "API rate limit exceeded"}),
                [MagicMock(number=1, title="Issue")]
            ]

            mock_github.return_value.get_user.return_value.get_repo.return_value = mock_repo

            # Should retry automatically
            result = await github_service.import_repository(
                repo_path="owner/repo",
                project_id="proj_1"
            )

            assert result.success is True

    async def test_rate_limit_backoff_strategy(self, github_service: GitHubImportService):
        """Test exponential backoff on rate limits."""
        retry_counts = []

        async def track_retries():
            retry_counts.append(len(retry_counts) + 1)
            if len(retry_counts) < 3:
                raise RateLimitExceededException(403, {})

        with patch.object(github_service, 'fetch_issues', side_effect=track_retries):
            await github_service.import_with_retry()

            # Should retry with backoff
            assert len(retry_counts) >= 3


@pytest.mark.integration
@pytest.mark.asyncio
class TestGitHubConflictResolution:
    """Tests for handling conflicts during import."""

    async def test_detect_duplicate_imports(
        self, github_service: GitHubImportService, db_session
    ):
        """Test detecting already-imported issues."""
        repo_path = "owner/repo"
        issue_number = 1

        # Create existing item from previous import
        existing_item = Item(
            title="Issue 1",
            project_id="proj_1",
            metadata={"github_issue": issue_number, "github_repo": repo_path}
        )
        db_session.add(existing_item)
        db_session.commit()

        with patch('github.Github') as mock_github:
            mock_issue = MagicMock()
            mock_issue.number = issue_number
            mock_issue.title = "Updated title"

            result = await github_service.import_repository(
                repo_path=repo_path,
                project_id="proj_1"
            )

            # Should detect duplicate
            assert result.skipped_count >= 1

    async def test_handle_merge_conflict_strategy(
        self, github_service: GitHubImportService
    ):
        """Test merge strategy for conflicting imports."""
        result = await github_service.import_with_strategy(
            repo_path="owner/repo",
            conflict_strategy="merge"
        )

        assert result.merge_count >= 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestGitHubDataMapping:
    """Tests for mapping GitHub data to TracerTM models."""

    async def test_map_issue_to_item(self, github_service: GitHubImportService):
        """Test mapping GitHub issue to Item model."""
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.title = "Test Issue"
        mock_issue.body = "Issue description"
        mock_issue.state = "open"
        mock_issue.labels = ["bug", "urgent"]
        mock_issue.created_at = datetime.now()
        mock_issue.updated_at = datetime.now()

        item = await github_service.map_issue_to_item(mock_issue, project_id="proj_1")

        assert item.title == "Test Issue"
        assert item.project_id == "proj_1"
        assert "github" in item.metadata

    async def test_map_pull_request_to_link(self, github_service: GitHubImportService):
        """Test mapping GitHub PR relationships to links."""
        mock_pr = MagicMock()
        mock_pr.number = 456
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"

        link = await github_service.map_pr_to_link(
            mock_pr,
            project_id="proj_1"
        )

        assert link is not None
        assert link.metadata.get("github_pr_number") == 456


@pytest.mark.integration
@pytest.mark.asyncio
class TestGitHubNetworkResilience:
    """Tests for network error handling."""

    async def test_retry_on_connection_timeout(
        self, github_service: GitHubImportService
    ):
        """Test retrying on connection timeout."""
        import socket

        with patch('github.Github') as mock_github:
            mock_github.return_value.get_user.side_effect = [
                socket.timeout("Connection timed out"),
                MagicMock(login="testuser")
            ]

            result = await github_service.authenticate("token")

            assert result.success is True

    async def test_handle_network_offline(
        self, github_service: GitHubImportService
    ):
        """Test graceful handling of network offline."""
        import requests

        with patch('github.Github') as mock_github:
            mock_github.return_value.get_user.side_effect = requests.ConnectionError(
                "Network is unreachable"
            )

            with pytest.raises(NetworkError):
                await github_service.authenticate("token")

    async def test_retry_with_exponential_backoff(
        self, github_service: GitHubImportService
    ):
        """Test exponential backoff on network errors."""
        attempt_times = []

        async def track_attempts():
            attempt_times.append(datetime.now())
            if len(attempt_times) < 3:
                raise ConnectionError()
            return MagicMock(login="user")

        with patch.object(
            github_service, 'authenticate_internal',
            side_effect=track_attempts
        ):
            result = await github_service.authenticate("token")

            assert result.success is True

            # Verify backoff timing (second attempt delayed more than first)
            if len(attempt_times) >= 2:
                gap1 = (attempt_times[1] - attempt_times[0]).total_seconds()
                if len(attempt_times) >= 3:
                    gap2 = (attempt_times[2] - attempt_times[1]).total_seconds()
                    assert gap2 >= gap1


# Test Fixtures

@pytest.fixture
async def github_service():
    """Create GitHub import service."""
    return GitHubImportService()


@pytest.fixture
def mock_github_api():
    """Mock GitHub API."""
    return MagicMock()


# Custom Exceptions

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class PermissionError(Exception):
    """Raised when insufficient permissions."""
    pass


class NetworkError(Exception):
    """Raised on network errors."""
    pass


class RateLimitExceededException(Exception):
    """Raised when rate limit exceeded."""
    pass
```

---

## Priority 3: Exception Path Coverage (CRITICAL)

### Gap Summary
- **Current:** 25.6% of tests
- **Impact:** Production reliability, error messages
- **Required:** +500 `pytest.raises` assertions
- **Time Estimate:** 12 hours

### Implementation Template

Add to existing service test files:

```python
# Pattern 1: Validation Errors
@pytest.mark.unit
async def test_service_method_with_none_input(service):
    """Test that None input raises ValueError."""
    with pytest.raises(ValueError, match="parameter required"):
        await service.method(param=None)

@pytest.mark.unit
async def test_service_method_with_empty_string(service):
    """Test that empty string input raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        await service.method(param="")

@pytest.mark.unit
async def test_service_method_with_invalid_type(service):
    """Test that invalid type raises TypeError."""
    with pytest.raises(TypeError, match="expected str"):
        await service.method(param=123)


# Pattern 2: Business Logic Errors
@pytest.mark.unit
async def test_circular_reference_detection(service):
    """Test that circular references are rejected."""
    with pytest.raises(ValueError, match="circular reference"):
        await service.create_link(source_id="item_1", target_id="item_1")

@pytest.mark.unit
async def test_duplicate_creation_prevention(service):
    """Test that duplicates are prevented."""
    # Create first
    item1 = await service.create_item(title="Test", project_id="proj_1")

    # Try to create duplicate
    with pytest.raises(ValueError, match="already exists"):
        await service.create_item(title="Test", project_id="proj_1")


# Pattern 3: Database Errors
@pytest.mark.unit
async def test_database_constraint_violation(service, db_session):
    """Test handling of database constraint violations."""
    with pytest.raises(IntegrityError):
        # Violate unique constraint
        await service.create_item(
            id="item_1",  # Duplicate ID
            title="Test",
            project_id="proj_1"
        )

@pytest.mark.unit
async def test_database_connection_failure(service):
    """Test handling of database connection errors."""
    with patch('database.get_session') as mock_session:
        mock_session.side_effect = ConnectionError("DB unavailable")

        with pytest.raises(DatabaseError, match="connection"):
            await service.get_item("item_1")


# Pattern 4: Async/Concurrency Errors
@pytest.mark.unit
@pytest.mark.asyncio
async def test_concurrent_modification_detection(service):
    """Test detection of concurrent modifications."""
    item = await service.get_item("item_1")
    original_version = item.version

    # Simulate concurrent modification
    with patch.object(service, 'verify_version') as mock_verify:
        mock_verify.side_effect = ConcurrencyError("Version mismatch")

        with pytest.raises(ConcurrencyError):
            await service.update_item("item_1", title="New")


# Pattern 5: Resource Errors
@pytest.mark.unit
async def test_not_found_error(service):
    """Test handling of not found errors."""
    with pytest.raises(NotFoundError, match="Item not found"):
        await service.get_item("nonexistent_id")

@pytest.mark.unit
async def test_permission_denied_error(service):
    """Test handling of permission errors."""
    with pytest.raises(PermissionError, match="Not authorized"):
        await service.delete_item("item_1", user_id="other_user")
```

---

## Verification Checklist

After implementation, verify:

- [ ] All 5 gap service tests created
- [ ] Each test file has 25-35 comprehensive tests
- [ ] Error paths tested with `pytest.raises`
- [ ] Async operations tested with `@pytest.mark.asyncio`
- [ ] Fixtures provided for test data
- [ ] Mocking setup for external dependencies
- [ ] Test pass rate at 100%
- [ ] Coverage reports generated

---

## Running the New Tests

```bash
# Run event service tests
pytest tests/unit/services/test_event_service_comprehensive.py -v

# Run GitHub integration tests
pytest tests/integration/test_github_integration_comprehensive.py -v

# Run with coverage
pytest --cov=src/tracertm --cov-report=html tests/unit tests/integration

# Run specific test class
pytest tests/unit/services/test_event_service_comprehensive.py::TestEventServiceCreation -v

# Run with markers
pytest -m unit -v
pytest -m integration -v
```

---

## Expected Outcomes

**After completing this guide:**
- Service coverage: 92.6% → 100%
- Error path tests: 25.6% → 80%+
- New test files: +3
- New test cases: +75-100
- Total test code: +150-200 hours of coverage

