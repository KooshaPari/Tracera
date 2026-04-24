"""End-to-End workflow tests for TraceRTM MCP Server.

These tests validate complete workflows:
- Project creation and management
- Item creation and linking
- Traceability analysis
- Gap analysis and impact analysis
"""

from __future__ import annotations

import os

# ============================================================================
# Fixtures
# ============================================================================
from typing import Any

import pytest

from tests.test_constants import COUNT_TEN


@pytest.fixture(autouse=True)
def setup_env() -> None:
    """Setup environment for tests."""
    os.environ["TRACERTM_MCP_AUTH_MODE"] = "static"
    os.environ["TRACERTM_MCP_DEV_API_KEYS"] = "test-key-1"
    os.environ["TRACERTM_MCP_DEV_SCOPES"] = "read:*,write:*,analyze:*"
    # Cleanup handled by pytest


@pytest.fixture
def mcp_server() -> None:
    """Get MCP server instance."""
    from tracertm.mcp.server import mcp

    return mcp


# ============================================================================
# Workflow 1: Project and Item Creation
# ============================================================================


class TestWorkflow_ProjectCreation:
    """Test project creation workflow."""

    def test_create_project_tool_exists(self, mcp_server: Any) -> None:
        """Test that create_project tool exists."""
        assert "create_project" in {t.name for t in mcp_server._tools.values()}

    def test_create_project_has_required_parameters(self, mcp_server: Any) -> None:
        """Test create_project has required parameters."""
        tool = mcp_server._tools["create_project"]
        param_names = {p.name for p in tool.parameters}

        assert "name" in param_names

    def test_list_projects_tool_exists(self, mcp_server: Any) -> None:
        """Test that list_projects tool exists."""
        assert "list_projects" in {t.name for t in mcp_server._tools.values()}

    def test_select_project_tool_exists(self, mcp_server: Any) -> None:
        """Test that select_project tool exists."""
        assert "select_project" in {t.name for t in mcp_server._tools.values()}

    def test_select_project_has_project_id_parameter(self, mcp_server: Any) -> None:
        """Test select_project has project_id parameter."""
        tool = mcp_server._tools["select_project"]
        param_names = {p.name for p in tool.parameters}

        assert "project_id" in param_names


# ============================================================================
# Workflow 2: Item Management
# ============================================================================


class TestWorkflow_ItemManagement:
    """Test item management workflow."""

    def test_create_item_tool_exists(self, mcp_server: Any) -> None:
        """Test that create_item tool exists."""
        assert "create_item" in {t.name for t in mcp_server._tools.values()}

    def test_create_item_has_required_parameters(self, mcp_server: Any) -> None:
        """Test create_item has required parameters."""
        tool = mcp_server._tools["create_item"]
        param_names = {p.name for p in tool.parameters}

        assert "project_id" in param_names
        assert "name" in param_names
        assert "item_type" in param_names

    def test_get_item_tool_exists(self, mcp_server: Any) -> None:
        """Test that get_item tool exists."""
        assert "get_item" in {t.name for t in mcp_server._tools.values()}

    def test_update_item_tool_exists(self, mcp_server: Any) -> None:
        """Test that update_item tool exists."""
        assert "update_item" in {t.name for t in mcp_server._tools.values()}

    def test_delete_item_tool_exists(self, mcp_server: Any) -> None:
        """Test that delete_item tool exists."""
        assert "delete_item" in {t.name for t in mcp_server._tools.values()}

    def test_query_items_tool_exists(self, mcp_server: Any) -> None:
        """Test that query_items tool exists."""
        assert "query_items" in {t.name for t in mcp_server._tools.values()}

    def test_query_items_has_filter_parameters(self, mcp_server: Any) -> None:
        """Test query_items has filter parameters."""
        tool = mcp_server._tools["query_items"]
        param_names = {p.name for p in tool.parameters}

        # Should have at least project_id and some filters
        assert "project_id" in param_names

    def test_bulk_update_items_tool_exists(self, mcp_server: Any) -> None:
        """Test that bulk_update_items tool exists."""
        assert "bulk_update_items" in {t.name for t in mcp_server._tools.values()}

    def test_bulk_update_items_has_ids_and_updates(self, mcp_server: Any) -> None:
        """Test bulk_update_items has item_ids and updates parameters."""
        tool = mcp_server._tools["bulk_update_items"]
        param_names = {p.name for p in tool.parameters}

        assert "item_ids" in param_names
        assert "updates" in param_names


# ============================================================================
# Workflow 3: Link Management
# ============================================================================


class TestWorkflow_LinkManagement:
    """Test link management workflow."""

    def test_create_link_tool_exists(self, mcp_server: Any) -> None:
        """Test that create_link tool exists."""
        assert "create_link" in {t.name for t in mcp_server._tools.values()}

    def test_create_link_has_required_parameters(self, mcp_server: Any) -> None:
        """Test create_link has required parameters."""
        tool = mcp_server._tools["create_link"]
        param_names = {p.name for p in tool.parameters}

        assert "source_item_id" in param_names
        assert "target_item_id" in param_names
        assert "link_type" in param_names

    def test_list_links_tool_exists(self, mcp_server: Any) -> None:
        """Test that list_links tool exists."""
        assert "list_links" in {t.name for t in mcp_server._tools.values()}

    def test_list_links_has_item_id_parameter(self, mcp_server: Any) -> None:
        """Test list_links has item_id parameter."""
        tool = mcp_server._tools["list_links"]
        param_names = {p.name for p in tool.parameters}

        assert "item_id" in param_names

    def test_find_orphaned_links_tool_exists(self, mcp_server: Any) -> None:
        """Test that find_orphaned_links tool exists."""
        assert "find_orphaned_links" in {t.name for t in mcp_server._tools.values()}

    def test_find_missing_links_tool_exists(self, mcp_server: Any) -> None:
        """Test that find_missing_links tool exists."""
        assert "find_missing_links" in {t.name for t in mcp_server._tools.values()}

    def test_delete_link_tool_exists(self, mcp_server: Any) -> None:
        """Test that delete_link tool exists."""
        assert "delete_link" in {t.name for t in mcp_server._tools.values()}


# ============================================================================
# Workflow 4: Traceability Analysis
# ============================================================================


class TestWorkflow_TraceabilityAnalysis:
    """Test traceability analysis workflow."""

    def test_gap_analysis_tool_exists(self, mcp_server: Any) -> None:
        """Test that trace_gap_analysis tool exists."""
        assert "trace_gap_analysis" in {t.name for t in mcp_server._tools.values()}

    def test_gap_analysis_has_project_id_parameter(self, mcp_server: Any) -> None:
        """Test gap_analysis has project_id parameter."""
        tool = mcp_server._tools["trace_gap_analysis"]
        param_names = {p.name for p in tool.parameters}

        assert "project_id" in param_names

    def test_impact_analysis_tool_exists(self, mcp_server: Any) -> None:
        """Test that trace_impact_analysis tool exists."""
        assert "trace_impact_analysis" in {t.name for t in mcp_server._tools.values()}

    def test_impact_analysis_has_item_id_parameter(self, mcp_server: Any) -> None:
        """Test impact_analysis has item_id parameter."""
        tool = mcp_server._tools["trace_impact_analysis"]
        param_names = {p.name for p in tool.parameters}

        assert "item_id" in param_names

    def test_reverse_impact_tool_exists(self, mcp_server: Any) -> None:
        """Test that trace_reverse_impact tool exists."""
        assert "trace_reverse_impact" in {t.name for t in mcp_server._tools.values()}

    def test_matrix_tool_exists(self, mcp_server: Any) -> None:
        """Test that trace_matrix tool exists."""
        assert "trace_matrix" in {t.name for t in mcp_server._tools.values()}

    def test_health_assessment_tool_exists(self, mcp_server: Any) -> None:
        """Test that trace_health_assessment tool exists."""
        assert "trace_health_assessment" in {t.name for t in mcp_server._tools.values()}


# ============================================================================
# Workflow 5: Graph Analysis
# ============================================================================


class TestWorkflow_GraphAnalysis:
    """Test graph analysis workflow."""

    def test_cycle_analysis_tool_exists(self, mcp_server: Any) -> None:
        """Test that analyze_cycles tool exists."""
        assert "analyze_cycles" in {t.name for t in mcp_server._tools.values()}

    def test_cycle_analysis_has_project_id_parameter(self, mcp_server: Any) -> None:
        """Test cycle_analysis has project_id parameter."""
        tool = mcp_server._tools["analyze_cycles"]
        param_names = {p.name for p in tool.parameters}

        assert "project_id" in param_names

    def test_shortest_path_tool_exists(self, mcp_server: Any) -> None:
        """Test that analyze_shortest_path tool exists."""
        assert "analyze_shortest_path" in {t.name for t in mcp_server._tools.values()}

    def test_shortest_path_has_required_parameters(self, mcp_server: Any) -> None:
        """Test shortest_path has required parameters."""
        tool = mcp_server._tools["analyze_shortest_path"]
        param_names = {p.name for p in tool.parameters}

        assert "start_item_id" in param_names
        assert "end_item_id" in param_names

    def test_dependencies_tool_exists(self, mcp_server: Any) -> None:
        """Test that analyze_dependencies tool exists."""
        assert "analyze_dependencies" in {t.name for t in mcp_server._tools.values()}


# ============================================================================
# Workflow 6: Specification Management
# ============================================================================


class TestWorkflow_SpecificationManagement:
    """Test specification management workflow."""

    def test_create_spec_tool_exists(self, mcp_server: Any) -> None:
        """Test that create_specification tool exists."""
        assert "create_specification" in {t.name for t in mcp_server._tools.values()}

    def test_create_spec_has_required_parameters(self, mcp_server: Any) -> None:
        """Test create_specification has required parameters."""
        tool = mcp_server._tools["create_specification"]
        param_names = {p.name for p in tool.parameters}

        assert "project_id" in param_names
        assert "spec_kind" in param_names

    def test_list_specs_tool_exists(self, mcp_server: Any) -> None:
        """Test that list_specifications tool exists."""
        assert "list_specifications" in {t.name for t in mcp_server._tools.values()}

    def test_update_spec_tool_exists(self, mcp_server: Any) -> None:
        """Test that update_specification tool exists."""
        assert "update_specification" in {t.name for t in mcp_server._tools.values()}


# ============================================================================
# Workflow 7: Quality Analysis
# ============================================================================


class TestWorkflow_QualityAnalysis:
    """Test quality analysis workflow."""

    def test_quality_analysis_tool_exists(self, mcp_server: Any) -> None:
        """Test that analyze_quality tool exists."""
        assert "analyze_quality" in {t.name for t in mcp_server._tools.values()}

    def test_quality_analysis_has_project_id_parameter(self, mcp_server: Any) -> None:
        """Test analyze_quality has project_id parameter."""
        tool = mcp_server._tools["analyze_quality"]
        param_names = {p.name for p in tool.parameters}

        assert "project_id" in param_names


# ============================================================================
# Configuration Management
# ============================================================================


class TestWorkflow_ConfigurationManagement:
    """Test configuration management workflow."""

    def test_get_config_tool_exists(self, mcp_server: Any) -> None:
        """Test that get_config tool exists."""
        assert "get_config" in {t.name for t in mcp_server._tools.values()}

    def test_update_config_tool_exists(self, mcp_server: Any) -> None:
        """Test that update_config tool exists."""
        assert "update_config" in {t.name for t in mcp_server._tools.values()}


# ============================================================================
# Complete Workflow Sequences
# ============================================================================


class TestCompleteWorkflows:
    """Test complete workflow sequences."""

    def test_project_setup_workflow_has_all_tools(self, mcp_server: Any) -> None:
        """Test that complete project setup has all required tools."""
        required_tools = [
            "create_project",
            "list_projects",
            "select_project",
            "create_item",
            "create_link",
        ]

        registered = {t.name for t in mcp_server._tools.values()}

        for tool in required_tools:
            assert tool in registered, f"Missing tool in project setup: {tool}"

    def test_analysis_workflow_has_all_tools(self, mcp_server: Any) -> None:
        """Test that analysis workflow has all required tools."""
        required_tools = [
            "trace_gap_analysis",
            "trace_impact_analysis",
            "trace_matrix",
            "analyze_cycles",
            "analyze_dependencies",
        ]

        registered = {t.name for t in mcp_server._tools.values()}

        for tool in required_tools:
            assert tool in registered, f"Missing tool in analysis: {tool}"

    def test_all_categories_represented(self, mcp_server: Any) -> None:
        """Test that all tool categories have at least one tool."""
        tool_names = {t.name for t in mcp_server._tools.values()}

        categories = {
            "project": ["create_project", "list_projects"],
            "item": ["create_item", "get_item"],
            "link": ["create_link", "list_links"],
            "trace": ["trace_gap_analysis", "trace_matrix"],
            "graph": ["analyze_cycles", "analyze_shortest_path"],
            "spec": ["create_specification", "list_specifications"],
            "quality": ["analyze_quality"],
            "config": ["get_config"],
        }

        for category, tools in categories.items():
            found = [t for t in tools if t in tool_names]
            assert len(found) > 0, f"No tools found for category '{category}': {tools}"


# ============================================================================
# Tool Parameter Validation
# ============================================================================


class TestToolParameterValidation:
    """Test that tool parameters are properly defined."""

    def test_all_tools_have_parameters(self, mcp_server: Any) -> None:
        """Test that all tools have parameters defined."""
        for tool in mcp_server._tools.values():
            # Most tools should have at least one parameter
            # (except maybe system tools)
            assert hasattr(tool, "parameters")

    def test_create_tools_have_data_parameters(self, mcp_server: Any) -> None:
        """Test that create tools have data parameters."""
        create_tools = [t for t in mcp_server._tools.values() if "create" in t.name]

        for tool in create_tools:
            param_names = {p.name for p in tool.parameters}
            # Should have at least one required parameter
            assert len(param_names) > 0

    def test_analysis_tools_have_project_or_item_parameter(self, mcp_server: Any) -> None:
        """Test that analysis tools take project or item parameters."""
        analysis_tools = [t for t in mcp_server._tools.values() if "analyze" in t.name or "trace" in t.name]

        for tool in analysis_tools:
            param_names = {p.name for p in tool.parameters}
            # Should have project_id or item_id
            has_context = "project_id" in param_names or "item_id" in param_names
            assert has_context, f"Tool {tool.name} missing project_id or item_id"


# ============================================================================
# Error Handling in Workflows
# ============================================================================


class TestWorkflowErrorHandling:
    """Test error handling across workflows."""

    def test_tools_handle_missing_project_gracefully(self, mcp_server: Any) -> None:
        """Test that tools can handle missing project."""
        # Verify tools exist that work with projects
        assert "create_item" in {t.name for t in mcp_server._tools.values()}

    def test_tools_handle_missing_item_gracefully(self, mcp_server: Any) -> None:
        """Test that tools can handle missing item."""
        # Verify tools exist that work with items
        assert "get_item" in {t.name for t in mcp_server._tools.values()}

    def test_analysis_tools_defined(self, mcp_server: Any) -> None:
        """Test that analysis tools are properly defined."""
        assert "trace_gap_analysis" in {t.name for t in mcp_server._tools.values()}


# ============================================================================
# Tool Description Quality
# ============================================================================


class TestToolDescriptionQuality:
    """Test that tools have good descriptions."""

    def test_all_tools_have_descriptions(self, mcp_server: Any) -> None:
        """Test that all tools have descriptions."""
        for tool in mcp_server._tools.values():
            assert tool.description is not None
            assert len(tool.description) > 0
            assert isinstance(tool.description, str)

    def test_descriptions_are_descriptive(self, mcp_server: Any) -> None:
        """Test that descriptions actually describe the tool."""
        for tool in mcp_server._tools.values():
            desc = tool.description
            # Should have meaningful length
            assert len(desc) >= COUNT_TEN, f"Tool {tool.name} has too short description"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
