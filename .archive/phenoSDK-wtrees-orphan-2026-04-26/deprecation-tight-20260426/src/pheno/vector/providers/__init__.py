"""
Embedding providers for Vector-Kit.
"""

from __future__ import annotations

from typing import Any, List

from pheno.vector.providers.base import EmbeddingProvider
from pheno.vector.providers.factory import (
    get_available_providers,
    get_embedding_service,
)

__all__ = [
    "EmbeddingProvider",
    "LiteLLMEmbeddingProvider",
    "SentenceTransformersEmbeddingProvider",
    "get_available_providers",
    "get_embedding_service",
]


def __getattr__(name: str) -> Any:
    if name == "LiteLLMEmbeddingProvider":
        from pheno.vector.providers.litellm_provider import LiteLLMEmbeddingProvider

        return LiteLLMEmbeddingProvider
    if name == "SentenceTransformersEmbeddingProvider":
        from pheno.vector.providers.sentence_transformers import (
            SentenceTransformersEmbeddingProvider,
        )

        return SentenceTransformersEmbeddingProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
