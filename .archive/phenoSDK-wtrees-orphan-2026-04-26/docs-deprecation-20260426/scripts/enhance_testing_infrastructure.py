#!/usr/bin/env python3
"""
Testing Infrastructure Enhancement Script
Implements comprehensive testing improvements for Phase 3.
"""

import argparse
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TestSuite:
    """Represents a test suite configuration."""
    name: str
    path: str
    markers: list[str]
    coverage_target: float
    timeout: int
    parallel: bool


class TestingInfrastructureEnhancer:
    """Enhances testing infrastructure for comprehensive coverage."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.tests_path = self.project_root / "tests"
        self.reports_path = self.project_root / "reports"

        # Create reports directory
        self.reports_path.mkdir(exist_ok=True)

        # Define test suites
        self.test_suites = [
            TestSuite(
                name="unit",
                path="tests/unit",
                markers=["unit", "fast"],
                coverage_target=95.0,
                timeout=60,
                parallel=True,
            ),
            TestSuite(
                name="integration",
                path="tests/integration",
                markers=["integration", "slow"],
                coverage_target=85.0,
                timeout=300,
                parallel=False,
            ),
            TestSuite(
                name="e2e",
                path="tests/e2e",
                markers=["e2e", "slow"],
                coverage_target=80.0,
                timeout=600,
                parallel=False,
            ),
            TestSuite(
                name="security",
                path="tests/security",
                markers=["security", "slow"],
                coverage_target=90.0,
                timeout=180,
                parallel=True,
            ),
            TestSuite(
                name="performance",
                path="tests/performance",
                markers=["performance", "slow"],
                coverage_target=70.0,
                timeout=1200,
                parallel=False,
            ),
            TestSuite(
                name="contract",
                path="tests/contract",
                markers=["contract", "integration"],
                coverage_target=85.0,
                timeout=120,
                parallel=True,
            ),
        ]

    def enhance_testing_infrastructure(self) -> dict[str, Any]:
        """Enhance the entire testing infrastructure."""
        print("🧪 Enhancing Testing Infrastructure...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "enhancements": [],
            "test_suites": {},
            "coverage_improvements": {},
            "performance_improvements": {},
            "new_tools": [],
        }

        # 1. Create missing test directories and files
        self._create_test_structure()
        results["enhancements"].append("Created comprehensive test structure")

        # 2. Generate test templates
        self._generate_test_templates()
        results["enhancements"].append("Generated test templates")

        # 3. Create test fixtures and utilities
        self._create_test_utilities()
        results["enhancements"].append("Created test utilities and fixtures")

        # 4. Set up performance testing
        self._setup_performance_testing()
        results["enhancements"].append("Set up performance testing framework")

        # 5. Create test data management
        self._create_test_data_management()
        results["enhancements"].append("Created test data management")

        # 6. Set up test reporting
        self._setup_test_reporting()
        results["enhancements"].append("Set up comprehensive test reporting")

        # 7. Create test automation scripts
        self._create_test_automation()
        results["enhancements"].append("Created test automation scripts")

        # 8. Generate coverage analysis
        for suite in self.test_suites:
            suite_results = self._analyze_test_suite(suite)
            results["test_suites"][suite.name] = suite_results

        return results

    def _create_test_structure(self) -> None:
        """Create comprehensive test directory structure."""
        test_dirs = [
            "tests/unit/domain",
            "tests/unit/application",
            "tests/unit/infrastructure",
            "tests/unit/adapters",
            "tests/integration/api",
            "tests/integration/database",
            "tests/integration/external",
            "tests/e2e/workflows",
            "tests/e2e/user_journeys",
            "tests/security/auth",
            "tests/security/data",
            "tests/security/injection",
            "tests/performance/load",
            "tests/performance/stress",
            "tests/performance/memory",
            "tests/contract/api",
            "tests/contract/external",
            "tests/fixtures",
            "tests/data",
            "tests/mocks",
            "tests/utilities",
        ]

        for test_dir in test_dirs:
            (self.project_root / test_dir).mkdir(parents=True, exist_ok=True)
            # Create __init__.py files
            (self.project_root / test_dir / "__init__.py").touch()

    def _generate_test_templates(self) -> None:
        """Generate test templates for different types of tests."""

        # Unit test template
        unit_test_template = '''"""
Unit test template for {module_name}.
"""

import pytest
from unittest.mock import Mock, patch
from {module_path} import {class_name}


class Test{class_name}:
    """Test cases for {class_name}."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = {class_name}()
    
    def test_initialization(self):
        """Test object initialization."""
        assert self.instance is not None
    
    def test_method_example(self):
        """Test example method."""
        # Arrange
        input_value = "test"
        
        # Act
        result = self.instance.example_method(input_value)
        
        # Assert
        assert result is not None
    
    @pytest.mark.parametrize("input_val,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_parametrized(self, input_val, expected):
        """Test with multiple parameters."""
        result = self.instance.example_method(input_val)
        assert result == expected
    
    @patch('{module_path}.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependencies."""
        mock_dependency.return_value = "mocked"
        result = self.instance.method_with_dependency()
        assert result == "mocked"
        mock_dependency.assert_called_once()
'''

        # Integration test template
        integration_test_template = '''"""
Integration test template for {module_name}.
"""

import pytest
from {module_path} import {class_name}


@pytest.mark.integration
class Test{class_name}Integration:
    """Integration tests for {class_name}."""
    
    @pytest.fixture(autouse=True)
    def setup_integration(self):
        """Set up integration test environment."""
        # Set up test database, external services, etc.
        pass
    
    def test_end_to_end_workflow(self):
        """Test complete workflow."""
        # Test the entire flow from start to finish
        pass
    
    def test_external_service_integration(self):
        """Test integration with external services."""
        # Test actual external service calls
        pass
'''

        # Performance test template
        performance_test_template = '''"""
Performance test template for {module_name}.
"""

import pytest
import time
from {module_path} import {class_name}


@pytest.mark.performance
class Test{class_name}Performance:
    """Performance tests for {class_name}."""
    
    def test_execution_time(self):
        """Test method execution time."""
        instance = {class_name}()
        
        start_time = time.time()
        result = instance.example_method("test")
        execution_time = time.time() - start_time
        
        assert execution_time < 1.0  # Should complete within 1 second
        assert result is not None
    
    @pytest.mark.benchmark
    def test_benchmark_performance(self, benchmark):
        """Benchmark performance of critical methods."""
        instance = {class_name}()
        result = benchmark(instance.example_method, "test")
        assert result is not None
'''

        # Save templates
        templates_dir = self.project_root / "tests" / "templates"
        templates_dir.mkdir(exist_ok=True)

        with open(templates_dir / "unit_test_template.py", "w") as f:
            f.write(unit_test_template)

        with open(templates_dir / "integration_test_template.py", "w") as f:
            f.write(integration_test_template)

        with open(templates_dir / "performance_test_template.py", "w") as f:
            f.write(performance_test_template)

    def _create_test_utilities(self) -> None:
        """Create test utilities and fixtures."""

        # Test fixtures
        fixtures_content = '''"""
Test fixtures and utilities.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    return {
        "database_url": "sqlite:///:memory:",
        "api_key": "test_key",
        "debug": True
    }


@pytest.fixture
def sample_data():
    """Sample data for tests."""
    return {
        "users": [
            {"id": 1, "name": "Test User 1", "email": "user1@test.com"},
            {"id": 2, "name": "Test User 2", "email": "user2@test.com"}
        ],
        "products": [
            {"id": 1, "name": "Product 1", "price": 10.99},
            {"id": 2, "name": "Product 2", "price": 20.99}
        ]
    }


@pytest.fixture
def mock_external_service():
    """Mock external service."""
    with patch('external_service.api_call') as mock:
        mock.return_value = {"status": "success", "data": "test"}
        yield mock


class TestDataBuilder:
    """Builder pattern for test data."""
    
    def __init__(self):
        self.data = {}
    
    def with_user(self, **kwargs):
        """Add user data."""
        self.data.setdefault("users", []).append(kwargs)
        return self
    
    def with_product(self, **kwargs):
        """Add product data."""
        self.data.setdefault("products", []).append(kwargs)
        return self
    
    def build(self):
        """Build the test data."""
        return self.data


@pytest.fixture
def test_data_builder():
    """Test data builder fixture."""
    return TestDataBuilder
'''

        # Test utilities
        utilities_content = '''"""
Test utilities and helpers.
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List


class TestHelper:
    """Helper class for common test operations."""
    
    @staticmethod
    def load_test_data(file_path: str) -> Dict[str, Any]:
        """Load test data from JSON or YAML file."""
        path = Path(file_path)
        if path.suffix == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        elif path.suffix in ['.yml', '.yaml']:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    @staticmethod
    def save_test_data(data: Dict[str, Any], file_path: str) -> None:
        """Save test data to JSON or YAML file."""
        path = Path(file_path)
        if path.suffix == '.json':
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        elif path.suffix in ['.yml', '.yaml']:
            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
    
    @staticmethod
    def assert_dict_contains(expected: Dict[str, Any], actual: Dict[str, Any]) -> None:
        """Assert that actual dict contains all expected keys and values."""
        for key, value in expected.items():
            assert key in actual, f"Key '{key}' not found in actual dict"
            assert actual[key] == value, f"Value for key '{key}' doesn't match"
    
    @staticmethod
    def create_mock_response(status_code: int = 200, data: Any = None) -> Mock:
        """Create a mock HTTP response."""
        from unittest.mock import Mock
        response = Mock()
        response.status_code = status_code
        response.json.return_value = data or {}
        return response


class PerformanceHelper:
    """Helper class for performance testing."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    
    @staticmethod
    def assert_execution_time_under(func, max_time: float, *args, **kwargs):
        """Assert that function executes within specified time."""
        _, execution_time = PerformanceHelper.measure_execution_time(func, *args, **kwargs)
        assert execution_time < max_time, f"Execution time {execution_time:.3f}s exceeds {max_time}s"
'''

        # Save utilities
        with open(self.tests_path / "fixtures.py", "w") as f:
            f.write(fixtures_content)

        with open(self.tests_path / "utilities" / "helpers.py", "w") as f:
            f.write(utilities_content)

    def _setup_performance_testing(self) -> None:
        """Set up performance testing framework."""

        # Performance test configuration
        performance_config = '''"""
Performance testing configuration.
"""

import pytest
from pytest_benchmark.fixture import BenchmarkFixture


@pytest.fixture(scope="session")
def performance_config():
    """Performance testing configuration."""
    return {
        "max_execution_time": 1.0,  # seconds
        "memory_limit_mb": 100,
        "cpu_usage_limit": 80,  # percentage
        "benchmark_rounds": 5,
        "warmup_rounds": 2
    }


@pytest.fixture
def benchmark_config(benchmark: BenchmarkFixture):
    """Configure benchmark settings."""
    benchmark.min_rounds = 5
    benchmark.warmup = True
    benchmark.warmup_iterations = 2
    return benchmark


class PerformanceTestBase:
    """Base class for performance tests."""
    
    def assert_performance(self, func, max_time: float, *args, **kwargs):
        """Assert function performance meets requirements."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        assert execution_time < max_time, f"Performance test failed: {execution_time:.3f}s > {max_time}s"
        return result
'''

        # Memory profiling utilities
        memory_profiler = '''"""
Memory profiling utilities for tests.
"""

import psutil
import os
from typing import Dict, Any


class MemoryProfiler:
    """Memory profiling for tests."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": self.process.memory_percent()
        }
    
    def get_memory_delta(self) -> Dict[str, float]:
        """Get memory usage delta since initialization."""
        current = self.get_memory_usage()
        return {
            "rss_delta": current["rss"] - self.initial_memory["rss"],
            "vms_delta": current["vms"] - self.initial_memory["vms"],
            "percent_delta": current["percent"] - self.initial_memory["percent"]
        }
    
    def assert_memory_usage(self, max_mb: float):
        """Assert memory usage is within limits."""
        current = self.get_memory_usage()
        assert current["rss"] < max_mb, f"Memory usage {current['rss']:.1f}MB exceeds limit {max_mb}MB"


@pytest.fixture
def memory_profiler():
    """Memory profiler fixture."""
    return MemoryProfiler()
'''

        # Save performance testing files
        with open(self.tests_path / "performance" / "config.py", "w") as f:
            f.write(performance_config)

        with open(self.tests_path / "utilities" / "memory_profiler.py", "w") as f:
            f.write(memory_profiler)

    def _create_test_data_management(self) -> None:
        """Create test data management system."""

        # Test data factory
        data_factory = '''"""
Test data factory for generating test data.
"""

from typing import Any, Dict, List, Optional
from faker import Faker
import random


class TestDataFactory:
    """Factory for generating test data."""
    
    def __init__(self):
        self.fake = Faker()
    
    def create_user(self, **overrides) -> Dict[str, Any]:
        """Create test user data."""
        return {
            "id": self.fake.random_int(min=1, max=10000),
            "name": self.fake.name(),
            "email": self.fake.email(),
            "age": self.fake.random_int(min=18, max=100),
            "is_active": True,
            **overrides
        }
    
    def create_product(self, **overrides) -> Dict[str, Any]:
        """Create test product data."""
        return {
            "id": self.fake.random_int(min=1, max=10000),
            "name": self.fake.word().title(),
            "description": self.fake.text(max_nb_chars=200),
            "price": round(self.fake.pyfloat(min_value=1, max_value=1000, right_digits=2), 2),
            "category": self.fake.word(),
            "in_stock": self.fake.boolean(),
            **overrides
        }
    
    def create_batch(self, factory_method, count: int, **overrides) -> List[Dict[str, Any]]:
        """Create a batch of test data."""
        return [factory_method(**overrides) for _ in range(count)]
    
    def create_realistic_dataset(self, size: int) -> Dict[str, List[Dict[str, Any]]]:
        """Create a realistic dataset for testing."""
        users = self.create_batch(self.create_user, size)
        products = self.create_batch(self.create_product, size * 2)
        
        return {
            "users": users,
            "products": products,
            "orders": self._create_orders(users, products, size)
        }
    
    def _create_orders(self, users: List[Dict], products: List[Dict], count: int) -> List[Dict[str, Any]]:
        """Create test orders."""
        orders = []
        for _ in range(count):
            user = random.choice(users)
            product = random.choice(products)
            orders.append({
                "id": self.fake.random_int(min=1, max=10000),
                "user_id": user["id"],
                "product_id": product["id"],
                "quantity": random.randint(1, 10),
                "total": round(product["price"] * random.randint(1, 10), 2),
                "status": random.choice(["pending", "completed", "cancelled"])
            })
        return orders


@pytest.fixture
def data_factory():
    """Test data factory fixture."""
    return TestDataFactory()
'''

        # Test data fixtures
        data_fixtures = '''"""
Test data fixtures.
"""

import pytest
from .utilities.data_factory import TestDataFactory


@pytest.fixture
def sample_users(data_factory):
    """Sample users for testing."""
    return data_factory.create_batch(data_factory.create_user, 10)


@pytest.fixture
def sample_products(data_factory):
    """Sample products for testing."""
    return data_factory.create_batch(data_factory.create_product, 20)


@pytest.fixture
def realistic_dataset(data_factory):
    """Realistic dataset for integration testing."""
    return data_factory.create_realistic_dataset(100)


@pytest.fixture
def empty_dataset():
    """Empty dataset for edge case testing."""
    return {
        "users": [],
        "products": [],
        "orders": []
    }
'''

        # Save test data management files
        with open(self.tests_path / "utilities" / "data_factory.py", "w") as f:
            f.write(data_factory)

        with open(self.tests_path / "fixtures" / "data_fixtures.py", "w") as f:
            f.write(data_fixtures)

    def _setup_test_reporting(self) -> None:
        """Set up comprehensive test reporting."""

        # Test reporter
        test_reporter = '''"""
Test reporting utilities.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class TestReporter:
    """Comprehensive test reporting."""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """Generate detailed coverage report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_coverage": coverage_data.get("total_coverage", 0),
            "line_coverage": coverage_data.get("line_coverage", 0),
            "branch_coverage": coverage_data.get("branch_coverage", 0),
            "files": coverage_data.get("files", {}),
            "summary": self._analyze_coverage(coverage_data)
        }
        
        report_path = self.reports_dir / "coverage_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)
    
    def generate_performance_report(self, performance_data: Dict[str, Any]) -> str:
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
            "recommendations": self._analyze_performance(performance_data)
        }
        
        report_path = self.reports_dir / "performance_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)
    
    def generate_security_report(self, security_data: Dict[str, Any]) -> str:
        """Generate security test report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": security_data.get("vulnerabilities", []),
            "security_tests_passed": security_data.get("passed", 0),
            "security_tests_failed": security_data.get("failed", 0),
            "risk_level": self._assess_security_risk(security_data),
            "recommendations": self._generate_security_recommendations(security_data)
        }
        
        report_path = self.reports_dir / "security_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)
    
    def _analyze_coverage(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
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
            "improvement_needed": max(0, 80 - total_coverage)
        }
    
    def _analyze_performance(self, performance_data: Dict[str, Any]) -> List[str]:
        """Analyze performance data and provide recommendations."""
        recommendations = []
        
        avg_time = performance_data.get("average_execution_time", 0)
        if avg_time > 5.0:
            recommendations.append("Consider optimizing slow tests")
        
        memory_usage = performance_data.get("memory_usage", {})
        if memory_usage.get("peak_mb", 0) > 500:
            recommendations.append("High memory usage detected - consider memory optimization")
        
        return recommendations
    
    def _assess_security_risk(self, security_data: Dict[str, Any]) -> str:
        """Assess overall security risk level."""
        vulnerabilities = security_data.get("vulnerabilities", [])
        failed_tests = security_data.get("failed", 0)
        
        if len(vulnerabilities) > 5 or failed_tests > 3:
            return "high"
        elif len(vulnerabilities) > 2 or failed_tests > 1:
            return "medium"
        else:
            return "low"
    
    def _generate_security_recommendations(self, security_data: Dict[str, Any]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        vulnerabilities = security_data.get("vulnerabilities", [])
        if any(v.get("severity") == "high" for v in vulnerabilities):
            recommendations.append("Address high-severity vulnerabilities immediately")
        
        if security_data.get("failed", 0) > 0:
            recommendations.append("Fix failing security tests")
        
        return recommendations
'''

        # Save test reporting
        with open(self.tests_path / "utilities" / "test_reporter.py", "w") as f:
            f.write(test_reporter)

    def _create_test_automation(self) -> None:
        """Create test automation scripts."""

        # Test runner script
        test_runner = '''#!/usr/bin/env python3
"""
Comprehensive test runner for all test suites.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """Comprehensive test runner."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_all_tests(self, parallel: bool = True, coverage: bool = True) -> Dict[str, Any]:
        """Run all test suites."""
        results = {}
        
        test_suites = [
            ("unit", "tests/unit", ["unit", "fast"]),
            ("integration", "tests/integration", ["integration"]),
            ("e2e", "tests/e2e", ["e2e"]),
            ("security", "tests/security", ["security"]),
            ("performance", "tests/performance", ["performance"]),
            ("contract", "tests/contract", ["contract"])
        ]
        
        for suite_name, suite_path, markers in test_suites:
            print(f"Running {suite_name} tests...")
            result = self._run_test_suite(suite_name, suite_path, markers, parallel, coverage)
            results[suite_name] = result
        
        return results
    
    def run_specific_suite(self, suite_name: str, parallel: bool = True) -> Dict[str, Any]:
        """Run a specific test suite."""
        suite_configs = {
            "unit": ("tests/unit", ["unit", "fast"]),
            "integration": ("tests/integration", ["integration"]),
            "e2e": ("tests/e2e", ["e2e"]),
            "security": ("tests/security", ["security"]),
            "performance": ("tests/performance", ["performance"]),
            "contract": ("tests/contract", ["contract"])
        }
        
        if suite_name not in suite_configs:
            raise ValueError(f"Unknown test suite: {suite_name}")
        
        suite_path, markers = suite_configs[suite_name]
        return self._run_test_suite(suite_name, suite_path, markers, parallel, True)
    
    def _run_test_suite(self, suite_name: str, suite_path: str, markers: List[str], 
                       parallel: bool, coverage: bool) -> Dict[str, Any]:
        """Run a specific test suite."""
        cmd = ["python", "-m", "pytest", suite_path, "-v"]
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
                "--cov-report=json:coverage.json"
            ])
        
        # Add markers
        if markers:
            marker_str = " or ".join(markers)
            cmd.extend(["-m", marker_str])
        
        # Add reporting
        cmd.extend([
            "--html=reports/test-report.html",
            "--self-contained-html",
            "--junitxml=reports/junit.xml"
        ])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive test runner")
    parser.add_argument("--suite", help="Specific test suite to run")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    
    args = parser.parse_args()
    
    runner = TestRunner(".")
    
    if args.suite:
        results = runner.run_specific_suite(args.suite, not args.no_parallel)
    else:
        results = runner.run_all_tests(not args.no_parallel, not args.no_coverage)
    
    # Print summary
    for suite_name, result in results.items():
        status = "PASSED" if result["success"] else "FAILED"
        print(f"{suite_name}: {status}")
    
    # Exit with error code if any tests failed
    if any(not result["success"] for result in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

        # Save test automation
        with open(self.project_root / "scripts" / "run_tests.py", "w") as f:
            f.write(test_runner)

        # Make executable
        os.chmod(self.project_root / "scripts" / "run_tests.py", 0o755)

    def _analyze_test_suite(self, suite: TestSuite) -> dict[str, Any]:
        """Analyze a specific test suite."""
        suite_path = self.project_root / suite.path

        if not suite_path.exists():
            return {
                "exists": False,
                "test_count": 0,
                "coverage": 0.0,
                "status": "missing",
            }

        # Count test files
        test_files = list(suite_path.rglob("test_*.py")) + list(suite_path.rglob("*_test.py"))
        test_count = len(test_files)

        return {
            "exists": True,
            "test_count": test_count,
            "coverage_target": suite.coverage_target,
            "timeout": suite.timeout,
            "parallel": suite.parallel,
            "status": "ready" if test_count > 0 else "empty",
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enhance testing infrastructure")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output report file")

    args = parser.parse_args()

    enhancer = TestingInfrastructureEnhancer(args.project_root)
    results = enhancer.enhance_testing_infrastructure()

    # Generate report
    report = f"""
# Testing Infrastructure Enhancement Report

## Summary
- **Enhancements Applied**: {len(results['enhancements'])}
- **Test Suites Configured**: {len(results['test_suites'])}
- **Timestamp**: {results['timestamp']}

## Enhancements Applied
"""

    for enhancement in results["enhancements"]:
        report += f"- ✅ {enhancement}\n"

    report += "\n## Test Suites Status\n"
    for suite_name, suite_data in results["test_suites"].items():
        status_emoji = "✅" if suite_data["status"] == "ready" else "⚠️" if suite_data["status"] == "empty" else "❌"
        report += f"- {status_emoji} **{suite_name}**: {suite_data['test_count']} tests, {suite_data['coverage_target']}% target\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
