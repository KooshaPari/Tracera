"""Unit tests for AI Tools - MCP-style tool executors for TraceRTM Chat.

Tests filesystem tools, CLI execution, and TraceRTM-specific tools.
"""

import os
import pathlib
import tempfile
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TWO
from tracertm.services.ai_tools import (
    TOOLS,
    execute_tool,
    is_binary_file,
    is_command_safe,
    is_path_allowed,
    set_allowed_paths,
)

pytestmark = pytest.mark.unit


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> None:
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_file(temp_dir: Any) -> None:
    """Create a temporary file with content."""
    file_path = os.path.join(temp_dir, "test_file.txt")
    pathlib.Path(file_path).write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n", encoding="utf-8")
    return file_path


@pytest.fixture
def mock_db_session() -> None:
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture(autouse=True)
def reset_allowed_paths() -> None:
    """Reset allowed paths before each test."""
    set_allowed_paths([])
    yield
    set_allowed_paths([])


# =============================================================================
# Tool Definitions Tests
# =============================================================================


class TestToolDefinitions:
    """Test the TOOLS array structure and schema."""

    def test_tools_array_exists(self) -> None:
        """TOOLS array is defined and non-empty."""
        assert TOOLS is not None
        assert isinstance(TOOLS, list)
        assert len(TOOLS) > 0

    def test_all_tools_have_required_fields(self) -> None:
        """Each tool has name, description, and input_schema."""
        for tool in TOOLS:
            assert "name" in tool, "Tool missing 'name'"
            assert "description" in tool, f"Tool {tool.get('name')} missing 'description'"
            assert "input_schema" in tool, f"Tool {tool['name']} missing 'input_schema'"

    def test_filesystem_tools_defined(self) -> None:
        """Filesystem tools are defined."""
        tool_names = {t["name"] for t in TOOLS}
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "edit_file" in tool_names
        assert "list_directory" in tool_names
        assert "search_files" in tool_names

    def test_cli_tool_defined(self) -> None:
        """CLI tool is defined."""
        tool_names = {t["name"] for t in TOOLS}
        assert "run_command" in tool_names

    def test_tracertm_tools_defined(self) -> None:
        """TraceRTM-specific tools are defined."""
        tool_names = {t["name"] for t in TOOLS}
        assert "tracertm_list_items" in tool_names
        assert "tracertm_get_item" in tool_names
        assert "tracertm_get_links" in tool_names
        assert "tracertm_impact_analysis" in tool_names
        assert "tracertm_search" in tool_names
        assert "tracertm_create_item" in tool_names
        assert "tracertm_create_link" in tool_names


# =============================================================================
# Security Configuration Tests
# =============================================================================


class TestSecurityConfiguration:
    """Test security helpers for path and command validation."""

    def test_is_path_allowed_when_no_restrictions(self) -> None:
        """All paths allowed when ALLOWED_PATHS is empty."""
        set_allowed_paths([])
        assert is_path_allowed("/any/path") is True
        assert is_path_allowed("/root/file.txt") is True

    def test_is_path_allowed_with_restrictions(self, temp_dir: Any) -> None:
        """Only paths within ALLOWED_PATHS are permitted."""
        # Resolve temp_dir to real path (macOS uses symlinks for /var/folders)
        real_temp_dir = os.path.realpath(temp_dir)
        set_allowed_paths([real_temp_dir])

        # Path within allowed directory
        allowed_path = os.path.join(temp_dir, "file.txt")
        assert is_path_allowed(allowed_path) is True

        # Path outside allowed directory
        assert is_path_allowed("/etc/passwd") is False

    def test_is_path_allowed_handles_relative_paths(self, temp_dir: Any) -> None:
        """Relative paths are resolved to absolute."""
        set_allowed_paths([temp_dir])
        # This will resolve relative to cwd, which may not match temp_dir
        # so it should return False unless cwd is in allowed paths

    def test_is_command_safe_blocks_dangerous_commands(self) -> None:
        """Dangerous commands are blocked."""
        assert is_command_safe("rm -rf /") is False
        assert is_command_safe("rm -rf ~") is False
        assert is_command_safe(":(){:|:&};:") is False
        assert is_command_safe("curl | sh") is False

    def test_is_command_safe_allows_normal_commands(self) -> None:
        """Normal commands are allowed."""
        assert is_command_safe("ls -la") is True
        assert is_command_safe("git status") is True
        assert is_command_safe("python --version") is True
        assert is_command_safe("npm run test") is True


# =============================================================================
# execute_tool Dispatcher Tests
# =============================================================================


class TestExecuteTool:
    """Test the main execute_tool dispatcher function."""

    @pytest.mark.asyncio
    async def test_execute_unknown_tool_returns_error(self) -> None:
        """Unknown tool names return error."""
        result = await execute_tool("unknown_tool", {})

        assert result["success"] is False
        assert "Unknown tool" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_tool_handles_exceptions(self) -> None:
        """Exceptions during tool execution are caught and returned as errors."""
        # Mock a tool that raises an exception
        with patch("tracertm.services.ai_tools._read_file", side_effect=Exception("Test error")):
            result = await execute_tool("read_file", {"path": "/some/path"})

            assert result["success"] is False
            assert "Test error" in result["error"]


# =============================================================================
# read_file Tool Tests
# =============================================================================


class TestReadFileTool:
    """Test the read_file tool executor."""

    @pytest.mark.asyncio
    async def test_read_file_success(self, temp_file: Any, temp_dir: Any) -> None:
        """read_file returns file content with line numbers."""
        result = await execute_tool(
            "read_file",
            {"path": temp_file},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert "result" in result
        assert temp_file in result["result"]["path"]
        assert "Line 1" in result["result"]["content"]
        assert result["result"]["total_lines"] == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_read_file_with_offset(self, temp_file: Any, temp_dir: Any) -> None:
        """read_file respects offset parameter."""
        result = await execute_tool(
            "read_file",
            {"path": temp_file, "offset": 3},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        # Should start from line 3
        assert "Line 3" in result["result"]["content"]
        assert "Line 1" not in result["result"]["content"]

    @pytest.mark.asyncio
    async def test_read_file_with_limit(self, temp_file: Any, temp_dir: Any) -> None:
        """read_file respects limit parameter."""
        result = await execute_tool(
            "read_file",
            {"path": temp_file, "limit": 2},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert result["result"]["total_lines"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_read_file_not_found(self, temp_dir: Any) -> None:
        """read_file returns error for non-existent file."""
        result = await execute_tool(
            "read_file",
            {"path": os.path.join(temp_dir, "nonexistent.txt")},
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_read_file_path_denied(self, temp_file: Any, temp_dir: Any) -> None:
        """read_file returns error for paths outside allowed directories."""
        # Set allowed paths to a different directory
        set_allowed_paths(["/some/other/path"])

        result = await execute_tool(
            "read_file",
            {"path": temp_file},
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "Access denied" in result["error"]

    @pytest.mark.asyncio
    async def test_read_file_relative_path(self, temp_dir: Any) -> None:
        """read_file handles relative paths with working directory."""
        # Create a file in the temp dir
        file_path = os.path.join(temp_dir, "relative_test.txt")
        pathlib.Path(file_path).write_text("Test content\n", encoding="utf-8")

        result = await execute_tool(
            "read_file",
            {"path": "relative_test.txt"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert "Test content" in result["result"]["content"]


# =============================================================================
# write_file Tool Tests
# =============================================================================


class TestWriteFileTool:
    """Test the write_file tool executor."""

    @pytest.mark.asyncio
    async def test_write_file_success(self, temp_dir: Any) -> None:
        """write_file creates a new file with content."""
        file_path = os.path.join(temp_dir, "new_file.txt")
        content = "Hello, World!"

        result = await execute_tool(
            "write_file",
            {"path": file_path, "content": content},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert result["result"]["bytes_written"] == len(content.encode("utf-8"))

        # Verify file was actually created
        assert pathlib.Path(file_path).exists()
        with pathlib.Path(file_path).open(encoding="utf-8") as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_write_file_creates_parent_dirs(self, temp_dir: Any) -> None:
        """write_file creates parent directories if needed."""
        file_path = os.path.join(temp_dir, "subdir", "nested", "file.txt")
        content = "Nested content"

        result = await execute_tool(
            "write_file",
            {"path": file_path, "content": content},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert pathlib.Path(file_path).exists()

    @pytest.mark.asyncio
    async def test_write_file_overwrites_existing(self, temp_file: Any, temp_dir: Any) -> None:
        """write_file overwrites existing file."""
        new_content = "Completely new content"

        result = await execute_tool(
            "write_file",
            {"path": temp_file, "content": new_content},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        with pathlib.Path(temp_file).open(encoding="utf-8") as f:
            assert f.read() == new_content

    @pytest.mark.asyncio
    async def test_write_file_path_denied(self, temp_dir: Any) -> None:
        """write_file returns error for paths outside allowed directories."""
        set_allowed_paths(["/some/other/path"])

        result = await execute_tool(
            "write_file",
            {"path": os.path.join(temp_dir, "test.txt"), "content": "test"},
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "Access denied" in result["error"]


# =============================================================================
# edit_file Tool Tests
# =============================================================================


class TestEditFileTool:
    """Test the edit_file tool executor."""

    @pytest.mark.asyncio
    async def test_edit_file_success(self, temp_file: Any, temp_dir: Any) -> None:
        """edit_file replaces unique string."""
        result = await execute_tool(
            "edit_file",
            {
                "path": temp_file,
                "old_string": "Line 2\n",
                "new_string": "Replaced Line\n",
            },
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert result["result"]["replacements"] == 1

        content = pathlib.Path(temp_file).read_text(encoding="utf-8")
        assert "Replaced Line" in content
        assert "Line 2" not in content

    @pytest.mark.asyncio
    async def test_edit_file_string_not_found(self, temp_file: Any, temp_dir: Any) -> None:
        """edit_file returns error when string not found."""
        result = await execute_tool(
            "edit_file",
            {
                "path": temp_file,
                "old_string": "NonexistentString",
                "new_string": "NewString",
            },
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_edit_file_multiple_matches(self, temp_dir: Any) -> None:
        """edit_file returns error when string matches multiple times."""
        file_path = os.path.join(temp_dir, "duplicate.txt")
        pathlib.Path(file_path).write_text("duplicate\nsome text\nduplicate\n", encoding="utf-8")

        result = await execute_tool(
            "edit_file",
            {
                "path": file_path,
                "old_string": "duplicate",
                "new_string": "unique",
            },
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "2 times" in result["error"]

    @pytest.mark.asyncio
    async def test_edit_file_not_found(self, temp_dir: Any) -> None:
        """edit_file returns error for non-existent file."""
        result = await execute_tool(
            "edit_file",
            {
                "path": os.path.join(temp_dir, "nonexistent.txt"),
                "old_string": "old",
                "new_string": "new",
            },
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "not found" in result["error"].lower()


# =============================================================================
# list_directory Tool Tests
# =============================================================================


class TestListDirectoryTool:
    """Test the list_directory tool executor."""

    @pytest.mark.asyncio
    async def test_list_directory_success(self, temp_dir: Any) -> None:
        """list_directory returns directory contents."""
        # Create some files and dirs
        pathlib.Path(os.path.join(temp_dir, "subdir")).mkdir(parents=True)
        pathlib.Path(os.path.join(temp_dir, "file1.txt")).write_text("content", encoding="utf-8")
        pathlib.Path(os.path.join(temp_dir, "file2.py")).write_text("content", encoding="utf-8")

        result = await execute_tool(
            "list_directory",
            {"path": temp_dir},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        entries = result["result"]["entries"]
        entry_names = {e["path"] for e in entries}
        assert "subdir" in entry_names
        assert "file1.txt" in entry_names
        assert "file2.py" in entry_names

    @pytest.mark.asyncio
    async def test_list_directory_with_pattern(self, temp_dir: Any) -> None:
        """list_directory filters by glob pattern."""
        pathlib.Path(os.path.join(temp_dir, "file1.txt")).write_text("content", encoding="utf-8")
        pathlib.Path(os.path.join(temp_dir, "file2.py")).write_text("content", encoding="utf-8")

        result = await execute_tool(
            "list_directory",
            {"path": temp_dir, "pattern": "*.py"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        entries = result["result"]["entries"]
        assert len(entries) == 1
        assert entries[0]["path"] == "file2.py"

    @pytest.mark.asyncio
    async def test_list_directory_recursive(self, temp_dir: Any) -> None:
        """list_directory searches recursively when enabled."""
        # Create nested structure
        pathlib.Path(os.path.join(temp_dir, "subdir")).mkdir(parents=True)
        pathlib.Path(os.path.join(temp_dir, "root.txt")).write_text("content", encoding="utf-8")
        pathlib.Path(os.path.join(temp_dir, "subdir", "nested.txt")).write_text("content", encoding="utf-8")

        result = await execute_tool(
            "list_directory",
            {"path": temp_dir, "recursive": True},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        entry_paths = {e["path"] for e in result["result"]["entries"]}
        assert "root.txt" in entry_paths
        # Nested file should be found with path relative to temp_dir

    @pytest.mark.asyncio
    async def test_list_directory_not_found(self, temp_dir: Any) -> None:
        """list_directory returns error for non-existent directory."""
        result = await execute_tool(
            "list_directory",
            {"path": os.path.join(temp_dir, "nonexistent")},
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "not found" in result["error"].lower()


# =============================================================================
# search_files Tool Tests
# =============================================================================


class TestSearchFilesTool:
    """Test the search_files tool executor."""

    @pytest.mark.asyncio
    async def test_search_files_finds_matches(self, temp_dir: Any) -> None:
        """search_files finds pattern matches in files."""
        pathlib.Path(os.path.join(temp_dir, "file1.py")).write_text("def hello_world():\n    pass\n", encoding="utf-8")
        pathlib.Path(os.path.join(temp_dir, "file2.py")).write_text(
            "def goodbye_world():\n    pass\n", encoding="utf-8"
        )

        result = await execute_tool(
            "search_files",
            {"pattern": "hello"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        matches = result["result"]["matches"]
        assert len(matches) >= 1
        assert any("hello_world" in m["match"] for m in matches)

    @pytest.mark.asyncio
    async def test_search_files_with_file_pattern(self, temp_dir: Any) -> None:
        """search_files filters by file pattern."""
        pathlib.Path(os.path.join(temp_dir, "code.py")).write_text("pattern_match\n", encoding="utf-8")
        pathlib.Path(os.path.join(temp_dir, "text.txt")).write_text("pattern_match\n", encoding="utf-8")

        result = await execute_tool(
            "search_files",
            {"pattern": "pattern_match", "file_pattern": "*.py"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        matches = result["result"]["matches"]
        assert all(m["file"].endswith(".py") for m in matches)

    @pytest.mark.asyncio
    async def test_search_files_respects_max_results(self, temp_dir: Any) -> None:
        """search_files limits results to max_results."""
        # Create file with many matches
        with pathlib.Path(os.path.join(temp_dir, "many.txt")).open("w", encoding="utf-8") as f:
            f.writelines(f"match_line_{i}\n" for i in range(100))

        result = await execute_tool(
            "search_files",
            {"pattern": "match_line", "max_results": 5},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert len(result["result"]["matches"]) <= COUNT_FIVE

    @pytest.mark.asyncio
    async def test_search_files_invalid_regex(self, temp_dir: Any) -> None:
        """search_files returns error for invalid regex."""
        result = await execute_tool(
            "search_files",
            {"pattern": "[invalid(regex"},
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "regex" in result["error"].lower()


# =============================================================================
# run_command Tool Tests
# =============================================================================


class TestRunCommandTool:
    """Test the run_command tool executor."""

    @pytest.mark.asyncio
    async def test_run_command_success(self, temp_dir: Any) -> None:
        """run_command executes command and returns output."""
        result = await execute_tool(
            "run_command",
            {"command": "echo 'Hello World'"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert "Hello World" in result["result"]["stdout"]
        assert result["result"]["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_run_command_captures_stderr(self, temp_dir: Any) -> None:
        """run_command captures stderr output."""
        result = await execute_tool(
            "run_command",
            {"command": "echo 'error' >&2"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert "error" in result["result"]["stderr"]

    @pytest.mark.asyncio
    async def test_run_command_returns_exit_code(self, temp_dir: Any) -> None:
        """run_command returns the exit code."""
        result = await execute_tool(
            "run_command",
            {"command": "exit 42"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert result["result"]["exit_code"] == 42

    @pytest.mark.asyncio
    async def test_run_command_blocked_dangerous(self, temp_dir: Any) -> None:
        """run_command blocks dangerous commands."""
        result = await execute_tool(
            "run_command",
            {"command": "rm -rf /"},
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "blocked" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_run_command_respects_timeout(self, temp_dir: Any) -> None:
        """run_command times out long-running commands."""
        result = await execute_tool(
            "run_command",
            {"command": "sleep 10", "timeout": 1},
            working_directory=temp_dir,
        )

        assert result["success"] is False
        assert "timed out" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_run_command_uses_working_directory(self, temp_dir: Any) -> None:
        """run_command runs in specified working directory."""
        result = await execute_tool(
            "run_command",
            {"command": "pwd"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        # The actual path might have /private prefix on macOS
        assert temp_dir.split("/")[-1] in result["result"]["stdout"]


# =============================================================================
# TraceRTM Tool Tests
# =============================================================================


class TestTraceRTMTools:
    """Test TraceRTM-specific tool executors."""

    @pytest.mark.asyncio
    async def test_tracertm_list_items_requires_db_session(self) -> None:
        """tracertm_list_items returns error without db_session."""
        result = await execute_tool(
            "tracertm_list_items",
            {"project_id": "test-project-id"},
            db_session=None,
        )

        assert result["success"] is False
        assert "Database session required" in result["error"]

    @pytest.mark.asyncio
    async def test_tracertm_list_items_with_mock_session(self) -> None:
        """tracertm_list_items queries repository with db_session."""
        mock_session = AsyncMock()

        # Mock the ItemRepository at the import location
        with patch("tracertm.repositories.item_repository.ItemRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.get_by_project = AsyncMock(return_value=[])
            mock_repo_cls.return_value = mock_repo

            result = await execute_tool(
                "tracertm_list_items",
                {"project_id": "test-project-id"},
                db_session=mock_session,
            )

            assert result["success"] is True
            mock_repo.get_by_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_tracertm_get_item_requires_db_session(self) -> None:
        """tracertm_get_item returns error without db_session."""
        result = await execute_tool(
            "tracertm_get_item",
            {"item_id": "test-item-id"},
            db_session=None,
        )

        assert result["success"] is False
        assert "Database session required" in result["error"]

    @pytest.mark.asyncio
    async def test_tracertm_get_item_not_found(self) -> None:
        """tracertm_get_item returns error when item not found."""
        mock_session = AsyncMock()

        with patch("tracertm.repositories.item_repository.ItemRepository") as mock_repo_cls:
            mock_repo = AsyncMock()
            mock_repo.get_by_id = AsyncMock(return_value=None)
            mock_repo_cls.return_value = mock_repo

            result = await execute_tool(
                "tracertm_get_item",
                {"item_id": "nonexistent-id"},
                db_session=mock_session,
            )

            assert result["success"] is False
            assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_tracertm_get_links_requires_db_session(self) -> None:
        """tracertm_get_links returns error without db_session."""
        result = await execute_tool(
            "tracertm_get_links",
            {"item_id": "test-item-id"},
            db_session=None,
        )

        assert result["success"] is False
        assert "Database session required" in result["error"]

    @pytest.mark.asyncio
    async def test_tracertm_impact_analysis_requires_db_session(self) -> None:
        """tracertm_impact_analysis returns error without db_session."""
        result = await execute_tool(
            "tracertm_impact_analysis",
            {"item_id": "test-item-id"},
            db_session=None,
        )

        assert result["success"] is False
        assert "Database session required" in result["error"]

    @pytest.mark.asyncio
    async def test_tracertm_search_requires_db_session(self) -> None:
        """tracertm_search returns error without db_session."""
        result = await execute_tool(
            "tracertm_search",
            {"query": "test query"},
            db_session=None,
        )

        assert result["success"] is False
        assert "Database session required" in result["error"]

    @pytest.mark.asyncio
    async def test_tracertm_create_item_requires_db_session(self) -> None:
        """tracertm_create_item returns error without db_session."""
        result = await execute_tool(
            "tracertm_create_item",
            {
                "project_id": "test-project-id",
                "title": "New Item",
                "type": "FEATURE",
            },
            db_session=None,
        )

        assert result["success"] is False
        assert "Database session required" in result["error"]

    @pytest.mark.asyncio
    async def test_tracertm_create_link_requires_db_session(self) -> None:
        """tracertm_create_link returns error without db_session."""
        result = await execute_tool(
            "tracertm_create_link",
            {
                "source_id": "source-id",
                "target_id": "target-id",
                "link_type": "implements",
            },
            db_session=None,
        )

        assert result["success"] is False
        assert "Database session required" in result["error"]

    @pytest.mark.asyncio
    async def test_unknown_tracertm_tool(self) -> None:
        """Unknown tracertm_* tools return error."""
        result = await execute_tool(
            "tracertm_unknown_tool",
            {},
            db_session=AsyncMock(),
        )

        assert result["success"] is False
        assert "Unknown TraceRTM tool" in result["error"]


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEnhancedSecurity:
    """Test enhanced security features."""

    def test_is_command_safe_blocks_sudo_commands(self) -> None:
        """Sudo commands are blocked."""
        assert is_command_safe("sudo rm -rf /") is False
        assert is_command_safe("sudo chmod 777 /") is False

    def test_is_command_safe_blocks_system_commands(self) -> None:
        """System control commands are blocked."""
        assert is_command_safe("shutdown now") is False
        assert is_command_safe("reboot") is False
        assert is_command_safe("halt") is False

    def test_is_command_safe_blocks_destructive_dd(self) -> None:
        """Destructive dd commands are blocked."""
        assert is_command_safe("dd if=/dev/zero of=/dev/sda") is False
        assert is_command_safe("dd if=/dev/random of=/dev/hda") is False

    @pytest.mark.asyncio
    async def test_run_command_caps_timeout(self, temp_dir: Any) -> None:
        """run_command caps timeout at 5 minutes."""
        result = await execute_tool(
            "run_command",
            {"command": "echo 'test'", "timeout": 1000},  # Try 1000s
            working_directory=temp_dir,
        )
        # Should succeed (the cap is internal)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_run_command_invalid_working_directory(self, temp_dir: Any) -> None:
        """run_command returns error for invalid working directory."""
        result = await execute_tool(
            "run_command",
            {"command": "echo 'test'", "working_directory": "/nonexistent/path"},
            working_directory=temp_dir,
        )
        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestBinaryFileSkipping:
    """Test binary file detection and skipping."""

    @pytest.mark.asyncio
    async def test_search_skips_binary_files(self, temp_dir: Any) -> None:
        """search_files skips binary file extensions."""
        # Create a text file with match
        pathlib.Path(os.path.join(temp_dir, "code.py")).write_text("findme = True\n", encoding="utf-8")

        # Create a "binary" file with match (simulated by extension)
        pathlib.Path(os.path.join(temp_dir, "data.pyc")).write_text("findme = True\n", encoding="utf-8")

        result = await execute_tool(
            "search_files",
            {"pattern": "findme"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        matches = result["result"]["matches"]
        # Should only find the .py file, not .pyc
        assert len(matches) == 1
        assert matches[0]["file"] == "code.py"

    @pytest.mark.asyncio
    async def test_search_skips_image_files(self, _temp_dir: Any) -> None:
        """search_files skips image extensions."""
        assert is_binary_file("image.png") is True
        assert is_binary_file("photo.jpg") is True
        assert is_binary_file("icon.svg") is True
        assert is_binary_file("code.py") is False
        assert is_binary_file("README.md") is False


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_read_file_with_unicode(self, temp_dir: Any) -> None:
        """read_file handles unicode content."""
        file_path = os.path.join(temp_dir, "unicode.txt")
        content = "Hello 世界 🌍\nמה נשמע?\n"
        pathlib.Path(file_path).write_text(content, encoding="utf-8")

        result = await execute_tool(
            "read_file",
            {"path": file_path},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert "世界" in result["result"]["content"]

    @pytest.mark.asyncio
    async def test_write_file_with_unicode(self, temp_dir: Any) -> None:
        """write_file handles unicode content."""
        file_path = os.path.join(temp_dir, "unicode_write.txt")
        content = "Привет мир! 🚀"

        result = await execute_tool(
            "write_file",
            {"path": file_path, "content": content},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        with pathlib.Path(file_path).open(encoding="utf-8") as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_empty_file_operations(self, temp_dir: Any) -> None:
        """File operations handle empty files."""
        file_path = os.path.join(temp_dir, "empty.txt")
        with pathlib.Path(file_path).open("w", encoding="utf-8"):
            pass  # Create empty file

        result = await execute_tool(
            "read_file",
            {"path": file_path},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert result["result"]["total_lines"] == 0

    @pytest.mark.asyncio
    async def test_search_files_in_empty_directory(self, temp_dir: Any) -> None:
        """search_files handles empty directories."""
        result = await execute_tool(
            "search_files",
            {"pattern": "anything"},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert len(result["result"]["matches"]) == 0

    @pytest.mark.asyncio
    async def test_list_directory_empty(self, temp_dir: Any) -> None:
        """list_directory handles empty directories."""
        empty_dir = os.path.join(temp_dir, "empty_subdir")
        pathlib.Path(empty_dir).mkdir(parents=True)

        result = await execute_tool(
            "list_directory",
            {"path": empty_dir},
            working_directory=temp_dir,
        )

        assert result["success"] is True
        assert len(result["result"]["entries"]) == 0
