"""Code embeddings infrastructure backed by pheno-sdk."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pheno.config.integration import MorphIntegrationSettings, get_morph_settings
from pheno.logging.core.logger import get_logger
from pheno.utilities.cache.lru import LruCache
from pheno.vector.embeddings import build_embedding_service

logger = get_logger("morph.embeddings")


class CodeEmbeddingsCache:
    """Simple disk cache for embeddings (compatible with legacy Morph cache)."""

    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, code: str, model: str) -> Path:
        digest = hashlib.sha256(f"{model}:{code}".encode()).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def get(self, code: str, model: str) -> list[float] | None:
        path = self._key(code, model)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            logger.debug("embedding_disk_cache_corrupt", file=str(path))
            return None

    def set(self, code: str, model: str, embedding: list[float]) -> None:
        path = self._key(code, model)
        try:
            with path.open("w", encoding="utf-8") as handle:
                json.dump(embedding, handle)
        except Exception as exc:
            logger.debug("embedding_disk_cache_write_failed", file=str(path), error=str(exc))

    def clear(self) -> None:
        for path in self.cache_dir.glob("*.json"):
            try:
                path.unlink()
            except Exception:
                logger.debug("embedding_disk_cache_clear_failed", file=str(path))


class CodeEmbedder:
    """Generate embeddings for code using shared pheno-sdk services."""

    def __init__(self, settings: MorphIntegrationSettings | None = None):
        self.settings = settings or get_morph_settings()
        self.model = self.settings.embedding_model
        namespace = "morph-embeddings"

        cache: LruCache | None = None
        if self.settings.cache_strategy.lower() == "lru":
            cache = LruCache(
                max_entries=self.settings.cache_max_entries,
                ttl=self.settings.cache_ttl_seconds,
                namespace=namespace,
            )

        self._service = build_embedding_service(
            provider=self.settings.embedding_provider,
            model=self.settings.embedding_model,
            base_url=self.settings.embedding_base_url,
            cache=cache,
            cache_namespace=namespace,
        )

        self._disk_cache = (
            CodeEmbeddingsCache(self.settings.embedding_cache_dir)
            if self.settings.embedding_cache_dir
            else None
        )

    async def embed_code(self, code: str) -> list[float]:
        """Embed a single code snippet, using disk/in-memory cache where possible."""

        if self._disk_cache:
            cached = self._disk_cache.get(code, self.model)
            if cached is not None:
                return cached

        try:
            vector = await self._service.embed_text(code)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("embedding_service_error", error=str(exc))
            vector = self._simple_embedding(code)

        if self._disk_cache:
            self._disk_cache.set(code, self.model, vector)
        return vector

    async def embed_codes(self, codes: list[str]) -> list[list[float]]:
        """Embed multiple snippets, leveraging caches and batch API when available."""
        vectors: list[list[float]] = []
        uncached_codes: list[str] = []
        uncached_indices: list[int] = []

        if self._disk_cache:
            for idx, code in enumerate(codes):
                cached = self._disk_cache.get(code, self.model)
                if cached is not None:
                    vectors.append(cached)
                else:
                    uncached_indices.append(idx)
                    uncached_codes.append(code)
        else:
            uncached_codes = codes
            uncached_indices = list(range(len(codes)))

        if uncached_codes:
            try:
                uncached_vectors = await self._service.embed_batch(uncached_codes)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("embedding_batch_error", error=str(exc))
                uncached_vectors = [self._simple_embedding(code) for code in uncached_codes]

            if self._disk_cache:
                for code, vector in zip(uncached_codes, uncached_vectors, strict=False):
                    self._disk_cache.set(code, self.model, vector)

            for idx, vector in zip(uncached_indices, uncached_vectors, strict=False):
                while len(vectors) <= idx:
                    vectors.append([])
                vectors[idx] = vector

        return vectors

    def _simple_embedding(self, code: str, *, dimension: int = 300) -> list[float]:
        """Fallback embedding using hashed token frequencies (legacy compatibility)."""
        import re

        tokens = re.findall(r"\w+", code.lower())
        embedding = [0.0] * dimension

        for position, token in enumerate(tokens[:dimension]):
            index = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % dimension
            weight = 1.0 / (1.0 + position * 0.01)
            embedding[index] += weight

        for idx in range(len(tokens) - 1):
            bigram = f"{tokens[idx]}_{tokens[idx + 1]}"
            index = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16) % dimension
            embedding[index] += 0.5

        norm = sum(value * value for value in embedding) ** 0.5
        if norm > 0:
            embedding = [value / norm for value in embedding]
        return embedding


_embedder: CodeEmbedder | None = None


def get_code_embedder() -> CodeEmbedder:
    """Singleton accessor to maintain compatibility with existing imports."""
    global _embedder
    if _embedder is None:
        _embedder = CodeEmbedder()
    return _embedder
