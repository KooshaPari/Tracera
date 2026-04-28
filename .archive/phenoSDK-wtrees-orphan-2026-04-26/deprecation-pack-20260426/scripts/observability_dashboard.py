#!/usr/bin/env python3
"""
Observability Dashboard and Alerting System
Comprehensive monitoring dashboard with real-time alerts.
"""

import argparse
import json
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Alert:
    """Alert definition."""
    id: str
    name: str
    condition: str
    threshold: float
    severity: str  # "info", "warning", "error", "critical"
    enabled: bool = True
    cooldown: int = 300  # 5 minutes
    last_triggered: float | None = None


@dataclass
class AlertEvent:
    """Alert event."""
    alert_id: str
    message: str
    severity: str
    timestamp: float
    value: float
    threshold: float
    resolved: bool = False


class ObservabilityDashboard:
    """Comprehensive observability dashboard and alerting system."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "observability"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.alerts = []
        self.alert_events = []
        self.metrics_history = []
        self.dashboard_data = {}

        # Initialize default alerts
        self._initialize_default_alerts()

        # Alert handlers
        self.alert_handlers = {
            "console": self._handle_console_alert,
            "email": self._handle_email_alert,
            "webhook": self._handle_webhook_alert,
            "file": self._handle_file_alert,
        }

    def _initialize_default_alerts(self) -> None:
        """Initialize default alert configurations."""
        self.alerts = [
            Alert(
                id="high_cpu_usage",
                name="High CPU Usage",
                condition="system_cpu_usage > 90",
                threshold=90.0,
                severity="warning",
            ),
            Alert(
                id="high_memory_usage",
                name="High Memory Usage",
                condition="system_memory_usage > 85",
                threshold=85.0,
                severity="warning",
            ),
            Alert(
                id="low_test_coverage",
                name="Low Test Coverage",
                condition="test_coverage < 80",
                threshold=80.0,
                severity="error",
            ),
            Alert(
                id="high_security_issues",
                name="High Security Issues",
                condition="security_high_severity > 0",
                threshold=0.0,
                severity="critical",
            ),
            Alert(
                id="pipeline_failure",
                name="Pipeline Failure",
                condition="pipeline_success_rate < 95",
                threshold=95.0,
                severity="error",
            ),
            Alert(
                id="kit_health_degradation",
                name="Kit Health Degradation",
                condition="kit_health_score < 70",
                threshold=70.0,
                severity="warning",
            ),
        ]

    def start_dashboard(self, duration: int = 3600) -> None:
        """Start the observability dashboard."""
        print("🚀 Starting Observability Dashboard...")

        # Start monitoring threads
        self._start_metrics_collection()
        self._start_alert_monitoring()
        self._start_dashboard_generation()

        print(f"📊 Dashboard running for {duration} seconds...")

        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")

        # Generate final report
        self._generate_final_report()

    def _start_metrics_collection(self) -> None:
        """Start metrics collection thread."""
        def collect_metrics():
            while True:
                try:
                    # Collect various metrics
                    self._collect_system_metrics()
                    self._collect_quality_metrics()
                    self._collect_pipeline_metrics()
                    self._collect_kit_health_metrics()

                    time.sleep(60)  # Collect every minute
                except Exception as e:
                    print(f"Error collecting metrics: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()

    def _start_alert_monitoring(self) -> None:
        """Start alert monitoring thread."""
        def monitor_alerts():
            while True:
                try:
                    self._check_alerts()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    print(f"Error monitoring alerts: {e}")
                    time.sleep(30)

        thread = threading.Thread(target=monitor_alerts, daemon=True)
        thread.start()

    def _start_dashboard_generation(self) -> None:
        """Start dashboard generation thread."""
        def generate_dashboard():
            while True:
                try:
                    self._generate_dashboard_data()
                    time.sleep(300)  # Generate every 5 minutes
                except Exception as e:
                    print(f"Error generating dashboard: {e}")
                    time.sleep(300)

        thread = threading.Thread(target=generate_dashboard, daemon=True)
        thread.start()

    def _collect_system_metrics(self) -> None:
        """Collect system metrics."""
        try:
            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric("system_cpu_usage", cpu_percent, "percent")

            # Memory usage
            memory = psutil.virtual_memory()
            self._add_metric("system_memory_usage", memory.percent, "percent")

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self._add_metric("system_disk_usage", disk_percent, "percent")

        except Exception as e:
            print(f"Error collecting system metrics: {e}")

    def _collect_quality_metrics(self) -> None:
        """Collect quality metrics."""
        try:
            # Test coverage
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                self._add_metric("test_coverage", total_coverage, "percent")

            # Security issues
            bandit_file = self.project_root / "bandit-report.json"
            if bandit_file.exists():
                with open(bandit_file) as f:
                    bandit_data = json.load(f)

                high_severity = len([r for r in bandit_data.get("results", []) if r.get("issue_severity") == "HIGH"])
                self._add_metric("security_high_severity", high_severity, "count")

        except Exception as e:
            print(f"Error collecting quality metrics: {e}")

    def _collect_pipeline_metrics(self) -> None:
        """Collect pipeline metrics."""
        try:
            # Simulate pipeline success rate (would be real data in production)
            success_rate = 95.0  # This would come from actual pipeline data
            self._add_metric("pipeline_success_rate", success_rate, "percent")

        except Exception as e:
            print(f"Error collecting pipeline metrics: {e}")

    def _collect_kit_health_metrics(self) -> None:
        """Collect kit health metrics."""
        try:
            # Run kit health monitor
            result = subprocess.run([
                "python", "scripts/kit_health_monitor.py", str(self.project_root), "--json",
            ], check=False, capture_output=True, text=True, cwd=self.project_root, timeout=60)

            if result.returncode == 0:
                kit_data = json.loads(result.stdout)
                avg_health = kit_data.get("summary", {}).get("average_health_score", 0)
                self._add_metric("kit_health_score", avg_health, "percent")

        except Exception as e:
            print(f"Error collecting kit health metrics: {e}")

    def _add_metric(self, name: str, value: float, unit: str) -> None:
        """Add a metric to the history."""
        metric = {
            "name": name,
            "value": value,
            "unit": unit,
            "timestamp": time.time(),
        }
        self.metrics_history.append(metric)

        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

    def _check_alerts(self) -> None:
        """Check all alerts against current metrics."""
        current_metrics = {m["name"]: m["value"] for m in self.metrics_history[-10:]}  # Last 10 metrics

        for alert in self.alerts:
            if not alert.enabled:
                continue

            # Check cooldown
            if alert.last_triggered and time.time() - alert.last_triggered < alert.cooldown:
                continue

            # Evaluate alert condition
            if self._evaluate_alert_condition(alert, current_metrics):
                self._trigger_alert(alert, current_metrics)

    def _evaluate_alert_condition(self, alert: Alert, metrics: dict[str, float]) -> bool:
        """Evaluate alert condition against current metrics."""
        try:
            # Simple condition evaluation (would be more sophisticated in production)
            if ">" in alert.condition:
                metric_name, threshold_str = alert.condition.split(" > ")
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())

                if metric_name in metrics:
                    return metrics[metric_name] > threshold

            elif "<" in alert.condition:
                metric_name, threshold_str = alert.condition.split(" < ")
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())

                if metric_name in metrics:
                    return metrics[metric_name] < threshold

            elif "==" in alert.condition:
                metric_name, threshold_str = alert.condition.split(" == ")
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())

                if metric_name in metrics:
                    return metrics[metric_name] == threshold

        except Exception as e:
            print(f"Error evaluating alert condition: {e}")

        return False

    def _trigger_alert(self, alert: Alert, metrics: dict[str, float]) -> None:
        """Trigger an alert."""
        # Get current metric value
        metric_name = alert.condition.split()[0]
        current_value = metrics.get(metric_name, 0)

        # Create alert event
        alert_event = AlertEvent(
            alert_id=alert.id,
            message=f"{alert.name}: {metric_name} = {current_value} (threshold: {alert.threshold})",
            severity=alert.severity,
            timestamp=time.time(),
            value=current_value,
            threshold=alert.threshold,
        )

        self.alert_events.append(alert_event)
        alert.last_triggered = time.time()

        # Handle alert
        self._handle_alert(alert_event)

        print(f"🚨 ALERT: {alert_event.message}")

    def _handle_alert(self, alert_event: AlertEvent) -> None:
        """Handle an alert event."""
        # Console output (always enabled)
        self.alert_handlers["console"](alert_event)

        # File logging
        self.alert_handlers["file"](alert_event)

        # Additional handlers based on severity
        if alert_event.severity in ["error", "critical"]:
            # Could add email/webhook notifications here
            pass

    def _handle_console_alert(self, alert_event: AlertEvent) -> None:
        """Handle console alert output."""
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨",
        }

        emoji = severity_emoji.get(alert_event.severity, "📢")
        print(f"{emoji} {alert_event.message}")

    def _handle_file_alert(self, alert_event: AlertEvent) -> None:
        """Handle file alert logging."""
        alert_log_file = self.reports_dir / "alerts.log"

        with open(alert_log_file, "a") as f:
            f.write(f"{datetime.fromtimestamp(alert_event.timestamp).isoformat()} - {alert_event.severity.upper()} - {alert_event.message}\n")

    def _handle_email_alert(self, alert_event: AlertEvent) -> None:
        """Handle email alert (placeholder)."""
        # Would implement email sending here

    def _handle_webhook_alert(self, alert_event: AlertEvent) -> None:
        """Handle webhook alert (placeholder)."""
        # Would implement webhook sending here

    def _generate_dashboard_data(self) -> None:
        """Generate dashboard data."""
        # Calculate current metrics
        current_metrics = {}
        for metric in self.metrics_history[-10:]:  # Last 10 metrics
            current_metrics[metric["name"]] = metric["value"]

        # Calculate trends
        trends = self._calculate_trends()

        # Calculate health score
        health_score = self._calculate_overall_health_score()

        # Generate dashboard data
        self.dashboard_data = {
            "timestamp": time.time(),
            "current_metrics": current_metrics,
            "trends": trends,
            "health_score": health_score,
            "active_alerts": len([a for a in self.alert_events if not a.resolved]),
            "total_alerts": len(self.alert_events),
        }

        # Save dashboard data
        dashboard_file = self.reports_dir / "dashboard_data.json"
        with open(dashboard_file, "w") as f:
            json.dump(self.dashboard_data, f, indent=2)

    def _calculate_trends(self) -> dict[str, str]:
        """Calculate metric trends."""
        trends = {}

        # Group metrics by name
        metrics_by_name = {}
        for metric in self.metrics_history:
            name = metric["name"]
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append(metric)

        # Calculate trends
        for name, metrics_list in metrics_by_name.items():
            if len(metrics_list) > 1:
                # Sort by timestamp
                sorted_metrics = sorted(metrics_list, key=lambda x: x["timestamp"])

                # Calculate trend
                first_value = sorted_metrics[0]["value"]
                last_value = sorted_metrics[-1]["value"]

                if first_value == 0:
                    change_percent = 0
                else:
                    change_percent = ((last_value - first_value) / first_value) * 100

                if change_percent > 5:
                    trends[name] = "increasing"
                elif change_percent < -5:
                    trends[name] = "decreasing"
                else:
                    trends[name] = "stable"

        return trends

    def _calculate_overall_health_score(self) -> float:
        """Calculate overall health score."""
        if not self.metrics_history:
            return 100.0

        # Get latest metrics
        latest_metrics = {}
        for metric in self.metrics_history[-10:]:
            latest_metrics[metric["name"]] = metric["value"]

        # Calculate score based on key metrics
        score = 100.0

        # Deduct for high resource usage
        if "system_cpu_usage" in latest_metrics and latest_metrics["system_cpu_usage"] > 90:
            score -= 20
        if "system_memory_usage" in latest_metrics and latest_metrics["system_memory_usage"] > 85:
            score -= 20

        # Deduct for low test coverage
        if "test_coverage" in latest_metrics and latest_metrics["test_coverage"] < 80:
            score -= 15

        # Deduct for security issues
        if "security_high_severity" in latest_metrics and latest_metrics["security_high_severity"] > 0:
            score -= 25

        # Deduct for low kit health
        if "kit_health_score" in latest_metrics and latest_metrics["kit_health_score"] < 70:
            score -= 10

        return max(0, min(100, score))

    def _generate_final_report(self) -> None:
        """Generate final observability report."""
        print("📊 Generating Final Observability Report...")

        # Calculate summary statistics
        total_metrics = len(self.metrics_history)
        total_alerts = len(self.alert_events)
        active_alerts = len([a for a in self.alert_events if not a.resolved])

        # Group alerts by severity
        alerts_by_severity = {}
        for alert in self.alert_events:
            severity = alert.severity
            if severity not in alerts_by_severity:
                alerts_by_severity[severity] = 0
            alerts_by_severity[severity] += 1

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_metrics_collected": total_metrics,
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "health_score": self._calculate_overall_health_score(),
                "alerts_by_severity": alerts_by_severity,
            },
            "dashboard_data": self.dashboard_data,
            "recent_metrics": self.metrics_history[-50:],  # Last 50 metrics
            "recent_alerts": self.alert_events[-20:],  # Last 20 alerts
            "trends": self._calculate_trends(),
        }

        # Save report
        report_file = self.reports_dir / f"observability_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Generate markdown summary
        summary_file = self.reports_dir / f"observability_summary_{int(time.time())}.md"
        self._generate_markdown_summary(report, summary_file)

        print("📊 Observability reports saved:")
        print(f"  JSON: {report_file}")
        print(f"  Summary: {summary_file}")

    def _generate_markdown_summary(self, report: dict[str, Any], file_path: Path) -> None:
        """Generate markdown summary report."""
        summary = report["summary"]

        content = f"""# Observability Dashboard Report

**Generated**: {report['timestamp']}
**Health Score**: {summary['health_score']:.1f}/100

## Summary

| Metric | Value |
|--------|-------|
| Total Metrics Collected | {summary['total_metrics_collected']} |
| Total Alerts | {summary['total_alerts']} |
| Active Alerts | {summary['active_alerts']} |
| Health Score | {summary['health_score']:.1f}/100 |

## Alerts by Severity

"""

        for severity, count in summary["alerts_by_severity"].items():
            content += f"- **{severity.title()}**: {count}\n"

        if report["recent_alerts"]:
            content += "\n## Recent Alerts\n\n"
            for alert in report["recent_alerts"][-10:]:  # Last 10
                severity_emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}.get(alert["severity"], "📢")
                content += f"- {severity_emoji} **{alert['severity'].upper()}**: {alert['message']}\n"

        if report["trends"]:
            content += "\n## Metric Trends\n\n"
            for metric, trend in report["trends"].items():
                trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(trend, "❓")
                content += f"- {trend_emoji} **{metric}**: {trend}\n"

        with open(file_path, "w") as f:
            f.write(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Observability Dashboard")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--duration", type=int, default=3600, help="Dashboard duration in seconds")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    dashboard = ObservabilityDashboard(args.project_root)

    try:
        dashboard.start_dashboard(args.duration)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        dashboard._generate_final_report()
    except Exception as e:
        print(f"❌ Error in dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
