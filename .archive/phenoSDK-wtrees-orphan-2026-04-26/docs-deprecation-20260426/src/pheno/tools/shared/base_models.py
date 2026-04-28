"""Shared base models for tools (requests and common field descriptions).

These models are intentionally minimal and SDK-agnostic so that both pheno-sdk tools and
downstream servers (e.g., Zen MCP) can reuse them.
"""

from __future__ import annotations

try:  # Keep pydantic optional at import time
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - fallback stub if pydantic missing

    class BaseModel:  # type: ignore
        pass

    def Field(*_args, **_kwargs):  # type: ignore
        return None


class ToolRequest(BaseModel):
    """Canonical simple tool request model.

    Tools can subclass this to add extra fields. This mirrors the example
    structure (prompt/files/images/model/temperature/thinking_mode/continuation_id)
    and is compatible with Pydantic v2 style usage.
    """

    prompt: str = Field(..., description="The user's question or request")
    model: str | None = Field(None, description="Model to use (optional in auto-mode)")
    temperature: float | None = Field(
        None, description="Sampling temperature (0-2)", ge=0.0, le=2.0,
    )
    thinking_mode: str | None = Field(None, description="Thinking mode for extended reasoning")
    files: list[str] | None = Field(
        default_factory=list, description="Absolute file paths to include",
    )
    images: list[str] | None = Field(
        default_factory=list, description="Image paths or data URLs to include",
    )
    continuation_id: str | None = Field(
        None, description="Continuation thread id for follow-up turns",
    )


# Common JSON schema snippets (used by SchemaBuilder and tools)
SIMPLE_FIELD_SCHEMAS: dict[str, dict] = {
    "files": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Absolute file paths to process",
    },
}

COMMON_FIELD_SCHEMAS: dict[str, dict] = {
    "images": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Images (paths or data URLs)",
    },
    "model": {"type": "string", "description": "Model name or alias"},
    "temperature": {
        "type": "number",
        "minimum": 0,
        "maximum": 2,
        "description": "Sampling temperature (0-2)",
    },
    "thinking_mode": {"type": "string", "description": "Thinking mode"},
    "continuation_id": {"type": "string", "description": "Continuation thread id"},
}

__all__ = [
    "COMMON_FIELD_SCHEMAS",
    "SIMPLE_FIELD_SCHEMAS",
    "ToolRequest",
]
