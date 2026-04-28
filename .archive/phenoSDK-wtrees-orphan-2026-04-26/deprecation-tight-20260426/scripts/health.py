#!/usr/bin/env python3
"""
Unified Health Monitoring Tool for Pheno-SDK

This tool provides comprehensive health monitoring for:
- Pheno-SDK overall health
- Individual kit health
- Atlas health monitoring
- Performance metrics

Usage:
    python scripts/health.py [command] [options]

Commands:
    dashboard     Show health dashboard
    kit           Monitor individual kit health
    atlas         Monitor Atlas health
    performance   Monitor performance metrics
    all           Run all health checks

Options:
    --project PROJECT    Target project (pheno, kit, atlas, all)
    --verbose           Verbose output
    --json              Output results as JSON
    --live              Live monitoring mode
"""

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

console = Console()
app = typer.Typer(help="Unified Health Monitoring Tool for Pheno-SDK")

# Add src to path
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@dataclass
class HealthMetric:
    """Health metric data structure."""

    name: str
    value: float
    unit: str
    timestamp: float
    status: str  # "healthy", "warning", "critical", "unknown"
    threshold: float | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "status": self.status,
            "threshold": self.threshold,
            "description": self.description,
        }


@dataclass
class HealthResult:
    """Health check result."""

    component: str
    status: str
    metrics: list[HealthMetric]
    summary: dict[str, Any]
    timestamp: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "metrics": [m.to_dict() for m in self.metrics],
            "summary": self.summary,
            "timestamp": self.timestamp,
        }


class PhenoSDKHealthMonitor:
    """Pheno-SDK overall health monitoring."""

    def __init__(self):
        self.name = "Pheno-SDK"

    def check_health(self) -> HealthResult:
        """Check overall Pheno-SDK health."""
        metrics = []

        # Check memory usage
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_metric = HealthMetric(
                name="Memory Usage",
                value=memory.percent,
                unit="%",
                timestamp=time.time(),
                status="healthy"
                if memory.percent < 80
                else "warning"
                if memory.percent < 90
                else "critical",
                threshold=80.0,
                description="System memory usage",
            )
            metrics.append(memory_metric)
        except ImportError:
            metrics.append(
                HealthMetric(
                    name="Memory Usage",
                    value=0.0,
                    unit="%",
                    timestamp=time.time(),
                    status="unknown",
                    description="psutil not available",
                ),
            )

        # Check CPU usage
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=1)
            cpu_metric = HealthMetric(
                name="CPU Usage",
                value=cpu,
                unit="%",
                timestamp=time.time(),
                status="healthy" if cpu < 70 else "warning" if cpu < 85 else "critical",
                threshold=70.0,
                description="System CPU usage",
            )
            metrics.append(cpu_metric)
        except ImportError:
            metrics.append(
                HealthMetric(
                    name="CPU Usage",
                    value=0.0,
                    unit="%",
                    timestamp=time.time(),
                    status="unknown",
                    description="psutil not available",
                ),
            )

        # Check disk usage
        try:
            import psutil

            disk = psutil.disk_usage("/")
            disk_metric = HealthMetric(
                name="Disk Usage",
                value=(disk.used / disk.total) * 100,
                unit="%",
                timestamp=time.time(),
                status="healthy"
                if (disk.used / disk.total) < 80
                else "warning"
                if (disk.used / disk.total) < 90
                else "critical",
                threshold=80.0,
                description="Disk usage",
            )
            metrics.append(disk_metric)
        except ImportError:
            metrics.append(
                HealthMetric(
                    name="Disk Usage",
                    value=0.0,
                    unit="%",
                    timestamp=time.time(),
                    status="unknown",
                    description="psutil not available",
                ),
            )

        # Determine overall status
        statuses = [m.status for m in metrics if m.status != "unknown"]
        if not statuses:
            overall_status = "unknown"
        elif "critical" in statuses:
            overall_status = "critical"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return HealthResult(
            component=self.name,
            status=overall_status,
            metrics=metrics,
            summary={
                "total_metrics": len(metrics),
                "healthy_count": len([m for m in metrics if m.status == "healthy"]),
                "warning_count": len([m for m in metrics if m.status == "warning"]),
                "critical_count": len([m for m in metrics if m.status == "critical"]),
                "unknown_count": len([m for m in metrics if m.status == "unknown"]),
            },
            timestamp=time.time(),
        )


class KitHealthMonitor:
    """Individual kit health monitoring."""

    def __init__(self, kit_name: str):
        self.kit_name = kit_name

    def check_health(self) -> HealthResult:
        """Check kit health."""
        metrics = []

        # Simulate kit-specific health checks
        # In a real implementation, this would check actual kit metrics

        # Check kit availability
        availability_metric = HealthMetric(
            name="Availability",
            value=95.0,  # Simulated
            unit="%",
            timestamp=time.time(),
            status="healthy",
            threshold=90.0,
            description="Kit availability percentage",
        )
        metrics.append(availability_metric)

        # Check response time
        response_time_metric = HealthMetric(
            name="Response Time",
            value=150.0,  # Simulated
            unit="ms",
            timestamp=time.time(),
            status="healthy",
            threshold=200.0,
            description="Average response time",
        )
        metrics.append(response_time_metric)

        # Check error rate
        error_rate_metric = HealthMetric(
            name="Error Rate",
            value=0.5,  # Simulated
            unit="%",
            timestamp=time.time(),
            status="healthy",
            threshold=1.0,
            description="Error rate percentage",
        )
        metrics.append(error_rate_metric)

        # Determine overall status
        statuses = [m.status for m in metrics]
        if "critical" in statuses:
            overall_status = "critical"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return HealthResult(
            component=f"Kit: {self.kit_name}",
            status=overall_status,
            metrics=metrics,
            summary={
                "kit_name": self.kit_name,
                "total_metrics": len(metrics),
                "healthy_count": len([m for m in metrics if m.status == "healthy"]),
                "warning_count": len([m for m in metrics if m.status == "warning"]),
                "critical_count": len([m for m in metrics if m.status == "critical"]),
            },
            timestamp=time.time(),
        )


class AtlasHealthMonitor:
    """Atlas health monitoring."""

    def __init__(self, project: str = "atlas"):
        self.project = project

    def check_health(self) -> HealthResult:
        """Check Atlas health."""
        metrics = []

        # Simulate Atlas-specific health checks
        # In a real implementation, this would check actual Atlas metrics

        # Check Atlas service status
        service_metric = HealthMetric(
            name="Service Status",
            value=100.0,  # Simulated
            unit="%",
            timestamp=time.time(),
            status="healthy",
            threshold=95.0,
            description="Atlas service availability",
        )
        metrics.append(service_metric)

        # Check data consistency
        consistency_metric = HealthMetric(
            name="Data Consistency",
            value=98.5,  # Simulated
            unit="%",
            timestamp=time.time(),
            status="healthy",
            threshold=95.0,
            description="Data consistency percentage",
        )
        metrics.append(consistency_metric)

        # Check replication lag
        replication_metric = HealthMetric(
            name="Replication Lag",
            value=50.0,  # Simulated
            unit="ms",
            timestamp=time.time(),
            status="healthy",
            threshold=100.0,
            description="Replication lag in milliseconds",
        )
        metrics.append(replication_metric)

        # Determine overall status
        statuses = [m.status for m in metrics]
        if "critical" in statuses:
            overall_status = "critical"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return HealthResult(
            component=f"Atlas: {self.project}",
            status=overall_status,
            metrics=metrics,
            summary={
                "project": self.project,
                "total_metrics": len(metrics),
                "healthy_count": len([m for m in metrics if m.status == "healthy"]),
                "warning_count": len([m for m in metrics if m.status == "warning"]),
                "critical_count": len([m for m in metrics if m.status == "critical"]),
            },
            timestamp=time.time(),
        )


class PerformanceMonitor:
    """Performance metrics monitoring."""

    def __init__(self):
        self.name = "Performance"

    def check_health(self) -> HealthResult:
        """Check performance metrics."""
        metrics = []

        # Simulate performance metrics
        # In a real implementation, this would check actual performance data

        # Check throughput
        throughput_metric = HealthMetric(
            name="Throughput",
            value=1000.0,  # Simulated
            unit="req/s",
            timestamp=time.time(),
            status="healthy",
            threshold=800.0,
            description="Requests per second",
        )
        metrics.append(throughput_metric)

        # Check latency
        latency_metric = HealthMetric(
            name="Latency",
            value=120.0,  # Simulated
            unit="ms",
            timestamp=time.time(),
            status="healthy",
            threshold=200.0,
            description="Average latency",
        )
        metrics.append(latency_metric)

        # Check queue depth
        queue_metric = HealthMetric(
            name="Queue Depth",
            value=5.0,  # Simulated
            unit="items",
            timestamp=time.time(),
            status="healthy",
            threshold=10.0,
            description="Queue depth",
        )
        metrics.append(queue_metric)

        # Determine overall status
        statuses = [m.status for m in metrics]
        if "critical" in statuses:
            overall_status = "critical"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return HealthResult(
            component=self.name,
            status=overall_status,
            metrics=metrics,
            summary={
                "total_metrics": len(metrics),
                "healthy_count": len([m for m in metrics if m.status == "healthy"]),
                "warning_count": len([m for m in metrics if m.status == "warning"]),
                "critical_count": len([m for m in metrics if m.status == "critical"]),
            },
            timestamp=time.time(),
        )


def display_health_dashboard(results: list[HealthResult]):
    """Display health dashboard."""
    layout = Layout()

    # Create header
    header = Panel(
        f"[bold blue]Pheno-SDK Health Dashboard[/bold blue]\n"
        f"[dim]Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        style="blue",
    )

    # Create summary table
    summary_table = Table(title="Health Summary")
    summary_table.add_column("Component", style="cyan")
    summary_table.add_column("Status", style="green")
    summary_table.add_column("Metrics", style="yellow")
    summary_table.add_column("Healthy", style="green")
    summary_table.add_column("Warning", style="yellow")
    summary_table.add_column("Critical", style="red")

    for result in results:
        status_style = {
            "healthy": "green",
            "warning": "yellow",
            "critical": "red",
            "unknown": "dim",
        }.get(result.status, "white")

        summary_table.add_row(
            result.component,
            f"[{status_style}]{result.status}[/{status_style}]",
            str(result.summary.get("total_metrics", 0)),
            str(result.summary.get("healthy_count", 0)),
            str(result.summary.get("warning_count", 0)),
            str(result.summary.get("critical_count", 0)),
        )

    # Create metrics table
    metrics_table = Table(title="Detailed Metrics")
    metrics_table.add_column("Component", style="cyan")
    metrics_table.add_column("Metric", style="white")
    metrics_table.add_column("Value", style="green")
    metrics_table.add_column("Unit", style="dim")
    metrics_table.add_column("Status", style="green")
    metrics_table.add_column("Threshold", style="dim")

    for result in results:
        for metric in result.metrics:
            status_style = {
                "healthy": "green",
                "warning": "yellow",
                "critical": "red",
                "unknown": "dim",
            }.get(metric.status, "white")

            metrics_table.add_row(
                result.component,
                metric.name,
                f"{metric.value:.2f}",
                metric.unit,
                f"[{status_style}]{metric.status}[/{status_style}]",
                f"{metric.threshold:.2f}" if metric.threshold else "N/A",
            )

    # Layout the dashboard
    layout.split_column(
        Layout(header, size=3),
        Layout(summary_table, size=len(results) + 3),
        Layout(metrics_table, size=20),
    )

    console.print(layout)


# CLI Commands
@app.command()
def dashboard(
    project: str = typer.Option(
        "all", "--project", help="Target project (pheno, kit, atlas, all)",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
    live: bool = typer.Option(False, "--live", help="Live monitoring mode"),
):
    """Show health dashboard."""

    def run_dashboard():
        results = []

        if project in ["pheno", "all"]:
            pheno_monitor = PhenoSDKHealthMonitor()
            results.append(pheno_monitor.check_health())

        if project in ["kit", "all"]:
            kit_monitor = KitHealthMonitor("default-kit")
            results.append(kit_monitor.check_health())

        if project in ["atlas", "all"]:
            atlas_monitor = AtlasHealthMonitor()
            results.append(atlas_monitor.check_health())

        if project == "all":
            perf_monitor = PerformanceMonitor()
            results.append(perf_monitor.check_health())

        if json_output:
            console.print(json.dumps([r.to_dict() for r in results], indent=2))
        elif live:
            with Live(display_health_dashboard(results), refresh_per_second=1):
                try:
                    while True:
                        time.sleep(1)
                        # In a real implementation, you would refresh the data here
                except KeyboardInterrupt:
                    pass
        else:
            display_health_dashboard(results)

    run_dashboard()


@app.command()
def kit(
    kit_name: str = typer.Argument("default-kit", help="Kit name to monitor"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Monitor individual kit health."""
    monitor = KitHealthMonitor(kit_name)
    result = monitor.check_health()

    if json_output:
        console.print(json.dumps(result.to_dict(), indent=2))
    else:
        display_health_dashboard([result])


@app.command()
def atlas(
    project: str = typer.Option("atlas", "--project", help="Atlas project name"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Monitor Atlas health."""
    monitor = AtlasHealthMonitor(project)
    result = monitor.check_health()

    if json_output:
        console.print(json.dumps(result.to_dict(), indent=2))
    else:
        display_health_dashboard([result])


@app.command()
def performance(
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Monitor performance metrics."""
    monitor = PerformanceMonitor()
    result = monitor.check_health()

    if json_output:
        console.print(json.dumps(result.to_dict(), indent=2))
    else:
        display_health_dashboard([result])


@app.command()
def all(
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
    live: bool = typer.Option(False, "--live", help="Live monitoring mode"),
):
    """Run all health checks."""
    dashboard(project="all", verbose=verbose, json_output=json_output, live=live)


if __name__ == "__main__":
    app()
