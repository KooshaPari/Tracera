"""Prebuilt ML inference adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import AdapterOperationError, BasePrebuiltAdapter, MissingDependencyError

if TYPE_CHECKING:
    from collections.abc import Mapping


class _HTTPInferenceAdapter(BasePrebuiltAdapter):
    """Common utilities for HTTP-based inference backends."""

    def __init__(self, *, base_url: str, timeout: float | None = None, **config: Any):
        super().__init__(base_url=base_url.rstrip("/"), timeout=timeout, **config)

    def _post(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        url = f"{self._config['base_url']}/{path.lstrip('/')}"
        timeout = self._config.get("timeout", 30)
        try:
            httpx = self._require("httpx")
            response = httpx.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except MissingDependencyError:
            requests = self._require("requests")
            resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # pragma: no cover - actual request
            raise AdapterOperationError(f"Inference request failed: {exc}") from exc


class OllamaAdapter(_HTTPInferenceAdapter):
    """Adapter for the Ollama local inference server."""

    name = "ollama"
    category = "ml"

    def __init__(self, *, model: str = "llama3", base_url: str = "http://127.0.0.1:11434", **config: Any):
        super().__init__(base_url=base_url, **config)
        self._config["model"] = model

    def generate(self, prompt: str, **options: Any) -> str:
        payload = {"model": self._config["model"], "prompt": prompt, **options}
        result = self._post("api/generate", payload)
        return str(result.get("response", ""))

    def health_check(self) -> bool:
        try:
            self._post("api/tags", {})
            return True
        except AdapterOperationError:
            return False


class VLLMAdapter(_HTTPInferenceAdapter):
    """Adapter for vLLM HTTP server."""

    name = "vllm"
    category = "ml"

    def __init__(self, *, model: str, base_url: str = "http://127.0.0.1:8000", **config: Any):
        super().__init__(base_url=base_url, **config)
        self._config["model"] = model

    def generate(self, prompt: str, **options: Any) -> str:
        payload = {"prompt": prompt, "model": self._config["model"], **options}
        data = self._post("generate", payload)
        choices = data.get("choices") or []
        if choices:
            return str(choices[0].get("text", ""))
        return str(data.get("text", ""))


class MLXAdapter(BasePrebuiltAdapter):
    """Adapter wrapping Apple's ``mlx`` inference utilities."""

    name = "mlx"
    category = "ml"

    def __init__(self, *, model: str, **config: Any):
        super().__init__(model=model, **config)
        self._model = None

    def connect(self) -> None:
        self._require("mlx.core", install_hint="mlx")
        generation = self._require("mlx_lm", install_hint="mlx-lm")

        def _load() -> Any:
            return generation.load(self._config["model"], **self._config.get("load_options", {}))

        loaded = self._wrap_errors("load_model", _load)
        if isinstance(loaded, tuple) and len(loaded) == 2:
            self._model = {"model": loaded[0], "tokenizer": loaded[1]}
        elif isinstance(loaded, dict):
            self._model = loaded
        else:  # pragma: no cover - defensive
            raise AdapterOperationError("Unexpected MLX load() return value")
        super().connect()

    def generate(self, prompt: str, **options: Any) -> str:
        self.ensure_connected()
        if not self._model:
            raise AdapterOperationError("mlx model not loaded")
        tokenizer = self._model.get("tokenizer")
        generator = self._model.get("model")
        if tokenizer is None or generator is None:
            raise AdapterOperationError("mlx adapter missing tokenizer or model")
        tokens = tokenizer.encode(prompt)
        max_tokens = options.get("max_tokens", 128)
        temperature = options.get("temperature", 0.7)

        try:
            sampled = generator.generate(tokens, max_tokens=max_tokens, temperature=temperature)
            return tokenizer.decode(sampled)
        except Exception as exc:  # pragma: no cover - relies on native libs
            raise AdapterOperationError(f"mlx generation failed: {exc}") from exc

    def close(self) -> None:
        self._model = None
        super().close()


class OpenAIInferenceAdapter(BasePrebuiltAdapter):
    """Adapter using the ``openai`` SDK for hosted inference."""

    name = "openai"
    category = "ml"

    def __init__(self, *, model: str = "gpt-4o-mini", api_key: str | None = None, **config: Any):
        super().__init__(model=model, api_key=api_key, **config)
        self._client: Any | None = None

    def connect(self) -> None:
        openai = self._require("openai")

        def _create() -> Any:
            key = self._config.get("api_key")
            if hasattr(openai, "OpenAI"):
                if key:
                    return openai.OpenAI(api_key=key)
                return openai.OpenAI()
            if key:
                openai.api_key = key
            return openai

        self._client = self._wrap_errors("connect", _create)
        super().connect()

    def generate(self, prompt: str, **options: Any) -> str:
        self.ensure_connected()
        messages = options.get("messages")
        content = prompt if messages is None else None

        def _call() -> Any:
            if hasattr(self._client, "chat"):
                return self._client.chat.completions.create(
                    model=self._config.get("model"),
                    messages=messages or [{"role": "user", "content": content}],
                    temperature=options.get("temperature"),
                    max_tokens=options.get("max_tokens"),
                )
            if hasattr(self._client, "responses"):
                return self._client.responses.create(
                    model=self._config.get("model"),
                    input=messages or content or "",
                    temperature=options.get("temperature"),
                    max_output_tokens=options.get("max_tokens"),
                )
            # Legacy API
            return self._client.ChatCompletion.create(
                model=self._config.get("model"),
                messages=messages or [{"role": "user", "content": content}],
                temperature=options.get("temperature"),
                max_tokens=options.get("max_tokens"),
            )

        result = self._wrap_errors("generate", _call)
        if hasattr(result, "choices"):
            choice = result.choices[0]
            message = getattr(choice, "message", choice)
            return getattr(message, "content", message.get("content", ""))
        if isinstance(result, dict):
            return result.get("output_text") or ""
        return str(result)


__all__ = [
    "MLXAdapter",
    "OllamaAdapter",
    "OpenAIInferenceAdapter",
    "VLLMAdapter",
]
