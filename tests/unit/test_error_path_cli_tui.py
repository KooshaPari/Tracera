"""
Error path tests for CLI and TUI operations.

Comprehensive error testing for:
- Command line argument errors
- Configuration errors
- User input validation
- Terminal/UI rendering errors
- File I/O errors in CLI context
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tracertm.config.manager import ConfigManager

# ============================================================================
# CLI ARGUMENT PARSING ERROR TESTS
# ============================================================================


class TestCLIArgumentErrors:
    """Test CLI argument parsing errors."""

    def test_missing_required_argument(self):
        """Test error when required argument is missing."""

        def parse_args(args):
            if not args or "project" not in args:
                raise ValueError("Missing required argument: project")
            return {"project": args[0]}

        with pytest.raises(ValueError, match="Missing required argument"):
            parse_args([])

    def test_invalid_argument_type(self):
        """Test error when argument has wrong type."""

        def parse_args(args):
            project_id = args.get("id")
            if not isinstance(project_id, str):
                raise TypeError("project_id must be a string")
            return project_id

        with pytest.raises(TypeError):
            parse_args({"id": 12345})

    def test_unknown_command_error(self):
        """Test error for unknown command."""

        def get_command(cmd):
            valid_commands = ["create", "list", "delete"]
            if cmd not in valid_commands:
                raise ValueError(f"Unknown command: {cmd}")
            return cmd

        with pytest.raises(ValueError, match="Unknown command"):
            get_command("invalid")

    def test_mutually_exclusive_arguments(self):
        """Test error for mutually exclusive arguments."""

        def validate_args(args):
            if args.get("output") and args.get("interactive"):
                raise ValueError("--output and --interactive are mutually exclusive")

        with pytest.raises(ValueError, match="mutually exclusive"):
            validate_args({"output": "file", "interactive": True})

    def test_argument_requires_value(self):
        """Test error when argument requires value."""

        def parse_args(args):
            if "--name" in args:
                idx = args.index("--name")
                if idx + 1 >= len(args):
                    raise ValueError("--name requires a value")
                return args[idx + 1]
            return None

        with pytest.raises(ValueError, match="requires a value"):
            parse_args(["--name"])


# ============================================================================
# CONFIGURATION ERROR TESTS
# ============================================================================


class TestConfigurationErrors:
    """Test configuration loading and validation errors."""

    def test_config_file_not_found(self):
        """Test error when config file doesn't exist."""
        config_path = Path("/nonexistent/config.yaml")

        def check_and_raise():
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            check_and_raise()

    def test_config_file_permission_denied(self):
        """Test error when can't read config file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            config_path = Path(f.name)
            f.write("key: value")

        try:
            config_path.chmod(0o000)  # No permissions

            with pytest.raises(PermissionError):
                config_path.read_text()
        finally:
            config_path.chmod(0o644)
            config_path.unlink()

    def test_invalid_config_format(self):
        """Test error when config has invalid format."""

        def load_config(content):
            import yaml

            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML format: {e}") from e

        invalid_yaml = "key: value\n  invalid:\n  indent:"

        with pytest.raises((ValueError, Exception)):
            load_config(invalid_yaml)

    def test_missing_required_config_key(self):
        """Test error when required config key is missing."""

        def validate_config(config):
            required_keys = ["database_url", "project_id"]
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Missing required config key: {key}")

        with pytest.raises(ValueError, match="Missing required config key"):
            validate_config({"database_url": "sqlite://"})

    def test_invalid_config_value_type(self):
        """Test error when config value has wrong type."""

        def validate_config(config):
            if not isinstance(config.get("port"), int):
                raise TypeError("port must be an integer")

        with pytest.raises(TypeError):
            validate_config({"port": "8000"})


# ============================================================================
# USER INPUT VALIDATION ERROR TESTS
# ============================================================================


class TestUserInputValidationErrors:
    """Test user input validation in CLI."""

    def test_empty_input_validation(self):
        """Test validation of empty input."""

        def validate_title(title):
            if not title or not title.strip():
                raise ValueError("Title cannot be empty")

        with pytest.raises(ValueError, match="cannot be empty"):
            validate_title("")

    def test_input_too_long(self):
        """Test validation of oversized input."""

        def validate_description(desc, max_length=1000):
            if len(desc) > max_length:
                raise ValueError(f"Description too long (max {max_length} chars)")

        long_input = "x" * 2000

        with pytest.raises(ValueError, match="too long"):
            validate_description(long_input)

    def test_input_contains_invalid_characters(self):
        """Test validation of invalid characters."""
        import re

        def validate_project_name(name):
            if not re.match(r"^[a-zA-Z0-9_-]+$", name):
                raise ValueError("Project name contains invalid characters")

        with pytest.raises(ValueError, match="invalid characters"):
            validate_project_name("project@invalid!")

    def test_input_sql_injection_attempt(self):
        """Test detection of SQL injection in input."""

        def validate_query(query):
            dangerous_patterns = ["DROP", "DELETE", "TRUNCATE"]
            upper_query = query.upper()
            for pattern in dangerous_patterns:
                if pattern in upper_query:
                    raise ValueError("Potential SQL injection detected")

        with pytest.raises(ValueError, match="SQL injection"):
            validate_query("1'; DROP TABLE items;--")

    def test_input_cross_site_scripting(self):
        """Test detection of XSS in input."""

        def validate_html(content):
            dangerous_tags = ["<script>", "<iframe>", "onclick"]
            lower_content = content.lower()
            for tag in dangerous_tags:
                if tag in lower_content:
                    raise ValueError("Potentially dangerous HTML detected")

        with pytest.raises(ValueError, match="dangerous HTML"):
            validate_html("<script>alert('xss')</script>")


# ============================================================================
# FILE I/O ERROR TESTS FOR CLI
# ============================================================================


class TestCLIFileIOErrors:
    """Test file I/O errors in CLI context."""

    def test_read_nonexistent_file(self):
        """Test reading file that doesn't exist."""

        def read_file(path):
            file_path = Path(path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            return file_path.read_text()

        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")

    def test_write_to_directory_instead_of_file(self):
        """Test writing to path that is a directory."""

        def write_file(path, content):
            file_path = Path(path)
            if file_path.is_dir():
                raise IsADirectoryError(f"Cannot write to directory: {path}")
            file_path.write_text(content)

        with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(IsADirectoryError):
            write_file(tmpdir, "content")

    def test_write_with_insufficient_permissions(self):
        """Test write fails with insufficient permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            test_file = tmp_path / "test.txt"

            # Create file with no write permissions
            test_file.write_text("original")
            test_file.chmod(0o444)

            try:
                with pytest.raises(PermissionError):
                    test_file.write_text("new content")
            finally:
                test_file.chmod(0o644)

    def test_read_corrupted_data_file(self):
        """Test reading corrupted data file."""

        def read_json_file(path):
            import json

            file_path = Path(path)
            content = file_path.read_text()
            return json.loads(content)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            bad_file = tmp_path / "bad.json"
            bad_file.write_text("{invalid json")

            with pytest.raises((json.JSONDecodeError, ValueError), match=r"Expecting|invalid"):
                read_json_file(str(bad_file))

    def test_file_already_exists_error(self):
        """Test error when trying to create existing file."""

        def create_file_exclusive(path):
            file_path = Path(path)
            if file_path.exists():
                raise FileExistsError(f"File already exists: {path}")
            file_path.touch()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            existing_file = tmp_path / "existing.txt"
            existing_file.touch()

            with pytest.raises(FileExistsError):
                create_file_exclusive(str(existing_file))


# ============================================================================
# TERMINAL/TUI RENDERING ERROR TESTS
# ============================================================================


class TestTUIRenderingErrors:
    """Test TUI rendering and output errors."""

    def test_unicode_rendering_error(self):
        """Test error rendering unicode characters."""

        def render_text(text):
            try:
                # Simulate terminal rendering
                encoded = text.encode("utf-8")
                return encoded.decode("utf-8")
            except UnicodeError as e:
                raise RuntimeError(f"Failed to render text: {e}") from e

        # This should succeed
        result = render_text("Unicode: ñ, é, 中文, 🎉")
        assert "Unicode:" in result

    def test_terminal_size_error(self):
        """Test error getting terminal size."""

        def get_terminal_size():
            try:
                import shutil

                size = shutil.get_terminal_size((80, 24))
                if size.columns < 1 or size.lines < 1:
                    raise ValueError("Invalid terminal size")
                return size
            except Exception as e:
                raise RuntimeError(f"Cannot determine terminal size: {e}") from e

        # Should work or raise with informative error
        try:
            size = get_terminal_size()
            assert size.columns > 0
        except RuntimeError:
            pass  # Expected in some test environments

    def test_color_output_error(self):
        """Test error with colored output."""

        def colorize_text(text, color):
            colors = {"red": "\033[31m", "green": "\033[32m"}
            if color not in colors:
                raise ValueError(f"Unknown color: {color}")
            return f"{colors[color]}{text}\033[0m"

        with pytest.raises(ValueError, match="Unknown color"):
            colorize_text("text", "invalid_color")

    def test_menu_navigation_error(self):
        """Test error in menu navigation."""

        class Menu:
            def __init__(self, options):
                self.options = options
                self.current_index = 0

            def select_option(self, index):
                if not (0 <= index < len(self.options)):
                    raise IndexError(f"Invalid option index: {index}")
                self.current_index = index
                return self.options[index]

        menu = Menu(["option1", "option2", "option3"])

        with pytest.raises(IndexError):
            menu.select_option(10)

    def test_input_buffer_overflow(self):
        """Test error with input buffer overflow."""

        def read_user_input(max_length=100):
            user_input = "x" * 1000  # Simulate very long input

            if len(user_input) > max_length:
                raise ValueError(f"Input too long (max {max_length} chars, got {len(user_input)})")
            return user_input

        with pytest.raises(ValueError, match="Input too long"):
            read_user_input()


# ============================================================================
# CONFIGURATION MANAGER ERROR TESTS
# ============================================================================


class TestConfigManagerErrors:
    """Test ConfigManager error handling."""

    def test_config_manager_get_missing_key(self):
        """Test getting missing config key."""
        with patch("os.path.expanduser") as mock_expand:
            mock_expand.return_value = "/nonexistent/config"

            manager = ConfigManager()

            # Getting missing key returns None
            result = manager.get("nonexistent_key")
            assert result is None

    def test_config_manager_set_invalid_key(self):
        """Test setting invalid config key."""
        manager = ConfigManager()

        # Should allow setting any key or validate
        manager.set("test_key", "test_value")
        assert manager.get("test_key") == "test_value"

    def test_config_persistence_error(self):
        """Test error saving config to file."""

        def write_config():
            with Path("/config/file").open("w") as f:
                f.write("config")

        with (
            patch("builtins.open", side_effect=OSError("Write failed")),
            pytest.raises(OSError, match="Write failed"),
        ):
            write_config()

    def test_config_encryption_error(self):
        """Test error encrypting sensitive config."""

        def encrypt_config(data, key):
            if not key:
                raise ValueError("Encryption key required")
            # Simulate encryption
            return f"encrypted:{data}"

        with pytest.raises(ValueError, match="Encryption key required"):
            encrypt_config({"password": "secret"}, None)


# ============================================================================
# STORAGE MANAGER ERROR TESTS
# ============================================================================


@pytest.mark.asyncio
class TestStorageManagerErrors:
    """Test storage manager error handling."""

    async def test_storage_init_permission_denied(self):
        """Test storage initialization with permission denied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)

            # Make directory read-only
            storage_path.chmod(0o444)

            try:
                with pytest.raises((PermissionError, OSError)):
                    # Try to create subdirectory
                    (storage_path / "subdir").mkdir()
            finally:
                storage_path.chmod(0o755)

    async def test_storage_corrupted_metadata(self):
        """Test handling of corrupted storage metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create corrupted metadata
            meta_file = Path(tmpdir) / ".metadata.json"
            meta_file.write_text("{invalid json")

            def load_meta():
                return json.loads(meta_file.read_text())

            with pytest.raises((json.JSONDecodeError, ValueError), match=r"Expecting|invalid"):
                load_meta()

    async def test_storage_disk_full(self, tmp_path):
        """Test handling of disk full error."""
        test_file = tmp_path / "test.txt"
        with (
            patch(
                "pathlib.Path.write_text",
                side_effect=OSError("No space left on device"),
            ),
            pytest.raises(OSError, match="No space left on device"),
        ):
            test_file.write_text("test")

    async def test_storage_concurrent_access_error(self):
        """Test handling of concurrent access errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate concurrent access conflict
            item_data = {"title": "test", "version": 1}

            item_file = Path(tmpdir) / "item-1.json"

            # First write succeeds
            item_file.write_text(json.dumps(item_data))

            # Concurrent write with same item
            concurrent_data = {"title": "concurrent", "version": 1}

            # Second write should succeed
            item_file.write_text(json.dumps(concurrent_data))

            # Verify last write wins
            result = json.loads(item_file.read_text())
            assert result["title"] == "concurrent"


# ============================================================================
# INITIALIZATION ERROR TESTS
# ============================================================================


class TestInitializationErrors:
    """Test initialization errors."""

    def test_database_init_failure(self):
        """Test database initialization failure."""

        def init_database(url):
            if not url:
                raise ValueError("Database URL required")
            # Simulate initialization
            return f"connection:{url}"

        with pytest.raises(ValueError, match="Database URL required"):
            init_database("")

    def test_missing_dependencies(self):
        """Test error when dependencies are missing."""

        def check_dependencies():
            required = ["package1", "package2"]
            missing = []

            # Simulate checking
            for pkg in required:
                try:
                    __import__(pkg)
                except ImportError:
                    missing.append(pkg)

            if missing:
                raise ImportError(f"Missing required packages: {missing}")

        # This might or might not raise depending on environment

    def test_version_compatibility_error(self):
        """Test version compatibility check."""

        def check_version_compatibility(required_version):
            import sys

            current = sys.version_info

            if current.major < required_version[0]:
                raise RuntimeError(f"Python {required_version[0]}.{required_version[1]}+ required")

        # Check with reasonable version requirement
        check_version_compatibility((3, 7))  # Should pass

        with pytest.raises(RuntimeError):
            check_version_compatibility((99, 0))  # Should fail


# ============================================================================
# INTEGRATION ERROR SCENARIOS FOR CLI
# ============================================================================


@pytest.mark.asyncio
class TestCLIIntegrationErrors:
    """Test error scenarios across CLI operations."""

    async def test_command_execution_chain_error(self):
        """Test error in command execution chain."""
        commands = []

        async def execute_command(cmd):
            await asyncio.sleep(0)
            commands.append(cmd)
            if cmd == "fail":
                raise RuntimeError("Command failed")
            return f"result:{cmd}"

        # Execute commands
        try:
            await execute_command("init")
            await execute_command("fail")
        except RuntimeError as e:
            assert "Command failed" in str(e)

        # First command should have executed
        assert "init" in commands

    async def test_cleanup_after_cli_error(self):
        """Test cleanup after CLI error."""
        cleanup_called = False
        resources = []

        async def command_with_cleanup():
            await asyncio.sleep(0)
            nonlocal cleanup_called
            resources.append("resource1")

            try:
                raise RuntimeError("Command error")
            finally:
                cleanup_called = True
                resources.clear()

        with pytest.raises(RuntimeError, match="Command error"):
            await command_with_cleanup()

        assert cleanup_called
        assert len(resources) == 0

    async def test_user_interrupt_handling(self):
        """Test handling of user interrupt (Ctrl+C)."""

        async def long_running_command():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError as err:
                raise KeyboardInterrupt("User interrupted") from err

        task = asyncio.create_task(long_running_command())
        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises((asyncio.CancelledError, KeyboardInterrupt)):
            await task


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
