"""
Embedding service factory that can select between multiple providers.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pheno.vector.providers.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_TRUTHY = {"1", "true", "yes", "on"}


def _env_flag(name: str, default: str = "0") -> bool:
    value = os.getenv(name, default)
    return value.strip().lower() in _TRUTHY if value is not None else False


_SENTENCE_TRANSFORMERS_OPT_IN = _env_flag("PHENO_ENABLE_SENTENCE_TRANSFORMERS", "0")
_SENTENCE_TRANSFORMERS_DISABLED = _env_flag("PHENO_DISABLE_SENTENCE_TRANSFORMERS", "0")


# ---------------------------------------------------------------------------
# Result containers mirroring VertexAIEmbeddingService return types
# ---------------------------------------------------------------------------


@dataclass
class EmbeddingResult:
    embedding: list[float]
    tokens_used: int
    model: str
    cached: bool = False


@dataclass
class BatchEmbeddingResult:
    embeddings: list[list[float]]
    total_tokens: int
    model: str
    cached_count: int = 0


class ProviderAdapter:
    """
    Adapter that wraps an EmbeddingProvider in the Vertex-compatible API.
    """

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    async def generate_embedding(
        self,
        text: str,
        model: str | None = None,
        use_cache: bool = True,
    ) -> EmbeddingResult:
        vector = await self.provider.generate_embedding(text)
        provider_name = getattr(self.provider, "provider_name", self.provider.__class__.__name__)
        return EmbeddingResult(
            embedding=vector,
            tokens_used=0,
            model=model or provider_name,
            cached=False,
        )

    async def generate_batch_embeddings(
        self,
        texts: list[str],
        model: str | None = None,
        use_cache: bool = True,
        batch_size: int = 128,
    ) -> BatchEmbeddingResult:
        embeddings = await self.provider.generate_embeddings(texts)
        provider_name = getattr(self.provider, "provider_name", self.provider.__class__.__name__)
        return BatchEmbeddingResult(
            embeddings=embeddings,
            total_tokens=0,
            model=model or provider_name,
            cached_count=0,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def get_embedding_service(provider_type: str | None = None, **kwargs: Any):
    """Get an embedding service instance.

    If ``provider_type`` is omitted, auto-detect providers in preference order:
    Vertex AI → LiteLLM. The sentence-transformers provider is opt-in via
    ``PHENO_ENABLE_SENTENCE_TRANSFORMERS=1`` because importing the optional
    dependency triggers heavyweight native libraries that are not available in
    all environments.
    """
    if provider_type:
        provider_key = provider_type.replace("_", "-").lower()
        if provider_key in ("vertex", "vertex-ai", "gemini", "google"):
            return _create_vertex_service(**kwargs)
        if provider_key in ("sentence-transformers", "sentence-transformer", "local"):
            return _create_sentence_transformers_service(**kwargs)
        if provider_key in ("litellm", "openai", "voyageai", "cohere"):
            return _create_litellm_service(provider_key, **kwargs)
        raise ValueError(f"Unknown embedding provider type: {provider_type}")

    # Auto detection mode
    errors: list[Exception] = []
    for candidate in _auto_detect_candidates():
        try:
            return get_embedding_service(candidate, **kwargs)
        except Exception as exc:  # pragma: no cover - control flow
            errors.append(exc)
            continue

    if errors:
        logger.debug("embedding_provider_auto_detect_failed", errors=[str(e) for e in errors])
        message = (
            "No embedding provider available. Install google-cloud-aiplatform or litellm "
            "(with API credentials). To opt into the local sentence-transformers provider, "
            "set PHENO_ENABLE_SENTENCE_TRANSFORMERS=1 and ensure the dependency is installed."
        )
        raise RuntimeError(message) from errors[-1]

    raise RuntimeError("No embedding provider available.")


def _auto_detect_candidates() -> tuple[str, ...]:
    """
    Return provider keys to try during auto-detection.
    """
    candidates: list[str] = ["vertex", "litellm"]
    if _should_include_sentence_transformers():
        candidates.append("sentence-transformers")
    return tuple(candidates)


def get_available_providers() -> dict[str, bool]:
    """
    Return availability flags for known providers.
    """
    return {
        "vertex_ai": _check_vertex_ai_available(),
        "sentence_transformers": _has_sentence_transformers(),
        "litellm": _has_litellm(),
    }


# ---------------------------------------------------------------------------
# Provider creation helpers
# ---------------------------------------------------------------------------


def _should_include_sentence_transformers() -> bool:
    """
    Determine if auto-detection should attempt the sentence-transformers provider.
    """
    if _SENTENCE_TRANSFORMERS_DISABLED:
        return False
    if not _SENTENCE_TRANSFORMERS_OPT_IN:
        return False
    return _has_sentence_transformers()


@lru_cache(maxsize=1)
def _has_sentence_transformers() -> bool:
    """
    Lightweight check for sentence-transformers availability.
    """
    if _SENTENCE_TRANSFORMERS_DISABLED:
        return False
    try:
        return importlib.util.find_spec("sentence_transformers") is not None
    except Exception:
        return False


@lru_cache(maxsize=1)
def _has_litellm() -> bool:
    """
    Lightweight check for litellm availability.
    """
    try:
        return importlib.util.find_spec("litellm") is not None
    except Exception:
        return False


def _create_vertex_service(**kwargs: Any):
    """
    Instantiate the Vertex AI embedding service.
    """
    if not _check_vertex_ai_available():
        raise RuntimeError(
            "Vertex AI is not properly configured. Required:\n"
            "  - GOOGLE_CLOUD_PROJECT environment variable\n"
            "  - GOOGLE_APPLICATION_CREDENTIALS or gcloud ADC\n"
            "  - google-cloud-aiplatform package installed",
        )

    try:
        from .vertex import (  # Local import to avoid heavy dependency at module import
            VertexAIEmbeddingService,
        )

        if kwargs:
            logger.debug(
                "vertex_embedding_extra_kwargs_ignored", extra_kwargs=sorted(kwargs.keys()),
            )
        logger.info("Using Vertex AI embedding service (gemini-embedding-001)")
        return VertexAIEmbeddingService()
    except Exception as exc:
        raise RuntimeError(f"Failed to initialize Vertex AI embeddings: {exc}") from exc


def _create_sentence_transformers_service(**kwargs: Any):
    """
    Instantiate the sentence-transformers embedding provider lazily.
    """
    if not _has_sentence_transformers():
        raise RuntimeError(
            "sentence-transformers is not installed or has been disabled. "
            "Install the dependency and set PHENO_ENABLE_SENTENCE_TRANSFORMERS=1 to use local embeddings.",
        )

    try:
        module = importlib.import_module("pheno.vector.providers.sentence_transformers")
    except Exception as exc:  # pragma: no cover - defensive guard
        raise RuntimeError(f"Failed to import sentence-transformers provider: {exc}") from exc

    provider_cls = getattr(module, "SentenceTransformersEmbeddingProvider", None)
    if provider_cls is None:
        raise RuntimeError(
            "sentence-transformers provider unavailable. Ensure pheno-sdk is up to date.",
        )

    provider = provider_cls(**kwargs)
    return ProviderAdapter(provider)


def _create_litellm_service(provider_key: str, **kwargs: Any):
    """
    Instantiate a LiteLLM embedding provider, applying sensible defaults per provider.
    """
    try:
        module = importlib.import_module("pheno.vector.providers.litellm_provider")
    except Exception as exc:  # pragma: no cover - defensive guard
        raise RuntimeError(f"Failed to import litellm provider: {exc}") from exc

    provider_cls = getattr(module, "LiteLLMEmbeddingProvider", None)
    if getattr(module, "litellm", None) is None or provider_cls is None:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "litellm is not installed. Install with `pip install litellm` and configure the desired provider API key.",
        )

    defaults: Mapping[str, str] = {
        "litellm": kwargs.get("model", "text-embedding-3-large"),
        "openai": kwargs.get("model", "text-embedding-3-large"),
        "voyageai": kwargs.get("model", "voyage-large-2"),
        "cohere": kwargs.get("model", "cohere/embed-english-v3.0"),
    }

    model = defaults.get(provider_key, kwargs.get("model", "text-embedding-3-large"))
    api_key = kwargs.get("api_key")
    litellm_kwargs = kwargs.get("litellm_kwargs", {})

    provider = provider_cls(model=model, api_key=api_key, litellm_kwargs=litellm_kwargs)
    return ProviderAdapter(provider)


# ---------------------------------------------------------------------------
# Availability checks
# ---------------------------------------------------------------------------


def _check_vertex_ai_available() -> bool:
    """
    Check if Vertex AI is available and properly configured.
    """
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
        if not project:
            return False

        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not creds_path and not creds_json and not _check_gcloud_auth():
            return False

        # Ensure google-cloud-aiplatform is installed
        import importlib.util

        return importlib.util.find_spec("vertexai") is not None
    except Exception:
        return False


def _check_gcloud_auth() -> bool:
    try:
        from google.auth import default  # type: ignore

        creds, project = default()
        return bool(creds and project)
    except Exception:
        return False
