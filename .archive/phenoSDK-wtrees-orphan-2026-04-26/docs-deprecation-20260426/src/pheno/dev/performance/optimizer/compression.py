"""
Compression and context management helpers.
"""

from __future__ import annotations

import gzip
import hashlib
import threading
import zlib
from typing import Any

from .stats import CompressionResult


class TextCompressor:
    """
    Utility methods for compressing text.
    """

    @staticmethod
    def create_context_id(text: str) -> str:
        """
        Generate a deterministic identifier for a context payload.
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest()[:8]

    @staticmethod
    def compress_text(text: str, algorithm: str = "gzip", level: int = 6) -> CompressionResult:
        """
        Compress text into a `CompressionResult`.
        """
        if not text:
            return CompressionResult(
                compressed_data=b"",
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                algorithm=algorithm,
            )

        payload = text.encode("utf-8")
        original_size = len(payload)

        if algorithm == "gzip":
            compressed_data = gzip.compress(payload, compresslevel=level)
        elif algorithm == "zlib":
            compressed_data = zlib.compress(payload, level)
        else:  # pragma: no cover - defensive validation
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")

        compressed_size = len(compressed_data)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0.0

        return CompressionResult(
            compressed_data=compressed_data,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            algorithm=algorithm,
        )

    @staticmethod
    def should_compress(text: str, min_size: int = 1024, min_ratio: float = 1.2) -> bool:
        """
        Heuristically determine whether compression is worthwhile.
        """
        if len(text) < min_size:
            return False

        sample = text[: min(len(text), 1000)]
        sample_result = TextCompressor.compress_text(sample)
        return sample_result.compression_ratio >= min_ratio


class ContextManager:
    """
    Store and retrieve compressed contexts.
    """

    def __init__(self, max_context_tokens: int = 128_000, compression_threshold: int = 10_000):
        self.max_context_tokens = max_context_tokens
        self.compression_threshold = compression_threshold
        self.compressed_contexts: dict[str, CompressionResult] = {}
        self._lock = threading.RLock()

    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimator (1 token ≈ 4 characters).
        """
        return len(text) // 4

    def chunk_context(self, text: str, max_chunk_tokens: int | None = None) -> list[str]:
        """
        Split large contexts into smaller chunks.
        """
        max_chunk_tokens = max_chunk_tokens or (self.max_context_tokens // 4)
        max_chunk_chars = max_chunk_tokens * 4

        if len(text) <= max_chunk_chars:
            return [text]

        chunks: list[str] = []
        lines = text.split("\n")
        current_chunk: list[str] = []
        current_size = 0

        for line in lines:
            line_size = len(line) + 1  # include newline

            if current_size + line_size > max_chunk_chars and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def compress_context(self, context_id: str, text: str) -> bool:
        """
        Compress and store a context if it exceeds the threshold.
        """
        if len(text) < self.compression_threshold:
            return False

        if TextCompressor.should_compress(text):
            compressed = TextCompressor.compress_text(text)

            with self._lock:
                self.compressed_contexts[context_id] = compressed

            return True

        return False

    def get_context(self, context_id: str) -> str | None:
        """
        Retrieve a previously stored context.
        """
        with self._lock:
            compressed = self.compressed_contexts.get(context_id)

        return compressed.decompress() if compressed else None

    def remove_context(self, context_id: str):
        """
        Remove a context from memory.
        """
        with self._lock:
            self.compressed_contexts.pop(context_id, None)

    def get_memory_usage(self) -> dict[str, Any]:
        """
        Report aggregated memory usage for compressed contexts.
        """
        with self._lock:
            total_original = sum(item.original_size for item in self.compressed_contexts.values())
            total_compressed = sum(
                item.compressed_size for item in self.compressed_contexts.values()
            )
            count = len(self.compressed_contexts)

        return {
            "contexts_count": count,
            "total_original_mb": total_original / 1024 / 1024,
            "total_compressed_mb": total_compressed / 1024 / 1024,
            "memory_saved_mb": (total_original - total_compressed) / 1024 / 1024,
            "average_compression_ratio": (
                total_original / total_compressed if total_compressed > 0 else 0.0
            ),
        }
