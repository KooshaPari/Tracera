#!/usr/bin/env python3
"""
CI/CD Monitoring Infrastructure
Comprehensive monitoring and observability for CI/CD pipelines.
"""

import argparse
import json
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
import yaml


@dataclass
class PipelineMetric:
    """CI/CD pipeline metric."""
    name: str
    value: float
    unit: str
    timestamp: float
    category: str
    severity: str = "info"  # "info", "warning", "error", "critical"


@dataclass
class PipelineEvent:
    """CI/CD pipeline event."""
    event_type: str  # "start", "success", "failure", "timeout", "cancelled"
    pipeline_name: str
    duration: float
    timestamp: float
    metadata: dict[str, Any]
    error_message: str | None = None


class CICDMonitor:
    """Comprehensive CI/CD monitoring system."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "monitoring"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = []
        self.events = []
        self.alerts = []

        # Monitoring configuration
        self.config = {
            "pipeline_timeout": 3600,  # 1 hour
            "memory_threshold": 80,    # 80% memory usage
            "cpu_threshold": 90,       # 90% CPU usage
            "disk_threshold": 85,      # 85% disk usage
            "alert_cooldown": 300,     # 5 minutes
            "retention_days": 30,       # 30 days data retention
        }

    def start_monitoring(self) -> None:
        """Start comprehensive CI/CD monitoring."""
        print("🔍 Starting CI/CD Monitoring Infrastructure...")

        # Start monitoring threads
        self._start_system_monitoring()
        self._start_pipeline_monitoring()
        self._start_quality_monitoring()
        self._start_resource_monitoring()

        print("✅ CI/CD Monitoring Infrastructure Active")

    def _start_system_monitoring(self) -> None:
        """Start system resource monitoring."""
        def monitor_system():
            while True:
                try:
                    # Monitor system resources
                    self._collect_system_metrics()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    print(f"Error in system monitoring: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=monitor_system, daemon=True)
        thread.start()

    def _start_pipeline_monitoring(self) -> None:
        """Start pipeline execution monitoring."""
        def monitor_pipelines():
            while True:
                try:
                    # Monitor GitHub Actions workflows
                    self._monitor_github_actions()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    print(f"Error in pipeline monitoring: {e}")
                    time.sleep(300)

        thread = threading.Thread(target=monitor_pipelines, daemon=True)
        thread.start()

    def _start_quality_monitoring(self) -> None:
        """Start quality metrics monitoring."""
        def monitor_quality():
            while True:
                try:
                    # Monitor quality metrics
                    self._collect_quality_metrics()
                    time.sleep(1800)  # Check every 30 minutes
                except Exception as e:
                    print(f"Error in quality monitoring: {e}")
                    time.sleep(1800)

        thread = threading.Thread(target=monitor_quality, daemon=True)
        thread.start()

    def _start_resource_monitoring(self) -> None:
        """Start resource utilization monitoring."""
        def monitor_resources():
            while True:
                try:
                    # Monitor resource utilization
                    self._collect_resource_metrics()
                    time.sleep(120)  # Check every 2 minutes
                except Exception as e:
                    print(f"Error in resource monitoring: {e}")
                    time.sleep(120)

        thread = threading.Thread(target=monitor_resources, daemon=True)
        thread.start()

    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.append(PipelineMetric(
                name="system_cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=time.time(),
                category="system",
                severity="warning" if cpu_percent > self.config["cpu_threshold"] else "info",
            ))

            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.append(PipelineMetric(
                name="system_memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=time.time(),
                category="system",
                severity="warning" if memory.percent > self.config["memory_threshold"] else "info",
            ))

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self.metrics.append(PipelineMetric(
                name="system_disk_usage",
                value=disk_percent,
                unit="percent",
                timestamp=time.time(),
                category="system",
                severity="warning" if disk_percent > self.config["disk_threshold"] else "info",
            ))

            # Process count
            process_count = len(psutil.pids())
            self.metrics.append(PipelineMetric(
                name="system_process_count",
                value=process_count,
                unit="count",
                timestamp=time.time(),
                category="system",
            ))

        except Exception as e:
            print(f"Error collecting system metrics: {e}")

    def _monitor_github_actions(self) -> None:
        """Monitor GitHub Actions workflows."""
        try:
            # Check for workflow files
            workflows_dir = self.project_root / ".github" / "workflows"
            if not workflows_dir.exists():
                return

            # Get recent workflow runs (simulated - would need GitHub API)
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

            for workflow_file in workflow_files:
                # Simulate workflow monitoring
                self.metrics.append(PipelineMetric(
                    name="workflow_count",
                    value=len(workflow_files),
                    unit="count",
                    timestamp=time.time(),
                    category="pipeline",
                ))

                # Check workflow configuration
                self._validate_workflow_config(workflow_file)

        except Exception as e:
            print(f"Error monitoring GitHub Actions: {e}")

    def _validate_workflow_config(self, workflow_file: Path) -> None:
        """Validate workflow configuration."""
        try:
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for required fields
            required_fields = ["name", "on", "jobs"]
            missing_fields = [field for field in required_fields if field not in workflow_config]

            if missing_fields:
                self.metrics.append(PipelineMetric(
                    name="workflow_config_issues",
                    value=len(missing_fields),
                    unit="count",
                    timestamp=time.time(),
                    category="pipeline",
                    severity="warning",
                ))

            # Check for timeout configuration
            jobs = workflow_config.get("jobs", {})
            for job_name, job_config in jobs.items():
                if "timeout-minutes" not in job_config:
                    self.metrics.append(PipelineMetric(
                        name="workflow_missing_timeout",
                        value=1,
                        unit="count",
                        timestamp=time.time(),
                        category="pipeline",
                        severity="warning",
                    ))

        except Exception as e:
            print(f"Error validating workflow {workflow_file}: {e}")

    def _collect_quality_metrics(self) -> None:
        """Collect quality metrics."""
        try:
            # Check test coverage
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                self.metrics.append(PipelineMetric(
                    name="test_coverage",
                    value=total_coverage,
                    unit="percent",
                    timestamp=time.time(),
                    category="quality",
                    severity="warning" if total_coverage < 80 else "info",
                ))

            # Check code quality reports
            quality_reports = list(self.project_root.glob("reports/*.json"))
            self.metrics.append(PipelineMetric(
                name="quality_reports_count",
                value=len(quality_reports),
                unit="count",
                timestamp=time.time(),
                category="quality",
            ))

            # Check for security issues
            security_file = self.project_root / "bandit-report.json"
            if security_file.exists():
                with open(security_file) as f:
                    security_data = json.load(f)

                high_severity = len([r for r in security_data.get("results", []) if r.get("issue_severity") == "HIGH"])
                self.metrics.append(PipelineMetric(
                    name="security_high_severity",
                    value=high_severity,
                    unit="count",
                    timestamp=time.time(),
                    category="security",
                    severity="critical" if high_severity > 0 else "info",
                ))

        except Exception as e:
            print(f"Error collecting quality metrics: {e}")

    def _collect_resource_metrics(self) -> None:
        """Collect resource utilization metrics."""
        try:
            # Monitor current process
            process = psutil.Process()

            # Memory usage
            memory_info = process.memory_info()
            self.metrics.append(PipelineMetric(
                name="process_memory_rss",
                value=memory_info.rss / 1024 / 1024,  # MB
                unit="MB",
                timestamp=time.time(),
                category="process",
            ))

            # CPU usage
            cpu_percent = process.cpu_percent()
            self.metrics.append(PipelineMetric(
                name="process_cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=time.time(),
                category="process",
            ))

            # File descriptors
            try:
                open_files = len(process.open_files())
                self.metrics.append(PipelineMetric(
                    name="process_open_files",
                    value=open_files,
                    unit="count",
                    timestamp=time.time(),
                    category="process",
                ))
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

            # Thread count
            thread_count = process.num_threads()
            self.metrics.append(PipelineMetric(
                name="process_thread_count",
                value=thread_count,
                unit="count",
                timestamp=time.time(),
                category="process",
            ))

        except Exception as e:
            print(f"Error collecting resource metrics: {e}")

    def generate_monitoring_report(self) -> dict[str, Any]:
        """Generate comprehensive monitoring report."""
        print("📊 Generating CI/CD Monitoring Report...")

        # Calculate summary statistics
        total_metrics = len(self.metrics)
        critical_alerts = len([m for m in self.metrics if m.severity == "critical"])
        warning_alerts = len([m for m in self.metrics if m.severity == "warning"])

        # Group metrics by category
        metrics_by_category = {}
        for metric in self.metrics:
            category = metric.category
            if category not in metrics_by_category:
                metrics_by_category[category] = []
            metrics_by_category[category].append(asdict(metric))

        # Calculate trends
        trends = self._calculate_trends()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_metrics": total_metrics,
                "critical_alerts": critical_alerts,
                "warning_alerts": warning_alerts,
                "metrics_by_category": {k: len(v) for k, v in metrics_by_category.items()},
                "health_score": self._calculate_health_score(),
            },
            "metrics_by_category": metrics_by_category,
            "trends": trends,
            "recommendations": recommendations,
            "config": self.config,
        }

        # Save report
        self._save_report(report)

        return report

    def _calculate_trends(self) -> dict[str, Any]:
        """Calculate metric trends."""
        trends = {}

        # Group metrics by name and calculate trends
        metrics_by_name = {}
        for metric in self.metrics:
            name = metric.name
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append(metric)

        for name, metrics_list in metrics_by_name.items():
            if len(metrics_list) > 1:
                # Sort by timestamp
                sorted_metrics = sorted(metrics_list, key=lambda x: x.timestamp)

                # Calculate trend
                first_value = sorted_metrics[0].value
                last_value = sorted_metrics[-1].value
                trend_direction = "increasing" if last_value > first_value else "decreasing" if last_value < first_value else "stable"

                trends[name] = {
                    "direction": trend_direction,
                    "first_value": first_value,
                    "last_value": last_value,
                    "change_percent": ((last_value - first_value) / first_value * 100) if first_value != 0 else 0,
                    "data_points": len(metrics_list),
                }

        return trends

    def _generate_recommendations(self) -> list[str]:
        """Generate monitoring recommendations."""
        recommendations = []

        # Check for critical alerts
        critical_metrics = [m for m in self.metrics if m.severity == "critical"]
        if critical_metrics:
            recommendations.append(f"Address {len(critical_metrics)} critical alerts immediately")

        # Check for warning alerts
        warning_metrics = [m for m in self.metrics if m.severity == "warning"]
        if warning_metrics:
            recommendations.append(f"Review {len(warning_metrics)} warning alerts")

        # Check for high resource usage
        cpu_metrics = [m for m in self.metrics if m.name == "system_cpu_usage" and m.value > 80]
        if cpu_metrics:
            recommendations.append("High CPU usage detected - consider optimizing processes")

        memory_metrics = [m for m in self.metrics if m.name == "system_memory_usage" and m.value > 80]
        if memory_metrics:
            recommendations.append("High memory usage detected - consider memory optimization")

        # Check for low test coverage
        coverage_metrics = [m for m in self.metrics if m.name == "test_coverage" and m.value < 80]
        if coverage_metrics:
            recommendations.append("Low test coverage detected - increase test coverage")

        return recommendations

    def _calculate_health_score(self) -> float:
        """Calculate overall health score."""
        if not self.metrics:
            return 100.0

        # Base score
        score = 100.0

        # Deduct for critical alerts
        critical_count = len([m for m in self.metrics if m.severity == "critical"])
        score -= critical_count * 20

        # Deduct for warning alerts
        warning_count = len([m for m in self.metrics if m.severity == "warning"])
        score -= warning_count * 5

        # Deduct for high resource usage
        high_cpu = len([m for m in self.metrics if m.name == "system_cpu_usage" and m.value > 90])
        score -= high_cpu * 10

        high_memory = len([m for m in self.metrics if m.name == "system_memory_usage" and m.value > 90])
        score -= high_memory * 10

        # Ensure score is between 0 and 100
        return max(0, min(100, score))

    def _save_report(self, report: dict[str, Any]) -> None:
        """Save monitoring report."""
        # Save JSON report
        json_file = self.reports_dir / f"ci_cd_monitoring_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save summary report
        summary_file = self.reports_dir / f"monitoring_summary_{int(time.time())}.md"
        self._save_summary_report(report, summary_file)

        print("📊 Monitoring reports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Summary: {summary_file}")

    def _save_summary_report(self, report: dict[str, Any], file_path: Path) -> None:
        """Save markdown summary report."""
        summary = report["summary"]

        content = f"""# CI/CD Monitoring Report

**Generated**: {report['timestamp']}
**Health Score**: {summary['health_score']:.1f}/100

## Summary

| Metric | Value |
|--------|-------|
| Total Metrics | {summary['total_metrics']} |
| Critical Alerts | {summary['critical_alerts']} |
| Warning Alerts | {summary['warning_alerts']} |
| Health Score | {summary['health_score']:.1f}/100 |

## Metrics by Category

"""

        for category, count in summary["metrics_by_category"].items():
            content += f"- **{category.title()}**: {count} metrics\n"

        if report["trends"]:
            content += "\n## Trends\n\n"
            for name, trend in report["trends"].items():
                direction_emoji = "📈" if trend["direction"] == "increasing" else "📉" if trend["direction"] == "decreasing" else "➡️"
                content += f"- {direction_emoji} **{name}**: {trend['direction']} ({trend['change_percent']:.1f}%)\n"

        if report["recommendations"]:
            content += "\n## Recommendations\n\n"
            for rec in report["recommendations"]:
                content += f"- {rec}\n"

        with open(file_path, "w") as f:
            f.write(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CI/CD Monitoring Infrastructure")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--duration", type=int, default=3600, help="Monitoring duration in seconds")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    monitor = CICDMonitor(args.project_root)

    try:
        # Start monitoring
        monitor.start_monitoring()

        # Run for specified duration
        print(f"🔍 Monitoring for {args.duration} seconds...")
        time.sleep(args.duration)

        # Generate final report
        report = monitor.generate_monitoring_report()

        if args.json:
            output = json.dumps(report, indent=2)
        else:
            # Pretty print format
            summary = report["summary"]
            output = f"""
🔍 CI/CD MONITORING REPORT
{'=' * 50}
Health Score: {summary['health_score']:.1f}/100
Total Metrics: {summary['total_metrics']}
Critical Alerts: {summary['critical_alerts']}
Warning Alerts: {summary['warning_alerts']}

Recommendations:
"""
            for rec in report["recommendations"]:
                output += f"  • {rec}\n"

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Report saved to {args.output}")
        else:
            print(output)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
        report = monitor.generate_monitoring_report()
        print("📊 Final report generated")
    except Exception as e:
        print(f"❌ Error in monitoring: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
