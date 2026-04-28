#!/usr/bin/env python3
"""
Monitoring Orchestrator
Orchestrates all monitoring and observability systems.
"""

import argparse
import json
import queue
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MonitoringSystem:
    """Monitoring system configuration."""

    name: str
    script: str
    interval: int  # seconds
    enabled: bool
    category: str
    priority: int  # 1 = highest, 5 = lowest


class MonitoringOrchestrator:
    """Orchestrates all monitoring and observability systems."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "monitoring"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Define monitoring systems
        self.monitoring_systems = [
            MonitoringSystem(
                name="ci_cd_monitoring",
                script="scripts/ci_cd_monitoring.py",
                interval=300,  # 5 minutes
                enabled=True,
                category="infrastructure",
                priority=1,
            ),
            MonitoringSystem(
                name="quality_metrics",
                script="scripts/quality_metrics_collector.py",
                interval=1800,  # 30 minutes
                enabled=True,
                category="quality",
                priority=2,
            ),
            MonitoringSystem(
                name="kit_health_monitor",
                script="scripts/kit_health_monitor.py",
                interval=3600,  # 1 hour
                enabled=True,
                category="health",
                priority=3,
            ),
            MonitoringSystem(
                name="observability_dashboard",
                script="scripts/observability_dashboard.py",
                interval=60,  # 1 minute
                enabled=True,
                category="dashboard",
                priority=1,
            ),
        ]

        self.running = False
        self.threads = []
        self.results_queue = queue.Queue()

    def start_monitoring(self, duration: int = 3600) -> None:
        """Start all monitoring systems."""
        print("🚀 Starting Monitoring Orchestrator...")

        self.running = True

        # Start each monitoring system
        for system in self.monitoring_systems:
            if system.enabled:
                print(f"  📊 Starting {system.name} (interval: {system.interval}s)")
                thread = threading.Thread(
                    target=self._run_monitoring_system,
                    args=(system,),
                    daemon=True,
                )
                thread.start()
                self.threads.append(thread)

        print(f"✅ Monitoring orchestrator running for {duration} seconds...")

        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")

        self.running = False

        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=10)

        # Generate final report
        self._generate_final_report()

    def _run_monitoring_system(self, system: MonitoringSystem) -> None:
        """Run a monitoring system in a loop."""
        while self.running:
            try:
                # Run the monitoring script
                result = subprocess.run(
                    [
                        "python",
                        system.script,
                        str(self.project_root),
                        "--json",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=system.interval,
                )

                # Process result
                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout)
                        self.results_queue.put(
                            {
                                "system": system.name,
                                "timestamp": time.time(),
                                "status": "success",
                                "data": data,
                            },
                        )
                    except json.JSONDecodeError:
                        self.results_queue.put(
                            {
                                "system": system.name,
                                "timestamp": time.time(),
                                "status": "error",
                                "error": "Invalid JSON output",
                            },
                        )
                else:
                    self.results_queue.put(
                        {
                            "system": system.name,
                            "timestamp": time.time(),
                            "status": "error",
                            "error": result.stderr,
                        },
                    )

            except subprocess.TimeoutExpired:
                self.results_queue.put(
                    {
                        "system": system.name,
                        "timestamp": time.time(),
                        "status": "timeout",
                        "error": f"Script timed out after {system.interval} seconds",
                    },
                )
            except Exception as e:
                self.results_queue.put(
                    {
                        "system": system.name,
                        "timestamp": time.time(),
                        "status": "error",
                        "error": str(e),
                    },
                )

            # Wait for next interval
            time.sleep(system.interval)

    def run_single_system(self, system_name: str) -> dict[str, Any]:
        """Run a single monitoring system."""
        system = next(
            (s for s in self.monitoring_systems if s.name == system_name), None,
        )
        if not system:
            return {"error": f"Unknown monitoring system: {system_name}"}

        print(f"🔍 Running {system.name}...")

        try:
            result = subprocess.run(
                [
                    "python",
                    system.script,
                    str(self.project_root),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "system": system.name,
                    "status": "success",
                    "data": data,
                }
            return {
                "system": system.name,
                "status": "error",
                "error": result.stderr,
            }

        except Exception as e:
            return {
                "system": system.name,
                "status": "error",
                "error": str(e),
            }

    def run_all_systems_once(self) -> dict[str, Any]:
        """Run all monitoring systems once."""
        print("🔍 Running All Monitoring Systems...")

        results = {}

        for system in self.monitoring_systems:
            if system.enabled:
                print(f"  📊 Running {system.name}...")
                result = self.run_single_system(system.name)
                results[system.name] = result

        return results

    def get_system_status(self) -> dict[str, Any]:
        """Get status of all monitoring systems."""
        status: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "systems": {},
            "overall_status": "unknown",
        }
        systems: dict[str, Any] = status["systems"]  # type: ignore

        for system in self.monitoring_systems:
            systems[system.name] = {
                "enabled": system.enabled,
                "interval": system.interval,
                "category": system.category,
                "priority": system.priority,
                "script_exists": (self.project_root / system.script).exists(),
            }

        # Determine overall status
        enabled_systems = [s for s in self.monitoring_systems if s.enabled]
        if len(enabled_systems) == 0:
            status["overall_status"] = "disabled"
        elif all((self.project_root / s.script).exists() for s in enabled_systems):
            status["overall_status"] = "ready"
        else:
            status["overall_status"] = "error"

        return status

    def _generate_final_report(self) -> None:
        """Generate final monitoring report."""
        print("📊 Generating Final Monitoring Report...")

        # Collect all results from queue
        results = []
        while not self.results_queue.empty():
            try:
                result = self.results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break

        # Group results by system
        results_by_system = {}
        for result in results:
            system = result["system"]
            if system not in results_by_system:
                results_by_system[system] = []
            results_by_system[system].append(result)

        # Calculate statistics
        total_runs = len(results)
        successful_runs = len([r for r in results if r["status"] == "success"])
        error_runs = len([r for r in results if r["status"] == "error"])
        timeout_runs = len([r for r in results if r["status"] == "timeout"])

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "error_runs": error_runs,
                "timeout_runs": timeout_runs,
                "success_rate": (successful_runs / total_runs * 100)
                if total_runs > 0
                else 0,
            },
            "results_by_system": results_by_system,
            "system_status": self.get_system_status(),
        }

        # Save report
        report_file = (
            self.reports_dir / f"monitoring_orchestrator_{int(time.time())}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Generate summary
        summary_file = self.reports_dir / f"monitoring_summary_{int(time.time())}.md"
        self._generate_summary_report(report, summary_file)

        print("📊 Monitoring reports saved:")
        print(f"  JSON: {report_file}")
        print(f"  Summary: {summary_file}")

    def _generate_summary_report(self, report: dict[str, Any], file_path: Path) -> None:
        """Generate markdown summary report."""
        summary = report["summary"]

        content = f"""# Monitoring Orchestrator Report

**Generated**: {report["timestamp"]}
**Success Rate**: {summary["success_rate"]:.1f}%

## Summary

| Metric | Value |
|--------|-------|
| Total Runs | {summary["total_runs"]} |
| Successful Runs | {summary["successful_runs"]} |
| Error Runs | {summary["error_runs"]} |
| Timeout Runs | {summary["timeout_runs"]} |
| Success Rate | {summary["success_rate"]:.1f}% |

## System Status

"""

        for system_name, system_status in report["system_status"]["systems"].items():
            status_emoji = (
                "✅"
                if system_status["enabled"] and system_status["script_exists"]
                else "❌"
            )
            content += f"### {system_name}\n"
            content += f"- **Status**: {status_emoji} {'Enabled' if system_status['enabled'] else 'Disabled'}\n"
            content += f"- **Interval**: {system_status['interval']}s\n"
            content += f"- **Category**: {system_status['category']}\n"
            content += f"- **Priority**: {system_status['priority']}\n"
            content += f"- **Script Exists**: {'Yes' if system_status['script_exists'] else 'No'}\n\n"

        # Add recent results
        if report["results_by_system"]:
            content += "## Recent Results\n\n"
            for system_name, system_results in report["results_by_system"].items():
                content += f"### {system_name}\n"
                recent_results = system_results[-5:]  # Last 5 results
                for result in recent_results:
                    status_emoji = "✅" if result["status"] == "success" else "❌"
                    content += f"- {status_emoji} {result['status']} ({datetime.fromtimestamp(result['timestamp']).strftime('%H:%M:%S')})\n"
                content += "\n"

        with open(file_path, "w") as f:
            f.write(content)


def main()  # noqa: PLR0912, PLR0915:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitoring Orchestrator")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--system", help="Run specific monitoring system")
    parser.add_argument("--once", action="store_true", help="Run all systems once")
    parser.add_argument(
        "--duration", type=int, default=3600, help="Monitoring duration in seconds",
    )
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    orchestrator = MonitoringOrchestrator(args.project_root)

    try:
        if args.status:
            # Show system status
            status = orchestrator.get_system_status()
            if args.json:
                output = json.dumps(status, indent=2)
            else:
                output = f"""
🔍 MONITORING SYSTEM STATUS
{"=" * 50}
Overall Status: {status["overall_status"].upper()}

Systems:
"""
                for system_name, system_status in status["systems"].items():
                    status_emoji = (
                        "✅"
                        if system_status["enabled"] and system_status["script_exists"]
                        else "❌"
                    )
                    output += f"  {status_emoji} {system_name}: {'Enabled' if system_status['enabled'] else 'Disabled'}\n"

            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
            else:
                print(output)

        elif args.system:
            # Run specific system
            result = orchestrator.run_single_system(args.system)
            if args.json:
                output = json.dumps(result, indent=2)
            else:
                output = f"""
🔍 {args.system.upper()} RESULT
{"=" * 50}
Status: {result["status"].upper()}
"""
                if result["status"] == "success":
                    output += f"Data: {json.dumps(result['data'], indent=2)}\n"
                else:
                    output += f"Error: {result['error']}\n"

            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
            else:
                print(output)

        elif args.once:
            # Run all systems once
            results = orchestrator.run_all_systems_once()
            if args.json:
                output = json.dumps(results, indent=2)
            else:
                output = f"""
🔍 ALL SYSTEMS RESULT
{"=" * 50}
"""
                for system_name, result in results.items():
                    status_emoji = "✅" if result["status"] == "success" else "❌"
                    output += f"{status_emoji} {system_name}: {result['status']}\n"

            if args.output:
                with open(args.output, "w") as f:
                    f.write(output)
            else:
                print(output)

        else:
            # Start continuous monitoring
            orchestrator.start_monitoring(args.duration)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error in monitoring orchestrator: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
