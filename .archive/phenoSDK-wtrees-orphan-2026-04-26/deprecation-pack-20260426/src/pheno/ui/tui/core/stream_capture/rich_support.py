"""
Shared Rich imports for stream capture utilities.
"""

try:  # pragma: no cover - optional dependency
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.text import Text

    HAS_RICH = True
except ImportError:  # pragma: no cover - optional dependency
    Console = object  # type: ignore[misc,assignment]
    Syntax = object  # type: ignore[misc,assignment]
    Text = object  # type: ignore[misc,assignment]
    HAS_RICH = False


__all__ = ["HAS_RICH", "Console", "Syntax", "Text"]
