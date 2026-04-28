"""MCP HTTP Client Example for TraceRTM.

This example demonstrates how to use the MCP server over HTTP with:
- JSON-RPC 2.0 request/response handling
- Bearer token authentication
- Async httpx-based implementation
- Type-safe responses with Pydantic

Usage:
    python examples/mcp_http_client.py

Requirements:
    httpx>=0.27.0
    pydantic>=2.0.0
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
from typing import Any, Self

import httpx
from pydantic import BaseModel


class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request structure."""

    jsonrpc: str = "2.0"
    id: int
    method: str
    params: dict[str, Any] | None = None


class JsonRpcError(BaseModel):
    """JSON-RPC 2.0 error structure."""

    code: int
    message: str
    data: Any | None = None


class JsonRpcResponse(BaseModel):
    """JSON-RPC 2.0 response structure."""

    jsonrpc: str
    id: int
    result: Any | None = None
    error: JsonRpcError | None = None


class MCPHTTPClient:
    """HTTP-based MCP client implementation."""

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize MCP HTTP client.

        Args:
            base_url: Base URL of the MCP server (e.g., "http://localhost:8000")
            token: Optional bearer token for authentication
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self._request_id = 0
        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def _next_request_id(self) -> int:
        """Generate a unique request ID."""
        self._request_id += 1
        return self._request_id

    def _build_headers(self) -> dict[str, str]:
        """Build headers for MCP requests."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _send_request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a JSON-RPC request to the MCP server.

        Args:
            method: JSON-RPC method name
            params: Optional method parameters

        Returns:
            Response result

        Raises:
            httpx.HTTPError: On HTTP errors
            ValueError: On JSON-RPC errors or invalid responses
        """
        request = JsonRpcRequest(id=self._next_request_id(), method=method, params=params)

        response = await self._client.post(
            f"{self.base_url}/mcp/rpc",
            headers=self._build_headers(),
            content=request.model_dump_json(),
        )

        response.raise_for_status()

        data = JsonRpcResponse.model_validate_json(response.content)

        if data.error:
            msg = f"JSON-RPC Error {data.error.code}: {data.error.message}"
            raise ValueError(msg)

        if data.result is None:
            msg = "Invalid JSON-RPC response: missing result"
            raise ValueError(msg)

        return data.result

    async def initialize(
        self,
        protocol_version: str = "2024-11-05",
        client_name: str = "Python MCP Client",
        client_version: str = "1.0.0",
    ) -> dict[str, Any]:
        """Initialize the MCP session.

        Args:
            protocol_version: MCP protocol version
            client_name: Name of the client application
            client_version: Version of the client application

        Returns:
            Server initialization response with server info and capabilities
        """
        return await self._send_request(
            "initialize",
            {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True,
                },
                "clientInfo": {
                    "name": client_name,
                    "version": client_version,
                },
            },
        )

    async def list_tools(self) -> dict[str, Any]:
        """List available tools.

        Returns:
            Dictionary with 'tools' key containing list of tool definitions
        """
        return await self._send_request("tools/list")

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call a tool with parameters.

        Args:
            name: Tool name
            arguments: Optional tool arguments

        Returns:
            Tool execution result
        """
        return await self._send_request("tools/call", {"name": name, "arguments": arguments or {}})

    async def list_resources(self) -> dict[str, Any]:
        """List available resources.

        Returns:
            Dictionary with 'resources' key containing list of resource definitions
        """
        return await self._send_request("resources/list")

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """Read a resource by URI.

        Args:
            uri: Resource URI

        Returns:
            Dictionary with 'contents' key containing resource data
        """
        return await self._send_request("resources/read", {"uri": uri})

    async def list_prompts(self) -> dict[str, Any]:
        """List available prompts.

        Returns:
            Dictionary with 'prompts' key containing list of prompt definitions
        """
        return await self._send_request("prompts/list")

    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get a prompt with arguments.

        Args:
            name: Prompt name
            arguments: Optional prompt arguments

        Returns:
            Dictionary with 'messages' key containing prompt messages
        """
        return await self._send_request("prompts/get", {"name": name, "arguments": arguments or {}})

    async def close(self) -> None:
        """Close the MCP session and HTTP client."""
        try:
            # Send cancellation notification (no response expected)
            await self._client.post(
                f"{self.base_url}/mcp/rpc",
                headers=self._build_headers(),
                content=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "notifications/cancelled",
                    "params": {},
                }),
            )
        except Exception as e:
            __import__("logging").getLogger(__name__).debug("close: %s", e)
        finally:
            await self._client.aclose()


async def example_usage() -> None:
    """Example usage of the MCP HTTP client."""
    # Initialize client with authentication
    token = os.environ.get("MCP_AUTH_TOKEN", "")
    async with MCPHTTPClient(
        base_url="http://localhost:8000",
        token=token,
    ) as client:
        # Initialize session
        await client.initialize()

        # List available tools
        tools_response = await client.list_tools()
        for _tool in tools_response["tools"][:5]:  # Show first 5
            pass

        # Call a tool (example: list projects)
        with contextlib.suppress(Exception):
            await client.call_tool(
                "project_manage",
                {"action": "list", "params": {}},
            )

        # List resources
        resources_response = await client.list_resources()
        for _resource in resources_response["resources"][:5]:  # Show first 5
            pass

        # List prompts
        prompts_response = await client.list_prompts()
        for _prompt in prompts_response["prompts"][:5]:  # Show first 5
            pass


async def example_with_error_handling() -> None:
    """Example with comprehensive error handling."""
    try:
        token = os.environ.get("MCP_AUTH_TOKEN", "")
        async with MCPHTTPClient(
            base_url="http://localhost:8000",
            token=token,
        ) as client:
            await client.initialize()
            await client.call_tool("project_manage", {"action": "list"})

    except httpx.HTTPError:
        pass
    except ValueError:
        pass
    except Exception:
        pass


async def example_manual_lifecycle() -> None:
    """Example with manual client lifecycle management."""
    token = os.environ.get("MCP_AUTH_TOKEN", "")
    client = MCPHTTPClient(
        base_url="http://localhost:8000",
        token=token,
    )

    try:
        # Initialize
        await client.initialize()

        # Use client
        await client.list_tools()

    finally:
        # Always close
        await client.close()


if __name__ == "__main__":
    # Run the main example
    asyncio.run(example_usage())

    asyncio.run(example_with_error_handling())
