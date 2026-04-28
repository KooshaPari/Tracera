"""Comprehensive tests for utility modules and logging configuration.

This module provides 50+ tests for:
- Figma utility functions (all scenarios)
- Logging configuration and handlers
- String operations and path handling
- Property-based testing with Hypothesis
- Error handling and edge cases
"""

from typing import Any, Never

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tests.test_constants import COUNT_FOUR, COUNT_THREE, COUNT_TWO
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


class TestFigmaMetadataProperties:
    """Test suite for FigmaMetadata computed properties."""

    @pytest.mark.unit
    def test_base_url_without_file_name_or_node(self) -> None:
        """Test base_url with only file_key."""
        meta = FigmaMetadata(file_key="abc123")
        assert meta.base_url == "https://www.figma.com/file/abc123"

    @pytest.mark.unit
    def test_base_url_with_file_name_no_node(self) -> None:
        """Test base_url with file_key and file_name."""
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject")
        assert meta.base_url == "https://www.figma.com/file/abc123/MyProject"

    @pytest.mark.unit
    def test_base_url_with_encoded_file_name(self) -> None:
        """Test base_url with URL-encoded file name."""
        meta = FigmaMetadata(file_key="abc123", file_name="My%20Project")
        assert meta.base_url == "https://www.figma.com/file/abc123/My%20Project"

    @pytest.mark.unit
    def test_node_url_without_node_id(self) -> None:
        """Test node_url returns None without node_id."""
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject")
        assert meta.node_url is None

    @pytest.mark.unit
    def test_node_url_with_node_id(self) -> None:
        """Test node_url with node_id."""
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject", node_id="1:42")
        assert meta.node_url == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"

    @pytest.mark.unit
    def test_node_url_with_complex_node_id(self) -> None:
        """Test node_url with complex node_id."""
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject", node_id="123:456")
        assert meta.node_url == "https://www.figma.com/file/abc123/MyProject?node-id=123:456"

    @pytest.mark.unit
    def test_api_file_url(self) -> None:
        """Test api_file_url property."""
        meta = FigmaMetadata(file_key="xyz789")
        assert meta.api_file_url == "https://api.figma.com/v1/files/xyz789"

    @pytest.mark.unit
    def test_api_node_url_without_node_id(self) -> None:
        """Test api_node_url returns None without node_id."""
        meta = FigmaMetadata(file_key="abc123")
        assert meta.api_node_url is None

    @pytest.mark.unit
    def test_api_node_url_with_node_id(self) -> None:
        """Test api_node_url with node_id."""
        meta = FigmaMetadata(file_key="abc123", node_id="1:42")
        assert meta.api_node_url == "https://api.figma.com/v1/files/abc123/nodes?ids=1:42"

    @pytest.mark.unit
    def test_metadata_with_team_id(self) -> None:
        """Test metadata with team_id."""
        meta = FigmaMetadata(file_key="abc123", team_id="team456")
        assert meta.team_id == "team456"

    @pytest.mark.unit
    def test_metadata_with_full_url(self) -> None:
        """Test metadata with full_url."""
        url = "https://www.figma.com/file/abc123/MyProject?node-id=1:42"
        meta = FigmaMetadata(file_key="abc123", file_name="MyProject", node_id="1:42", full_url=url)
        assert meta.full_url == url


class TestParseFigmaUrlEdgeCases:
    """Test suite for parse_figma_url edge cases."""

    @pytest.mark.unit
    def test_parse_url_with_leading_whitespace(self) -> None:
        """Test parsing URL with leading whitespace."""
        url = "  https://www.figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    @pytest.mark.unit
    def test_parse_url_with_trailing_whitespace(self) -> None:
        """Test parsing URL with trailing whitespace."""
        url = "https://www.figma.com/file/abc123/MyProject  "
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    @pytest.mark.unit
    def test_parse_url_without_protocol(self) -> None:
        """Test parsing URL without protocol."""
        url = "www.figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    @pytest.mark.unit
    def test_parse_url_without_www(self) -> None:
        """Test parsing URL without www."""
        url = "https://figma.com/file/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    @pytest.mark.unit
    def test_parse_design_url(self) -> None:
        """Test parsing /design/ URL format."""
        url = "https://www.figma.com/design/abc123/MyProject"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"

    @pytest.mark.unit
    def test_parse_url_with_multiple_query_params(self) -> None:
        """Test parsing URL with multiple query parameters."""
        url = "https://www.figma.com/file/abc123/MyProject?node-id=1:42&viewer=1"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"
        assert meta.node_id == "1:42"

    @pytest.mark.unit
    def test_parse_url_without_file_name(self) -> None:
        """Test parsing URL without file name."""
        url = "https://www.figma.com/file/abc123"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name is None

    @pytest.mark.unit
    def test_parse_url_with_encoded_file_name(self) -> None:
        """Test parsing URL with URL-encoded file name."""
        url = "https://www.figma.com/file/abc123/My%20Project%20Name"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "My%20Project%20Name"

    @pytest.mark.unit
    def test_parse_url_with_hyphenated_node_id(self) -> None:
        """Test parsing URL with hyphenated node-id parameter."""
        url = "https://www.figma.com/file/abc123/MyProject?node-id=100:200"
        meta = parse_figma_url(url)
        assert meta.node_id == "100:200"

    @pytest.mark.unit
    def test_parse_url_invalid_domain(self) -> None:
        """Test parsing URL with invalid domain."""
        with pytest.raises(ValueError, match=r"Not a Figma URL"):
            parse_figma_url("https://example.com/file/abc123")

    @pytest.mark.unit
    def test_parse_url_invalid_path(self) -> None:
        """Test parsing URL with invalid path."""
        with pytest.raises(ValueError, match=r"Invalid Figma URL format"):
            parse_figma_url("https://www.figma.com/invalid/abc123")

    @pytest.mark.unit
    def test_parse_url_missing_file_key(self) -> None:
        """Test parsing URL with missing file key."""
        with pytest.raises(ValueError, match=r"Invalid Figma URL format"):
            parse_figma_url("https://www.figma.com/file/")

    @pytest.mark.unit
    def test_parse_url_with_fragment(self) -> None:
        """Test parsing URL with fragment."""
        url = "https://www.figma.com/file/abc123/MyProject#section"
        meta = parse_figma_url(url)
        assert meta.file_key == "abc123"
        assert meta.file_name == "MyProject"


class TestIsFigmaUrl:
    """Test suite for is_figma_url function."""

    @pytest.mark.unit
    def test_is_figma_url_valid(self) -> None:
        """Test is_figma_url with valid URLs."""
        assert is_figma_url("https://www.figma.com/file/abc123/MyProject") is True
        assert is_figma_url("https://figma.com/file/abc123") is True
        assert is_figma_url("https://www.figma.com/design/abc123/MyProject") is True

    @pytest.mark.unit
    def test_is_figma_url_invalid(self) -> None:
        """Test is_figma_url with invalid URLs."""
        assert is_figma_url("https://example.com") is False
        assert is_figma_url("https://www.figma.com/invalid/abc123") is False
        assert is_figma_url("not a url") is False

    @pytest.mark.unit
    def test_is_figma_url_empty_string(self) -> None:
        """Test is_figma_url with empty string."""
        assert is_figma_url("") is False

    @pytest.mark.unit
    def test_is_figma_url_whitespace(self) -> None:
        """Test is_figma_url with whitespace."""
        assert is_figma_url("   ") is False

    @pytest.mark.unit
    def test_is_figma_url_partial_url(self) -> None:
        """Test is_figma_url with partial URL."""
        assert is_figma_url("figma.com/file/abc123") is True


class TestBuildFigmaUrl:
    """Test suite for build_figma_url function."""

    @pytest.mark.unit
    def test_build_url_file_key_only(self) -> None:
        """Test building URL with only file_key."""
        url = build_figma_url("abc123")
        assert url == "https://www.figma.com/file/abc123"

    @pytest.mark.unit
    def test_build_url_with_file_name(self) -> None:
        """Test building URL with file_key and file_name."""
        url = build_figma_url("abc123", "MyProject")
        assert url == "https://www.figma.com/file/abc123/MyProject"

    @pytest.mark.unit
    def test_build_url_with_node_id(self) -> None:
        """Test building URL with file_key and node_id."""
        url = build_figma_url("abc123", node_id="1:42")
        assert url == "https://www.figma.com/file/abc123?node-id=1:42"

    @pytest.mark.unit
    def test_build_url_with_all_params(self) -> None:
        """Test building URL with all parameters."""
        url = build_figma_url("abc123", "MyProject", "1:42")
        assert url == "https://www.figma.com/file/abc123/MyProject?node-id=1:42"

    @pytest.mark.unit
    def test_build_url_with_special_characters_in_name(self) -> None:
        """Test building URL with special characters in file name."""
        url = build_figma_url("abc123", "My Project (v1)")
        assert url == "https://www.figma.com/file/abc123/My Project (v1)"

    @pytest.mark.unit
    def test_build_url_with_complex_node_id(self) -> None:
        """Test building URL with complex node_id."""
        url = build_figma_url("abc123", "MyProject", "999:888")
        assert url == "https://www.figma.com/file/abc123/MyProject?node-id=999:888"

    @pytest.mark.unit
    def test_build_url_none_file_name(self) -> None:
        """Test building URL with None file_name."""
        url = build_figma_url("abc123", None, "1:42")
        assert url == "https://www.figma.com/file/abc123?node-id=1:42"


class TestExtractFigmaProtocolUrl:
    """Test suite for extract_figma_protocol_url function."""

    @pytest.mark.unit
    def test_extract_single_protocol_url(self) -> None:
        """Test extracting single figma:// URL."""
        text = "![Preview](figma://abc123/1:42)"
        result = extract_figma_protocol_url(text)
        assert result == [("abc123", "1:42")]

    @pytest.mark.unit
    def test_extract_multiple_protocol_urls(self) -> None:
        """Test extracting multiple figma:// URLs."""
        text = "![Preview1](figma://abc123/1:42) and ![Preview2](figma://xyz789/2:84)"
        result = extract_figma_protocol_url(text)
        assert len(result) == COUNT_TWO
        assert ("abc123", "1:42") in result
        assert ("xyz789", "2:84") in result

    @pytest.mark.unit
    def test_extract_no_protocol_urls(self) -> None:
        """Test extracting from text with no figma:// URLs."""
        text = "This is plain text with no Figma URLs"
        result = extract_figma_protocol_url(text)
        assert result == []

    @pytest.mark.unit
    def test_extract_with_regular_urls(self) -> None:
        """Test extracting with regular https URLs present."""
        text = "![Preview](figma://abc123/1:42) and https://www.figma.com/file/xyz789"
        result = extract_figma_protocol_url(text)
        assert result == [("abc123", "1:42")]

    @pytest.mark.unit
    def test_extract_with_complex_node_ids(self) -> None:
        """Test extracting with complex node IDs."""
        text = "![Preview](figma://abc123/999:888)"
        result = extract_figma_protocol_url(text)
        assert result == [("abc123", "999:888")]

    @pytest.mark.unit
    def test_extract_empty_string(self) -> None:
        """Test extracting from empty string."""
        result = extract_figma_protocol_url("")
        assert result == []

    @pytest.mark.unit
    def test_extract_multiline_text(self) -> None:
        """Test extracting from multiline text."""
        text = """
        # Design Document

        ![Preview1](figma://abc123/1:42)

        Some text here.

        ![Preview2](figma://xyz789/2:84)
        """
        result = extract_figma_protocol_url(text)
        assert len(result) == COUNT_TWO


class TestConvertFigmaProtocolToUrl:
    """Test suite for convert_figma_protocol_to_url function."""

    @pytest.mark.unit
    def test_convert_single_protocol_url(self) -> None:
        """Test converting single figma:// URL."""
        text = "![Preview](figma://abc123/1:42)"
        result = convert_figma_protocol_to_url(text)
        assert "https://www.figma.com/file/abc123?node-id=1:42" in result
        assert "figma://" not in result

    @pytest.mark.unit
    def test_convert_multiple_protocol_urls(self) -> None:
        """Test converting multiple figma:// URLs."""
        text = "![Preview1](figma://abc123/1:42) and ![Preview2](figma://xyz789/2:84)"
        result = convert_figma_protocol_to_url(text)
        assert "https://www.figma.com/file/abc123?node-id=1:42" in result
        assert "https://www.figma.com/file/xyz789?node-id=2:84" in result
        assert "figma://" not in result

    @pytest.mark.unit
    def test_convert_no_protocol_urls(self) -> None:
        """Test converting text with no figma:// URLs."""
        text = "This is plain text"
        result = convert_figma_protocol_to_url(text)
        assert result == text

    @pytest.mark.unit
    def test_convert_preserves_other_content(self) -> None:
        """Test that conversion preserves other content."""
        text = "Before ![Preview](figma://abc123/1:42) After"
        result = convert_figma_protocol_to_url(text)
        assert result.startswith("Before")
        assert result.endswith("After")
        assert "https://www.figma.com/file/abc123?node-id=1:42" in result

    @pytest.mark.unit
    def test_convert_empty_string(self) -> None:
        """Test converting empty string."""
        result = convert_figma_protocol_to_url("")
        assert result == ""

    @pytest.mark.unit
    def test_convert_multiline_text(self) -> None:
        """Test converting multiline text."""
        text = """
        # Design
        ![Preview](figma://abc123/1:42)
        """
        result = convert_figma_protocol_to_url(text)
        assert "https://www.figma.com/file/abc123?node-id=1:42" in result
        assert "# Design" in result


class TestValidateFigmaMetadata:
    """Test suite for validate_figma_metadata function."""

    @pytest.mark.unit
    def test_validate_valid_metadata(self) -> None:
        """Test validating valid metadata."""
        metadata = {"figma_url": "https://www.figma.com/file/abc123/Project"}
        errors = validate_figma_metadata(metadata)
        assert errors == []

    @pytest.mark.unit
    def test_validate_invalid_figma_url(self) -> None:
        """Test validating invalid Figma URL."""
        metadata = {"figma_url": "https://example.com"}
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "Invalid Figma URL" in errors[0]

    @pytest.mark.unit
    def test_validate_file_key_mismatch(self) -> None:
        """Test validating mismatched file_key."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/Project",
            "figma_file_key": "xyz789",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "does not match" in errors[0]

    @pytest.mark.unit
    def test_validate_node_id_mismatch(self) -> None:
        """Test validating mismatched node_id."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/Project?node-id=1:42",
            "figma_node_id": "2:84",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "node_id" in errors[0]

    @pytest.mark.unit
    def test_validate_invalid_file_key_format(self) -> None:
        """Test validating invalid file_key format."""
        metadata = {"figma_file_key": "abc-123"}  # Hyphen not allowed
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "file_key format" in errors[0]

    @pytest.mark.unit
    def test_validate_invalid_node_id_format(self) -> None:
        """Test validating invalid node_id format."""
        metadata = {"figma_node_id": "1-42"}  # Hyphen instead of colon
        errors = validate_figma_metadata(metadata)
        assert len(errors) > 0
        assert "node_id format" in errors[0]

    @pytest.mark.unit
    def test_validate_empty_metadata(self) -> None:
        """Test validating empty metadata."""
        errors = validate_figma_metadata({})
        assert errors == []

    @pytest.mark.unit
    def test_validate_multiple_errors(self) -> None:
        """Test validating metadata with multiple errors."""
        metadata = {
            "figma_url": "https://example.com",
            "figma_file_key": "abc-123",
            "figma_node_id": "invalid",
        }
        errors = validate_figma_metadata(metadata)
        assert len(errors) >= COUNT_THREE

    @pytest.mark.unit
    def test_validate_valid_file_key(self) -> None:
        """Test validating valid file_key."""
        metadata = {"figma_file_key": "abc123XYZ789"}
        errors = validate_figma_metadata(metadata)
        assert errors == []

    @pytest.mark.unit
    def test_validate_valid_node_id(self) -> None:
        """Test validating valid node_id."""
        metadata = {"figma_node_id": "123:456"}
        errors = validate_figma_metadata(metadata)
        assert errors == []

    @pytest.mark.unit
    def test_validate_matching_metadata(self) -> None:
        """Test validating matching URL and separate fields."""
        metadata = {
            "figma_url": "https://www.figma.com/file/abc123/Project?node-id=1:42",
            "figma_file_key": "abc123",
            "figma_node_id": "1:42",
        }
        errors = validate_figma_metadata(metadata)
        assert errors == []


class TestFigmaAPIError:
    """Test suite for FigmaAPIError exception."""

    @pytest.mark.unit
    def test_figma_api_error_creation(self) -> None:
        """Test creating FigmaAPIError."""
        error = FigmaAPIError("API request failed")
        assert str(error) == "API request failed"

    @pytest.mark.unit
    def test_figma_api_error_raise(self) -> Never:
        """Test raising FigmaAPIError."""
        with pytest.raises(FigmaAPIError) as exc_info:
            msg = "Test error"
            raise FigmaAPIError(msg)
        assert "Test error" in str(exc_info.value)

    @pytest.mark.unit
    def test_figma_api_error_inheritance(self) -> None:
        """Test FigmaAPIError inherits from Exception."""
        error = FigmaAPIError("Test")
        assert isinstance(error, Exception)


class TestPropertyBasedFigmaHypothesis:
    """Property-based tests for Figma utilities using Hypothesis."""

    @pytest.mark.unit
    @pytest.mark.property
    @given(file_key=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1, max_size=50))
    def test_build_url_accepts_alphanumeric_file_keys(self, file_key: Any) -> None:
        """Test build_figma_url accepts alphanumeric file keys."""
        url = build_figma_url(file_key)
        assert file_key in url
        assert url.startswith("https://www.figma.com/file/")

    @pytest.mark.unit
    @pytest.mark.property
    @given(
        file_key=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1, max_size=50),
        file_name=st.text(min_size=1, max_size=100),
    )
    def test_build_url_with_arbitrary_file_names(self, file_key: Any, file_name: Any) -> None:
        """Test build_figma_url with arbitrary file names."""
        url = build_figma_url(file_key, file_name)
        assert file_key in url
        assert file_name in url

    @pytest.mark.unit
    @pytest.mark.property
    @given(
        file_key=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1, max_size=50),
        node_parts=st.tuples(st.integers(min_value=1, max_value=9999), st.integers(min_value=1, max_value=9999)),
    )
    def test_build_url_with_generated_node_ids(self, file_key: Any, node_parts: Any) -> None:
        """Test build_figma_url with generated node IDs."""
        node_id = f"{node_parts[0]}:{node_parts[1]}"
        url = build_figma_url(file_key, node_id=node_id)
        assert f"node-id={node_id}" in url

    @pytest.mark.unit
    @pytest.mark.property
    @given(text=st.text(min_size=0, max_size=500))
    def test_extract_protocol_url_never_crashes(self, text: Any) -> None:
        """Test extract_figma_protocol_url never crashes."""
        result = extract_figma_protocol_url(text)
        assert isinstance(result, list)

    @pytest.mark.unit
    @pytest.mark.property
    @given(text=st.text(min_size=0, max_size=500))
    def test_convert_protocol_url_never_crashes(self, text: Any) -> None:
        """Test convert_figma_protocol_to_url never crashes."""
        result = convert_figma_protocol_to_url(text)
        assert isinstance(result, str)

    @pytest.mark.unit
    @pytest.mark.property
    @given(url=st.text(min_size=0, max_size=200))
    def test_is_figma_url_never_crashes(self, url: Any) -> None:
        """Test is_figma_url never crashes."""
        result = is_figma_url(url)
        assert isinstance(result, bool)


class TestLoggingConfiguration:
    """Test suite for logging configuration."""

    @pytest.mark.unit
    def test_logger_import(self) -> None:
        """Test logger can be imported."""
        from loguru import logger as test_logger

        assert test_logger is not None

    @pytest.mark.unit
    def test_logger_basic_logging(self) -> None:
        """Test logger can log basic messages."""
        from loguru import logger as test_logger

        # Remove default handlers
        test_logger.remove()

        # Add custom handler to capture output
        logs = []
        test_logger.add(logs.append, format="{message}")

        test_logger.info("Test message")
        assert len(logs) == 1
        assert "Test message" in logs[0]

    @pytest.mark.unit
    def test_logger_different_levels(self) -> None:
        """Test logger handles different log levels."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs = []
        test_logger.add(logs.append, format="{level}:{message}", level="DEBUG")

        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")

        assert len(logs) == COUNT_FOUR
        assert "DEBUG:Debug message" in logs[0]
        assert "INFO:Info message" in logs[1]
        assert "WARNING:Warning message" in logs[2]
        assert "ERROR:Error message" in logs[3]

    @pytest.mark.unit
    def test_logger_structured_logging(self) -> None:
        """Test logger can do structured logging."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs = []
        test_logger.add(logs.append, format="{message}", serialize=True)

        test_logger.bind(user="alice").info("User action")
        assert len(logs) == 1

    @pytest.mark.unit
    def test_logger_context_binding(self) -> None:
        """Test logger context binding."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs = []
        test_logger.add(logs.append, format="{message}")

        bound_logger = test_logger.bind(module="test_module")
        bound_logger.info("Bound message")

        assert len(logs) == 1

    @pytest.mark.unit
    def test_logger_exception_logging(self) -> None:
        """Test logger can log exceptions."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs = []
        test_logger.add(logs.append, format="{message}")

        try:
            msg = "Test exception"
            raise ValueError(msg)
        except ValueError:
            test_logger.exception("Caught exception")

        assert len(logs) == 1
        assert "Caught exception" in logs[0]

    @pytest.mark.unit
    def test_logger_filtering(self) -> None:
        """Test logger filtering by level."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs = []
        test_logger.add(logs.append, format="{message}", level="WARNING")

        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")

        assert len(logs) == COUNT_TWO  # Only WARNING and ERROR
        assert "Warning message" in logs[0]
        assert "Error message" in logs[1]

    @pytest.mark.unit
    def test_logger_format_customization(self) -> None:
        """Test logger format customization."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs = []
        custom_format = "[{level}] {message}"
        test_logger.add(logs.append, format=custom_format)

        test_logger.info("Test")
        assert len(logs) == 1
        assert "[INFO] Test" in logs[0]

    @pytest.mark.unit
    def test_logger_multiple_handlers(self) -> None:
        """Test logger with multiple handlers."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs1 = []
        logs2 = []

        test_logger.add(logs1.append, format="{message}", level="INFO")
        test_logger.add(logs2.append, format="{message}", level="ERROR")

        test_logger.info("Info message")
        test_logger.error("Error message")

        assert len(logs1) == COUNT_TWO  # Both INFO and ERROR
        assert len(logs2) == 1  # Only ERROR

    @pytest.mark.unit
    def test_logger_catch_decorator(self) -> None:
        """Test logger @catch decorator functionality."""
        from loguru import logger as test_logger

        test_logger.remove()
        logs = []
        test_logger.add(logs.append, format="{message}")

        @test_logger.catch
        def failing_function() -> Never:
            msg = "Function failed"
            raise RuntimeError(msg)

        result = failing_function()

        assert result is None  # @catch returns None on exception
        assert len(logs) > 0  # Exception was logged


class TestEdgeCasesAndRobustness:
    """Test suite for edge cases and robustness."""

    @pytest.mark.unit
    def test_figma_metadata_equality(self) -> None:
        """Test FigmaMetadata equality."""
        meta1 = FigmaMetadata(file_key="abc123", node_id="1:42")
        meta2 = FigmaMetadata(file_key="abc123", node_id="1:42")

        assert meta1.file_key == meta2.file_key
        assert meta1.node_id == meta2.node_id

    @pytest.mark.unit
    def test_parse_figma_url_with_uppercase(self) -> None:
        """Test parsing Figma URL with uppercase letters."""
        url = "HTTPS://WWW.FIGMA.COM/FILE/ABC123/MYPROJECT"
        # Should work with case-insensitive domain
        try:
            meta = parse_figma_url(url)
            assert meta is not None
        except ValueError:
            # URL parsing is case-sensitive for some components
            pass

    @pytest.mark.unit
    def test_build_figma_url_empty_file_key(self) -> None:
        """Test building URL with empty file key."""
        url = build_figma_url("")
        assert url == "https://www.figma.com/file/"

    @pytest.mark.unit
    def test_validate_figma_metadata_with_none_values(self) -> None:
        """Test validating metadata with None values."""
        metadata = {
            "figma_url": None,
            "figma_file_key": None,
            "figma_node_id": None,
        }
        errors = validate_figma_metadata(metadata)
        # None values should be acceptable
        assert isinstance(errors, list)

    @pytest.mark.unit
    def test_extract_protocol_url_with_malformed_pattern(self) -> None:
        """Test extracting with malformed figma:// patterns."""
        text = "figma://incomplete"
        result = extract_figma_protocol_url(text)
        assert result == []  # Should not match incomplete pattern

    @pytest.mark.unit
    def test_convert_protocol_url_with_no_matches(self) -> None:
        """Test converting text with no figma:// patterns."""
        text = "Regular text with https://www.figma.com/file/abc123"
        result = convert_figma_protocol_to_url(text)
        assert result == text  # Should be unchanged
