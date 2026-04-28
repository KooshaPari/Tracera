"""
Droid Hook - Integration with Droid testing framework

Provides pre-discovery and post-selection hooks for Droid.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DroidContext:
    """Droid execution context"""

    test_type: str
    target: str
    framework: str | None = None
    coverage: bool | None = None
    verbose: bool | None = None


class DroidHook:
    """
    Droid integration hook.

    Supports:
    - Unit testing
    - Integration testing
    - End-to-end testing
    - Coverage analysis
    """

    def __init__(self, router, registry, search_service):
        """
        Initialize Droid hook.

        Args:
            router: ArchRouter instance
            registry: ToolRegistry instance
            search_service: SearchService instance
        """
        self.router = router
        self.registry = registry
        self.search_service = search_service

        logger.info("DroidHook initialized")

    async def pre_discovery(
        self,
        context: DroidContext,
    ) -> dict[str, Any]:
        """
        Pre-discovery hook for Droid.

        Args:
            context: Droid context

        Returns:
            Discovery result with routing information
        """
        try:
            logger.debug(f"Droid pre-discovery: test_type={context.test_type}")

            # Build query from context
            query = f"{context.test_type} test: {context.target}"
            if context.framework:
                query += f" ({context.framework})"

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
                "test_type": context.test_type,
                "target": context.target,
                "framework": context.framework,
            }

            logger.info(f"Droid discovery: route={result['route']}")
            return result

        except Exception as e:
            logger.error(f"Droid pre-discovery failed: {e}")
            raise

    async def post_selection(
        self,
        context: DroidContext,
        route: str,
        tools: list,
    ) -> dict[str, Any]:
        """
        Post-selection hook for Droid.

        Args:
            context: Droid context
            route: Selected route
            tools: Selected tools

        Returns:
            Post-selection result
        """
        try:
            logger.debug(f"Droid post-selection: route={route}")

            result = {
                "route": route,
                "tools": tools,
                "test_type": context.test_type,
                "target": context.target,
                "framework": context.framework or "pytest",
                "coverage": context.coverage or False,
                "verbose": context.verbose or False,
                "status": "ready",
            }

            logger.info(f"Droid post-selection: {json.dumps(result)}")
            return result

        except Exception as e:
            logger.error(f"Droid post-selection failed: {e}")
            raise

    async def on_completion(
        self,
        context: DroidContext,
        route: str,
        result: str,
        success: bool,
    ) -> dict[str, Any]:
        """
        Completion hook for Droid.

        Args:
            context: Droid context
            route: Used route
            result: Execution result
            success: Whether execution was successful

        Returns:
            Completion result
        """
        try:
            logger.debug(f"Droid completion: route={route}, success={success}")

            completion_result = {
                "route": route,
                "test_type": context.test_type,
                "success": success,
                "result_length": len(result) if result else 0,
            }

            logger.info(f"Droid completion: {json.dumps(completion_result)}")
            return completion_result

        except Exception as e:
            logger.error(f"Droid completion failed: {e}")
            raise


async def droid_pre_discovery(
    test_type: str,
    target: str,
    router,
    registry,
    search_service,
    framework: str | None = None,
    coverage: bool | None = None,
    verbose: bool | None = None,
) -> dict[str, Any]:
    """
    Standalone Droid pre-discovery hook.

    Args:
        test_type: Type of test (unit, integration, e2e)
        target: Test target
        router: ArchRouter instance
        registry: ToolRegistry instance
        search_service: SearchService instance
        framework: Testing framework
        coverage: Enable coverage
        verbose: Verbose output

    Returns:
        Discovery result
    """
    context = DroidContext(
        test_type=test_type,
        target=target,
        framework=framework,
        coverage=coverage,
        verbose=verbose,
    )

    hook = DroidHook(router, registry, search_service)
    return await hook.pre_discovery(context)
