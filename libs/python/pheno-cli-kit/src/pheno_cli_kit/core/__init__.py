"""CLI Kit core components.

Provides command definitions, builders, and decorators for CLI construction.
"""

from .builder import CLIBuilder
from .command import Argument, ArgumentDefinition, ArgumentType, Command, CommandDefinition, Option
from .decorators import (
    Argument,
    Command,
    CommandRegistry,
    Option,
    argument,
    cli_command,
    cli_group,
    command,
    get_registry,
    group,
    option,
    reset_registry,
)

__all__ = [
    # Builder
    "CLIBuilder",
    # Command definitions
    "Argument",
    "Option",
    "Command",
    "ArgumentType",
    # Aliases
    "ArgumentDefinition",
    "CommandDefinition",
    # Decorators
    "cli_command",
    "cli_group",
    "command",
    "argument",
    "option",
    "group",
    "CommandRegistry",
    "get_registry",
    "reset_registry",
]
