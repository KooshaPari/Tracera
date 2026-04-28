"""CLI Integration Test Script.

Tests all CLI hooks with sample data.

Usage:
    python scripts/test_cli_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Any

from hooks import (
    auggie_pre_discovery,
    claude_cli_pre_discovery,
    cursor_agent_pre_discovery,
    droid_pre_discovery,
)
from router import TOOL_REGISTRY, ArchRouter, ToolRegistry


class MockSearchService:
    """Mock search service for testing."""

    async def semantic_search(self, *_args: Any, **_kwargs: Any) -> None:
        """Semantic search."""
        return []


async def test_cursor_agent() -> None:
    """Test Cursor Agent hook."""
    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    await cursor_agent_pre_discovery(
        action="generate",
        prompt="create FastAPI endpoint for user management",
        router=router,
        registry=registry,
        search_service=search_service,
        file_path="main.py",
        language="python",
    )


async def test_claude_cli() -> None:
    """Test Claude CLI hook."""
    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    await claude_cli_pre_discovery(
        command="generate",
        args=["code", "for", "REST", "API"],
        router=router,
        registry=registry,
        search_service=search_service,
        model="claude-3-sonnet",
    )


async def test_auggie() -> None:
    """Test Auggie hook."""
    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    await auggie_pre_discovery(
        operation="transform",
        input_file="data.csv",
        router=router,
        registry=registry,
        search_service=search_service,
        output_format="parquet",
    )


async def test_droid() -> None:
    """Test Droid hook."""
    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    await droid_pre_discovery(
        test_type="unit",
        target="tests/unit/",
        router=router,
        registry=registry,
        search_service=search_service,
        framework="pytest",
        coverage=True,
    )


async def main() -> bool | None:
    """Run all tests."""
    try:
        await test_cursor_agent()
        await test_claude_cli()
        await test_auggie()
        await test_droid()

        return True

    except Exception:
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
