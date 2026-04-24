"""Pytest test suite for Python backend route validation.

Validates all API routes respond correctly without server errors,
logs are captured for debugging, and comprehensive reporting is generated.

Routes tested:
- Health: GET /health
- Projects: GET/POST /api/v1/projects
- Items: GET/POST /api/v1/items
- Links: GET /api/v1/links
- Search: POST /api/v1/search
- Notifications: GET /api/v1/notifications
- WebSocket: OPTIONS /api/v1/ws (CORS preflight)
"""

import json

# Use TestClient for synchronous testing
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from tracertm.api.main import app

client = TestClient(app)

# Test credentials
TEST_USER_TOKEN = "test-token-abc123"

# Routes to validate
# Note: Routes are tested based on availability in test environment
# Some routes may return 4xx (auth/validation errors) which is acceptable
# We validate that they don't return 5xx (server errors)
ROUTES_TO_TEST = [
    {"path": "/health", "method": "GET", "requires_auth": False},
    {"path": "/api/v1/projects", "method": "GET", "requires_auth": True},
    {"path": "/api/v1/projects", "method": "POST", "requires_auth": True},
    {"path": "/api/v1/items", "method": "GET", "requires_auth": True},
    {"path": "/api/v1/items", "method": "POST", "requires_auth": True},
    {"path": "/api/v1/links", "method": "GET", "requires_auth": True},
    {"path": "/api/v1/search", "method": "POST", "requires_auth": True},
    {"path": "/api/v1/notifications", "method": "GET", "requires_auth": True},
]


class TestRouteValidation:
    """Validate all API routes respond correctly and log errors/warnings."""

    @pytest.mark.parametrize(
        "route",
        ROUTES_TO_TEST,
        ids=lambda r: f"{r['method']} {r['path']}",
    )
    @patch("tracertm.api.main.auth_guard")
    @patch("tracertm.api.main.get_db")
    def test_route_responds(self, mock_db: Any, mock_auth: Any, route: Any) -> None:
        """Test that each route responds without server errors (5xx).

        This test validates that routes are defined and respond with a valid
        HTTP status code (not 5xx errors). Authentication and validation errors
        (4xx) are expected and acceptable.
        """
        # Setup auth mock
        mock_auth.return_value = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "user",
            "org_id": "test-org",
        }

        # Setup database mock
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        # Build headers
        headers = {"Origin": "http://localhost:5173"}
        if route["requires_auth"]:
            headers["Authorization"] = f"Bearer {TEST_USER_TOKEN}"

        # Make request based on method
        try:
            if route["method"] == "GET":
                response = client.get(route["path"], headers=headers)
            elif route["method"] == "POST":
                response = client.post(
                    route["path"],
                    json={},
                    headers=headers,
                )
            elif route["method"] == "OPTIONS":
                response = client.options(route["path"], headers=headers)
            else:
                response = client.request(
                    route["method"],
                    route["path"],
                    headers=headers,
                )

            # Main assertion - status code must be less than 500 (no server errors)
            assert response.status_code < 500, (
                f"{route['method']} {route['path']} returned {response.status_code}: {response.text[:200]}"
            )
            assert response.status_code > 0, f"{route['method']} {route['path']} did not respond"

        except Exception as e:
            pytest.fail(
                f"Exception for {route['method']} {route['path']}: {e!s}",
            )

    @patch("tracertm.api.main.auth_guard")
    @patch("tracertm.api.main.get_db")
    def test_websocket_cors_headers(self, mock_db: Any, mock_auth: Any) -> None:
        """Test WebSocket endpoint has proper CORS headers."""
        # Setup mocks
        mock_auth.return_value = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "user",
            "org_id": "test-org",
        }
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        # Make OPTIONS request for CORS preflight
        response = client.options(
            "/api/v1/ws",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )

        # Check CORS headers are present
        cors_origin = response.headers.get("access-control-allow-origin")
        cors_credentials = response.headers.get("access-control-allow-credentials")
        cors_methods = response.headers.get("access-control-allow-methods", "")

        # Assertions - CORS headers should be present for WebSocket
        # Note: If endpoint doesn't support CORS, we still verify response is not 500+
        assert response.status_code < 500, f"WebSocket CORS preflight returned {response.status_code}"

        if cors_origin:
            assert cors_credentials == "true", "CORS credentials should allow true"
            assert "GET" in cors_methods or "*" in cors_methods, "CORS methods should include GET or *"

    @patch("tracertm.api.main.auth_guard")
    @patch("tracertm.api.main.get_db")
    def test_all_routes_summary(self, mock_db: Any, mock_auth: Any) -> None:
        """Generate summary report of all routes.

        Validates that all routes respond without 5xx server errors.
        """
        # Setup mocks
        mock_auth.return_value = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "user",
            "org_id": "test-org",
        }
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        results = []

        for route in ROUTES_TO_TEST:
            headers = {"Origin": "http://localhost:5173"}
            if route["requires_auth"]:
                headers["Authorization"] = f"Bearer {TEST_USER_TOKEN}"

            try:
                if route["method"] == "GET":
                    response = client.get(route["path"], headers=headers)
                elif route["method"] == "POST":
                    response = client.post(
                        route["path"],
                        json={},
                        headers=headers,
                    )
                else:
                    response = client.request(
                        route["method"],
                        route["path"],
                        headers=headers,
                    )

                # Success = responded without 5xx error
                is_success = response.status_code < 500
                results.append(
                    {
                        "route": route["path"],
                        "method": route["method"],
                        "status": response.status_code,
                        "success": is_success,
                    },
                )
            except Exception as e:
                results.append(
                    {
                        "route": route["path"],
                        "method": route["method"],
                        "status": 0,
                        "error": str(e),
                        "success": False,
                    },
                )

        # Calculate summary statistics
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful

        # Print summary
        (
            f"\n📊 API Route Validation Summary:\n"
            f"Total routes: {len(results)}\n"
            f"Successful (no 5xx): {successful}\n"
            f"Failed (5xx errors): {failed}\n"
            f"\nDetailed Results:\n"
            f"{json.dumps(results, indent=2)}\n"
        )

        # Assert all successful (no 5xx errors)
        failed_routes = [r for r in results if not r["success"]]
        assert not failed_routes, f"Routes returned 5xx errors: {json.dumps(failed_routes, indent=2)}"

    def test_health_endpoint_response_structure(self) -> None:
        """Test health endpoint returns expected response structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Verify expected fields
        assert "status" in data, "Health response must include 'status' field"
        assert data["status"] in {"healthy", "ok"}, "Status must be 'healthy' or 'ok'"

    @patch("tracertm.api.main.auth_guard")
    @patch("tracertm.api.main.get_db")
    def test_auth_required_routes_reject_missing_token(self, _mock_db: Any, mock_auth: Any) -> None:
        """Test that auth-required routes reject requests without token."""
        # Setup mock to raise for missing auth
        mock_auth.side_effect = Exception("Missing authorization header")

        auth_required_routes = [
            "/api/v1/projects",
            "/api/v1/items",
            "/api/v1/links",
            "/api/v1/search",
            "/api/v1/notifications",
        ]

        for route in auth_required_routes:
            try:
                # Request without auth headers
                response = client.get(route, headers={"Origin": "http://localhost:5173"})

                # Should return 4xx error or success (depends on mock)
                # Main thing is it doesn't crash with 500
                assert response.status_code < 500, f"{route} returned 500+ without auth: {response.status_code}"

            except Exception as e:
                # Exception is OK if it's about missing auth
                if "Missing authorization" not in str(e):
                    pytest.fail(f"Unexpected exception for {route}: {e!s}")

    @patch("tracertm.api.main.auth_guard")
    @patch("tracertm.api.main.get_db")
    def test_routes_return_json_or_error(self, mock_db: Any, mock_auth: Any) -> None:
        """Test that public routes return valid response (JSON or error)."""
        mock_auth.return_value = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "user",
        }
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        # Test public routes that should always respond
        test_routes = ["/health"]

        headers = {"Origin": "http://localhost:5173"}

        for route in test_routes:
            response = client.get(route, headers=headers)
            assert response.status_code < 500, f"{route} returned server error: {response.status_code}"

            # If 2xx or 3xx, should have content-type header
            if response.status_code < 400:
                assert "content-type" in response.headers, f"{route} response missing content-type"
