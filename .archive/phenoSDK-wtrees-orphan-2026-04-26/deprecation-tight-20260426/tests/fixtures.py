"""
Test fixtures and utilities.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


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
        "debug": True,
    }


@pytest.fixture
def sample_data():
    """Sample data for tests."""
    return {
        "users": [
            {"id": 1, "name": "Test User 1", "email": "user1@test.com"},
            {"id": 2, "name": "Test User 2", "email": "user2@test.com"},
        ],
        "products": [
            {"id": 1, "name": "Product 1", "price": 10.99},
            {"id": 2, "name": "Product 2", "price": 20.99},
        ],
    }


@pytest.fixture
def mock_external_service():
    """Mock external service."""
    with patch("external_service.api_call") as mock:
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
