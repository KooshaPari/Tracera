#!/usr/bin/env python3
"""
Advanced Analytics and Reporting Dashboard
Comprehensive analytics dashboard with predictive analytics and business intelligence.
"""

import argparse
import json
import statistics
import sys
import threading
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import psutil


@dataclass
class AnalyticsMetric:
    """Analytics metric data."""

    name: str
    value: float
    unit: str
    timestamp: float
    category: str
    trend: str  # "increasing", "decreasing", "stable"
    change_percent: float
    forecast: float | None = None
    confidence: float | None = None


@dataclass
class KPIMetric:
    """Key Performance Indicator metric."""

    name: str
    current_value: float
    target_value: float
    unit: str
    status: str  # "excellent", "good", "warning", "critical"
    trend: str
    change_percent: float
    last_updated: float


@dataclass
class PredictiveInsight:
    """Predictive analytics insight."""

    metric_name: str
    prediction: str
    confidence: float
    timeframe: str
    recommendation: str
    impact: str  # "high", "medium", "low"


class DataCollector:
    """Comprehensive data collection system."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.metrics = []
        self.kpis = {}
        self.insights = []

        # Data collection configuration
        self.collection_interval = 60  # seconds
        self.retention_days = 30
        self.collecting = False
        self.collection_thread = None

    def start_collection(self) -> None:
        """Start continuous data collection."""
        self.collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True,
        )
        self.collection_thread.start()
        print("📊 Started data collection...")

    def stop_collection(self) -> None:
        """Stop data collection."""
        self.collecting = False
        if self.collection_thread:
            self.collection_thread.join()
        print("📊 Stopped data collection...")

    def _collection_loop(self) -> None:
        """Main data collection loop."""
        while self.collecting:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Collect project metrics
                self._collect_project_metrics()

                # Collect quality metrics
                self._collect_quality_metrics()

                # Collect performance metrics
                self._collect_performance_metrics()

                # Collect security metrics
                self._collect_security_metrics()

                # Clean old data
                self._clean_old_data()

                time.sleep(self.collection_interval)

            except Exception as e:
                print(f"Error in data collection: {e}")
                time.sleep(self.collection_interval)

    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        timestamp = time.time()

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.append(
            AnalyticsMetric(
                name="system_cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                category="system",
                trend="stable",
                change_percent=0.0,
            ),
        )

        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics.append(
            AnalyticsMetric(
                name="system_memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=timestamp,
                category="system",
                trend="stable",
                change_percent=0.0,
            ),
        )

        # Disk usage
        disk = psutil.disk_usage("/")
        disk_percent = (disk.used / disk.total) * 100
        self.metrics.append(
            AnalyticsMetric(
                name="system_disk_usage",
                value=disk_percent,
                unit="percent",
                timestamp=timestamp,
                category="system",
                trend="stable",
                change_percent=0.0,
            ),
        )

        # Process count
        process_count = len(psutil.pids())
        self.metrics.append(
            AnalyticsMetric(
                name="system_process_count",
                value=process_count,
                unit="count",
                timestamp=timestamp,
                category="system",
                trend="stable",
                change_percent=0.0,
            ),
        )

    def _collect_project_metrics(self) -> None:
        """Collect project-specific metrics."""
        timestamp = time.time()

        # Code metrics
        code_metrics = self._analyze_code_metrics()
        for name, value in code_metrics.items():
            self.metrics.append(
                AnalyticsMetric(
                    name=name,
                    value=value,
                    unit="count",
                    timestamp=timestamp,
                    category="project",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

        # File metrics
        file_metrics = self._analyze_file_metrics()
        for name, value in file_metrics.items():
            self.metrics.append(
                AnalyticsMetric(
                    name=name,
                    value=value,
                    unit="count",
                    timestamp=timestamp,
                    category="project",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

    def _collect_quality_metrics(self) -> None:
        """Collect quality metrics."""
        timestamp = time.time()

        # Test coverage
        coverage = self._get_test_coverage()
        if coverage is not None:
            self.metrics.append(
                AnalyticsMetric(
                    name="test_coverage",
                    value=coverage,
                    unit="percent",
                    timestamp=timestamp,
                    category="quality",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

        # Code quality score
        quality_score = self._get_code_quality_score()
        if quality_score is not None:
            self.metrics.append(
                AnalyticsMetric(
                    name="code_quality_score",
                    value=quality_score,
                    unit="score",
                    timestamp=timestamp,
                    category="quality",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

        # Security score
        security_score = self._get_security_score()
        if security_score is not None:
            self.metrics.append(
                AnalyticsMetric(
                    name="security_score",
                    value=security_score,
                    unit="score",
                    timestamp=timestamp,
                    category="quality",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

    def _collect_performance_metrics(self) -> None:
        """Collect performance metrics."""
        timestamp = time.time()

        # Build time
        build_time = self._get_build_time()
        if build_time is not None:
            self.metrics.append(
                AnalyticsMetric(
                    name="build_time",
                    value=build_time,
                    unit="seconds",
                    timestamp=timestamp,
                    category="performance",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

        # Test execution time
        test_time = self._get_test_execution_time()
        if test_time is not None:
            self.metrics.append(
                AnalyticsMetric(
                    name="test_execution_time",
                    value=test_time,
                    unit="seconds",
                    timestamp=timestamp,
                    category="performance",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

    def _collect_security_metrics(self) -> None:
        """Collect security metrics."""
        timestamp = time.time()

        # Security vulnerabilities
        vuln_count = self._get_vulnerability_count()
        if vuln_count is not None:
            self.metrics.append(
                AnalyticsMetric(
                    name="security_vulnerabilities",
                    value=vuln_count,
                    unit="count",
                    timestamp=timestamp,
                    category="security",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

        # Dependency issues
        dep_issues = self._get_dependency_issues()
        if dep_issues is not None:
            self.metrics.append(
                AnalyticsMetric(
                    name="dependency_issues",
                    value=dep_issues,
                    unit="count",
                    timestamp=timestamp,
                    category="security",
                    trend="stable",
                    change_percent=0.0,
                ),
            )

    def _analyze_code_metrics(self) -> dict[str, float]:
        """Analyze code metrics."""
        metrics = {}

        try:
            # Count Python files
            python_files = list(self.project_root.rglob("*.py"))
            metrics["python_files"] = len(python_files)

            # Count lines of code
            total_lines = 0
            for py_file in python_files:
                try:
                    with open(py_file, encoding="utf-8") as f:
                        total_lines += len(f.readlines())
                except Exception:
                    pass
            metrics["total_lines_of_code"] = total_lines

            # Count functions
            function_count = 0
            for py_file in python_files:
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()
                        function_count += content.count("def ")
                except Exception:
                    pass
            metrics["function_count"] = function_count

            # Count classes
            class_count = 0
            for py_file in python_files:
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()
                        class_count += content.count("class ")
                except Exception:
                    pass
            metrics["class_count"] = class_count

        except Exception as e:
            print(f"Error analyzing code metrics: {e}")

        return metrics

    def _analyze_file_metrics(self) -> dict[str, float]:
        """Analyze file metrics."""
        metrics = {}

        try:
            # Count different file types
            file_types = defaultdict(int)
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file():
                    suffix = file_path.suffix.lower()
                    file_types[suffix] += 1

            metrics["total_files"] = sum(file_types.values())
            metrics["python_files"] = file_types.get(".py", 0)
            metrics["markdown_files"] = file_types.get(".md", 0)
            metrics["yaml_files"] = file_types.get(".yml", 0) + file_types.get(
                ".yaml",
                0,
            )
            metrics["json_files"] = file_types.get(".json", 0)
            metrics["txt_files"] = file_types.get(".txt", 0)

        except Exception as e:
            print(f"Error analyzing file metrics: {e}")

        return metrics

    def _get_test_coverage(self) -> float | None:
        """Get test coverage percentage."""
        try:
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                return coverage_data.get("totals", {}).get("percent_covered", 0)
        except Exception:
            pass
        return None

    def _get_code_quality_score(self) -> float | None:
        """Get code quality score."""
        try:
            # This would typically run quality analysis tools
            # For now, return a simulated score
            return 85.0
        except Exception:
            return None

    def _get_security_score(self) -> float | None:
        """Get security score."""
        try:
            # This would typically run security analysis tools
            # For now, return a simulated score
            return 90.0
        except Exception:
            return None

    def _get_build_time(self) -> float | None:
        """Get build time in seconds."""
        try:
            # This would typically measure actual build time
            # For now, return a simulated value
            return 45.0
        except Exception:
            return None

    def _get_test_execution_time(self) -> float | None:
        """Get test execution time in seconds."""
        try:
            # This would typically measure actual test time
            # For now, return a simulated value
            return 120.0
        except Exception:
            return None

    def _get_vulnerability_count(self) -> float | None:
        """Get security vulnerability count."""
        try:
            # This would typically run security scanning tools
            # For now, return a simulated value
            return 0.0
        except Exception:
            return None

    def _get_dependency_issues(self) -> float | None:
        """Get dependency issue count."""
        try:
            # This would typically run dependency scanning tools
            # For now, return a simulated value
            return 0.0
        except Exception:
            return None

    def _clean_old_data(self) -> None:
        """Clean old data beyond retention period."""
        cutoff_time = time.time() - (self.retention_days * 24 * 60 * 60)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]


class PredictiveAnalytics:
    """Predictive analytics engine."""

    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self.insights = []

    def generate_predictions(self) -> list[PredictiveInsight]:
        """Generate predictive insights."""
        print("🔮 Generating predictive insights...")

        insights = []

        # Analyze trends for each metric
        metrics_by_name = defaultdict(list)
        for metric in self.data_collector.metrics:
            metrics_by_name[metric.name].append(metric)

        for metric_name, metrics in metrics_by_name.items():
            if len(metrics) < 3:  # Need at least 3 data points
                continue

            # Sort by timestamp
            sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)

            # Calculate trend
            trend = self._calculate_trend(sorted_metrics)

            # Generate prediction
            prediction = self._generate_prediction(metric_name, sorted_metrics, trend)
            if prediction:
                insights.append(prediction)

        self.insights = insights
        return insights

    def _calculate_trend(self, metrics: list[AnalyticsMetric]) -> str:
        """Calculate trend for a metric."""
        if len(metrics) < 2:
            return "stable"

        values = [m.value for m in metrics]

        # Simple linear regression
        x = np.arange(len(values))
        y = np.array(values)

        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]

            if slope > 0.1:
                return "increasing"
            if slope < -0.1:
                return "decreasing"
            return "stable"

        return "stable"

    def _generate_prediction(
        self,
        metric_name: str,
        metrics: list[AnalyticsMetric],
        trend: str,
    ) -> PredictiveInsight | None:
        """Generate prediction for a metric."""
        if len(metrics) < 3:
            return None

        values = [m.value for m in metrics]
        current_value = values[-1]

        # Simple linear extrapolation
        x = np.arange(len(values))
        y = np.array(values)

        if len(x) > 1:
            slope, intercept = np.polyfit(x, y, 1)

            # Predict next 3 values
            next_x = len(values)
            predicted_value = slope * next_x + intercept

            # Calculate confidence based on R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            confidence = max(0, min(1, r_squared))

            # Generate prediction text
            change_percent = (
                ((predicted_value - current_value) / current_value * 100)
                if current_value != 0
                else 0
            )

            if abs(change_percent) < 5:
                prediction_text = f"Stable around {current_value:.1f}"
            elif change_percent > 0:
                prediction_text = (
                    f"Increase to {predicted_value:.1f} (+{change_percent:.1f}%)"
                )
            else:
                prediction_text = (
                    f"Decrease to {predicted_value:.1f} ({change_percent:.1f}%)"
                )

            # Generate recommendation
            recommendation = self._generate_recommendation(
                metric_name,
                trend,
                change_percent,
            )

            # Determine impact
            impact = (
                "high"
                if abs(change_percent) > 20
                else "medium"
                if abs(change_percent) > 10
                else "low"
            )

            return PredictiveInsight(
                metric_name=metric_name,
                prediction=prediction_text,
                confidence=confidence,
                timeframe="7 days",
                recommendation=recommendation,
                impact=impact,
            )

        return None

    def _generate_recommendation(
        self,
        metric_name: str,
        trend: str,
        change_percent: float,
    ) -> str:
        """Generate recommendation based on metric and trend."""
        if "cpu_usage" in metric_name:
            if trend == "increasing" and change_percent > 10:
                return "Consider optimizing CPU usage or scaling resources"
            if trend == "decreasing":
                return "CPU usage is improving, monitor for consistency"

        elif "memory_usage" in metric_name:
            if trend == "increasing" and change_percent > 10:
                return "Memory usage is increasing, investigate memory leaks"
            if trend == "decreasing":
                return "Memory usage is improving, continue monitoring"

        elif "test_coverage" in metric_name:
            if trend == "decreasing":
                return "Test coverage is decreasing, add more tests"
            if trend == "increasing":
                return "Test coverage is improving, maintain current practices"

        elif "security_score" in metric_name:
            if trend == "decreasing":
                return "Security score is decreasing, review security practices"
            if trend == "increasing":
                return "Security score is improving, continue security efforts"

        elif "build_time" in metric_name:
            if trend == "increasing" and change_percent > 20:
                return "Build time is increasing significantly, optimize build process"
            if trend == "decreasing":
                return "Build time is improving, maintain optimization efforts"

        return "Continue monitoring this metric"


class KPICalculator:
    """Key Performance Indicator calculator."""

    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self.kpis = {}

    def calculate_kpis(self) -> dict[str, KPIMetric]:
        """Calculate key performance indicators."""
        print("📊 Calculating KPIs...")

        kpis = {}

        # System Health KPI
        system_health = self._calculate_system_health_kpi()
        if system_health:
            kpis["system_health"] = system_health

        # Code Quality KPI
        code_quality = self._calculate_code_quality_kpi()
        if code_quality:
            kpis["code_quality"] = code_quality

        # Security KPI
        security = self._calculate_security_kpi()
        if security:
            kpis["security"] = security

        # Performance KPI
        performance = self._calculate_performance_kpi()
        if performance:
            kpis["performance"] = performance

        # Test Coverage KPI
        test_coverage = self._calculate_test_coverage_kpi()
        if test_coverage:
            kpis["test_coverage"] = test_coverage

        self.kpis = kpis
        return kpis

    def _calculate_system_health_kpi(self) -> KPIMetric | None:
        """Calculate system health KPI."""
        cpu_metrics = [
            m for m in self.data_collector.metrics if m.name == "system_cpu_usage"
        ]
        memory_metrics = [
            m for m in self.data_collector.metrics if m.name == "system_memory_usage"
        ]

        if not cpu_metrics or not memory_metrics:
            return None

        # Calculate average system health
        cpu_avg = statistics.mean(
            [m.value for m in cpu_metrics[-10:]],
        )  # Last 10 readings
        memory_avg = statistics.mean([m.value for m in memory_metrics[-10:]])

        # System health is inverse of resource usage
        system_health = 100 - ((cpu_avg + memory_avg) / 2)

        # Determine status
        if system_health >= 80:
            status = "excellent"
        elif system_health >= 60:
            status = "good"
        elif system_health >= 40:
            status = "warning"
        else:
            status = "critical"

        # Calculate trend
        trend = self._calculate_kpi_trend(cpu_metrics + memory_metrics)

        return KPIMetric(
            name="System Health",
            current_value=system_health,
            target_value=80.0,
            unit="score",
            status=status,
            trend=trend,
            change_percent=0.0,  # Would calculate actual change
            last_updated=time.time(),
        )

    def _calculate_code_quality_kpi(self) -> KPIMetric | None:
        """Calculate code quality KPI."""
        quality_metrics = [
            m for m in self.data_collector.metrics if m.name == "code_quality_score"
        ]

        if not quality_metrics:
            return None

        current_value = quality_metrics[-1].value
        trend = self._calculate_kpi_trend(quality_metrics)

        # Determine status
        if current_value >= 90:
            status = "excellent"
        elif current_value >= 80:
            status = "good"
        elif current_value >= 70:
            status = "warning"
        else:
            status = "critical"

        return KPIMetric(
            name="Code Quality",
            current_value=current_value,
            target_value=85.0,
            unit="score",
            status=status,
            trend=trend,
            change_percent=0.0,
            last_updated=time.time(),
        )

    def _calculate_security_kpi(self) -> KPIMetric | None:
        """Calculate security KPI."""
        security_metrics = [
            m for m in self.data_collector.metrics if m.name == "security_score"
        ]

        if not security_metrics:
            return None

        current_value = security_metrics[-1].value
        trend = self._calculate_kpi_trend(security_metrics)

        # Determine status
        if current_value >= 95:
            status = "excellent"
        elif current_value >= 85:
            status = "good"
        elif current_value >= 70:
            status = "warning"
        else:
            status = "critical"

        return KPIMetric(
            name="Security",
            current_value=current_value,
            target_value=90.0,
            unit="score",
            status=status,
            trend=trend,
            change_percent=0.0,
            last_updated=time.time(),
        )

    def _calculate_performance_kpi(self) -> KPIMetric | None:
        """Calculate performance KPI."""
        build_metrics = [
            m for m in self.data_collector.metrics if m.name == "build_time"
        ]
        test_metrics = [
            m for m in self.data_collector.metrics if m.name == "test_execution_time"
        ]

        if not build_metrics or not test_metrics:
            return None

        # Performance KPI is based on build and test times (lower is better)
        build_time = build_metrics[-1].value
        test_time = test_metrics[-1].value

        # Convert to performance score (100 - normalized time)
        max_build_time = 300  # 5 minutes
        max_test_time = 600  # 10 minutes

        build_score = max(0, 100 - (build_time / max_build_time) * 100)
        test_score = max(0, 100 - (test_time / max_test_time) * 100)

        performance_score = (build_score + test_score) / 2

        # Determine status
        if performance_score >= 80:
            status = "excellent"
        elif performance_score >= 60:
            status = "good"
        elif performance_score >= 40:
            status = "warning"
        else:
            status = "critical"

        return KPIMetric(
            name="Performance",
            current_value=performance_score,
            target_value=75.0,
            unit="score",
            status=status,
            trend="stable",
            change_percent=0.0,
            last_updated=time.time(),
        )

    def _calculate_test_coverage_kpi(self) -> KPIMetric | None:
        """Calculate test coverage KPI."""
        coverage_metrics = [
            m for m in self.data_collector.metrics if m.name == "test_coverage"
        ]

        if not coverage_metrics:
            return None

        current_value = coverage_metrics[-1].value
        trend = self._calculate_kpi_trend(coverage_metrics)

        # Determine status
        if current_value >= 90:
            status = "excellent"
        elif current_value >= 80:
            status = "good"
        elif current_value >= 70:
            status = "warning"
        else:
            status = "critical"

        return KPIMetric(
            name="Test Coverage",
            current_value=current_value,
            target_value=85.0,
            unit="percent",
            status=status,
            trend=trend,
            change_percent=0.0,
            last_updated=time.time(),
        )

    def _calculate_kpi_trend(self, metrics: list[AnalyticsMetric]) -> str:
        """Calculate trend for KPI metrics."""
        if len(metrics) < 2:
            return "stable"

        values = [m.value for m in metrics[-5:]]  # Last 5 values

        if len(values) < 2:
            return "stable"

        # Simple trend calculation
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        change_percent = (
            ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0
        )

        if change_percent > 5:
            return "increasing"
        if change_percent < -5:
            return "decreasing"
        return "stable"


class AdvancedAnalyticsDashboard:
    """Comprehensive analytics dashboard."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "analytics"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.data_collector = DataCollector(project_root)
        self.predictive_analytics = PredictiveAnalytics(self.data_collector)
        self.kpi_calculator = KPICalculator(self.data_collector)

        self.dashboard_data = {}

    def generate_comprehensive_dashboard(self) -> dict[str, Any]:
        """Generate comprehensive analytics dashboard."""
        print("📊 Generating Comprehensive Analytics Dashboard...")

        # Start data collection
        self.data_collector.start_collection()

        # Collect data for a short period
        time.sleep(10)

        # Stop data collection
        self.data_collector.stop_collection()

        # Generate predictions
        predictions = self.predictive_analytics.generate_predictions()

        # Calculate KPIs
        kpis = self.kpi_calculator.calculate_kpis()

        # Generate dashboard data
        dashboard_data = self._generate_dashboard_data(predictions, kpis)

        # Generate visualizations
        self._generate_visualizations()

        # Save dashboard
        self._save_dashboard(dashboard_data)

        return dashboard_data

    def _generate_dashboard_data(
        self,
        predictions: list[PredictiveInsight],
        kpis: dict[str, KPIMetric],
    ) -> dict[str, Any]:
        """Generate dashboard data."""
        # Calculate summary statistics
        total_metrics = len(self.data_collector.metrics)
        metrics_by_category = defaultdict(list)

        for metric in self.data_collector.metrics:
            metrics_by_category[metric.category].append(metric)

        # Calculate category averages
        category_averages = {}
        for category, metrics in metrics_by_category.items():
            if metrics:
                category_averages[category] = statistics.mean(
                    [m.value for m in metrics],
                )

        # Calculate overall health score
        health_score = self._calculate_overall_health_score(kpis)

        # Generate insights
        insights = self._generate_insights(predictions, kpis)

        # Generate recommendations
        recommendations = self._generate_recommendations(predictions, kpis)

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_metrics": total_metrics,
                "categories": len(metrics_by_category),
                "predictions": len(predictions),
                "kpis": len(kpis),
                "health_score": health_score,
                "category_averages": category_averages,
            },
            "metrics": [asdict(m) for m in self.data_collector.metrics],
            "predictions": [asdict(p) for p in predictions],
            "kpis": {name: asdict(kpi) for name, kpi in kpis.items()},
            "insights": insights,
            "recommendations": recommendations,
            "trends": self._calculate_trends(),
        }

    def _calculate_overall_health_score(self, kpis: dict[str, KPIMetric]) -> float:
        """Calculate overall health score."""
        if not kpis:
            return 0.0

        # Weight different KPIs
        weights = {
            "system_health": 0.25,
            "code_quality": 0.20,
            "security": 0.20,
            "performance": 0.20,
            "test_coverage": 0.15,
        }

        weighted_score = 0.0
        total_weight = 0.0

        for name, kpi in kpis.items():
            if name in weights:
                weight = weights[name]
                weighted_score += kpi.current_value * weight
                total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _generate_insights(
        self,
        predictions: list[PredictiveInsight],
        kpis: dict[str, KPIMetric],
    ) -> list[str]:
        """Generate insights from data."""
        insights = []

        # KPI insights
        for kpi in kpis.values():
            if kpi.status == "critical":
                insights.append(
                    f"Critical: {kpi.name} is at {kpi.current_value:.1f} (target: {kpi.target_value:.1f})",
                )
            elif kpi.status == "warning":
                insights.append(
                    f"Warning: {kpi.name} needs attention at {kpi.current_value:.1f}",
                )
            elif kpi.status == "excellent":
                insights.append(
                    f"Excellent: {kpi.name} is performing well at {kpi.current_value:.1f}",
                )

        # Prediction insights
        high_impact_predictions = [p for p in predictions if p.impact == "high"]
        for prediction in high_impact_predictions:
            insights.append(
                f"High Impact Prediction: {prediction.metric_name} - {prediction.prediction}",
            )

        # Trend insights
        trends = self._calculate_trends()
        for metric, trend in trends.items():
            if trend == "increasing":
                insights.append(f"Trend: {metric} is increasing")
            elif trend == "decreasing":
                insights.append(f"Trend: {metric} is decreasing")

        return insights

    def _generate_recommendations(
        self,
        predictions: list[PredictiveInsight],
        kpis: dict[str, KPIMetric],
    ) -> list[str]:
        """Generate recommendations."""
        recommendations = []

        # KPI-based recommendations
        for kpi in kpis.values():
            if kpi.status == "critical":
                recommendations.append(
                    f"Urgent: Improve {kpi.name} from {kpi.current_value:.1f} to {kpi.target_value:.1f}",
                )
            elif kpi.status == "warning":
                recommendations.append(f"Monitor: {kpi.name} is below target")

        # Prediction-based recommendations
        for prediction in predictions:
            if prediction.impact == "high":
                recommendations.append(f"Action: {prediction.recommendation}")

        # General recommendations
        recommendations.append("Implement continuous monitoring and alerting")
        recommendations.append("Regular review of KPIs and metrics")
        recommendations.append("Automated reporting and dashboard updates")
        recommendations.append("Team training on analytics and insights")

        return recommendations

    def _calculate_trends(self) -> dict[str, str]:
        """Calculate trends for all metrics."""
        trends = {}

        metrics_by_name = defaultdict(list)
        for metric in self.data_collector.metrics:
            metrics_by_name[metric.name].append(metric)

        for name, metrics in metrics_by_name.items():
            if len(metrics) >= 3:
                trend = self._calculate_metric_trend(metrics)
                trends[name] = trend

        return trends

    def _calculate_metric_trend(self, metrics: list[AnalyticsMetric]) -> str:
        """Calculate trend for a specific metric."""
        if len(metrics) < 2:
            return "stable"

        values = [m.value for m in metrics[-5:]]  # Last 5 values

        if len(values) < 2:
            return "stable"

        # Simple linear trend
        x = np.arange(len(values))
        y = np.array(values)

        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]

            if slope > 0.1:
                return "increasing"
            if slope < -0.1:
                return "decreasing"
            return "stable"

        return "stable"

    def _generate_visualizations(self) -> None:
        """Generate visualization charts."""
        print("📈 Generating visualizations...")

        try:
            # Set style
            plt.style.use("seaborn-v0_8")

            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle("Pheno SDK Analytics Dashboard", fontsize=16)

            # Plot 1: System metrics over time
            self._plot_system_metrics(axes[0, 0])

            # Plot 2: KPI status
            self._plot_kpi_status(axes[0, 1])

            # Plot 3: Metric trends
            self._plot_metric_trends(axes[1, 0])

            # Plot 4: Category distribution
            self._plot_category_distribution(axes[1, 1])

            plt.tight_layout()

            # Save plot
            plot_file = self.reports_dir / f"analytics_dashboard_{int(time.time())}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches="tight")
            plt.close()

            print(f"📈 Visualization saved: {plot_file}")

        except Exception as e:
            print(f"Error generating visualizations: {e}")

    def _plot_system_metrics(self, ax) -> None:
        """Plot system metrics over time."""
        cpu_metrics = [
            m for m in self.data_collector.metrics if m.name == "system_cpu_usage"
        ]
        memory_metrics = [
            m for m in self.data_collector.metrics if m.name == "system_memory_usage"
        ]

        if cpu_metrics and memory_metrics:
            timestamps = [datetime.fromtimestamp(m.timestamp) for m in cpu_metrics]
            cpu_values = [m.value for m in cpu_metrics]
            memory_values = [m.value for m in memory_metrics]

            ax.plot(timestamps, cpu_values, label="CPU Usage %", marker="o")
            ax.plot(timestamps, memory_values, label="Memory Usage %", marker="s")
            ax.set_title("System Metrics Over Time")
            ax.set_ylabel("Usage %")
            ax.legend()
            ax.grid(True, alpha=0.3)

    def _plot_kpi_status(self, ax) -> None:
        """Plot KPI status."""
        kpis = self.kpi_calculator.kpis

        if kpis:
            names = list(kpis.keys())
            values = [kpi.current_value for kpi in kpis.values()]
            targets = [kpi.target_value for kpi in kpis.values()]

            x = np.arange(len(names))
            width = 0.35

            ax.bar(x - width / 2, values, width, label="Current", alpha=0.8)
            ax.bar(x + width / 2, targets, width, label="Target", alpha=0.8)

            ax.set_title("KPI Status")
            ax.set_ylabel("Score")
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)

    def _plot_metric_trends(self, ax) -> None:
        """Plot metric trends."""
        trends = self._calculate_trends()

        if trends:
            trend_counts = Counter(trends.values())

            ax.pie(trend_counts.values(), labels=trend_counts.keys(), autopct="%1.1f%%")
            ax.set_title("Metric Trends Distribution")

    def _plot_category_distribution(self, ax) -> None:
        """Plot category distribution."""
        metrics_by_category = defaultdict(list)
        for metric in self.data_collector.metrics:
            metrics_by_category[metric.category].append(metric)

        if metrics_by_category:
            categories = list(metrics_by_category.keys())
            counts = [len(metrics) for metrics in metrics_by_category.values()]

            ax.bar(categories, counts, alpha=0.8)
            ax.set_title("Metrics by Category")
            ax.set_ylabel("Count")
            ax.tick_params(axis="x", rotation=45)

    def _save_dashboard(self, dashboard_data: dict[str, Any]) -> None:
        """Save dashboard data."""
        # Save JSON data
        json_file = self.reports_dir / f"dashboard_data_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(dashboard_data, f, indent=2)

        # Save summary report
        summary_file = self.reports_dir / f"dashboard_summary_{int(time.time())}.md"
        self._save_dashboard_summary(dashboard_data, summary_file)

        print("📊 Dashboard saved:")
        print(f"  JSON: {json_file}")
        print(f"  Summary: {summary_file}")

    def _save_dashboard_summary(
        self,
        dashboard_data: dict[str, Any],
        file_path: Path,
    ) -> None:
        """Save markdown dashboard summary."""
        summary = dashboard_data["summary"]

        content = f"""# Advanced Analytics Dashboard

**Generated**: {dashboard_data["timestamp"]}
**Health Score**: {summary["health_score"]:.1f}/100

## Summary

| Metric | Value |
|--------|-------|
| Total Metrics | {summary["total_metrics"]} |
| Categories | {summary["categories"]} |
| Predictions | {summary["predictions"]} |
| KPIs | {summary["kpis"]} |
| Health Score | {summary["health_score"]:.1f}/100 |

## KPIs

"""

        for kpi in dashboard_data["kpis"].values():
            status_emoji = (
                "🟢"
                if kpi["status"] == "excellent"
                else "🟡"
                if kpi["status"] == "good"
                else "🟠"
                if kpi["status"] == "warning"
                else "🔴"
            )
            content += f"### {status_emoji} {kpi['name']}\n\n"
            content += (
                f"- **Current Value**: {kpi['current_value']:.1f} {kpi['unit']}\n"
            )
            content += f"- **Target Value**: {kpi['target_value']:.1f} {kpi['unit']}\n"
            content += f"- **Status**: {kpi['status']}\n"
            content += f"- **Trend**: {kpi['trend']}\n\n"

        if dashboard_data["predictions"]:
            content += "## Predictions\n\n"
            for prediction in dashboard_data["predictions"]:
                confidence_emoji = (
                    "🟢"
                    if prediction["confidence"] > 0.8
                    else "🟡"
                    if prediction["confidence"] > 0.6
                    else "🟠"
                )
                content += f"### {confidence_emoji} {prediction['metric_name']}\n\n"
                content += f"- **Prediction**: {prediction['prediction']}\n"
                content += f"- **Confidence**: {prediction['confidence']:.1%}\n"
                content += f"- **Timeframe**: {prediction['timeframe']}\n"
                content += f"- **Recommendation**: {prediction['recommendation']}\n"
                content += f"- **Impact**: {prediction['impact']}\n\n"

        if dashboard_data["insights"]:
            content += "## Insights\n\n"
            for insight in dashboard_data["insights"]:
                content += f"- {insight}\n"

        if dashboard_data["recommendations"]:
            content += "\n## Recommendations\n\n"
            for rec in dashboard_data["recommendations"]:
                content += f"- {rec}\n"

        with open(file_path, "w") as f:
            f.write(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Advanced Analytics Dashboard")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Data collection duration in seconds",
    )
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    dashboard = AdvancedAnalyticsDashboard(args.project_root)

    try:
        # Generate comprehensive dashboard
        dashboard_data = dashboard.generate_comprehensive_dashboard()

        if args.json:
            output = json.dumps(dashboard_data, indent=2)
        else:
            # Pretty print format
            summary = dashboard_data["summary"]
            output = f"""
📊 ADVANCED ANALYTICS DASHBOARD
{"=" * 60}
Health Score: {summary["health_score"]:.1f}/100
Total Metrics: {summary["total_metrics"]}
Categories: {summary["categories"]}
Predictions: {summary["predictions"]}
KPIs: {summary["kpis"]}

KPIs:
"""
            for kpi in dashboard_data["kpis"].values():
                status_emoji = (
                    "🟢"
                    if kpi["status"] == "excellent"
                    else "🟡"
                    if kpi["status"] == "good"
                    else "🟠"
                    if kpi["status"] == "warning"
                    else "🔴"
                )
                output += f"  {status_emoji} {kpi['name']}: {kpi['current_value']:.1f}/{kpi['target_value']:.1f} ({kpi['status']})\n"

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Report saved to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"❌ Error in analytics dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
