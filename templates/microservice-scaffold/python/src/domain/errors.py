"""Domain errors - explicit error handling."""

class DomainError(Exception):
    """Base domain error."""

    def __init__(self, message: str, code: str, field: str | None = None):
        super().__init__(message)
        self.code = code
        self.field = field


class NotFoundError(DomainError):
    """Entity not found."""

    def __init__(self, entity_id: str):
        super().__init__(
            message=f"Entity not found: {entity_id}",
            code="NOT_FOUND",
            field="id",
        )


class ValidationError(DomainError):
    """Validation error."""

    def __init__(self, field: str, message: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            field=field,
        )


class ConcurrencyError(DomainError):
    """Concurrency conflict."""

    def __init__(self, message: str = "Concurrency conflict detected"):
        super().__init__(
            message=message,
            code="CONCURRENCY_ERROR",
        )
