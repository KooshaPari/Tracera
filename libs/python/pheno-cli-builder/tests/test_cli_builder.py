"""Tests for pheno-cli-builder package."""

import pytest
from pheno_cli_builder import Argument, ArgumentType, Command, Option


class TestArgument:
    """Test Argument class."""

    def test_argument_creation(self) -> None:
        """Test creating an argument."""
        arg = Argument("name", ArgumentType.STRING, "A name argument", required=True)
        assert arg.name == "name"
        assert arg.type == ArgumentType.STRING
        assert arg.help == "A name argument"
        assert arg.required is True
        assert arg.default is None

    def test_argument_with_default(self) -> None:
        """Test argument with default value."""
        arg = Argument("count", ArgumentType.INTEGER, default=10, required=False)
        assert arg.default == 10
        assert arg.required is False

    def test_argument_types(self) -> None:
        """Test all argument types."""
        assert ArgumentType.STRING.value == "string"
        assert ArgumentType.INTEGER.value == "integer"
        assert ArgumentType.FLOAT.value == "float"
        assert ArgumentType.BOOLEAN.value == "boolean"
        assert ArgumentType.LIST.value == "list"


class TestOption:
    """Test Option class."""

    def test_option_creation(self) -> None:
        """Test creating an option."""
        opt = Option("verbose", ArgumentType.BOOLEAN, "Enable verbose output", is_flag=True)
        assert opt.name == "verbose"
        assert opt.type == ArgumentType.BOOLEAN
        assert opt.help == "Enable verbose output"
        assert opt.is_flag is True
        assert opt.default is None

    def test_option_with_default(self) -> None:
        """Test option with default value."""
        opt = Option("format", ArgumentType.STRING, "Output format", default="json")
        assert opt.default == "json"
        assert opt.is_flag is False


class TestCommand:
    """Test Command class."""

    def test_command_creation(self) -> None:
        """Test creating a command."""
        cmd = Command("test", "A test command")
        assert cmd.name == "test"
        assert cmd.description == "A test command"
        assert cmd.arguments == []
        assert cmd.options == []
        assert cmd.subcommands == []

    def test_command_with_arguments(self) -> None:
        """Test command with arguments."""
        cmd = Command("greet")
        arg = Argument("name", ArgumentType.STRING, "Name to greet")
        cmd.add_argument(arg)
        assert len(cmd.arguments) == 1
        assert cmd.arguments[0].name == "name"

    def test_command_with_options(self) -> None:
        """Test command with options."""
        cmd = Command("list")
        opt = Option("all", ArgumentType.BOOLEAN, "Show all items", is_flag=True)
        cmd.add_option(opt)
        assert len(cmd.options) == 1
        assert cmd.options[0].name == "all"

    def test_command_with_subcommands(self) -> None:
        """Test command with subcommands."""
        parent = Command("git", "Git commands")
        child = Command("clone", "Clone a repository")
        parent.add_subcommand(child)
        assert len(parent.subcommands) == 1
        assert parent.subcommands[0].name == "clone"

    def test_nested_command(self) -> None:
        """Test deeply nested command structure."""
        root = Command("app", "Main application")
        sub1 = Command("config", "Configuration commands")
        sub2 = Command("set", "Set configuration value")
        
        arg = Argument("key", ArgumentType.STRING, "Configuration key")
        sub2.add_argument(arg)
        
        sub1.add_subcommand(sub2)
        root.add_subcommand(sub1)
        
        assert root.subcommands[0].name == "config"
        assert root.subcommands[0].subcommands[0].name == "set"
        assert len(root.subcommands[0].subcommands[0].arguments) == 1


def test_imports() -> None:
    """Test that all exports are available."""
    from pheno_cli_builder import __all__
    assert "Argument" in __all__
    assert "ArgumentType" in __all__
    assert "Command" in __all__
    assert "Option" in __all__


def test_core_imports() -> None:
    """Test that core module exports work."""
    from pheno_cli_builder.core import Argument, ArgumentType, Command, Option
    assert Argument is not None
    assert ArgumentType is not None
    assert Command is not None
    assert Option is not None
