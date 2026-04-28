"""
MCP CLI Framework for Pheno SDK
===============================

Specialized CLI framework for MCP (Model Context Protocol) servers.
"""

import logging
import os
import sys
from pathlib import Path

from .base import CLIFramework
from .environment import EnvironmentManager


class MCPCLIFramework(CLIFramework):
    """CLI framework specialized for MCP servers.

    Provides MCP-specific functionality:
    - Automatic pheno-sdk path injection
    - Environment management
    - MCP endpoint configuration
    - Service orchestration integration
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        epilog: str | None = None,
        logger: logging.Logger | None = None,
    ):
        super().__init__(name, description, version, epilog, logger)

        self.env_manager = EnvironmentManager()
        self._setup_pheno_sdk_paths()
        self.setup_commands()

    def _setup_pheno_sdk_paths(self):
        """
        Set up pheno-sdk paths for development usage.
        """
        # Allow disabling pheno-sdk sys.path injection for lean/minimal runs
        if os.getenv("SKIP_PHENO_PATHS", "0").lower() in ("1", "true", "yes", "on"):
            return

        candidate_roots: list[Path] = []

        # Check environment variable
        env_root = os.environ.get("PHENO_SDK_ROOT")
        if env_root:
            candidate_roots.append(Path(env_root).expanduser())

        # Check common locations
        current_dir = Path(__file__).parent.parent.parent.parent
        sibling_root = current_dir / "pheno-sdk"
        inside_root = current_dir / "pheno-sdk"

        for root in (sibling_root, inside_root):
            if root.exists():
                candidate_roots.append(root)

        seen_roots: set[str] = set()
        candidate_paths: list[Path] = []

        for root in candidate_roots:
            root_str = str(root.resolve())
            if root_str in seen_roots or not root.exists():
                continue
            seen_roots.add(root_str)

            # Add package directories
            for child in sorted(root.iterdir()):
                if not child.is_dir() or child.name.startswith("."):
                    continue
                if (child / "pyproject.toml").exists() or (child / "setup.py").exists():
                    candidate_paths.append(child)

            # Add KInfra path
            kinfra_path = root / "KInfra" / "libraries" / "python"
            if kinfra_path.exists():
                candidate_paths.append(kinfra_path)

        # Add paths to sys.path
        added: list[str] = []
        for path in candidate_paths:
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                added.append(path_str)

        if added:
            pythonpath = os.environ.get("PYTHONPATH", "")
            path_prefix = ":".join(added)
            os.environ["PYTHONPATH"] = f"{path_prefix}:{pythonpath}" if pythonpath else path_prefix

            self.logger.debug(f"Added pheno-sdk paths: {added}")

    def setup_commands(self):
        """
        Set up MCP-specific commands.
        """
        # Start command
        self.register_command(
            name="start",
            description="Start the MCP server",
            handler=self._cmd_start,
            parser_config=self._config_start_parser,
        )

        # Stop command
        self.register_command(
            name="stop",
            description="Stop the MCP server",
            handler=self._cmd_stop,
        )

        # Status command
        self.register_command(
            name="status",
            description="Show server status",
            handler=self._cmd_status,
        )

        # Health command
        self.register_command(
            name="health",
            description="Perform health check",
            handler=self._cmd_health,
        )

        # Validate command
        self.register_command(
            name="validate",
            description="Validate configuration",
            handler=self._cmd_validate,
        )

    def _config_start_parser(self, parser):
        """
        Configure the start command parser.
        """
        parser.add_argument("--port", type=int, help="Port to run on")
        parser.add_argument("--domain", help="Domain for tunnel")
        parser.add_argument("--no-tunnel", action="store_true", help="Disable tunnel")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
        parser.add_argument("--dev", action="store_true", help="Enable development mode")
        parser.add_argument("--no-auth", action="store_true", help="Disable authentication")
        parser.add_argument(
            "--skip-validation", action="store_true", help="Skip startup validation",
        )

    def _cmd_start(self, args) -> int:
        """
        Handle start command.
        """
        self.logger.info(
            "Starting MCP server", port=args.port, dev=args.dev, no_tunnel=args.no_tunnel,
        )

        # This should be implemented by subclasses
        return self._start_server(args)

    def _cmd_stop(self, args) -> int:
        """
        Handle stop command.
        """
        self.logger.info("Stopping MCP server")
        return self._stop_server(args)

    def _cmd_status(self, args) -> int:
        """
        Handle status command.
        """
        self.logger.info("Checking server status")
        return self._show_status(args)

    def _cmd_health(self, args) -> int:
        """
        Handle health command.
        """
        self.logger.info("Performing health check")
        return self._health_check(args)

    def _cmd_validate(self, args) -> int:
        """
        Handle validate command.
        """
        self.logger.info("Validating configuration")
        return self._validate_config(args)

    # Abstract methods to be implemented by subclasses
    def _start_server(self, args) -> int:
        """Start the MCP server.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _start_server")

    def _stop_server(self, args) -> int:
        """Stop the MCP server.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _stop_server")

    def _show_status(self, args) -> int:
        """Show server status.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _show_status")

    def _health_check(self, args) -> int:
        """Perform health check.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _health_check")

    def _validate_config(self, args) -> int:
        """Validate configuration.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _validate_config")
