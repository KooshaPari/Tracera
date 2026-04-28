"""High-level embedding service with Morph-compatible API.

Provides unified interface for text embeddings with caching and batch processing.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger
from pheno.vector.embeddings.base import EmbeddingProvider, InMemoryEmbeddings

if TYPE_CHECKING:
    from pathlib import Path

    from pheno.utilities.cache.base import CacheProtocol

logger = get_logger("pheno.vector.embeddings.service")


@dataclass
class ModelInfo:
    """
    Information about the embedding model.
    """

    name: str
    dimension: int
    max_tokens: int
    provider: str


class EmbeddingService:
    """Unified embedding service (Morph-compatible).

    Provides text embedding with caching and batch processing support.
    """

    def __init__(
        self,
        provider: EmbeddingProvider | None = None,
        *,
        cache: CacheProtocol | None = None,
        batch_size: int = 100,
    ) -> None:
        """Initialize embedding service.

        Args:
            provider: Embedding provider (default: InMemoryEmbeddings)
            cache: Optional cache for embeddings
            batch_size: Maximum batch size for processing
        """
        self.provider = provider or InMemoryEmbeddings()
        self.cache = cache
        self.batch_size = batch_size
        self._cache_namespace = "embeddings"
        self._model_name = getattr(self.provider, "model_name", "unknown")

    async def embed_text(self, text: str) -> list[float]:
        """Embed single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache first
        if self.cache:
            cache_key = self._cache_key(text)
            cached = await self.cache.get(cache_key)
            if cached is not None:
                logger.debug("embedding_cache_hit", namespace=self._cache_namespace)
                return cached

        # Generate embedding
        vector = await self.provider.embed_text(text)

        # Store in cache
        if self.cache:
            await self.cache.set(self._cache_key(text), vector)

        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts with batching.

        Args:
            texts: Texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Process in batches
        results: list[list[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]

            # Check cache for each text
            batch_results: list[list[float] | None] = [None] * len(batch)
            uncached_indices: list[int] = []
            uncached_texts: list[str] = []

            if self.cache:
                for j, text in enumerate(batch):
                    cache_key = self._cache_key(text)
                    cached = await self.cache.get(cache_key)
                    if cached is not None:
                        batch_results[j] = cached
                    else:
                        uncached_indices.append(j)
                        uncached_texts.append(text)
            else:
                uncached_indices = list(range(len(batch)))
                uncached_texts = batch

            # Generate embeddings for uncached texts
            if uncached_texts:
                uncached_vectors = await self.provider.embed_documents(uncached_texts)

                # Store in cache and results
                for idx, vector in zip(uncached_indices, uncached_vectors, strict=False):
                    batch_results[idx] = vector

                    if self.cache:
                        cache_key = self._cache_key(batch[idx])
                        await self.cache.set(cache_key, vector)

            results.extend([v for v in batch_results if v is not None])

        return results

    async def get_model_info(self) -> ModelInfo:
        """Get information about the embedding model.

        Returns:
            ModelInfo with model details
        """
        return ModelInfo(
            name=self._model_name,
            dimension=self.provider.dimension,
            max_tokens=getattr(self.provider, "max_tokens", 8192),
            provider=self.provider.__class__.__name__,
        )

    async def embed_file(
        self, file_path: Path, *, chunk_size: int = 1000,
    ) -> list[tuple[str, list[float]]]:
        """Embed text from a file, splitting into chunks.

        Args:
            file_path: Path to text file
            chunk_size: Maximum characters per chunk

        Returns:
            List of (chunk_text, embedding) tuples
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.exception("file_read_error", file=str(file_path), error=str(e))
            return []

        # Split into chunks
        chunks = self._split_text(content, chunk_size)

        # Embed chunks
        vectors = await self.embed_batch(chunks)

        return list(zip(chunks, vectors, strict=False))

    def _split_text(self, text: str, chunk_size: int) -> list[str]:
        """
        Split text into chunks.
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        current_chunk = []
        current_size = 0

        # Split by sentences (simple approach)
        sentences = text.replace("! ", "!|").replace("? ", "?|").replace(". ", ".|").split("|")

        for sentence in sentences:
            sentence_size = len(sentence)

            if current_size + sentence_size > chunk_size and current_chunk:
                # Start new chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _cache_key(self, text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"{self._cache_namespace}:{self._model_name}:{digest}"


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI embeddings provider.

    Requires: pip install openai
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "text-embedding-3-small",
        dimension: int = 1536,
    ):
        """Initialize OpenAI embeddings.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model name
            dimension: Embedding dimension
        """
        try:
            import openai
        except ImportError:
            raise ImportError("OpenAI embeddings require: pip install openai")

        client_kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        if extra_headers:
            client_kwargs["default_headers"] = extra_headers

        self.client = openai.AsyncOpenAI(**client_kwargs)
        self.model_name = model
        self._dimension = dimension
        self.max_tokens = 8192

    async def embed_text(self, text: str) -> list[float]:
        """
        Embed single text using OpenAI.
        """
        response = await self.client.embeddings.create(
            model=self.model_name,
            input=text,
        )
        return response.data[0].embedding

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents using OpenAI.
        """
        response = await self.client.embeddings.create(
            model=self.model_name,
            input=texts,
        )
        return [item.embedding for item in response.data]

    @property
    def dimension(self) -> int:
        """
        Get embedding dimension.
        """
        return self._dimension


class SentenceTransformerEmbeddings(EmbeddingProvider):
    """Sentence Transformers embeddings provider (local).

    Requires: pip install sentence-transformers
    """

    def __init__(
        self,
        model: str = "all-MiniLM-L6-v2",
        *,
        device: str | None = None,
    ):
        """Initialize Sentence Transformers embeddings.

        Args:
            model: Model name from HuggingFace
            device: Device to use ('cpu', 'cuda', etc.)
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("Sentence Transformers require: pip install sentence-transformers")

        self.model = SentenceTransformer(model, device=device)
        self.model_name = model
        self._dimension = self.model.get_sentence_embedding_dimension()
        self.max_tokens = 512  # Typical for sentence transformers

    async def embed_text(self, text: str) -> list[float]:
        """
        Embed single text using Sentence Transformers.
        """
        import asyncio

        # Run in thread pool since sentence-transformers is sync
        loop = asyncio.get_running_loop()
        vector = await loop.run_in_executor(None, self.model.encode, text)
        return vector.tolist()

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents using Sentence Transformers.
        """
        import asyncio

        loop = asyncio.get_running_loop()
        vectors = await loop.run_in_executor(None, self.model.encode, texts)
        return [v.tolist() for v in vectors]

    @property
    def dimension(self) -> int:
        """
        Get embedding dimension.
        """
        return self._dimension


def create_embedding_provider(
    provider: str,
    *,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    device: str | None = None,
) -> EmbeddingProvider:
    """Factory to create embedding providers by name.

    Supported providers:
        - ``openai``: Uses OpenAI embeddings (default).
        - ``openrouter``: OpenAI-compatible API hosted by OpenRouter.
        - ``sentence_transformers``: Local sentence-transformers models.
        - ``inmemory``: Deterministic random vectors (testing).
    """
    key = provider.lower()
    if key == "openrouter":
        # OpenRouter is OpenAI-compatible; allow overriding base URL
        return OpenAIEmbeddings(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            model=model or "text-embedding-3-small",
            base_url=base_url or "https://openrouter.ai/api/v1",
            extra_headers={"HTTP-Referer": "https://github.com/phenoflow/"},
        )
    if key == "openai":
        return OpenAIEmbeddings(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            model=model or "text-embedding-3-small",
            base_url=base_url,
        )
    if key in {"sentence-transformers", "sentence_transformers"}:
        return SentenceTransformerEmbeddings(model=model or "all-MiniLM-L6-v2", device=device)
    if key in {"inmemory", "mock"}:
        return InMemoryEmbeddings(dim=384)
    raise ValueError(f"Unsupported embedding provider: {provider}")


def build_embedding_service(
    *,
    provider: str,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    cache: CacheProtocol | None = None,
    batch_size: int = 100,
    cache_namespace: str = "embeddings",
    device: str | None = None,
) -> EmbeddingService:
    """
    Build an ``EmbeddingService`` instance using factory configuration.
    """
    try:
        embedding_provider = create_embedding_provider(
            provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            device=device,
        )
    except ImportError as exc:
        logger.warning(
            "embedding_provider_import_failed",
            provider=provider,
            error=str(exc),
        )
        embedding_provider = InMemoryEmbeddings()
    return EmbeddingService(
        provider=embedding_provider,
        cache=cache,
        batch_size=batch_size,
    )
