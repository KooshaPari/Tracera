"""Command callback handlers and event processing.

Provides callback mechanisms, event handlers, and result processing for command
execution workflows.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .execution_pipeline import CommandConfig, CommandResult, CommandStatus

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


class CommandValidator(ABC):
    """
    Base class for command validators.
    """

    @abstractmethod
    def validate(self, command: str | list[str], config: CommandConfig) -> None:
        """Validate command before execution.

        Args:
            command: Command to validate
            config: Command configuration

        Raises:
            ValueError: If command is invalid
        """

    @abstractmethod
    def validate_result(self, result: CommandResult) -> None:
        """Validate command result after execution.

        Args:
            result: Command execution result

        Raises:
            ValueError: If result is invalid
        """


class CommandCallback(ABC):
    """
    Base class for command execution callbacks.
    """

    @abstractmethod
    async def on_pre_execute(
        self, command: str | list[str], config: CommandConfig, process_id: str,
    ) -> None:
        """Called before command execution.

        Args:
            command: Command to be executed
            config: Command configuration
            process_id: Process identifier
        """

    @abstractmethod
    async def on_post_execute(
        self,
        result: CommandResult,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """Called after command execution.

        Args:
            result: Command execution result
            command: Executed command
            config: Command configuration
            process_id: Process identifier
        """

    @abstractmethod
    async def on_success(
        self,
        result: CommandResult,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """Called on successful command execution.

        Args:
            result: Successful command result
            command: Executed command
            config: Command configuration
            process_id: Process identifier
        """

    @abstractmethod
    async def on_error(
        self,
        result: CommandResult,
        error: Exception,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """Called on command execution error.

        Args:
            result: Error command result
            error: Exception that occurred
            command: Command that failed
            config: Command configuration
            process_id: Process identifier
        """


@dataclass
class ValidationResult:
    """
    Result of command validation.
    """

    is_valid: bool
    errors: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class SecurityValidator(CommandValidator):
    """
    Validates command security and safety.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._dangerous_commands = {
            "rm",
            "rmdir",
            "del",
            "erase",
            "format",
            "dd",
            "mv",
            "cp",
            "chmod",
        }
        self._dangerous_patterns = ["rm -rf", "rm -r", ":(){ :|:& };:", ">", ">>"]

    def validate(self, command: str | list[str], config: CommandConfig) -> None:
        """
        Validate command security.
        """
        command_str = " ".join(command) if isinstance(command, list) else command

        # Check for dangerous commands
        command_parts = command_str.split()
        if command_parts and command_parts[0] in self._dangerous_commands:
            raise ValueError(f"Potentially dangerous command blocked: {command_parts[0]}")

        # Check for dangerous patterns
        for pattern in self._dangerous_patterns:
            if pattern in command_str:
                raise ValueError(f"Potentially dangerous pattern detected: {pattern}")

        self.logger.debug(f"Security validation passed for: {command_str}")

    def validate_result(self, result: CommandResult) -> None:
        """
        Validate result security (no-op for this validator).
        """

    def add_dangerous_command(self, command: str) -> None:
        """
        Add a command to the dangerous commands list.
        """
        self._dangerous_commands.add(command)
        self.logger.info(f"Added dangerous command: {command}")

    def remove_dangerous_command(self, command: str) -> bool:
        """
        Remove a command from the dangerous commands list.
        """
        if command in self._dangerous_commands:
            self._dangerous_commands.remove(command)
            self.logger.info(f"Removed dangerous command: {command}")
            return True
        return False


class OutputValidator(CommandValidator):
    """
    Validates command output and result content.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._max_output_size = 10 * 1024 * 1024  # 10MB
        self._allowed_exit_codes = {0}

    def validate(self, command: str | list[str], config: CommandConfig) -> None:
        """
        Validate command configuration.
        """
        # This validator focuses on result validation

    def validate_result(self, result: CommandResult) -> None:
        """
        Validate command result output.
        """
        # Check exit code
        if result.return_code not in self._allowed_exit_codes:
            raise ValueError(f"Unexpected exit code: {result.return_code}")

        # Check output size
        output_size = len(result.stdout) + len(result.stderr)
        if output_size > self._max_output_size:
            raise ValueError(
                f"Output too large: {output_size} bytes (max: {self._max_output_size})",
            )

        self.logger.debug(f"Output validation passed: {output_size} bytes")

    def set_max_output_size(self, size_bytes: int) -> None:
        """
        Set maximum allowed output size.
        """
        self._max_output_size = size_bytes
        self.logger.info(f"Set max output size to: {size_bytes} bytes")

    def add_allowed_exit_code(self, code: int) -> None:
        """
        Add an allowed exit code.
        """
        self._allowed_exit_codes.add(code)
        self.logger.info(f"Added allowed exit code: {code}")


class LoggingCallback(CommandCallback):
    """
    Logs command execution events.
    """

    def __init__(self, logger_instance: logging.Logger | None = None):
        self.logger = logger_instance or logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def on_pre_execute(
        self, command: str | list[str], config: CommandConfig, process_id: str,
    ) -> None:
        """
        Log pre-execution event.
        """
        command_str = " ".join(command) if isinstance(command, list) else command
        self.logger.info(f"Starting execution: {command_str} (process: {process_id})")

    async def on_post_execute(
        self,
        result: CommandResult,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """
        Log post-execution event.
        """
        command_str = " ".join(command) if isinstance(command, list) else command
        status = result.status.value
        self.logger.info(
            f"Completed execution: {command_str} (process: {process_id}, status: {status}, duration: {result.duration:.2f}s)",
        )

    async def on_success(
        self,
        result: CommandResult,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """
        Log successful execution.
        """
        command_str = " ".join(command) if isinstance(command, list) else command
        self.logger.info(
            f"Success: {command_str} returned {result.return_code} in {result.duration:.2f}s",
        )

    async def on_error(
        self,
        result: CommandResult,
        error: Exception,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """
        Log error execution.
        """
        command_str = " ".join(command) if isinstance(command, list) else command
        self.logger.error(f"Error: {command_str} failed after {result.duration:.2f}s: {error}")


class NotificationCallback(CommandCallback):
    """
    Sends notifications for command events.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._notification_handlers: list[Callable[[str, dict[str, Any]], Awaitable[None]]] = []

    async def on_pre_execute(
        self, command: str | list[str], config: CommandConfig, process_id: str,
    ) -> None:
        """
        Send pre-execution notification.
        """
        await self._send_notification(
            "pre_execute",
            {
                "command": command,
                "process_id": process_id,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    async def on_post_execute(
        self,
        result: CommandResult,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """
        Send post-execution notification.
        """
        await self._send_notification(
            "post_execute",
            {
                "command": command,
                "result": result,
                "process_id": process_id,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    async def on_success(
        self,
        result: CommandResult,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """
        Send success notification.
        """
        await self._send_notification(
            "success",
            {
                "command": command,
                "result": result,
                "process_id": process_id,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    async def on_error(
        self,
        result: CommandResult,
        error: Exception,
        command: str | list[str],
        config: CommandConfig,
        process_id: str,
    ) -> None:
        """
        Send error notification.
        """
        await self._send_notification(
            "error",
            {
                "command": command,
                "error": str(error),
                "result": result,
                "process_id": process_id,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    def add_notification_handler(
        self, handler: Callable[[str, dict[str, Any]], Awaitable[None]],
    ) -> None:
        """
        Add a notification handler.
        """
        self._notification_handlers.append(handler)
        self.logger.info("Added notification handler")

    def remove_notification_handler(
        self, handler: Callable[[str, dict[str, Any]], Awaitable[None]],
    ) -> bool:
        """
        Remove a notification handler.
        """
        if handler in self._notification_handlers:
            self._notification_handlers.remove(handler)
            self.logger.info("Removed notification handler")
            return True
        return False

    async def _send_notification(self, event_type: str, data: dict[str, Any]) -> None:
        """
        Send notification to all handlers.
        """
        for handler in self._notification_handlers:
            try:
                await handler(event_type, data)
            except Exception as e:
                self.logger.exception(f"Notification handler failed: {e}")


class ResultProcessor:
    """
    Processes and transforms command results.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._result_transformers: dict[str, Callable[[CommandResult], Any]] = {}

    def add_result_transformer(
        self, name: str, transformer: Callable[[CommandResult], Any],
    ) -> None:
        """Add a result transformer.

        Args:
            name: Transformer name
            transformer: Function that takes CommandResult and returns transformed data
        """
        self._result_transformers[name] = transformer
        self.logger.info(f"Added result transformer: {name}")

    def remove_result_transformer(self, name: str) -> bool:
        """Remove a result transformer.

        Args:
            name: Transformer name to remove

        Returns:
            True if removed, False if not found
        """
        if name in self._result_transformers:
            del self._result_transformers[name]
            self.logger.info(f"Removed result transformer: {name}")
            return True
        return False

    def process_result(self, result: CommandResult, transformer_name: str) -> Any:
        """Process result using specified transformer.

        Args:
            result: Command result to process
            transformer_name: Name of transformer to use

        Returns:
            Transformed result data

        Raises:
            ValueError: If transformer not found
        """
        if transformer_name not in self._result_transformers:
            raise ValueError(f"Transformer not found: {transformer_name}")

        try:
            transformer = self._result_transformers[transformer_name]
            return transformer(result)
        except Exception as e:
            self.logger.exception(f"Result transformation failed: {e}")
            raise

    def get_available_transformers(self) -> list[str]:
        """Get list of available transformer names.

        Returns:
            List of transformer names
        """
        return list(self._result_transformers.keys())

    # Built-in transformers
    def _transform_to_summary(self, result: CommandResult) -> dict[str, Any]:
        """
        Transform result to summary format.
        """
        return {
            "status": result.status.value,
            "return_code": result.return_code,
            "duration": result.duration,
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr),
            "has_output": bool(result.stdout or result.stderr),
            "success": result.status == CommandStatus.COMPLETED,
        }

    def _transform_to_error_only(self, result: CommandResult) -> str | None:
        """
        Transform result to error output only.
        """
        return result.stderr if result.stderr else None

    def _transform_to_stdout_only(self, result: CommandResult) -> str | None:
        """
        Transform result to stdout only.
        """
        return result.stdout if result.stdout else None

    def setup_default_transformers(self) -> None:
        """
        Set up default result transformers.
        """
        self.add_result_transformer("summary", self._transform_to_summary)
        self.add_result_transformer("errors_only", self._transform_to_error_only)
        self.add_result_transformer("output_only", self._transform_to_stdout_only)
        self.logger.info("Set up default result transformers")
