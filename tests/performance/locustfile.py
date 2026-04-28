"""Locust load testing configuration for trace management system.

This file defines user behaviors for load testing:
- Item CRUD operations
- Link operations
- Query operations
- Mixed workload scenarios

Usage:
    locust -f locustfile.py --host=http://localhost:8000
"""

import random
import time

from locust import HttpUser, TaskSet, constant, task


class UserBehavior(TaskSet):
    """Define user behavior and tasks."""

    def on_start(self) -> None:
        """Called when a user is spawned."""
        self.project_id = "load-test-proj"
        self.item_ids = []
        self.link_ids = []

    # ============================================================
    # Item Operations
    # ============================================================

    @task(3)
    def create_item(self) -> None:
        """Create a new item."""
        item_id = f"item-{int(time.time() * 1000)}-{random.randint(0, 10000)}"
        payload = {
            "id": item_id,
            "project_id": self.project_id,
            "title": f"Load Test Item {item_id}",
            "view": "FEATURE",
            "item_type": "feature",
            "status": "todo",
            "priority": random.choice(["low", "medium", "high"]),
        }

        with self.client.post("/api/items", json=payload, catch_response=True) as response:
            if response.status_code == 201:
                self.item_ids.append(item_id)
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(2)
    def read_item(self) -> None:
        """Read an item."""
        if self.item_ids:
            item_id = random.choice(self.item_ids)
            with self.client.get(f"/api/items/{item_id}", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed with status {response.status_code}")

    @task(2)
    def update_item(self) -> None:
        """Update an item."""
        if self.item_ids:
            item_id = random.choice(self.item_ids)
            payload = {
                "status": random.choice(["todo", "in_progress", "done"]),
                "priority": random.choice(["low", "medium", "high"]),
            }

            with self.client.put(f"/api/items/{item_id}", json=payload, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed with status {response.status_code}")

    @task(1)
    def delete_item(self) -> None:
        """Delete an item."""
        if self.item_ids:
            item_id = self.item_ids.pop(0)
            with self.client.delete(f"/api/items/{item_id}", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed with status {response.status_code}")

    # ============================================================
    # Query Operations
    # ============================================================

    @task(2)
    def list_items(self) -> None:
        """List items with pagination."""
        params = {
            "project_id": self.project_id,
            "limit": 20,
            "offset": random.randint(0, 100),
        }

        with self.client.get("/api/items", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(1)
    def search_items(self) -> None:
        """Search items by query."""
        search_terms = ["feature", "bug", "test", "requirement"]
        query = random.choice(search_terms)

        params = {
            "project_id": self.project_id,
            "q": query,
        }

        with self.client.get("/api/items/search", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    # ============================================================
    # Link Operations
    # ============================================================

    @task(2)
    def create_link(self) -> None:
        """Create a link between items."""
        if len(self.item_ids) >= 2:
            link_id = f"link-{int(time.time() * 1000)}-{random.randint(0, 10000)}"
            source_id = random.choice(self.item_ids)
            target_id = random.choice(self.item_ids)

            if source_id != target_id:
                payload = {
                    "id": link_id,
                    "project_id": self.project_id,
                    "source_id": source_id,
                    "target_id": target_id,
                    "link_type": random.choice(["depends_on", "related_to", "blocks"]),
                }

                with self.client.post("/api/links", json=payload, catch_response=True) as response:
                    if response.status_code == 201:
                        self.link_ids.append(link_id)
                        response.success()
                    else:
                        response.failure(f"Failed with status {response.status_code}")

    @task(1)
    def list_links(self) -> None:
        """List links for a project."""
        params = {
            "project_id": self.project_id,
        }

        with self.client.get("/api/links", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")


class TraceUser(HttpUser):
    """Simulated user for load testing."""

    tasks = [UserBehavior]
    wait_time = constant(0.5)  # Wait 500ms between tasks


class HighLoadUser(HttpUser):
    """High-intensity load user."""

    tasks = [UserBehavior]
    wait_time = constant(0.1)  # Wait 100ms between tasks


class LowLoadUser(HttpUser):
    """Low-intensity load user."""

    tasks = [UserBehavior]
    wait_time = constant(2.0)  # Wait 2s between tasks
