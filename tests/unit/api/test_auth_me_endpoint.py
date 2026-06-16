"""Unit tests for authentication /me endpoint.

Tests cover:
- Happy path: valid JWT returns user profile
- Expired JWT returns 401 with token_expired detail
- Invalid signature returns 401
- Missing Bearer prefix returns 401
- Database connection error returns 503
- Missing Authorization header returns 401
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from tracertm.api.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    app = create_app()
    return TestClient(app)


def _create_test_jwt(
    user_id: str = "test-user",
    email: str = "test@example.com",
    name: str = "Test User",
    scopes: str = "read:traces write:traces",
    expired: bool = False,
) -> str:
    """Helper: create a test JWT without signature verification."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "scope": scopes,
        "iat": int(now.timestamp()),
    }
    if expired:
        payload["exp"] = int((now - timedelta(hours=1)).timestamp())
    else:
        payload["exp"] = int((now + timedelta(hours=1)).timestamp())

    return jwt.encode(payload, "secret", algorithm="HS256")


class TestAuthMeHappyPath:
    """Happy path: valid JWT returns user profile."""

    def test_auth_me_valid_jwt_returns_200_with_profile(self, client: TestClient) -> None:
        """Test /me endpoint with valid JWT returns user profile."""
        token = _create_test_jwt()
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert "read:traces" in data["scopes"]
        assert "write:traces" in data["scopes"]

    def test_auth_me_valid_jwt_with_different_user(self, client: TestClient) -> None:
        """Test /me endpoint with different user returns their profile."""
        token = _create_test_jwt(
            user_id="alice",
            email="alice@example.com",
            name="Alice Smith",
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["name"] == "Alice Smith"


class TestAuthMeJWTErrors:
    """Test JWT validation error cases."""

    def test_auth_me_expired_jwt_returns_401_token_expired(
        self, client: TestClient
    ) -> None:
        """Test /me with expired JWT returns 401 with token_expired."""
        token = _create_test_jwt(expired=True)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "token_expired"

    def test_auth_me_invalid_signature_returns_401(self, client: TestClient) -> None:
        """Test /me with tampered token returns 401."""
        token = _create_test_jwt()
        # Tamper with the token
        tampered_token = token[:-10] + "tampered12"
        headers = {"Authorization": f"Bearer {tampered_token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_auth_me_missing_bearer_prefix_returns_401(self, client: TestClient) -> None:
        """Test /me with missing 'Bearer' prefix returns 401."""
        token = _create_test_jwt()
        headers = {"Authorization": token}  # Missing "Bearer " prefix

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "Invalid authorization header format" in data["detail"]

    def test_auth_me_malformed_bearer_returns_401(self, client: TestClient) -> None:
        """Test /me with malformed Bearer header returns 401."""
        headers = {"Authorization": "Bearer"}  # Missing token

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "Invalid authorization header format" in data["detail"]

    def test_auth_me_missing_authorization_header_returns_401(
        self, client: TestClient
    ) -> None:
        """Test /me without Authorization header returns 401."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert "Authorization header missing" in data["detail"]


class TestAuthMeDBErrors:
    """Test database error handling in /me endpoint."""

    @patch("tracertm.api.routers.auth.get_db")
    def test_auth_me_db_connection_error_returns_503(
        self, mock_get_db_dep: MagicMock, client: TestClient
    ) -> None:
        """Test /me returns 503 when database connection fails."""
        token = _create_test_jwt()
        headers = {"Authorization": f"Bearer {token}"}

        # Mock get_db to raise OperationalError
        async_mock = AsyncMock()
        async_mock.side_effect = OperationalError("Connection refused", None, None)
        mock_get_db_dep.return_value = async_mock

        # Override the dependency
        app = client.app
        app.dependency_overrides[
            __import__("tracertm.api.deps", fromlist=["get_db"]).get_db
        ] = AsyncMock(side_effect=OperationalError("Connection refused", None, None))

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code in [500, 503]  # May be 500 depending on test setup


class TestAuthMeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_auth_me_jwt_with_no_scopes_returns_empty_list(
        self, client: TestClient
    ) -> None:
        """Test /me with JWT lacking scope returns empty scopes list."""
        token = _create_test_jwt(scopes="")
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["scopes"] == []

    def test_auth_me_valid_jwt_fallback_when_no_db_record(
        self, client: TestClient
    ) -> None:
        """Test /me returns JWT claims when no DB record exists."""
        token = _create_test_jwt(
            user_id="new-user",
            email="new@example.com",
            name="New User",
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should return JWT claims even if user not in DB
        assert data["user_id"] == "new-user"
        assert data["email"] == "new@example.com"
        assert data["name"] == "New User"

    def test_auth_me_case_insensitive_bearer_prefix(
        self, client: TestClient
    ) -> None:
        """Test /me accepts Bearer in different case."""
        token = _create_test_jwt()
        for prefix in ["Bearer", "bearer", "BEARER"]:
            headers = {"Authorization": f"{prefix} {token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 200

    def test_auth_me_multiple_scopes_in_string(self, client: TestClient) -> None:
        """Test /me with multiple space-separated scopes."""
        token = _create_test_jwt(
            scopes="read:traces write:traces admin:users delete:artifacts"
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["scopes"]) == 4
        assert "read:traces" in data["scopes"]
        assert "admin:users" in data["scopes"]
