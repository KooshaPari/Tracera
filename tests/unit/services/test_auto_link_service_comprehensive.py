"""
Comprehensive tests for AutoLinkService.

Tests all methods: parse_commit_message, create_auto_links, _determine_link_type.

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from tracertm.services.auto_link_service import AutoLinkService
from tracertm.models.item import Item
from tracertm.models.link import Link


class TestParseCommitMessage:
    """Test parse_commit_message method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return AutoLinkService(mock_session)

    def test_parse_hash_pattern(self, service, mock_session):
        """Test parsing #STORY-123 pattern."""
        item = Mock(spec=Item)
        item.id = "STORY-123"
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message("proj-1", "Fixed bug #STORY-123")

        # Multiple patterns may match STORY-123 format, check at least one found
        assert len(result) >= 1
        assert any(r[0] == "STORY-123" for r in result)

    def test_parse_story_pattern(self, service, mock_session):
        """Test parsing STORY-123 pattern."""
        item = Mock(spec=Item)
        item.id = "123"
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message("proj-1", "Implement STORY-123 feature")

        assert len(result) >= 1

    def test_parse_bracket_pattern(self, service, mock_session):
        """Test parsing [FEAT-456] pattern."""
        item = Mock(spec=Item)
        item.id = "FEAT-456"
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message("proj-1", "Add feature [FEAT-456]")

        assert len(result) == 1
        assert result[0][0] == "FEAT-456"

    def test_parse_paren_pattern(self, service, mock_session):
        """Test parsing (BUG-789) pattern."""
        item = Mock(spec=Item)
        item.id = "BUG-789"
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message("proj-1", "Bugfix (BUG-789)")

        assert len(result) == 1
        assert result[0][0] == "BUG-789"

    def test_parse_uuid_pattern(self, service, mock_session):
        """Test parsing UUID pattern."""
        uuid_id = "12345678-1234-1234-1234-123456789abc"
        item = Mock(spec=Item)
        item.id = uuid_id
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message(
            "proj-1", f"Relates to {uuid_id}"
        )

        assert len(result) == 1
        assert result[0][0] == uuid_id

    def test_parse_no_matches(self, service, mock_session):
        """Test parsing message with no item references."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        result = service.parse_commit_message("proj-1", "Simple commit message")

        assert result == []

    def test_parse_item_not_found(self, service, mock_session):
        """Test when referenced item doesn't exist."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        result = service.parse_commit_message("proj-1", "Update #FAKE-123")

        assert result == []

    def test_parse_multiple_items(self, service, mock_session):
        """Test parsing message with multiple item references."""
        item1 = Mock(spec=Item)
        item1.id = "FEAT-1"
        item2 = Mock(spec=Item)
        item2.id = "FEAT-2"

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            item1, item2
        ]

        result = service.parse_commit_message(
            "proj-1", "Update [FEAT-1] and [FEAT-2]"
        )

        assert len(result) == 2

    def test_parse_case_insensitive(self, service, mock_session):
        """Test case-insensitive matching."""
        item = Mock(spec=Item)
        item.id = "123"
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message("proj-1", "story-123 lowercase")

        assert len(result) >= 1

    def test_parse_determines_test_link_type(self, service, mock_session):
        """Test that test-related commits get 'tests' link type."""
        item = Mock(spec=Item)
        item.id = "STORY-1"
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message(
            "proj-1", "Add unit test for #STORY-1"
        )

        # Multiple patterns may match, check at least one has 'tests' link type
        assert len(result) >= 1
        assert any(r[1] == "tests" for r in result)

    def test_parse_determines_implements_link_type(self, service, mock_session):
        """Test that implementation commits get 'implements' link type."""
        item = Mock(spec=Item)
        item.id = "STORY-1"
        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.parse_commit_message(
            "proj-1", "Implement feature #STORY-1"
        )

        # Multiple patterns may match, check at least one has 'implements' link type
        assert len(result) >= 1
        assert any(r[1] == "implements" for r in result)


class TestCreateAutoLinks:
    """Test create_auto_links method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return AutoLinkService(mock_session)

    def test_creates_link_for_found_item(self, service, mock_session):
        """Test link creation for found item."""
        item = Mock(spec=Item)
        item.id = "item-123"

        # Use simple numeric ID to avoid multiple pattern matches
        # First return item for parse query, then None for existing link check
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            item,  # parse_commit_message query for first match
            item,  # parse_commit_message query for second match (STORY pattern also matches)
            None,  # Existing link check for first
            None,  # Existing link check for second
        ]

        result = service.create_auto_links(
            project_id="proj-1",
            commit_message="Implement #STORY-1",
            code_item_id="code-1",
            commit_hash="abc123",
        )

        # Multiple matches, should create at least one link
        assert len(result) >= 1
        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()

    def test_skips_existing_link(self, service, mock_session):
        """Test that existing links are not duplicated."""
        item = Mock(spec=Item)
        item.id = "item-123"
        existing_link = Mock(spec=Link)

        # Multiple pattern matches, all with existing links
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            item,  # parse_commit_message query for first match
            item,  # parse_commit_message query for second match
            existing_link,  # Existing link check - found
            existing_link,  # Existing link check - found
        ]

        result = service.create_auto_links(
            project_id="proj-1",
            commit_message="Implement #STORY-1",
            code_item_id="code-1",
        )

        # All links already exist, none should be created
        assert len(result) == 0
        mock_session.add.assert_not_called()

    def test_creates_multiple_links(self, service, mock_session):
        """Test creation of multiple links."""
        item1 = Mock(spec=Item)
        item1.id = "FEAT-1"
        item2 = Mock(spec=Item)
        item2.id = "FEAT-2"

        # First two for parse, next two for existing link checks
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            item1, item2,  # parse_commit_message queries
            None, None,  # Existing link checks
        ]

        result = service.create_auto_links(
            project_id="proj-1",
            commit_message="Update [FEAT-1] and [FEAT-2]",
            code_item_id="code-1",
        )

        assert len(result) == 2
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()

    def test_no_commit_when_no_links(self, service, mock_session):
        """Test no commit when no links created."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        result = service.create_auto_links(
            project_id="proj-1",
            commit_message="Simple commit",
            code_item_id="code-1",
        )

        assert len(result) == 0
        mock_session.commit.assert_not_called()

    def test_link_metadata_includes_commit_info(self, service, mock_session):
        """Test link metadata includes commit information."""
        item = Mock(spec=Item)
        item.id = "item-123"

        # Provide enough side_effect values for multiple pattern matches
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            item,  # First pattern match
            item,  # Second pattern match
            None,  # Existing link check for first
            None,  # Existing link check for second
        ]

        captured_link = None

        def capture_add(link):
            nonlocal captured_link
            captured_link = link

        mock_session.add.side_effect = capture_add

        service.create_auto_links(
            project_id="proj-1",
            commit_message="Fix #STORY-1",
            code_item_id="code-1",
            commit_hash="abc123",
        )

        assert captured_link is not None
        assert captured_link.link_metadata["auto_linked"] is True
        assert captured_link.link_metadata["commit_hash"] == "abc123"
        assert captured_link.link_metadata["commit_message"] == "Fix #STORY-1"


class TestDetermineLinkType:
    """Test _determine_link_type method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return AutoLinkService(Mock())

    def test_test_keyword_returns_tests(self, service):
        """Test 'test' keyword returns 'tests' type."""
        result = service._determine_link_type("Add unit test for login")
        assert result == "tests"

    def test_testing_keyword_returns_tests(self, service):
        """Test 'testing' keyword returns 'tests' type."""
        result = service._determine_link_type("Testing the new feature")
        assert result == "tests"

    def test_spec_keyword_returns_tests(self, service):
        """Test 'spec' keyword returns 'tests' type."""
        result = service._determine_link_type("Add spec for user model")
        assert result == "tests"

    def test_specification_keyword_returns_tests(self, service):
        """Test 'specification' keyword returns 'tests' type."""
        result = service._determine_link_type("Write specification tests")
        assert result == "tests"

    def test_implement_keyword_returns_implements(self, service):
        """Test 'implement' keyword returns 'implements' type."""
        result = service._determine_link_type("Implement new login flow")
        assert result == "implements"

    def test_add_keyword_returns_implements(self, service):
        """Test 'add' keyword returns 'implements' type."""
        result = service._determine_link_type("Add user authentication")
        assert result == "implements"

    def test_create_keyword_returns_implements(self, service):
        """Test 'create' keyword returns 'implements' type."""
        result = service._determine_link_type("Create API endpoint")
        assert result == "implements"

    def test_feat_keyword_returns_implements(self, service):
        """Test 'feat' keyword returns 'implements' type."""
        result = service._determine_link_type("feat: new dashboard")
        assert result == "implements"

    def test_default_returns_implements(self, service):
        """Test default behavior returns 'implements'."""
        result = service._determine_link_type("Some random commit message")
        assert result == "implements"

    def test_case_insensitive(self, service):
        """Test case insensitivity."""
        result = service._determine_link_type("TEST: check auth flow")
        assert result == "tests"


class TestStoryPatterns:
    """Test STORY_PATTERNS constant."""

    def test_patterns_exist(self):
        """Test patterns are defined."""
        assert len(AutoLinkService.STORY_PATTERNS) > 0

    def test_hash_pattern_matches(self):
        """Test #STORY-123 pattern."""
        import re
        pattern = AutoLinkService.STORY_PATTERNS[0]
        match = re.search(pattern, "#FEAT-123")
        assert match is not None
        assert match.group(1) == "FEAT-123"

    def test_story_pattern_matches(self):
        """Test STORY-123 pattern."""
        import re
        pattern = AutoLinkService.STORY_PATTERNS[1]
        match = re.search(pattern, "STORY-456")
        assert match is not None

    def test_bracket_pattern_matches(self):
        """Test [STORY-123] pattern."""
        import re
        pattern = AutoLinkService.STORY_PATTERNS[2]
        match = re.search(pattern, "[BUG-789]")
        assert match is not None
        assert match.group(1) == "BUG-789"

    def test_paren_pattern_matches(self):
        """Test (STORY-123) pattern."""
        import re
        pattern = AutoLinkService.STORY_PATTERNS[3]
        match = re.search(pattern, "(TASK-101)")
        assert match is not None
        assert match.group(1) == "TASK-101"


class TestServiceInit:
    """Test service initialization."""

    def test_init_with_session(self):
        """Test initialization stores session."""
        session = Mock(spec=Session)
        service = AutoLinkService(session)
        assert service.session == session
