"""
Local embedding provider backed by sentence-transformers.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from functools import partial
from typing import Any

from pheno.vector.providers.base import EmbeddingProvider

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    SentenceTransformer = None


class SentenceTransformersEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using HuggingFace sentence-transformers models.

    Args:
        model_name: Sentence-transformers model to load
        cache_folder: Optional cache directory for model weights
        device: Device identifier ("cpu", "cuda", etc.)
        normalize_embeddings: Normalise output vectors (L2)
        encode_kwargs: Additional keyword arguments passed to ``encode``
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        *,
        cache_folder: str | None = None,
        device: str | None = None,
        normalize_embeddings: bool = True,
        encode_kwargs: dict[str, Any] | None = None,
    ) -> None:
        if SentenceTransformer is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Install with `pip install sentence-transformers` to enable local embeddings.",
            )

        self.model_name = model_name
        self._model = SentenceTransformer(model_name, cache_folder=cache_folder, device=device)
        self._dimension = int(self._model.get_sentence_embedding_dimension())
        self._normalize = normalize_embeddings
        self._encode_kwargs = encode_kwargs or {}

        logger.info("Loaded sentence-transformers model %s (dim=%s)", model_name, self._dimension)

    @property
    def provider_name(self) -> str:
        return f"sentence-transformers::{self.model_name}"

    @property
    def dimension(self) -> int:
        return self._dimension

    async def generate_embedding(self, text: str) -> list[float]:
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            partial(
                self._model.encode,
                texts,
                normalize_embeddings=self._normalize,
                convert_to_numpy=False,
                **self._encode_kwargs,
            ),
        )

        # sentence-transformers returns either list[list] or ndarray depending on options.
        return _to_list(result)


def _to_list(values: Any) -> list[list[float]]:
    if isinstance(values, list):
        if values and isinstance(values[0], list):
            return values
        if values and hasattr(values[0], "__iter__"):
            return [list(row) for row in values]
        return [list(values)]

    try:  # pragma: no cover - numpy optional
        import numpy as np  # type: ignore

        if isinstance(values, np.ndarray):
            if values.ndim == 1:
                return [values.astype(float).tolist()]
            return [row.astype(float).tolist() for row in values]
    except Exception:
        pass

    # Fallback: best effort conversion
    if not isinstance(values, Iterable):
        raise TypeError(f"Unexpected embedding payload type: {type(values)}")
    return [list(map(float, values))]
