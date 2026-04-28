"""Resource Provider Port.

Defines the protocol for MCP resource access and scheme handling. Supports URI-based
resource access (e.g., config://, db://, storage://).
"""

from typing import Any, Protocol


class ResourceSchemeHandler(Protocol):
    """Protocol for handling a specific resource URI scheme.

    Each scheme (config://, db://, storage://, etc.) has a handler
    that knows how to resolve resources for that scheme.

    Example:
        >>> handler = DbSchemeHandler()
        >>> resource = await handler.get_resource("db://users/123")
        >>> resources = await handler.list_resources("db://users")
    """

    async def get_resource(self, uri: str) -> Any:
        """Get a resource by URI.

        Args:
            uri: Resource URI (e.g., "db://users/123")

        Returns:
            Resource data

        Raises:
            ResourceNotFoundError: If resource doesn't exist

        Example:
            >>> user = await handler.get_resource("db://users/123")
        """
        ...

    async def list_resources(self, uri: str) -> list[str]:
        """List resources matching a URI pattern.

        Args:
            uri: URI pattern (e.g., "db://users")

        Returns:
            List of resource URIs

        Example:
            >>> uris = await handler.list_resources("db://users")
            >>> # ["db://users/1", "db://users/2", ...]
        """
        ...

    def supports_scheme(self, scheme: str) -> bool:
        """Check if this handler supports a scheme.

        Args:
            scheme: Scheme name (e.g., "db")

        Returns:
            True if supported

        Example:
            >>> handler.supports_scheme("db")  # True
        """
        ...


class ResourceProvider(Protocol):
    """Protocol for MCP resource access and management.

    Provides unified access to resources across different schemes.
    Manages scheme handlers and routes requests to appropriate handlers.

    Example:
        >>> provider = get_resource_provider()
        >>>
        >>> # Register scheme handlers
        >>> provider.register_scheme("db", DbSchemeHandler())
        >>> provider.register_scheme("storage", StorageSchemeHandler())
        >>>
        >>> # Access resources via URIs
        >>> user = await provider.get_resource("db://users/123")
        >>> file = await provider.get_resource("storage://s3/bucket/file.txt")
    """

    async def get_resource(self, uri: str) -> Any:
        """Get a resource by URI.

        Automatically routes to the appropriate scheme handler.

        Args:
            uri: Resource URI with scheme (e.g., "db://users/123")

        Returns:
            Resource data

        Raises:
            UnsupportedSchemeError: If scheme not registered
            ResourceNotFoundError: If resource doesn't exist

        Example:
            >>> config = await provider.get_resource("config://app/database")
            >>> logs = await provider.get_resource("logs://app/errors?limit=100")
        """
        ...

    async def list_resources(self, pattern: str) -> list[str]:
        """List resources matching a pattern.

        Args:
            pattern: URI pattern (e.g., "db://users/*")

        Returns:
            List of matching resource URIs

        Example:
            >>> uris = await provider.list_resources("db://users/*")
        """
        ...

    def register_scheme(self, scheme: str, handler: ResourceSchemeHandler) -> None:
        """Register a scheme handler.

        Args:
            scheme: Scheme name (e.g., "db", "storage")
            handler: Handler implementation

        Example:
            >>> provider.register_scheme("db", DbSchemeHandler())
            >>> provider.register_scheme("vector", VectorSchemeHandler())
        """
        ...

    def unregister_scheme(self, scheme: str) -> None:
        """Unregister a scheme handler.

        Args:
            scheme: Scheme name to unregister

        Example:
            >>> provider.unregister_scheme("db")
        """
        ...

    def get_scheme_handler(self, scheme: str) -> ResourceSchemeHandler:
        """Get the handler for a scheme.

        Args:
            scheme: Scheme name

        Returns:
            Scheme handler

        Raises:
            UnsupportedSchemeError: If scheme not registered

        Example:
            >>> handler = provider.get_scheme_handler("db")
        """
        ...

    def list_schemes(self) -> list[str]:
        """List all registered schemes.

        Returns:
            List of scheme names

        Example:
            >>> schemes = provider.list_schemes()
            >>> # ["config", "db", "storage", "vector", ...]
        """
        ...

    async def create_resource(
        self, uri: str, data: Any, metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new resource.

        Args:
            uri: Resource URI
            data: Resource data
            metadata: Optional metadata

        Returns:
            Created resource URI

        Example:
            >>> uri = await provider.create_resource(
            ...     "db://users",
            ...     {"name": "Alice", "email": "alice@example.com"}
            ... )
        """
        ...

    async def update_resource(self, uri: str, data: Any) -> None:
        """Update an existing resource.

        Args:
            uri: Resource URI
            data: Updated data

        Example:
            >>> await provider.update_resource(
            ...     "db://users/123",
            ...     {"email": "newemail@example.com"}
            ... )
        """
        ...

    async def delete_resource(self, uri: str) -> None:
        """Delete a resource.

        Args:
            uri: Resource URI

        Example:
            >>> await provider.delete_resource("db://users/123")
        """
        ...


__all__ = [
    "ResourceProvider",
    "ResourceSchemeHandler",
]
