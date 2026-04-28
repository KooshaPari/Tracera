"""MCP Server implementation for Pheno SDK.

This server exposes Pheno SDK functionality through the Model Context Protocol, allowing
AI assistants to interact with deployments, services, and configurations.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

from pheno.patterns.creational.use_case_factory import UseCaseFactory

from .handlers import PromptHandler, ResourceHandler, ToolHandler

if TYPE_CHECKING:
    from pheno.application.ports.events import EventPublisher
    from pheno.application.ports.repositories import (
        ConfigurationRepository,
        DeploymentRepository,
        ServiceRepository,
        UserRepository,
    )


class MCPServer:
    """Model Context Protocol server for Pheno SDK.

    Exposes resources, tools, and prompts for AI assistants to interact with the Pheno
    SDK through the MCP protocol.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        deployment_repository: DeploymentRepository,
        service_repository: ServiceRepository,
        configuration_repository: ConfigurationRepository,
        event_publisher: EventPublisher,
        name: str = "pheno-sdk",
        version: str = "1.0.0",
    ):
        """Initialize MCP server.

        Args:
            user_repository: User repository
            deployment_repository: Deployment repository
            service_repository: Service repository
            configuration_repository: Configuration repository
            event_publisher: Event publisher
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version

        # Create use case factory
        self.use_case_factory = UseCaseFactory(
            user_repository=user_repository,
            deployment_repository=deployment_repository,
            service_repository=service_repository,
            configuration_repository=configuration_repository,
            event_publisher=event_publisher,
        )

        # Initialize handlers
        self.resource_handler = ResourceHandler(self.use_case_factory)
        self.tool_handler = ToolHandler(self.use_case_factory)
        self.prompt_handler = PromptHandler()

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle an MCP request.

        Args:
            request: MCP request dictionary

        Returns:
            MCP response dictionary
        """
        method = request.get("method")
        params = request.get("params", {})

        try:
            if method == "initialize":
                return await self._handle_initialize(params)
            if method == "resources/list":
                return await self._handle_list_resources(params)
            if method == "resources/read":
                return await self._handle_read_resource(params)
            if method == "tools/list":
                return await self._handle_list_tools(params)
            if method == "tools/call":
                return await self._handle_call_tool(params)
            if method == "prompts/list":
                return await self._handle_list_prompts(params)
            if method == "prompts/get":
                return await self._handle_get_prompt(params)
            return self._error_response(f"Unknown method: {method}")
        except Exception as e:
            return self._error_response(str(e))

    async def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle initialize request.
        """
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "resources": {"subscribe": False, "listChanged": False},
                "tools": {},
                "prompts": {"listChanged": False},
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version,
            },
        }

    async def _handle_list_resources(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle list resources request.
        """
        resources = await self.resource_handler.list_resources()
        return {"resources": resources}

    async def _handle_read_resource(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle read resource request.
        """
        uri = params.get("uri")
        if not uri:
            return self._error_response("Missing uri parameter")

        content = await self.resource_handler.read_resource(uri)
        return {"contents": [content]}

    async def _handle_list_tools(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle list tools request.
        """
        tools = await self.tool_handler.list_tools()
        return {"tools": tools}

    async def _handle_call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle call tool request.
        """
        name = params.get("name")
        arguments = params.get("arguments", {})

        if not name:
            return self._error_response("Missing name parameter")

        result = await self.tool_handler.call_tool(name, arguments)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    async def _handle_list_prompts(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle list prompts request.
        """
        prompts = await self.prompt_handler.list_prompts()
        return {"prompts": prompts}

    async def _handle_get_prompt(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Handle get prompt request.
        """
        name = params.get("name")
        arguments = params.get("arguments", {})

        if not name:
            return self._error_response("Missing name parameter")

        prompt = await self.prompt_handler.get_prompt(name, arguments)
        return {"messages": prompt}

    def _error_response(self, message: str) -> dict[str, Any]:
        """
        Create error response.
        """
        return {"error": {"code": -32000, "message": message}}

    async def start(self, host: str = "localhost", port: int = 3000):
        """Start the MCP server.

        Args:
            host: Server host
            port: Server port
        """
        # This is a simplified version - in production, you'd use a proper
        # MCP server implementation with stdio or HTTP transport
        print(f"MCP Server started: {self.name} v{self.version}")
        print(f"Listening on {host}:{port}")
        print("Resources, tools, and prompts are available")

        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nServer stopped")
