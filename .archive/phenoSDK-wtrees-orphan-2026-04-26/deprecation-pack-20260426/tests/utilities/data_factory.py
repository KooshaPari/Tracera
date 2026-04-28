"""
Test data factory for generating test data.
"""

import random
from typing import Any

from faker import Faker


class TestDataFactory:
    """Factory for generating test data."""

    def __init__(self):
        self.fake = Faker()

    def create_user(self, **overrides) -> dict[str, Any]:
        """Create test user data."""
        return {
            "id": self.fake.random_int(min=1, max=10000),
            "name": self.fake.name(),
            "email": self.fake.email(),
            "age": self.fake.random_int(min=18, max=100),
            "is_active": True,
            **overrides,
        }

    def create_product(self, **overrides) -> dict[str, Any]:
        """Create test product data."""
        return {
            "id": self.fake.random_int(min=1, max=10000),
            "name": self.fake.word().title(),
            "description": self.fake.text(max_nb_chars=200),
            "price": round(self.fake.pyfloat(min_value=1, max_value=1000, right_digits=2), 2),
            "category": self.fake.word(),
            "in_stock": self.fake.boolean(),
            **overrides,
        }

    def create_batch(self, factory_method, count: int, **overrides) -> list[dict[str, Any]]:
        """Create a batch of test data."""
        return [factory_method(**overrides) for _ in range(count)]

    def create_realistic_dataset(self, size: int) -> dict[str, list[dict[str, Any]]]:
        """Create a realistic dataset for testing."""
        users = self.create_batch(self.create_user, size)
        products = self.create_batch(self.create_product, size * 2)

        return {
            "users": users,
            "products": products,
            "orders": self._create_orders(users, products, size),
        }

    def _create_orders(self, users: list[dict], products: list[dict], count: int) -> list[dict[str, Any]]:
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
                "status": random.choice(["pending", "completed", "cancelled"]),
            })
        return orders


@pytest.fixture
def data_factory():
    """Test data factory fixture."""
    return TestDataFactory()
