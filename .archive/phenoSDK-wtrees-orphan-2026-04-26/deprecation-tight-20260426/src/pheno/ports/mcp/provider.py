"""MCP Provider Port.

Defines the protocol for MCP server connection and tool execution. Adapters (mcp-sdk-
kit, mcp-infra-sdk) implement this protocol.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # Avoid runtime import cycle with pheno.mcp.__init__
    from pheno.mcp.types import McpServer, McpSession, McpTool, ToolResult


class McpProvider(Protocol):
    """Protocol for MCP implementation providers.

    Defines the contract for connecting to MCP servers and executing tools.
    Implementations handle the actual MCP protocol communication.

    Example:
        >>> provider = get_mcp_provider()  # Returns implementation
        >>> session = await provider.connect(server)
        >>> result = await provider.execute_tool(tool, {"param": "value"})
        >>> await provider.disconnect(session)
    """

    async def connect(self, server: McpServer) -> McpSession:
        """Connect to an MCP server.

        Args:
            server: MCP server configuration

        Returns:
            Active MCP session

        Raises:
            ConnectionError: If connection fails

        Example:
            >>> server = McpServer(url="http://localhost:8000")
            >>> session = await provider.connect(server)
        """
        ...

    async def disconnect(self, session: McpSession) -> None:
        """Disconnect from an MCP server.

        Args:
            session: Active MCP session to close

        Example:
            >>> await provider.disconnect(session)
        """
        ...

    async def execute_tool(
        self, tool: McpTool, params: dict[str, Any], session: McpSession | None = None,
    ) -> ToolResult:
        """Execute an MCP tool.

        Args:
            tool: Tool to execute
            params: Tool parameters
            session: Optional session (creates temporary if None)

        Returns:
            Tool execution result

        Raises:
            ToolExecutionError: If execution fails

        Example:
            >>> tool = McpTool(name="search", description="Search docs")
            >>> result = await provider.execute_tool(tool, {"query": "hello"})
            >>> print(result.output)
        """
        ...

    async def list_tools(self, session: McpSession) -> list[McpTool]:
        """List available tools from an MCP server.

        Args:
            session: Active MCP session

        Returns:
            List of available tools

        Example:
            >>> tools = await provider.list_tools(session)
            >>> for tool in tools:
            ...     print(f"{tool.name}: {tool.description}")
        """
        ...

    async def get_server_info(self, session: McpSession) -> dict[str, Any]:
        """Get information about the MCP server.

        Args:
            session: Active MCP session

        Returns:
            Server information dictionary

        Example:
            >>> info = await provider.get_server_info(session)
            >>> print(f"Server: {info['name']} v{info['version']}")
        """
        ...

    def is_connected(self, session: McpSession) -> bool:
        """Check if session is still connected.

        Args:
            session: MCP session to check

        Returns:
            True if connected, False otherwise

        Example:
            >>> if provider.is_connected(session):
            ...     print("Still connected")
        """
        ...


__all__ = ["McpProvider"]
