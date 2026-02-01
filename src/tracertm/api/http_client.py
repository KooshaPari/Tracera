"""
HTTP client for TraceRTM API (canonical contract for MCP/CLI/other clients).
Includes wait+retry with exponential backoff for transient failures.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class TraceRTMHttpError(RuntimeError):
    """HTTP error from TraceRTM API."""

    def __init__(self, status: int, message: str, payload: Any | None = None) -> None:
        super().__init__(f"TraceRTM API error {status}: {message}")
        self.status = status
        self.message = message
        self.payload = payload


def _default_base_url() -> str:
    return (
        os.getenv("TRACERTM_API_URL")
        or os.getenv("PYTHON_BACKEND_URL")
        or "http://127.0.0.1:4000"
    )


def _is_retryable_status(status: int) -> bool:
    return status in (408, 429) or 500 <= status < 600


class TraceRTMHttpClient:
    """Lightweight HTTP client for TraceRTM REST API with wait+retry."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 20.0,
        max_retries: int = 3,
    ) -> None:
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
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        return self._request_with_retry(method, path, params=params, json=json, headers=headers)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(
            lambda e: isinstance(e, (httpx.NetworkError, httpx.TimeoutException))
            or (
                isinstance(e, TraceRTMHttpError)
                and _is_retryable_status(e.status)
            )
        ),
        reraise=True,
    )
    def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method.upper(),
                url,
                params=params,
                json=json,
                headers=self._build_headers(headers),
            )
        if response.status_code >= 400:
            if _is_retryable_status(response.status_code):
                message = response.text
                try:
                    payload = response.json()
                    if isinstance(payload, dict) and payload.get("detail"):
                        message = str(payload.get("detail"))
                except Exception:
                    payload = None
                raise TraceRTMHttpError(response.status_code, message, payload)
            message = response.text
            payload_val: Any | None = None
            try:
                payload_val = response.json()
                if isinstance(payload_val, dict) and payload_val.get("detail"):
                    message = str(payload_val.get("detail"))
            except Exception:
                payload_val = None
            raise TraceRTMHttpError(response.status_code, message, payload_val)
        if not response.content:
            return None
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Any | None = None, params: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, json=json, params=params)

    def put(self, path: str, *, json: Any | None = None, params: dict[str, Any] | None = None) -> Any:
        return self.request("PUT", path, json=json, params=params)

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("DELETE", path, params=params)
