"""Request-ID middleware for FastAPI.

Reads ``X-Request-Id`` from the inbound request (or generates a UUID4),
stores it in a module-level :class:`contextvars.ContextVar`, and echoes the
value on the response.  This replaces the removed ``phenotype-request-id``
PyPI dependency (which was a project-private package unavailable on PyPI).

Implemented as a pure-ASGI middleware to avoid the known limitations of
``starlette.middleware.base.BaseHTTPMiddleware`` (in particular, the
disruption of ``contextvars`` propagation when ``BaseHTTPMiddleware`` is
sits in front of downstream middleware).  This pattern is the
recommendation from the Starlette docs (see
https://www.starlette.io/middleware/#pure-asgi-middleware).
"""
from __future__ import annotations

import uuid
from contextvars import ContextVar

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

#: Holds the current request-ID for the active request context.
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

HEADER_NAME = "X-Request-ID"


class RequestIdMiddleware:
    """Attach a unique request-ID to every request and response.

    Parameters
    ----------
    app:
        The ASGI application to wrap.
    header_name:
        The HTTP header used to read/write the request-ID.
        Defaults to ``X-Request-ID``.
    """

    def __init__(self, app: ASGIApp, header_name: str = HEADER_NAME) -> None:
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract or generate the request ID before entering the context.
        request = Request(scope, receive=receive)
        req_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        token = request_id_var.set(req_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                # Append (do not overwrite) the request-ID header.
                headers.append(
                    (self.header_name.lower().encode("latin-1"), req_id.encode("latin-1"))
                )
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_var.reset(token)
