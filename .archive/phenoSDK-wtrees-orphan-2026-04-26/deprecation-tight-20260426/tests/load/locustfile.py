"""Load Testing with Locust for Pheno-SDK.

Multi-user scenarios and performance testing.
"""

import random

from locust import HttpUser, between, task


class PhenoUser(HttpUser):
    """
    Simulated user for Pheno-SDK load testing.
    """

    wait_time = between(1, 3)

    def on_start(self):
        """
        Called when a user starts.
        """
        self.client.verify = False  # Disable SSL verification for testing

    @task(3)
    def health_check(self):
        """
        Test health endpoint.
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def sdk_status(self):
        """
        Test SDK status endpoint.
        """
        with self.client.get("/sdk/status", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"SDK status failed: {response.status_code}")

    @task(1)
    def auth_request(self):
        """
        Test authentication request.
        """
        auth_data = {"username": f"user_{random.randint(1, 100)}", "password": "test_password"}

        with self.client.post("/auth/login", json=auth_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Auth request failed: {response.status_code}")

    @task(1)
    def data_processing(self):
        """
        Test data processing endpoint.
        """
        data = {"input": [random.random() for _ in range(10)], "operation": "process"}

        with self.client.post("/data/process", json=data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Data processing failed: {response.status_code}")


class HighLoadUser(PhenoUser):
    """
    High-load user with more frequent requests.
    """

    wait_time = between(0.1, 0.5)
    weight = 1  # Lower weight means fewer of these users

    @task(5)
    def rapid_health_check(self):
        """
        Rapid health checks.
        """
        self.health_check()

    @task(3)
    def rapid_data_processing(self):
        """
        Rapid data processing.
        """
        self.data_processing()
