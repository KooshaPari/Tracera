"""
Auggie Hook - Integration with Auggie data processing tool

Provides pre-discovery and post-selection hooks for Auggie.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AuggieContext:
    """Auggie execution context"""

    operation: str
    input_file: str
    output_format: str | None = None
    options: dict[str, Any] | None = None


class AuggieHook:
    """
    Auggie integration hook.

    Supports:
    - Data processing
    - Data transformation
    - Data validation
    - Data export
    """

    def __init__(self, router, registry, search_service):
        """
        Initialize Auggie hook.

        Args:
            router: ArchRouter instance
            registry: ToolRegistry instance
            search_service: SearchService instance
        """
        self.router = router
        self.registry = registry
        self.search_service = search_service

        logger.info("AuggieHook initialized")

    async def pre_discovery(
        self,
        context: AuggieContext,
    ) -> dict[str, Any]:
        """
        Pre-discovery hook for Auggie.

        Args:
            context: Auggie context

        Returns:
            Discovery result with routing information
        """
        try:
            logger.debug(f"Auggie pre-discovery: operation={context.operation}")

            # Build query from context
            query = f"{context.operation}: {context.input_file}"
            if context.output_format:
                query += f" to {context.output_format}"

            # Get available routes
            routes = self.registry.export_registry()

            # Route using Arch Router
            routing_result = self.router.route(query, routes)

            result = {
                "route": routing_result.route,
                "tools": self.registry.get_tools(routing_result.route),
                "cli_command": self.registry.get_cli_command(routing_result.route),
                "hooks": self.registry.get_hooks(routing_result.route),
                "confidence": routing_result.confidence,
                "operation": context.operation,
                "input_file": context.input_file,
                "output_format": context.output_format,
            }

            logger.info(f"Auggie discovery: route={result['route']}")
            return result

        except Exception as e:
            logger.error(f"Auggie pre-discovery failed: {e}")
            raise

    async def post_selection(
        self,
        context: AuggieContext,
        route: str,
        tools: list,
    ) -> dict[str, Any]:
        """
        Post-selection hook for Auggie.

        Args:
            context: Auggie context
            route: Selected route
            tools: Selected tools

        Returns:
            Post-selection result
        """
        try:
            logger.debug(f"Auggie post-selection: route={route}")

            result = {
                "route": route,
                "tools": tools,
                "operation": context.operation,
                "input_file": context.input_file,
                "output_format": context.output_format,
                "options": context.options or {},
                "status": "ready",
            }

            logger.info(f"Auggie post-selection: {json.dumps(result)}")
            return result

        except Exception as e:
            logger.error(f"Auggie post-selection failed: {e}")
            raise

    async def on_completion(
        self,
        context: AuggieContext,
        route: str,
        result: str,
        success: bool,
    ) -> dict[str, Any]:
        """
        Completion hook for Auggie.

        Args:
            context: Auggie context
            route: Used route
            result: Execution result
            success: Whether execution was successful

        Returns:
            Completion result
        """
        try:
            logger.debug(f"Auggie completion: route={route}, success={success}")

            completion_result = {
                "route": route,
                "operation": context.operation,
                "success": success,
                "result_length": len(result) if result else 0,
            }

            logger.info(f"Auggie completion: {json.dumps(completion_result)}")
            return completion_result

        except Exception as e:
            logger.error(f"Auggie completion failed: {e}")
            raise


async def auggie_pre_discovery(
    operation: str,
    input_file: str,
    router,
    registry,
    search_service,
    output_format: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Standalone Auggie pre-discovery hook.

    Args:
        operation: Data operation
        input_file: Input file path
        router: ArchRouter instance
        registry: ToolRegistry instance
        search_service: SearchService instance
        output_format: Output format
        options: Additional options

    Returns:
        Discovery result
    """
    context = AuggieContext(
        operation=operation,
        input_file=input_file,
        output_format=output_format,
        options=options,
    )

    hook = AuggieHook(router, registry, search_service)
    return await hook.pre_discovery(context)
