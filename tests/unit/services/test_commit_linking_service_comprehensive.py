"""
Comprehensive tests for CommitLinkingService.

Tests all methods: parse_commit_message, auto_link_commit,
_find_item_by_reference, register_commit_hook.

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from tracertm.services.commit_linking_service import CommitLinkingService


class TestParseCommitMessage:
    """Test parse_commit_message method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = CommitLinkingService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_no_references(self, service):
        """Test parsing message with no references."""
        service.items.get_by_id = AsyncMock(return_value=None)
        service.items.query = AsyncMock(return_value=[])

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Simple commit message",
            commit_hash="abc123",
            author="user@example.com",
        )

        assert result["found"] == []
        assert result["linked"] == []
        assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_hash_pattern(self, service):
        """Test parsing #123 pattern."""
        item = Mock()
        item.id = "item-1"
        item.title = "Feature Item"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Fix bug #123",
            commit_hash="abc123",
            author="dev@example.com",
        )

        assert len(result["found"]) == 1
        assert result["found"][0]["pattern"] == "hash"
        assert result["found"][0]["reference"] == "123"

    @pytest.mark.asyncio
    async def test_jira_pattern(self, service):
        """Test parsing JIRA-123 pattern."""
        item = Mock()
        item.id = "item-1"
        item.title = "JIRA Item"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Implement FEAT-456",
            commit_hash="def456",
            author="dev@example.com",
        )

        assert len(result["found"]) == 1
        assert result["found"][0]["pattern"] == "jira"
        assert result["found"][0]["reference"] == "FEAT-456"

    @pytest.mark.asyncio
    async def test_github_pattern(self, service):
        """Test parsing GH-123 pattern."""
        item = Mock()
        item.id = "item-1"
        item.title = "GitHub Item"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Close GH-789",
            commit_hash="ghi789",
            author="dev@example.com",
        )

        # Multiple patterns can match, check at least one with github pattern
        assert len(result["found"]) >= 1
        assert any(r["pattern"] == "github" for r in result["found"])

    @pytest.mark.asyncio
    async def test_gitlab_pattern(self, service):
        """Test parsing GL-123 pattern."""
        item = Mock()
        item.id = "item-1"
        item.title = "GitLab Item"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Fix GL-101",
            commit_hash="jkl101",
            author="dev@example.com",
        )

        # Multiple patterns can match, check at least one with gitlab pattern
        assert len(result["found"]) >= 1
        assert any(r["pattern"] == "gitlab" for r in result["found"])

    @pytest.mark.asyncio
    async def test_custom_pattern(self, service):
        """Test parsing [FEAT-123] pattern."""
        item = Mock()
        item.id = "item-1"
        item.title = "Custom Item"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Add feature [TASK-202]",
            commit_hash="mno202",
            author="dev@example.com",
        )

        # Multiple patterns can match, check at least one with custom pattern
        assert len(result["found"]) >= 1
        assert any(r["pattern"] == "custom" for r in result["found"])

    @pytest.mark.asyncio
    async def test_multiple_references(self, service):
        """Test parsing multiple references."""
        item = Mock()
        item.id = "item-1"
        item.title = "Item"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Fix #123 and FEAT-456",
            commit_hash="abc123",
            author="dev@example.com",
        )

        assert len(result["found"]) == 2

    @pytest.mark.asyncio
    async def test_item_not_found(self, service):
        """Test when referenced item doesn't exist."""
        service.items.get_by_id = AsyncMock(return_value=None)
        service.items.query = AsyncMock(return_value=[])

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Fix #999",
            commit_hash="abc123",
            author="dev@example.com",
        )

        assert result["found"] == []

    @pytest.mark.asyncio
    async def test_item_wrong_project(self, service):
        """Test when item belongs to different project."""
        item = Mock()
        item.id = "item-1"
        item.title = "Item"
        item.project_id = "other-proj"  # Different project

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.query = AsyncMock(return_value=[])

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Fix #123",
            commit_hash="abc123",
            author="dev@example.com",
        )

        # Item should not be found as it's in different project
        assert len(result["found"]) == 0

    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling during parsing."""
        service.items.get_by_id = AsyncMock(side_effect=Exception("DB error"))

        result = await service.parse_commit_message(
            project_id="proj-1",
            commit_message="Fix #123",
            commit_hash="abc123",
            author="dev@example.com",
        )

        assert len(result["errors"]) == 1
        assert "DB error" in result["errors"][0]


class TestAutoLinkCommit:
    """Test auto_link_commit method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = CommitLinkingService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_creates_link_for_found_item(self, service):
        """Test link creation for found item."""
        item = Mock()
        item.id = "item-1"
        item.title = "Feature"
        item.project_id = "proj-1"

        link = Mock()
        link.id = "link-1"

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.create = AsyncMock(return_value=link)
        service.events.log = AsyncMock()

        result = await service.auto_link_commit(
            project_id="proj-1",
            commit_message="Implement #123",
            commit_hash="abc123",
            author="dev@example.com",
        )

        assert len(result["linked"]) == 1
        service.links.create.assert_called_once()
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_link_includes_metadata(self, service):
        """Test created link includes commit metadata."""
        item = Mock()
        item.id = "item-1"
        item.title = "Feature"
        item.project_id = "proj-1"

        link = Mock()
        link.id = "link-1"

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.create = AsyncMock(return_value=link)
        service.events.log = AsyncMock()

        await service.auto_link_commit(
            project_id="proj-1",
            commit_message="Implement #123",
            commit_hash="abc123",
            author="dev@example.com",
        )

        # Verify metadata passed to create
        call_kwargs = service.links.create.call_args.kwargs
        assert call_kwargs["metadata"]["commit_hash"] == "abc123"
        assert call_kwargs["metadata"]["author"] == "dev@example.com"

    @pytest.mark.asyncio
    async def test_logs_event_on_link(self, service):
        """Test event is logged for created link."""
        item = Mock()
        item.id = "item-1"
        item.title = "Feature"
        item.project_id = "proj-1"

        link = Mock()
        link.id = "link-1"

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.create = AsyncMock(return_value=link)
        service.events.log = AsyncMock()

        await service.auto_link_commit(
            project_id="proj-1",
            commit_message="Implement #123",
            commit_hash="abc123",
            author="dev@example.com",
            agent_id="bot-1",
        )

        # Verify event logged with correct type
        call_kwargs = service.events.log.call_args.kwargs
        assert call_kwargs["event_type"] == "commit_linked"
        assert call_kwargs["agent_id"] == "bot-1"

    @pytest.mark.asyncio
    async def test_link_creation_error_handled(self, service):
        """Test error handling during link creation."""
        item = Mock()
        item.id = "item-1"
        item.title = "Feature"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.create = AsyncMock(side_effect=Exception("Create failed"))
        service.events.log = AsyncMock()

        result = await service.auto_link_commit(
            project_id="proj-1",
            commit_message="Implement #123",
            commit_hash="abc123",
            author="dev@example.com",
        )

        assert len(result["errors"]) == 1
        assert "Failed to link" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_no_links_when_no_references(self, service):
        """Test no links created when no references found."""
        service.items.get_by_id = AsyncMock(return_value=None)
        service.items.query = AsyncMock(return_value=[])

        result = await service.auto_link_commit(
            project_id="proj-1",
            commit_message="Simple commit",
            commit_hash="abc123",
            author="dev@example.com",
        )

        assert result["linked"] == []
        service.links.create.assert_not_called()


class TestFindItemByReference:
    """Test _find_item_by_reference method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = CommitLinkingService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_finds_by_direct_id(self, service):
        """Test finding item by direct ID lookup."""
        item = Mock()
        item.id = "item-123"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service._find_item_by_reference("proj-1", "item-123")

        assert result == item

    @pytest.mark.asyncio
    async def test_finds_by_metadata_query(self, service):
        """Test finding item by metadata query."""
        item = Mock()
        item.id = "item-1"
        item.project_id = "proj-1"

        service.items.get_by_id = AsyncMock(return_value=None)
        service.items.query = AsyncMock(return_value=[item])

        result = await service._find_item_by_reference("proj-1", "some-ref")

        assert result == item

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, service):
        """Test returns None when item not found."""
        service.items.get_by_id = AsyncMock(return_value=None)
        service.items.query = AsyncMock(return_value=[])

        result = await service._find_item_by_reference("proj-1", "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_rejects_wrong_project(self, service):
        """Test rejects item from wrong project."""
        item = Mock()
        item.id = "item-1"
        item.project_id = "other-proj"

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.query = AsyncMock(return_value=[])

        result = await service._find_item_by_reference("proj-1", "item-1")

        # Should fallback to query since direct lookup returned wrong project
        assert result is None


class TestRegisterCommitHook:
    """Test register_commit_hook method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return CommitLinkingService(session)

    @pytest.mark.asyncio
    async def test_register_git_hook(self, service):
        """Test registering git hook."""
        result = await service.register_commit_hook(
            project_id="proj-1",
            hook_type="git",
            config={"repo": "/path/to/repo"},
        )

        assert result["project_id"] == "proj-1"
        assert result["hook_type"] == "git"
        assert result["status"] == "registered"

    @pytest.mark.asyncio
    async def test_register_github_hook(self, service):
        """Test registering github hook."""
        result = await service.register_commit_hook(
            project_id="proj-1",
            hook_type="github",
            config={"webhook_secret": "secret123"},
        )

        assert result["hook_type"] == "github"
        assert result["config"]["webhook_secret"] == "secret123"

    @pytest.mark.asyncio
    async def test_register_gitlab_hook(self, service):
        """Test registering gitlab hook."""
        result = await service.register_commit_hook(
            project_id="proj-1",
            hook_type="gitlab",
            config={"token": "token123"},
        )

        assert result["hook_type"] == "gitlab"


class TestPatterns:
    """Test PATTERNS constant."""

    def test_patterns_defined(self):
        """Test patterns are defined."""
        assert len(CommitLinkingService.PATTERNS) > 0

    def test_hash_pattern(self):
        """Test hash pattern matches #123."""
        import re
        pattern = CommitLinkingService.PATTERNS["hash"]
        match = re.search(pattern, "Fix #456")
        assert match is not None
        assert match.group(1) == "456"

    def test_jira_pattern(self):
        """Test JIRA pattern matches PROJ-123."""
        import re
        pattern = CommitLinkingService.PATTERNS["jira"]
        match = re.search(pattern, "Implement FEAT-789")
        assert match is not None
        assert match.group(1) == "FEAT-789"

    def test_github_pattern(self):
        """Test GitHub pattern matches GH-123."""
        import re
        pattern = CommitLinkingService.PATTERNS["github"]
        match = re.search(pattern, "Close GH-101")
        assert match is not None
        assert match.group(1) == "101"

    def test_gitlab_pattern(self):
        """Test GitLab pattern matches GL-123."""
        import re
        pattern = CommitLinkingService.PATTERNS["gitlab"]
        match = re.search(pattern, "Fix GL-202")
        assert match is not None
        assert match.group(1) == "202"

    def test_custom_pattern(self):
        """Test custom pattern matches [TASK-123]."""
        import re
        pattern = CommitLinkingService.PATTERNS["custom"]
        match = re.search(pattern, "Add [BUG-303]")
        assert match is not None
        assert match.group(1) == "BUG-303"


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_repositories(self):
        """Test initialization creates repositories."""
        session = AsyncMock()
        service = CommitLinkingService(session)

        assert service.session == session
        assert service.items is not None
        assert service.links is not None
        assert service.events is not None
