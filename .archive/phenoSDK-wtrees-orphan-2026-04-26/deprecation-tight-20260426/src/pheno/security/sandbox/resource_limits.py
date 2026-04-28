"""
Resource limits and monitoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psutil

from pheno.logging.core.logger import get_logger

logger = get_logger("pheno.security.sandbox.resource_limits")


@dataclass(slots=True)
class ResourceLimitConfig:
    """
    Configuration for resource limits.
    """

    max_memory_mb: int = 512
    max_cpu_percent: float = 50.0
    max_file_descriptors: int = 100
    max_processes: int = 10
    max_disk_usage_mb: int = 100


class ResourceExhaustedError(Exception):
    """
    Raised when resource limits are exceeded.
    """



class ResourceLimits:
    """
    Resource limits enforcement.
    """

    def __init__(self, config: ResourceLimitConfig | None = None):
        self.config = config or ResourceLimitConfig()
        self._process = psutil.Process()

    def check_memory_limit(self) -> bool:
        """
        Check if memory usage is within limits.
        """
        memory_info = self._process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        return memory_mb <= self.config.max_memory_mb

    def check_cpu_limit(self) -> bool:
        """
        Check if CPU usage is within limits.
        """
        cpu_percent = self._process.cpu_percent()
        return cpu_percent <= self.config.max_cpu_percent

    def check_file_descriptors(self) -> bool:
        """
        Check if file descriptor count is within limits.
        """
        try:
            fd_count = self._process.num_fds()
            return fd_count <= self.config.max_file_descriptors
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True

    def check_process_count(self) -> bool:
        """
        Check if process count is within limits.
        """
        try:
            children = self._process.children(recursive=True)
            return len(children) <= self.config.max_processes
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True

    def check_disk_usage(self, path: str) -> bool:
        """
        Check if disk usage is within limits.
        """
        try:
            disk_usage = psutil.disk_usage(path)
            usage_mb = disk_usage.used / 1024 / 1024
            return usage_mb <= self.config.max_disk_usage_mb
        except (OSError, psutil.AccessDenied):
            return True

    def enforce_limits(self) -> None:
        """
        Enforce all resource limits.
        """
        if not self.check_memory_limit():
            raise ResourceExhaustedError("Memory limit exceeded")

        if not self.check_cpu_limit():
            raise ResourceExhaustedError("CPU limit exceeded")

        if not self.check_file_descriptors():
            raise ResourceExhaustedError("File descriptor limit exceeded")

        if not self.check_process_count():
            raise ResourceExhaustedError("Process count limit exceeded")


class ResourceMonitor:
    """
    Monitors resource usage.
    """

    def __init__(self, config: ResourceLimitConfig | None = None):
        self.config = config or ResourceLimitConfig()
        self.limits = ResourceLimits(config)
        self._process = psutil.Process()

    def get_memory_usage(self) -> dict[str, float]:
        """
        Get memory usage information.
        """
        memory_info = self._process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": self._process.memory_percent(),
            "limit_mb": self.config.max_memory_mb,
        }

    def get_cpu_usage(self) -> dict[str, float]:
        """
        Get CPU usage information.
        """
        return {
            "percent": self._process.cpu_percent(),
            "limit_percent": self.config.max_cpu_percent,
        }

    def get_file_descriptor_count(self) -> dict[str, int]:
        """
        Get file descriptor information.
        """
        try:
            fd_count = self._process.num_fds()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            fd_count = 0

        return {"count": fd_count, "limit": self.config.max_file_descriptors}

    def get_process_count(self) -> dict[str, int]:
        """
        Get process count information.
        """
        try:
            children = self._process.children(recursive=True)
            process_count = len(children)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process_count = 0

        return {"count": process_count, "limit": self.config.max_processes}

    def get_disk_usage(self, path: str) -> dict[str, float]:
        """
        Get disk usage information.
        """
        try:
            disk_usage = psutil.disk_usage(path)
            usage_mb = disk_usage.used / 1024 / 1024
        except (OSError, psutil.AccessDenied):
            usage_mb = 0

        return {"used_mb": usage_mb, "limit_mb": self.config.max_disk_usage_mb}

    def get_all_metrics(self) -> dict[str, Any]:
        """
        Get all resource metrics.
        """
        return {
            "memory": self.get_memory_usage(),
            "cpu": self.get_cpu_usage(),
            "file_descriptors": self.get_file_descriptor_count(),
            "processes": self.get_process_count(),
        }
