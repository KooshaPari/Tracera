"""HTTP utilities module for PyDevKit.

Note: HTTPClient is deprecated in favor of httpx-based factories
(create_client/create_async_client) in pydevkit.http.httpx_client.
"""

from .auth import APIKeyAuth, BasicAuth, BearerAuth
from .correlation import (
    build_async_httpx_correlation_hooks,
    build_httpx_correlation_hooks,
)
from .headers import HeaderManager, add_user_agent, normalize_headers
from .httpx_client import (
    async_request_with_retries,
    create_async_client,
    create_client,
    request_with_retries,
)
from .otel_hooks import (
    build_async_httpx_otel_hooks,
    build_httpx_otel_hooks,
)
from .retries import RetryStrategy, exponential_backoff, with_retries

__all__ = [
    "APIKeyAuth",
    "BasicAuth",
    "BearerAuth",
    "HeaderManager",
    "RetryStrategy",
    "add_user_agent",
    "async_request_with_retries",
    "build_async_httpx_correlation_hooks",
    "build_async_httpx_otel_hooks",
    # Correlation header hooks for httpx
    "build_httpx_correlation_hooks",
    # OTel hooks for httpx
    "build_httpx_otel_hooks",
    "create_async_client",
    # httpx-based factories/helpers
    "create_client",
    "exponential_backoff",
    "normalize_headers",
    "request_with_retries",
    "with_retries",
]
