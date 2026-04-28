"""Comprehensive unit tests for Figma utilities module.

Tests all functions in tracertm.utils.figma:
- parse_figma_url
- is_figma_url
- build_figma_url
- extract_figma_protocol_url
- convert_figma_protocol_to_url
- validate_figma_metadata
- FigmaMetadata dataclass
"""

from typing import Never

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.utils.figma import (
    FigmaAPIError,
    FigmaMetadata,
    build_figma_url,
    convert_figma_protocol_to_url,
    extract_figma_protocol_url,
    is_figma_url,
    parse_figma_url,
    validate_figma_metadata,
)


class TestFigmaMetadataDataclass:
    """Test FigmaMetadata dataclass."""

    def test_create_minimal_metadata(self) -> None:
        """Test creating metadata with only file_key."""
        meta = FigmaMetadata(file_key="abc123")
        assert meta.file_key == "abc123"
        assert meta.node_id is None
        assert meta.file_name is None
        assert meta.team_id is None
        assert meta.full_url is None

    def test_create_full_metadata(self) -> None:
        """Test creating metadata with all fields."""
        meta = FigmaMetadata(
            file_key="abc123",
            node_id="1:42",
            file_name="MyProject",
            team_id="team123",
            full_url="https://www.figma.com/file/abc123/MyProject?node-id=1:42",
        )
        assert meta.file_key == "abc123"
        assert meta.node_id == "1:42"
        assert meta.file_name == "MyProject"
        assert meta.team_id == "team123"
        assert meta.full_url == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"

    def test_base_url_with_file_name(self) -> None:
        """Test base_url property with file_name."""
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject")
        assert meta.base_url == "https://www.figma.com/file/abc123/MyProject"

    def test_base_url_without_file_name(self) -> None:
        """Test base_url property without file_name."""
        meta = FigmaMetadata(file_key="abc123")
        assert meta.base_url == "https://www.figma.com/file/abc123"

    def test_node_url_with_node_id(self) -> None:
        """Test node_url property with node_id."""
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject", node_id="1:42")
        assert meta.node_url == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"

    def test_node_url_without_node_id(self) -> None:
        """Test node_url property without node_id."""
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject")
        assert meta.node_url is None

    def test_api_file_url(self) -> None:
        """Test api_file_url property."""
        meta = FigmaMetadata(file_key="abc123")
        assert meta.api_file_url == "https://api.figma.com/v1/files/abc123"

    def test_api_node_url_with_node_id(self) -> None:
        """Test api_node_url property with node_id."""
        meta = FigmaMetadata(file_key="abc123", node_id="1:42")
        assert meta.api_node_url == "https://api.figma.com/v1/files/abc123/nodes?ids=1:42"

    def test_api_node_url_without_node_id(self) -> None:
        """Test api_node_url property without node_id."""
        meta = FigmaMetadata(file_key="abc123")
        assert meta.api_node_url is None


class TestParseFigmaUrl:
    """Test parse_figma_url function."""

    def test_parse_basic_file_url(self) -> None:
        """Test parsing basic file URL."""
        url = "https://www.figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"
        assert meta.node_id is None

    def test_parse_file_url_with_node_id(self) -> None:
        """Test parsing file URL with node-id."""
        url = "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"
        assert meta.node_id == "1:42"

    def test_parse_design_url(self) -> None:
        """Test parsing design URL (alternative path)."""
        url = "https://www.figma.com/design/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    def test_parse_url_without_https(self) -> None:
        """Test parsing URL without https prefix."""
        url = "figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    def test_parse_url_with_http(self) -> None:
        """Test parsing URL with http prefix."""
        url = "http://www.figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    def test_parse_url_with_subdomain(self) -> None:
        """Test parsing URL with www subdomain."""
        url = "https://www.figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"

    def test_parse_url_without_file_name(self) -> None:
        """Test parsing URL without file name."""
        url = "https://www.figma.com/file/abc123"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name is None

    def test_parse_url_with_multiple_query_params(self) -> None:
        """Test parsing URL with multiple query parameters."""
        url = "https://www.figma.com/file/abc123/MyProject?node-id=1:42&viewer=1"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.node_id == "1:42"

    def test_parse_url_with_complex_node_id(self) -> None:
        """Test parsing URL with complex node-id."""
        url = "https://www.figma.com/file/abc123/MyProject?node-id=123:456"
        meta = parse_figma_url(url)
        assert meta.node_id == "123:456"

    def test_parse_url_with_whitespace(self) -> None:
        """Test parsing URL with leading/trailing whitespace."""
        url = "  https://www.figma.com/file/abc123/MyProject  "
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"

    def test_parse_url_stores_full_url(self) -> None:
        """Test that full_url is stored."""
        url = "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
        meta = parse_figma_url(url)
        assert meta.full_url == url

    def test_invalid_url_not_figma(self) -> None:
        """Test parsing non-Figma URL raises error."""
        with pytest.raises(ValueError, match="Not a Figma URL"):
            parse_figma_url("https://example.com")

    def test_invalid_url_wrong_path(self) -> None:
        """Test parsing Figma URL with wrong path raises error."""
        with pytest.raises(ValueError, match="Invalid Figma URL format"):
            parse_figma_url("https://www.figma.com/invalid/path")

    def test_invalid_url_missing_file_key(self) -> None:
        """Test parsing Figma URL without file key raises error."""
        with pytest.raises(ValueError, match="Invalid Figma URL format"):
            parse_figma_url("https://www.figma.com/file/")

    def test_parse_url_with_encoded_characters(self) -> None:
        """Test parsing URL with URL-encoded characters in file name."""
        url = "https://www.figma.com/file/abc123/My%20Project"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "My%20Project"


class TestIsFigmaUrl:
    """Test is_figma_url function."""

    def test_valid_file_url(self) -> None:
        """Test valid file URL returns True."""
        assert is_figma_url("https://www.figma.com/file/abc123/MyProject") is True

    def test_valid_design_url(self) -> None:
        """Test valid design URL returns True."""
        assert is_figma_url("https://www.figma.com/design/abc123/MyProject") is True

    def test_valid_url_with_node_id(self) -> None:
        """Test valid URL with node-id returns True."""
        assert is_figma_url("https://www.figma.com/file/abc123/MyProject?node-id=1:42") is True

    def test_invalid_url_not_figma(self) -> None:
        """Test non-Figma URL returns False."""
        assert is_figma_url("https://example.com") is False

    def test_invalid_url_wrong_path(self) -> None:
        """Test Figma URL with wrong path returns False."""
        assert is_figma_url("https://www.figma.com/invalid/path") is False

    def test_invalid_url_empty_string(self) -> None:
        """Test empty string returns False."""
        assert is_figma_url("") is False

    def test_invalid_url_malformed(self) -> None:
        """Test malformed URL returns False."""
        assert is_figma_url("not a url") is False


class TestBuildFigmaUrl:
    """Test build_figma_url function."""

    def test_build_url_file_key_only(self) -> None:
        """Test building URL with file_key only."""
        url = build_figma_url("abc123")
        assert url == "https://www.figma.com/file/abc123"

    def test_build_url_with_file_name(self) -> None:
        """Test building URL with file_name."""
        url = build_figma_url("abc123", file_name="MyProject")
        assert url == "https://www.figma.com/file/abc123/MyProject"

    def test_build_url_with_node_id(self) -> None:
        """Test building URL with node_id."""
        url = build_figma_url("abc123", node_id="1:42")
        assert url == "https://www.figma.com/file/abc123?node-id=1:42"

    def test_build_url_with_all_params(self) -> None:
        """Test building URL with all parameters."""
        url = build_figma_url("abc123", file_name="MyProject", node_id="1:42")
        assert url == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"

    def test_build_url_with_complex_node_id(self) -> None:
        """Test building URL with complex node_id."""
        url = build_figma_url("abc123", node_id="123:456")
        assert url == "https://www.figma.com/file/abc123?node-id=123:456"

    def test_build_url_with_special_chars_in_name(self) -> None:
        """Test building URL with special characters in file_name."""
        url = build_figma_url("abc123", file_name="My-Project_v2")
        assert url == "https://www.figma.com/file/abc123/My-Project_v2"


class TestExtractFigmaProtocolUrl:
    """Test extract_figma_protocol_url function."""

    def test_extract_single_protocol_url(self) -> None:
        """Test extracting single figma:// URL."""
        markdown = "![Preview](figma://abc123/1:42)"
        results = extract_figma_protocol_url(markdown)
        assert len(results) == 1
        assert results[0] == ("abc123", "1:42")

    def test_extract_multiple_protocol_urls(self) -> None:
        """Test extracting multiple figma:// URLs."""
        markdown = """
        ![Preview1](figma://abc123/1:42)
        Some text
        ![Preview2](figma://def456/2:84)
        """
        results = extract_figma_protocol_url(markdown)
        assert len(results) == COUNT_TWO
        assert ("abc123", "1:42") in results
        assert ("def456", "2:84") in results

    def test_extract_no_protocol_urls(self) -> None:
        """Test extracting from markdown with no figma:// URLs."""
        markdown = "Just some regular text with no Figma URLs"
        results = extract_figma_protocol_url(markdown)
        assert len(results) == 0

    def test_extract_mixed_urls(self) -> None:
        """Test extracting from markdown with mixed URL types."""
        markdown = """
        Regular link: [Figma](https://figma.com/file/abc123)
        Protocol link: ![Preview](figma://abc123/1:42)
        """
        results = extract_figma_protocol_url(markdown)
        assert len(results) == 1
        assert results[0] == ("abc123", "1:42")

    def test_extract_with_complex_node_ids(self) -> None:
        """Test extracting URLs with complex node IDs."""
        markdown = "![Preview](figma://xyz789/123:456)"
        results = extract_figma_protocol_url(markdown)
        assert results[0] == ("xyz789", "123:456")

    def test_extract_from_empty_string(self) -> None:
        """Test extracting from empty string."""
        results = extract_figma_protocol_url("")
        assert len(results) == 0


class TestConvertFigmaProtocolToUrl:
    """Test convert_figma_protocol_to_url function."""

    def test_convert_single_protocol_url(self) -> None:
        """Test converting single figma:// URL."""
        markdown = "![Preview](figma://abc123/1:42)"
        result = convert_figma_protocol_to_url(markdown)
        assert result == "![Preview](https://www.figma.com/file/abc123?node-id=1:42)"

    def test_convert_multiple_protocol_urls(self) -> None:
        """Test converting multiple figma:// URLs."""
        markdown = """
        ![Preview1](figma://abc123/1:42)
        Some text
        ![Preview2](figma://def456/2:84)
        """
        result = convert_figma_protocol_to_url(markdown)
        assert "https://www.figma.com/file/abc123?node-id=1:42" in result
        assert "https://www.figma.com/file/def456?node-id=2:84" in result
        assert "figma://" not in result

    def test_convert_no_protocol_urls(self) -> None:
        """Test converting markdown with no figma:// URLs."""
        markdown = "Just some regular text"
        result = convert_figma_protocol_to_url(markdown)
        assert result == markdown

    def test_convert_preserves_other_content(self) -> None:
        """Test that conversion preserves other markdown content."""
        markdown = """
        # Heading
        Some text with ![Preview](figma://abc123/1:42) inline.
        More text.
        """
        result = convert_figma_protocol_to_url(markdown)
        assert "# Heading" in result
        assert "Some text with" in result
        assert "More text." in result
        assert "https://www.figma.com/file/abc123?node-id=1:42" in result

    def test_convert_with_complex_node_ids(self) -> None:
        """Test converting URLs with complex node IDs."""
        markdown = "![Preview](figma://xyz789/123:456)"
        result = convert_figma_protocol_to_url(markdown)
        assert result == "![Preview](https://www.figma.com/file/xyz789?node-id=123:456)"


class TestValidateFigmaMetadata:
    """Test validate_figma_metadata function."""

    def test_validate_valid_metadata(self) -> None:
        """Test validating valid Figma metadata."""
        metadata = {"figma_url": "https://www.figma.com/file/abc123/MyProject"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 0

    def test_validate_valid_metadata_with_node_id(self) -> None:
        """Test validating valid metadata with node_id."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/MyProject?node-id=1:42",
            "figma_file_key": "abc123",
            "figma_node_id": "1:42",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 0

    def test_validate_invalid_figma_url(self) -> None:
        """Test validating invalid Figma URL."""
        metadata = {"figma_url": "https://example.com"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 1
        assert "Invalid Figma URL" in errors[0]

    def test_validate_mismatched_file_key(self) -> None:
        """Test validating mismatched file_key."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/MyProject",
            "figma_file_key": "xyz789",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 1
        assert "file_key" in errors[0]
        assert "does not match" in errors[0]

    def test_validate_mismatched_node_id(self) -> None:
        """Test validating mismatched node_id."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/MyProject?node-id=1:42",
            "figma_node_id": "2:84",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 1
        assert "node_id" in errors[0]
        assert "does not match" in errors[0]

    def test_validate_invalid_file_key_format(self) -> None:
        """Test validating invalid file_key format."""
        metadata = {"figma_file_key": "invalid-key-with-dashes!"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 1
        assert "Invalid figma_file_key format" in errors[0]

    def test_validate_invalid_node_id_format(self) -> None:
        """Test validating invalid node_id format."""
        metadata = {"figma_node_id": "invalid"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 1
        assert "Invalid figma_node_id format" in errors[0]
        assert "expected format: '1:42'" in errors[0]

    def test_validate_valid_node_id_format(self) -> None:
        """Test validating valid node_id format."""
        metadata = {"figma_node_id": "123:456"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 0

    def test_validate_multiple_errors(self) -> None:
        """Test validating metadata with multiple errors."""
        metadata = {
            "figma_url": "https://example.com",
            "figma_file_key": "invalid-key!",
            "figma_node_id": "invalid",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) >= COUNT_TWO  # At least URL and format errors

    def test_validate_empty_metadata(self) -> None:
        """Test validating empty metadata."""
        metadata = {}
        errors = validate_figma_metadata(metadata)
        assert len(errors) == 0  # No errors if no Figma fields provided


class TestFigmaAPIError:
    """Test FigmaAPIError exception."""

    def test_create_figma_api_error(self) -> None:
        """Test creating FigmaAPIError."""
        error = FigmaAPIError("Test error message")
        assert str(error) == "Test error message"

    def test_raise_figma_api_error(self) -> Never:
        """Test raising FigmaAPIError."""
        with pytest.raises(FigmaAPIError) as exc_info:
            msg = "API error"
            raise FigmaAPIError(msg)
        assert str(exc_info.value) == "API error"

    def test_figma_api_error_is_exception(self) -> None:
        """Test that FigmaAPIError is an Exception."""
        error = FigmaAPIError("Test")
        assert isinstance(error, Exception)
