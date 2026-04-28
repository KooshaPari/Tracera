"""HTTP client for TraceRTM API (canonical contract for MCP/CLI/other clients).

Includes wait+retry with exponential backoff for transient failures.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

# HTTP status ranges for retry and error handling
HTTP_BAD_REQUEST_START = 400
HTTP_SERVER_ERROR_START = 500
HTTP_SERVER_ERROR_END = 600


class TraceRTMHttpError(RuntimeError):
    """HTTP error from TraceRTM API."""

    def __init__(self, status: int, message: str, payload: object | None = None) -> None:
        """Initialize TraceRTMHttpError.

        Args:
            status: HTTP status code.
            message: Human-readable error message.
            payload: Optional parsed response payload.
        """
        super().__init__(f"TraceRTM API error {status}: {message}")
        self.status = status
        self.message = message
        self.payload = payload


def _default_base_url() -> str:
    """Return the default base URL for the TraceRTM API."""
    return os.getenv("TRACERTM_API_URL") or os.getenv("PYTHON_BACKEND_URL") or "http://127.0.0.1:4000"


def _is_retryable_status(status: int) -> bool:
    """Return True if the HTTP status code should be retried."""
    return status in {408, 429} or (HTTP_SERVER_ERROR_START <= status < HTTP_SERVER_ERROR_END)


def _error_message_and_payload(response: httpx.Response) -> tuple[str, Any | None]:
    """Extract message and optional payload from error response body."""
    message = response.text
    payload: object | None = None
    try:
        payload = response.json()
        if isinstance(payload, dict) and payload.get("detail"):
            message = str(payload.get("detail"))
    except ValueError:
        payload = None
    return message, payload


class TraceRTMHttpClient:
    """Lightweight HTTP client for TraceRTM REST API with wait+retry."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 20.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: Optional base URL override.
            token: Optional bearer token.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for transient failures.
        """
        self.base_url = (base_url or _default_base_url()).rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries

    def _build_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        merged: dict[str, str] = {
            "Content-Type": "application/json",
        }
        if headers:
            merged.update(headers)
        if self.token:
            merged.setdefault("Authorization", f"Bearer {self.token}")
        return merged

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: object | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Perform an HTTP request with retry behavior.

        Args:
            method: HTTP method (GET/POST/etc.).
            path: Request path relative to base_url.
            params: Optional query parameters.
            json: Optional JSON body.
            headers: Optional extra headers.

        Returns:
            Parsed response content (JSON/dict) or raw text/None.
        """
        return self._request_with_retry(method, path, params=params, json=json, headers=headers)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(
            lambda e: (
                isinstance(e, (httpx.NetworkError, httpx.TimeoutException))
                or (isinstance(e, TraceRTMHttpError) and _is_retryable_status(e.status))
            ),
        ),
        reraise=True,
    )
    def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: object | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Perform a request and raise TraceRTMHttpError for non-2xx responses."""
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method.upper(),
                url,
                params=params,
                json=json,
                headers=self._build_headers(headers),
            )
        if response.status_code >= HTTP_BAD_REQUEST_START:
            message, payload = _error_message_and_payload(response)
            raise TraceRTMHttpError(response.status_code, message, payload)
        if not response.content:
            return None
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Send a GET request."""
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: object | None = None, params: dict[str, Any] | None = None) -> Any:
        """Send a POST request."""
        return self.request("POST", path, json=json, params=params)

    def put(self, path: str, *, json: object | None = None, params: dict[str, Any] | None = None) -> Any:
        """Send a PUT request."""
        return self.request("PUT", path, json=json, params=params)

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Send a DELETE request."""
        return self.request("DELETE", path, params=params)
