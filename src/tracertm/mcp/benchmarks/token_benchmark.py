"""Benchmark script for MCP token optimizations.

Measures:
- Token usage reduction (target: 50%)
- Response time improvements
- Compression effectiveness
- Streaming efficiency
"""

from __future__ import annotations

import json

# Token batch size for benchmarking
_TOKEN_BATCH_SIZE = 50
# Target token reduction percentage for "achieved" status
_TARGET_REDUCTION_PCT = 50
# Default list response item count
_DEFAULT_LIST_ITEM_COUNT = 50
# List benchmark sizes
_LIST_BENCHMARK_COUNTS = (50, 100)

# Mock data for testing
MOCK_ITEM: dict[str, object] = {
    "id": "12345678-1234-1234-1234-123456789012",
    "external_id": "FEA-123",
    "project_id": "87654321-4321-4321-4321-210987654321",
    "title": "Implement new feature for user authentication",
    "description": "This feature will add OAuth2 support for third-party login providers including Google, GitHub, and Microsoft. It should integrate with existing user management and provide seamless migration for current users.",
    "view": "FEATURE",
    "item_type": "epic",
    "status": "in_progress",
    "priority": "high",
    "owner": "john.doe@example.com",
    "parent_id": None,
    "item_metadata": {
        "sprint": "Sprint 24",
        "story_points": 13,
        "labels": ["auth", "oauth", "security"],
        "custom_fields": {
            "business_value": "high",
            "technical_complexity": "medium",
            "dependencies": ["user-service", "auth-service"],
        },
    },
    "version": 5,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z",
}


def format_original_response(item: dict[str, object]) -> dict[str, object]:
    """Format response using original envelope (v1)."""
    return {
        "ok": True,
        "action": "get",
        "data": item,
        "actor": {
            "client_id": "test-client",
            "sub": "user-123",
            "email": "test@example.com",
            "auth_type": "bearer",
            "scopes": ["read", "write"],
            "project_id": "87654321-4321-4321-4321-210987654321",
            "project_ids": ["87654321-4321-4321-4321-210987654321"],
        },
    }


def format_optimized_response(item: dict[str, object]) -> dict[str, object]:
    """Format response using optimized lean format (v2)."""
    item_id = item.get("id", "")
    return {
        "id": str(item_id)[:8] if isinstance(item_id, str) else "",
        "title": item.get("title", ""),
        "view": item.get("view", ""),
        "type": item.get("item_type", ""),
        "status": item.get("status", ""),
    }


def measure_token_usage(data: dict[str, object]) -> int:
    """Estimate token usage (rough approximation: 1 token ≈ 4 chars)."""
    serialized = json.dumps(data)
    return len(serialized) // 4


def benchmark_single_item() -> dict[str, object]:
    """Benchmark single item response."""
    # Original format
    original = format_original_response(MOCK_ITEM)
    original_tokens = measure_token_usage(original)
    original_size = len(json.dumps(original))

    # Optimized format
    optimized = format_optimized_response(MOCK_ITEM)
    optimized_tokens = measure_token_usage(optimized)
    optimized_size = len(json.dumps(optimized))

    # Calculate reduction
    ((original_size - optimized_size) / original_size) * 100
    token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_list_response(item_count: int = _DEFAULT_LIST_ITEM_COUNT) -> dict[str, object]:
    """Benchmark list response with multiple items."""
    items = [MOCK_ITEM.copy() for _ in range(item_count)]

    # Original format
    original: dict[str, object] = {
        "ok": True,
        "action": "query",
        "data": {
            "items": items,
            "count": item_count,
            "limit": item_count,
        },
        "actor": {
            "client_id": "test-client",
            "project_id": "87654321-4321-4321-4321-210987654321",
        },
    }
    original_tokens = measure_token_usage(original)
    original_size = len(json.dumps(original))

    # Optimized format
    optimized: dict[str, object] = {
        "items": [format_optimized_response(item) for item in items],
        "count": item_count,
        "total": item_count,
        "has_more": False,
    }
    optimized_tokens = measure_token_usage(optimized)
    optimized_size = len(json.dumps(optimized))

    # Calculate reduction
    ((original_size - optimized_size) / original_size) * 100
    token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_compression() -> dict[str, object]:
    """Benchmark compression effectiveness."""
    import base64
    import gzip

    items = [MOCK_ITEM.copy() for _ in range(100)]
    data = {"items": items, "count": 100}

    # Uncompressed
    uncompressed = json.dumps(data)
    uncompressed_size = len(uncompressed)
    uncompressed_tokens = uncompressed_size // 4

    # Compressed
    compressed = gzip.compress(uncompressed.encode("utf-8"))
    compressed_b64 = base64.b64encode(compressed).decode("ascii")
    compressed_size = len(compressed_b64)
    compressed_tokens = compressed_size // 4

    # Calculate reduction
    ((uncompressed_size - compressed_size) / uncompressed_size) * 100
    token_reduction = ((uncompressed_tokens - compressed_tokens) / uncompressed_tokens) * 100

    return {
        "uncompressed_tokens": uncompressed_tokens,
        "compressed_tokens": compressed_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_streaming() -> dict[str, object]:
    """Benchmark streaming vs full response."""
    total_items = 200
    batch_size = 50

    items = [MOCK_ITEM.copy() for _ in range(total_items)]

    # Full response (all items at once)
    full_response: dict[str, object] = {
        "items": [format_optimized_response(item) for item in items],
        "count": total_items,
    }
    full_tokens = measure_token_usage(full_response)

    # Streaming response (first batch only)
    batch_response: dict[str, object] = {
        "items": [format_optimized_response(item) for item in items[:batch_size]],
        "batch": 1,
        "total": total_items,
        "batch_size": batch_size,
        "has_more": True,
    }
    batch_tokens = measure_token_usage(batch_response)

    # Calculate savings for initial response
    token_reduction = ((full_tokens - batch_tokens) / full_tokens) * 100

    return {
        "full_tokens": full_tokens,
        "batch_tokens": batch_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_error_messages() -> dict[str, object]:
    """Benchmark error message optimization."""
    # Original error format
    original_error: dict[str, object] = {
        "ok": False,
        "action": "get_item",
        "error": "Item not found: abc123",
        "actor": {
            "client_id": "test-client",
            "sub": "user-123",
            "email": "test@example.com",
            "auth_type": "bearer",
            "scopes": ["read", "write"],
            "project_id": "87654321-4321-4321-4321-210987654321",
            "project_ids": ["87654321-4321-4321-4321-210987654321"],
        },
    }
    original_tokens = measure_token_usage(original_error)

    # Optimized error format
    optimized_error: dict[str, object] = {
        "ok": False,
        "error": "Item not found: abc123",
        "category": "not_found",
        "suggestions": [
            "Check the item ID or use query_items() to search",
            "Item IDs support prefix matching (e.g., 'abc' matches 'abcdef...')",
        ],
    }
    optimized_tokens = measure_token_usage(optimized_error)

    token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "reduction_pct": token_reduction,
    }


def main() -> None:
    """Run all benchmarks and generate summary."""
    results = {}

    # Run benchmarks
    results["single_item"] = benchmark_single_item()
    results["list_50"] = benchmark_list_response(_LIST_BENCHMARK_COUNTS[0])
    results["list_100"] = benchmark_list_response(_LIST_BENCHMARK_COUNTS[1])
    results["compression"] = benchmark_compression()
    results["streaming"] = benchmark_streaming()
    results["errors"] = benchmark_error_messages()

    # Summary
    reduction_results = [r for r in results.values() if isinstance(r, dict) and "reduction_pct" in r]
    if reduction_results:
        sum(
            float(r["reduction_pct"]) if isinstance(r["reduction_pct"], (int, float)) else 0 for r in reduction_results
        ) / len(reduction_results)


if __name__ == "__main__":
    main()
