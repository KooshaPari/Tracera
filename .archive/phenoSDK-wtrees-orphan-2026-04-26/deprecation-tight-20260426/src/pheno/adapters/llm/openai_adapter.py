from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from typing import Any

from adapter_kit.llm.contracts import (
    BaseLLMProvider,
    GenerateRequest,
    GenerateResponse,
    ModelMetadata,
    TokenUsage,
)
from adapter_kit.llm.shared.http import (
    async_post_json,
    get_default_retries,
    get_default_timeout,
)

_DEFAULT_MODELS: list[ModelMetadata] = [
    ModelMetadata(
        id="gpt-4o-mini", provider="openai", description="Fast small model", context_window=128000,
    ),
    ModelMetadata(
        id="gpt-4.1", provider="openai", description="Reasoning model", context_window=200000,
    ),
]


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, *, models: Sequence[ModelMetadata] | None = None):
        self._models = list(models) if models else list(_DEFAULT_MODELS)

    @property
    def name(self) -> str:
        return "openai"

    async def list_models(self) -> Sequence[ModelMetadata]:
        return list(self._models)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """
        Generate text using OpenAI API or fallback to echo mode.
        """
        if self._should_use_real_api():
            result = await self._try_real_api_call(request)
            if result is not None:
                return result

        return self._create_echo_response(request)

    def _should_use_real_api(self) -> bool:
        """
        Check if real API calls are enabled.
        """
        return str(os.environ.get("PHENO_SDK_LLM_REAL", "")).lower() in {"1", "true", "yes"}

    async def _try_real_api_call(self, request: GenerateRequest) -> GenerateResponse | None:
        """
        Try to make a real API call, return None if it fails.
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or not request.model:
            return None

        try:
            payload = self._build_api_payload(request)
            raw = await self._make_api_request(payload, api_key)
            return self._process_api_response(raw)
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
            # Fall back to echo on any network/parse error
            return None

    def _build_api_payload(self, request: GenerateRequest) -> dict[str, Any]:
        """
        Build the API request payload.
        """
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": str(request.prompt)}],
        }

        opts: Mapping[str, Any] = request.options or {}
        if "temperature" in opts:
            payload["temperature"] = float(opts["temperature"])  # type: ignore[assignment]

        return payload

    async def _make_api_request(self, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
        """
        Make the actual API request.
        """
        return await async_post_json(
            os.environ.get("OPENAI_BASE_URL", "https://api.openai.com") + "/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            payload=payload,
            timeout=get_default_timeout(),
            max_retries=get_default_retries()[0],
            backoff_factor=get_default_retries()[1],
        )

    def _process_api_response(self, raw: dict[str, Any]) -> GenerateResponse:
        """
        Process the API response and create a GenerateResponse.
        """
        text = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage_obj = raw.get("usage") or {}
        tu = TokenUsage(
            input_tokens=int(
                usage_obj.get("prompt_tokens", 0) or usage_obj.get("input_tokens", 0) or 0,
            ),
            output_tokens=int(
                usage_obj.get("completion_tokens", 0) or usage_obj.get("output_tokens", 0) or 0,
            ),
        )
        return GenerateResponse(text=text or "", usage=tu, raw=raw, finish_reason="stop")

    def _create_echo_response(self, request: GenerateRequest) -> GenerateResponse:
        """
        Create an echo response when real API is not available.
        """
        opts: Mapping[str, Any] = request.options or {}
        usage = opts.get("usage")

        if isinstance(usage, dict):
            tu = TokenUsage(
                input_tokens=int(usage.get("input_tokens", 0)),
                output_tokens=int(usage.get("output_tokens", 0)),
            )
        else:
            tu = None

        return GenerateResponse(
            text=f"openai:{request.model}:{request.prompt}", usage=tu, finish_reason="stop",
        )

    async def generate_stream(self, request: GenerateRequest):
        """Stream text via OpenAI Chat Completions streaming when real-calls enabled.

        Falls back to echo chunking when disabled.
        """
        from adapter_kit.llm.contracts import StreamEvent

        # Real-call streaming path
        if str(os.environ.get("PHENO_SDK_LLM_REAL", "")).lower() in {"1", "true", "yes"}:
            api_key = os.environ.get("OPENAI_API_KEY")
            base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com")
            if api_key and request.model:
                try:
                    import aiohttp

                    url = base.rstrip("/") + "/v1/chat/completions"
                    payload = {
                        "model": request.model,
                        "messages": [{"role": "user", "content": str(request.prompt)}],
                        "stream": True,
                    }
                    opts: Mapping[str, Any] = request.options or {}
                    if "temperature" in opts:
                        payload["temperature"] = float(opts["temperature"])  # type: ignore[assignment]
                    timeout = aiohttp.ClientTimeout(total=get_default_timeout())
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(url, json=payload, headers=headers) as resp:
                            resp.raise_for_status()
                            async for line_bytes in resp.content:
                                line = line_bytes.decode("utf-8", errors="ignore").strip()
                                if not line:
                                    continue
                                if not line.startswith("data:"):
                                    continue
                                data = line.partition(":")[2].strip()
                                if data == "[DONE]":
                                    yield StreamEvent(type="done")
                                    return
                                import json as _json

                                try:
                                    obj = _json.loads(data)
                                except Exception:
                                    continue
                                # choices[0].delta.content may contain a piece of text
                                choices = obj.get("choices") or []
                                if choices:
                                    delta = choices[0].get("delta") or {}
                                    content = delta.get("content")
                                    if content:
                                        yield StreamEvent(type="delta", text=content)
                    return
                except Exception:
                    # Fall through to echo chunking
                    pass
        # Fallback: echo chunking
        text = f"openai:{request.model}:{request.prompt}"
        for i in range(0, len(text), 64):
            yield StreamEvent(type="delta", text=text[i : i + 64])
        # Try to propagate usage if any
        opts: Mapping[str, Any] = request.options or {}
        usage = opts.get("usage") if isinstance(opts, Mapping) else None
        tu = None
        if isinstance(usage, dict):
            tu = TokenUsage(int(usage.get("input_tokens", 0)), int(usage.get("output_tokens", 0)))
        yield StreamEvent(type="done", usage=tu)
