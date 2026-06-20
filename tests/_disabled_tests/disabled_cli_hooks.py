from typing import Any

"""CLI hooks integration tests."""

import pytest
from hooks import (
    AuggieContext,
    AuggieHook,
    ClaudeCliContext,
    ClaudeCliHook,
    CursorAgentContext,
    CursorAgentHook,
    DroidContext,
    DroidHook,
)
from router import TOOL_REGISTRY, ArchRouter, ToolRegistry


@pytest.mark.asyncio
class TestCliHooks:
    """Test CLI hooks."""

    @pytest.fixture
    def router(self) -> None:
        return ArchRouter()

    @pytest.fixture
    def registry(self) -> None:
        return ToolRegistry(TOOL_REGISTRY)

    @pytest.fixture
    def search_service(self) -> None:
        class MockSearchService:
            async def semantic_search(self, *args: Any, **kwargs: Any) -> None:
                return []

        return MockSearchService()

    async def test_cursor_agent_hook_initialization(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Cursor Agent hook initialization."""
        hook = CursorAgentHook(router, registry, search_service)
        assert hook is not None
        assert hook.router is not None
        assert hook.registry is not None

    async def test_cursor_agent_pre_discovery(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Cursor Agent pre-discovery."""
        hook = CursorAgentHook(router, registry, search_service)
        context = CursorAgentContext(
            action="generate",
            prompt="create endpoint",
            file_path="main.py",
        )

        result = await hook.pre_discovery(context)
        assert "route" in result
        assert "tools" in result

    async def test_cursor_agent_post_selection(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Cursor Agent post-selection."""
        hook = CursorAgentHook(router, registry, search_service)
        context = CursorAgentContext(
            action="generate",
            prompt="create endpoint",
        )

        result = await hook.post_selection(context, "api_development", ["fastapi"])
        assert result["route"] == "api_development"
        assert result["status"] == "ready"

    async def test_claude_cli_hook_initialization(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Claude CLI hook initialization."""
        hook = ClaudeCliHook(router, registry, search_service)
        assert hook is not None

    async def test_claude_cli_pre_discovery(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Claude CLI pre-discovery."""
        hook = ClaudeCliHook(router, registry, search_service)
        context = ClaudeCliContext(
            command="generate",
            args=["code"],
            model="claude-3-sonnet",
        )

        result = await hook.pre_discovery(context)
        assert "route" in result
        assert "tools" in result

    async def test_auggie_hook_initialization(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Auggie hook initialization."""
        hook = AuggieHook(router, registry, search_service)
        assert hook is not None

    async def test_auggie_pre_discovery(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Auggie pre-discovery."""
        hook = AuggieHook(router, registry, search_service)
        context = AuggieContext(
            operation="transform",
            input_file="data.csv",
            output_format="parquet",
        )

        result = await hook.pre_discovery(context)
        assert "route" in result
        assert "tools" in result

    async def test_droid_hook_initialization(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Droid hook initialization."""
        hook = DroidHook(router, registry, search_service)
        assert hook is not None

    async def test_droid_pre_discovery(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Droid pre-discovery."""
        hook = DroidHook(router, registry, search_service)
        context = DroidContext(
            test_type="unit",
            target="tests/",
            framework="pytest",
        )

        result = await hook.pre_discovery(context)
        assert "route" in result
        assert "tools" in result

    async def test_hook_completion(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test hook completion."""
        hook = CursorAgentHook(router, registry, search_service)
        context = CursorAgentContext(
            action="generate",
            prompt="create endpoint",
        )

        result = await hook.on_completion(
            context,
            "api_development",
            "def hello(): return 'world'",
            True,
        )

        assert result["success"] is True
        assert result["route"] == "api_development"
