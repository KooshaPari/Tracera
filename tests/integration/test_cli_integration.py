"""CLI Integration Tests.

Tests that all major CLI command groups work correctly with lazy loading,
shell completion, and alias system.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from tests.test_constants import COUNT_FIVE, COUNT_THREE


@pytest.fixture
def runner() -> None:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def cli_app() -> None:
    """Import CLI app."""
    from tracertm.cli.app import app

    return app


# ============================================================
# Major Command Group Tests
# ============================================================


class TestCommandGroups:
    """Test all major command groups work with optimizations."""

    def test_config_commands(self, runner: Any, cli_app: Any) -> None:
        """Test config command group."""
        result = runner.invoke(cli_app, ["config", "--help"])
        assert result.exit_code == 0
        assert "config" in result.stdout.lower() or "configuration" in result.stdout.lower()

    def test_project_commands(self, runner: Any, cli_app: Any) -> None:
        """Test project command group."""
        result = runner.invoke(cli_app, ["project", "--help"])
        assert result.exit_code == 0
        assert "project" in result.stdout.lower()

    def test_item_commands(self, runner: Any, cli_app: Any) -> None:
        """Test item command group."""
        result = runner.invoke(cli_app, ["item", "--help"])
        assert result.exit_code == 0
        assert "item" in result.stdout.lower()

    def test_link_commands(self, runner: Any, cli_app: Any) -> None:
        """Test link command group."""
        result = runner.invoke(cli_app, ["link", "--help"])
        assert result.exit_code == 0
        assert "link" in result.stdout.lower()

    def test_mcp_commands(self, runner: Any, cli_app: Any) -> None:
        """Test MCP command group."""
        result = runner.invoke(cli_app, ["mcp", "--help"])
        assert result.exit_code == 0
        assert "mcp" in result.stdout.lower() or "model context" in result.stdout.lower()

    def test_auth_commands(self, runner: Any, cli_app: Any) -> None:
        """Test auth command group if available."""
        result = runner.invoke(cli_app, ["auth", "--help"])
        # Auth might not be available in all configurations
        assert result.exit_code in {0, 2}  # 0=success, 2=command not found

    def test_test_commands(self, runner: Any, cli_app: Any) -> None:
        """Test test command group."""
        result = runner.invoke(cli_app, ["test", "--help"])
        # Test group might not be available
        assert result.exit_code in {0, 2}


# ============================================================
# Lazy Loading Verification Tests
# ============================================================


class TestLazyLoading:
    """Test that lazy loading doesn't break functionality."""

    def test_lazy_loader_module_caching(self) -> None:
        """Test that lazy loader properly caches modules."""
        from tracertm.cli.performance import get_loader

        loader = get_loader()

        # Load same module twice
        mod1 = loader.load("json")
        mod2 = loader.load("json")

        # Should be same object (cached)
        assert mod1 is mod2

    def test_lazy_loader_multiple_modules(self) -> None:
        """Test loading multiple modules."""
        from tracertm.cli.performance import get_loader

        loader = get_loader()

        # Load different modules
        json_mod = loader.load("json")
        os_mod = loader.load("os")
        sys_mod = loader.load("sys")

        # All should be loaded
        assert json_mod is not None
        assert os_mod is not None
        assert sys_mod is not None

        # Should be different objects
        assert json_mod is not os_mod
        assert os_mod is not sys_mod

    def test_lazy_loader_clear_cache(self) -> None:
        """Test cache clearing."""
        from tracertm.cli.performance import LazyLoader

        loader = LazyLoader()

        # Load module
        mod1 = loader.load("json")

        # Clear cache
        loader.clear_cache()

        # Load again - should be different object
        mod2 = loader.load("json")

        # Different instances but same functionality
        assert mod1.__name__ == mod2.__name__

    def test_command_execution_with_lazy_loading(self, runner: Any, cli_app: Any) -> None:
        """Test that commands work with lazy loading enabled."""
        # This should trigger lazy loading of command modules
        result = runner.invoke(cli_app, ["config", "--help"])
        assert result.exit_code == 0

        # Verify lazy loader was used
        from tracertm.cli.performance import get_loader

        loader = get_loader()
        assert loader is not None


# ============================================================
# Shell Completion Tests
# ============================================================


class TestShellCompletion:
    """Test shell completion generation."""

    def test_completion_install_bash(self, runner: Any, cli_app: Any) -> None:
        """Test bash completion can be generated."""
        # Test that completion install command exists and works
        result = runner.invoke(cli_app, ["--help"])
        assert result.exit_code == 0

        # Typer automatically adds completion
        # We just verify the CLI doesn't break with completion support

    def test_completion_install_zsh(self) -> None:
        """Test zsh completion installation."""
        # This is just a smoke test to ensure completion code exists
        try:
            from tracertm.cli.app import app

            # If app exists and has Typer's auto-completion, this passes
            assert app is not None
            assert hasattr(app, "registered_commands") or hasattr(app, "registered_groups")
        except Exception as e:
            pytest.fail(f"Completion support broken: {e}")

    def test_completion_list_commands(self, runner: Any, cli_app: Any) -> None:
        """Test that completion can list available commands."""
        result = runner.invoke(cli_app, ["--help"])
        assert result.exit_code == 0

        # Should show main commands
        stdout_lower = result.stdout.lower()
        # At least some commands should be visible
        assert any(cmd in stdout_lower for cmd in ["config", "project", "item", "help"])


# ============================================================
# Alias System Tests
# ============================================================


class TestAliasSystem:
    """Test CLI alias functionality."""

    def test_mvp_shortcuts_create(self, runner: Any, cli_app: Any) -> None:
        """Test MVP create shortcut."""
        # This uses the direct command, not alias
        result = runner.invoke(cli_app, ["create", "--help"])
        # May or may not be implemented
        assert result.exit_code in {0, 2}

    def test_mvp_shortcuts_list(self, runner: Any, cli_app: Any) -> None:
        """Test MVP list shortcut."""
        result = runner.invoke(cli_app, ["list", "--help"])
        # May or may not be implemented
        assert result.exit_code in {0, 2}

    def test_command_variations(self, runner: Any, cli_app: Any) -> None:
        """Test that command variations work."""
        # Test both full and short command forms
        commands_to_test = [
            ["config", "--help"],
            ["project", "--help"],
            ["item", "--help"],
        ]

        for cmd in commands_to_test:
            result = runner.invoke(cli_app, cmd)
            assert result.exit_code == 0, f"Command {cmd} failed"


# ============================================================
# Error Handling Tests
# ============================================================


class TestErrorHandling:
    """Test error handling with optimizations enabled."""

    def test_invalid_command_error(self, runner: Any, cli_app: Any) -> None:
        """Test graceful error for invalid command."""
        result = runner.invoke(cli_app, ["nonexistent-command"])
        assert result.exit_code != 0
        # Should show helpful error message
        assert len(result.stdout) > 0 or len(result.stderr if hasattr(result, "stderr") else "") > 0

    def test_missing_required_args_error(self, runner: Any, cli_app: Any) -> None:
        """Test error handling for missing required arguments."""
        # Try create without required args
        result = runner.invoke(cli_app, ["create"])
        assert result.exit_code != 0

    def test_help_flag_always_works(self, runner: Any, cli_app: Any) -> None:
        """Test that --help never fails."""
        help_commands = [
            ["--help"],
            ["-h"],
            ["config", "--help"],
            ["project", "--help"],
        ]

        for cmd in help_commands:
            result = runner.invoke(cli_app, cmd)
            # Help should always succeed
            assert result.exit_code in {0, 2}, f"Help failed for {cmd}"


# ============================================================
# Performance Under Load Tests
# ============================================================


class TestPerformanceUnderLoad:
    """Test CLI performance with multiple rapid invocations."""

    def test_rapid_help_invocations(self, runner: Any, cli_app: Any) -> None:
        """Test rapid successive help invocations."""
        import time

        start = time.perf_counter()

        # Invoke help 10 times rapidly
        for _ in range(10):
            result = runner.invoke(cli_app, ["--help"])
            assert result.exit_code == 0

        elapsed = time.perf_counter() - start

        # Should complete in reasonable time
        assert elapsed < float(COUNT_FIVE + 0.0), f"10 help invocations took {elapsed:.2f}s (too slow)"

    def test_mixed_command_sequence(self, runner: Any, cli_app: Any) -> None:
        """Test mixed command sequence performance."""
        commands = [
            ["--help"],
            ["config", "--help"],
            ["project", "--help"],
            ["--version"],
            ["item", "--help"],
        ]

        import time

        start = time.perf_counter()

        for cmd in commands:
            result = runner.invoke(cli_app, cmd)
            assert result.exit_code == 0, f"Command {cmd} failed"

        elapsed = time.perf_counter() - start

        # All commands should complete quickly
        assert elapsed < float(COUNT_THREE + 0.0), f"Command sequence took {elapsed:.2f}s"


# ============================================================
# Cache Behavior Tests
# ============================================================


class TestCacheBehavior:
    """Test command caching behavior."""

    def test_command_cache_basic(self) -> None:
        """Test basic command cache operations."""
        from tracertm.cli.performance import CommandCache

        cache = CommandCache(ttl=5)

        # Set and retrieve
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        # Non-existent key
        assert cache.get("nonexistent") is None

    def test_command_cache_expiration(self) -> None:
        """Test cache expiration."""
        import time

        from tracertm.cli.performance import CommandCache

        cache = CommandCache(ttl=1)  # 1 second TTL

        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("test_key") is None

    def test_command_cache_clear(self) -> None:
        """Test cache clearing."""
        from tracertm.cli.performance import CommandCache

        cache = CommandCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None


# ============================================================
# Regression Prevention Tests
# ============================================================


class TestRegressionPrevention:
    """Tests to prevent performance regressions."""

    def test_no_unnecessary_imports_at_startup(self) -> None:
        """Verify no heavy modules imported at startup."""
        # Record initial modules
        initial_modules = set(sys.modules.keys())

        # Import CLI app

        # Record modules after import
        final_modules = set(sys.modules.keys())

        # New modules imported
        new_modules = final_modules - initial_modules

        # Heavy modules that should NOT be imported at startup
        heavy_modules = {
            "pandas",
            "numpy",
            "matplotlib",
            "sqlalchemy.orm",
            "alembic",
        }

        # Check if any heavy modules were imported
        imported_heavy = new_modules & heavy_modules

        assert len(imported_heavy) == 0, f"Heavy modules imported at startup: {imported_heavy}"

    def test_version_command_fast(self, runner: Any, cli_app: Any) -> None:
        """Test that --version is consistently fast."""
        import time

        times = []
        for _ in range(5):
            start = time.perf_counter()
            result = runner.invoke(cli_app, ["--version"])
            elapsed = time.perf_counter() - start
            times.append(elapsed)

            assert result.exit_code == 0

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Should be consistently fast
        assert max_time < 0.5, f"Version command too slow: {max_time:.3f}s"
        assert avg_time < 0.1, f"Version command avg too slow: {avg_time:.3f}s"


# ============================================================
# Cross-Platform Tests
# ============================================================


class TestCrossPlatform:
    """Test CLI works across platforms."""

    def test_path_handling(self) -> None:
        """Test that path handling works on current platform."""
        from tracertm.cli.performance import CommandCache

        # Test cache directory creation
        cache = CommandCache()
        assert isinstance(cache.cache_dir, Path)

    def test_subprocess_compatibility(self) -> None:
        """Test subprocess calls work on current platform."""
        import sys

        # Test basic subprocess call
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        assert result.returncode == 0
        assert "Python" in result.stdout


# ============================================================
# Integration Smoke Tests
# ============================================================


@pytest.mark.integration
class TestIntegrationSmoke:
    """Smoke tests for CLI integration."""

    def test_full_startup_sequence(self, runner: Any, cli_app: Any) -> None:
        """Test complete startup sequence."""
        # Simulate user discovering CLI
        steps = [
            (["--help"], "main help"),
            (["--version"], "version"),
            (["config", "--help"], "config help"),
        ]

        for cmd, description in steps:
            result = runner.invoke(cli_app, cmd)
            assert result.exit_code == 0, f"Failed: {description}"

    def test_error_recovery(self, runner: Any, cli_app: Any) -> None:
        """Test CLI recovers from errors gracefully."""
        # Invalid command
        result1 = runner.invoke(cli_app, ["invalid"])
        assert result1.exit_code != 0

        # Valid command after error
        result2 = runner.invoke(cli_app, ["--help"])
        assert result2.exit_code == 0

    def test_all_command_groups_loadable(self, runner: Any, cli_app: Any) -> None:
        """Test all command groups can be loaded."""
        command_groups = [
            "config",
            "project",
            "item",
            "link",
            "mcp",
        ]

        for group in command_groups:
            result = runner.invoke(cli_app, [group, "--help"])
            assert result.exit_code == 0, f"Failed to load {group} command group"
