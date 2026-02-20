from typing import Any

"""End-to-end integration tests."""

import pytest
from hooks import (
    auggie_pre_discovery,
    claude_cli_pre_discovery,
    cursor_agent_pre_discovery,
    droid_pre_discovery,
)
from router import TOOL_REGISTRY, ArchRouter, ToolRegistry


@pytest.mark.asyncio
class TestEndToEnd:
    """End-to-end integration tests."""

    @pytest.fixture
    def router(self) -> None:
        """Create router."""
        return ArchRouter()

    @pytest.fixture
    def registry(self) -> None:
        """Create registry."""
        return ToolRegistry(TOOL_REGISTRY)

    @pytest.fixture
    def search_service(self) -> None:
        """Create mock search service."""

        class MockSearchService:
            async def semantic_search(self, *args: Any, **kwargs: Any) -> None:
                return []

        return MockSearchService()

    async def test_cursor_agent_flow(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Cursor Agent discovery flow."""
        result = await cursor_agent_pre_discovery(
            action="generate",
            prompt="create FastAPI endpoint",
            router=router,
            registry=registry,
            search_service=search_service,
            file_path="main.py",
            language="python",
        )

        assert "route" in result
        assert "tools" in result
        assert "cli_command" in result
        assert result["action"] == "generate"

    async def test_claude_cli_flow(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Claude CLI discovery flow."""
        result = await claude_cli_pre_discovery(
            command="generate",
            args=["code", "for", "api"],
            router=router,
            registry=registry,
            search_service=search_service,
            model="claude-3-sonnet",
        )

        assert "route" in result
        assert "tools" in result
        assert "cli_command" in result
        assert result["command"] == "generate"

    async def test_auggie_flow(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Auggie discovery flow."""
        result = await auggie_pre_discovery(
            operation="transform",
            input_file="data.csv",
            router=router,
            registry=registry,
            search_service=search_service,
            output_format="parquet",
        )

        assert "route" in result
        assert "tools" in result
        assert "cli_command" in result
        assert result["operation"] == "transform"

    async def test_droid_flow(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test Droid discovery flow."""
        result = await droid_pre_discovery(
            test_type="unit",
            target="tests/",
            router=router,
            registry=registry,
            search_service=search_service,
            framework="pytest",
            coverage=True,
        )

        assert "route" in result
        assert "tools" in result
        assert "cli_command" in result
        assert result["test_type"] == "unit"

    async def test_routing_consistency(self, router: Any, registry: Any, search_service: Any) -> None:
        """Test routing consistency across hooks."""
        # Test multiple queries
        queries = [
            ("generate", "create API endpoint"),
            ("test", "write unit tests"),
            ("process", "transform CSV data"),
        ]

        for action, prompt in queries:
            result = await cursor_agent_pre_discovery(
                action=action,
                prompt=prompt,
                router=router,
                registry=registry,
                search_service=search_service,
            )

            assert "route" in result
            assert result["route"] in registry.list_routes()
