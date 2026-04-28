"""
Callback abstractions and implementations for the command engine.
"""

from .base import CallbackEvent, CompletionCallback, ProgressCallback
from .composite import CompositeCallback
from .console import ConsoleProgressCallback
from .factory import (
    create_console_callback,
    create_file_callback,
    create_logging_callback,
    create_rich_callback,
)
from .file import FileCallback
from .logging import LoggingCallback
from .manager import CallbackManager
from .rich_callback import RichProgressCallback

__all__ = [
    "CallbackEvent",
    "CallbackManager",
    "CompletionCallback",
    "CompositeCallback",
    "ConsoleProgressCallback",
    "FileCallback",
    "LoggingCallback",
    "ProgressCallback",
    "RichProgressCallback",
    "create_console_callback",
    "create_file_callback",
    "create_logging_callback",
    "create_rich_callback",
]
