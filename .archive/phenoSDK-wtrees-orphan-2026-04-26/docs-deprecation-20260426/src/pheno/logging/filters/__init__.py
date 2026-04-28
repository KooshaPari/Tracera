"""Log filters for pheno-logging.

Filters can be used to:
- Redact sensitive information (PII, passwords, tokens)
- Filter by log level
- Filter by logger name
- Add context to log records
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .security_filter import PIIRedactor, SecurityFilter

__all__ = [
    "PIIRedactor",
    "SecurityFilter",
]


def __getattr__(name: str):
    """
    Lazy import for filters.
    """
    if name in ("SecurityFilter", "PIIRedactor"):
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
