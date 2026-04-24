"""Figma integration utilities for TraceRTM.

This module provides utilities for working with Figma URLs, extracting metadata,
and integrating Figma designs with TraceRTM wireframes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

# Token validation constants
_EXPECTED_TOKEN_COUNT = 2

# Minimum path components required for valid Figma URL (file key + at least one name component)
_FIGMA_PATH_MIN_PARTS = 2
# Expected path components for full Figma URL (file + file_key + file_name)
_FIGMA_PATH_FULL_PARTS = 3


@dataclass
class FigmaMetadata:
    """Metadata extracted from a Figma URL."""

    file_key: str
    node_id: str | None = None
    file_name: str | None = None
    team_id: str | None = None
    full_url: str | None = None

    @property
    def base_url(self) -> str:
        """Get the base Figma file URL without node-id."""
        if self.file_name:
            return f"https://www.figma.com/file/{self.file_key}/{self.file_name}"
        return f"https://www.figma.com/file/{self.file_key}"

    @property
    def node_url(self) -> str | None:
        """Get the full URL with node-id."""
        if self.node_id:
            base = self.base_url
            return f"{base}?node-id={self.node_id}"
        return None

    @property
    def api_file_url(self) -> str:
        """Get the Figma API URL for this file."""
        return f"https://api.figma.com/v1/files/{self.file_key}"

    @property
    def api_node_url(self) -> str | None:
        """Get the Figma API URL for this specific node."""
        if self.node_id:
            return f"https://api.figma.com/v1/files/{self.file_key}/nodes?ids={self.node_id}"
        return None


def parse_figma_url(url: str) -> FigmaMetadata:
    """Parse a Figma URL and extract metadata.

    Supports various Figma URL formats:
    - https://www.figma.com/file/{file_key}/{file_name}
    - https://www.figma.com/file/{file_key}/{file_name}?node-id={node_id}
    - https://www.figma.com/design/{file_key}/{file_name}
    - https://figma.com/file/{file_key}/{file_name}

    Args:
        url: Figma URL to parse

    Returns:
        FigmaMetadata object with extracted information

    Raises:
        ValueError: If the URL is not a valid Figma URL

    Examples:
        >>> meta = parse_figma_url("https://www.figma.com/file/abc123/MyProject?node-id=1:42")
        >>> meta.file_key
        'abc123'
        >>> meta.node_id
        '1:42'
        >>> meta.file_name
        'MyProject'
    """
    # Normalize URL
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Parse URL
    parsed = urlparse(url)

    # Validate domain
    if not parsed.netloc.endswith("figma.com"):
        msg = f"Not a Figma URL: {url}"
        raise ValueError(msg)

    # Extract path components
    path_parts = [p for p in parsed.path.split("/") if p]

    # Check for valid path
    if len(path_parts) < _FIGMA_PATH_MIN_PARTS or path_parts[0] not in {"file", "design"}:
        msg = f"Invalid Figma URL format: {url}"
        raise ValueError(msg)

    file_key = path_parts[1]
    file_name = path_parts[_FIGMA_PATH_FULL_PARTS - 1] if len(path_parts) > _FIGMA_PATH_FULL_PARTS - 1 else None

    # Extract node-id from query parameters
    query_params = parse_qs(parsed.query)
    node_id = query_params.get("node-id", [None])[0]

    return FigmaMetadata(
        file_key=file_key,
        node_id=node_id,
        file_name=file_name,
        full_url=url,
    )


def is_figma_url(url: str) -> bool:
    """Check if a URL is a valid Figma URL.

    Args:
        url: URL to check

    Returns:
        True if the URL is a valid Figma URL, False otherwise

    Examples:
        >>> is_figma_url("https://www.figma.com/file/abc123/MyProject")
        True
        >>> is_figma_url("https://example.com")
        False
    """
    try:
        parse_figma_url(url)
    except ValueError:
        return False
    else:
        return True


def build_figma_url(
    file_key: str,
    file_name: str | None = None,
    node_id: str | None = None,
) -> str:
    """Build a Figma URL from components.

    Args:
        file_key: Figma file key
        file_name: Optional file name for readable URL
        node_id: Optional node ID to link to specific frame

    Returns:
        Formatted Figma URL

    Examples:
        >>> build_figma_url("abc123", "MyProject", "1:42")
        'https://www.figma.com/file/abc123/MyProject?node-id=1:42'
    """
    base = "https://www.figma.com/file"

    url = f"{base}/{file_key}/{file_name}" if file_name else f"{base}/{file_key}"

    if node_id:
        url = f"{url}?node-id={node_id}"

    return url


def extract_figma_protocol_url(markdown_text: str) -> list[tuple[str, str]]:
    """Extract figma:// protocol URLs from markdown text.

    The figma:// protocol is used in markdown to embed Figma previews:
    ![Preview](figma://file_key/node_id)

    Args:
        markdown_text: Markdown content to search

    Returns:
        List of tuples (file_key, node_id) found in the text

    Examples:
        >>> text = "![Preview](figma://abc123/1:42)"
        >>> extract_figma_protocol_url(text)
        [('abc123', '1:42')]
    """
    # Pattern: figma://file_key/node_id
    pattern = r"figma://([a-zA-Z0-9]+)/([0-9:]+)"
    return re.findall(pattern, markdown_text)


def convert_figma_protocol_to_url(markdown_text: str) -> str:
    """Convert figma:// protocol URLs to standard Figma URLs.

    Converts: ![Preview](figma://abc123/1:42)
    To: ![Preview](https://www.figma.com/file/abc123?node-id=1:42)

    Args:
        markdown_text: Markdown content with figma:// URLs

    Returns:
        Markdown with converted URLs

    Examples:
        >>> text = "![Preview](figma://abc123/1:42)"
        >>> convert_figma_protocol_to_url(text)
        '![Preview](https://www.figma.com/file/abc123?node-id=1:42)'
    """

    def replace_figma_url(match: re.Match[str]) -> str:
        file_key = match.group(1)
        node_id = match.group(2)
        return build_figma_url(file_key, node_id=node_id)

    pattern = r"figma://([a-zA-Z0-9]+)/([0-9:]+)"
    return re.sub(pattern, replace_figma_url, markdown_text)


class FigmaAPIError(Exception):
    """Exception raised for Figma API errors."""


def _validate_figma_url(figma_url: str, metadata: dict[str, Any]) -> list[str]:
    """Validate Figma URL and its consistency with metadata.

    Args:
        figma_url: Figma URL string
        metadata: Dictionary containing figma_file_key and figma_node_id

    Returns:
        List of validation error messages
    """
    errors: list[str] = []

    if not is_figma_url(figma_url):
        errors.append(f"Invalid Figma URL: {figma_url}")
        return errors

    try:
        parsed = parse_figma_url(figma_url)

        # Validate file_key matches if provided separately
        file_key = metadata.get("figma_file_key")
        if file_key and file_key != parsed.file_key:
            errors.append(f"figma_file_key '{file_key}' does not match URL file key '{parsed.file_key}'")

        # Validate node_id matches if provided separately
        node_id = metadata.get("figma_node_id")
        if node_id and node_id != parsed.node_id:
            errors.append(f"figma_node_id '{node_id}' does not match URL node ID '{parsed.node_id}'")
    except ValueError as e:
        errors.append(str(e))

    return errors


def _validate_file_key_format(file_key: str) -> bool:
    """Validate file_key format (alphanumeric, no special chars).

    Args:
        file_key: File key to validate

    Returns:
        True if valid format, False otherwise
    """
    return bool(re.match(r"^[a-zA-Z0-9]+$", file_key))


def _validate_node_id_format(node_id: str) -> bool:
    """Validate node_id format (number:number).

    Args:
        node_id: Node ID to validate

    Returns:
        True if valid format, False otherwise
    """
    return bool(re.match(r"^\d+:\d+$", node_id))


def validate_figma_metadata(metadata: dict[str, Any]) -> list[str]:
    """Validate Figma metadata fields.

    Args:
        metadata: Dictionary with Figma metadata fields

    Returns:
        List of validation error messages (empty if valid)

    Examples:
        >>> validate_figma_metadata({"figma_url": "https://www.figma.com/file/abc123/Project"})
        []
        >>> validate_figma_metadata({"figma_url": "https://example.com"})
        ['Invalid Figma URL: https://example.com']
    """
    errors: list[str] = []

    figma_url = metadata.get("figma_url")
    if figma_url:
        errors.extend(_validate_figma_url(figma_url, metadata))

    # Validate file_key format (alphanumeric, no special chars)
    file_key = metadata.get("figma_file_key")
    if file_key and not _validate_file_key_format(file_key):
        errors.append(f"Invalid figma_file_key format: {file_key}")

    # Validate node_id format (number:number)
    node_id = metadata.get("figma_node_id")
    if node_id and not _validate_node_id_format(node_id):
        errors.append(f"Invalid figma_node_id format: {node_id} (expected format: '1:42')")

    return errors
