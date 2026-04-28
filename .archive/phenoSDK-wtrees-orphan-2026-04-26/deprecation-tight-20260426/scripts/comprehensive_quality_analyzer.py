#!/usr/bin/env python3
"""
Comprehensive Quality Analyzer Runs all quality check tools and generates unified
reports for comprehensive code quality analysis.
"""
import argparse
import json
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class QualityReport:
    """
    Represents a quality analysis report.
    """

    tool: str
    status: str
    violations: int
    warnings: int
    errors: int
    duration: float
    report_path: str
    summary: dict[str, Any]


class ComprehensiveQualityAnalyzer:
    """
    Runs all quality check tools and generates unified reports.
    """

    def __init__(self):
        self.reports = []
        self.start_time = time.time()
        self.quality_tools = {
            "atlas_health": {
                "script": "scripts/atlas_health.py",
                "args": ["--report", "--json"],
                "description": "Atlas Health Analysis",
            },
            "pattern_detection": {
                "script": "scripts/advanced_pattern_detector.py",
                "args": ["--json"],
                "description": "Advanced Pattern Detection",
            },
            "architectural_validation": {
                "script": "scripts/architectural_pattern_validator.py",
                "args": ["--json"],
                "description": "Architectural Pattern Validation",
            },
            "performance_anti_patterns": {
                "script": "scripts/performance_anti_pattern_detector.py",
                "args": ["--json"],
                "description": "Performance Anti-Pattern Detection",
            },
            "security_scanning": {
                "script": "scripts/security_pattern_scanner.py",
                "args": ["--json"],
                "description": "Security Pattern Scanning",
            },
            "code_smell_detection": {
                "script": "scripts/code_smell_detector.py",
                "args": ["--json"],
                "description": "Code Smell Detection",
            },
            "integration_gates": {
                "script": "scripts/integration_quality_gates.py",
                "args": ["--json"],
                "description": "Integration Quality Gates",
            },
            "legacy_scanner": {
                "script": "scripts/legacy_code_scanner.py",
                "args": ["--json"],
                "description": "Legacy Code Scanner",
            },
        }

        # Quality thresholds
        self.thresholds = {
            "max_violations": 100,
            "max_warnings": 200,
            "max_errors": 50,
            "max_duration_minutes": 30,
        }

    def run_analysis(self, target_path: str = ".", output_dir: str = "reports") -> dict[str, Any]:
        """
        Run comprehensive quality analysis.
        """
        print("🔍 COMPREHENSIVE QUALITY ANALYSIS")
        print("=" * 50)
        print(f"Target: {target_path}")
        print(f"Output: {output_dir}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)

        # Run each quality tool
        for tool_name, tool_config in self.quality_tools.items():
            print(f"Running {tool_config['description']}...")
            report = self._run_quality_tool(tool_name, tool_config, target_path, output_dir)
            self.reports.append(report)

            if report.status == "success":
                print(f"  ✅ {tool_config['description']} completed ({report.duration:.2f}s)")
            else:
                print(f"  ❌ {tool_config['description']} failed: {report.status}")
            print()

        # Generate unified report
        unified_report = self._generate_unified_report()

        # Save unified report
        unified_report_path = Path(output_dir) / "unified_quality_report.json"
        with open(unified_report_path, "w") as f:
            json.dump(unified_report, f, indent=2)

        # Generate summary
        self._print_summary(unified_report)

        return unified_report

    def _run_quality_tool(
        self, tool_name: str, tool_config: dict[str, Any], target_path: str, output_dir: str,
    ) -> QualityReport:
        """
        Run a single quality tool.
        """
        start_time = time.time()

        try:
            # Prepare command
            cmd = ["python3", tool_config["script"]] + tool_config["args"] + [target_path]

            # Run the tool
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, timeout=300,  # 5 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                # Parse JSON output
                try:
                    data = json.loads(result.stdout)
                    violations = self._count_violations(data, "violations")
                    warnings = self._count_violations(data, "warnings")
                    errors = self._count_violations(data, "errors")

                    # Save individual report
                    report_path = Path(output_dir) / f"{tool_name}_report.json"
                    with open(report_path, "w") as f:
                        json.dump(data, f, indent=2)

                    return QualityReport(
                        tool=tool_name,
                        status="success",
                        violations=violations,
                        warnings=warnings,
                        errors=errors,
                        duration=duration,
                        report_path=str(report_path),
                        summary=data.get("summary", {}),
                    )
                except json.JSONDecodeError:
                    return QualityReport(
                        tool=tool_name,
                        status="json_parse_error",
                        violations=0,
                        warnings=0,
                        errors=1,
                        duration=duration,
                        report_path="",
                        summary={},
                    )
            else:
                return QualityReport(
                    tool=tool_name,
                    status="execution_error",
                    violations=0,
                    warnings=0,
                    errors=1,
                    duration=duration,
                    report_path="",
                    summary={"error": result.stderr},
                )

        except subprocess.TimeoutExpired:
            return QualityReport(
                tool=tool_name,
                status="timeout",
                violations=0,
                warnings=0,
                errors=1,
                duration=time.time() - start_time,
                report_path="",
                summary={},
            )
        except Exception as e:
            return QualityReport(
                tool=tool_name,
                status="exception",
                violations=0,
                warnings=0,
                errors=1,
                duration=time.time() - start_time,
                report_path="",
                summary={"error": str(e)},
            )

    def _count_violations(self, data: dict[str, Any], key: str) -> int:
        """
        Count violations in the data.
        """
        if key in data:
            if isinstance(data[key], list):
                return len(data[key])
            if isinstance(data[key], dict) and "count" in data[key]:
                return data[key]["count"]
            if isinstance(data[key], int):
                return data[key]

        # Try to find violations in summary
        if "summary" in data:
            summary = data["summary"]
            if key in summary:
                if isinstance(summary[key], int):
                    return summary[key]
                if isinstance(summary[key], dict) and "count" in summary[key]:
                    return summary[key]["count"]

        return 0

    def _generate_unified_report(self) -> dict[str, Any]:
        """
        Generate unified quality report.
        """
        total_duration = time.time() - self.start_time

        # Calculate totals
        total_violations = sum(report.violations for report in self.reports)
        total_warnings = sum(report.warnings for report in self.reports)
        total_errors = sum(report.errors for report in self.reports)

        # Count successful tools
        successful_tools = sum(1 for report in self.reports if report.status == "success")
        total_tools = len(self.reports)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            total_violations, total_warnings, total_errors,
        )

        # Group by severity
        severity_breakdown = self._calculate_severity_breakdown()

        # Tool status summary
        tool_status = {
            report.tool: {
                "status": report.status,
                "violations": report.violations,
                "warnings": report.warnings,
                "errors": report.errors,
                "duration": report.duration,
            }
            for report in self.reports
        }

        # Recommendations
        recommendations = self._generate_recommendations(
            total_violations, total_warnings, total_errors,
        )

        return {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "total_duration_seconds": total_duration,
                "total_tools": total_tools,
                "successful_tools": successful_tools,
                "failed_tools": total_tools - successful_tools,
            },
            "summary": {
                "total_violations": total_violations,
                "total_warnings": total_warnings,
                "total_errors": total_errors,
                "quality_score": quality_score,
                "severity_breakdown": severity_breakdown,
            },
            "tool_reports": tool_status,
            "recommendations": recommendations,
            "thresholds": self.thresholds,
            "quality_status": self._determine_quality_status(quality_score, total_errors),
        }

    def _calculate_quality_score(self, violations: int, warnings: int, errors: int) -> float:
        """
        Calculate overall quality score (0-100)
        """
        # Base score
        score = 100.0

        # Deduct points for issues
        score -= min(violations * 0.5, 30)  # Max 30 points for violations
        score -= min(warnings * 0.2, 20)  # Max 20 points for warnings
        score -= min(errors * 1.0, 50)  # Max 50 points for errors

        return max(score, 0.0)

    def _calculate_severity_breakdown(self) -> dict[str, int]:
        """
        Calculate severity breakdown across all tools.
        """
        breakdown = defaultdict(int)

        for report in self.reports:
            if report.status == "success" and report.summary:
                summary = report.summary
                if "severity_counts" in summary:
                    for severity, count in summary["severity_counts"].items():
                        breakdown[severity] += count

        return dict(breakdown)

    def _generate_recommendations(self, violations: int, warnings: int, errors: int) -> list[str]:
        """
        Generate recommendations based on analysis results.
        """
        recommendations = []

        if errors > 0:
            recommendations.append(
                "🚨 Critical: Fix all errors immediately - they may cause system failures",
            )

        if violations > self.thresholds["max_violations"]:
            recommendations.append(
                f"⚠️ High: {violations} violations exceed threshold ({self.thresholds['max_violations']}) - prioritize fixing high-severity issues",
            )

        if warnings > self.thresholds["max_warnings"]:
            recommendations.append(
                f"📝 Medium: {warnings} warnings exceed threshold ({self.thresholds['max_warnings']}) - address systematically",
            )

        if violations > 50:
            recommendations.append(
                "🔧 Consider refactoring large functions and classes to reduce complexity",
            )

        if warnings > 100:
            recommendations.append("📚 Improve code documentation and add type hints")

        if errors == 0 and violations < 20 and warnings < 50:
            recommendations.append(
                "✅ Excellent code quality! Consider adding more comprehensive tests",
            )

        return recommendations

    def _determine_quality_status(self, quality_score: float, errors: int) -> str:
        """
        Determine overall quality status.
        """
        if errors > 0:
            return "CRITICAL"
        if quality_score >= 90:
            return "EXCELLENT"
        if quality_score >= 80:
            return "GOOD"
        if quality_score >= 70:
            return "FAIR"
        if quality_score >= 60:
            return "POOR"
        return "CRITICAL"

    def _print_summary(self, report: dict[str, Any]) -> None:
        """
        Print analysis summary.
        """
        print("📊 QUALITY ANALYSIS SUMMARY")
        print("=" * 50)

        metadata = report["metadata"]
        summary = report["summary"]

        print(f"Analysis completed in {metadata['total_duration_seconds']:.2f} seconds")
        print(f"Tools executed: {metadata['successful_tools']}/{metadata['total_tools']}")
        print()

        print("📈 Quality Metrics:")
        print(f"  Violations: {summary['total_violations']}")
        print(f"  Warnings: {summary['total_warnings']}")
        print(f"  Errors: {summary['total_errors']}")
        print(f"  Quality Score: {summary['quality_score']:.1f}/100")
        print()

        print("🎯 Quality Status:")
        status = report["quality_status"]
        if status == "EXCELLENT":
            print(f"  {status} ✅ - Outstanding code quality!")
        elif status == "GOOD":
            print(f"  {status} ✅ - Good code quality with minor improvements needed")
        elif status == "FAIR":
            print(f"  {status} ⚠️ - Fair code quality, some improvements recommended")
        elif status == "POOR":
            print(f"  {status} ⚠️ - Poor code quality, significant improvements needed")
        else:
            print(f"  {status} 🚨 - Critical issues found, immediate action required")
        print()

        print("🔧 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        print()

        print("📁 Reports saved to reports/ directory")
        print("📄 Unified report: reports/unified_quality_report.json")


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Comprehensive Quality Analyzer")
    parser.add_argument("path", nargs="?", default=".", help="Path to analyze")
    parser.add_argument("--output", "-o", default="reports", help="Output directory")
    parser.add_argument("--json", action="store_true", help="Output JSON format only")
    parser.add_argument("--tool", help="Run specific tool only")
    parser.add_argument("--thresholds", help="Path to custom thresholds file")

    args = parser.parse_args()

    analyzer = ComprehensiveQualityAnalyzer()

    # Load custom thresholds if provided
    if args.thresholds:
        with open(args.thresholds) as f:
            custom_thresholds = json.load(f)
            analyzer.thresholds.update(custom_thresholds)

    # Run specific tool if requested
    if args.tool and args.tool in analyzer.quality_tools:
        tool_config = analyzer.quality_tools[args.tool]
        report = analyzer._run_quality_tool(args.tool, tool_config, args.path, args.output)
        if args.json:
            print(
                json.dumps(
                    {
                        "tool": report.tool,
                        "status": report.status,
                        "violations": report.violations,
                        "warnings": report.warnings,
                        "errors": report.errors,
                        "duration": report.duration,
                        "summary": report.summary,
                    },
                    indent=2,
                ),
            )
        else:
            print(f"Tool: {report.tool}")
            print(f"Status: {report.status}")
            print(f"Violations: {report.violations}")
            print(f"Warnings: {report.warnings}")
            print(f"Errors: {report.errors}")
            print(f"Duration: {report.duration:.2f}s")
    else:
        # Run comprehensive analysis
        report = analyzer.run_analysis(args.path, args.output)

        if args.json:
            print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
