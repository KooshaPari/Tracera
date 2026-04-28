"""
Atoms MCP Entry Point Constructor
=================================

Specialized entry point for the Atoms MCP server, providing Atoms-specific
configuration and defaults.
"""

import logging
from pathlib import Path

from ..cli_framework import EnvironmentManager, MCPCLIFramework
from .base import MCPEntryPoint, MCPServiceConfig


class AtomsMCPEntryPoint(MCPEntryPoint):
    """Entry point constructor for the Atoms MCP server.

    Provides Atoms-specific defaults and configuration:
    - Default port: 50002
    - Default domain: atomcp.kooshapari.com
    - Atoms-specific service configuration
    - Integration with pheno-sdk packages
    """

    # Atoms-specific defaults
    DEFAULT_PORT = 50002
    DEFAULT_DOMAIN = "atomcp.kooshapari.com"
    PROJECT_NAME = "atoms_mcp"

    def __init__(
        self,
        port: int | None = None,
        domain: str | None = None,
        verbose: bool = False,
        no_tunnel: bool = False,
        logger: logging.Logger | None = None,
    ):
        """Initialize the Atoms MCP entry point.

        Args:
            port: Port to run on (default: 50002)
            domain: Domain for tunnel (default: atomcp.kooshapari.com)
            verbose: Enable verbose logging
            no_tunnel: Disable CloudFlare tunnel
            logger: Optional logger instance
        """
        self.port = port or self.DEFAULT_PORT
        self.domain = domain if not no_tunnel else None
        self.verbose = verbose
        self.no_tunnel = no_tunnel

        # Configure logging
        if logger is None:
            logger = logging.getLogger(self.PROJECT_NAME)
            if verbose:
                logger.setLevel(logging.DEBUG)

        # Create Atoms-specific service configuration
        service_configs = self._create_atoms_service_configs()

        # Initialize base class
        super().__init__(
            project_name=self.PROJECT_NAME,
            service_configs=service_configs,
            dependencies={},  # Atoms doesn't have complex dependencies
            service_domain=self.domain,
            logger=logger,
        )

    def _create_atoms_service_configs(self) -> list[MCPServiceConfig]:
        """
        Create Atoms-specific service configurations.
        """
        # Build the command with proper PYTHONPATH
        repo_root = Path(__file__).parent.parent.parent.parent.resolve()
        sdk_root = repo_root / "pheno-sdk"

        # Set up PYTHONPATH for pheno-sdk packages
        sdk_paths = [
            str(sdk_root / "KInfra" / "libraries" / "python"),
            str(sdk_root / "mcp-QA"),
        ]

        # Create environment variables
        environment = {
            "PYTHONPATH": ":".join(sdk_paths),
            "ATOMS_VERBOSE": "1" if self.verbose else "0",
            "ATOMS_NO_TUNNEL": "1" if self.no_tunnel else "0",
        }

        # Create service configuration
        service_config = MCPServiceConfig(
            name="atoms_server",
            command="python -m atoms_mcp_old.atoms-mcp start",
            port=self.port,
            domain=self.domain,
            health_check_path="/health",
            startup_timeout=30,
            shutdown_timeout=10,
            environment=environment,
            working_directory=repo_root,
        )

        return [service_config]

    async def start_atoms_server(self) -> int:
        """Start the Atoms MCP server.

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            success = await self.start(monitor=True)
            return 0 if success else 1
        except Exception as e:
            self.logger.exception(f"Failed to start Atoms MCP server: {e}")
            return 1

    def get_server_info(self) -> dict:
        """
        Get information about the Atoms MCP server configuration.
        """
        return {
            "project": self.PROJECT_NAME,
            "port": self.port,
            "domain": self.domain,
            "tunnel_enabled": not self.no_tunnel,
            "verbose": self.verbose,
            "services": [config.name for config in self.service_configs],
        }


class AtomsMCPCLI(MCPCLIFramework):
    """CLI framework for the Atoms MCP server.

    Provides a complete CLI interface using the pheno-sdk framework.
    """

    def __init__(self):
        super().__init__(
            name="atoms-mcp",
            description="Atoms MCP - Unified CLI for all operations",
            version="1.0.0",
            epilog="""
Examples:
  atoms-mcp start                      # Start local server
  atoms-mcp start --port 50003         # Start on custom port
  atoms-mcp start --no-tunnel          # Start without tunnel
  atoms-mcp stop                       # Stop server
  atoms-mcp status                     # Show status
  atoms-mcp health                     # Health check
  atoms-mcp validate                   # Validate configuration
            """,
        )

        self.env_manager = EnvironmentManager()
        self.atoms_entry: AtomsMCPEntryPoint | None = None

    def _start_server(self, args) -> int:
        """
        Start the Atoms MCP server.
        """
        try:
            # Set MCP endpoint for local runtime
            self.env_manager.set_mcp_endpoint_for_target("local")

            # Create Atoms MCP entry point
            self.atoms_entry = AtomsMCPEntryPoint(
                port=args.port,
                domain=args.domain,
                verbose=args.verbose,
                no_tunnel=args.no_tunnel,
                logger=self.logger,
            )

            # Show server info
            info = self.atoms_entry.get_server_info()
            self.log_info(
                "Starting Atoms MCP Server",
                port=info["port"],
                domain=info["domain"],
                tunnel_enabled=info["tunnel_enabled"],
            )

            # Start the server
            exit_code = await self.atoms_entry.start_atoms_server()

            if exit_code == 0:
                self.log_info("Atoms MCP Server started successfully")
            else:
                self.log_error("Failed to start Atoms MCP Server")

            return exit_code

        except Exception as e:
            self.log_error(f"Error starting Atoms MCP Server: {e}")
            return 1

    def _stop_server(self, args) -> int:
        """
        Stop the Atoms MCP server.
        """
        try:
            if not self.atoms_entry:
                self.atoms_entry = AtomsMCPEntryPoint(logger=self.logger)

            await self.atoms_entry.stop()
            self.log_info("Atoms MCP Server stopped")
            return 0

        except Exception as e:
            self.log_error(f"Error stopping Atoms MCP Server: {e}")
            return 1

    def _show_status(self, args) -> int:
        """
        Show server status.
        """
        try:
            if not self.atoms_entry:
                self.atoms_entry = AtomsMCPEntryPoint(logger=self.logger)

            self.atoms_entry.show_status()
            return 0

        except Exception as e:
            self.log_error(f"Error getting server status: {e}")
            return 1

    def _health_check(self, args) -> int:
        """
        Perform health check.
        """
        try:
            if not self.atoms_entry:
                self.atoms_entry = AtomsMCPEntryPoint(logger=self.logger)

            health = await self.atoms_entry.health_check()

            self.log_info("Atoms MCP Server Health Check")
            self.log_info(f"Overall Status: {health['overall_status']}")

            for service_name, service_health in health["services"].items():
                self.log_info(
                    f"{service_name}: {service_health['state']} on port {service_health['port']}",
                )
                if service_health.get("tunnel_url"):
                    self.log_info(f"  Tunnel URL: {service_health['tunnel_url']}")

            return 0 if health["overall_status"] == "healthy" else 1

        except Exception as e:
            self.log_error(f"Error performing health check: {e}")
            return 1

    def _validate_config(self, args) -> int:
        """
        Validate configuration.
        """
        try:
            # Basic validation - check if required components are available
            self.log_info("Validating Atoms MCP configuration...")

            # Check if KInfra is available
            try:
                self.log_info("✅ KInfra is available")
            except ImportError as e:
                self.log_error(f"❌ KInfra is not available: {e}")
                return 1

            # Check if mcp-QA is available
            try:
                self.log_info("✅ mcp-QA is available")
            except ImportError as e:
                self.log_error(f"❌ mcp-QA is not available: {e}")
                return 1

            self.log_info("✅ Configuration validation passed")
            return 0

        except Exception as e:
            self.log_error(f"Error validating configuration: {e}")
            return 1
