"""Response optimization utilities for MCP tools.

Provides:
- Lean response formatting (minimal metadata)
- Response compression for large payloads
- Optimized error messages for LLM context
- Token-efficient data serialization
"""

from __future__ import annotations

import gzip
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class ResponseFormat:
    """Response format mode for controlling metadata inclusion."""

    LEAN = "lean"  # Minimal metadata, just data
    STANDARD = "standard"  # Include basic metadata
    VERBOSE = "verbose"  # Include all metadata (backward compat)


def format_response(
    data: object,
    format_mode: str = ResponseFormat.LEAN,
    compress: bool = False,
    compress_threshold: int = 1024,
    ctx: object | None = None,
) -> dict[str, object] | str:
    """Format a response with optional compression and metadata.

    Args:
        data: Response data
        format_mode: Response format mode (lean/standard/verbose)
        compress: Enable compression for large responses
        compress_threshold: Size threshold in bytes for compression (default 1KB)
        ctx: MCP context for extracting metadata

    Returns:
        Formatted response (dict or compressed string)
    """
    response: dict[str, object] | object
    if format_mode == ResponseFormat.LEAN:
        # Return just the data, no envelope
        response = data
    elif format_mode == ResponseFormat.STANDARD:
        # Minimal metadata
        response = {"data": data, "ok": True}
    else:
        # Full metadata (backward compatible)
        response = {
            "ok": True,
            "data": data,
            "actor": _extract_actor(ctx) if ctx else None,
        }

    # Compression for large responses
    if compress and isinstance(response, dict):
        serialized = json.dumps(response)
        if len(serialized) > compress_threshold:
            compressed = gzip.compress(serialized.encode("utf-8"))
            # Return compressed as base64 with metadata
            import base64

            return {
                "compressed": True,
                "encoding": "gzip+base64",
                "data": base64.b64encode(compressed).decode("ascii"),
                "original_size": len(serialized),
                "compressed_size": len(compressed),
            }

    # Type narrow for return
    if isinstance(response, (dict, str)):
        return response
    # Fallback - shouldn't happen but satisfies mypy
    return {"data": response}


def format_error(
    error: str | Exception,
    action: str | None = None,
    suggestions: list[str] | None = None,
    category: str = "error",
    format_mode: str = ResponseFormat.LEAN,
    ctx: object | None = None,
) -> dict[str, object]:
    """Format an error response optimized for LLM understanding.

    Args:
        error: Error message or exception
        action: Action that failed (optional)
        suggestions: List of suggestions to fix the error
        category: Error category (error/validation/auth/not_found)
        format_mode: Response format mode
        ctx: MCP context

    Returns:
        Formatted error response
    """
    error_msg = str(error)

    # Categorize common errors
    if category == "error" and error_msg:
        if "not found" in error_msg.lower():
            category = "not_found"
        elif "required" in error_msg.lower() or "invalid" in error_msg.lower():
            category = "validation"
        elif "access denied" in error_msg.lower() or "unauthorized" in error_msg.lower():
            category = "auth"

    # Auto-generate suggestions for common errors
    if not suggestions:
        suggestions = _generate_suggestions(error_msg, category)

    if format_mode == ResponseFormat.LEAN:
        response = {
            "ok": False,
            "error": error_msg,
            "category": category,
        }
        if suggestions:
            response["suggestions"] = suggestions
    elif format_mode == ResponseFormat.STANDARD:
        response = {
            "ok": False,
            "error": error_msg,
            "category": category,
        }
        if action:
            response["action"] = action
        if suggestions:
            response["suggestions"] = suggestions
    else:
        # Verbose mode
        response = {
            "ok": False,
            "error": error_msg,
            "category": category,
            "action": action,
            "suggestions": suggestions or [],
            "actor": _extract_actor(ctx) if ctx else None,
        }

    return response


def _extract_actor(ctx: object) -> dict[str, object] | None:
    """Extract minimal actor information from context.

    Only includes essential fields for debugging.
    """
    if ctx is None:
        return None

    try:
        from fastmcp.server.dependencies import get_access_token
    except ImportError:
        return None

    token = get_access_token()
    if token is None:
        return None

    claims = getattr(token, "claims", {}) or {}
    return {
        "client_id": getattr(token, "client_id", None),
        "project_id": claims.get("project_id"),
    }


def _generate_suggestions(error_msg: str, category: str) -> list[str]:
    """Generate helpful suggestions based on error message and category."""
    suggestions: list[str] = []

    if category == "not_found":
        if "project" in error_msg.lower():
            suggestions.extend((
                "Use select_project() to select a project first",
                "Use list_projects() to see available projects",
            ))
        elif "item" in error_msg.lower():
            suggestions.extend((
                "Check the item ID or use query_items() to search",
                "Item IDs support prefix matching (e.g., 'abc' matches 'abcdef...')",
            ))

    elif category == "validation":
        if "required" in error_msg.lower():
            suggestions.append("Check the required parameters for this operation")
        if "project_id" in error_msg.lower():
            suggestions.append("Use select_project() to set the current project")

    elif category == "auth":
        suggestions.extend(("Check your access token and permissions", "Verify project access for the current user"))

    return suggestions


def optimize_item_response(item: object, include_metadata: bool = False) -> dict[str, object]:
    """Optimize item response for minimal token usage.

    Args:
        item: SQLAlchemy Item model or dict
        include_metadata: Include item_metadata field

    Returns:
        Optimized item dict with only essential fields
    """
    # Handle both model objects and dicts
    if hasattr(item, "__dict__"):
        data = {
            "id": str(item.id)[:8],  # type: ignore[attr-defined]  # Short ID prefix
            "title": item.title,  # type: ignore[attr-defined]
            "view": item.view,  # type: ignore[attr-defined]
            "type": item.item_type,  # type: ignore[attr-defined]
            "status": item.status,  # type: ignore[attr-defined]
        }
        if include_metadata and item.item_metadata:  # type: ignore[attr-defined]
            data["metadata"] = item.item_metadata  # type: ignore[attr-defined]
    else:
        data = {
            "id": str(item.get("id", ""))[:8],  # type: ignore[attr-defined]
            "title": item.get("title"),  # type: ignore[attr-defined]
            "view": item.get("view"),  # type: ignore[attr-defined]
            "type": item.get("item_type"),  # type: ignore[attr-defined]
            "status": item.get("status"),  # type: ignore[attr-defined]
        }
        if include_metadata and item.get("item_metadata"):  # type: ignore[attr-defined]
            data["metadata"] = item["item_metadata"]  # type: ignore[index]

    return data


def optimize_link_response(link: object) -> dict[str, object]:
    """Optimize link response for minimal token usage.

    Args:
        link: SQLAlchemy Link model or dict

    Returns:
        Optimized link dict
    """
    if hasattr(link, "__dict__"):
        return {
            "id": str(link.id)[:8],  # type: ignore[attr-defined]
            "source": str(link.source_id)[:8],  # type: ignore[attr-defined]
            "target": str(link.target_id)[:8],  # type: ignore[attr-defined]
            "type": link.link_type,  # type: ignore[attr-defined]
        }
    return {
        "id": str(link.get("id", ""))[:8],  # type: ignore[attr-defined]
        "source": str(link.get("source_id", ""))[:8],  # type: ignore[attr-defined]
        "target": str(link.get("target_id", ""))[:8],  # type: ignore[attr-defined]
        "type": link.get("link_type"),  # type: ignore[attr-defined]
    }


def paginate_response(
    items: list[object],
    page: int = 1,
    page_size: int = 50,
    optimizer_func: Callable[..., Any] | None = None,
) -> dict[str, object]:
    """Create a paginated response with lean metadata.

    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        page_size: Items per page
        optimizer_func: Optional function to optimize each item

    Returns:
        Paginated response with minimal metadata
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size

    page_items = items[start:end]
    if optimizer_func:
        page_items = [optimizer_func(item) for item in page_items]

    return {
        "items": page_items,
        "page": page,
        "total": total,
        "has_more": page < total_pages,
    }


__all__ = [
    "ResponseFormat",
    "format_error",
    "format_response",
    "optimize_item_response",
    "optimize_link_response",
    "paginate_response",
]
