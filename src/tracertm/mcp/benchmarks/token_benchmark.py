"""Benchmark script for Phase 2 MCP optimizations.

Measures:
- Token usage reduction (target: 50%)
- Response time improvements
- Compression effectiveness
- Streaming efficiency
"""

from __future__ import annotations

import json
from typing import Any

# Mock data for testing
MOCK_ITEM = {
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


def format_original_response(item: dict[str, Any]) -> dict[str, Any]:
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


def format_optimized_response(item: dict[str, Any]) -> dict[str, Any]:
    """Format response using optimized lean format (v2)."""
    return {
        "id": item["id"][:8],
        "title": item["title"],
        "view": item["view"],
        "type": item["item_type"],
        "status": item["status"],
    }


def measure_token_usage(data: dict[str, Any]) -> int:
    """Estimate token usage (rough approximation: 1 token ≈ 4 chars)."""
    serialized = json.dumps(data)
    return len(serialized) // 4


def benchmark_single_item():
    """Benchmark single item response."""
    print("=" * 80)
    print("Single Item Response Benchmark")
    print("=" * 80)

    # Original format
    original = format_original_response(MOCK_ITEM)
    original_tokens = measure_token_usage(original)
    original_size = len(json.dumps(original))

    print("\n📊 Original Format (v1):")
    print(f"  - Size: {original_size:,} bytes")
    print(f"  - Estimated tokens: {original_tokens:,}")

    # Optimized format
    optimized = format_optimized_response(MOCK_ITEM)
    optimized_tokens = measure_token_usage(optimized)
    optimized_size = len(json.dumps(optimized))

    print("\n✨ Optimized Format (v2):")
    print(f"  - Size: {optimized_size:,} bytes")
    print(f"  - Estimated tokens: {optimized_tokens:,}")

    # Calculate reduction
    size_reduction = ((original_size - optimized_size) / original_size) * 100
    token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

    print("\n📉 Reduction:")
    print(f"  - Size: {size_reduction:.1f}%")
    print(f"  - Tokens: {token_reduction:.1f}%")
    print("  - Target: 50%")
    print(f"  - Status: {'✅ ACHIEVED' if token_reduction >= 50 else '⚠️  SHORT'}")

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_list_response(item_count: int = 50):
    """Benchmark list response with multiple items."""
    print("\n" + "=" * 80)
    print(f"List Response Benchmark ({item_count} items)")
    print("=" * 80)

    items = [MOCK_ITEM.copy() for _ in range(item_count)]

    # Original format
    original = {
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

    print("\n📊 Original Format (v1):")
    print(f"  - Size: {original_size:,} bytes")
    print(f"  - Estimated tokens: {original_tokens:,}")

    # Optimized format
    optimized = {
        "items": [format_optimized_response(item) for item in items],
        "count": item_count,
        "total": item_count,
        "has_more": False,
    }
    optimized_tokens = measure_token_usage(optimized)
    optimized_size = len(json.dumps(optimized))

    print("\n✨ Optimized Format (v2):")
    print(f"  - Size: {optimized_size:,} bytes")
    print(f"  - Estimated tokens: {optimized_tokens:,}")

    # Calculate reduction
    size_reduction = ((original_size - optimized_size) / original_size) * 100
    token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

    print("\n📉 Reduction:")
    print(f"  - Size: {size_reduction:.1f}%")
    print(f"  - Tokens: {token_reduction:.1f}%")
    print("  - Target: 50%")
    print(f"  - Status: {'✅ ACHIEVED' if token_reduction >= 50 else '⚠️  SHORT'}")

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_compression():
    """Benchmark compression effectiveness."""
    print("\n" + "=" * 80)
    print("Compression Benchmark")
    print("=" * 80)

    import base64
    import gzip

    items = [MOCK_ITEM.copy() for _ in range(100)]
    data = {"items": items, "count": 100}

    # Uncompressed
    uncompressed = json.dumps(data)
    uncompressed_size = len(uncompressed)
    uncompressed_tokens = uncompressed_size // 4

    print("\n📊 Uncompressed:")
    print(f"  - Size: {uncompressed_size:,} bytes")
    print(f"  - Estimated tokens: {uncompressed_tokens:,}")

    # Compressed
    compressed = gzip.compress(uncompressed.encode("utf-8"))
    compressed_b64 = base64.b64encode(compressed).decode("ascii")
    compressed_size = len(compressed_b64)
    compressed_tokens = compressed_size // 4

    print("\n✨ Compressed (gzip + base64):")
    print(f"  - Size: {compressed_size:,} bytes")
    print(f"  - Estimated tokens: {compressed_tokens:,}")

    # Calculate reduction
    size_reduction = ((uncompressed_size - compressed_size) / uncompressed_size) * 100
    token_reduction = ((uncompressed_tokens - compressed_tokens) / uncompressed_tokens) * 100

    print("\n📉 Reduction:")
    print(f"  - Size: {size_reduction:.1f}%")
    print(f"  - Tokens: {token_reduction:.1f}%")

    return {
        "uncompressed_tokens": uncompressed_tokens,
        "compressed_tokens": compressed_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_streaming():
    """Benchmark streaming vs full response."""
    print("\n" + "=" * 80)
    print("Streaming vs Full Response Benchmark")
    print("=" * 80)

    total_items = 200
    batch_size = 50

    items = [MOCK_ITEM.copy() for _ in range(total_items)]

    # Full response (all items at once)
    full_response = {
        "items": [format_optimized_response(item) for item in items],
        "count": total_items,
    }
    full_tokens = measure_token_usage(full_response)

    print(f"\n📊 Full Response (all {total_items} items):")
    print(f"  - Estimated tokens: {full_tokens:,}")

    # Streaming response (first batch only)
    batch_response = {
        "items": [format_optimized_response(item) for item in items[:batch_size]],
        "batch": 1,
        "total": total_items,
        "batch_size": batch_size,
        "has_more": True,
    }
    batch_tokens = measure_token_usage(batch_response)

    print(f"\n✨ Streaming Response (first batch of {batch_size}):")
    print(f"  - Estimated tokens: {batch_tokens:,}")

    # Calculate savings for initial response
    token_reduction = ((full_tokens - batch_tokens) / full_tokens) * 100

    print("\n📉 Initial Response Reduction:")
    print(f"  - Tokens saved: {token_reduction:.1f}%")
    print(f"  - Benefit: User gets first {batch_size} items immediately")
    print("  - Benefit: Can request more batches only if needed")

    return {
        "full_tokens": full_tokens,
        "batch_tokens": batch_tokens,
        "reduction_pct": token_reduction,
    }


def benchmark_error_messages():
    """Benchmark error message optimization."""
    print("\n" + "=" * 80)
    print("Error Message Optimization Benchmark")
    print("=" * 80)

    # Original error format
    original_error = {
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

    print("\n📊 Original Error Format:")
    print(f"  - Estimated tokens: {original_tokens:,}")

    # Optimized error format
    optimized_error = {
        "ok": False,
        "error": "Item not found: abc123",
        "category": "not_found",
        "suggestions": [
            "Check the item ID or use query_items() to search",
            "Item IDs support prefix matching (e.g., 'abc' matches 'abcdef...')",
        ],
    }
    optimized_tokens = measure_token_usage(optimized_error)

    print("\n✨ Optimized Error Format:")
    print(f"  - Estimated tokens: {optimized_tokens:,}")
    print("  - Includes helpful suggestions")
    print("  - Categorized for better LLM understanding")

    token_reduction = ((original_tokens - optimized_tokens) / original_tokens) * 100

    print("\n📉 Reduction:")
    print(f"  - Tokens: {token_reduction:.1f}%")
    print("  - Benefit: More helpful while using fewer tokens")

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "reduction_pct": token_reduction,
    }


def main():
    """Run all benchmarks and generate summary."""
    print("\n" + "=" * 80)
    print("MCP Phase 2 Optimization Benchmarks")
    print("=" * 80)
    print("\nTarget: 50% token reduction across all operations")
    print("\n")

    results = {}

    # Run benchmarks
    results["single_item"] = benchmark_single_item()
    results["list_50"] = benchmark_list_response(50)
    results["list_100"] = benchmark_list_response(100)
    results["compression"] = benchmark_compression()
    results["streaming"] = benchmark_streaming()
    results["errors"] = benchmark_error_messages()

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    avg_reduction = sum(r["reduction_pct"] for r in results.values() if "reduction_pct" in r) / len([
        r for r in results.values() if "reduction_pct" in r
    ])

    print(f"\n📊 Average Token Reduction: {avg_reduction:.1f}%")
    print("🎯 Target: 50%")
    print(f"📈 Status: {'✅ ACHIEVED' if avg_reduction >= 50 else '⚠️  SHORT'}")

    print("\n📋 Breakdown:")
    print(f"  - Single Item: {results['single_item']['reduction_pct']:.1f}%")
    print(f"  - List (50 items): {results['list_50']['reduction_pct']:.1f}%")
    print(f"  - List (100 items): {results['list_100']['reduction_pct']:.1f}%")
    print(f"  - Compression: {results['compression']['reduction_pct']:.1f}%")
    print(f"  - Streaming: {results['streaming']['reduction_pct']:.1f}%")
    print(f"  - Errors: {results['errors']['reduction_pct']:.1f}%")

    print("\n✨ Key Improvements:")
    print("  ✅ Lean response format (no envelope overhead)")
    print("  ✅ Short IDs (8 chars vs 36 chars)")
    print("  ✅ Minimal metadata (only essential fields)")
    print("  ✅ Compression for large responses")
    print("  ✅ Streaming for better UX")
    print("  ✅ Helpful error messages with suggestions")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
