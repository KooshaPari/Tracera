#!/usr/bin/env python3
"""Performance Profiling Dashboard.

Performance data visualization with trend analysis.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich import box
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("Rich library not found. Install with: pip install rich")
    sys.exit(1)


class PerformanceDashboard:
    """
    Performance data visualization dashboard.
    """

    def __init__(self):
        self.console = Console()
        self.performance_data: list[dict[str, Any]] = []
        self.metrics_history: dict[str, list[float]] = {
            "response_time": [],
            "memory_usage": [],
            "cpu_usage": [],
            "test_duration": [],
            "coverage": [],
            "complexity": [],
        }

    def load_performance_data(self, data_file: str | None = None):
        """
        Load performance data from file or generate sample data.
        """
        if data_file and Path(data_file).exists():
            with open(data_file) as f:
                self.performance_data = json.load(f)
        else:
            # Generate sample data for demonstration
            self._generate_sample_data()

    def _generate_sample_data(self):
        """
        Generate sample performance data.
        """
        base_time = time.time() - (7 * 24 * 3600)  # 7 days ago

        for i in range(168):  # 168 hours = 7 days
            timestamp = base_time + (i * 3600)

            # Generate realistic performance data with trends
            response_time = 100 + (i * 0.5) + (i % 24) * 2  # Gradual increase with daily pattern
            memory_usage = 512 + (i * 0.3) + (i % 12) * 10  # Gradual increase with daily pattern
            cpu_usage = 20 + (i % 24) * 2 + (i % 7) * 5  # Daily and weekly patterns
            test_duration = 120 + (i * 0.1) + (i % 24) * 5  # Gradual increase
            coverage = 85 + (i * 0.02) + (i % 7) * 2  # Gradual improvement
            complexity = 15 - (i * 0.01) + (i % 24) * 0.5  # Gradual improvement

            self.performance_data.append(
                {
                    "timestamp": timestamp,
                    "response_time_ms": response_time,
                    "memory_usage_mb": memory_usage,
                    "cpu_usage_percent": cpu_usage,
                    "test_duration_seconds": test_duration,
                    "coverage_percent": coverage,
                    "complexity_score": complexity,
                    "test_count": 150 + (i % 10),
                    "error_count": max(0, 5 - (i % 7)),
                    "build_time_seconds": 45 + (i % 12) * 2,
                },
            )

    def calculate_trends(self) -> dict[str, Any]:
        """
        Calculate performance trends.
        """
        if not self.performance_data:
            return {}

        # Get recent data (last 24 hours)
        recent_data = (
            self.performance_data[-24:]
            if len(self.performance_data) >= 24
            else self.performance_data
        )

        trends = {}

        for metric in [
            "response_time_ms",
            "memory_usage_mb",
            "cpu_usage_percent",
            "test_duration_seconds",
            "coverage_percent",
            "complexity_score",
        ]:
            values = [d[metric] for d in recent_data if metric in d]
            if len(values) >= 2:
                # Calculate trend (positive = increasing, negative = decreasing)
                trend = (values[-1] - values[0]) / len(values)
                trends[metric] = {
                    "current": values[-1],
                    "trend": trend,
                    "direction": (
                        "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable"
                    ),
                    "change_percent": (trend / values[0] * 100) if values[0] != 0 else 0,
                }

        return trends

    def create_metrics_table(self) -> Table:
        """
        Create metrics overview table.
        """
        table = Table(title="Performance Metrics Overview", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Current Value", style="green")
        table.add_column("Trend", style="yellow")
        table.add_column("Change %", style="magenta")

        trends = self.calculate_trends()

        metric_names = {
            "response_time_ms": "Response Time (ms)",
            "memory_usage_mb": "Memory Usage (MB)",
            "cpu_usage_percent": "CPU Usage (%)",
            "test_duration_seconds": "Test Duration (s)",
            "coverage_percent": "Coverage (%)",
            "complexity_score": "Complexity Score",
        }

        for metric, data in trends.items():
            if metric in metric_names:
                direction_icon = (
                    "📈"
                    if data["direction"] == "increasing"
                    else "📉" if data["direction"] == "decreasing" else "➡️"
                )
                change_color = (
                    "red"
                    if data["change_percent"] > 5
                    else "green" if data["change_percent"] < -5 else "yellow"
                )

                table.add_row(
                    metric_names[metric],
                    f"{data['current']:.2f}",
                    f"{direction_icon} {data['direction']}",
                    f"[{change_color}]{data['change_percent']:+.1f}%[/{change_color}]",
                )

        return table

    def create_performance_chart(self) -> Panel:
        """
        Create ASCII performance chart.
        """
        if not self.performance_data:
            return Panel("No data available", title="Performance Chart")

        # Get last 24 data points
        recent_data = self.performance_data[-24:]

        # Create response time chart
        chart_lines = []
        chart_lines.append("Response Time Trend (last 24 hours):")
        chart_lines.append("")

        max_rt = max(d["response_time_ms"] for d in recent_data)
        min_rt = min(d["response_time_ms"] for d in recent_data)
        range_rt = max_rt - min_rt if max_rt != min_rt else 1

        for i, data in enumerate(recent_data):
            rt = data["response_time_ms"]
            normalized = (rt - min_rt) / range_rt
            bar_length = int(normalized * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            time_str = datetime.fromtimestamp(data["timestamp"]).strftime("%H:%M")
            chart_lines.append(f"{time_str} │{bar}│ {rt:.1f}ms")

        return Panel("\n".join(chart_lines), title="Performance Chart", border_style="blue")

    def create_health_status(self) -> Panel:
        """
        Create system health status panel.
        """
        if not self.performance_data:
            return Panel("No data available", title="System Health")

        latest = self.performance_data[-1]
        trends = self.calculate_trends()

        # Determine overall health
        health_score = 100
        issues = []

        # Check response time
        if latest["response_time_ms"] > 1000:
            health_score -= 20
            issues.append("High response time")

        # Check memory usage
        if latest["memory_usage_mb"] > 1024:
            health_score -= 15
            issues.append("High memory usage")

        # Check CPU usage
        if latest["cpu_usage_percent"] > 80:
            health_score -= 15
            issues.append("High CPU usage")

        # Check error count
        if latest["error_count"] > 10:
            health_score -= 25
            issues.append("High error count")

        # Check coverage
        if latest["coverage_percent"] < 80:
            health_score -= 10
            issues.append("Low test coverage")

        # Determine health status
        if health_score >= 90:
            status = "🟢 Excellent"
            status_color = "green"
        elif health_score >= 70:
            status = "🟡 Good"
            status_color = "yellow"
        elif health_score >= 50:
            status = "🟠 Fair"
            status_color = "orange"
        else:
            status = "🔴 Poor"
            status_color = "red"

        health_content = f"""
Overall Health: [{status_color}]{status}[/{status_color}] ({health_score}/100)

Current Metrics:
• Response Time: {latest['response_time_ms']:.1f}ms
• Memory Usage: {latest['memory_usage_mb']:.1f}MB
• CPU Usage: {latest['cpu_usage_percent']:.1f}%
• Test Coverage: {latest['coverage_percent']:.1f}%
• Error Count: {latest['error_count']}
• Build Time: {latest['build_time_seconds']}s
"""

        if issues:
            health_content += "\nIssues Detected:\n"
            for issue in issues:
                health_content += f"• {issue}\n"

        return Panel(health_content, title="System Health", border_style=status_color)

    def create_recommendations(self) -> Panel:
        """
        Create performance recommendations panel.
        """
        trends = self.calculate_trends()
        recommendations = []

        # Response time recommendations
        if trends.get("response_time_ms", {}).get("direction") == "increasing":
            recommendations.append("• Consider optimizing database queries")
            recommendations.append("• Review API endpoint performance")
            recommendations.append("• Implement caching strategies")

        # Memory usage recommendations
        if trends.get("memory_usage_mb", {}).get("direction") == "increasing":
            recommendations.append("• Check for memory leaks")
            recommendations.append("• Optimize data structures")
            recommendations.append("• Consider garbage collection tuning")

        # CPU usage recommendations
        if trends.get("cpu_usage_percent", {}).get("direction") == "increasing":
            recommendations.append("• Profile CPU-intensive operations")
            recommendations.append("• Consider parallel processing")
            recommendations.append("• Optimize algorithms")

        # Coverage recommendations
        if trends.get("coverage_percent", {}).get("current", 0) < 85:
            recommendations.append("• Increase test coverage")
            recommendations.append("• Add integration tests")
            recommendations.append("• Review untested code paths")

        # Complexity recommendations
        if trends.get("complexity_score", {}).get("current", 0) > 20:
            recommendations.append("• Refactor complex functions")
            recommendations.append("• Break down large modules")
            recommendations.append("• Apply design patterns")

        if not recommendations:
            recommendations.append("• System performance is optimal")
            recommendations.append("• Continue monitoring trends")
            recommendations.append("• Maintain current practices")

        content = "\n".join(recommendations) if recommendations else "No recommendations available"
        return Panel(content, title="Performance Recommendations", border_style="green")

    def create_dashboard_layout(self) -> Layout:
        """
        Create the main dashboard layout.
        """
        layout = Layout()

        layout.split_column(
            Layout(self.create_health_status(), size=8),
            Layout(self.create_metrics_table(), size=12),
            Layout.split_row(
                Layout(self.create_performance_chart(), size=20),
                Layout(self.create_recommendations(), size=20),
            ),
        )

        return layout

    def run_live_dashboard(self, refresh_interval: int = 5):
        """
        Run live updating dashboard.
        """
        self.console.print("Starting live performance dashboard...")
        self.console.print("Press Ctrl+C to stop")

        try:
            with Live(
                self.create_dashboard_layout(), refresh_per_second=1 / refresh_interval,
            ) as live:
                while True:
                    # Update data (in real implementation, this would fetch new data)
                    time.sleep(refresh_interval)

                    # Update the layout
                    live.update(self.create_dashboard_layout())

        except KeyboardInterrupt:
            self.console.print("\nDashboard stopped")

    def generate_report(self) -> str:
        """
        Generate a comprehensive performance report.
        """
        report = []
        report.append("Performance Profiling Dashboard Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        if not self.performance_data:
            report.append("No performance data available")
            return "\n".join(report)

        # Latest metrics
        latest = self.performance_data[-1]
        report.append("Latest Performance Metrics:")
        report.append(f"  Response Time: {latest['response_time_ms']:.2f}ms")
        report.append(f"  Memory Usage: {latest['memory_usage_mb']:.2f}MB")
        report.append(f"  CPU Usage: {latest['cpu_usage_percent']:.2f}%")
        report.append(f"  Test Duration: {latest['test_duration_seconds']:.2f}s")
        report.append(f"  Coverage: {latest['coverage_percent']:.2f}%")
        report.append(f"  Complexity: {latest['complexity_score']:.2f}")
        report.append("")

        # Trends analysis
        trends = self.calculate_trends()
        report.append("Performance Trends (last 24 hours):")
        for metric, data in trends.items():
            report.append(
                f"  {metric}: {data['current']:.2f} ({data['direction']}, {data['change_percent']:+.1f}%)",
            )
        report.append("")

        # Recommendations
        report.append("Recommendations:")
        if trends.get("response_time_ms", {}).get("direction") == "increasing":
            report.append("  - Optimize database queries and API endpoints")
        if trends.get("memory_usage_mb", {}).get("direction") == "increasing":
            report.append("  - Check for memory leaks and optimize data structures")
        if trends.get("coverage_percent", {}).get("current", 0) < 85:
            report.append("  - Increase test coverage")

        return "\n".join(report)


def main():
    """
    Main dashboard function.
    """
    parser = argparse.ArgumentParser(description="Performance Profiling Dashboard")
    parser.add_argument("--data-file", help="Path to performance data JSON file")
    parser.add_argument("--live", action="store_true", help="Run live dashboard")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds")
    parser.add_argument("--report", action="store_true", help="Generate text report")
    parser.add_argument("--json", action="store_true", help="Output data as JSON")

    args = parser.parse_args()

    dashboard = PerformanceDashboard()
    dashboard.load_performance_data(args.data_file)

    if args.json:
        print(json.dumps(dashboard.performance_data, indent=2))
    elif args.report:
        report = dashboard.generate_report()
        print(report)
    elif args.live:
        dashboard.run_live_dashboard(args.refresh)
    else:
        # Static dashboard
        console = Console()
        console.print(Panel("Performance Profiling Dashboard", style="bold blue"))
        console.print(dashboard.create_dashboard_layout())


if __name__ == "__main__":
    main()
