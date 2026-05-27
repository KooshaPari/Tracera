"""Compatibility exports for chat handlers."""

from typing import Any

from fastapi import Request


async def simple_chat(
    request: Request,
    message: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Simple chat handler for compatibility."""
    return {
        "response": f"Echo: {message}",
        "context": context or {},
    }


async def stream_chat(
    request: Request,
    message: str,
    context: dict[str, Any] | None = None,
):
    """Stream chat handler for compatibility."""
    yield f"Echo: {message}"
