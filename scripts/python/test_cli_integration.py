"""
CLI Integration Test Script

Tests all CLI hooks with sample data.

Usage:
    python scripts/test_cli_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hooks import (
    auggie_pre_discovery,
    claude_cli_pre_discovery,
    cursor_agent_pre_discovery,
    droid_pre_discovery,
)
from router import TOOL_REGISTRY, ArchRouter, ToolRegistry


class MockSearchService:
    """Mock search service for testing"""

    async def semantic_search(self, *args, **kwargs):
        return []


async def test_cursor_agent():
    """Test Cursor Agent hook"""
    print("\n" + "=" * 60)
    print("Testing Cursor Agent Hook")
    print("=" * 60)

    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    result = await cursor_agent_pre_discovery(
        action="generate",
        prompt="create FastAPI endpoint for user management",
        router=router,
        registry=registry,
        search_service=search_service,
        file_path="main.py",
        language="python",
    )

    print(f"✓ Route: {result['route']}")
    print(f"✓ Tools: {result['tools']}")
    print(f"✓ CLI Command: {result['cli_command']}")
    print(f"✓ Confidence: {result['confidence']}")


async def test_claude_cli():
    """Test Claude CLI hook"""
    print("\n" + "=" * 60)
    print("Testing Claude CLI Hook")
    print("=" * 60)

    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    result = await claude_cli_pre_discovery(
        command="generate",
        args=["code", "for", "REST", "API"],
        router=router,
        registry=registry,
        search_service=search_service,
        model="claude-3-sonnet",
    )

    print(f"✓ Route: {result['route']}")
    print(f"✓ Tools: {result['tools']}")
    print(f"✓ CLI Command: {result['cli_command']}")
    print(f"✓ Model: {result['model']}")


async def test_auggie():
    """Test Auggie hook"""
    print("\n" + "=" * 60)
    print("Testing Auggie Hook")
    print("=" * 60)

    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    result = await auggie_pre_discovery(
        operation="transform",
        input_file="data.csv",
        router=router,
        registry=registry,
        search_service=search_service,
        output_format="parquet",
    )

    print(f"✓ Route: {result['route']}")
    print(f"✓ Tools: {result['tools']}")
    print(f"✓ CLI Command: {result['cli_command']}")
    print(f"✓ Output Format: {result['output_format']}")


async def test_droid():
    """Test Droid hook"""
    print("\n" + "=" * 60)
    print("Testing Droid Hook")
    print("=" * 60)

    router = ArchRouter()
    registry = ToolRegistry(TOOL_REGISTRY)
    search_service = MockSearchService()

    result = await droid_pre_discovery(
        test_type="unit",
        target="tests/unit/",
        router=router,
        registry=registry,
        search_service=search_service,
        framework="pytest",
        coverage=True,
    )

    print(f"✓ Route: {result['route']}")
    print(f"✓ Tools: {result['tools']}")
    print(f"✓ CLI Command: {result['cli_command']}")
    print(f"✓ Framework: {result['framework']}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CLI Integration Tests")
    print("=" * 60)

    try:
        await test_cursor_agent()
        await test_claude_cli()
        await test_auggie()
        await test_droid()

        print("\n" + "=" * 60)
        print("✓ All CLI integration tests passed!")
        print("=" * 60 + "\n")
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
