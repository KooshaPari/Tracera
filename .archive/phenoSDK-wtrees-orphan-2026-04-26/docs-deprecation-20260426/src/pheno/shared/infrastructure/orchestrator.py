"""Service Orchestrator.

Provides advanced orchestration capabilities for complex service deployments with
dependency management, health monitoring, and auto-recovery.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class OrchestrationMode(Enum):
    """
    Orchestration execution mode.
    """

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DEPENDENCY_ORDERED = "dependency_ordered"


class OrchestrationStatus(Enum):
    """
    Status of orchestration.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OrchestrationConfig:
    """
    Configuration for service orchestration.
    """

    project_name: str
    mode: OrchestrationMode = OrchestrationMode.DEPENDENCY_ORDERED
    startup_timeout: float = 300.0  # 5 minutes
    shutdown_timeout: float = 60.0  # 1 minute
    health_check_interval: float = 30.0
    enable_monitoring: bool = True
    enable_auto_recovery: bool = True
    max_restart_attempts: int = 3
    restart_delay: float = 5.0
    parallel_limit: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """
    Result of orchestration execution.
    """

    success: bool
    status: OrchestrationStatus
    services_started: list[str]
    services_failed: list[str]
    duration: float
    start_time: datetime
    end_time: datetime | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ServiceOrchestrator:
    """Advanced service orchestrator with dependency management and monitoring.

    Provides comprehensive orchestration capabilities including:
    - Dependency resolution and ordering
    - Parallel and sequential execution modes
    - Health monitoring and auto-recovery
    - Graceful shutdown with dependency ordering
    - Progress tracking and status reporting
    """

    def __init__(self, config: OrchestrationConfig):
        """Initialize the service orchestrator.

        Args:
            config: Orchestration configuration
        """
        self.config = config
        self.services: dict[str, Any] = {}
        self.dependencies: dict[str, list[str]] = {}
        self.service_status: dict[str, str] = {}
        self.monitoring_tasks: list[asyncio.Task] = []
        self._shutdown_requested = False

        logger.info(f"ServiceOrchestrator initialized for project: {config.project_name}")

    def add_service(
        self, name: str, service_config: Any, depends_on: list[str] | None = None,
    ) -> None:
        """Add a service to the orchestrator.

        Args:
            name: Service name
            service_config: Service configuration
            depends_on: List of service dependencies
        """
        self.services[name] = service_config
        self.dependencies[name] = depends_on or []
        self.service_status[name] = "pending"

        logger.info(f"Added service '{name}' with dependencies: {depends_on}")

    async def orchestrate_services(
        self, service_configs: list[Any], dependencies: dict[str, list[str]] | None = None,
    ) -> OrchestrationResult:
        """Orchestrate multiple services with dependency management.

        Args:
            service_configs: List of service configurations
            dependencies: Optional dependency mapping

        Returns:
            OrchestrationResult with execution details
        """
        start_time = datetime.now()

        try:
            logger.info(f"Starting orchestration of {len(service_configs)} services")

            self._setup_services(service_configs, dependencies)
            self._validate_dependencies()
            execution_plan = self._create_execution_plan()

            services_started, services_failed = await self._execute_plan(execution_plan)

            if self.config.enable_monitoring and services_started:
                await self._start_monitoring()

            return self._create_orchestration_result(
                start_time, services_started, services_failed, len(service_configs),
            )

        except Exception as e:
            return self._create_error_result(start_time, e)

    def _setup_services(
        self, service_configs: list[Any], dependencies: dict[str, list[str]] | None,
    ) -> None:
        """
        Setup services and their dependencies.
        """
        for service_config in service_configs:
            service_name = getattr(service_config, "name", f"service_{len(self.services)}")
            service_deps = dependencies.get(service_name, []) if dependencies else []
            self.add_service(service_name, service_config, service_deps)

    async def _execute_plan(self, execution_plan: list[list[str]]) -> tuple[list[str], list[str]]:
        """
        Execute the orchestration plan.
        """
        services_started = []
        services_failed = []

        for batch in execution_plan:
            if self._shutdown_requested:
                break

            batch_results = await self._execute_batch(batch)
            self._process_batch_results(batch_results, services_started, services_failed)

        return services_started, services_failed

    async def _execute_batch(self, batch: list[str]) -> dict[str, bool]:
        """
        Execute a batch of services based on configuration mode.
        """
        if self.config.mode == OrchestrationMode.PARALLEL:
            return await self._execute_batch_parallel(batch)
        return await self._execute_batch_sequential(batch)

    def _process_batch_results(
        self,
        batch_results: dict[str, bool],
        services_started: list[str],
        services_failed: list[str],
    ) -> None:
        """
        Process results from a batch execution.
        """
        for service_name, success in batch_results.items():
            if success:
                services_started.append(service_name)
                self.service_status[service_name] = "running"
            else:
                services_failed.append(service_name)
                self.service_status[service_name] = "failed"

    def _create_orchestration_result(
        self,
        start_time: datetime,
        services_started: list[str],
        services_failed: list[str],
        total_services: int,
    ) -> OrchestrationResult:
        """
        Create the final orchestration result.
        """
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        success = len(services_failed) == 0
        status = OrchestrationStatus.COMPLETED if success else OrchestrationStatus.FAILED

        result = OrchestrationResult(
            success=success,
            status=status,
            services_started=services_started,
            services_failed=services_failed,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "mode": self.config.mode.value,
                "total_services": total_services,
                "monitoring_enabled": self.config.enable_monitoring,
            },
        )

        logger.info(
            f"Orchestration completed: {len(services_started)} started, "
            f"{len(services_failed)} failed in {duration:.2f}s",
        )

        return result

    def _create_error_result(self, start_time: datetime, error: Exception) -> OrchestrationResult:
        """
        Create an error result for failed orchestration.
        """
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.error(f"Orchestration failed: {error}")

        return OrchestrationResult(
            success=False,
            status=OrchestrationStatus.FAILED,
            services_started=[],
            services_failed=list(self.services.keys()),
            duration=duration,
            start_time=start_time,
            end_time=end_time,
            error_message=str(error),
        )

    def _validate_dependencies(self) -> None:
        """
        Validate that all dependencies exist.
        """
        for service_name, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.services:
                    raise ValueError(f"Service '{service_name}' depends on unknown service '{dep}'")

    def _create_execution_plan(self) -> list[list[str]]:
        """
        Create execution plan based on dependencies and mode.
        """
        if self.config.mode == OrchestrationMode.SEQUENTIAL:
            return self._create_sequential_plan()
        if self.config.mode == OrchestrationMode.PARALLEL:
            return self._create_parallel_plan()
        # DEPENDENCY_ORDERED
        return self._create_dependency_ordered_plan()

    def _create_sequential_plan(self) -> list[list[str]]:
        """
        Create sequential execution plan.
        """
        return [[name] for name in self.services]

    def _create_parallel_plan(self) -> list[list[str]]:
        """
        Create parallel execution plan (all services at once).
        """
        return [list(self.services.keys())]

    def _create_dependency_ordered_plan(self) -> list[list[str]]:
        """
        Create dependency-ordered execution plan.
        """
        plan = []
        remaining = set(self.services.keys())
        completed = set()

        while remaining:
            # Find services with no pending dependencies
            ready = []
            for service in remaining:
                deps = self.dependencies.get(service, [])
                if all(dep in completed for dep in deps):
                    ready.append(service)

            if not ready:
                # Circular dependency or missing dependency
                raise ValueError(f"Cannot resolve dependencies for services: {remaining}")

            # Add ready services to current batch
            batch = ready[: self.config.parallel_limit]  # Respect parallel limit
            plan.append(batch)

            # Update state
            completed.update(batch)
            remaining -= set(batch)

        return plan

    async def _execute_batch_sequential(self, batch: list[str]) -> dict[str, bool]:
        """
        Execute services in batch sequentially.
        """
        results = {}

        for service_name in batch:
            if self._shutdown_requested:
                break

            logger.info(f"Starting service: {service_name}")
            success = await self._start_service(service_name)
            results[service_name] = success

            if not success and not self.config.enable_auto_recovery:
                logger.error(f"Service '{service_name}' failed, stopping orchestration")
                break

        return results

    async def _execute_batch_parallel(self, batch: list[str]) -> dict[str, bool]:
        """
        Execute services in batch in parallel.
        """
        logger.info(f"Starting {len(batch)} services in parallel")

        tasks = []
        for service_name in batch:
            task = asyncio.create_task(self._start_service(service_name))
            tasks.append((service_name, task))

        results = {}
        for service_name, task in tasks:
            try:
                success = await task
                results[service_name] = success
            except Exception as e:
                logger.exception(f"Service '{service_name}' failed: {e}")
                results[service_name] = False

        return results

    async def _start_service(self, service_name: str) -> bool:
        """
        Start a single service.
        """
        try:
            self.services[service_name]
            self.service_status[service_name] = "starting"

            # Simulate service startup (replace with actual implementation)
            await asyncio.sleep(1)

            self.service_status[service_name] = "running"
            logger.info(f"Service '{service_name}' started successfully")
            return True

        except Exception as e:
            logger.exception(f"Failed to start service '{service_name}': {e}")
            self.service_status[service_name] = "failed"
            return False

    async def _start_monitoring(self) -> None:
        """
        Start health monitoring for all services.
        """
        for service_name in self.services:
            if self.service_status[service_name] == "running":
                task = asyncio.create_task(self._monitor_service(service_name))
                self.monitoring_tasks.append(task)

    async def _monitor_service(self, service_name: str) -> None:
        """
        Monitor a single service.
        """
        restart_count = 0

        while not self._shutdown_requested:
            try:
                # Check service health
                healthy = await self._check_service_health(service_name)

                if not healthy and self.config.enable_auto_recovery:
                    if restart_count < self.config.max_restart_attempts:
                        logger.warning(f"Service '{service_name}' unhealthy, restarting...")
                        await self._restart_service(service_name)
                        restart_count += 1
                        await asyncio.sleep(self.config.restart_delay)
                    else:
                        logger.error(
                            f"Service '{service_name}' failed after {restart_count} restart attempts",
                        )
                        self.service_status[service_name] = "failed"
                        break

                await asyncio.sleep(self.config.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Monitoring error for service '{service_name}': {e}")
                await asyncio.sleep(30)

    async def _check_service_health(self, service_name: str) -> bool:
        """
        Check health of a service.
        """
        # Simulate health check (replace with actual implementation)
        return self.service_status[service_name] == "running"

    async def _restart_service(self, service_name: str) -> bool:
        """
        Restart a service.
        """
        logger.info(f"Restarting service: {service_name}")
        self.service_status[service_name] = "restarting"

        # Stop service
        await self._stop_service(service_name)

        # Wait a bit
        await asyncio.sleep(2)

        # Start service
        return await self._start_service(service_name)

    async def _stop_service(self, service_name: str) -> None:
        """
        Stop a service.
        """
        logger.info(f"Stopping service: {service_name}")
        self.service_status[service_name] = "stopping"

        # Simulate service stop (replace with actual implementation)
        await asyncio.sleep(0.5)

        self.service_status[service_name] = "stopped"

    async def stop_all(self) -> None:
        """
        Stop all services and monitoring.
        """
        logger.info("Stopping all services...")

        self._shutdown_requested = True

        # Stop monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()

        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()

        # Stop all services
        for service_name in self.services:
            await self._stop_service(service_name)

        logger.info("All services stopped")

    def get_status(self) -> dict[str, Any]:
        """
        Get current orchestration status.
        """
        return {
            "project_name": self.config.project_name,
            "mode": self.config.mode.value,
            "services": dict(self.service_status),
            "dependencies": dict(self.dependencies),
            "monitoring_enabled": self.config.enable_monitoring,
            "auto_recovery_enabled": self.config.enable_auto_recovery,
        }
