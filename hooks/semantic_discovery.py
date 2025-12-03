"""
Semantic Discovery Hook - Pre-discovery routing

Automatically routes based on action and prompt before CLI execution.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryResult:
    """Result of semantic discovery"""
    route: str
    tools: list
    cli_command: str
    hooks: list
    confidence: float
    action: str
    prompt: str


class SemanticDiscoveryHook:
    """
    Pre-discovery hook for semantic routing.
    
    Captures action/prompt and routes to appropriate tools before execution.
    """
    
    def __init__(self, router, registry):
        """
        Initialize hook.
        
        Args:
            router: ArchRouter instance
            registry: ToolRegistry instance
        """
        self.router = router
        self.registry = registry
        logger.info("SemanticDiscoveryHook initialized")
    
    async def execute(
        self,
        action: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DiscoveryResult:
        """
        Execute pre-discovery hook.
        
        Args:
            action: User action (e.g., "generate", "test", "process")
            prompt: User prompt/query
            context: Additional context
        
        Returns:
            DiscoveryResult with routing information
        """
        try:
            # Combine action and prompt for routing
            query = f"{action}: {prompt}"
            
            logger.debug(f"Pre-discovery: action='{action}', prompt='{prompt}'")
            
            # Get available routes
            routes = self.registry.export_registry()
            
            # Route using Arch Router
            routing_result = self.router.route(query, routes)
            
            route = routing_result.route
            route_info = self.registry.get_route(route)
            
            if not route_info:
                logger.warning(f"Route not found: {route}")
                raise ValueError(f"Invalid route: {route}")
            
            result = DiscoveryResult(
                route=route,
                tools=route_info.get("tools", []),
                cli_command=route_info.get("cli_command", ""),
                hooks=route_info.get("hooks", []),
                confidence=routing_result.confidence,
                action=action,
                prompt=prompt,
            )
            
            logger.info(
                f"Discovery complete: route={route}, "
                f"tools={result.tools}, confidence={result.confidence}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Pre-discovery failed: {e}")
            raise


async def pre_discovery_hook(
    action: str,
    prompt: str,
    router,
    registry,
    context: Optional[Dict[str, Any]] = None,
) -> DiscoveryResult:
    """
    Standalone pre-discovery hook function.
    
    Args:
        action: User action
        prompt: User prompt
        router: ArchRouter instance
        registry: ToolRegistry instance
        context: Additional context
    
    Returns:
        DiscoveryResult
    """
    hook = SemanticDiscoveryHook(router, registry)
    return await hook.execute(action, prompt, context)

