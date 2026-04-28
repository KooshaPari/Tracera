"""
Lightweight logging bootstrap utilities.
"""

from __future__ import annotations

import logging
import os

try:  # pragma: no cover - optional dependency
    from pythonjsonlogger.json import JsonFormatter  # type: ignore

    _HAS_JSON = True
except ImportError:  # pragma: no cover
    # Fallback for older versions
    try:
        from pythonjsonlogger import jsonlogger  # type: ignore

        _HAS_JSON = True
    except ImportError:
        _HAS_JSON = False
except Exception:  # pragma: no cover
    _HAS_JSON = False


def configure_logging(level: str = "INFO", json: bool | None = None) -> None:
    """
    Configure root logging with optional JSON output.
    """
    use_json = bool(int(os.getenv("PHENO_JSON_LOGS", "0"))) if json is None else json
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler()
    if use_json and _HAS_JSON:
        try:
            # Try new import first
            formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        except NameError:
            # Fallback to old import
            formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger with the given name.
    """
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
