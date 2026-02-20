"""Tests for UUID validation utilities."""

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR
from tracertm.validation.id_validator import (
    generate_uuid,
    is_valid_uuid,
    normalize_uuid,
    validate_uuid,
    validate_uuids,
)


class TestValidateUUID:
    """Tests for validate_uuid function."""

    def test_valid_lowercase_uuid(self) -> None:
        """Should accept valid lowercase UUID."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        validate_uuid(valid_uuid)  # Should not raise

    def test_valid_uppercase_uuid(self) -> None:
        """Should accept valid uppercase UUID."""
        valid_uuid = "123E4567-E89B-12D3-A456-426614174000"
        validate_uuid(valid_uuid)  # Should not raise

    def test_valid_uuid_with_spaces(self) -> None:
        """Should accept UUID with surrounding spaces."""
        valid_uuid = "  123e4567-e89b-12d3-a456-426614174000  "
        validate_uuid(valid_uuid)  # Should not raise

    def test_invalid_uuid_too_short(self) -> None:
        """Should reject UUID that is too short."""
        invalid_uuid = "123e4567-e89b-12d3-a456-42661417400"
        with pytest.raises(ValueError, match="Invalid UUID format"):
            validate_uuid(invalid_uuid)

    def test_invalid_uuid_missing_dashes(self) -> None:
        """Should reject UUID without dashes."""
        invalid_uuid = "123e4567e89b12d3a456426614174000"
        with pytest.raises(ValueError, match="Invalid UUID format"):
            validate_uuid(invalid_uuid)

    def test_invalid_uuid_invalid_characters(self) -> None:
        """Should reject UUID with invalid characters."""
        invalid_uuid = "123g4567-e89b-12d3-a456-426614174000"
        with pytest.raises(ValueError, match="Invalid UUID format"):
            validate_uuid(invalid_uuid)

    def test_empty_string(self) -> None:
        """Should reject empty string."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            validate_uuid("")

    def test_none_raises_error(self) -> None:
        """Should raise appropriate error for None."""
        with pytest.raises(AttributeError):
            validate_uuid(None)


class TestNormalizeUUID:
    """Tests for normalize_uuid function."""

    def test_uppercase_to_lowercase(self) -> None:
        """Should convert uppercase UUID to lowercase."""
        uuid_str = "123E4567-E89B-12D3-A456-426614174000"
        expected = "123e4567-e89b-12d3-a456-426614174000"
        assert normalize_uuid(uuid_str) == expected

    def test_trim_spaces(self) -> None:
        """Should trim surrounding spaces."""
        uuid_str = "  123e4567-e89b-12d3-a456-426614174000  "
        expected = "123e4567-e89b-12d3-a456-426614174000"
        assert normalize_uuid(uuid_str) == expected

    def test_already_normalized(self) -> None:
        """Should return same string if already normalized."""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        assert normalize_uuid(uuid_str) == uuid_str

    def test_mixed_case(self) -> None:
        """Should normalize mixed case UUID."""
        uuid_str = "123e4567-E89B-12d3-A456-426614174000"
        expected = "123e4567-e89b-12d3-a456-426614174000"
        assert normalize_uuid(uuid_str) == expected


class TestGenerateUUID:
    """Tests for generate_uuid function."""

    def test_generates_valid_uuid(self) -> None:
        """Should generate a valid UUID string."""
        generated = generate_uuid()
        # Should not raise
        validate_uuid(generated)

    def test_generates_unique_uuids(self) -> None:
        """Should generate unique UUIDs."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2

    def test_generates_lowercase(self) -> None:
        """Generated UUIDs should be lowercase."""
        generated = generate_uuid()
        assert generated == generated.lower()

    def test_generates_proper_format(self) -> None:
        """Should generate UUID in proper format."""
        generated = generate_uuid()
        parts = generated.split("-")
        assert len(parts) == COUNT_FIVE
        assert len(parts[0]) == 8
        assert len(parts[1]) == COUNT_FOUR
        assert len(parts[2]) == COUNT_FOUR
        assert len(parts[3]) == COUNT_FOUR
        assert len(parts[4]) == 12


class TestIsValidUUID:
    """Tests for is_valid_uuid function."""

    def test_valid_uuid_returns_true(self) -> None:
        """Should return True for valid UUID."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        assert is_valid_uuid(valid_uuid) is True

    def test_invalid_uuid_returns_false(self) -> None:
        """Should return False for invalid UUID."""
        invalid_uuid = "invalid"
        assert is_valid_uuid(invalid_uuid) is False

    def test_empty_string_returns_false(self) -> None:
        """Should return False for empty string."""
        assert is_valid_uuid("") is False

    def test_uppercase_uuid_returns_true(self) -> None:
        """Should return True for uppercase UUID."""
        valid_uuid = "123E4567-E89B-12D3-A456-426614174000"
        assert is_valid_uuid(valid_uuid) is True

    def test_uuid_with_spaces_returns_true(self) -> None:
        """Should return True for UUID with spaces."""
        valid_uuid = "  123e4567-e89b-12d3-a456-426614174000  "
        assert is_valid_uuid(valid_uuid) is True


class TestValidateUUIDs:
    """Tests for validate_uuids function."""

    def test_all_valid_uuids(self) -> None:
        """Should not raise for all valid UUIDs."""
        uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "223e4567-e89b-12d3-a456-426614174000",
            "323e4567-e89b-12d3-a456-426614174000",
        ]
        validate_uuids(uuids)  # Should not raise

    def test_one_invalid_uuid(self) -> None:
        """Should raise on first invalid UUID."""
        uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "invalid",
            "323e4567-e89b-12d3-a456-426614174000",
        ]
        with pytest.raises(ValueError, match="Invalid UUID format"):
            validate_uuids(uuids)

    def test_empty_list(self) -> None:
        """Should handle empty list."""
        validate_uuids([])  # Should not raise

    def test_single_valid_uuid(self) -> None:
        """Should handle single valid UUID."""
        uuids = ["123e4567-e89b-12d3-a456-426614174000"]
        validate_uuids(uuids)  # Should not raise

    def test_mixed_case_valid_uuids(self) -> None:
        """Should accept mixed case UUIDs."""
        uuids = [
            "123E4567-e89b-12d3-a456-426614174000",
            "223e4567-E89B-12d3-a456-426614174000",
        ]
        validate_uuids(uuids)  # Should not raise
