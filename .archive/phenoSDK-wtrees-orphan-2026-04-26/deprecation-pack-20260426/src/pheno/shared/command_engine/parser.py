"""Command parsing and composition utilities.

Provides command parsing, tokenization, and composition capabilities for unified command
execution.
"""

from __future__ import annotations

import logging
import shlex
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ParsedCommand:
    """
    Result of command parsing.
    """

    command: str
    args: list[str]
    flags: dict[str, str | bool]
    options: dict[str, str | list[str]]
    raw_command: str

    def to_list(self) -> list[str]:
        """
        Convert parsed command back to list format.
        """
        result = [self.command]

        # Add flags
        for flag, value in self.flags.items():
            if isinstance(value, bool) and value:
                result.append(f"--{flag}")
            elif isinstance(value, str):
                result.extend([f"--{flag}", value])

        # Add options
        for option, value in self.options.items():
            if isinstance(value, list):
                result.extend([f"--{option}", *value])
            else:
                result.extend([f"--{option}", str(value)])

        # Add positional arguments
        result.extend(self.args)

        return result

    def to_string(self) -> str:
        """
        Convert parsed command back to string format.
        """
        return " ".join(shlex.quote(str(arg)) for arg in self.to_list())


class CommandParser:
    """
    Parses command strings and lists into structured components.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def parse_command_string(self, command: str) -> ParsedCommand:
        """Parse a command string into structured components.

        Args:
            command: Command string to parse

        Returns:
            ParsedCommand with structured components
        """
        try:
            parts = shlex.split(command)
            return self.parse_command_list(parts)
        except Exception as e:
            self.logger.warning(f"Failed to parse command string: {e}")
            # Fallback: simple whitespace split
            parts = command.split()
            return self.parse_command_list(parts)

    def parse_command_list(self, command_parts: list[str]) -> ParsedCommand:
        """Parse a command list into structured components.

        Args:
            command_parts: List of command parts

        Returns:
            ParsedCommand with structured components
        """
        if not command_parts:
            raise ValueError("Command parts cannot be empty")

        command = command_parts[0]
        args = []
        flags = {}
        options = {}

        i = 1
        while i < len(command_parts):
            part = command_parts[i]

            if part.startswith("--"):
                # Long option
                option_name = part[2:]

                if i + 1 < len(command_parts) and not command_parts[i + 1].startswith("-"):
                    # Option with value
                    next_part = command_parts[i + 1]
                    if "," in next_part:
                        # Multiple values
                        options[option_name] = next_part.split(",")
                    else:
                        # Single value
                        options[option_name] = next_part
                    i += 2
                else:
                    # Flag (boolean option)
                    flags[option_name] = True
                    i += 1

            elif part.startswith("-") and len(part) > 1:
                # Short option
                short_flag = part[1:]

                if len(short_flag) == 1:
                    # Single character flag
                    if i + 1 < len(command_parts) and not command_parts[i + 1].startswith("-"):
                        # Option with value
                        flags[short_flag] = command_parts[i + 1]
                        i += 2
                    else:
                        # Boolean flag
                        flags[short_flag] = True
                        i += 1
                else:
                    # Multiple flags combined (-abc style)
                    for char in short_flag:
                        flags[char] = True
                    i += 1

            else:
                # Positional argument
                args.append(part)
                i += 1

        return ParsedCommand(
            command=command,
            args=args,
            flags=flags,
            options=options,
            raw_command=" ".join(command_parts),
        )

    def parse_command_with_template(
        self, command: str | list[str], template: dict[str, Any],
    ) -> ParsedCommand:
        """Parse command using a template for validation.

        Args:
            command: Command string or list
            template: Command template for validation

        Returns:
            ParsedCommand with template validation
        """
        if isinstance(command, str):
            parsed = self.parse_command_string(command)
        else:
            parsed = self.parse_command_list(command)

        # Validate against template
        self._validate_against_template(parsed, template)

        return parsed

    def _validate_against_template(self, parsed: ParsedCommand, template: dict[str, Any]) -> None:
        """
        Validate parsed command against template.
        """
        # Extract template information
        required_args = template.get("required_args", [])
        template.get("optional_args", [])
        allowed_flags = template.get("allowed_flags", [])
        allowed_options = template.get("allowed_options", [])

        # Check required arguments
        if len(parsed.args) < len(required_args):
            raise ValueError(
                f"Command requires at least {len(required_args)} arguments, got {len(parsed.args)}",
            )

        # Check allowed flags
        for flag in parsed.flags:
            if flag not in allowed_flags:
                raise ValueError(f"Flag --{flag} is not allowed")

        # Check allowed options
        for option in parsed.options:
            if option not in allowed_options:
                raise ValueError(f"Option --{option} is not allowed")


class CommandComposer:
    """
    Composes command strings and lists from structured components.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def compose_command(
        self,
        command: str,
        args: list[str] | None = None,
        flags: dict[str, str | bool] | None = None,
        options: dict[str, str | list[str]] | None = None,
    ) -> str:
        """Compose a command string from components.

        Args:
            command: Main command
            args: Positional arguments
            flags: Boolean flags
            options: Options with values

        Returns:
            Composed command string
        """
        parts = [command]

        # Add flags
        if flags:
            for flag, value in flags.items():
                if isinstance(value, bool) and value:
                    parts.append(f"--{flag}")
                elif isinstance(value, str):
                    parts.extend([f"--{flag}", value])

        # Add options
        if options:
            for option, value in options.items():
                if isinstance(value, list):
                    parts.extend([f"--{option}", ",".join(value)])
                else:
                    parts.extend([f"--{option}", str(value)])

        # Add positional arguments
        if args:
            parts.extend(args)

        return " ".join(shlex.quote(str(part)) for part in parts)

    def compose_command_list(
        self,
        command: str,
        args: list[str] | None = None,
        flags: dict[str, str | bool] | None = None,
        options: dict[str, str | list[str]] | None = None,
    ) -> list[str]:
        """Compose a command list from components.

        Args:
            command: Main command
            args: Positional arguments
            flags: Boolean flags
            options: Options with values

        Returns:
            Composed command list
        """
        parts = [command]

        # Add flags
        if flags:
            for flag, value in flags.items():
                if isinstance(value, bool) and value:
                    parts.append(f"--{flag}")
                elif isinstance(value, str):
                    parts.extend([f"--{flag}", value])

        # Add options
        if options:
            for option, value in options.items():
                if isinstance(value, list):
                    parts.extend([f"--{option}", *value])
                else:
                    parts.extend([f"--{option}", str(value)])

        # Add positional arguments
        if args:
            parts.extend(args)

        return parts

    def compose_from_template(
        self, command: str, template: dict[str, Any], values: dict[str, Any],
    ) -> str:
        """Compose command using a template and values.

        Args:
            command: Main command
            template: Command template
            values: Values to populate template

        Returns:
            Composed command string
        """
        args = []
        flags = {}
        options = {}

        # Process template
        for arg_name, arg_template in template.get("args", {}).items():
            if arg_name in values:
                if arg_template.get("required", False) and arg_name not in values:
                    raise ValueError(f"Required argument '{arg_name}' not provided")

                if arg_name in values:
                    args.append(str(values[arg_name]))

        for flag_name in template.get("flags", {}):
            if flag_name in values:
                flags[flag_name] = bool(values[flag_name])

        for option_name in template.get("options", {}):
            if option_name in values:
                options[option_name] = values[option_name]

        return self.compose_command(command, args, flags, options)

    def escape_command_part(self, part: str) -> str:
        """Escape a command part for safe shell usage.

        Args:
            part: Command part to escape

        Returns:
            Escaped command part
        """
        return shlex.quote(str(part))

    def merge_commands(self, base_command: str, additional_args: list[str]) -> str:
        """Merge additional arguments into a base command.

        Args:
            base_command: Base command string
            additional_args: Additional arguments to append

        Returns:
            Merged command string
        """
        if not additional_args:
            return base_command

        escaped_args = [shlex.quote(str(arg)) for arg in additional_args]
        return f"{base_command} {' '.join(escaped_args)}"
