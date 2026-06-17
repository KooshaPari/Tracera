"""Compatibility exports for chat handlers."""
from typing import Any, Dict, Optional
from fastapi import Request


async def simple_chat(
    request: Request,
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Simple chat handler for compatibility."""
    return {
        "response": f"Echo: {message}",
        "context": context or {},
    }


async def stream_chat(
    request: Request,
    message: str,
    context: Optional[Dict[str, Any]] = None,
):
    """Stream chat handler for compatibility."""
    yield f"Echo: {message}"
