"""
Helpers for running FastMCP/ASGI apps on serverless platforms.
"""

from __future__ import annotations

from typing import Any

from starlette.middleware.gzip import GZipMiddleware

_PATCHED = False


def _patch_streamable_manager() -> None:
    global _PATCHED
    if _PATCHED:
        return

    import anyio
    from mcp.server.streamable_http_manager import (
        StreamableHTTPSessionManager,  # type: ignore
    )

    original_handle_request = StreamableHTTPSessionManager.handle_request

    async def patched_handle_request(self, scope, receive, send):
        if self._task_group is None:
            async with anyio.create_task_group() as task_group:
                self._task_group = task_group
                try:
                    await original_handle_request(self, scope, receive, send)
                finally:
                    self._task_group = None
        else:
            await original_handle_request(self, scope, receive, send)

    StreamableHTTPSessionManager.handle_request = patched_handle_request
    _PATCHED = True


def make_serverless_http_app(fastmcp_app: Any, *, path: str = "/api/mcp", enable_gzip: bool = True):
    """
    Return an ASGI application configured for serverless environments.
    """
    _patch_streamable_manager()
    http_app = fastmcp_app.http_app(path=path, stateless_http=True)
    if enable_gzip:
        return GZipMiddleware(http_app, minimum_size=500)
    return http_app


__all__ = ["make_serverless_http_app"]
