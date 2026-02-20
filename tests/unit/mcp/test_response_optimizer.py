from typing import Any

"""Unit tests for response_optimizer module."""

import json

from tests.test_constants import COUNT_FIVE, COUNT_TWO
from tracertm.mcp.tools.response_optimizer import (
    ResponseFormat,
    format_error,
    format_response,
    optimize_item_response,
    optimize_link_response,
    paginate_response,
)


class TestResponseFormat:
    """Test response formatting."""

    def test_lean_format(self) -> None:
        """Test lean response format (just data)."""
        data = {"id": "123", "title": "Test"}
        result = format_response(data, format_mode=ResponseFormat.LEAN)

        assert result == data
        assert "ok" not in result
        assert "actor" not in result

    def test_standard_format(self) -> None:
        """Test standard response format (minimal metadata)."""
        data = {"id": "123", "title": "Test"}
        result = format_response(data, format_mode=ResponseFormat.STANDARD)

        assert result["ok"] is True
        assert result["data"] == data
        assert "actor" not in result

    def test_verbose_format(self) -> None:
        """Test verbose response format (full metadata)."""
        data = {"id": "123", "title": "Test"}
        result = format_response(data, format_mode=ResponseFormat.VERBOSE)

        assert result["ok"] is True
        assert result["data"] == data
        assert "actor" in result

    def test_compression_threshold(self) -> None:
        """Test compression is applied when threshold exceeded."""
        # Create data larger than threshold
        large_data = {"items": [{"id": str(i), "title": f"Item {i}"} for i in range(100)]}

        result = format_response(
            large_data,
            compress=True,
            compress_threshold=100,  # Low threshold
        )

        assert result.get("compressed") is True
        assert result.get("encoding") == "gzip+base64"
        assert "data" in result
        assert result["compressed_size"] < result["original_size"]

    def test_no_compression_below_threshold(self) -> None:
        """Test compression not applied below threshold."""
        small_data = {"id": "123"}

        result = format_response(
            small_data,
            compress=True,
            compress_threshold=1000,  # High threshold
        )

        # Should return data without compression
        assert "compressed" not in result or result.get("compressed") is False


class TestErrorFormatting:
    """Test error response formatting."""

    def test_lean_error(self) -> None:
        """Test lean error format."""
        result = format_error("Test error", action="test", format_mode=ResponseFormat.LEAN)

        assert result["ok"] is False
        assert result["error"] == "Test error"
        assert "category" in result
        assert "action" not in result
        assert "actor" not in result

    def test_error_with_suggestions(self) -> None:
        """Test error includes suggestions."""
        result = format_error(
            "Item not found",
            suggestions=["Check item ID", "Try query_items()"],
            format_mode=ResponseFormat.LEAN,
        )

        assert "suggestions" in result
        assert len(result["suggestions"]) == COUNT_TWO
        assert "Check item ID" in result["suggestions"]

    def test_error_categorization(self) -> None:
        """Test automatic error categorization."""
        # Test not_found
        result = format_error("Item not found: abc", format_mode=ResponseFormat.LEAN)
        assert result["category"] == "not_found"

        # Test validation
        result = format_error("field is required", format_mode=ResponseFormat.LEAN)
        assert result["category"] == "validation"

        # Test auth
        result = format_error("access denied", format_mode=ResponseFormat.LEAN)
        assert result["category"] == "auth"

    def test_auto_suggestions_not_found(self) -> None:
        """Test auto-generated suggestions for not_found errors."""
        result = format_error("Project not found", category="not_found")

        assert "suggestions" in result
        assert any("select_project" in s for s in result["suggestions"])

    def test_auto_suggestions_validation(self) -> None:
        """Test auto-generated suggestions for validation errors."""
        result = format_error("project_id is required", category="validation")

        assert "suggestions" in result
        assert any("select_project" in s for s in result["suggestions"])


class TestItemOptimization:
    """Test item response optimization."""

    def test_optimize_item_dict(self) -> None:
        """Test optimizing item from dict."""
        item = {
            "id": "12345678-1234-1234-1234-123456789012",
            "title": "Test Item",
            "view": "FEATURE",
            "item_type": "epic",
            "status": "active",
            "item_metadata": {"key": "value"},
        }

        result = optimize_item_response(item, include_metadata=False)

        assert result["id"] == "12345678"  # Short ID
        assert result["title"] == "Test Item"
        assert result["view"] == "FEATURE"
        assert result["type"] == "epic"
        assert result["status"] == "active"
        assert "metadata" not in result

    def test_optimize_item_with_metadata(self) -> None:
        """Test optimizing item includes metadata when requested."""
        item = {
            "id": "12345678-1234-1234-1234-123456789012",
            "title": "Test Item",
            "view": "FEATURE",
            "item_type": "epic",
            "status": "active",
            "item_metadata": {"key": "value"},
        }

        result = optimize_item_response(item, include_metadata=True)

        assert "metadata" in result
        assert result["metadata"] == {"key": "value"}

    def test_optimize_item_model(self) -> None:
        """Test optimizing item from model object."""

        class MockItem:
            id = "12345678-1234-1234-1234-123456789012"
            title = "Test Item"
            view = "FEATURE"
            item_type = "epic"
            status = "active"
            item_metadata = None

        item = MockItem()
        result = optimize_item_response(item, include_metadata=False)

        assert result["id"] == "12345678"
        assert result["title"] == "Test Item"


class TestLinkOptimization:
    """Test link response optimization."""

    def test_optimize_link_dict(self) -> None:
        """Test optimizing link from dict."""
        link = {
            "id": "abcdefgh-1234-1234-1234-123456789012",
            "source_id": "12345678-1234-1234-1234-123456789012",
            "target_id": "87654321-4321-4321-4321-210987654321",
            "link_type": "implements",
        }

        result = optimize_link_response(link)

        assert result["id"] == "abcdefgh"
        assert result["source"] == "12345678"
        assert result["target"] == "87654321"
        assert result["type"] == "implements"

    def test_optimize_link_model(self) -> None:
        """Test optimizing link from model object."""

        class MockLink:
            id = "abcdefgh-1234-1234-1234-123456789012"
            source_id = "12345678-1234-1234-1234-123456789012"
            target_id = "87654321-4321-4321-4321-210987654321"
            link_type = "implements"

        link = MockLink()
        result = optimize_link_response(link)

        assert result["id"] == "abcdefgh"
        assert result["source"] == "12345678"
        assert result["type"] == "implements"


class TestPagination:
    """Test pagination helper."""

    def test_paginate_basic(self) -> None:
        """Test basic pagination."""
        items = [{"id": str(i)} for i in range(100)]

        result = paginate_response(items, page=1, page_size=20)

        assert len(result["items"]) == 20
        assert result["page"] == 1
        assert result["total"] == 100
        assert result["has_more"] is True

    def test_paginate_last_page(self) -> None:
        """Test pagination on last page."""
        items = [{"id": str(i)} for i in range(100)]

        result = paginate_response(items, page=5, page_size=20)

        assert len(result["items"]) == 20
        assert result["page"] == COUNT_FIVE
        assert result["total"] == 100
        assert result["has_more"] is False

    def test_paginate_with_optimizer(self) -> None:
        """Test pagination with optimizer function."""
        items = [
            {
                "id": "12345678-1234-1234-1234-123456789012",
                "title": f"Item {i}",
            }
            for i in range(10)
        ]

        def optimizer(item: Any) -> None:
            return {"id": item["id"][:8], "title": item["title"]}

        result = paginate_response(items, page=1, page_size=5, optimizer_func=optimizer)

        assert len(result["items"]) == COUNT_FIVE
        assert result["items"][0]["id"] == "12345678"  # Optimized ID


class TestTokenReduction:
    """Test actual token reduction metrics."""

    def test_single_item_reduction(self) -> None:
        """Test token reduction for single item."""
        full_item = {
            "id": "12345678-1234-1234-1234-123456789012",
            "external_id": "FEA-123",
            "project_id": "87654321-4321-4321-4321-210987654321",
            "title": "Test Feature",
            "description": "Long description...",
            "view": "FEATURE",
            "item_type": "epic",
            "status": "active",
            "priority": "high",
            "owner": "user@example.com",
            "item_metadata": {"key": "value"},
            "version": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }

        # Original format (v1)
        v1_response = {
            "ok": True,
            "action": "get",
            "data": full_item,
            "actor": {
                "client_id": "test",
                "project_id": "87654321-4321-4321-4321-210987654321",
            },
        }

        # Optimized format (v2)
        v2_response = optimize_item_response(full_item, include_metadata=False)

        v1_size = len(json.dumps(v1_response))
        v2_size = len(json.dumps(v2_response))

        reduction = ((v1_size - v2_size) / v1_size) * 100

        # Should achieve >50% reduction
        assert reduction > 50

    def test_list_reduction(self) -> None:
        """Test token reduction for list of items."""
        items = [
            {
                "id": f"1234567{i}-1234-1234-1234-123456789012",
                "external_id": f"FEA-{i}",
                "project_id": "87654321-4321-4321-4321-210987654321",
                "title": f"Feature {i} - Implement user authentication",
                "description": "A detailed description of the feature implementation",
                "view": "FEATURE",
                "item_type": "epic",
                "status": "active",
                "priority": "high",
                "owner": "user@example.com",
                "item_metadata": {"sprint": "Sprint 1", "points": 8},
                "version": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            }
            for i in range(50)
        ]

        # Original format (v1)
        v1_response = {
            "ok": True,
            "action": "query",
            "data": {"items": items, "count": 50, "limit": 50},
            "actor": {
                "client_id": "test",
                "sub": "user-123",
                "email": "test@example.com",
                "project_id": "87654321-4321-4321-4321-210987654321",
            },
        }

        # Optimized format (v2)
        v2_response = {
            "items": [optimize_item_response(item) for item in items],
            "count": 50,
            "total": 50,
            "has_more": False,
        }

        v1_size = len(json.dumps(v1_response))
        v2_size = len(json.dumps(v2_response))

        reduction = ((v1_size - v2_size) / v1_size) * 100

        # Should achieve >50% reduction
        assert reduction > 50
