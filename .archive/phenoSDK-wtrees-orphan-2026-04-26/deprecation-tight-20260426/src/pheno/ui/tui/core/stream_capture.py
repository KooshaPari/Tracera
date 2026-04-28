"""
Compatibility wrapper exposing the stream capture toolkit.
"""

from .stream_capture import (
    CapturedLine,
    LogLevel,
    OutputFormatter,
    StreamCapture,
    capture_output,
)

__all__ = [
    "CapturedLine",
    "LogLevel",
    "OutputFormatter",
    "StreamCapture",
    "capture_output",
]
