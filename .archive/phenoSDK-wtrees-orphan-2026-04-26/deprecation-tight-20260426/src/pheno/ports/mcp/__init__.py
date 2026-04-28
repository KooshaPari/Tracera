"""
MCP Ports - Protocol interfaces for Model Context Protocol

These ports define the contracts that MCP adapters must implement.
Following hexagonal architecture, the domain layer depends on these
ports, and adapters (mcp-sdk-kit, mcp-infra-sdk) implement them.

Port Protocols:
- McpProvider: Core MCP server connection and tool execution
- ResourceProvider: Resource access and scheme handling
- ToolRegistry: Tool registration and discovery
- SessionManager: Session lifecycle management
- MonitoringProvider: Workflow and metrics monitoring
"""

from .monitoring import MonitoringProvider
from .provider import McpProvider
from .resource_provider import ResourceProvider, ResourceSchemeHandler
from .session_manager import SessionManager
from .tool_registry import ToolRegistry

__all__ = [
    "McpProvider",
    "MonitoringProvider",
    "ResourceProvider",
    "ResourceSchemeHandler",
    "SessionManager",
    "ToolRegistry",
]
