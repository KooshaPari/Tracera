"""
Streaming helpers for large file operations.
"""

from __future__ import annotations

import logging
import mmap
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


class LargeFileHandler:
    """
    Read large files without exhausting memory.
    """

    @staticmethod
    def read_file_chunked(file_path: str, chunk_size: int = 8192) -> Generator[str, None, None]:
        """
        Yield file contents chunk by chunk.
        """
        try:
            with open(file_path, encoding="utf-8") as handle:
                while True:
                    chunk = handle.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as exc:
            logger.exception("Error reading file %s: %s", file_path, exc)
            raise

    @staticmethod
    def read_file_mmap(file_path: str) -> str:
        """
        Read a file via memory mapping with a plain read fallback.
        """
        try:
            with open(file_path, encoding="utf-8") as handle:
                with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    return mm.read().decode("utf-8")
        except Exception as exc:
            logger.exception("Error reading file with mmap %s: %s", file_path, exc)
            with open(file_path, encoding="utf-8") as handle:
                return handle.read()

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        Return file size in megabytes.
        """
        try:
            return os.path.getsize(file_path) / 1024 / 1024
        except Exception:
            return 0.0

    @staticmethod
    def should_use_streaming(file_path: str, size_threshold_mb: float = 10.0) -> bool:
        """
        Decide if the file should be read via streaming.
        """
        return LargeFileHandler.get_file_size_mb(file_path) > size_threshold_mb
