"""
Dataclasses holding memory optimisation state.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MemoryStats:
    """
    Snapshot of memory usage information.
    """

    rss_mb: float = 0.0
    vms_mb: float = 0.0
    percent: float = 0.0
    total_mb: float = 0.0
    available_mb: float = 0.0
    used_mb: float = 0.0
    gc_collections: dict[int, int] = field(default_factory=dict)
    gc_collected: dict[int, int] = field(default_factory=dict)
    gc_uncollectable: dict[int, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CompressionResult:
    """
    Outcome of a compression operation.
    """

    compressed_data: bytes
    original_size: int
    compressed_size: int
    compression_ratio: float
    encoding: str = "utf-8"
    algorithm: str = "gzip"

    def decompress(self) -> str:
        """
        Restore the original text.
        """
        from gzip import decompress as gzip_decompress
        from zlib import decompress as zlib_decompress

        if self.algorithm == "gzip":
            return gzip_decompress(self.compressed_data).decode(self.encoding)
        if self.algorithm == "zlib":
            return zlib_decompress(self.compressed_data).decode(self.encoding)
        raise ValueError(f"Unsupported compression algorithm: {self.algorithm}")
