"""
Validation helpers for tool responses and individual fields.
"""

import re
from datetime import datetime
from typing import Any


class ResponseValidator:
    """
    Validate MCP tool responses and extract common fields.
    """

    @staticmethod
    def has_fields(response: dict[str, Any], required_fields: list[str]) -> bool:
        """
        Check if the response has all required fields.
        """
        if not isinstance(response, dict):
            return False
        return all(field in response for field in required_fields)

    @staticmethod
    def has_any_fields(response: dict[str, Any], fields: list[str]) -> bool:
        """
        Check if the response has any of the specified fields.
        """
        if not isinstance(response, dict):
            return False
        return any(field in response for field in fields)

    @staticmethod
    def validate_pagination(response: dict[str, Any]) -> bool:
        """
        Validate pagination structure.
        """
        required = ["total", "limit", "offset"]
        return ResponseValidator.has_fields(response, required)

    @staticmethod
    def validate_list_response(
        response: dict[str, Any],
        data_key: str = "data",
    ) -> bool:
        """
        Validate list response structure.
        """
        if not isinstance(response, dict):
            return False
        if data_key not in response:
            return False
        return isinstance(response[data_key], list)

    @staticmethod
    def validate_success_response(result: dict[str, Any]) -> bool:
        """
        Validate standard success response.
        """
        return result.get("success", False) and result.get("error") is None

    @staticmethod
    def extract_id(response: dict[str, Any]) -> str | None:
        """
        Extract an identifier field from common response shapes.
        """
        if not isinstance(response, dict):
            return None
        if "id" in response:
            return response["id"]
        if "data" in response and isinstance(response["data"], dict):
            return response["data"].get("id")
        return None


class FieldValidator:
    """
    Validate common field types and formats.
    """

    @staticmethod
    def is_uuid(value: Any) -> bool:
        """
        Check if value is a valid UUID string.
        """
        if not isinstance(value, str):
            return False
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(uuid_pattern, value, re.IGNORECASE))

    @staticmethod
    def is_iso_timestamp(value: Any) -> bool:
        """
        Check if value is an ISO 8601 timestamp.
        """
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def is_in_range(
        value: Any,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> bool:
        """
        Check if value is within a numeric range.
        """
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False
            return not (max_val is not None and num > max_val)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_slug(
        value: Any,
        pattern: str = r"^[a-z][a-z0-9-]*$",
    ) -> bool:
        """
        Check if value matches a slug pattern.
        """
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))


__all__ = ["FieldValidator", "ResponseValidator"]
