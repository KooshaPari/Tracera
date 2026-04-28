"""
Project Entry Point Template for Pheno SDK
==========================================

This template provides a standardized entry point for Pheno SDK projects,
including server orchestration, vendoring utilities, and project management
functions.

TODO: Implement the following placeholders:
- server_start(): Server initialization and startup logic
- server_stop(): Graceful shutdown and cleanup
- server_status(): Health checks and status reporting
- vendor_setup(): Dependency tracing and setup
- vendor_clean(): Remove vendor directories
- vendor_status(): Check vendoring completeness
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

try:
    # Import project-specific modules - adjust as needed
    from .core.config import get_config
    from .core.database import get_database
    from .core.logging import setup_logging
    from .services.server import ApplicationServer
except ImportError:
    # Fallback for projects that haven't set up these modules yet
    logging.warning("Project modules not found, using template fallback")
    from .template_fallbacks import get_config, setup_logging


logger = setup_logging(__name__)


class ServerOrchestrator:
    """
    Manages server lifecycle and orchestration for Pheno projects.
    """

    def __init__(self):
        self.server: ApplicationServer | None = None
        self.is_running = False
        self.config = get_config()
        self.database = get_database() if get_database else None

    async def start_server(self) -> None:
        """
        Initialize and start the application server.
        """
        try:
            logger.info("Starting Pheno SDK server...")

            # Initialize database connection if available
            if self.database:
                await self.database.initialize()
                logger.info("Database connection established")

            # Create server instance
            self.server = ApplicationServer(host=self.config.host, port=self.config.port)
            await self.server.start()

            self.is_running = True
            logger.info(f"Server started successfully on {self.config.host}:{self.config.port}")

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise

    async def stop_server(self) -> None:
        """
        Gracefully shutdown the server and cleanup resources.
        """
        try:
            logger.info("Shutting down Pheno SDK server...")

            if self.server:
                await self.server.stop()
                logger.info("Server stopped")

            # Close database connections
            if self.database:
                await self.database.close()
                logger.info("Database connections closed")

            self.is_running = False
            logger.info("Server shutdown complete")

        except Exception as e:
            logger.error(f"Error during server shutdown: {e}")

    async def get_server_status(self) -> dict[str, Any]:
        """
        Get comprehensive server health and status information.
        """
        status = {
            "running": self.is_running,
            "config": {
                "host": getattr(self.config, "host", "unknown"),
                "port": getattr(self.config, "port", "unknown"),
                "environment": getattr(self.config, "environment", "unknown"),
            },
            "health": {},
        }

        if self.server:
            try:
                status["health"]["server"] = await self.server.health_check()
            except Exception as e:
                status["health"]["server"] = {"status": "unhealthy", "error": str(e)}

        if self.database:
            try:
                status["health"]["database"] = await self.database.health_check()
            except Exception as e:
                status["health"]["database"] = {"status": "unhealthy", "error": str(e)}

        return status


class VendorManager:
    """
    Manages dependency vendoring for Pheno projects.
    """

    def __init__(self):
        self.vendor_dir = Path(__file__).parent / "vendor"
        self.config_file = self.vendor_dir / "vendor_config.json"

    async def setup_vendoring(self) -> None:
        """
        Set up vendoring environment and trace dependencies.
        """
        try:
            logger.info("Setting up dependency vendoring...")

            # Create vendor directory
            self.vendor_dir.mkdir(exist_ok=True)

            # Trace dependencies
            import pkg_resources

            dependencies = []
            for pkg in pkg_resources.working_set:
                if not pkg.location.startswith(sys.prefix):  # Only non-system packages
                    dependencies.append(
                        {
                            "name": pkg.project_name,
                            "version": pkg.version,
                            "location": pkg.location,
                            "files": list(pkg.get_entry_map().keys())[:5],  # Limit file listing
                        },
                    )

            # Create vendor configuration
            config = {
                "project": getattr(self, "get_project_name", lambda: "pheno-project")(),
                "created_at": asyncio.get_event_loop().time(),
                "dependencies": dependencies,
                "vendor_path": str(self.vendor_dir.relative_to(Path.cwd())),
            }

            import json

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Vendoring setup complete. Found {len(dependencies)} dependencies")

        except Exception as e:
            logger.error(f"Failed to setup vendoring: {e}")
            raise

    async def clean_vendors(self) -> None:
        """
        Remove all vendored dependencies and reset state.
        """
        try:
            logger.info("Cleaning vendor directory...")

            if self.vendor_dir.exists():
                import shutil

                shutil.rmtree(self.vendor_dir)
                logger.info("Vendor directory removed")

            # Clean up any additional vendor-related files
            vendor_files = [
                "requirements-frozen.txt",
                "vendor_requirements.txt",
                "vendor_lock.json",
            ]

            for file in vendor_files:
                file_path = Path(file)
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Removed {file}")

        except Exception as e:
            logger.error(f"Failed to clean vendors: {e}")
            raise

    async def get_vendor_status(self) -> dict[str, Any]:
        """
        Check the status and completeness of vendoring.
        """
        status = {
            "vendoring_enabled": False,
            "vendor_directory_exists": self.vendor_dir.exists(),
            "config_exists": self.config_file.exists(),
            "dependencies_count": 0,
            "last_updated": None,
        }

        if self.config_file.exists():
            try:
                import json

                with open(self.config_file) as f:
                    config = json.load(f)

                status.update(
                    {
                        "vendoring_enabled": True,
                        "dependencies_count": len(config.get("dependencies", [])),
                        "last_updated": config.get("created_at"),
                        "project": config.get("project", "unknown"),
                    },
                )
            except Exception as e:
                logger.warning(f"Error reading vendor config: {e}")

        return status


# Global instances
server_orchestrator = ServerOrchestrator()
vendor_manager = VendorManager()


# Public API functions
async def server_start() -> None:
    """
    Start the Pheno SDK server (Template Implementation).
    """
    await server_orchestrator.start_server()


async def server_stop() -> None:
    """
    Stop the Pheno SDK server (Template Implementation).
    """
    await server_orchestrator.stop_server()


async def server_status() -> dict[str, Any]:
    """
    Get server status information (Template Implementation).
    """
    return await server_orchestrator.get_server_status()


async def vendor_setup() -> None:
    """
    Set up dependency vendoring (Template Implementation).
    """
    await vendor_manager.setup_vendoring()


async def vendor_clean() -> None:
    """
    Clean vendoring environment (Template Implementation).
    """
    await vendor_manager.clean_vendors()


async def vendor_status() -> dict[str, Any]:
    """
    Get vendoring status information (Template Implementation).
    """
    return await vendor_manager.get_vendor_status()


# Backwards compatibility aliases
def start_server():
    """Deprecated: Use server_start() instead."""
    return server_start()


def stop_server():
    """Deprecated: Use server_stop() instead."""
    return server_stop()


def get_server_status():
    """Deprecated: Use server_status() instead."""
    return server_status()


def setup_vendoring():
    """Deprecated: Use vendor_setup() instead."""
    return vendor_setup()


def clean_vendors():
    """Deprecated: Use vendor_clean() instead."""
    return vendor_clean()


def get_vendor_status():
    """Deprecated: Use vendor_status() instead."""
    return vendor_status()
