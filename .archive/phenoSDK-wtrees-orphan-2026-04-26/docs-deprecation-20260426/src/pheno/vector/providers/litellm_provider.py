"""
Embedding provider that delegates to litellm.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pheno.vector.providers.base import EmbeddingProvider

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import litellm  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    litellm = None


class LiteLLMEmbeddingProvider(EmbeddingProvider):
    """Embedder backed by `litellm.embedding` / `litellm.aembedding`.

    Args:
        model: Embedding model identifier (e.g. ``"text-embedding-3-large"``)
        api_key: Optional API key (falls back to environment variables supported by litellm)
        litellm_kwargs: Additional kwargs forwarded to the litellm call
    """

    def __init__(
        self,
        model: str,
        *,
        api_key: str | None = None,
        litellm_kwargs: dict[str, Any] | None = None,
    ) -> None:
        if litellm is None:  # pragma: no cover - dependency guard
            raise RuntimeError(
                "litellm is not installed. "
                "Install with `pip install litellm` to enable remote embedding providers.",
            )

        self.model = model
        self.api_key = api_key
        self._litellm_kwargs = litellm_kwargs or {}
        self._dimension: int | None = None

    @property
    def provider_name(self) -> str:
        return f"litellm::{self.model}"

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise RuntimeError(
                "Embedding dimension unknown; run generate_embedding(s) at least once to populate dimension.",
            )
        return self._dimension

    async def generate_embedding(self, text: str) -> list[float]:
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        payload: dict[str, Any] = {"model": self.model, "input": texts}
        if self.api_key:
            payload["api_key"] = self.api_key

        payload.update(self._litellm_kwargs)

        try:
            response = await _call_litellm_embedding(payload)
        except Exception as exc:  # pragma: no cover - defensive path
            logger.exception("litellm_embedding_failed", model=self.model, error=str(exc))
            raise

        embeddings = _extract_embeddings(response)
        if self._dimension is None and embeddings:
            self._dimension = len(embeddings[0])

        return embeddings


async def _call_litellm_embedding(payload: dict[str, Any]) -> Any:
    """
    Call litellm embedding API, preferring async interface.
    """
    assert litellm is not None  # For type checkers

    if hasattr(litellm, "aembedding"):
        return await litellm.aembedding(**payload)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: litellm.embedding(**payload))


def _extract_embeddings(response: Any) -> list[list[float]]:
    """Extract embeddings from litellm response payload.

    Supports both dictionary-style responses and typed objects.
    """
    if response is None:
        raise RuntimeError("litellm returned no response for embeddings")

    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")

    if not data:
        raise RuntimeError("litellm embedding response missing data field")

    embeddings: list[list[float]] = []
    for item in data:
        embedding = getattr(item, "embedding", None)
        if embedding is None and isinstance(item, dict):
            embedding = item.get("embedding")
        if embedding is None:
            raise RuntimeError(f"litellm embedding item missing 'embedding': {item!r}")
        embeddings.append(list(map(float, embedding)))

    return embeddings
