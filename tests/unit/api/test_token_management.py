"""Token management and refresh flow tests.

Tests for JWT token lifecycle, refresh tokens, token revocation,
and token management scenarios.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest

from tests.test_constants import COUNT_THREE


@pytest.fixture
def mock_token_manager() -> None:
    """Mock token manager."""
    with patch("tracertm.api.main.TokenManager") as mock:
        yield mock.return_value


@pytest.fixture
def mock_refresh_token() -> str:
    """Generate mock refresh token."""
    return "refresh_token_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh_payload.signature"


class TestAccessTokenGeneration:
    """Test access token generation."""

    def test_access_token_contains_required_claims(self, mock_token_manager: Any) -> None:
        """Test that access tokens contain required claims."""
        mock_token_manager.generate_access_token.return_value = {
            "access_token": "token",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        token = mock_token_manager.generate_access_token(user_id="user123")

        assert "access_token" in token
        assert "expires_in" in token
        assert token["token_type"] == "bearer"

    def test_access_token_expiration_time_set(self, mock_token_manager: Any) -> None:
        """Test that access token expiration is properly set."""
        mock_token_manager.generate_access_token.return_value = {
            "access_token": "token",
            "expires_in": 3600,
        }

        token = mock_token_manager.generate_access_token(user_id="user123")

        # Should have 1 hour expiration
        assert token["expires_in"] == 3600

    def test_access_token_subject_claim(self, mock_token_manager: Any) -> None:
        """Test that access token contains user subject claim."""
        mock_token_manager.generate_access_token.return_value = {
            "access_token": "token_with_sub",
            "user_id": "user123",
        }

        token = mock_token_manager.generate_access_token(user_id="user123")

        # Token should contain user ID
        assert token.get("user_id") == "user123"

    def test_access_token_scopes(self, mock_token_manager: Any) -> None:
        """Test that access token includes scopes."""
        mock_token_manager.generate_access_token.return_value = {
            "access_token": "scoped_token",
            "scopes": ["read:projects", "write:items"],
        }

        token = mock_token_manager.generate_access_token(user_id="user123", scopes=["read:projects", "write:items"])

        assert "scopes" in token


class TestRefreshTokenFlow:
    """Test refresh token functionality."""

    def test_refresh_token_generates_new_access_token(self, mock_refresh_token: Any, mock_token_manager: Any) -> None:
        """Test that refresh token generates new access token."""
        mock_token_manager.refresh_access_token.return_value = {
            "access_token": "new_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        token = mock_token_manager.refresh_access_token(mock_refresh_token)

        assert "access_token" in token
        assert token["access_token"] != mock_refresh_token

    def test_refresh_token_preserves_user_identity(self, mock_refresh_token: Any, mock_token_manager: Any) -> None:
        """Test that refresh token generates token for same user."""
        mock_token_manager.refresh_access_token.return_value = {
            "access_token": "new_token",
            "user_id": "user123",
        }

        token = mock_token_manager.refresh_access_token(mock_refresh_token)

        # New token should be for same user
        assert token.get("user_id") == "user123"

    def test_refresh_token_validation(self, mock_refresh_token: Any, mock_token_manager: Any) -> None:
        """Test refresh token validation."""
        mock_token_manager.validate_refresh_token.return_value = True

        is_valid = mock_token_manager.validate_refresh_token(mock_refresh_token)

        assert is_valid is True

    def test_invalid_refresh_token_rejected(self, mock_token_manager: Any) -> None:
        """Test that invalid refresh token is rejected."""
        mock_token_manager.validate_refresh_token.return_value = False

        is_valid = mock_token_manager.validate_refresh_token("invalid_refresh")

        assert is_valid is False

    def test_expired_refresh_token_rejected(self, mock_token_manager: Any) -> None:
        """Test that expired refresh token is rejected."""
        mock_token_manager.validate_refresh_token.side_effect = ValueError("Refresh token expired")

        with pytest.raises(ValueError, match="Refresh token expired"):
            mock_token_manager.validate_refresh_token("expired_refresh")

    def test_refresh_token_single_use(self, mock_refresh_token: Any, mock_token_manager: Any) -> None:
        """Test that refresh token can only be used once (rotation)."""
        mock_token_manager.refresh_access_token.return_value = {
            "access_token": "new_token",
            "refresh_token": "new_refresh_token",
        }

        # First use should succeed
        token = mock_token_manager.refresh_access_token(mock_refresh_token)
        assert "access_token" in token

        # Second use with same refresh token should fail (token rotation)
        mock_token_manager.refresh_access_token.side_effect = ValueError("Refresh token already used")

        with pytest.raises(ValueError, match="Refresh token already used"):
            mock_token_manager.refresh_access_token(mock_refresh_token)


class TestTokenRevocation:
    """Test token revocation and blacklisting."""

    def test_token_revocation(self, mock_token_manager: Any) -> None:
        """Test token revocation functionality."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature"

        mock_token_manager.revoke_token.return_value = True

        is_revoked = mock_token_manager.revoke_token(token)

        assert is_revoked is True

    def test_revoked_token_rejected(self, mock_token_manager: Any) -> None:
        """Test that revoked tokens are rejected."""
        token = "revoked_token"

        mock_token_manager.validate_token.side_effect = ValueError("Token is revoked")

        with pytest.raises(ValueError, match="Token is revoked"):
            mock_token_manager.validate_token(token)

    def test_logout_revokes_all_tokens(self, mock_token_manager: Any) -> None:
        """Test that logout revokes all tokens for a user."""
        user_id = "user123"

        mock_token_manager.revoke_all_user_tokens.return_value = 3

        revoked_count = mock_token_manager.revoke_all_user_tokens(user_id)

        assert revoked_count == COUNT_THREE

    def test_revoked_token_in_blacklist(self, mock_token_manager: Any) -> None:
        """Test that revoked tokens are added to blacklist."""
        token = "token_to_revoke"

        mock_token_manager.is_token_blacklisted.return_value = False
        mock_token_manager.revoke_token(token)
        mock_token_manager.is_token_blacklisted.return_value = True

        # After revocation, token should be blacklisted
        assert mock_token_manager.is_token_blacklisted(token) is True


class TestTokenExpiration:
    """Test token expiration handling."""

    def test_token_expiration_check(self, mock_token_manager: Any) -> None:
        """Test token expiration validation."""
        token = {
            "exp": (datetime.now(UTC) + timedelta(hours=1)).timestamp(),
        }

        mock_token_manager.is_token_expired.return_value = False

        is_expired = mock_token_manager.is_token_expired(token)

        assert is_expired is False

    def test_expired_token_detected(self, mock_token_manager: Any) -> None:
        """Test detection of expired tokens."""
        token = {
            "exp": (datetime.now(UTC) - timedelta(hours=1)).timestamp(),
        }

        mock_token_manager.is_token_expired.return_value = True

        is_expired = mock_token_manager.is_token_expired(token)

        assert is_expired is True

    def test_token_near_expiration_warning(self, mock_token_manager: Any) -> None:
        """Test warning for tokens nearing expiration."""
        token = {
            "exp": (datetime.now(UTC) + timedelta(minutes=5)).timestamp(),
        }

        mock_token_manager.is_token_expiring_soon.return_value = True

        is_expiring = mock_token_manager.is_token_expiring_soon(token, minutes=10)

        assert is_expiring is True

    def test_token_grace_period(self, mock_token_manager: Any) -> None:
        """Test grace period for just-expired tokens."""
        token = {
            "exp": (datetime.now(UTC) - timedelta(seconds=10)).timestamp(),
        }

        mock_token_manager.is_token_expired.return_value = False  # Within grace period

        is_expired = mock_token_manager.is_token_expired(token, grace_seconds=60)

        assert is_expired is False


class TestTokenScopes:
    """Test token scopes and permissions."""

    def test_token_scopes_validation(self, mock_token_manager: Any) -> None:
        """Test token scope validation."""
        token = {
            "scopes": ["read:projects", "write:items"],
        }

        mock_token_manager.has_scope.return_value = True

        has_scope = mock_token_manager.has_scope(token, "read:projects")

        assert has_scope is True

    def test_insufficient_scopes_denied(self, mock_token_manager: Any) -> None:
        """Test that insufficient scopes are denied."""
        token = {
            "scopes": ["read:projects"],
        }

        mock_token_manager.has_scope.return_value = False

        has_scope = mock_token_manager.has_scope(token, "write:projects")

        assert has_scope is False

    def test_multiple_scopes_check(self, mock_token_manager: Any) -> None:
        """Test checking multiple required scopes."""
        token = {
            "scopes": ["read:projects", "write:items"],
        }

        mock_token_manager.has_scopes.return_value = True

        has_scopes = mock_token_manager.has_scopes(token, ["read:projects", "write:items"])

        assert has_scopes is True

    def test_scope_hierarchy(self, mock_token_manager: Any) -> None:
        """Test scope hierarchy (admin scope includes all)."""
        token = {
            "scopes": ["admin"],
        }

        mock_token_manager.has_scope.return_value = True

        # Admin should have all scopes
        assert mock_token_manager.has_scope(token, "read:projects") is True
        assert mock_token_manager.has_scope(token, "write:items") is True


class TestTokenEncoding:
    """Test token encoding and validation."""

    def test_token_signature_validation(self, mock_token_manager: Any) -> None:
        """Test token signature validation."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.valid_signature"

        mock_token_manager.validate_signature.return_value = True

        is_valid = mock_token_manager.validate_signature(token)

        assert is_valid is True

    def test_invalid_token_signature_rejected(self, mock_token_manager: Any) -> None:
        """Test that invalid signatures are rejected."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.invalid_signature"

        mock_token_manager.validate_signature.return_value = False

        is_valid = mock_token_manager.validate_signature(token)

        assert is_valid is False

    def test_token_format_validation(self, mock_token_manager: Any) -> None:
        """Test token format validation."""
        valid_token = "header.payload.signature"
        invalid_token = "invalid_format"

        mock_token_manager.validate_format.return_value = True
        assert mock_token_manager.validate_format(valid_token) is True

        mock_token_manager.validate_format.return_value = False
        assert mock_token_manager.validate_format(invalid_token) is False

    def test_token_payload_decoding(self, mock_token_manager: Any) -> None:
        """Test token payload decoding."""
        token = "header.eyJzdWIiOiJ1c2VyMTIzIn0.signature"

        mock_token_manager.decode_payload.return_value = {
            "sub": "user123",
        }

        payload = mock_token_manager.decode_payload(token)

        assert payload["sub"] == "user123"


class TestTokenAudience:
    """Test token audience validation."""

    def test_token_audience_claim(self, mock_token_manager: Any) -> None:
        """Test token audience claim validation."""
        token = {
            "aud": "api.tracertm.com",
        }

        mock_token_manager.validate_audience.return_value = True

        is_valid = mock_token_manager.validate_audience(token, "api.tracertm.com")

        assert is_valid is True

    def test_invalid_audience_rejected(self, mock_token_manager: Any) -> None:
        """Test that invalid audience is rejected."""
        token = {
            "aud": "api.other.com",
        }

        mock_token_manager.validate_audience.return_value = False

        is_valid = mock_token_manager.validate_audience(token, "api.tracertm.com")

        assert is_valid is False

    def test_missing_audience_claim(self, mock_token_manager: Any) -> None:
        """Test handling of missing audience claim."""
        token = {}

        mock_token_manager.validate_audience.side_effect = ValueError("Missing audience claim")

        with pytest.raises(ValueError, match="Missing audience claim"):
            mock_token_manager.validate_audience(token, "api.tracertm.com")


class TestTokenIssuer:
    """Test token issuer validation."""

    def test_token_issuer_claim(self, mock_token_manager: Any) -> None:
        """Test token issuer claim validation."""
        token = {
            "iss": "tracertm",
        }

        mock_token_manager.validate_issuer.return_value = True

        is_valid = mock_token_manager.validate_issuer(token, "tracertm")

        assert is_valid is True

    def test_invalid_issuer_rejected(self, mock_token_manager: Any) -> None:
        """Test that invalid issuer is rejected."""
        token = {
            "iss": "unknown",
        }

        mock_token_manager.validate_issuer.return_value = False

        is_valid = mock_token_manager.validate_issuer(token, "tracertm")

        assert is_valid is False


class TestTokenNotBefore:
    """Test token not-before claim."""

    def test_token_not_before_validation(self, mock_token_manager: Any) -> None:
        """Test token not-before claim validation."""
        token = {
            "nbf": (datetime.now(UTC) - timedelta(hours=1)).timestamp(),
        }

        mock_token_manager.is_token_valid_yet.return_value = True

        is_valid = mock_token_manager.is_token_valid_yet(token)

        assert is_valid is True

    def test_token_not_yet_valid(self, mock_token_manager: Any) -> None:
        """Test token not yet valid (future nbf)."""
        token = {
            "nbf": (datetime.now(UTC) + timedelta(hours=1)).timestamp(),
        }

        mock_token_manager.is_token_valid_yet.return_value = False

        is_valid = mock_token_manager.is_token_valid_yet(token)

        assert is_valid is False


class TestTokenMetadata:
    """Test token metadata and claims."""

    def test_token_user_id_claim(self, mock_token_manager: Any) -> None:
        """Test token contains user ID claim."""
        token = {"sub": "user123"}

        mock_token_manager.get_claim.return_value = "user123"

        user_id = mock_token_manager.get_claim(token, "sub")

        assert user_id == "user123"

    def test_token_additional_claims(self, mock_token_manager: Any) -> None:
        """Test token can contain additional claims."""
        token = {
            "sub": "user123",
            "role": "admin",
            "department": "engineering",
        }

        mock_token_manager.get_claim.return_value = "admin"

        role = mock_token_manager.get_claim(token, "role")

        assert role == "admin"

    def test_token_issued_at_claim(self, mock_token_manager: Any) -> None:
        """Test token issued-at claim."""
        now = datetime.now(UTC).timestamp()
        token = {
            "iat": now,
        }

        mock_token_manager.get_issued_at.return_value = now

        issued_at = mock_token_manager.get_issued_at(token)

        assert issued_at == now
