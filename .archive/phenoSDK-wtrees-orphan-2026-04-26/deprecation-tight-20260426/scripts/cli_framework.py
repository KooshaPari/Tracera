#!/usr/bin/env python3
"""
Pheno SDK CLI Framework
=======================

Rich CLI framework with colors, progress bars, and interactive prompts.
Provides a foundation for building user-friendly command-line interfaces.

Usage:
    python scripts/cli_framework.py --help
"""

import argparse
import sys
import time


class CLIFramework:
    """
    Rich CLI framework with enhanced user experience.
    """

    # Color codes
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    NC = "\033[0m"  # No Color

    def __init__(self, app_name: str = "Pheno SDK"):
        self.app_name = app_name

    def echo(self, message: str, color: str | None = None) -> None:
        """
        Print colored message to console.
        """
        if color:
            print(f"{color}{message}{self.NC}")
        else:
            print(message)

    def info(self, message: str) -> None:
        """
        Print info message in blue.
        """
        self.echo(message, self.BLUE)

    def success(self, message: str) -> None:
        """
        Print success message in green.
        """
        self.echo(f"✓ {message}", self.GREEN)

    def warning(self, message: str) -> None:
        """
        Print warning message in yellow.
        """
        self.echo(f"⚠ {message}", self.YELLOW)

    def error(self, message: str) -> None:
        """
        Print error message in red.
        """
        self.echo(f"✗ {message}", self.RED)

    def progress_bar(self, total: int, prefix: str = "Progress") -> None:
        """Display a simple progress bar.

        Args:
            total: Total number of steps
            prefix: Progress bar prefix text
        """
        for i in range(total + 1):
            percent = int(100 * (i / total))
            filled = int(50 * (i / total))
            bar = "█" * filled + "-" * (50 - filled)
            print(f"\r{self.BLUE}{prefix}{self.NC}: |{bar}| {percent}%", end="")
            sys.stdout.flush()
            time.sleep(0.1)  # Simulate work
        print()  # New line when complete

    def confirm(self, message: str) -> bool:
        """Get user confirmation.

        Args:
            message: Confirmation message

        Returns:
            True if user confirms, False otherwise
        """
        response = input(f"{self.YELLOW}{message} (y/N): {self.NC}").strip().lower()
        return response in ["y", "yes"]

    def choice_menu(self, title: str, choices: list) -> int | None:
        """Display a choice menu.

        Args:
            title: Menu title
            choices: List of choices

        Returns:
            Selected choice index or None if cancelled
        """
        self.echo(f"\n{title}", self.BLUE)
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")

        try:
            selection = input(f"\n{self.BLUE}Select option (1-{len(choices)}): {self.NC}")
            if selection.lower() == "q":
                return None
            index = int(selection) - 1
            if 0 <= index < len(choices):
                return index
            self.error(f"Invalid selection. Please choose 1-{len(choices)}")
            return None
        except ValueError:
            self.error("Invalid input. Please enter a number.")
            return None


def demo_cli() -> None:
    """
    Demonstrate CLI framework capabilities.
    """
    cli = CLIFramework("Pheno SDK Demo")

    cli.info("Pheno SDK CLI Framework Demo")
    cli.echo("=" * 40)

    # Demo colored output
    cli.success("This is a success message")
    cli.warning("This is a warning message")
    cli.error("This is an error message")
    cli.info("This is an info message")

    # Demo progress bar
    cli.progress_bar(20, "Processing files")

    # Demo confirmation
    if cli.confirm("Do you want to continue?"):
        cli.success("User confirmed")
    else:
        cli.warning("User cancelled")

    # Demo choice menu
    choices = [
        "Install development dependencies",
        "Run linting checks",
        "Run tests",
        "Build package",
        "Exit",
    ]

    selection = cli.choice_menu("Available Actions", choices)
    if selection is not None:
        cli.success(f"You selected: {choices[selection]}")
    else:
        cli.info("No selection made")


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description="Pheno SDK CLI Framework", formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--demo", action="store_true", help="Run CLI framework demo")

    args = parser.parse_args()

    if args.demo:
        demo_cli()
    else:
        # Default action
        print("Pheno SDK CLI Framework")
        print("Use --demo to see capabilities")


if __name__ == "__main__":
    main()
