"""
Test data fixtures.
"""

import pytest


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
        "orders": [],
    }
