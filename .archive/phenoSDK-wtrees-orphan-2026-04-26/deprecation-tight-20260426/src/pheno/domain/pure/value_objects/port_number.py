from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortNumber:
    """
    Immutable value object that guarantees port numbers stay within
    the valid TCP/UDP range.
    """

    value: int

    MIN_PORT: int = 1
    MAX_PORT: int = 65535

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError("PortNumber expects an integer")
        if not self.MIN_PORT <= self.value <= self.MAX_PORT:
            raise ValueError(
                f"Port number {self.value} must be between "
                f"{self.MIN_PORT} and {self.MAX_PORT}",
            )

    def __int__(self) -> int:  # pragma: no cover - trivial
        return self.value

    def __str__(self) -> str:  # pragma: no cover - trivial
        return str(self.value)
