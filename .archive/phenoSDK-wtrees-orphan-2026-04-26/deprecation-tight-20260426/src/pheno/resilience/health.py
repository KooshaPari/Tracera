"""
Health checking and monitoring utilities.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from pheno.logging.core.logger import get_logger

logger = get_logger("pheno.resilience.health")


class HealthStatus(Enum):
    """
    Health status levels.
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class HealthCheck:
    """
    Represents a health check.
    """

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = None
    timestamp: datetime = None
    response_time: float = 0.0

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass(slots=True)
class HealthConfig:
    """
    Configuration for health monitoring.
    """

    check_interval: float = 30.0  # seconds
    timeout: float = 5.0  # seconds
    retry_count: int = 3
    enable_monitoring: bool = True


class HealthChecker(ABC):
    """
    Abstract base class for health checkers.
    """

    @abstractmethod
    async def check_health(self) -> HealthCheck:
        """
        Perform health check.
        """


class HealthMonitor:
    """
    Monitors health of various components.
    """

    def __init__(self, config: HealthConfig | None = None):
        self.config = config or HealthConfig()
        self._checkers: dict[str, HealthChecker] = {}
        self._monitoring_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()
        self._last_checks: dict[str, HealthCheck] = {}

    def add_checker(self, name: str, checker: HealthChecker) -> None:
        """
        Add health checker.
        """
        self._checkers[name] = checker
        logger.info(f"Added health checker '{name}'")

    def remove_checker(self, name: str) -> bool:
        """
        Remove health checker.
        """
        if name in self._checkers:
            del self._checkers[name]
            logger.info(f"Removed health checker '{name}'")
            return True
        return False

    async def check_all(self) -> dict[str, HealthCheck]:
        """
        Check health of all components.
        """
        results = {}

        for name, checker in self._checkers.items():
            try:
                start_time = time.time()
                health_check = await asyncio.wait_for(
                    checker.check_health(), timeout=self.config.timeout,
                )
                health_check.response_time = time.time() - start_time
                results[name] = health_check
                self._last_checks[name] = health_check

            except TimeoutError:
                logger.warning(f"Health check '{name}' timed out")
                results[name] = HealthCheck(
                    name=name, status=HealthStatus.UNHEALTHY, message="Health check timed out",
                )

            except Exception as e:
                logger.exception(f"Health check '{name}' failed: {e}")
                results[name] = HealthCheck(
                    name=name, status=HealthStatus.UNHEALTHY, message=f"Health check failed: {e}",
                )

        return results

    async def get_overall_health(self) -> HealthStatus:
        """
        Get overall health status.
        """
        checks = await self.check_all()

        if not checks:
            return HealthStatus.UNKNOWN

        statuses = [check.status for check in checks.values()]

        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        if any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED

    async def start_monitoring(self) -> None:
        """
        Start health monitoring.
        """
        if not self.config.enable_monitoring or self._monitoring_task is not None:
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started health monitoring")

    async def stop_monitoring(self) -> None:
        """
        Stop health monitoring.
        """
        if self._monitoring_task is None:
            return

        self._shutdown_event.set()
        self._monitoring_task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await self._monitoring_task

        self._monitoring_task = None
        logger.info("Stopped health monitoring")

    async def _monitoring_loop(self) -> None:
        """
        Health monitoring loop.
        """
        while not self._shutdown_event.is_set():
            try:
                checks = await self.check_all()
                overall_health = await self.get_overall_health()

                logger.debug(f"Health check results: {overall_health.value}")

                # Log unhealthy components
                for name, check in checks.items():
                    if check.status != HealthStatus.HEALTHY:
                        logger.warning(
                            f"Component '{name}' is {check.status.value}: {check.message}",
                        )

                await asyncio.sleep(self.config.check_interval)

            except Exception as e:
                logger.exception(f"Error in health monitoring: {e}")
                await asyncio.sleep(5.0)
