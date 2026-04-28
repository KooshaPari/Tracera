"""Tool Registry Port.

Defines the protocol for MCP tool registration and discovery.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # Avoid runtime import cycle with pheno.mcp.__init__
    from collections.abc import Callable

    from pheno.mcp.types import McpTool


class ToolRegistry(Protocol):
    """Protocol for tool registration and discovery.

    Manages the registry of available MCP tools, allowing tools to be
    registered, discovered, and retrieved by name or category.

    Example:
        >>> registry = get_tool_registry()
        >>>
        >>> # Register tools
        >>> registry.register_tool(McpTool(
        ...     name="search",
        ...     description="Search documentation",
        ...     handler=search_handler
        ... ))
        >>>
        >>> # Discover tools
        >>> tools = registry.list_tools()
        >>> tool = registry.get_tool("search")
    """

    def register_tool(self, tool: McpTool, handler: Callable | None = None) -> None:
        """Register a tool in the registry.

        Args:
            tool: Tool definition
            handler: Optional handler function

        Example:
            >>> async def search_handler(query: str) -> str:
            ...     return f"Results for: {query}"
            >>>
            >>> registry.register_tool(
            ...     McpTool(name="search", description="Search docs"),
            ...     handler=search_handler
            ... )
        """
        ...

    def unregister_tool(self, name: str) -> None:
        """Unregister a tool from the registry.

        Args:
            name: Tool name

        Example:
            >>> registry.unregister_tool("search")
        """
        ...

    def get_tool(self, name: str) -> McpTool:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool definition

        Raises:
            ToolNotFoundError: If tool doesn't exist

        Example:
            >>> tool = registry.get_tool("search")
            >>> print(tool.description)
        """
        ...

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered.

        Args:
            name: Tool name

        Returns:
            True if tool exists

        Example:
            >>> if registry.has_tool("search"):
            ...     tool = registry.get_tool("search")
        """
        ...

    def list_tools(
        self, category: str | None = None, tags: list[str] | None = None,
    ) -> list[McpTool]:
        """List registered tools.

        Args:
            category: Optional category filter
            tags: Optional tag filters

        Returns:
            List of tools

        Example:
            >>> # All tools
            >>> all_tools = registry.list_tools()
            >>>
            >>> # Tools in category
            >>> search_tools = registry.list_tools(category="search")
            >>>
            >>> # Tools with tags
            >>> db_tools = registry.list_tools(tags=["database"])
        """
        ...

    def get_tool_handler(self, name: str) -> Callable:
        """Get the handler function for a tool.

        Args:
            name: Tool name

        Returns:
            Handler function

        Raises:
            ToolNotFoundError: If tool doesn't exist
            HandlerNotFoundError: If tool has no handler

        Example:
            >>> handler = registry.get_tool_handler("search")
            >>> result = await handler(query="hello")
        """
        ...

    def list_categories(self) -> list[str]:
        """List all tool categories.

        Returns:
            List of category names

        Example:
            >>> categories = registry.list_categories()
            >>> # ["search", "database", "storage", ...]
        """
        ...

    def get_tool_metadata(self, name: str) -> dict[str, Any]:
        """Get metadata for a tool.

        Args:
            name: Tool name

        Returns:
            Tool metadata dictionary

        Example:
            >>> metadata = registry.get_tool_metadata("search")
            >>> print(metadata["version"])
        """
        ...

    def search_tools(self, query: str) -> list[McpTool]:
        """Search for tools by name or description.

        Args:
            query: Search query

        Returns:
            Matching tools

        Example:
            >>> tools = registry.search_tools("database")
            >>> for tool in tools:
            ...     print(f"{tool.name}: {tool.description}")
        """
        ...


__all__ = ["ToolRegistry"]
