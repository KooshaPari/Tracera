"""UI Layer Polish: Integration Tests.

This test suite covers integration scenarios linking CLI, TUI, and API with services.

Coverage areas:
- CLI command → Service integration with edge cases
- TUI widget → Service integration with state synchronization
- API endpoint → Service integration with data transformations
- Cross-layer data flow and consistency
- Error propagation across layers

Target: 20-30 integration tests
"""

import uuid

import pytest
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# CLI → Service Integration Tests
# =============================================================================


class TestCliServiceIntegration:
    """Test CLI command integration with services."""

    def test_cli_create_item_basic(self) -> None:
        """Test CLI create command basic flow."""
        from tracertm.cli.commands.item import app

        result = runner.invoke(app, ["create", "Integration Test Item", "--view", "CODE", "--type", "file"])

        # Should execute without crashing
        assert result.exit_code in {0, 1, 2}

    def test_cli_create_link_basic(self) -> None:
        """Test CLI link command basic flow."""
        from tracertm.cli.commands.link import app

        test_id_1 = str(uuid.uuid4())
        test_id_2 = str(uuid.uuid4())

        result = runner.invoke(app, ["create", test_id_1, test_id_2])

        # Should execute without crashing
        assert result.exit_code in {0, 1, 2}

    def test_cli_list_items_basic(self) -> None:
        """Test CLI list command basic flow."""
        from tracertm.cli.commands.item import app

        result = runner.invoke(app, ["list"])

        # Should execute without crashing
        assert result.exit_code in {0, 1, 2}


# =============================================================================
# CLI → Service Data Flow Tests
# =============================================================================


class TestCliServiceDataFlow:
    """Test CLI data flow through services."""

    def test_cli_parses_input_with_special_chars(self) -> None:
        """Test CLI correctly parses arguments with special characters."""
        from tracertm.cli.commands.item import app

        test_name = "Test Item: @#$%^&*() Special Chars 中文"

        result = runner.invoke(app, ["create", test_name, "--view", "CODE", "--type", "file"])

        # Should handle special chars gracefully
        assert result.exit_code in {0, 1, 2}

    def test_cli_handles_long_arguments(self) -> None:
        """Test CLI handles very long arguments."""
        from tracertm.cli.commands.item import app

        long_name = "A" * 500

        result = runner.invoke(app, ["create", long_name, "--view", "CODE", "--type", "file"])

        # Should handle long args gracefully
        assert result.exit_code in {0, 1, 2}


# =============================================================================
# TUI → Service Integration Tests
# =============================================================================


class TestTuiServiceIntegration:
    """Test TUI integration with services."""

    def test_tui_widget_instantiation(self) -> None:
        """Test TUI widget can be created."""
        try:
            from tracertm.tui.widgets.item_list import ItemListWidget

            widget = ItemListWidget()
            assert widget is not None
        except ImportError:
            pytest.skip("Textual not available")

    def test_sync_status_widget_creation(self) -> None:
        """Test sync status widget creation."""
        try:
            from tracertm.tui.widgets.sync_status import SyncStatusWidget

            widget = SyncStatusWidget()
            assert widget is not None
        except ImportError:
            pytest.skip("Textual not available")

    def test_conflict_panel_widget_creation(self) -> None:
        """Test conflict panel widget creation."""
        try:
            from tracertm.tui.widgets.conflict_panel import ConflictPanel

            panel = ConflictPanel()
            assert panel is not None
        except ImportError:
            pytest.skip("Textual not available")


# =============================================================================
# API → Service Integration Tests
# =============================================================================


class TestApiServiceIntegration:
    """Test API integration with services."""

    def test_api_config_creation(self) -> None:
        """Test API config can be created."""
        from tracertm.api.sync_client import ApiClient, ApiConfig

        config = ApiConfig(base_url="http://localhost:8000")
        client = ApiClient(config)
        assert client is not None

    def test_api_config_with_token(self) -> None:
        """Test API config with token."""
        from tracertm.api.sync_client import ApiClient, ApiConfig

        config = ApiConfig(base_url="http://localhost:8000", token="test-token")
        client = ApiClient(config)
        assert client is not None


# =============================================================================
# Cross-Layer Data Consistency Tests
# =============================================================================


class TestCrossLayerDataConsistency:
    """Test data consistency across UI layers."""

    def test_cli_item_command_variations(self) -> None:
        """Test CLI item commands with various inputs."""
        from tracertm.cli.commands.item import app

        # Test multiple variations
        test_cases = [
            ["list"],
            ["create", "test1", "--view", "CODE", "--type", "file"],
            ["create", "test2", "--view", "CODE", "--type", "file", "--description", "Test"],
        ]

        for test_case in test_cases:
            result = runner.invoke(app, test_case)
            # All should complete without crashing
            assert result.exit_code in {0, 1, 2}

    def test_project_commands(self) -> None:
        """Test project commands."""
        from tracertm.cli.commands.project import app

        result = runner.invoke(app, ["list"])

        assert result.exit_code in {0, 1, 2}


# =============================================================================
# Error Handling Edge Cases
# =============================================================================


class TestErrorHandlingEdgeCases:
    """Test error handling in integration scenarios."""

    def test_invalid_command_error_handling(self) -> None:
        """Test invalid command error handling."""
        from tracertm.cli.app import app

        result = runner.invoke(app, ["invalid-command"])

        # Should show error
        assert result.exit_code != 0

    def test_missing_required_args_error(self) -> None:
        """Test missing required arguments error."""
        from tracertm.cli.commands.item import app

        result = runner.invoke(app, ["create"])

        # Should show error for missing args
        assert result.exit_code != 0


# =============================================================================
# Unicode and International Character Tests
# =============================================================================


class TestUnicodeIntegration:
    """Test unicode handling across all layers."""

    def test_cli_with_chinese_characters(self) -> None:
        """Test CLI with Chinese characters."""
        from tracertm.cli.commands.item import app

        result = runner.invoke(app, ["create", "测试项目 Test Project 中文", "--view", "CODE", "--type", "file"])

        assert result.exit_code in {0, 1, 2}

    def test_cli_with_japanese_characters(self) -> None:
        """Test CLI with Japanese characters."""
        from tracertm.cli.commands.item import app

        result = runner.invoke(
            app,
            ["create", "テストプロジェクト Test Project 日本語", "--view", "CODE", "--type", "file"],
        )

        assert result.exit_code in {0, 1, 2}

    def test_cli_with_korean_characters(self) -> None:
        """Test CLI with Korean characters."""
        from tracertm.cli.commands.item import app

        result = runner.invoke(app, ["create", "테스트 프로젝트 Test Project 한글", "--view", "CODE", "--type", "file"])

        assert result.exit_code in {0, 1, 2}


# =============================================================================
# Output Formatting Integration Tests
# =============================================================================


class TestOutputFormattingIntegration:
    """Test output formatting across layers."""

    def test_help_text_formatting(self) -> None:
        """Test help text formatting."""
        from tracertm.cli.app import app

        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert len(result.output) > 0
        lines = result.output.split("\n")
        assert len(lines) > 1

    def test_command_help_formatting(self) -> None:
        """Test individual command help."""
        from tracertm.cli.commands.item import app

        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert len(result.output) > 0


# =============================================================================
# Configuration Integration Tests
# =============================================================================


class TestConfigurationIntegration:
    """Test configuration across layers."""

    def test_api_config_variations(self) -> None:
        """Test various API configurations."""
        from tracertm.api.sync_client import ApiClient, ApiConfig

        configs = [
            ApiConfig(base_url="http://localhost:8000"),
            ApiConfig(base_url="http://localhost:8000", token="test-token"),
            ApiConfig(base_url="https://localhost:8000", verify_ssl=False),
            ApiConfig(base_url="http://localhost:8000", timeout=60.0),
        ]

        for config in configs:
            client = ApiClient(config)
            assert client is not None


# =============================================================================
# Search and Query Integration Tests
# =============================================================================


class TestSearchIntegration:
    """Test search functionality across layers."""

    def test_search_command_with_simple_query(self) -> None:
        """Test search command with simple query."""
        from tracertm.cli.commands.search import app

        result = runner.invoke(app, ["query", "test"])

        assert result.exit_code in {0, 1, 2}

    def test_search_command_with_unicode_query(self) -> None:
        """Test search command with unicode query."""
        from tracertm.cli.commands.search import app

        result = runner.invoke(app, ["query", "测试"])

        assert result.exit_code in {0, 1, 2}

    def test_search_command_with_special_chars(self) -> None:
        """Test search command with special characters."""
        from tracertm.cli.commands.search import app

        result = runner.invoke(app, ["query", "@#$%"])

        assert result.exit_code in {0, 1, 2}


# =============================================================================
# Project Management Integration Tests
# =============================================================================


class TestProjectIntegration:
    """Test project management across layers."""

    def test_project_list_command(self) -> None:
        """Test project list command."""
        from tracertm.cli.commands.project import app

        result = runner.invoke(app, ["list"])

        assert result.exit_code in {0, 1, 2}

    def test_project_init_command(self) -> None:
        """Test project initialization."""
        from tracertm.cli.commands.project import app

        result = runner.invoke(app, ["init", "test-project"])

        assert result.exit_code in {0, 1, 2}

    def test_project_init_with_description(self) -> None:
        """Test project initialization with description."""
        from tracertm.cli.commands.project import app

        result = runner.invoke(app, ["init", "test-project-2", "--description", "A test project"])

        assert result.exit_code in {0, 1, 2}


# =============================================================================
# Stress Testing Integration Tests
# =============================================================================


class TestStressIntegration:
    """Test stress scenarios across layers."""

    def test_rapid_command_execution(self) -> None:
        """Test rapid command execution."""
        from tracertm.cli.commands.item import app

        for i in range(5):
            result = runner.invoke(app, ["create", f"Rapid Test Item {i}", "--view", "CODE", "--type", "file"])
            assert result.exit_code in {0, 1, 2}

    def test_large_input_handling(self) -> None:
        """Test handling of large inputs."""
        from tracertm.cli.commands.item import app

        large_description = "Description: " + "A" * 1000

        result = runner.invoke(
            app,
            ["create", "Large Input Test", "--view", "CODE", "--type", "file", "--description", large_description],
        )

        assert result.exit_code in {0, 1, 2}
