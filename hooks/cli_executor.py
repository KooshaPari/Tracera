"""
CLI Executor - Execute CLI commands with routing

Executes CLI commands with semantic routing information.
"""

import logging
import subprocess
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of CLI execution"""
    route: str
    cli_command: str
    exit_code: int
    stdout: str
    stderr: str
    success: bool


class CLIExecutor:
    """
    Execute CLI commands with semantic routing.
    
    Supports:
    - cursor-agent
    - claude
    - auggie
    - droid
    """
    
    def __init__(self):
        """Initialize CLI executor"""
        logger.info("CLIExecutor initialized")
    
    async def execute(
        self,
        route: str,
        cli_command: str,
        tools: List[str],
        prompt: str,
        **kwargs,
    ) -> ExecutionResult:
        """
        Execute CLI command with routing.
        
        Args:
            route: Selected route
            cli_command: CLI command to execute
            tools: Tools for this route
            prompt: User prompt
            **kwargs: Additional arguments
        
        Returns:
            ExecutionResult
        """
        try:
            # Build command
            cmd = [
                cli_command.split()[0],  # CLI tool name
                cli_command.split()[1] if len(cli_command.split()) > 1 else "",
                "--route", route,
                "--tools", ",".join(tools),
                "--prompt", prompt,
            ]
            
            # Remove empty strings
            cmd = [c for c in cmd if c]
            
            logger.info(f"Executing: {' '.join(cmd)}")
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            execution_result = ExecutionResult(
                route=route,
                cli_command=cli_command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                success=success,
            )
            
            if success:
                logger.info(f"CLI execution successful: {cli_command}")
            else:
                logger.error(f"CLI execution failed: {result.stderr}")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"CLI execution timeout: {cli_command}")
            return ExecutionResult(
                route=route,
                cli_command=cli_command,
                exit_code=-1,
                stdout="",
                stderr="Execution timeout",
                success=False,
            )
        except Exception as e:
            logger.error(f"CLI execution failed: {e}")
            return ExecutionResult(
                route=route,
                cli_command=cli_command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                success=False,
            )


async def execute_cli_command(
    route: str,
    cli_command: str,
    tools: List[str],
    prompt: str,
    **kwargs,
) -> ExecutionResult:
    """
    Standalone CLI execution function.
    
    Args:
        route: Selected route
        cli_command: CLI command
        tools: Tools for route
        prompt: User prompt
        **kwargs: Additional arguments
    
    Returns:
        ExecutionResult
    """
    executor = CLIExecutor()
    return await executor.execute(route, cli_command, tools, prompt, **kwargs)

