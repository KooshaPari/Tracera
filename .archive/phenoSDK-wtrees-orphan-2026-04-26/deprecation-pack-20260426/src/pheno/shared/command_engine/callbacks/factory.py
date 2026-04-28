"""
Factory helpers for command engine callbacks.
"""

from __future__ import annotations

from .console import ConsoleProgressCallback
from .file import FileCallback
from .logging import LoggingCallback
from .rich_callback import RichProgressCallback


# Convenience functions
def create_console_callback(verbose: bool = False) -> ConsoleProgressCallback:
    """Factory for :class:`ConsoleProgressCallback`.

    Args:
        verbose: When ``True`` emit intermediate log lines.

    Returns:
        Configured :class:`ConsoleProgressCallback` instance.
    """
    return ConsoleProgressCallback(verbose=verbose)


def create_rich_callback(console=None) -> RichProgressCallback:
    """Factory for :class:`RichProgressCallback`.

    Args:
        console: Optional Rich ``Console`` instance to reuse.

    Returns:
        Configured :class:`RichProgressCallback` instance.
    """
    return RichProgressCallback(console=console)


def create_logging_callback(logger_name: str = "command_engine") -> LoggingCallback:
    """Factory for :class:`LoggingCallback`.

    Args:
        logger_name: Name passed to ``logging.getLogger``.

    Returns:
        Configured :class:`LoggingCallback` instance.
    """
    return LoggingCallback(logger_name=logger_name)


def create_file_callback(log_file: str) -> FileCallback:
    """Factory for :class:`FileCallback`.

    Args:
        log_file: Path to the log file.

    Returns:
        Configured :class:`FileCallback` instance.
    """
    return FileCallback(log_file=log_file)
