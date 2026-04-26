"""Value objects - immutable types."""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UUID:
    """UUID value object."""

    value: UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Pagination:
    """Pagination value object."""

    page: int = 1
    page_size: int = 20

    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def limit(self) -> int:
        return min(self.page_size, 100)  # Max 100
