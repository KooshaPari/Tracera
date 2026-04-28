"""
Test reporting utilities.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class TestReporter:
    """Comprehensive test reporting."""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)

    def generate_coverage_report(self, coverage_data: dict[str, Any]) -> str:
        """Generate detailed coverage report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_coverage": coverage_data.get("total_coverage", 0),
            "line_coverage": coverage_data.get("line_coverage", 0),
            "branch_coverage": coverage_data.get("branch_coverage", 0),
            "files": coverage_data.get("files", {}),
            "summary": self._analyze_coverage(coverage_data),
        }

        report_path = self.reports_dir / "coverage_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return str(report_path)

    def generate_performance_report(self, performance_data: dict[str, Any]) -> str:
        """Generate performance test report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": performance_data.get("test_suite", "unknown"),
            "total_tests": performance_data.get("total_tests", 0),
            "passed": performance_data.get("passed", 0),
            "failed": performance_data.get("failed", 0),
            "average_execution_time": performance_data.get("average_execution_time", 0),
            "slowest_tests": performance_data.get("slowest_tests", []),
            "memory_usage": performance_data.get("memory_usage", {}),
            "recommendations": self._analyze_performance(performance_data),
        }

        report_path = self.reports_dir / "performance_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return str(report_path)

    def generate_security_report(self, security_data: dict[str, Any]) -> str:
        """Generate security test report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": security_data.get("vulnerabilities", []),
            "security_tests_passed": security_data.get("passed", 0),
            "security_tests_failed": security_data.get("failed", 0),
            "risk_level": self._assess_security_risk(security_data),
            "recommendations": self._generate_security_recommendations(security_data),
        }

        report_path = self.reports_dir / "security_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return str(report_path)

    def _analyze_coverage(self, coverage_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze coverage data and provide insights."""
        total_coverage = coverage_data.get("total_coverage", 0)

        if total_coverage >= 90:
            status = "excellent"
        elif total_coverage >= 80:
            status = "good"
        elif total_coverage >= 70:
            status = "fair"
        else:
            status = "poor"

        return {
            "status": status,
            "target_met": total_coverage >= 80,
            "improvement_needed": max(0, 80 - total_coverage),
        }

    def _analyze_performance(self, performance_data: dict[str, Any]) -> list[str]:
        """Analyze performance data and provide recommendations."""
        recommendations = []

        avg_time = performance_data.get("average_execution_time", 0)
        if avg_time > 5.0:
            recommendations.append("Consider optimizing slow tests")

        memory_usage = performance_data.get("memory_usage", {})
        if memory_usage.get("peak_mb", 0) > 500:
            recommendations.append("High memory usage detected - consider memory optimization")

        return recommendations

    def _assess_security_risk(self, security_data: dict[str, Any]) -> str:
        """Assess overall security risk level."""
        vulnerabilities = security_data.get("vulnerabilities", [])
        failed_tests = security_data.get("failed", 0)

        if len(vulnerabilities) > 5 or failed_tests > 3:
            return "high"
        if len(vulnerabilities) > 2 or failed_tests > 1:
            return "medium"
        return "low"

    def _generate_security_recommendations(self, security_data: dict[str, Any]) -> list[str]:
        """Generate security recommendations."""
        recommendations = []

        vulnerabilities = security_data.get("vulnerabilities", [])
        if any(v.get("severity") == "high" for v in vulnerabilities):
            recommendations.append("Address high-severity vulnerabilities immediately")

        if security_data.get("failed", 0) > 0:
            recommendations.append("Fix failing security tests")

        return recommendations
