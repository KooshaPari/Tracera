"""OpenTelemetry event hooks for httpx clients.

Provides helpers to build event_hooks mapping for httpx Client/AsyncClient that
create spans for outbound HTTP requests.

Usage:
    hooks = build_httpx_otel_hooks()
    client = create_client(event_hooks=hooks)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opentelemetry import trace

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


def build_httpx_otel_hooks() -> Mapping[str, Iterable[Any]]:
    """
    Return httpx event_hooks for sync Client.
    """
    tracer = trace.get_tracer("pydevkit.http.httpx")

    def on_request(request):
        span = tracer.start_span(name=f"HTTP {request.method}")
        # store span on request extensions to finish later
        request.extensions["otel_span"] = span
        try:
            url = str(request.url)
        except Exception:
            url = ""
        span.set_attribute("http.request.method", request.method)
        span.set_attribute("http.request.url", url)

    def on_response(response):
        span = response.request.extensions.pop("otel_span", None)
        if span is None:
            return
        span.set_attribute("http.response.status_code", response.status_code)
        span.end()  # finish span

    return {"request": [on_request], "response": [on_response]}


def build_async_httpx_otel_hooks() -> Mapping[str, Iterable[Any]]:
    """
    Return httpx event_hooks for AsyncClient.
    """
    tracer = trace.get_tracer("pydevkit.http.httpx")

    async def on_request(request):
        span = tracer.start_span(name=f"HTTP {request.method}")
        request.extensions["otel_span"] = span
        try:
            url = str(request.url)
        except Exception:
            url = ""
        span.set_attribute("http.request.method", request.method)
        span.set_attribute("http.request.url", url)

    async def on_response(response):
        span = response.request.extensions.pop("otel_span", None)
        if span is None:
            return
        span.set_attribute("http.response.status_code", response.status_code)
        span.end()

    return {"request": [on_request], "response": [on_response]}
