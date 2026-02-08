"""Tests for wireframe parsing and Figma integration."""

from datetime import datetime
from pathlib import Path

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.storage.markdown_parser import ItemData, parse_item_markdown, write_item_markdown
from tracertm.utils.figma import (
    FigmaMetadata,
    build_figma_url,
    convert_figma_protocol_to_url,
    extract_figma_protocol_url,
    is_figma_url,
    parse_figma_url,
    validate_figma_metadata,
)


class TestFigmaURLParsing:
    """Test Figma URL parsing utilities."""

    def test_parse_basic_figma_url(self) -> None:
        """Test parsing a basic Figma URL."""
        url = "https://www.figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)

        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"
        assert meta.node_id is None

    def test_parse_figma_url_with_node_id(self) -> None:
        """Test parsing a Figma URL with node-id."""
        url = "https://www.figma.com/file/abc123xyz/MyProject?node-id=1:42"
        meta = parse_figma_url(url)

        assert meta.file_key == "abc123xyz"
        assert meta.file_name == "MyProject"
        assert meta.node_id == "1:42"

    def test_parse_figma_design_url(self) -> None:
        """Test parsing a Figma design URL (newer format)."""
        url = "https://www.figma.com/design/abc123/MyProject"
        meta = parse_figma_url(url)

        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    def test_parse_figma_url_without_https(self) -> None:
        """Test parsing a Figma URL without https:// prefix."""
        url = "figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)

        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    def test_parse_invalid_url_raises_error(self) -> None:
        """Test that invalid URLs raise ValueError."""
        with pytest.raises(ValueError, match="Not a Figma URL"):
            parse_figma_url("https://example.com")

    def test_is_figma_url(self) -> None:
        """Test URL validation."""
        assert is_figma_url("https://www.figma.com/file/abc123/MyProject")
        assert is_figma_url("figma.com/file/abc123/MyProject")
        assert not is_figma_url("https://example.com")
        assert not is_figma_url("invalid")

    def test_build_figma_url(self) -> None:
        """Test building Figma URLs."""
        url = build_figma_url("abc123", "MyProject", "1:42")
        assert url == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"

        url = build_figma_url("abc123", "MyProject")
        assert url == "https://www.figma.com/file/abc123/MyProject"

        url = build_figma_url("abc123")
        assert url == "https://www.figma.com/file/abc123"

    def test_figma_metadata_properties(self) -> None:
        """Test FigmaMetadata computed properties."""
        meta = FigmaMetadata(file_key="abc123", node_id="1:42", file_name="MyProject", full_url="https://...")

        assert meta.base_url == "https://www.figma.com/file/abc123/MyProject"
        assert meta.node_url == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
        assert meta.api_file_url == "https://api.figma.com/v1/files/abc123"
        assert meta.api_node_url == "https://api.figma.com/v1/files/abc123/nodes?ids=1:42"


class TestFigmaProtocol:
    """Test Figma protocol conversion utilities."""

    def test_extract_figma_protocol_url(self) -> None:
        """Test extracting figma:// URLs from markdown."""
        text = "![Preview](figma://abc123/1:42)"
        matches = extract_figma_protocol_url(text)

        assert len(matches) == 1
        assert matches[0] == ("abc123", "1:42")

    def test_extract_multiple_figma_urls(self) -> None:
        """Test extracting multiple figma:// URLs."""
        text = """
        ![Screen 1](figma://abc123/1:42)
        ![Screen 2](figma://abc123/2:10)
        """
        matches = extract_figma_protocol_url(text)

        assert len(matches) == COUNT_TWO
        assert matches[0] == ("abc123", "1:42")
        assert matches[1] == ("abc123", "2:10")

    def test_convert_figma_protocol_to_url(self) -> None:
        """Test converting figma:// to standard URLs."""
        text = "![Preview](figma://abc123/1:42)"
        converted = convert_figma_protocol_to_url(text)

        assert "figma://" not in converted
        assert "https://www.figma.com/file/abc123?node-id=1:42" in converted


class TestFigmaMetadataValidation:
    """Test Figma metadata validation."""

    def test_validate_valid_metadata(self) -> None:
        """Test validation of valid metadata."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/MyProject?node-id=1:42",
            "figma_file_key": "abc123",
            "figma_node_id": "1:42",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 0

    def test_validate_invalid_url(self) -> None:
        """Test validation catches invalid URLs."""
        metadata = {"figma_url": "https://example.com"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "Invalid Figma URL" in errors[0]

    def test_validate_mismatched_file_key(self) -> None:
        """Test validation catches mismatched file keys."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/MyProject",
            "figma_file_key": "xyz789",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "does not match URL file key" in errors[0]

    def test_validate_invalid_node_id_format(self) -> None:
        """Test validation catches invalid node ID format."""
        metadata = {"figma_node_id": "invalid"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "Invalid figma_node_id format" in errors[0]

    def test_validate_valid_node_id_format(self) -> None:
        """Test validation accepts valid node ID format."""
        metadata = {"figma_node_id": "1:42"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 0


class TestWireframeItemData:
    """Test wireframe ItemData creation and serialization."""

    def test_create_wireframe_item(self) -> None:
        """Test creating a wireframe ItemData object."""
        now = datetime.now()

        item = ItemData(
            id="test-uuid",
            external_id="WF-001",
            item_type="wireframe",
            status="draft",
            priority="high",
            owner="@designer",
            created=now,
            updated=now,
            figma_url="https://www.figma.com/file/abc123/MyProject?node-id=1:42",
            figma_file_key="abc123",
            figma_node_id="1:42",
            components=["Button", "InputField"],
            screens=["LoginScreen", "SignupScreen"],
            implements=["STORY-001", "STORY-002"],
            title="Login Screen Wireframe",
            description="Wireframe for authentication flow",
        )

        assert item.item_type == "wireframe"
        assert item.figma_file_key == "abc123"
        assert item.figma_node_id == "1:42"
        assert len(item.components) == COUNT_TWO
        assert len(item.screens) == COUNT_TWO
        assert len(item.implements) == COUNT_TWO

    def test_wireframe_to_frontmatter(self) -> None:
        """Test converting wireframe to frontmatter dict."""
        item = ItemData(
            id="test-uuid",
            external_id="WF-001",
            item_type="wireframe",
            status="draft",
            figma_url="https://www.figma.com/file/abc123/MyProject?node-id=1:42",
            figma_file_key="abc123",
            figma_node_id="1:42",
            components=["Button"],
            screens=["LoginScreen"],
            implements=["STORY-001"],
        )

        fm = item.to_frontmatter_dict()

        assert fm["type"] == "wireframe"
        assert fm["figma_url"] == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
        assert fm["figma_file_key"] == "abc123"
        assert fm["figma_node_id"] == "1:42"
        assert fm["components"] == ["Button"]
        assert fm["screens"] == ["LoginScreen"]
        assert fm["implements"] == ["STORY-001"]

    def test_wireframe_to_markdown_body(self) -> None:
        """Test converting wireframe to markdown body."""
        item = ItemData(
            id="test-uuid",
            external_id="WF-001",
            item_type="wireframe",
            status="draft",
            title="Login Screen",
            description="Auth flow wireframe",
            figma_url="https://www.figma.com/file/abc123/MyProject?node-id=1:42",
            figma_file_key="abc123",
            figma_node_id="1:42",
            components=["Button", "InputField"],
            screens=["LoginScreen"],
        )

        body = item.to_markdown_body()

        assert "# Login Screen" in body
        assert "## Description" in body
        assert "Auth flow wireframe" in body
        assert "## Figma Preview" in body
        assert "figma://abc123/1:42" in body
        assert "## Components Used" in body
        assert "- Button" in body
        assert "- InputField" in body
        assert "## Screens" in body
        assert "- LoginScreen" in body


class TestWireframeMarkdownParsing:
    """Test parsing wireframe markdown files."""

    def test_parse_wireframe_markdown(self, tmp_path: Path) -> None:
        """Test parsing a wireframe markdown file."""
        wireframe_md = """---
id: "test-uuid"
external_id: "WF-001"
type: wireframe
status: draft
figma_url: "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
figma_file_key: "abc123"
figma_node_id: "1:42"
components:
  - Button
  - InputField
screens:
  - LoginScreen
implements:
  - STORY-001
---

# Login Screen Wireframe

## Description

Wireframe for authentication flow.

## Figma Preview

![Preview](figma://abc123/1:42)

[View in Figma](https://www.figma.com/file/abc123/MyProject?node-id=1:42)

## Components Used

- Button
- InputField

## Screens

- LoginScreen
"""

        # Write test file
        test_file = tmp_path / "WF-001.md"
        test_file.write_text(wireframe_md)

        # Parse it
        item = parse_item_markdown(test_file)

        assert item.item_type == "wireframe"
        assert item.external_id == "WF-001"
        assert item.figma_file_key == "abc123"
        assert item.figma_node_id == "1:42"
        assert item.components == ["Button", "InputField"]
        assert item.screens == ["LoginScreen"]
        assert item.implements == ["STORY-001"]
        assert item.title == "Login Screen Wireframe"
        assert "authentication flow" in item.description

    def test_write_and_read_wireframe(self, tmp_path: Path) -> None:
        """Test round-trip write and read of wireframe."""
        now = datetime.now()

        original = ItemData(
            id="test-uuid",
            external_id="WF-001",
            item_type="wireframe",
            status="approved",
            priority="high",
            owner="@designer",
            created=now,
            updated=now,
            figma_url="https://www.figma.com/file/abc123/MyProject?node-id=1:42",
            figma_file_key="abc123",
            figma_node_id="1:42",
            components=["Button", "InputField", "Card"],
            screens=["LoginScreen", "SignupScreen"],
            implements=["STORY-001", "STORY-002"],
            title="Authentication Wireframe",
            description="Complete auth flow design",
            tags=["authentication", "ui"],
        )

        # Write to file
        test_file = tmp_path / "WF-001.md"
        write_item_markdown(original, test_file)

        # Read it back
        parsed = parse_item_markdown(test_file)

        # Verify all fields
        assert parsed.external_id == original.external_id
        assert parsed.item_type == original.item_type
        assert parsed.status == original.status
        assert parsed.priority == original.priority
        assert parsed.owner == original.owner
        assert parsed.figma_url == original.figma_url
        assert parsed.figma_file_key == original.figma_file_key
        assert parsed.figma_node_id == original.figma_node_id
        assert parsed.components == original.components
        assert parsed.screens == original.screens
        assert parsed.implements == original.implements
        assert parsed.title == original.title
        assert parsed.description == original.description
        assert parsed.tags == original.tags
