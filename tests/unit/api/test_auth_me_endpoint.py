"""Tests for the /auth/me endpoint implementation.

Verifies that the endpoint correctly fetches user data from WorkOS API.
"""

from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.test_constants import HTTP_INTERNAL_SERVER_ERROR, HTTP_NOT_FOUND, HTTP_OK, HTTP_UNAUTHORIZED


@pytest.fixture
def mock_workos_user() -> None:
    """Mock WorkOS user response."""
    return {
        "id": "user_01HXYZ123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "email_verified": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z",
        "profile_picture_url": "https://example.com/photo.jpg",
    }


@pytest.fixture
def mock_jwt_claims() -> None:
    """Mock JWT claims from auth_guard."""
    return {
        "sub": "user_01HXYZ123",
        "email": "test@example.com",
        "iat": 1234567890,
        "exp": 1234571490,
        "org_id": "org_01ABC",
        "org_name": "Test Organization",
    }


class TestAuthMeEndpoint:
    """Test /auth/me endpoint functionality."""

    def test_me_endpoint_returns_user_data(self, mock_workos_user: Any, mock_jwt_claims: Any) -> None:
        """Test that /me endpoint returns real user data from WorkOS."""
        from tracertm.api.main import app

        client = TestClient(app)
        headers = {"Authorization": "Bearer valid_token"}

        # Mock auth_guard to return claims
        # Mock get_user to return WorkOS user data
        with (
            patch("tracertm.api.routers.auth.auth_guard") as mock_auth,
            patch("tracertm.api.routers.auth.get_user") as mock_get_user,
        ):
            mock_auth.return_value = mock_jwt_claims
            mock_get_user.return_value = mock_workos_user

            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == HTTP_OK
            data = response.json()

            # Verify user data structure
            assert "user" in data
            assert "claims" in data
            assert "account" in data

            # Verify user fields
            user = data["user"]
            assert user["id"] == "user_01HXYZ123"
            assert user["email"] == "test@example.com"
            assert user["firstName"] == "Test"
            assert user["lastName"] == "User"
            assert user["emailVerified"] is True
            assert user["profilePictureUrl"] == "https://example.com/photo.jpg"

            # Verify claims passed through
            assert data["claims"]["sub"] == "user_01HXYZ123"

            # Verify account data
            assert data["account"]["id"] == "org_01ABC"
            assert data["account"]["name"] == "Test Organization"

            # Verify get_user was called with correct user_id
            mock_get_user.assert_called_once_with("user_01HXYZ123")

    def test_me_endpoint_missing_user_id_in_claims(self) -> None:
        """Test that /me endpoint returns 401 if user_id missing in claims."""
        from tracertm.api.main import app

        client = TestClient(app)
        headers = {"Authorization": "Bearer valid_token"}

        # Mock auth_guard to return claims without 'sub'
        with patch("tracertm.api.routers.auth.auth_guard") as mock_auth:
            mock_auth.return_value = {"email": "test@example.com"}  # Missing 'sub'

            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == HTTP_UNAUTHORIZED
            assert "missing user ID" in response.json()["detail"]

    def test_me_endpoint_user_not_found(self, mock_jwt_claims: Any) -> None:
        """Test that /me endpoint returns 404 if user not found in WorkOS."""
        from tracertm.api.main import app

        client = TestClient(app)
        headers = {"Authorization": "Bearer valid_token"}

        # Mock auth_guard to return claims
        # Mock get_user to raise a 404 error
        with (
            patch("tracertm.api.routers.auth.auth_guard") as mock_auth,
            patch("tracertm.api.routers.auth.get_user") as mock_get_user,
        ):
            mock_auth.return_value = mock_jwt_claims
            mock_get_user.side_effect = Exception("404 User not found")

            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == HTTP_NOT_FOUND
            assert "not found" in response.json()["detail"]

    def test_me_endpoint_workos_api_error(self, mock_jwt_claims: Any) -> None:
        """Test that /me endpoint returns 500 on WorkOS API error."""
        from tracertm.api.main import app

        client = TestClient(app)
        headers = {"Authorization": "Bearer valid_token"}

        # Mock auth_guard to return claims
        # Mock get_user to raise a general API error
        with (
            patch("tracertm.api.routers.auth.auth_guard") as mock_auth,
            patch("tracertm.api.routers.auth.get_user") as mock_get_user,
        ):
            mock_auth.return_value = mock_jwt_claims
            mock_get_user.side_effect = Exception("API connection failed")

            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == HTTP_INTERNAL_SERVER_ERROR
            assert "Failed to fetch user information" in response.json()["detail"]

    def test_me_endpoint_workos_not_configured(self, mock_jwt_claims: Any) -> None:
        """Test that /me endpoint returns 500 if WorkOS not configured."""
        from tracertm.api.main import app

        client = TestClient(app)
        headers = {"Authorization": "Bearer valid_token"}

        # Mock auth_guard to return claims
        # Mock get_user to raise a ValueError (configuration error)
        with (
            patch("tracertm.api.routers.auth.auth_guard") as mock_auth,
            patch("tracertm.api.routers.auth.get_user") as mock_get_user,
        ):
            mock_auth.return_value = mock_jwt_claims
            mock_get_user.side_effect = ValueError("WORKOS_API_KEY is required")

            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == HTTP_INTERNAL_SERVER_ERROR
            assert "not configured" in response.json()["detail"]

    def test_me_endpoint_no_account_in_claims(self, mock_workos_user: Any) -> None:
        """Test that /me endpoint handles missing account data in claims."""
        from tracertm.api.main import app

        client = TestClient(app)
        headers = {"Authorization": "Bearer valid_token"}

        # Mock auth_guard to return claims without org_id
        claims_no_org = {
            "sub": "user_01HXYZ123",
            "email": "test@example.com",
            "iat": 1234567890,
            "exp": 1234571490,
        }

        with (
            patch("tracertm.api.routers.auth.auth_guard") as mock_auth,
            patch("tracertm.api.routers.auth.get_user") as mock_get_user,
        ):
            mock_auth.return_value = claims_no_org
            mock_get_user.return_value = mock_workos_user

            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == HTTP_OK
            data = response.json()

            # Account should be None
            assert data["account"] is None
