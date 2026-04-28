"""
Tests for CLI Framework

Tests the pheno-sdk CLI framework including Command base class,
CLIRunner, and output formatting utilities.
"""

import json
from typing import Any

import pytest

from pheno.cli import (
    Command,
    CommandConfig,
    CommandError,
    OutputFormatter,
    SyncCommand,
    TableBuilder,
    format_dict_as_table,
    format_list_as_table,
)


class HelloCommand(Command):
    """Test command that says hello."""

    async def execute(self, args: dict[str, Any]) -> Any:
        name = args.get("name", "World")
        return {"message": f"Hello, {name}!", "name": name}

    def format_output(self, result: Any) -> str:
        if self.config.json_output:
            return json.dumps(result)
        return result["message"]


class ErrorCommand(Command):
    """Test command that raises an error."""

    async def execute(self, args: dict[str, Any]) -> Any:
        raise CommandError("Test error", code=42)

    def format_output(self, result: Any) -> str:
        return str(result)


class ValidatingCommand(Command):
    """Test command with validation."""

    def validate(self, args: dict[str, Any]) -> None:
        if "required_arg" not in args:
            raise ValueError("required_arg is missing")

    async def execute(self, args: dict[str, Any]) -> Any:
        return {"status": "ok"}

    def format_output(self, result: Any) -> str:
        return "Success"


class SyncHelloCommand(SyncCommand):
    """Test synchronous command."""

    def execute_sync(self, args: dict[str, Any]) -> Any:
        name = args.get("name", "World")
        return f"Sync Hello, {name}!"

    def format_output(self, result: Any) -> str:
        return result


# Tests for Command base class
class TestCommand:
    """Test Command base class."""

    @pytest.mark.asyncio
    async def test_basic_command_execution(self):
        """Test basic command execution."""
        config = CommandConfig(verbose=False, json_output=False)
        cmd = HelloCommand(config)

        output = await cmd.run({"name": "Alice"})
        assert output == "Hello, Alice!"

    @pytest.mark.asyncio
    async def test_command_json_output(self):
        """Test command with JSON output."""
        config = CommandConfig(verbose=False, json_output=True)
        cmd = HelloCommand(config)

        output = await cmd.run({"name": "Bob"})
        result = json.loads(output)
        assert result["message"] == "Hello, Bob!"
        assert result["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_command_validation(self):
        """Test command validation."""
        config = CommandConfig()
        cmd = ValidatingCommand(config)

        # Should fail validation
        with pytest.raises(ValueError, match="required_arg is missing"):
            await cmd.run({})

        # Should pass validation
        output = await cmd.run({"required_arg": "value"})
        assert output == "Success"

    @pytest.mark.asyncio
    async def test_command_error(self):
        """Test command error handling."""
        config = CommandConfig()
        cmd = ErrorCommand(config)

        with pytest.raises(CommandError) as exc_info:
            await cmd.run({})

        assert exc_info.value.message == "Test error"
        assert exc_info.value.code == 42

    @pytest.mark.asyncio
    async def test_sync_command(self):
        """Test synchronous command wrapper."""
        config = CommandConfig()
        cmd = SyncHelloCommand(config)

        output = await cmd.run({"name": "Charlie"})
        assert output == "Sync Hello, Charlie!"


# Tests for OutputFormatter
class TestOutputFormatter:
    """Test OutputFormatter class."""

    def test_format_json(self):
        """Test JSON formatting."""
        formatter = OutputFormatter()

        data = {"key": "value", "number": 42}
        json_str = formatter.format_json(data)

        assert "key" in json_str
        assert "value" in json_str
        parsed = json.loads(json_str)
        assert parsed == data

    def test_format_json_pretty(self):
        """Test pretty JSON formatting."""
        formatter = OutputFormatter()

        data = {"key": "value"}
        json_str = formatter.format_json(data, pretty=True)

        assert "\n" in json_str  # Pretty print has newlines
        assert "  " in json_str  # Pretty print has indentation

    def test_create_table(self):
        """Test table creation."""
        formatter = OutputFormatter()

        table = formatter.create_table(
            title="Test Table",
            columns=["ID", "Name", "Status"],
            rows=[
                ["1", "Alice", "active"],
                ["2", "Bob", "inactive"],
            ],
        )

        assert table.title == "Test Table"
        assert len(table.columns) == 3

    def test_create_table_with_styles(self):
        """Test table creation with column styles."""
        formatter = OutputFormatter()

        table = formatter.create_table(
            columns=[
                {"name": "ID", "style": "cyan"},
                {"name": "Name", "style": "magenta"},
            ],
            rows=[["1", "Alice"]],
        )

        assert len(table.columns) == 2

    def test_format_dict_as_table(self):
        """Test dictionary to table conversion."""
        data = {"ID": "123", "Name": "Test", "Status": "active"}
        table = format_dict_as_table(data, title="Details")

        assert table.title == "Details"
        # Table should have 2 columns (key, value)

    def test_format_list_as_table(self):
        """Test list of dicts to table conversion."""
        data = [
            {"id": "1", "name": "Alice", "status": "active"},
            {"id": "2", "name": "Bob", "status": "inactive"},
        ]

        table = format_list_as_table(data, columns=["id", "name"], title="Users")

        assert table.title == "Users"
        assert len(table.columns) == 2

    def test_format_empty_list_as_table(self):
        """Test empty list to table conversion."""
        table = format_list_as_table([], title="Empty")
        assert table.title == "Empty"


# Tests for TableBuilder
class TestTableBuilder:
    """Test TableBuilder class."""

    def test_table_builder_basic(self):
        """Test basic table building."""
        table = (TableBuilder("Test")
                 .add_column("ID")
                 .add_column("Name")
                 .add_row("1", "Alice")
                 .add_row("2", "Bob")
                 .build())

        assert table.title == "Test"
        assert len(table.columns) == 2

    def test_table_builder_with_styles(self):
        """Test table building with styles."""
        table = (TableBuilder("Styled")
                 .add_column("ID", style="cyan")
                 .add_column("Name", style="magenta")
                 .add_row("1", "Alice")
                 .build())

        assert len(table.columns) == 2

    def test_table_builder_chaining(self):
        """Test method chaining."""
        builder = TableBuilder("Chain Test")

        # Should return self for chaining
        result = builder.add_column("Test")
        assert result is builder

        result = builder.add_row("Value")
        assert result is builder


# Integration test for CommandConfig
class TestCommandConfig:
    """Test CommandConfig class."""

    def test_config_defaults(self):
        """Test config default values."""
        config = CommandConfig()

        assert config.verbose is False
        assert config.json_output is False
        assert config.config_path is None
        assert config.extra == {}

    def test_config_with_values(self):
        """Test config with custom values."""
        config = CommandConfig(
            verbose=True,
            json_output=True,
            config_path="/path/to/config",
            custom_option="value",
        )

        assert config.verbose is True
        assert config.json_output is True
        assert config.config_path == "/path/to/config"
        assert config.extra["custom_option"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
