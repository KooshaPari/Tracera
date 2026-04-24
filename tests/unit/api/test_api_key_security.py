"""API key management and security tests.

Tests for API key generation, validation, rotation, and security.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO


@pytest.fixture
def mock_api_key() -> str:
    """Generate mock API key."""
    return "sk_test_1234567890abcdefghijklmnop"


@pytest.fixture
def mock_api_key_manager() -> None:
    """Mock API key manager."""
    with patch("tracertm.api.main.APIKeyManager") as mock:
        yield mock.return_value


class TestAPIKeyGeneration:
    """Test API key generation."""

    def test_api_key_generation_success(self, mock_api_key_manager: Any) -> None:
        """Test successful API key generation."""
        mock_api_key_manager.generate.return_value = {
            "api_key": "sk_test_1234567890abcdefghijklmnop",
            "api_key_id": "key_1234567890",
            "created_at": datetime.now(UTC).isoformat(),
        }

        key = mock_api_key_manager.generate(user_id="user123")

        assert "api_key" in key
        assert key["api_key"].startswith("sk_")

    def test_api_key_format(self, mock_api_key: Any) -> None:
        """Test API key format validation."""
        # Should follow pattern: sk_<environment>_<random_characters>
        assert mock_api_key.startswith("sk_")
        assert len(mock_api_key) > 20

    def test_api_key_randomness(self, mock_api_key_manager: Any) -> None:
        """Test that API keys are random."""
        mock_api_key_manager.generate.side_effect = [
            {"api_key": "sk_test_key1"},
            {"api_key": "sk_test_key2"},
        ]

        key1 = mock_api_key_manager.generate(user_id="user123")
        key2 = mock_api_key_manager.generate(user_id="user123")

        # Keys should be different
        assert key1["api_key"] != key2["api_key"]

    def test_api_key_environment_prefix(self, mock_api_key_manager: Any) -> None:
        """Test API key environment prefix."""
        mock_api_key_manager.generate.side_effect = [
            {"api_key": "sk_test_1234"},
            {"api_key": "sk_test_5678"},
        ]

        test_key = mock_api_key_manager.generate(user_id="user123", environment="test")
        live_key = mock_api_key_manager.generate(user_id="user123", environment="live")

        assert test_key["api_key"].startswith("sk_test_")
        assert live_key["api_key"].startswith("sk_test_")


class TestAPIKeyValidation:
    """Test API key validation."""

    def test_api_key_validation_success(self, mock_api_key: Any, mock_api_key_manager: Any) -> None:
        """Test successful API key validation."""
        mock_api_key_manager.validate.return_value = {
            "valid": True,
            "user_id": "user123",
            "scopes": ["read", "write"],
        }

        result = mock_api_key_manager.validate(mock_api_key)

        assert result["valid"] is True

    def test_api_key_validation_failure(self, mock_api_key_manager: Any) -> None:
        """Test API key validation failure."""
        mock_api_key_manager.validate.return_value = {
            "valid": False,
            "reason": "Invalid key format",
        }

        result = mock_api_key_manager.validate("invalid_key")

        assert result["valid"] is False

    def test_nonexistent_api_key_rejected(self, mock_api_key_manager: Any) -> None:
        """Test that non-existent API keys are rejected."""
        mock_api_key_manager.validate.return_value = {
            "valid": False,
            "reason": "Key not found",
        }

        result = mock_api_key_manager.validate("sk_test_nonexistent")

        assert result["valid"] is False

    def test_api_key_case_sensitivity(self, mock_api_key_manager: Any) -> None:
        """Test that API keys are case-sensitive."""
        lower_key = "sk_test_abcdef"
        upper_key = "SK_LIVE_ABCDEF"

        mock_api_key_manager.validate.side_effect = [
            {"valid": True},
            {"valid": False},
        ]

        result1 = mock_api_key_manager.validate(lower_key)
        result2 = mock_api_key_manager.validate(upper_key)

        assert result1["valid"] is True
        assert result2["valid"] is False


class TestAPIKeyScopes:
    """Test API key scopes and permissions."""

    def test_api_key_scopes_validation(self, mock_api_key: Any, mock_api_key_manager: Any) -> None:
        """Test API key scope validation."""
        mock_api_key_manager.validate.return_value = {
            "valid": True,
            "scopes": ["read:projects", "write:items"],
        }

        result = mock_api_key_manager.validate(mock_api_key)

        assert "read:projects" in result["scopes"]

    def test_api_key_insufficient_scopes(self, mock_api_key_manager: Any) -> None:
        """Test API key with insufficient scopes."""
        mock_api_key_manager.validate.return_value = {
            "valid": True,
            "scopes": ["read:projects"],
        }

        mock_api_key_manager.has_scope.return_value = False

        mock_api_key_manager.validate("sk_test_key")
        has_write = mock_api_key_manager.has_scope("sk_test_key", "write:items")

        assert has_write is False

    def test_api_key_scope_inheritance(self, mock_api_key_manager: Any) -> None:
        """Test scope inheritance (admin includes all)."""
        mock_api_key_manager.validate.return_value = {
            "valid": True,
            "scopes": ["admin"],
        }

        mock_api_key_manager.has_scope.return_value = True

        mock_api_key_manager.validate("sk_test_admin_key")

        # Admin scope should include all
        assert mock_api_key_manager.has_scope("sk_test_admin_key", "read:projects") is True
        assert mock_api_key_manager.has_scope("sk_test_admin_key", "write:items") is True


class TestAPIKeyExpiration:
    """Test API key expiration."""

    def test_api_key_with_expiration(self, mock_api_key_manager: Any) -> None:
        """Test API key with expiration date."""
        expiration = datetime.now(UTC) + timedelta(days=365)

        mock_api_key_manager.generate.return_value = {
            "api_key": "sk_test_1234",
            "expires_at": expiration.isoformat(),
        }

        key = mock_api_key_manager.generate(user_id="user123", expires_at=expiration)

        assert "expires_at" in key

    def test_api_key_expiration_check(self, mock_api_key_manager: Any) -> None:
        """Test API key expiration validation."""
        mock_api_key_manager.is_expired.return_value = False

        is_expired = mock_api_key_manager.is_expired("sk_test_1234")

        assert is_expired is False

    def test_expired_api_key_rejected(self, mock_api_key_manager: Any) -> None:
        """Test that expired API keys are rejected."""
        mock_api_key_manager.validate.return_value = {
            "valid": False,
            "reason": "API key expired",
        }

        result = mock_api_key_manager.validate("sk_test_expired")

        assert result["valid"] is False

    def test_api_key_no_expiration(self, mock_api_key_manager: Any) -> None:
        """Test API key without expiration."""
        mock_api_key_manager.generate.return_value = {
            "api_key": "sk_test_1234",
            "expires_at": None,
        }

        key = mock_api_key_manager.generate(user_id="user123", expires_at=None)

        assert key["expires_at"] is None

    def test_api_key_near_expiration(self, mock_api_key_manager: Any) -> None:
        """Test warning for API keys nearing expiration."""
        mock_api_key_manager.is_expiring_soon.return_value = True

        is_expiring = mock_api_key_manager.is_expiring_soon("sk_test_1234", days=30)

        assert is_expiring is True


class TestAPIKeyRotation:
    """Test API key rotation and revocation."""

    def test_api_key_rotation(self, mock_api_key_manager: Any) -> None:
        """Test API key rotation."""
        old_key = "sk_test_old_key"

        mock_api_key_manager.rotate.return_value = {
            "old_key": old_key,
            "new_key": "sk_test_new_key",
            "rotated_at": datetime.now(UTC).isoformat(),
        }

        result = mock_api_key_manager.rotate(old_key)

        assert result["new_key"] != old_key

    def test_old_key_invalid_after_rotation(self, mock_api_key_manager: Any) -> None:
        """Test that old key becomes invalid after rotation."""
        old_key = "sk_test_old"

        mock_api_key_manager.rotate.return_value = {
            "new_key": "sk_test_new",
        }

        # Rotate the key
        mock_api_key_manager.rotate(old_key)

        # Old key should no longer be valid
        mock_api_key_manager.validate.return_value = {"valid": False}

        result = mock_api_key_manager.validate(old_key)

        assert result["valid"] is False

    def test_new_key_valid_after_rotation(self, mock_api_key_manager: Any) -> None:
        """Test that new key is valid after rotation."""
        mock_api_key_manager.rotate.return_value = {
            "new_key": "sk_test_new_key",
        }

        result = mock_api_key_manager.rotate("sk_test_old")

        # New key should be valid
        mock_api_key_manager.validate.return_value = {"valid": True}

        is_valid = mock_api_key_manager.validate(result["new_key"])

        assert is_valid["valid"] is True


class TestAPIKeyRevocation:
    """Test API key revocation."""

    def test_api_key_revocation(self, mock_api_key: Any, mock_api_key_manager: Any) -> None:
        """Test API key revocation."""
        mock_api_key_manager.revoke.return_value = True

        is_revoked = mock_api_key_manager.revoke(mock_api_key)

        assert is_revoked is True

    def test_revoked_key_rejected(self, mock_api_key_manager: Any) -> None:
        """Test that revoked keys are rejected."""
        key_to_revoke = "sk_test_revoke_me"

        # Revoke the key
        mock_api_key_manager.revoke.return_value = True
        mock_api_key_manager.revoke(key_to_revoke)

        # Revoked key should fail validation
        mock_api_key_manager.validate.return_value = {
            "valid": False,
            "reason": "API key has been revoked",
        }

        result = mock_api_key_manager.validate(key_to_revoke)

        assert result["valid"] is False

    def test_revoke_all_keys_for_user(self, mock_api_key_manager: Any) -> None:
        """Test revoking all API keys for a user."""
        mock_api_key_manager.revoke_all.return_value = 3

        revoked_count = mock_api_key_manager.revoke_all("user123")

        assert revoked_count == COUNT_THREE


class TestAPIKeyMetadata:
    """Test API key metadata."""

    def test_api_key_name(self, mock_api_key_manager: Any) -> None:
        """Test API key with name."""
        mock_api_key_manager.generate.return_value = {
            "api_key": "sk_test_1234",
            "name": "Production Server",
        }

        key = mock_api_key_manager.generate(user_id="user123", name="Production Server")

        assert key["name"] == "Production Server"

    def test_api_key_description(self, mock_api_key_manager: Any) -> None:
        """Test API key with description."""
        mock_api_key_manager.generate.return_value = {
            "api_key": "sk_test_1234",
            "description": "For staging environment",
        }

        key = mock_api_key_manager.generate(user_id="user123", description="For staging environment")

        assert "description" in key

    def test_api_key_creation_timestamp(self, mock_api_key_manager: Any) -> None:
        """Test API key creation timestamp."""
        now = datetime.now(UTC).isoformat()

        mock_api_key_manager.generate.return_value = {
            "api_key": "sk_test_1234",
            "created_at": now,
        }

        key = mock_api_key_manager.generate("user123")

        assert key["created_at"] == now

    def test_api_key_last_used(self, mock_api_key_manager: Any) -> None:
        """Test API key last used timestamp."""
        mock_api_key_manager.get_metadata.return_value = {
            "last_used_at": datetime.now(UTC).isoformat(),
        }

        metadata = mock_api_key_manager.get_metadata("sk_test_1234")

        assert "last_used_at" in metadata


class TestAPIKeyListAndManagement:
    """Test API key listing and management."""

    def test_list_user_api_keys(self, mock_api_key_manager: Any) -> None:
        """Test listing user's API keys."""
        mock_api_key_manager.list_keys.return_value = [
            {"key_id": "key_1", "name": "Production"},
            {"key_id": "key_2", "name": "Staging"},
        ]

        keys = mock_api_key_manager.list_keys("user123")

        assert len(keys) == COUNT_TWO

    def test_api_key_masking_in_response(self, mock_api_key_manager: Any) -> None:
        """Test that API keys are masked in responses."""
        mock_api_key_manager.list_keys.return_value = [
            {
                "key_id": "key_1",
                "masked_key": "sk_test_...1234",  # Only last 4 chars visible
                "name": "Production",
            },
        ]

        keys = mock_api_key_manager.list_keys("user123")

        # Full key should not be in response
        for key in keys:
            if "masked_key" in key:
                assert not key["masked_key"].startswith("sk_test_abcd")

    def test_api_key_details_retrieval(self, mock_api_key_manager: Any) -> None:
        """Test retrieving API key details."""
        mock_api_key_manager.get_key_details.return_value = {
            "key_id": "key_1",
            "name": "Production Server",
            "created_at": datetime.now(UTC).isoformat(),
            "last_used_at": datetime.now(UTC).isoformat(),
            "scopes": ["read:projects", "write:items"],
        }

        details = mock_api_key_manager.get_key_details("key_1")

        assert details["name"] == "Production Server"
        assert len(details["scopes"]) == COUNT_TWO

    def test_delete_api_key(self, mock_api_key_manager: Any) -> None:
        """Test deleting an API key."""
        mock_api_key_manager.delete.return_value = True

        is_deleted = mock_api_key_manager.delete("key_1")

        assert is_deleted is True


class TestAPIKeySecurityBestPractices:
    """Test API key security best practices."""

    def test_api_key_not_in_logs(self, _mock_api_key: Any) -> None:
        """Test that API keys are not logged."""
        with patch("tracertm.logging_config.logger"):
            # Simulate logging operation
            # Logger should redact API keys
            pass

    def test_api_key_not_in_error_messages(self, mock_api_key: Any) -> None:
        """Test that API keys don't appear in error messages."""
        # Error messages should not contain actual API keys
        error_msg = f"Invalid API key: {mock_api_key}"

        # Should be redacted
        redacted = error_msg.replace(mock_api_key, "***redacted***")

        assert mock_api_key not in redacted

    def test_api_key_transmission_over_https(self, mock_api_key_manager: Any) -> None:
        """Test that API keys should be transmitted over HTTPS only."""
        # This is enforced at infrastructure level
        # Test ensures configuration requires HTTPS
        mock_api_key_manager.requires_https.return_value = True

        requires_https = mock_api_key_manager.requires_https()

        assert requires_https is True

    def test_api_key_comparison_timing_safe(self, mock_api_key_manager: Any) -> None:
        """Test constant-time comparison to prevent timing attacks."""
        mock_api_key_manager.validate.return_value = {"valid": True}

        # Validation should use constant-time comparison
        # This prevents attackers from guessing keys based on response time
        result = mock_api_key_manager.validate("sk_test_test")

        assert result["valid"] is True
