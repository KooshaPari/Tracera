"""
Base CLI Framework for Pheno SDK
================================

Provides the foundational CLI framework classes and utilities.
"""

import argparse
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class CommandHandler:
    """
    Represents a command handler with metadata.
    """

    name: str
    description: str
    handler: Callable[[argparse.Namespace], int]
    parser_config: Callable[[argparse.ArgumentParser], None] | None = None
    help_text: str | None = None


class CLIFramework(ABC):
    """Base CLI framework for Pheno SDK projects.

    Provides common functionality for building command-line interfaces:
    - Subcommand routing
    - Argument parsing
    - Command registration
    - Help generation
    - Error handling
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        epilog: str | None = None,
        logger: logging.Logger | None = None,
    ):
        self.name = name
        self.description = description
        self.version = version
        self.epilog = epilog
        self.logger = logger or logging.getLogger(name)

        self.commands: dict[str, CommandHandler] = {}
        self._setup_base_parser()

    def _setup_base_parser(self):
        """
        Set up the base argument parser.
        """
        self.parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self.epilog,
        )

        self.parser.add_argument(
            "--version", action="version", version=f"{self.name} {self.version}",
        )

        self.subparsers = self.parser.add_subparsers(dest="command", help="Available commands")

    def register_command(
        self,
        name: str,
        description: str,
        handler: Callable[[argparse.Namespace], int],
        parser_config: Callable[[argparse.ArgumentParser], None] | None = None,
        help_text: str | None = None,
    ):
        """Register a command handler.

        Args:
            name: Command name
            description: Command description
            handler: Function to handle the command
            parser_config: Optional function to configure the argument parser
            help_text: Optional help text for the command
        """
        command_handler = CommandHandler(
            name=name,
            description=description,
            handler=handler,
            parser_config=parser_config,
            help_text=help_text,
        )

        self.commands[name] = command_handler

        # Create subparser
        subparser = self.subparsers.add_parser(
            name,
            help=description,
            description=help_text or description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Configure parser if provided
        if parser_config:
            parser_config(subparser)

        # Set the handler function
        subparser.set_defaults(func=handler)

    def run(self, args: list[str] | None = None) -> int:
        """Run the CLI with the given arguments.

        Args:
            args: Command line arguments (default: sys.argv[1:])

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            parsed_args = self.parser.parse_args(args)

            if not parsed_args.command:
                self.parser.print_help()
                return 1

            # Get the handler function
            handler = getattr(parsed_args, "func", None)
            if not handler:
                self.logger.error(f"No handler found for command: {parsed_args.command}")
                return 1

            # Run the handler
            return handler(parsed_args)

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
            return 1
        except Exception as e:
            self.logger.exception(f"Unexpected error: {e}")
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.exception("Full traceback:")
            return 1

    @abstractmethod
    def setup_commands(self):
        """
        Set up all commands for this CLI framework.
        """
