from typing import Any

"""Tests for token bridge service."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from jwt import PyJWKClient

from tracertm.services.token_bridge import TokenBridge, get_token_bridge

TEST_SECRET = "test-secret-must-be-at-least-32-bytes-long-for-security"
_TEST_WRONG_SECRET = "different-secret-at-least-32-bytes-long-for-tests"
TEST_JWKS_URL = "https://api.workos.com/sso/jwks/client_test"


@pytest.fixture
def token_bridge() -> None:
    """Create test token bridge."""
    return TokenBridge(
        hs_secret=TEST_SECRET,
        jwks_url=TEST_JWKS_URL,
        audience="client_test",
        issuer="https://api.workos.com/",
    )


class TestTokenBridgeInitialization:
    """Test token bridge initialization."""

    def test_valid_configuration(self) -> None:
        """Test token bridge with valid configuration."""
        bridge = TokenBridge(
            hs_secret=TEST_SECRET,
            jwks_url=TEST_JWKS_URL,
            audience="client_test",
            issuer="https://api.workos.com/",
        )
        assert bridge.hs_secret == TEST_SECRET
        assert bridge.jwks_url == TEST_JWKS_URL
        assert bridge.audience == "client_test"
        assert bridge.issuer == "https://api.workos.com/"

    def test_secret_too_short(self) -> None:
        """Test that short secrets are rejected."""
        with pytest.raises(ValueError, match="at least 32 characters"):
            TokenBridge(
                hs_secret="short",
                jwks_url=TEST_JWKS_URL,
                audience="client_test",
            )

    def test_default_audience_from_env(self, monkeypatch: Any) -> None:
        """Test audience defaults to WORKOS_CLIENT_ID."""
        monkeypatch.setenv("WORKOS_CLIENT_ID", "client_from_env")
        bridge = TokenBridge(
            hs_secret=TEST_SECRET,
            jwks_url=TEST_JWKS_URL,
        )
        assert bridge.audience == "client_from_env"


class TestCreateBridgeToken:
    """Test service token creation."""

    def test_creates_valid_hs256_token(self, token_bridge: Any) -> None:
        """Test creating a valid HS256 service token."""
        user_id = "user_123"
        org_id = "org_456"

        token = token_bridge.create_bridge_token(user_id, org_id)
        assert token
        assert isinstance(token, str)

        # Decode and verify
        decoded = jwt.decode(
            token,
            TEST_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True},
        )

        assert decoded["sub"] == user_id
        assert decoded["org_id"] == org_id
        assert decoded["type"] == "service"

    def test_token_expires_after_5_minutes(self, token_bridge: Any) -> None:
        """Test that service tokens have 5-minute TTL."""
        token = token_bridge.create_bridge_token("user_123", "org_456")

        decoded = jwt.decode(
            token,
            TEST_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True, "verify_exp": False},
        )

        # Check expiry is ~5 minutes from now
        exp = datetime.fromtimestamp(decoded["exp"], tz=UTC)
        now = datetime.now(UTC)
        expires_in = (exp - now).total_seconds()

        assert 290 < expires_in < 310  # 5 min ± 10 sec tolerance

    def test_custom_ttl(self, token_bridge: Any) -> None:
        """Test creating token with custom TTL."""
        token = token_bridge.create_bridge_token(
            "user_123",
            "org_456",
            ttl_minutes=10,
        )

        decoded = jwt.decode(
            token,
            TEST_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True, "verify_exp": False},
        )

        exp = datetime.fromtimestamp(decoded["exp"], tz=UTC)
        now = datetime.now(UTC)
        expires_in = (exp - now).total_seconds()

        assert 590 < expires_in < 610  # 10 min ± 10 sec


class TestValidateHS256Token:
    """Test HS256 service token validation."""

    def test_valid_service_token(self, token_bridge: Any) -> None:
        """Test validating a valid service token."""
        token = token_bridge.create_bridge_token("user_123", "org_456")

        claims = token_bridge._validate_hs256_token(token)
        assert claims["sub"] == "user_123"
        assert claims["org_id"] == "org_456"
        assert claims["type"] == "service"

    def test_wrong_secret(self, token_bridge: Any) -> None:
        """Test that wrong secret fails validation."""
        # Create token with different secret (test-only, not a real credential)
        wrong_secret = _TEST_WRONG_SECRET
        wrong_token = jwt.encode(
            {
                "sub": "user_123",
                "org_id": "org_456",
                "type": "service",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            wrong_secret,
            algorithm="HS256",
        )

        with pytest.raises(jwt.InvalidTokenError):
            token_bridge._validate_hs256_token(wrong_token)

    def test_expired_token(self, token_bridge: Any) -> None:
        """Test that expired tokens are rejected."""
        # Create expired token
        expired_token = jwt.encode(
            {
                "sub": "user_123",
                "org_id": "org_456",
                "type": "service",
                "exp": datetime.now(UTC) - timedelta(minutes=1),
                "iat": datetime.now(UTC) - timedelta(minutes=10),
            },
            TEST_SECRET,
            algorithm="HS256",
        )

        with pytest.raises(jwt.ExpiredSignatureError):
            token_bridge._validate_hs256_token(expired_token)

    def test_missing_type_claim_logs_warning(self, token_bridge: Any, caplog: Any) -> None:
        """Test that missing type=service logs a warning."""
        # Create token without type claim
        token = jwt.encode(
            {
                "sub": "user_123",
                "org_id": "org_456",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            TEST_SECRET,
            algorithm="HS256",
        )

        claims = token_bridge._validate_hs256_token(token)
        assert claims["sub"] == "user_123"
        # Check warning was logged
        assert "missing type=service" in caplog.text


class TestValidateToken:
    """Test unified token validation (RS256 or HS256)."""

    def test_validates_hs256_service_token(self, token_bridge: Any) -> None:
        """Test that ValidateToken accepts HS256 tokens."""
        token = token_bridge.create_bridge_token("user_123", "org_456")

        # Should try RS256, fail, then succeed with HS256
        claims = token_bridge.validate_token(token)
        assert claims["sub"] == "user_123"
        assert claims["org_id"] == "org_456"
        assert claims["type"] == "service"

    def test_rejects_invalid_token(self, token_bridge: Any) -> None:
        """Test that invalid tokens are rejected."""
        with pytest.raises(jwt.InvalidTokenError, match="validation failed"):
            token_bridge.validate_token("invalid.token.here")

    def test_rejects_empty_token(self, token_bridge: Any) -> None:
        """Test that empty tokens are rejected."""
        with pytest.raises(jwt.InvalidTokenError):
            token_bridge.validate_token("")

    def test_rejects_malformed_token(self, token_bridge: Any) -> None:
        """Test that malformed tokens are rejected."""
        with pytest.raises(jwt.InvalidTokenError):
            token_bridge.validate_token("not-a-jwt")


class TestGetTokenBridge:
    """Test token bridge factory function."""

    def test_creates_bridge_from_env(self, monkeypatch: Any) -> None:
        """Test creating bridge from environment variables."""
        monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
        monkeypatch.setenv("WORKOS_JWKS_URL", TEST_JWKS_URL)
        monkeypatch.setenv("WORKOS_CLIENT_ID", "client_test")
        monkeypatch.setenv("WORKOS_JWT_ISSUER", "https://api.workos.com/")

        bridge = get_token_bridge()
        assert bridge.hs_secret == TEST_SECRET
        assert bridge.jwks_url == TEST_JWKS_URL
        assert bridge.audience == "client_test"
        assert bridge.issuer == "https://api.workos.com/"

    def test_constructs_default_jwks_url(self, monkeypatch: Any) -> None:
        """Test that JWKS URL is constructed from client ID if not provided."""
        monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
        monkeypatch.setenv("WORKOS_CLIENT_ID", "client_abc123")
        monkeypatch.delenv("WORKOS_JWKS_URL", raising=False)

        bridge = get_token_bridge()
        assert bridge.jwks_url == "https://api.workos.com/sso/jwks/client_abc123"

    def test_custom_api_base_url(self, monkeypatch: Any) -> None:
        """Test using custom WorkOS API base URL."""
        monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
        monkeypatch.setenv("WORKOS_CLIENT_ID", "client_abc123")
        monkeypatch.setenv("WORKOS_API_BASE_URL", "https://custom.workos.com")
        monkeypatch.delenv("WORKOS_JWKS_URL", raising=False)

        bridge = get_token_bridge()
        assert bridge.jwks_url == "https://custom.workos.com/sso/jwks/client_abc123"

    def test_missing_jwt_secret_raises_error(self, monkeypatch: Any) -> None:
        """Test that missing JWT_SECRET raises error."""
        monkeypatch.delenv("JWT_SECRET", raising=False)
        monkeypatch.setenv("WORKOS_JWKS_URL", TEST_JWKS_URL)

        with pytest.raises(ValueError, match="JWT_SECRET"):
            get_token_bridge()

    def test_missing_jwks_url_and_client_id_raises_error(self, monkeypatch: Any) -> None:
        """Test that missing both JWKS_URL and CLIENT_ID raises error."""
        monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
        monkeypatch.delenv("WORKOS_JWKS_URL", raising=False)
        monkeypatch.delenv("WORKOS_CLIENT_ID", raising=False)

        with pytest.raises(ValueError, match="WORKOS_JWKS_URL or WORKOS_CLIENT_ID"):
            get_token_bridge()


class TestRefreshJWKS:
    """Test JWKS refresh functionality."""

    def test_refresh_jwks_creates_new_client(self, token_bridge: Any) -> None:
        """Test that refresh_jwks creates a new PyJWKClient."""
        old_client = token_bridge.jwks_client
        token_bridge.refresh_jwks()
        new_client = token_bridge.jwks_client

        # Should be a different instance
        assert old_client is not new_client
        assert isinstance(new_client, PyJWKClient)


class TestTokenBridgeIntegration:
    """Integration tests for token bridge."""

    def test_roundtrip_service_token(self, token_bridge: Any) -> None:
        """Test creating and validating a service token."""
        # Create token
        token = token_bridge.create_bridge_token("user_789", "org_xyz")

        # Validate token
        claims = token_bridge.validate_token(token)

        # Verify claims
        assert claims["sub"] == "user_789"
        assert claims["org_id"] == "org_xyz"
        assert claims["type"] == "service"

    def test_token_lifecycle(self, token_bridge: Any) -> None:
        """Test complete token lifecycle."""
        # 1. Create token
        token = token_bridge.create_bridge_token("user_123", "org_456")
        assert token

        # 2. Validate immediately (should work)
        claims = token_bridge.validate_token(token)
        assert claims["sub"] == "user_123"

        # 3. Wait for expiry (simulate by creating expired token)
        expired_token = jwt.encode(
            {
                "sub": "user_123",
                "org_id": "org_456",
                "type": "service",
                "exp": datetime.now(UTC) - timedelta(seconds=1),
            },
            TEST_SECRET,
            algorithm="HS256",
        )

        # 4. Validate expired token (should fail)
        with pytest.raises(jwt.InvalidTokenError):
            token_bridge.validate_token(expired_token)
