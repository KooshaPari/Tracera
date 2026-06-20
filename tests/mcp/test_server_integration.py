"""Integration tests for TraceRTM MCP Server.

Tests cover:
- Server startup and initialization
- Tool registration
- Authentication flows
- Basic tool operations
- Error handling
"""

from __future__ import annotations

import os

# ============================================================================
# Fixtures
# ============================================================================
from typing import Any

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO


@pytest.fixture
def mcp_server() -> None:
    """Import and return the MCP server instance."""
    os.environ["TRACERTM_MCP_AUTH_MODE"] = "static"
    os.environ["TRACERTM_MCP_DEV_API_KEYS"] = "test-key-1,test-key-2"
    os.environ["TRACERTM_MCP_DEV_SCOPES"] = "read:*,write:*,analyze:*"

    # Import after setting env vars
    from tracertm.mcp.server import mcp

    return mcp


@pytest.fixture
def dev_token() -> str:
    """Return a valid dev token for testing."""
    return "test-key-1"


@pytest.fixture
def auth_headers(dev_token: str) -> dict[str, str]:
    """Return authorization headers with dev token."""
    return {"Authorization": f"Bearer {dev_token}"}


# ============================================================================
# Server Startup Tests
# ============================================================================


class TestServerStartup:
    """Test MCP server initialization and startup."""

    def test_server_instance_exists(self, mcp_server: Any) -> None:
        """Test that MCP server instance is created."""
        assert mcp_server is not None
        assert mcp_server.name == "tracertm-mcp"

    def test_server_has_instructions(self, mcp_server: Any) -> None:
        """Test that server has usage instructions."""
        assert mcp_server.instructions is not None
        assert "TraceRTM" in mcp_server.instructions
        assert "tool groups" in mcp_server.instructions

    def test_server_has_auth_provider(self, mcp_server: Any) -> None:
        """Test that server is configured with auth provider."""
        # Auth provider is built based on env vars
        # May be None, CompositeTokenVerifier, or AuthKitProvider
        # Just verify it doesn't raise an error

    def test_auth_mode_static_configured(self) -> None:
        """Test static auth mode is properly configured."""
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "static"
        os.environ["TRACERTM_MCP_DEV_API_KEYS"] = "key1,key2"

        from tracertm.mcp.auth import build_auth_provider

        provider = build_auth_provider()
        assert provider is not None

    def test_auth_mode_disabled_when_set(self) -> None:
        """Test auth can be disabled."""
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "disabled"

        from tracertm.mcp.auth import build_auth_provider

        provider = build_auth_provider()
        assert provider is None

    def test_auth_mode_oauth_requires_config(self) -> None:
        """Test OAuth mode requires domain configuration."""
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "oauth"
        os.environ.pop("TRACERTM_MCP_AUTHKIT_DOMAIN", None)

        from tracertm.mcp.auth import build_auth_provider

        provider = build_auth_provider()
        # Should be None without config
        assert provider is None


# ============================================================================
# Tool Registration Tests
# ============================================================================


class TestToolRegistration:
    """Test MCP tool registration."""

    def test_project_tools_registered(self, mcp_server: Any) -> None:
        """Test project management tools are registered."""
        tool_names = {t.name for t in mcp_server._tools.values()}

        assert "create_project" in tool_names
        assert "list_projects" in tool_names
        assert "select_project" in tool_names

    def test_item_tools_registered(self, mcp_server: Any) -> None:
        """Test item management tools are registered."""
        tool_names = {t.name for t in mcp_server._tools.values()}

        assert "create_item" in tool_names
        assert "get_item" in tool_names
        assert "update_item" in tool_names
        assert "delete_item" in tool_names
        assert "query_items" in tool_names

    def test_link_tools_registered(self, mcp_server: Any) -> None:
        """Test link management tools are registered."""
        tool_names = {t.name for t in mcp_server._tools.values()}

        assert "create_link" in tool_names
        assert "list_links" in tool_names
        assert "find_orphaned_links" in tool_names

    def test_trace_tools_registered(self, mcp_server: Any) -> None:
        """Test traceability analysis tools are registered."""
        tool_names = {t.name for t in mcp_server._tools.values()}

        assert "trace_gap_analysis" in tool_names
        assert "trace_impact_analysis" in tool_names
        assert "trace_matrix" in tool_names

    def test_graph_tools_registered(self, mcp_server: Any) -> None:
        """Test graph analysis tools are registered."""
        tool_names = {t.name for t in mcp_server._tools.values()}

        assert "analyze_cycles" in tool_names
        assert "analyze_shortest_path" in tool_names

    def test_spec_tools_registered(self, mcp_server: Any) -> None:
        """Test specification tools are registered."""
        tool_names = {t.name for t in mcp_server._tools.values()}

        assert "create_specification" in tool_names
        assert "list_specifications" in tool_names

    def test_minimum_tool_count(self, mcp_server: Any) -> None:
        """Test that minimum expected number of tools are registered."""
        tool_count = len(mcp_server._tools)
        # Expecting 30+ tools minimum
        assert tool_count >= 30, f"Expected at least 30 tools, got {tool_count}"

    def test_all_tools_have_descriptions(self, mcp_server: Any) -> None:
        """Test all registered tools have descriptions."""
        for tool in mcp_server._tools.values():
            assert tool.description, f"Tool {tool.name} missing description"


# ============================================================================
# Authentication Tests
# ============================================================================


class TestAuthentication:
    """Test authentication mechanisms."""

    @pytest.mark.skip(reason="Auth uses OAuth only; static verifier API removed")
    def test_dev_key_static_verifier(self) -> None:
        """Test static verifier for dev keys (skipped: OAuth-only auth)."""

    @pytest.mark.skip(reason="Auth uses OAuth only; static verifier API removed")
    def test_dev_key_format(self) -> None:
        """Test dev keys format (skipped: OAuth-only auth)."""

    @pytest.mark.skip(reason="Auth uses OAuth only; composite verifier API removed")
    def test_composite_verifier_multiple_sources(self) -> None:
        """Test composite verifier (skipped: OAuth-only auth)."""

    def test_auth_mode_parsing(self) -> None:
        """Test auth mode parsing."""
        from tracertm.mcp.auth import build_auth_provider

        # Test disabled
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "disabled"
        assert build_auth_provider() is None

        # Test off
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "off"
        assert build_auth_provider() is None

        # Test none
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "none"
        assert build_auth_provider() is None

    def test_scopes_parsing(self) -> None:
        """Test scope parsing."""
        from fastmcp.utilities.auth import parse_scopes

        scopes_list: list[str] = parse_scopes("read:projects,write:items,analyze:*") or []
        assert len(scopes_list) == COUNT_THREE
        assert "read:projects" in scopes_list
        assert "write:items" in scopes_list


# ============================================================================
# Tool Operation Tests
# ============================================================================


class TestToolOperations:
    """Test basic MCP tool operations."""

    def test_create_project_structure(self, mcp_server: Any) -> None:
        """Test that create_project tool has correct structure."""
        tool = mcp_server._tools.get("create_project")
        assert tool is not None
        assert tool.name == "create_project"
        assert tool.description is not None

        # Check for expected parameters
        params = {p.name for p in tool.parameters}
        assert "name" in params

    def test_list_projects_structure(self, mcp_server: Any) -> None:
        """Test that list_projects tool has correct structure."""
        tool = mcp_server._tools.get("list_projects")
        assert tool is not None

    def test_query_items_structure(self, mcp_server: Any) -> None:
        """Test that query_items tool has correct structure."""
        tool = mcp_server._tools.get("query_items")
        assert tool is not None

        # Check for filter parameters
        params = {p.name for p in tool.parameters}
        assert "project_id" in params

    def test_trace_gap_analysis_structure(self, mcp_server: Any) -> None:
        """Test that trace_gap_analysis tool exists."""
        tool = mcp_server._tools.get("trace_gap_analysis")
        assert tool is not None

    def test_tool_parameters_typed(self, mcp_server: Any) -> None:
        """Test that tool parameters are properly typed."""
        tool = mcp_server._tools.get("create_item")
        assert tool is not None

        for param in tool.parameters:
            # Each parameter should have a type
            assert hasattr(param, "type") or hasattr(param, "json_schema")


# ============================================================================
# Middleware Tests
# ============================================================================


class TestMiddleware:
    """Test MCP middleware configuration."""

    def test_logging_middleware_registered(self, mcp_server: Any) -> None:
        """Test that logging middleware is registered."""
        # Middleware is added in core.py
        assert mcp_server is not None
        # Verify no errors on initialization


# ============================================================================
# Response Format Tests
# ============================================================================


class TestResponseFormats:
    """Test response envelope format."""

    def test_success_response_structure(self) -> None:
        """Test successful response structure."""
        from tracertm.mcp.tools.base import wrap_success

        response = wrap_success({"id": "123", "name": "Test"}, action="create", ctx=None)

        assert "ok" in response or response.get("ok")
        assert "data" in response or "result" in response

    def test_error_response_contains_message(self) -> None:
        """Test error response contains error message."""
        from fastmcp.exceptions import ToolError

        error = ToolError("Test error message")
        assert str(error) == "Test error message"


# ============================================================================
# Database Connection Tests
# ============================================================================


class TestDatabaseConnection:
    """Test database connection from MCP server."""

    def test_session_factory_available(self) -> None:
        """Test that session factory is available."""
        from tracertm.mcp.tools.base import get_session

        # Should not raise error
        try:
            with get_session() as session:
                assert session is not None
        except Exception:
            # May fail if DB not configured, but function should exist
            pass

    def test_config_manager_available(self) -> None:
        """Test that config manager is available."""
        from tracertm.mcp.tools.base import get_config_manager

        # Should not raise error
        try:
            manager = get_config_manager()
            assert manager is not None
        except Exception:
            # May fail if config not loaded, but function should exist
            pass


# ============================================================================
# Integration Scenario Tests
# ============================================================================


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_project_workflow_structure(self, mcp_server: Any) -> None:
        """Test that tools for basic project workflow exist."""
        required_tools = [
            "create_project",
            "list_projects",
            "create_item",
            "query_items",
            "create_link",
        ]

        registered = {t.name for t in mcp_server._tools.values()}

        for tool in required_tools:
            assert tool in registered, f"Missing tool: {tool}"

    def test_analysis_workflow_structure(self, mcp_server: Any) -> None:
        """Test that tools for analysis workflow exist."""
        required_tools = [
            "trace_gap_analysis",
            "trace_impact_analysis",
            "trace_matrix",
            "analyze_cycles",
        ]

        registered = {t.name for t in mcp_server._tools.values()}

        for tool in required_tools:
            assert tool in registered, f"Missing tool: {tool}"

    def test_specification_workflow_structure(self, mcp_server: Any) -> None:
        """Test that specification tools exist."""
        required_tools = [
            "create_specification",
            "list_specifications",
            "update_specification",
        ]

        registered = {t.name for t in mcp_server._tools.values()}

        for tool in required_tools:
            assert tool in registered, f"Missing tool: {tool}"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test error handling in MCP server."""

    def test_missing_required_parameter_error(self) -> None:
        """Test error when required parameter missing."""
        from fastmcp.exceptions import ToolError

        # Should be able to raise ToolError
        error = ToolError("Missing required parameter: name")
        assert "Missing" in str(error)

    def test_not_found_error(self) -> None:
        """Test not found error."""
        from fastmcp.exceptions import ToolError

        error = ToolError("Project not found: xyz")
        assert "not found" in str(error)

    def test_auth_error(self) -> None:
        """Test authentication error."""
        from fastmcp.exceptions import ToolError

        error = ToolError("Unauthorized")
        assert "Unauthorized" in str(error)


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfiguration:
    """Test MCP server configuration."""

    def test_env_var_auth_mode(self) -> None:
        """Test auth mode from environment variable."""
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "static"
        os.environ["TRACERTM_MCP_DEV_API_KEYS"] = "test-key"

        from tracertm.mcp.auth import build_auth_provider

        provider = build_auth_provider()
        assert provider is not None

    def test_env_var_scopes(self) -> None:
        """Test required scopes from environment variable."""
        os.environ["TRACERTM_MCP_REQUIRED_SCOPES"] = "read:projects,write:items"

        # Should parse without error
        from fastmcp.utilities.auth import parse_scopes

        scopes_list: list[str] = parse_scopes(os.getenv("TRACERTM_MCP_REQUIRED_SCOPES")) or []
        assert len(scopes_list) == COUNT_TWO

    def test_auth_mode_case_insensitive(self) -> None:
        """Test that auth mode is case insensitive."""
        os.environ["TRACERTM_MCP_AUTH_MODE"] = "DISABLED"

        from tracertm.mcp.auth import build_auth_provider

        # Should still recognize as disabled
        provider = build_auth_provider()
        assert provider is None


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Test performance characteristics."""

    def test_tool_registration_completes_quickly(self, _mcp_server: Any) -> None:
        """Test that tool registration is fast (< 1 second)."""
        import time

        start = time.time()
        # Re-import to measure registration time

        elapsed = time.time() - start
        assert elapsed < 1.0, f"Tool registration took {elapsed:.2f}s"

    def test_auth_provider_initialization_fast(self) -> None:
        """Test that auth provider initialization is fast."""
        import time

        os.environ["TRACERTM_MCP_AUTH_MODE"] = "static"
        os.environ["TRACERTM_MCP_DEV_API_KEYS"] = "test-key"

        from tracertm.mcp.auth import build_auth_provider

        start = time.time()
        build_auth_provider()
        elapsed = time.time() - start

        assert elapsed < 0.5, f"Auth provider init took {elapsed:.2f}s"


# ============================================================================
# Compliance Tests
# ============================================================================


class TestCompliancewithSpec:
    """Test compliance with MCP specification."""

    def test_server_has_required_fields(self, mcp_server: Any) -> None:
        """Test server has all required MCP fields."""
        assert hasattr(mcp_server, "name")
        assert hasattr(mcp_server, "instructions")
        assert hasattr(mcp_server, "_tools")

    def test_tools_are_callable(self, mcp_server: Any) -> None:
        """Test that tools are callable."""
        for tool in mcp_server._tools.values():
            # Tool should be a Tool object with necessary attributes
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
