"""
Test data factory for generating test data.

This module provides a factory for generating test data across different projects.
"""

import random
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class TestDataFactory:
    """Factory for generating test data."""

    seed: int | None = None
    _random: random.Random = field(default_factory=random.Random)

    def __post_init__(self):
        if self.seed is not None:
            self._random.seed(self.seed)

    def random_string(self, length: int = 10, chars: str = None) -> str:
        """Generate a random string."""
        if chars is None:
            chars = string.ascii_letters + string.digits
        return "".join(self._random.choices(chars, k=length))

    def random_email(self, domain: str = "example.com") -> str:
        """Generate a random email address."""
        username = self.random_string(8, string.ascii_lowercase + string.digits)
        return f"{username}@{domain}"

    def random_uuid(self) -> str:
        """Generate a random UUID."""
        return str(uuid.uuid4())

    def random_int(self, min_val: int = 0, max_val: int = 100) -> int:
        """Generate a random integer."""
        return self._random.randint(min_val, max_val)

    def random_float(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Generate a random float."""
        return self._random.uniform(min_val, max_val)

    def random_choice(self, choices: list[Any]) -> Any:
        """Choose a random item from a list."""
        return self._random.choice(choices)

    def random_choices(self, choices: list[Any], k: int = 1) -> list[Any]:
        """Choose multiple random items from a list."""
        return self._random.choices(choices, k=k)

    def random_bool(self) -> bool:
        """Generate a random boolean."""
        return self._random.choice([True, False])

    def random_datetime(self, start: datetime = None, end: datetime = None) -> datetime:
        """Generate a random datetime."""
        if start is None:
            start = datetime.now() - timedelta(days=365)
        if end is None:
            end = datetime.now()

        delta = end - start
        random_seconds = self._random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    def random_date(self, start: datetime = None, end: datetime = None) -> datetime:
        """Generate a random date (time set to 00:00:00)."""
        dt = self.random_datetime(start, end)
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def user_data(self, **overrides) -> dict[str, Any]:
        """Generate user test data."""
        data = {
            "id": self.random_uuid(),
            "username": self.random_string(8, string.ascii_lowercase + string.digits),
            "email": self.random_email(),
            "full_name": f"{self.random_string(6)} {self.random_string(8)}",
            "roles": self.random_choices(["user", "admin", "moderator"], k=self.random_int(1, 3)),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
            "is_active": self.random_bool(),
        }
        data.update(overrides)
        return data

    def organization_data(self, **overrides) -> dict[str, Any]:
        """Generate organization test data."""
        data = {
            "id": self.random_uuid(),
            "name": f"Test Organization {self.random_string(6)}",
            "description": f"Test organization description {self.random_string(20)}",
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
            "is_active": self.random_bool(),
        }
        data.update(overrides)
        return data

    def project_data(self, organization_id: str = None, **overrides) -> dict[str, Any]:
        """Generate project test data."""
        data = {
            "id": self.random_uuid(),
            "name": f"Test Project {self.random_string(6)}",
            "description": f"Test project description {self.random_string(20)}",
            "status": self.random_choice(["active", "inactive", "archived"]),
            "organization_id": organization_id or self.random_uuid(),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
        }
        data.update(overrides)
        return data

    def document_data(self, project_id: str = None, **overrides) -> dict[str, Any]:
        """Generate document test data."""
        data = {
            "id": self.random_uuid(),
            "title": f"Test Document {self.random_string(6)}",
            "content": f"Test document content {self.random_string(50)}",
            "project_id": project_id or self.random_uuid(),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
        }
        data.update(overrides)
        return data

    def requirement_data(self, document_id: str = None, **overrides) -> dict[str, Any]:
        """Generate requirement test data."""
        data = {
            "id": self.random_uuid(),
            "title": f"Test Requirement {self.random_string(6)}",
            "description": f"Test requirement description {self.random_string(30)}",
            "priority": self.random_choice(["low", "medium", "high", "critical"]),
            "status": self.random_choice(["draft", "review", "approved", "rejected"]),
            "document_id": document_id or self.random_uuid(),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
        }
        data.update(overrides)
        return data

    def test_data(self, project_id: str = None, **overrides) -> dict[str, Any]:
        """Generate test entity data."""
        data = {
            "id": self.random_uuid(),
            "name": f"Test {self.random_string(6)}",
            "description": f"Test description {self.random_string(20)}",
            "status": self.random_choice(["pending", "running", "passed", "failed", "skipped"]),
            "project_id": project_id or self.random_uuid(),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
        }
        data.update(overrides)
        return data

    def relationship_data(self, source_id: str = None, target_id: str = None, **overrides) -> dict[str, Any]:
        """Generate relationship test data."""
        data = {
            "id": self.random_uuid(),
            "source_id": source_id or self.random_uuid(),
            "target_id": target_id or self.random_uuid(),
            "relationship_type": self.random_choice(["parent", "child", "sibling", "related"]),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
        }
        data.update(overrides)
        return data

    def workflow_data(self, project_id: str = None, **overrides) -> dict[str, Any]:
        """Generate workflow test data."""
        data = {
            "id": self.random_uuid(),
            "name": f"Test Workflow {self.random_string(6)}",
            "description": f"Test workflow description {self.random_string(20)}",
            "status": self.random_choice(["draft", "active", "paused", "completed"]),
            "project_id": project_id or self.random_uuid(),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
        }
        data.update(overrides)
        return data

    def query_data(self, project_id: str = None, **overrides) -> dict[str, Any]:
        """Generate query test data."""
        data = {
            "id": self.random_uuid(),
            "name": f"Test Query {self.random_string(6)}",
            "query": f"SELECT * FROM test_table WHERE id = '{self.random_uuid()}'",
            "project_id": project_id or self.random_uuid(),
            "created_at": self.random_datetime(),
            "updated_at": self.random_datetime(),
        }
        data.update(overrides)
        return data

    def create_related_data(self, entity_type: str, count: int = 5, **overrides) -> list[dict[str, Any]]:
        """Create related test data."""
        data = []
        for _ in range(count):
            if entity_type == "user":
                data.append(self.user_data(**overrides))
            elif entity_type == "organization":
                data.append(self.organization_data(**overrides))
            elif entity_type == "project":
                data.append(self.project_data(**overrides))
            elif entity_type == "document":
                data.append(self.document_data(**overrides))
            elif entity_type == "requirement":
                data.append(self.requirement_data(**overrides))
            elif entity_type == "test":
                data.append(self.test_data(**overrides))
            elif entity_type == "relationship":
                data.append(self.relationship_data(**overrides))
            elif entity_type == "workflow":
                data.append(self.workflow_data(**overrides))
            elif entity_type == "query":
                data.append(self.query_data(**overrides))
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")
        return data
