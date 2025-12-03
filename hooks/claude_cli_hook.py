"""
Claude CLI Hook - Integration with Claude command-line interface

Provides pre-discovery and post-selection hooks for Claude CLI.
"""

import logging
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ClaudeCliContext:
    """Claude CLI execution context"""
    command: str
    args: list
    input_text: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None


class ClaudeCliHook:
    """
    Claude CLI integration hook.
    
    Supports:
    - Code generation
    - API development
    - Documentation
    - Analysis
    """
    
    def __init__(self, router, registry, search_service):
        """
        Initialize Claude CLI hook.
        
        Args:
            router: ArchRouter instance
            registry: ToolRegistry instance
            search_service: SearchService instance
        """
        self.router = router
        self.registry = registry
        self.search_service = search_service
        
        logger.info("ClaudeCliHook initialized")
    
    async def pre_discovery(
        self,
        context: ClaudeCliContext,
    ) -> Dict[str, Any]:
        """
        Pre-discovery hook for Claude CLI.
        
        Args:
            context: Claude CLI context
        
        Returns:
            Discovery result with routing information
        """
        try:
            logger.debug(f"Claude pre-discovery: command={context.command}")
            
            # Build query from context
            query = f"{context.command}: {' '.join(context.args)}"
            if context.input_text:
                query += f" (input: {context.input_text[:100]})"
            
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
                "command": context.command,
                "args": context.args,
                "model": context.model,
            }
            
            logger.info(f"Claude discovery: route={result['route']}")
            return result
            
        except Exception as e:
            logger.error(f"Claude pre-discovery failed: {e}")
            raise
    
    async def post_selection(
        self,
        context: ClaudeCliContext,
        route: str,
        tools: list,
    ) -> Dict[str, Any]:
        """
        Post-selection hook for Claude CLI.
        
        Args:
            context: Claude CLI context
            route: Selected route
            tools: Selected tools
        
        Returns:
            Post-selection result
        """
        try:
            logger.debug(f"Claude post-selection: route={route}")
            
            result = {
                "route": route,
                "tools": tools,
                "command": context.command,
                "args": context.args,
                "model": context.model or "claude-3-sonnet",
                "temperature": context.temperature or 0.7,
                "status": "ready",
            }
            
            logger.info(f"Claude post-selection: {json.dumps(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Claude post-selection failed: {e}")
            raise
    
    async def on_completion(
        self,
        context: ClaudeCliContext,
        route: str,
        result: str,
        success: bool,
    ) -> Dict[str, Any]:
        """
        Completion hook for Claude CLI.
        
        Args:
            context: Claude CLI context
            route: Used route
            result: Execution result
            success: Whether execution was successful
        
        Returns:
            Completion result
        """
        try:
            logger.debug(f"Claude completion: route={route}, success={success}")
            
            completion_result = {
                "route": route,
                "command": context.command,
                "success": success,
                "result_length": len(result) if result else 0,
            }
            
            logger.info(f"Claude completion: {json.dumps(completion_result)}")
            return completion_result
            
        except Exception as e:
            logger.error(f"Claude completion failed: {e}")
            raise


async def claude_cli_pre_discovery(
    command: str,
    args: list,
    router,
    registry,
    search_service,
    input_text: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Standalone Claude CLI pre-discovery hook.
    
    Args:
        command: CLI command
        args: Command arguments
        router: ArchRouter instance
        registry: ToolRegistry instance
        search_service: SearchService instance
        input_text: Input text
        model: Model name
        temperature: Temperature
    
    Returns:
        Discovery result
    """
    context = ClaudeCliContext(
        command=command,
        args=args,
        input_text=input_text,
        model=model,
        temperature=temperature,
    )
    
    hook = ClaudeCliHook(router, registry, search_service)
    return await hook.pre_discovery(context)

