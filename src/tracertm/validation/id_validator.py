"""UUID validation and normalization utilities."""

import re
import uuid

UUID_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def validate_uuid(id_str: str) -> None:
    """Validate UUID format, raise ValueError if invalid.

    Args:
        id_str: String to validate as UUID

    Raises:
        ValueError: If id_str is not a valid UUID format
    """
    normalized = normalize_uuid(id_str)
    if not UUID_REGEX.match(normalized):
        msg = f"Invalid UUID format: {id_str}"
        raise ValueError(msg)


def normalize_uuid(id_str: str) -> str:
    """Normalize UUID to lowercase and trimmed.

    Args:
        id_str: UUID string to normalize

    Returns:
        Normalized UUID string (lowercase, trimmed)
    """
    return id_str.strip().lower()


def generate_uuid() -> str:
    """Generate new UUID as string.

    Returns:
        New UUID v4 as string
    """
    return str(uuid.uuid4())


def is_valid_uuid(id_str: str) -> bool:
    """Check if string is a valid UUID.

    Args:
        id_str: String to validate

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        validate_uuid(id_str)
    except ValueError:
        return False
    else:
        return True


def validate_uuids(id_strs: list[str]) -> None:
    """Validate multiple UUIDs, raise ValueError on first invalid.

    Args:
        id_strs: List of UUID strings to validate

    Raises:
        ValueError: If any UUID is invalid
    """
    for id_str in id_strs:
        validate_uuid(id_str)
