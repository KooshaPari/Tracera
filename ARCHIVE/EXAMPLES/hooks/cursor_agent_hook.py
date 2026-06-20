"""
Cursor Agent Hook - Integration with Cursor IDE agent

Provides pre-discovery and post-selection hooks for Cursor Agent.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CursorAgentContext:
    """Cursor Agent execution context"""

    action: str
    prompt: str
    file_path: str | None = None
    selection: str | None = None
    language: str | None = None


class CursorAgentHook:
    """
    Cursor Agent integration hook.

    Supports:
    - Code generation
    - Code refactoring
    - Test generation
    - Documentation
    """

    def __init__(self, router, registry, search_service):
        """
        Initialize Cursor Agent hook.

        Args:
            router: ArchRouter instance
            registry: ToolRegistry instance
            search_service: SearchService instance
        """
        self.router = router
        self.registry = registry
        self.search_service = search_service

        logger.info("CursorAgentHook initialized")

    async def pre_discovery(
        self,
        context: CursorAgentContext,
    ) -> dict[str, Any]:
        """
        Pre-discovery hook for Cursor Agent.

        Args:
            context: Cursor Agent context

        Returns:
            Discovery result with routing information
        """
        try:
            logger.debug(f"Cursor pre-discovery: action={context.action}")

            # Build query from context
            query = f"{context.action}: {context.prompt}"
            if context.file_path:
                query += f" (file: {context.file_path})"

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
                "action": context.action,
                "prompt": context.prompt,
            }

            logger.info(f"Cursor discovery: route={result['route']}")
            return result

        except Exception as e:
            logger.error(f"Cursor pre-discovery failed: {e}")
            raise

    async def post_selection(
        self,
        context: CursorAgentContext,
        route: str,
        tools: list,
    ) -> dict[str, Any]:
        """
        Post-selection hook for Cursor Agent.

        Args:
            context: Cursor Agent context
            route: Selected route
            tools: Selected tools

        Returns:
            Post-selection result
        """
        try:
            logger.debug(f"Cursor post-selection: route={route}")

            # Log routing decision
            result = {
                "route": route,
                "tools": tools,
                "action": context.action,
                "prompt": context.prompt,
                "file_path": context.file_path,
                "status": "ready",
            }

            logger.info(f"Cursor post-selection: {json.dumps(result)}")
            return result

        except Exception as e:
            logger.error(f"Cursor post-selection failed: {e}")
            raise

    async def on_completion(
        self,
        context: CursorAgentContext,
        route: str,
        result: str,
        success: bool,
    ) -> dict[str, Any]:
        """
        Completion hook for Cursor Agent.

        Args:
            context: Cursor Agent context
            route: Used route
            result: Execution result
            success: Whether execution was successful

        Returns:
            Completion result
        """
        try:
            logger.debug(f"Cursor completion: route={route}, success={success}")

            completion_result = {
                "route": route,
                "action": context.action,
                "success": success,
                "result_length": len(result) if result else 0,
            }

            logger.info(f"Cursor completion: {json.dumps(completion_result)}")
            return completion_result

        except Exception as e:
            logger.error(f"Cursor completion failed: {e}")
            raise


async def cursor_agent_pre_discovery(
    action: str,
    prompt: str,
    router,
    registry,
    search_service,
    file_path: str | None = None,
    selection: str | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    """
    Standalone Cursor Agent pre-discovery hook.

    Args:
        action: User action
        prompt: User prompt
        router: ArchRouter instance
        registry: ToolRegistry instance
        search_service: SearchService instance
        file_path: File path
        selection: Selected text
        language: Programming language

    Returns:
        Discovery result
    """
    context = CursorAgentContext(
        action=action,
        prompt=prompt,
        file_path=file_path,
        selection=selection,
        language=language,
    )

    hook = CursorAgentHook(router, registry, search_service)
    return await hook.pre_discovery(context)
