"""
Test utilities and helpers.
"""

import json
from pathlib import Path
from typing import Any

import yaml


class TestHelper:
    """Helper class for common test operations."""

    @staticmethod
    def load_test_data(file_path: str) -> dict[str, Any]:
        """Load test data from JSON or YAML file."""
        path = Path(file_path)
        if path.suffix == ".json":
            with open(path) as f:
                return json.load(f)
        elif path.suffix in [".yml", ".yaml"]:
            with open(path) as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    @staticmethod
    def save_test_data(data: dict[str, Any], file_path: str) -> None:
        """Save test data to JSON or YAML file."""
        path = Path(file_path)
        if path.suffix == ".json":
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        elif path.suffix in [".yml", ".yaml"]:
            with open(path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)

    @staticmethod
    def assert_dict_contains(expected: dict[str, Any], actual: dict[str, Any]) -> None:
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
