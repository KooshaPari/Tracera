"""Schema builder utilities for Simple tools.

This mirrors the convenience provided in the example server:
- Provide reusable field schemas for common inputs
- Merge tool-specific fields with common fields
- Handle model field presence and "auto mode" defaults
"""

from __future__ import annotations

from typing import Any

from .base_models import COMMON_FIELD_SCHEMAS, SIMPLE_FIELD_SCHEMAS


class SchemaBuilder:
    """
    Utility to build input JSON schemas consistently across tools.
    """

    SIMPLE_FIELD_SCHEMAS = SIMPLE_FIELD_SCHEMAS
    COMMON_FIELD_SCHEMAS = COMMON_FIELD_SCHEMAS

    @staticmethod
    def default_model_field_schema() -> dict:
        return COMMON_FIELD_SCHEMAS["model"]

    @staticmethod
    def build_schema(
        *,
        tool_specific_fields: dict[str, dict[str, Any]] | None = None,
        required_fields: list[str] | None = None,
        model_field_schema: dict | None = None,
        auto_mode: bool = False,
        include_common_defaults: bool = True,
    ) -> dict:
        """Build a full JSON schema for a tool.

        Args:
            tool_specific_fields: Fields unique to the tool
            required_fields: Names that must be present in input
            model_field_schema: Custom model field schema (defaults to common)
            auto_mode: When True, include a model field but do not require it
            include_common_defaults: Whether to include temperature/thinking_mode/images/continuation_id
        """
        tool_specific_fields = tool_specific_fields or {}
        required_fields = list(required_fields or [])

        properties: dict[str, Any] = {}

        # Tool specific first so callers can override common defaults if desired
        properties.update(tool_specific_fields)

        # Add common defaults (temperature, thinking_mode, images, continuation)
        if include_common_defaults:
            for key in ("temperature", "thinking_mode", "images", "continuation_id"):
                if key not in properties:
                    properties[key] = COMMON_FIELD_SCHEMAS[key]

        # Always offer files helper (tools can override via tool_specific_fields)
        if "files" not in properties:
            properties["files"] = SIMPLE_FIELD_SCHEMAS["files"]

        # Model field handling
        if auto_mode:
            # Auto mode: include model optionally (not required)
            properties["model"] = model_field_schema or SchemaBuilder.default_model_field_schema()
        # Non auto-mode: include when explicitly provided by caller
        elif model_field_schema:
            properties["model"] = model_field_schema

        # Ensure "prompt" is a reasonable default if tool didn't provide one
        if "prompt" not in properties:
            properties["prompt"] = {
                "type": "string",
                "description": "User prompt or request",
            }

        # Add prompt to requireds unless caller decided otherwise
        if "prompt" not in required_fields:
            required_fields = ["prompt", *required_fields]

        return {
            "type": "object",
            "properties": properties,
            "required": required_fields,
            "additionalProperties": False,
        }


__all__ = ["SchemaBuilder"]
