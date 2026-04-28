"""
Universal Project Framework for Pheno SDK
=========================================

A flexible, composable framework for building entry points for ANY type of project.
This framework provides generic components that can be easily configured and extended
for any project implementation - web servers, CLI tools, APIs, microservices, etc.

Key Components:
- ProjectConfig: Configuration class for any project
- AdvancedCommandHandler: Advanced commands for complex operations
"""

from .config import ProjectConfig, ProjectConfigBuilder, ProjectType


class MCPServerBuilderAdapter:
    """Adapter that wraps ProjectConfigBuilder with additional MCP server methods."""

    def __init__(self, builder: ProjectConfigBuilder):
        """Initialize adapter with underlying builder.

        Args:
            builder: ProjectConfigBuilder instance
        """
        self._builder = builder
        self._cli_handlers = {}

    def description(self, text: str) -> "MCPServerBuilderAdapter":
        """Set server description."""
        self._builder.description(text)
        return self

    def version(self, version: str) -> "MCPServerBuilderAdapter":
        """Set server version."""
        self._builder.version(version)
        return self

    def domain(self, domain: str) -> "MCPServerBuilderAdapter":
        """Set server domain."""
        self._builder.custom("domain", domain)
        return self

    def command(self, cmd: str) -> "MCPServerBuilderAdapter":
        """Set startup command."""
        self._builder.custom("command", cmd)
        return self

    def working_directory(self, path: str) -> "MCPServerBuilderAdapter":
        """Set working directory."""
        self._builder.custom("working_directory", path)
        return self

    def environment(self, **env_vars) -> "MCPServerBuilderAdapter":
        """Set environment variables."""
        self._builder.custom("environment", env_vars)
        return self

    def health_check(self, endpoint: str) -> "MCPServerBuilderAdapter":
        """Set health check endpoint."""
        self._builder.custom("health_check", endpoint)
        return self

    def timeouts(self, connect: int, read: int) -> "MCPServerBuilderAdapter":
        """Set connection and read timeouts."""
        self._builder.custom("connect_timeout", connect)
        self._builder.custom("read_timeout", read)
        return self

    def custom(self, key: str, value) -> "MCPServerBuilderAdapter":
        """Set custom configuration value."""
        self._builder.custom(key, value)
        return self

    def cli_handler(self, command: str, handler) -> "MCPServerBuilderAdapter":
        """Register a CLI command handler.

        Args:
            command: Command name (e.g., "start", "stop")
            handler: Handler function

        Returns:
            Self for chaining
        """
        self._cli_handlers[command] = handler
        return self

    def build(self):
        """Build final server configuration."""
        return self._builder.build()

    def build_cli(self):
        """Build CLI handler for server management.

        Returns:
            A CLI handler object with start/stop methods
        """
        class CLIHandler:
            def __init__(self, adapter):
                self.adapter = adapter

            def _start_server(self, args):
                """Start the MCP server."""
                port = args.port or self.adapter._builder._config.custom_config.get("port", 8000)
                print(f"Starting server on port {port}...")
                # Placeholder - actual server startup would be implemented here
                return 0

        return CLIHandler(self)

    def build_entry_point(self):
        """Build entry point for command execution.

        Returns:
            A callable that handles CLI commands
        """
        def entry_point():
            # Simple entry point that runs the CLI handlers
            import sys
            if len(sys.argv) > 1:
                command = sys.argv[1]
                if command in self._cli_handlers:
                    # Create a simple args object
                    class Args:
                        pass
                    args = Args()
                    args.port = self._builder._config.custom_config.get("port", 8000)
                    args.dev = "--dev" in sys.argv
                    args.no_tunnel = "--no-tunnel" in sys.argv
                    args.verbose = "--verbose" in sys.argv
                    return self._cli_handlers[command](args)
            return 0
        return entry_point


def create_mcp_server(name: str, port: int = 8000):
    """Create a new MCP server configuration builder.

    This is a compatibility function that uses ProjectConfigBuilder
    to create MCP-specific server configurations.

    Args:
        name: Server name/identifier
        port: Port to run server on (default: 8000)

    Returns:
        MCPServerBuilderAdapter instance for MCP server configuration

    Example:
        >>> server = (create_mcp_server("my-server", port=8000)
        ...           .description("My MCP Server")
        ...           .version("1.0.0")
        ...           .build())
    """
    builder = ProjectConfigBuilder(name, ProjectType.MCP_SERVER)
    builder.custom("port", port)
    return MCPServerBuilderAdapter(builder)


# Optional imports - only if modules exist
try:
    from .advanced_commands import AdvancedCommandHandler

    _has_advanced_commands = True
except ImportError:
    _has_advanced_commands = False

try:
    _has_cli = True
except ImportError:
    _has_cli = False

try:
    _has_builder = True
except ImportError:
    _has_builder = False

__all__ = [
    "ProjectConfig",
    "ProjectConfigBuilder",
    "ProjectType",
    "create_mcp_server",
]

if _has_advanced_commands:
    __all__.append("AdvancedCommandHandler")

if _has_cli:
    __all__.extend(["ProjectCLI", "ProjectCLIBuilder"])

if _has_builder:
    __all__.append("ProjectBuilder")
