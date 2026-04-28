"""Command Engine Module.

Provides unified command execution, parsing, and processing capabilities across the
Pheno SDK ecosystem.
"""

# Re-export callback handlers
from .callback_handlers import (
    CommandCallback,
    CommandValidator,
    LoggingCallback,
    NotificationCallback,
    OutputValidator,
    ResultProcessor,
    SecurityValidator,
)

# Re-export execution pipeline
from .execution_pipeline import (
    ExecutionPipeline,
    ProcessManager,
)

# Re-export parser components
from .parser import (
    CommandComposer,
    CommandParser,
    ParsedCommand,
)

# Re-export main unified engine components
from .unified_engine import (
    CommandConfig,
    CommandEngine,
    CommandResult,
    CommandStatus,
    EnvironmentManager,
    OutputFormat,
    execute_command,
    execute_command_with_retry,
    get_command_engine,
)

__all__ = [
    "CommandCallback",
    "CommandComposer",
    "CommandConfig",
    # Unified engine
    "CommandEngine",
    # Parser
    "CommandParser",
    "CommandResult",
    "CommandStatus",
    # Callback handlers
    "CommandValidator",
    "EnvironmentManager",
    # Execution pipeline
    "ExecutionPipeline",
    "LoggingCallback",
    "NotificationCallback",
    "OutputFormat",
    "OutputValidator",
    "ParsedCommand",
    "ProcessManager",
    "ResultProcessor",
    "SecurityValidator",
    "execute_command",
    "execute_command_with_retry",
    "get_command_engine",
]
