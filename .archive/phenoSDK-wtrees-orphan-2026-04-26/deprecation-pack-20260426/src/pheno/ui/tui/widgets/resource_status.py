"""
ResourceStatusWidget Enhanced - Protocol-based resource monitoring with comprehensive metrics - Refactored Version

This is a production-ready, full-featured resource monitoring widget that provides:
- System resource monitoring (CPU, memory, disk I/O, network bandwidth)
- Database monitoring with connection pool stats and query latency
- Threshold-based alerts with color-coded indicators
- Historical trend tracking with sparkline visualization
- TaskMetrics integration for unified progress tracking
- Protocol-based design for flexible provider integration

Example Usage:
    # Basic system monitoring
    widget = ResourceStatusWidget(
        enable_system_monitoring=True,
        enable_sparklines=True
    )

    # With database monitoring
    class MyDatabaseProvider:
        async def get_pool_stats(self):
            return {"active": 5, "idle": 10, "total": 15}

        async def get_query_latency(self):
            return 12.5  # milliseconds

        async def check_health(self):
            return True

    widget = ResourceStatusWidget(
        database_provider=MyDatabaseProvider(),
        enable_system_monitoring=True
    )

    # With custom thresholds
    widget = ResourceStatusWidget()
    widget.set_thresholds("cpu", warning=60.0, critical=85.0)
    widget.set_thresholds("memory", warning=70.0, critical=90.0)

    # Export metrics to TaskMetrics
    task_metrics = widget.export_task_metrics()
    progress_widget.update("monitor", metrics=task_metrics)
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

import psutil
from textual.reactive import reactive
from textual.widgets import Static

# Import our refactored modules
from .resource_monitoring.monitoring_protocols import DatabaseProvider, ResourceMonitor

# Re-export key classes for backward compatibility
__all__ = [
    "DatabaseProvider",
    "DefaultResourceMonitor",
    "ResourceMetric",
    "ResourceMonitor",
    "ResourceStatusWidget",
]


@dataclass
class ResourceMetric:
    """
    Represents a single resource metric with timestamp and value.
    """

    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    unit: str = ""
    threshold_warning: float | None = None
    threshold_critical: float | None = None

    @property
    def status(self) -> str:
        """
        Get status based on thresholds.
        """
        if self.threshold_critical and self.value >= self.threshold_critical:
            return "critical"
        if self.threshold_warning and self.value >= self.threshold_warning:
            return "warning"
        return "normal"

    @property
    def status_color(self) -> str:
        """
        Get color for status.
        """
        status_colors = {
            "normal": "green",
            "warning": "yellow",
            "critical": "red",
        }
        return status_colors.get(self.status, "white")


class DefaultResourceMonitor:
    """
    Default system resource monitor using psutil.
    """

    def __init__(self):
        self._cpu_history = deque(maxlen=60)  # 1 minute of data
        self._memory_history = deque(maxlen=60)
        self._disk_history = deque(maxlen=60)
        self._network_history = deque(maxlen=60)

    async def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.
        """
        return psutil.cpu_percent(interval=0.1)

    async def get_memory_usage(self) -> dict[str, float]:
        """
        Get memory usage statistics.
        """
        memory = psutil.virtual_memory()
        return {
            "used_mb": memory.used / 1024 / 1024,
            "percent": memory.percent,
            "available_mb": memory.available / 1024 / 1024,
            "total_mb": memory.total / 1024 / 1024,
        }

    async def get_disk_usage(self) -> float:
        """
        Get disk usage percentage.
        """
        return psutil.disk_usage("/").percent

    async def get_network_bandwidth(self) -> dict[str, float]:
        """
        Get network bandwidth statistics.
        """
        net_io = psutil.net_io_counters()
        return {
            "upload_kbps": net_io.bytes_sent / 1024,
            "download_kbps": net_io.bytes_recv / 1024,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

    def get_historical_data(self, metric_name: str) -> list[float]:
        """
        Get historical data for a metric.
        """
        history_map = {
            "cpu": self._cpu_history,
            "memory": self._memory_history,
            "disk": self._disk_history,
            "network": self._network_history,
        }
        return list(history_map.get(metric_name, []))


class ResourceStatusWidget(Static):
    """Enhanced resource monitoring widget with comprehensive metrics.

    Features:
    - System resource monitoring (CPU, memory, disk, network)
    - Database monitoring with connection pool stats
    - Threshold-based alerts with color coding
    - Historical trend tracking with sparklines
    - TaskMetrics integration
    - Protocol-based design for custom providers
    """

    # Reactive attributes
    cpu_usage = reactive(0.0)
    memory_usage = reactive(0.0)
    disk_usage = reactive(0.0)
    network_upload = reactive(0.0)
    network_download = reactive(0.0)
    database_healthy = reactive(True)
    database_latency = reactive(0.0)
    database_pool_active = reactive(0)
    database_pool_idle = reactive(0)

    def __init__(
        self,
        resource_monitor: ResourceMonitor | None = None,
        database_provider: DatabaseProvider | None = None,
        enable_system_monitoring: bool = True,
        enable_database_monitoring: bool = False,
        enable_sparklines: bool = True,
        update_interval: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.resource_monitor = resource_monitor or DefaultResourceMonitor()
        self.database_provider = database_provider
        self.enable_system_monitoring = enable_system_monitoring
        self.enable_database_monitoring = enable_database_monitoring
        self.enable_sparklines = enable_sparklines
        self.update_interval = update_interval

        # Thresholds for alerts
        self.thresholds = {
            "cpu": {"warning": 70.0, "critical": 90.0},
            "memory": {"warning": 80.0, "critical": 95.0},
            "disk": {"warning": 85.0, "critical": 95.0},
            "database_latency": {"warning": 100.0, "critical": 500.0},
        }

        # Historical data for sparklines
        self.historical_data = {
            "cpu": deque(maxlen=60),
            "memory": deque(maxlen=60),
            "disk": deque(maxlen=60),
            "network": deque(maxlen=60),
        }

        # Task metrics integration
        self.task_metrics = {}

    def set_thresholds(self, metric: str, warning: float, critical: float):
        """
        Set thresholds for a metric.
        """
        if metric not in self.thresholds:
            self.thresholds[metric] = {}
        self.thresholds[metric]["warning"] = warning
        self.thresholds[metric]["critical"] = critical

    def get_metric_status(self, metric: str, value: float) -> str:
        """
        Get status for a metric based on thresholds.
        """
        if metric not in self.thresholds:
            return "normal"

        thresholds = self.thresholds[metric]
        if value >= thresholds.get("critical", float("inf")):
            return "critical"
        if value >= thresholds.get("warning", float("inf")):
            return "warning"
        return "normal"

    def get_status_color(self, status: str) -> str:
        """
        Get color for status.
        """
        status_colors = {
            "normal": "green",
            "warning": "yellow",
            "critical": "red",
        }
        return status_colors.get(status, "white")

    def generate_sparkline(self, data: list[float], width: int = 20) -> str:
        """
        Generate ASCII sparkline from data.
        """
        if not data:
            return " " * width

        min_val = min(data)
        max_val = max(data)

        if max_val == min_val:
            return "─" * width

        # Normalize data to 0-1 range
        normalized = [(val - min_val) / (max_val - min_val) for val in data]

        # Map to sparkline characters
        spark_chars = "▁▂▃▄▅▆▇█"
        sparkline = ""

        for val in normalized:
            char_index = int(val * (len(spark_chars) - 1))
            sparkline += spark_chars[char_index]

        return sparkline

    async def update_metrics(self):
        """
        Update all metrics.
        """
        if self.enable_system_monitoring:
            await self._update_system_metrics()

        if self.enable_database_monitoring and self.database_provider:
            await self._update_database_metrics()

        self._update_historical_data()
        self._update_task_metrics()

    async def _update_system_metrics(self):
        """
        Update system resource metrics.
        """
        try:
            self.cpu_usage = await self.resource_monitor.get_cpu_usage()
            memory_stats = await self.resource_monitor.get_memory_usage()
            self.memory_usage = memory_stats.get("percent", 0.0)
            self.disk_usage = await self.resource_monitor.get_disk_usage()

            network_stats = await self.resource_monitor.get_network_bandwidth()
            self.network_upload = network_stats.get("upload_kbps", 0.0)
            self.network_download = network_stats.get("download_kbps", 0.0)
        except Exception:
            # Handle monitoring errors gracefully
            pass

    async def _update_database_metrics(self):
        """
        Update database metrics.
        """
        try:
            self.database_healthy = await self.database_provider.check_health()
            self.database_latency = await self.database_provider.get_query_latency()

            pool_stats = await self.database_provider.get_pool_stats()
            self.database_pool_active = pool_stats.get("active", 0)
            self.database_pool_idle = pool_stats.get("idle", 0)
        except Exception:
            self.database_healthy = False

    def _update_historical_data(self):
        """
        Update historical data for sparklines.
        """
        if self.enable_sparklines:
            self.historical_data["cpu"].append(self.cpu_usage)
            self.historical_data["memory"].append(self.memory_usage)
            self.historical_data["disk"].append(self.disk_usage)
            self.historical_data["network"].append(self.network_upload)

    def _update_task_metrics(self):
        """
        Update task metrics for integration.
        """
        self.task_metrics = {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_upload": self.network_upload,
            "network_download": self.network_download,
            "database_healthy": self.database_healthy,
            "database_latency": self.database_latency,
            "database_pool_active": self.database_pool_active,
            "database_pool_idle": self.database_pool_idle,
        }

    def export_task_metrics(self) -> dict[str, Any]:
        """
        Export metrics for TaskMetrics integration.
        """
        return self.task_metrics.copy()

    def render(self) -> str:
        """
        Render the resource status widget.
        """
        lines = []

        # System metrics
        if self.enable_system_monitoring:
            lines.append("[bold]System Resources[/bold]")

            # CPU
            cpu_status = self.get_metric_status("cpu", self.cpu_usage)
            cpu_color = self.get_status_color(cpu_status)
            cpu_sparkline = ""
            if self.enable_sparklines and self.historical_data["cpu"]:
                cpu_sparkline = f" {self.generate_sparkline(list(self.historical_data['cpu']))}"
            lines.append(f"CPU: [{cpu_color}]{self.cpu_usage:.1f}%[/{cpu_color}]{cpu_sparkline}")

            # Memory
            memory_status = self.get_metric_status("memory", self.memory_usage)
            memory_color = self.get_status_color(memory_status)
            memory_sparkline = ""
            if self.enable_sparklines and self.historical_data["memory"]:
                memory_sparkline = (
                    f" {self.generate_sparkline(list(self.historical_data['memory']))}"
                )
            lines.append(
                f"Memory: [{memory_color}]{self.memory_usage:.1f}%[/{memory_color}]{memory_sparkline}",
            )

            # Disk
            disk_status = self.get_metric_status("disk", self.disk_usage)
            disk_color = self.get_status_color(disk_status)
            disk_sparkline = ""
            if self.enable_sparklines and self.historical_data["disk"]:
                disk_sparkline = f" {self.generate_sparkline(list(self.historical_data['disk']))}"
            lines.append(
                f"Disk: [{disk_color}]{self.disk_usage:.1f}%[/{disk_color}]{disk_sparkline}",
            )

            # Network
            network_sparkline = ""
            if self.enable_sparklines and self.historical_data["network"]:
                network_sparkline = (
                    f" {self.generate_sparkline(list(self.historical_data['network']))}"
                )
            lines.append(
                f"Network: ↑{self.network_upload:.1f}KB/s ↓{self.network_download:.1f}KB/s{network_sparkline}",
            )

        # Database metrics
        if self.enable_database_monitoring and self.database_provider:
            lines.append("\n[bold]Database[/bold]")

            # Health status
            health_color = "green" if self.database_healthy else "red"
            health_icon = "✅" if self.database_healthy else "❌"
            lines.append(
                f"Health: {health_icon} [{health_color}]{'Healthy' if self.database_healthy else 'Unhealthy'}[/{health_color}]",
            )

            # Latency
            latency_status = self.get_metric_status("database_latency", self.database_latency)
            latency_color = self.get_status_color(latency_status)
            lines.append(
                f"Latency: [{latency_color}]{self.database_latency:.1f}ms[/{latency_color}]",
            )

            # Pool stats
            lines.append(
                f"Pool: {self.database_pool_active} active, {self.database_pool_idle} idle",
            )

        return "\n".join(lines)

    async def on_mount(self):
        """
        Start monitoring when widget is mounted.
        """
        if self.enable_system_monitoring or self.enable_database_monitoring:
            self.set_interval(self.update_interval, self.update_metrics)
            await self.update_metrics()
