#!/usr/bin/env python3
"""
Kit Health Monitoring System
Comprehensive monitoring for individual kits and their health.
"""

import argparse
import ast
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class KitHealthMetric:
    """Kit health metric."""
    kit_name: str
    metric_name: str
    value: float
    unit: str
    timestamp: float
    status: str  # "healthy", "warning", "critical", "unknown"
    threshold: float | None = None


@dataclass
class KitHealthStatus:
    """Overall kit health status."""
    kit_name: str
    overall_status: str
    health_score: float
    metrics: list[KitHealthMetric]
    issues: list[str]
    recommendations: list[str]
    last_updated: float


class KitHealthMonitor:
    """Comprehensive kit health monitoring system."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.reports_dir = self.project_root / "reports" / "kit_health"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.kit_statuses = {}

        # Kit health thresholds
        self.thresholds = {
            "test_coverage": 80.0,
            "complexity": 10.0,
            "maintainability": 70.0,
            "documentation": 60.0,
            "dependencies": 5.0,
            "file_size": 500.0,
            "function_count": 20.0,
        }

    def monitor_all_kits(self) -> dict[str, Any]:
        """Monitor health of all kits."""
        print("🔍 Monitoring Kit Health...")

        # Discover kits
        kits = self._discover_kits()
        print(f"Found {len(kits)} kits to monitor")

        # Monitor each kit
        for kit_name in kits:
            print(f"  📦 Monitoring kit: {kit_name}")
            self._monitor_kit(kit_name)

        # Generate comprehensive report
        return self._generate_kit_health_report()

    def _discover_kits(self) -> list[str]:
        """Discover all kits in the project."""
        kits = []

        # Look for kit directories in src
        if self.src_path.exists():
            for item in self.src_path.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    # Check if it looks like a kit (has __init__.py or main module)
                    if (item / "__init__.py").exists() or any(item.glob("*.py")):
                        kits.append(item.name)

        # Also check for sub-kits
        for kit_dir in self.src_path.rglob("*"):
            if kit_dir.is_dir() and kit_dir != self.src_path:
                relative_path = kit_dir.relative_to(self.src_path)
                if len(relative_path.parts) == 1:  # Top-level kits only
                    continue

                # Check if it's a sub-kit
                if (kit_dir / "__init__.py").exists() or any(kit_dir.glob("*.py")):
                    kit_name = ".".join(relative_path.parts)
                    if kit_name not in kits:
                        kits.append(kit_name)

        return kits

    def _monitor_kit(self, kit_name: str) -> None:
        """Monitor health of a specific kit."""
        kit_path = self._get_kit_path(kit_name)
        if not kit_path:
            return

        metrics = []
        issues = []
        recommendations = []

        # Collect various health metrics
        self._collect_kit_metrics(kit_name, kit_path, metrics)
        self._analyze_kit_structure(kit_name, kit_path, metrics, issues)
        self._check_kit_dependencies(kit_name, kit_path, metrics, issues)
        self._validate_kit_tests(kit_name, kit_path, metrics, issues)
        self._assess_kit_documentation(kit_name, kit_path, metrics, issues)
        self._check_kit_performance(kit_name, kit_path, metrics, issues)

        # Calculate overall health score
        health_score = self._calculate_kit_health_score(metrics)

        # Determine overall status
        overall_status = self._determine_kit_status(health_score, issues)

        # Generate recommendations
        recommendations = self._generate_kit_recommendations(metrics, issues)

        # Store kit status
        self.kit_statuses[kit_name] = KitHealthStatus(
            kit_name=kit_name,
            overall_status=overall_status,
            health_score=health_score,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            last_updated=time.time(),
        )

    def _get_kit_path(self, kit_name: str) -> Path | None:
        """Get the path to a kit."""
        if "." in kit_name:
            # Sub-kit
            parts = kit_name.split(".")
            kit_path = self.src_path
            for part in parts:
                kit_path = kit_path / part
            return kit_path if kit_path.exists() else None
        # Top-level kit
        kit_path = self.src_path / kit_name
        return kit_path if kit_path.exists() else None

    def _collect_kit_metrics(self, kit_name: str, kit_path: Path, metrics: list[KitHealthMetric]) -> None:
        """Collect basic metrics for a kit."""
        # Count files
        python_files = list(kit_path.rglob("*.py"))
        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="python_files",
            value=len(python_files),
            unit="count",
            timestamp=time.time(),
            status="healthy",
        ))

        # Count lines of code
        total_lines = 0
        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    total_lines += len(f.readlines())
            except Exception:
                pass

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="lines_of_code",
            value=total_lines,
            unit="lines",
            timestamp=time.time(),
            status="healthy",
        ))

        # Average file size
        if python_files:
            avg_file_size = total_lines / len(python_files)
            metrics.append(KitHealthMetric(
                kit_name=kit_name,
                metric_name="avg_file_size",
                value=avg_file_size,
                unit="lines",
                timestamp=time.time(),
                status="warning" if avg_file_size > self.thresholds["file_size"] else "healthy",
                threshold=self.thresholds["file_size"],
            ))

    def _analyze_kit_structure(self, kit_name: str, kit_path: Path,
                              metrics: list[KitHealthMetric], issues: list[str]) -> None:
        """Analyze kit structure and complexity."""
        python_files = list(kit_path.rglob("*.py"))

        # Count functions and classes
        total_functions = 0
        total_classes = 0
        complex_functions = 0

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST for better analysis
                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1
                            # Simple complexity analysis
                            complexity = len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))])
                            if complexity > self.thresholds["complexity"]:
                                complex_functions += 1
                        elif isinstance(node, ast.ClassDef):
                            total_classes += 1

                except SyntaxError:
                    # Fallback to regex if AST parsing fails
                    import re
                    functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
                    total_functions += len(functions)

                    classes = re.findall(r"class\s+(\w+)", content)
                    total_classes += len(classes)

            except Exception as e:
                issues.append(f"Error analyzing {py_file.name}: {e}")

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="total_functions",
            value=total_functions,
            unit="count",
            timestamp=time.time(),
            status="warning" if total_functions > self.thresholds["function_count"] else "healthy",
            threshold=self.thresholds["function_count"],
        ))

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="total_classes",
            value=total_classes,
            unit="count",
            timestamp=time.time(),
            status="healthy",
        ))

        if total_functions > 0:
            complexity_ratio = (complex_functions / total_functions) * 100
            metrics.append(KitHealthMetric(
                kit_name=kit_name,
                metric_name="complex_functions_ratio",
                value=complexity_ratio,
                unit="percent",
                timestamp=time.time(),
                status="warning" if complexity_ratio > 20 else "healthy",
                threshold=20.0,
            ))

    def _check_kit_dependencies(self, kit_name: str, kit_path: Path,
                               metrics: list[KitHealthMetric], issues: list[str]) -> None:
        """Check kit dependencies and imports."""
        python_files = list(kit_path.rglob("*.py"))

        external_imports = set()
        internal_imports = set()
        circular_imports = []

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse imports
                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                external_imports.add(alias.name.split(".")[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                module_name = node.module.split(".")[0]
                                if module_name.startswith("pheno"):
                                    internal_imports.add(module_name)
                                else:
                                    external_imports.add(module_name)

                except SyntaxError:
                    # Fallback to regex
                    import re
                    import_lines = re.findall(r"^(?:from\s+(\S+)\s+)?import\s+(\S+)", content, re.MULTILINE)
                    for from_module, import_name in import_lines:
                        if from_module:
                            if from_module.startswith("pheno"):
                                internal_imports.add(from_module.split(".")[0])
                            else:
                                external_imports.add(from_module.split(".")[0])
                        else:
                            external_imports.add(import_name.split(".")[0])

            except Exception as e:
                issues.append(f"Error analyzing imports in {py_file.name}: {e}")

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="external_dependencies",
            value=len(external_imports),
            unit="count",
            timestamp=time.time(),
            status="warning" if len(external_imports) > self.thresholds["dependencies"] else "healthy",
            threshold=self.thresholds["dependencies"],
        ))

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="internal_dependencies",
            value=len(internal_imports),
            unit="count",
            timestamp=time.time(),
            status="healthy",
        ))

        if len(external_imports) > 10:
            issues.append(f"High number of external dependencies: {len(external_imports)}")

    def _validate_kit_tests(self, kit_name: str, kit_path: Path,
                           metrics: list[KitHealthMetric], issues: list[str]) -> None:
        """Validate kit tests."""
        # Look for test files
        test_files = list(kit_path.rglob("test_*.py")) + list(kit_path.rglob("*_test.py"))

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="test_files",
            value=len(test_files),
            unit="count",
            timestamp=time.time(),
            status="warning" if len(test_files) == 0 else "healthy",
        ))

        if len(test_files) == 0:
            issues.append("No test files found")

        # Check for test coverage (if available)
        coverage_file = self.project_root / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                # Find coverage for this kit
                kit_coverage = 0
                kit_files = 0

                for file_path, file_data in coverage_data.get("files", {}).items():
                    if kit_name in file_path:
                        kit_coverage += file_data.get("summary", {}).get("percent_covered", 0)
                        kit_files += 1

                if kit_files > 0:
                    avg_coverage = kit_coverage / kit_files
                    metrics.append(KitHealthMetric(
                        kit_name=kit_name,
                        metric_name="test_coverage",
                        value=avg_coverage,
                        unit="percent",
                        timestamp=time.time(),
                        status="warning" if avg_coverage < self.thresholds["test_coverage"] else "healthy",
                        threshold=self.thresholds["test_coverage"],
                    ))

            except Exception as e:
                issues.append(f"Error reading coverage data: {e}")

    def _assess_kit_documentation(self, kit_name: str, kit_path: Path,
                                 metrics: list[KitHealthMetric], issues: list[str]) -> None:
        """Assess kit documentation."""
        python_files = list(kit_path.rglob("*.py"))

        # Check for README
        readme_files = list(kit_path.glob("README*.md"))
        has_readme = len(readme_files) > 0

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="has_readme",
            value=1 if has_readme else 0,
            unit="boolean",
            timestamp=time.time(),
            status="warning" if not has_readme else "healthy",
        ))

        if not has_readme:
            issues.append("No README file found")

        # Check docstring coverage
        total_functions = 0
        documented_functions = 0

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Count functions with docstrings
                import re
                functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
                total_functions += len(functions)

                for func_name in functions:
                    func_pattern = rf'def\s+{func_name}\s*\([^)]*\):\s*\n\s*""".*?"""'
                    if re.search(func_pattern, content, re.DOTALL):
                        documented_functions += 1

            except Exception as e:
                issues.append(f"Error analyzing documentation in {py_file.name}: {e}")

        if total_functions > 0:
            docstring_coverage = (documented_functions / total_functions) * 100
            metrics.append(KitHealthMetric(
                kit_name=kit_name,
                metric_name="docstring_coverage",
                value=docstring_coverage,
                unit="percent",
                timestamp=time.time(),
                status="warning" if docstring_coverage < self.thresholds["documentation"] else "healthy",
                threshold=self.thresholds["documentation"],
            ))

    def _check_kit_performance(self, kit_name: str, kit_path: Path,
                              metrics: list[KitHealthMetric], issues: list[str]) -> None:
        """Check kit performance characteristics."""
        python_files = list(kit_path.rglob("*.py"))

        # Check for performance-related issues
        performance_issues = 0

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Look for common performance anti-patterns
                if "time.sleep(" in content:
                    performance_issues += 1
                if "while True:" in content:
                    performance_issues += 1
                if "for i in range(" in content and "for j in range(" in content:
                    performance_issues += 1  # Nested loops

            except Exception as e:
                issues.append(f"Error analyzing performance in {py_file.name}: {e}")

        metrics.append(KitHealthMetric(
            kit_name=kit_name,
            metric_name="performance_issues",
            value=performance_issues,
            unit="count",
            timestamp=time.time(),
            status="warning" if performance_issues > 0 else "healthy",
        ))

        if performance_issues > 0:
            issues.append(f"Potential performance issues found: {performance_issues}")

    def _calculate_kit_health_score(self, metrics: list[KitHealthMetric]) -> float:
        """Calculate overall health score for a kit."""
        if not metrics:
            return 0.0

        # Weight different metrics
        metric_weights = {
            "test_coverage": 0.25,
            "docstring_coverage": 0.20,
            "complex_functions_ratio": 0.15,
            "external_dependencies": 0.10,
            "avg_file_size": 0.10,
            "test_files": 0.10,
            "has_readme": 0.10,
        }

        weighted_score = 0.0
        total_weight = 0.0

        for metric in metrics:
            if metric.metric_name in metric_weights:
                weight = metric_weights[metric.metric_name]

                # Calculate score based on metric type
                if metric.metric_name in ["test_coverage", "docstring_coverage"]:
                    # Higher is better
                    score = min(100, metric.value)
                elif metric.metric_name in ["complex_functions_ratio", "external_dependencies", "avg_file_size"]:
                    # Lower is better
                    threshold = metric.threshold or 50
                    score = max(0, 100 - (metric.value / threshold) * 100)
                elif metric.metric_name == "test_files":
                    # Higher is better, but cap at reasonable number
                    score = min(100, metric.value * 10)
                elif metric.metric_name == "has_readme":
                    # Boolean
                    score = 100 if metric.value > 0 else 0
                else:
                    score = 50  # Default

                weighted_score += score * weight
                total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 50.0

    def _determine_kit_status(self, health_score: float, issues: list[str]) -> str:
        """Determine overall kit status."""
        if health_score >= 80 and len(issues) == 0:
            return "healthy"
        if health_score >= 60 and len(issues) <= 2:
            return "warning"
        if health_score >= 40:
            return "critical"
        return "unknown"

    def _generate_kit_recommendations(self, metrics: list[KitHealthMetric], issues: list[str]) -> list[str]:
        """Generate recommendations for kit improvement."""
        recommendations = []

        # Check specific metrics
        for metric in metrics:
            if metric.status == "warning" or metric.status == "critical":
                if metric.metric_name == "test_coverage" and metric.value < 80:
                    recommendations.append(f"Increase test coverage from {metric.value:.1f}% to at least 80%")
                elif metric.metric_name == "docstring_coverage" and metric.value < 60:
                    recommendations.append(f"Add docstrings to improve documentation coverage from {metric.value:.1f}%")
                elif metric.metric_name == "avg_file_size" and metric.value > 500:
                    recommendations.append(f"Split large files (avg {metric.value:.0f} lines) into smaller modules")
                elif metric.metric_name == "external_dependencies" and metric.value > 5:
                    recommendations.append(f"Reduce external dependencies (currently {metric.value:.0f})")
                elif metric.metric_name == "test_files" and metric.value == 0:
                    recommendations.append("Add test files to improve code reliability")
                elif metric.metric_name == "has_readme" and metric.value == 0:
                    recommendations.append("Add a README file to document the kit")

        # Add general recommendations based on issues
        if "No test files found" in issues:
            recommendations.append("Create comprehensive test suite")
        if "No README file found" in issues:
            recommendations.append("Add documentation for the kit")
        if any("performance" in issue.lower() for issue in issues):
            recommendations.append("Review and optimize performance-critical code")

        return recommendations

    def _generate_kit_health_report(self) -> dict[str, Any]:
        """Generate comprehensive kit health report."""
        print("📊 Generating Kit Health Report...")

        # Calculate overall statistics
        total_kits = len(self.kit_statuses)
        healthy_kits = len([k for k in self.kit_statuses.values() if k.overall_status == "healthy"])
        warning_kits = len([k for k in self.kit_statuses.values() if k.overall_status == "warning"])
        critical_kits = len([k for k in self.kit_statuses.values() if k.overall_status == "critical"])

        # Calculate average health score
        if total_kits > 0:
            avg_health_score = sum(k.health_score for k in self.kit_statuses.values()) / total_kits
        else:
            avg_health_score = 0.0

        # Generate recommendations
        all_recommendations = []
        for kit_status in self.kit_statuses.values():
            all_recommendations.extend(kit_status.recommendations)

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_kits": total_kits,
                "healthy_kits": healthy_kits,
                "warning_kits": warning_kits,
                "critical_kits": critical_kits,
                "average_health_score": round(avg_health_score, 1),
                "overall_health": "healthy" if critical_kits == 0 and warning_kits <= total_kits // 2 else "warning",
            },
            "kit_statuses": {name: asdict(status) for name, status in self.kit_statuses.items()},
            "recommendations": list(set(all_recommendations)),  # Remove duplicates
            "thresholds": self.thresholds,
        }

        # Save report
        self._save_kit_health_report(report)

        return report

    def _save_kit_health_report(self, report: dict[str, Any]) -> None:
        """Save kit health report."""
        # Save JSON report
        json_file = self.reports_dir / f"kit_health_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save summary report
        summary_file = self.reports_dir / f"kit_health_summary_{int(time.time())}.md"
        self._save_kit_health_summary(report, summary_file)

        print("📊 Kit health reports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Summary: {summary_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Kit Health Monitor")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--kit", help="Monitor specific kit only")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    monitor = KitHealthMonitor(args.project_root)

    if args.kit:
        # Monitor specific kit
        monitor._monitor_kit(args.kit)
        report = monitor._generate_kit_health_report()
    else:
        # Monitor all kits
        report = monitor.monitor_all_kits()

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        # Pretty print format
        summary = report["summary"]
        output = f"""
🔍 KIT HEALTH REPORT
{'=' * 50}
Total Kits: {summary['total_kits']}
Healthy: {summary['healthy_kits']}
Warning: {summary['warning_kits']}
Critical: {summary['critical_kits']}
Average Health Score: {summary['average_health_score']}/100
Overall Health: {summary['overall_health'].upper()}

Kit Status:
"""
        for kit_name, kit_status in report["kit_statuses"].items():
            status_emoji = "✅" if kit_status["overall_status"] == "healthy" else "⚠️" if kit_status["overall_status"] == "warning" else "❌"
            output += f"  {status_emoji} {kit_name}: {kit_status['health_score']:.1f}/100\n"

        if report["recommendations"]:
            output += "\nRecommendations:\n"
            for rec in report["recommendations"][:10]:  # Show first 10
                output += f"  • {rec}\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
