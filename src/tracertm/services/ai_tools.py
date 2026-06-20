"""AI Tool Definitions and Executors for TraceRTM Chat Assistant.

This module provides MCP-style tools that the AI can use:
- Filesystem operations (read, write, edit, glob, grep)
- Bash/CLI execution
- TraceRTM API operations
"""

from __future__ import annotations

import asyncio
import fnmatch
import logging
import os
import pathlib
import re
import subprocess
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# =============================================================================
# Tool Definitions (Claude Tool Use Format)
# =============================================================================

TOOLS = [
    # -------------------------------------------------------------------------
    # Filesystem Tools
    # -------------------------------------------------------------------------
    {
        "name": "read_file",
        "description": "Read the contents of a file. Use this to examine source code, configuration files, documentation, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read",
                },
                "offset": {
                    "type": "integer",
                    "description": "Line number to start reading from (1-indexed). Optional.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to read. Optional, defaults to 500.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Make a targeted edit to a file by replacing a specific string with new content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to edit",
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact string to find and replace (must be unique in the file)",
                },
                "new_string": {
                    "type": "string",
                    "description": "The string to replace old_string with",
                },
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories in a path. Use glob patterns to filter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to current working directory.",
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter results (e.g., '*.py', '**/*.ts'). Optional.",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to search recursively. Defaults to False.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "search_files",
        "description": "Search for a pattern in files using regex. Similar to grep.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for",
                },
                "path": {
                    "type": "string",
                    "description": "Directory or file to search in. Defaults to current working directory.",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter which files to search (e.g., '*.py'). Optional.",
                },
                "context_lines": {
                    "type": "integer",
                    "description": "Number of context lines before and after each match. Defaults to 2.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return. Defaults to 50.",
                },
            },
            "required": ["pattern"],
        },
    },
    # -------------------------------------------------------------------------
    # CLI/Bash Tool
    # -------------------------------------------------------------------------
    {
        "name": "run_command",
        "description": "Execute a bash/shell command. Use for git, npm, python, and other CLI operations. Commands run in the project's working directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute",
                },
                "working_directory": {
                    "type": "string",
                    "description": "Directory to run the command in. Optional, defaults to project root.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Defaults to 60.",
                },
            },
            "required": ["command"],
        },
    },
    # -------------------------------------------------------------------------
    # TraceRTM-Specific Tools
    # -------------------------------------------------------------------------
    {
        "name": "tracertm_list_items",
        "description": "List items (requirements, features, tests, etc.) in the current TraceRTM project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Project ID to list items from",
                },
                "view": {
                    "type": "string",
                    "description": "Filter by view type (e.g., 'FEATURE', 'REQUIREMENT', 'TEST'). Optional.",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (e.g., 'pending', 'approved', 'done'). Optional.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of items to return. Defaults to 50.",
                },
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "tracertm_get_item",
        "description": "Get detailed information about a specific item in TraceRTM.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to retrieve",
                },
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "tracertm_get_links",
        "description": "Get traceability links for an item (what it traces to/from).",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to get links for",
                },
                "direction": {
                    "type": "string",
                    "enum": ["outgoing", "incoming", "both"],
                    "description": "Direction of links to retrieve. Defaults to 'both'.",
                },
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "tracertm_impact_analysis",
        "description": "Run impact analysis to see what would be affected by changing an item.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to analyze impact for",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to traverse. Defaults to 3.",
                },
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "tracertm_search",
        "description": "Search for items in TraceRTM by title, description, or content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                },
                "project_id": {
                    "type": "string",
                    "description": "Project ID to search in. Optional.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "tracertm_create_item",
        "description": "Create a new item in TraceRTM (requirement, feature, test, etc.).",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Project ID to create the item in",
                },
                "title": {
                    "type": "string",
                    "description": "Title of the item",
                },
                "type": {
                    "type": "string",
                    "description": "Type/view of the item (e.g., 'FEATURE', 'REQUIREMENT', 'TEST')",
                },
                "description": {
                    "type": "string",
                    "description": "Description of the item. Optional.",
                },
                "status": {
                    "type": "string",
                    "description": "Initial status. Defaults to 'pending'.",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Priority level. Defaults to 'medium'.",
                },
            },
            "required": ["project_id", "title", "type"],
        },
    },
    {
        "name": "tracertm_create_link",
        "description": "Create a traceability link between two items.",
        "input_schema": {
            "type": "object",
            "properties": {
                "source_id": {
                    "type": "string",
                    "description": "ID of the source item",
                },
                "target_id": {
                    "type": "string",
                    "description": "ID of the target item",
                },
                "link_type": {
                    "type": "string",
                    "description": "Type of link (e.g., 'implements', 'tests', 'depends_on')",
                },
            },
            "required": ["source_id", "target_id", "link_type"],
        },
    },
]


# =============================================================================
# Security Configuration
# =============================================================================

# Directories that are allowed for filesystem operations
ALLOWED_PATHS: list[pathlib.Path] = []  # Empty = allow all (configure per-project)

# Commands that are blocked for security
BLOCKED_COMMANDS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf /*",
    "rm -rf .",
    "mkfs",
    ":(){:|:&};:",  # Fork bomb
    "dd if=/dev/zero",
    "dd if=/dev/random",
    "chmod -R 777 /",
    "chmod 777 /",
    "curl | sh",
    "curl | bash",
    "wget | sh",
    "wget | bash",
    "> /dev/sda",
    "> /dev/hda",
    "echo > /etc/passwd",
    "cat /dev/urandom",
    "sudo rm",
    "sudo chmod",
    "shutdown",
    "reboot",
    "init 0",
    "init 6",
    "halt",
    "poweroff",
]

# Binary file extensions to skip during search
BINARY_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".bin",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
    ".flac",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".sqlite",
    ".db",
    ".sqlite3",
}

# Maximum file size to read (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Maximum command output size (1MB)
MAX_OUTPUT_SIZE = 1 * 1024 * 1024

MAX_LIST_DIR_ENTRIES = 1000
MAX_LIST_DIR_RESULT = 500


def set_allowed_paths(paths: list[str]) -> None:
    """Configure allowed paths for filesystem operations."""
    global ALLOWED_PATHS
    ALLOWED_PATHS = [pathlib.Path(p).resolve() for p in paths]


def is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories.

    Also prevents symlink attacks by resolving the real path.
    """
    if not ALLOWED_PATHS:
        return True  # No restrictions configured

    # Resolve symlinks to prevent symlink-based attacks
    try:
        real_path = pathlib.Path(path).resolve()
    except (OSError, ValueError):
        return False

    return any(real_path.is_relative_to(allowed) for allowed in ALLOWED_PATHS)


def is_binary_file(filepath: str) -> bool:
    """Check if a file is likely binary based on extension."""
    ext = pathlib.Path(filepath).suffix.lower()
    return ext in BINARY_EXTENSIONS


def is_command_safe(command: str) -> bool:
    """Check if a command is safe to execute."""
    command_lower = command.lower()
    return not any(blocked in command_lower for blocked in BLOCKED_COMMANDS)


# =============================================================================
# Tool Executors
# =============================================================================


async def execute_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    working_directory: str | None = None,
    db_session: AsyncSession | None = None,
) -> dict[str, Any]:
    """Execute a tool and return the result.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool
        working_directory: Base directory for file operations
        db_session: Database session for TraceRTM operations

    Returns:
        Dict with 'success' bool and either 'result' or 'error'
    """
    try:
        if tool_name == "read_file":
            return _read_file(tool_input, working_directory)
        if tool_name == "write_file":
            return _write_file(tool_input, working_directory)
        if tool_name == "edit_file":
            return _edit_file(tool_input, working_directory)
        if tool_name == "list_directory":
            return _list_directory(tool_input, working_directory)
        if tool_name == "search_files":
            return _search_files(tool_input, working_directory)
        if tool_name == "run_command":
            return await _run_command(tool_input, working_directory)
        if tool_name.startswith("tracertm_"):
            return await _execute_tracertm_tool(tool_name, tool_input, db_session)
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.exception("Tool execution error: %s", tool_name)
        return {"success": False, "error": str(e)}


def _read_file(params: dict[str, Any], base_dir: str | None) -> dict[str, Any]:
    """Read file contents."""
    path_param = params["path"]
    path = pathlib.Path(str(path_param))
    if base_dir and not path.is_absolute():
        path = pathlib.Path(base_dir) / path

    if not is_path_allowed(str(path)):
        return {"success": False, "error": f"Access denied: {path}"}

    if not path.exists():
        return {"success": False, "error": f"File not found: {path}"}

    if path.stat().st_size > MAX_FILE_SIZE:
        return {"success": False, "error": f"File too large: {path}"}

    offset_param = params.get("offset", 1)
    offset = (int(str(offset_param)) if offset_param else 1) - 1  # Convert to 0-indexed
    limit_param = params.get("limit", 500)
    limit = int(str(limit_param)) if limit_param else 500

    with path.open(encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    if offset > 0:
        lines = lines[offset:]
    if limit:
        lines = lines[:limit]

    # Add line numbers
    numbered_lines = [f"{i + offset + 1:>6}\t{line.rstrip()}" for i, line in enumerate(lines)]

    return {
        "success": True,
        "result": {
            "path": path,
            "content": "\n".join(numbered_lines),
            "total_lines": len(lines),
        },
    }


def _write_file(params: dict[str, Any], base_dir: str | None) -> dict[str, Any]:
    """Write content to file."""
    path = pathlib.Path(str(params["path"]))
    content = str(params["content"])

    if base_dir and not path.is_absolute():
        path = pathlib.Path(base_dir) / path

    if not is_path_allowed(str(path)):
        return {"success": False, "error": f"Access denied: {path}"}

    # Create parent directories if needed
    path.parent.mkdir(exist_ok=True, parents=True)

    with path.open("w", encoding="utf-8") as f:
        f.write(content)

    return {
        "success": True,
        "result": {"path": str(path), "bytes_written": len(content.encode("utf-8"))},
    }


def _edit_file(params: dict[str, Any], base_dir: str | None) -> dict[str, Any]:
    """Edit file by replacing a string."""
    path = pathlib.Path(str(params["path"]))
    old_string = str(params["old_string"])
    new_string = str(params["new_string"])

    if base_dir and not path.is_absolute():
        path = pathlib.Path(base_dir) / path

    if not is_path_allowed(str(path)):
        return {"success": False, "error": f"Access denied: {path}"}

    if not path.exists():
        return {"success": False, "error": f"File not found: {path}"}

    with path.open(encoding="utf-8") as f:
        content = f.read()

    count = content.count(old_string)
    if count == 0:
        return {"success": False, "error": "String not found in file"}
    if count > 1:
        return {"success": False, "error": f"String found {count} times, must be unique"}

    new_content = content.replace(old_string, new_string, 1)

    with path.open("w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "result": {"path": path, "replacements": 1},
    }


def _list_directory(params: dict[str, Any], base_dir: str | None) -> dict[str, Any]:
    """List directory contents."""
    path_param = params.get("path", base_dir or ".")
    path = pathlib.Path(str(path_param))
    pattern_param = params.get("pattern", "*")
    pattern = str(pattern_param)
    recursive = bool(params.get("recursive"))

    if base_dir and not path.is_absolute():
        path = pathlib.Path(base_dir) / path

    if not is_path_allowed(str(path)):
        return {"success": False, "error": f"Access denied: {path}"}

    if not path.exists():
        return {"success": False, "error": f"Directory not found: {path}"}

    results = []
    # Directories to skip for performance
    skip_dirs = {"node_modules", "__pycache__", "venv", ".git", ".venv", "dist", "build", ".next", ".nuxt"}

    if recursive:
        for root, dirs, files in os.walk(path):
            # Filter out hidden and common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in skip_dirs]
            root_path = pathlib.Path(root)
            results.extend([
                {
                    "path": (root_path / name).relative_to(path),
                    "type": "directory" if (root_path / name).is_dir() else "file",
                }
                for name in files + dirs
                if fnmatch.fnmatch(name, pattern)
            ])
            if len(results) > MAX_LIST_DIR_ENTRIES:
                break
    else:
        # Use scandir for better performance (avoids extra stat calls)
        try:
            with os.scandir(path) as entries:
                results.extend([
                    {"path": entry.name, "type": "directory" if entry.is_dir() else "file"}
                    for entry in entries
                    if fnmatch.fnmatch(entry.name, pattern)
                ])
        except PermissionError:
            return {"success": False, "error": f"Permission denied: {path}"}

    return {
        "success": True,
        "result": {"path": path, "entries": results[:MAX_LIST_DIR_RESULT]},
    }


def _search_files(params: dict[str, Any], base_dir: str | None) -> dict[str, Any]:
    """Search for pattern in files."""
    pattern = str(params["pattern"])
    path_param = params.get("path", base_dir or ".")
    path = pathlib.Path(str(path_param))
    file_pattern_param = params.get("file_pattern", "*")
    file_pattern = str(file_pattern_param)
    context_lines_param = params.get("context_lines", 2)
    context_lines = int(str(context_lines_param)) if context_lines_param else 2
    max_results_param = params.get("max_results", 50)
    max_results = int(str(max_results_param)) if max_results_param else 50

    if base_dir and not path.is_absolute():
        path = pathlib.Path(base_dir) / path

    if not is_path_allowed(str(path)):
        return {"success": False, "error": f"Access denied: {path}"}

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return {"success": False, "error": f"Invalid regex: {e}"}

    results = []

    # Directories to skip for performance
    skip_dirs = {"node_modules", "__pycache__", "venv", ".git", ".venv", "dist", "build", ".next", ".nuxt"}

    for current_root, dirs, files in os.walk(path):
        # Filter directories in-place for efficiency
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in skip_dirs]
        root_path = pathlib.Path(current_root)

        for name in files:
            # Skip binary files for efficiency
            if is_binary_file(name):
                continue

            if not fnmatch.fnmatch(name, file_pattern):
                continue

            file_path = root_path / name
            rel_path = str(file_path.relative_to(path))

            # Skip large files
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            try:
                with file_path.open(encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    if regex.search(line):
                        start = max(0, i - context_lines)
                        end = min(len(lines), i + context_lines + 1)
                        context = "".join(lines[start:end])

                        results.append({
                            "file": rel_path,
                            "line": i + 1,
                            "match": line.strip(),
                            "context": context,
                        })

                        if len(results) >= max_results:
                            break
            except (OSError, UnicodeDecodeError, PermissionError) as e:
                logger.debug("Skipping file %s: %s", file_path, e)
                continue

            if len(results) >= max_results:
                break

        if len(results) >= max_results:
            break

    return {
        "success": True,
        "result": {"matches": results, "total": len(results)},
    }


async def _run_command(params: dict[str, Any], base_dir: str | None) -> dict[str, Any]:
    """Execute a shell command with security restrictions."""
    command = str(params["command"])
    working_dir_param = params.get("working_directory", base_dir or ".")
    working_dir = str(working_dir_param)
    timeout_param = params.get("timeout", 60)
    timeout = min(int(str(timeout_param)) if timeout_param else 60, 300)  # Cap at 5 minutes

    if not is_command_safe(command):
        return {"success": False, "error": "Command blocked for security reasons"}

    if base_dir and not pathlib.Path(working_dir).is_absolute():
        working_dir = str(pathlib.Path(base_dir) / working_dir)

    # Verify working directory exists
    if not await asyncio.to_thread(pathlib.Path(working_dir).is_dir):
        return {"success": False, "error": f"Working directory not found: {working_dir}"}

    # Create a sanitized environment (remove sensitive variables)
    env = os.environ.copy()
    sensitive_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_AI_KEY",
        "AWS_SECRET_ACCESS_KEY",
        "GITHUB_TOKEN",
        "DATABASE_URL",
        "SECRET_KEY",
        "JWT_SECRET",
        "PRIVATE_KEY",
    ]
    for var in sensitive_vars:
        env.pop(var, None)

    process: asyncio.subprocess.Process | None = None
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir,
            env=env,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )

        stdout_text = stdout.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]
        stderr_text = stderr.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]
    except TimeoutError:
        # Try to kill the process
        try:
            if process is not None:
                process.kill()
        except (ProcessLookupError, OSError) as e:
            logger.debug("Process kill failed: %s", e)
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except (OSError, subprocess.SubprocessError) as e:
        logger.exception("Command execution failed")
        return {"success": False, "error": str(e)}
    else:
        return {
            "success": True,
            "result": {
                "exit_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
            },
        }


async def _execute_tracertm_tool(
    tool_name: str,
    params: dict[str, Any],
    db_session: AsyncSession | None,
) -> dict[str, Any]:
    """Execute TraceRTM-specific tools."""
    # These will use the existing TraceRTM repositories/services
    # For now, return a placeholder - will be implemented with actual DB access

    if tool_name == "tracertm_list_items":
        from tracertm.repositories.item_repository import ItemRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        repo = ItemRepository(db_session)
        project_id = params["project_id"]
        limit = params.get("limit", 50)

        items = await repo.get_by_project(project_id, limit=limit)

        return {
            "success": True,
            "result": {
                "items": [
                    {
                        "id": str(item.id),
                        "title": item.title,
                        "type": getattr(item, "item_type", item.view),
                        "status": item.status,
                        "priority": getattr(item, "priority", "medium"),
                    }
                    for item in items
                ],
                "total": len(items),
            },
        }

    if tool_name == "tracertm_get_item":
        from tracertm.repositories.item_repository import ItemRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        repo = ItemRepository(db_session)
        item = await repo.get_by_id(params["item_id"])

        if not item:
            return {"success": False, "error": "Item not found"}

        return {
            "success": True,
            "result": {
                "id": str(item.id),
                "title": item.title,
                "description": item.description,
                "type": getattr(item, "item_type", item.view),
                "status": item.status,
                "priority": getattr(item, "priority", "medium"),
                "created_at": item.created_at.isoformat() if item.created_at else None,
            },
        }

    if tool_name == "tracertm_get_links":
        from tracertm.repositories.link_repository import LinkRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        link_repo = LinkRepository(db_session)
        item_id = params["item_id"]
        direction = params.get("direction", "both")

        links = []
        if direction in {"outgoing", "both"}:
            outgoing = await link_repo.get_by_source(item_id)
            links.extend([
                {"type": "outgoing", "target_id": str(link.target_item_id), "link_type": link.link_type}
                for link in outgoing
            ])
        if direction in {"incoming", "both"}:
            incoming = await link_repo.get_by_target(item_id)
            links.extend([
                {"type": "incoming", "source_id": str(link.source_item_id), "link_type": link.link_type}
                for link in incoming
            ])

        return {
            "success": True,
            "result": {"item_id": item_id, "links": links},
        }

    if tool_name == "tracertm_impact_analysis":
        from tracertm.services.impact_analysis_service import ImpactAnalysisService

        if not db_session:
            return {"success": False, "error": "Database session required"}

        impact_service = ImpactAnalysisService(db_session)
        impact_result = await impact_service.analyze_impact(params["item_id"])

        return {
            "success": True,
            "result": {
                "root_item_id": impact_result.root_item_id,
                "total_affected": impact_result.total_affected,
                "max_depth": impact_result.max_depth_reached,
                "affected_items": impact_result.affected_items[:50],  # Limit results
            },
        }

    if tool_name == "tracertm_search":
        # Simple search implementation
        from sqlalchemy import text

        from tracertm.repositories.item_repository import ItemRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        query = str(params["query"])
        project_id_param = params.get("project_id")
        project_id = str(project_id_param) if project_id_param else None

        # Use LIKE for simple search
        sql = text("""
            SELECT id, title, view, status FROM items
            WHERE (title LIKE :query OR description LIKE :query)
            AND deleted_at IS NULL
            LIMIT 50
        """)

        search_result = await db_session.execute(sql, {"query": f"%{query}%"})
        rows = search_result.fetchall()

        return {
            "success": True,
            "result": {
                "query": query,
                "results": [{"id": str(r.id), "title": r.title, "type": r.view, "status": r.status} for r in rows],
            },
        }

    if tool_name == "tracertm_create_item":
        from tracertm.repositories.item_repository import ItemRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        repo = ItemRepository(db_session)
        item_type = str(params["type"])
        item = await repo.create(
            project_id=str(params["project_id"]),
            title=str(params["title"]),
            view=item_type.upper(),
            item_type=item_type,
            description=params.get("description"),
            status=params.get("status", "pending"),
            priority=params.get("priority", "medium"),
        )
        await db_session.commit()

        return {
            "success": True,
            "result": {
                "id": str(item.id),
                "title": item.title,
                "type": item.item_type,
                "status": item.status,
            },
        }

    if tool_name == "tracertm_create_link":
        from tracertm.repositories.link_repository import LinkRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        create_link_repo = LinkRepository(db_session)
        project_id = params.get("project_id")
        if not project_id:
            return {"success": False, "error": "project_id required for tracertm_create_link"}
        link = await create_link_repo.create(
            project_id=project_id,
            source_item_id=params["source_id"],
            target_item_id=params["target_id"],
            link_type=params["link_type"],
        )
        await db_session.commit()

        return {
            "success": True,
            "result": {
                "id": str(link.id),
                "source_id": params["source_id"],
                "target_id": params["target_id"],
                "link_type": params["link_type"],
            },
        }

    return {"success": False, "error": f"Unknown TraceRTM tool: {tool_name}"}
