"""UUID generation utilities for Phenotype services.

Provides methods for generating unique identifiers with optional prefixes
for different use cases.
"""

import uuid


class Generator:
    """Generator provides methods for generating unique identifiers."""

    @staticmethod
    def generate_uuid() -> str:
        """Generate a new random UUID v4.

        Returns:
            String representation of a UUID v4
        """
        return str(uuid.uuid4())

    @staticmethod
    def generate_request_id() -> str:
        """Generate a new request ID using UUID v4.

        Returns:
            Request ID with 'req-' prefix
        """
        return f"req-{uuid.uuid4()}"

    @staticmethod
    def generate_trace_id() -> str:
        """Generate a new trace ID using UUID v4.

        Returns:
            Trace ID with 'trace-' prefix
        """
        return f"trace-{uuid.uuid4()}"

    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a new correlation ID using UUID v4.

        Returns:
            Correlation ID with 'corr-' prefix
        """
        return f"corr-{uuid.uuid4()}"

    @staticmethod
    def is_valid_uuid(id_str: str) -> bool:
        """Check if the given string is a valid UUID.

        Args:
            id_str: String to validate

        Returns:
            True if valid UUID, False otherwise
        """
        try:
            uuid.UUID(id_str)
            return True
        except (ValueError, AttributeError):
            return False
