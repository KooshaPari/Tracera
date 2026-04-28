"""Unified Command Engine.

Extracts common functionality from command frameworks into reusable services:
- Subprocess orchestration
- Environment handling
- Validator hooks
- Command execution
- Error handling
- Output formatting
"""

from __future__ import annotations

import logging
from pathlib import Path

from .callback_handlers import (
    CommandCallback,
    CommandValidator,
    LoggingCallback,
    NotificationCallback,
    OutputValidator,
    ResultProcessor,
    SecurityValidator,
)
from .execution_pipeline import (
    CommandConfig,
    CommandResult,
    CommandStatus,
    ExecutionPipeline,
    OutputFormat,
    ProcessManager,
)

# Re-export components from new modules
from .parser import CommandComposer, CommandParser, ParsedCommand

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """
    Manages environment variables and system configuration.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._env_cache: dict[str, str] = {}
        self._path_cache: list[Path] | None = None

    def get_env(self, key: str, default: str | None = None) -> str | None:
        """
        Get environment variable with caching.
        """
        if key not in self._env_cache:
            import os

            self._env_cache[key] = os.environ.get(key, default)
        return self._env_cache[key]

    def set_env(self, key: str, value: str) -> None:
        """
        Set environment variable.
        """
        import os

        os.environ[key] = value
        self._env_cache[key] = value

    def get_path(self) -> list[Path]:
        """
        Get PATH as list of Path objects with caching.
        """
        if self._path_cache is None:
            import os

            path_str = os.environ.get("PATH", "")
            self._path_cache = [Path(p) for p in path_str.split(os.pathsep) if p]
        return self._path_cache

    def add_to_path(self, path: str | Path) -> None:
        """
        Add path to PATH environment variable.
        """
        import os

        path = Path(path).resolve()
        current_path = os.environ.get("PATH", "")
        if str(path) not in current_path:
            os.environ["PATH"] = f"{path}{os.pathsep}{current_path}"
            self._path_cache = None  # Invalidate cache

    def get_python_path(self) -> Path | None:
        """
        Get Python executable path.
        """
        import shutil

        python_path = shutil.which("python3") or shutil.which("python")
        return Path(python_path) if python_path else None

    def get_pheno_sdk_path(self) -> Path | None:
        """
        Get pheno-sdk installation path.
        """
        try:
            import pheno

            return Path(pheno.__file__).parent.parent
        except ImportError:
            return None

    def setup_development_environment(self) -> None:
        """
        Set up development environment.
        """
        # Add pheno-sdk to PATH if in development
        pheno_path = self.get_pheno_sdk_path()
        if pheno_path and (pheno_path / "src").exists():
            self.add_to_path(pheno_path / "src")
            self.logger.info(f"Added pheno-sdk development path: {pheno_path / 'src'}")


class CommandEngine:
    """
    Unified command execution engine.
    """

    def __init__(
        self,
        env_manager: EnvironmentManager | None = None,
        pipeline: ExecutionPipeline | None = None,
    ):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.env_manager = env_manager or EnvironmentManager()
        self.pipeline = pipeline or ExecutionPipeline()
        self.parser = CommandParser()
        self.composer = CommandComposer()
        self.process_manager = ProcessManager()
        self.result_processor = ResultProcessor()
        self.result_processor.setup_default_transformers()

        # Set up default validators
        self.security_validator = SecurityValidator()
        self.output_validator = OutputValidator()
        self.validators: list[CommandValidator] = [self.security_validator, self.output_validator]

        # Set up default callbacks
        self.logging_callback = LoggingCallback()
        self.notification_callback = NotificationCallback()
        self.callbacks: list[CommandCallback] = [self.logging_callback]

    def add_validator(self, validator: CommandValidator) -> None:
        """
        Add a command validator.
        """
        self.validators.append(validator)

    def add_callback(self, callback: CommandCallback) -> None:
        """
        Add a command callback.
        """
        self.callbacks.append(callback)

    async def execute(
        self,
        command: str | list[str],
        config: CommandConfig | None = None,
        process_id: str | None = None,
    ) -> CommandResult:
        """
        Execute a command with full orchestration.
        """
        config = config or CommandConfig()

        try:
            # Prepare command for execution
            prepared_command = self._prepare_command(command)

            # Validate command
            self._validate_command(prepared_command, config)

            # Setup callbacks
            self._setup_callbacks()

            # Execute command
            result = await self.pipeline.execute_command(prepared_command, config, process_id)

            # Validate result if needed
            self._validate_result(result, config)

            return result

        except Exception as e:
            return self._handle_execution_error(command, e)

    def _prepare_command(self, command: str | list[str]) -> list[str]:
        """
        Prepare command for execution by parsing if needed.
        """
        if isinstance(command, str):
            parsed = self.parser.parse_command_string(command)
            return [parsed.command, *parsed.args]
        return command

    def _validate_command(self, command: list[str], config: CommandConfig) -> None:
        """
        Validate command using all validators.
        """
        for validator in self.validators:
            validator.validate(command, config)

    def _setup_callbacks(self) -> None:
        """
        Setup callbacks in the pipeline.
        """
        for callback in self.callbacks:
            self.pipeline.add_hook("pre_execute", callback.on_pre_execute)
            self.pipeline.add_hook("post_execute", callback.on_post_execute)
            self.pipeline.add_hook("on_success", callback.on_success)
            self.pipeline.add_hook("on_error", callback.on_error)

    def _validate_result(self, result: CommandResult, config: CommandConfig) -> None:
        """
        Validate command result if output validation is enabled.
        """
        if config.validate_output:
            for validator in self.validators:
                validator.validate_result(result)

    def _handle_execution_error(
        self, command: str | list[str], error: Exception,
    ) -> CommandResult:
        """
        Handle execution errors and return error result.
        """
        self.logger.error(f"Command execution failed: {error}")

        return CommandResult(
            status=CommandStatus.FAILED,
            return_code=1,
            error=error,
            metadata={
                "command": command,
                "error": str(error),
            },
        )

    async def execute_with_retry(
        self,
        command: str | list[str],
        config: CommandConfig | None = None,
        process_id: str | None = None,
    ) -> CommandResult:
        """
        Execute command with retry logic.
        """
        config = config or CommandConfig()

        # Add callbacks to pipeline
        for callback in self.callbacks:
            self.pipeline.add_hook("pre_execute", callback.on_pre_execute)
            self.pipeline.add_hook("post_execute", callback.on_post_execute)
            self.pipeline.add_hook("on_success", callback.on_success)
            self.pipeline.add_hook("on_error", callback.on_error)

        return await self.pipeline.execute_with_retry(command, config, process_id)


# Global command engine instance
_command_engine: CommandEngine | None = None


def get_command_engine() -> CommandEngine:
    """
    Get the global command engine instance.
    """
    global _command_engine
    if _command_engine is None:
        _command_engine = CommandEngine()
    return _command_engine


# Convenience functions
async def execute_command(
    command: str | list[str],
    config: CommandConfig | None = None,
    process_id: str | None = None,
) -> CommandResult:
    """
    Execute a command using the global command engine.
    """
    engine = get_command_engine()
    return await engine.execute(command, config, process_id)


async def execute_command_with_retry(
    command: str | list[str],
    config: CommandConfig | None = None,
    process_id: str | None = None,
) -> CommandResult:
    """
    Execute a command with retry using the global command engine.
    """
    engine = get_command_engine()
    return await engine.execute_with_retry(command, config, process_id)


# Export all public classes and functions
__all__ = [
    "CommandCallback",
    "CommandComposer",
    "CommandConfig",
    # Core classes
    "CommandEngine",
    # Parser components
    "CommandParser",
    "CommandResult",
    "CommandStatus",
    "CommandValidator",
    "EnvironmentManager",
    "ExecutionPipeline",
    # Callbacks
    "LoggingCallback",
    "NotificationCallback",
    "OutputFormat",
    "OutputValidator",
    "ParsedCommand",
    "ProcessManager",
    # Result processing
    "ResultProcessor",
    # Validators
    "SecurityValidator",
    # Convenience functions
    "execute_command",
    "execute_command_with_retry",
    # Global engine accessor
    "get_command_engine",
]
