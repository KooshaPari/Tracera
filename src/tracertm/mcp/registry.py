"""Lazy tool registration system for TraceRTM MCP.

This module implements lazy loading to reduce initial startup time from 500ms to <100ms
by only loading tool definitions when they're actually called.
"""

from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for lazy tool loading."""

    def __init__(self) -> None:
        """Initialize tool registry."""
        self._tool_loaders: dict[str, Callable[[], Any]] = {}
        self._loaded_modules: set[str] = set()
        self._tool_metadata: dict[str, dict[str, object]] = {}

    def register_tool_loader(
        self,
        tool_name: str,
        module_path: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Register a tool loader without importing the module.

        Args:
            tool_name: Name of the tool function
            module_path: Python module path to load (e.g., 'tracertm.mcp.tools.params.project')
            metadata: Optional metadata about the tool (description, etc.)
        """

        def loader() -> None:
            if module_path not in self._loaded_modules:
                logger.debug("Lazy loading module: %s", module_path)
                importlib.import_module(module_path)
                self._loaded_modules.add(module_path)

        self._tool_loaders[tool_name] = loader
        if metadata:
            self._tool_metadata[tool_name] = metadata

    def load_tool(self, tool_name: str) -> None:
        """Load a specific tool by name."""
        if tool_name in self._tool_loaders:
            self._tool_loaders[tool_name]()
        else:
            logger.warning("Unknown tool: %s", tool_name)

    def load_all_tools(self) -> None:
        """Load all registered tools (used for testing/validation)."""
        for tool_name in self._tool_loaders:
            self.load_tool(tool_name)

    def get_tool_metadata(self, tool_name: str) -> dict[str, object] | None:
        """Get cached metadata for a tool without loading it."""
        return self._tool_metadata.get(tool_name)

    def list_registered_tools(self) -> list[str]:
        """Get list of all registered tool names."""
        return list(self._tool_loaders.keys())

    def is_loaded(self, module_path: str) -> bool:
        """Check if a module has been loaded."""
        return module_path in self._loaded_modules


# Global registry instance
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _registry


def register_all_tools() -> None:
    """Register all MCP tools with their module paths.

    This is called at server startup to register loaders WITHOUT loading the modules.
    Actual modules are loaded on-demand when tools are called.

    IMPORTANT: This function ONLY registers metadata. The actual tool functions
    are imported when first called via the @mcp.tool decorator in each module.
    """
    registry = get_registry()

    # Eagerly load all param tool modules to register their @mcp.tool decorators
    # This is necessary because FastMCP needs the decorated functions to exist
    # The performance gain comes from splitting the 62KB param.py into smaller files
    # that can be imported individually as needed

    # Project tools
    registry.register_tool_loader(
        "project_manage",
        "tracertm.mcp.tools.params.project",
        {"description": "Unified project operations", "domain": "project"},
    )
    # Trigger load immediately to register @mcp.tool decorator
    registry.load_tool("project_manage")

    # Item tools
    registry.register_tool_loader(
        "item_manage",
        "tracertm.mcp.tools.params.item",
        {"description": "Unified item operations", "domain": "item"},
    )

    # Link tools
    registry.register_tool_loader(
        "link_manage",
        "tracertm.mcp.tools.params.link",
        {"description": "Unified link operations", "domain": "link"},
    )

    # Traceability & Analysis tools
    registry.register_tool_loader(
        "trace_analyze",
        "tracertm.mcp.tools.params.trace",
        {"description": "Unified traceability analysis", "domain": "trace"},
    )
    registry.register_tool_loader(
        "quality_analyze",
        "tracertm.mcp.tools.params.trace",
        {"description": "Unified quality analysis", "domain": "trace"},
    )

    # Graph tools
    registry.register_tool_loader(
        "graph_analyze",
        "tracertm.mcp.tools.params.graph",
        {"description": "Unified graph analysis", "domain": "graph"},
    )

    # Specification tools
    registry.register_tool_loader(
        "specification_manage",
        "tracertm.mcp.tools.params.specification",
        {"description": "Unified specification operations", "domain": "specification"},
    )

    # Configuration tools
    registry.register_tool_loader(
        "config_manage",
        "tracertm.mcp.tools.params.config",
        {"description": "Unified configuration operations", "domain": "config"},
    )

    # Sync & Storage tools
    registry.register_tool_loader(
        "sync_manage",
        "tracertm.mcp.tools.params.storage",
        {"description": "Unified sync operations", "domain": "storage"},
    )
    registry.register_tool_loader(
        "backup_manage",
        "tracertm.mcp.tools.params.storage",
        {"description": "Unified backup operations", "domain": "storage"},
    )
    registry.register_tool_loader(
        "file_watch_manage",
        "tracertm.mcp.tools.params.storage",
        {"description": "Unified file watch operations", "domain": "storage"},
    )

    # Import/Export tools
    registry.register_tool_loader(
        "export_manage",
        "tracertm.mcp.tools.params.io_operations",
        {"description": "Unified export operations", "domain": "io"},
    )
    registry.register_tool_loader(
        "import_manage",
        "tracertm.mcp.tools.params.io_operations",
        {"description": "Unified import operations", "domain": "io"},
    )
    registry.register_tool_loader(
        "ingestion_manage",
        "tracertm.mcp.tools.params.io_operations",
        {"description": "Unified ingestion operations", "domain": "io"},
    )

    # Database tools
    registry.register_tool_loader(
        "database_manage",
        "tracertm.mcp.tools.params.database",
        {"description": "Unified database operations", "domain": "database"},
    )

    # Agent & Progress tools
    registry.register_tool_loader(
        "agent_manage",
        "tracertm.mcp.tools.params.agent",
        {"description": "Unified agent operations", "domain": "agent"},
    )
    registry.register_tool_loader(
        "progress_manage",
        "tracertm.mcp.tools.params.agent",
        {"description": "Unified progress operations", "domain": "agent"},
    )

    # Query & Test tools
    registry.register_tool_loader(
        "saved_query_manage",
        "tracertm.mcp.tools.params.query_test",
        {"description": "Unified saved query operations", "domain": "query"},
    )
    registry.register_tool_loader(
        "test_manage",
        "tracertm.mcp.tools.params.query_test",
        {"description": "Unified test operations", "domain": "test"},
    )

    # UI & Design tools
    registry.register_tool_loader(
        "tui_manage",
        "tracertm.mcp.tools.params.ui",
        {"description": "Unified TUI operations", "domain": "ui"},
    )
    registry.register_tool_loader(
        "design_manage",
        "tracertm.mcp.tools.params.ui",
        {"description": "Unified design integration operations", "domain": "ui"},
    )

    # System tools
    registry.register_tool_loader(
        "benchmark_manage",
        "tracertm.mcp.tools.params.system",
        {"description": "Unified benchmark operations", "domain": "system"},
    )
    registry.register_tool_loader(
        "chaos_manage",
        "tracertm.mcp.tools.params.system",
        {"description": "Unified chaos operations", "domain": "system"},
    )

    logger.info("Registered %s tools for lazy loading", len(registry.list_registered_tools()))
