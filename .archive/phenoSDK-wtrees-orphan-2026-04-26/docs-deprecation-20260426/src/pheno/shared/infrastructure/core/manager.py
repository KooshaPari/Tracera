"""
InfrastructureManager implementation.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import ResourceConfig, ResourceInfo, ServiceConfig, ServiceInfo
from .statuses import ResourceStatus, ServiceStatus

logger = logging.getLogger(__name__)


class InfrastructureManager:
    """
    Unified infrastructure and process management system.
    """

    def __init__(
        self,
        project_name: str | None = None,
        config_dir: Path | None = None,
        enable_monitoring: bool = True,
        enable_auto_recovery: bool = True,
    ) -> None:
        self.project_name = project_name or Path.cwd().name
        self.config_dir = config_dir or Path.home() / ".pheno"
        self.enable_monitoring = enable_monitoring
        self.enable_auto_recovery = enable_auto_recovery

        self.services: dict[str, ServiceConfig] = {}
        self.service_info: dict[str, ServiceInfo] = {}
        self.service_processes: dict[str, Any] = {}

        self.resources: dict[str, ResourceConfig] = {}
        self.resource_info: dict[str, ResourceInfo] = {}

        self.port_allocator = None
        self.resource_allocator = None
        self.health_monitor = None
        self.metrics_collector = None
        self.orchestrator = None

        self._shutdown_requested = False
        self._monitoring_tasks: list[asyncio.Task] = []

        self._initialize_components()
        self._setup_signal_handlers()

        logger.info("InfrastructureManager initialized for project: %s", self.project_name)

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    def _initialize_components(self) -> None:
        """
        Initialize all infrastructure components.
        """
        try:
            self._import_components()
            self._setup_allocators()
            self._setup_monitoring_components()
            self._setup_orchestrator()
        except ImportError as exc:
            logger.warning("Some infrastructure components not available: %s", exc)

    def _import_components(self) -> None:
        """
        Import required infrastructure components.
        """
        from .allocation import PortAllocator, ResourceAllocator  # type: ignore
        from .monitoring import HealthMonitor, MetricsCollector  # type: ignore
        from .orchestrator import (  # type: ignore
            OrchestrationConfig,
            ServiceOrchestrator,
        )

        # Store imports for use in other methods
        self._PortAllocator = PortAllocator
        self._ResourceAllocator = ResourceAllocator
        self._HealthMonitor = HealthMonitor
        self._MetricsCollector = MetricsCollector
        self._OrchestrationConfig = OrchestrationConfig
        self._ServiceOrchestrator = ServiceOrchestrator

    def _setup_allocators(self) -> None:
        """
        Setup port and resource allocators.
        """
        self.port_allocator = self._PortAllocator()
        self.resource_allocator = self._ResourceAllocator()

    def _setup_monitoring_components(self) -> None:
        """
        Setup monitoring components if enabled.
        """
        if self.enable_monitoring:
            self.health_monitor = self._HealthMonitor()
            self.metrics_collector = self._MetricsCollector()

    def _setup_orchestrator(self) -> None:
        """
        Setup service orchestrator.
        """
        orchestrator_config = self._OrchestrationConfig(
            project_name=self.project_name,
            enable_monitoring=self.enable_monitoring,
            enable_auto_recovery=self.enable_auto_recovery,
        )
        self.orchestrator = self._ServiceOrchestrator(orchestrator_config)

    def _setup_signal_handlers(self) -> None:
        def signal_handler(signum, frame):
            logger.info("Received signal %s, initiating graceful shutdown...", signum)
            self._shutdown_requested = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    # ------------------------------------------------------------------
    # Registration APIs
    # ------------------------------------------------------------------
    def register_service(self, config: ServiceConfig) -> None:
        self.services[config.name] = config
        self.service_info[config.name] = ServiceInfo(
            name=config.name,
            status=ServiceStatus.PENDING,
            start_time=None,
            metadata=dict(config.metadata),
        )

    def register_resource(self, config: ResourceConfig) -> None:
        self.resources[config.name] = config
        self.resource_info[config.name] = ResourceInfo(
            name=config.name,
            resource_type=config.resource_type,
            status=ResourceStatus.PENDING,
            provider=config.provider,
            metadata=dict(config.metadata),
        )

    # ------------------------------------------------------------------
    # Service lifecycle (stubs for integration)
    # ------------------------------------------------------------------
    async def start_service(self, name: str) -> bool:
        logger.info("Starting service %s", name)
        config = self.services.get(name)
        info = self.service_info.get(name)
        if not config or not info:
            logger.error("Service config not found for %s", name)
            return False
        info.status = ServiceStatus.STARTING
        info.start_time = datetime.now()
        # Placeholder for actual implementation
        logger.debug("start_service not implemented; returning success")
        info.status = ServiceStatus.RUNNING
        return True

    async def stop_service(self, name: str) -> bool:
        logger.info("Stopping service %s", name)
        info = self.service_info.get(name)
        if not info:
            return False
        info.status = ServiceStatus.STOPPED
        return True

    async def start_all(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for service_name in self.services:
            results[service_name] = await self.start_service(service_name)
        return results

    async def shutdown(self) -> None:
        logger.info("Initiating InfrastructureManager shutdown")
        self._shutdown_requested = True
        for task in self._monitoring_tasks:
            task.cancel()
        await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
        for service_name in list(self.services.keys()):
            await self.stop_service(service_name)
        logger.info("InfrastructureManager shutdown complete")

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def get_service_status(self, name: str) -> ServiceInfo | None:
        return self.service_info.get(name)

    def get_resource_status(self, name: str) -> ResourceInfo | None:
        return self.resource_info.get(name)

    def get_status_snapshot(self) -> dict[str, Any]:
        return {
            "services": dict(self.service_info.items()),
            "resources": dict(self.resource_info.items()),
        }


__all__ = ["InfrastructureManager"]
