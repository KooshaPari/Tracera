"""AI Tool Definitions and Executors for TraceRTM Chat Assistant.

This module provides MCP-style tools that the AI can use:
- Filesystem operations (read, write, edit, glob, grep)
- Bash/CLI execution
- TraceRTM API operations
"""

import asyncio
import fnmatch
import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any

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
ALLOWED_PATHS: list[str] = []  # Empty = allow all (configure per-project)

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
    ".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".sqlite", ".db", ".sqlite3",
}

# Maximum file size to read (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Maximum command output size (1MB)
MAX_OUTPUT_SIZE = 1 * 1024 * 1024


def set_allowed_paths(paths: list[str]) -> None:
    """Configure allowed paths for filesystem operations."""
    global ALLOWED_PATHS
    ALLOWED_PATHS = [os.path.abspath(p) for p in paths]


def is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories.

    Also prevents symlink attacks by resolving the real path.
    """
    if not ALLOWED_PATHS:
        return True  # No restrictions configured

    # Resolve symlinks to prevent symlink-based attacks
    try:
        real_path = os.path.realpath(path)
    except (OSError, ValueError):
        return False

    return any(real_path.startswith(allowed) for allowed in ALLOWED_PATHS)


def is_binary_file(filepath: str) -> bool:
    """Check if a file is likely binary based on extension."""
    _, ext = os.path.splitext(filepath.lower())
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
    db_session: Any = None,
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
            return await _read_file(tool_input, working_directory)
        elif tool_name == "write_file":
            return await _write_file(tool_input, working_directory)
        elif tool_name == "edit_file":
            return await _edit_file(tool_input, working_directory)
        elif tool_name == "list_directory":
            return await _list_directory(tool_input, working_directory)
        elif tool_name == "search_files":
            return await _search_files(tool_input, working_directory)
        elif tool_name == "run_command":
            return await _run_command(tool_input, working_directory)
        elif tool_name.startswith("tracertm_"):
            return await _execute_tracertm_tool(tool_name, tool_input, db_session)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error(f"Tool execution error: {tool_name}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def _read_file(params: dict, base_dir: str | None) -> dict:
    """Read file contents."""
    path = params["path"]
    if base_dir and not os.path.isabs(path):
        path = os.path.join(base_dir, path)

    if not is_path_allowed(path):
        return {"success": False, "error": f"Access denied: {path}"}

    if not os.path.exists(path):
        return {"success": False, "error": f"File not found: {path}"}

    if os.path.getsize(path) > MAX_FILE_SIZE:
        return {"success": False, "error": f"File too large: {path}"}

    offset = params.get("offset", 1) - 1  # Convert to 0-indexed
    limit = params.get("limit", 500)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    if offset > 0:
        lines = lines[offset:]
    if limit:
        lines = lines[:limit]

    # Add line numbers
    numbered_lines = [
        f"{i + offset + 1:>6}\t{line.rstrip()}"
        for i, line in enumerate(lines)
    ]

    return {
        "success": True,
        "result": {
            "path": path,
            "content": "\n".join(numbered_lines),
            "total_lines": len(lines),
        },
    }


async def _write_file(params: dict, base_dir: str | None) -> dict:
    """Write content to file."""
    path = params["path"]
    content = params["content"]

    if base_dir and not os.path.isabs(path):
        path = os.path.join(base_dir, path)

    if not is_path_allowed(path):
        return {"success": False, "error": f"Access denied: {path}"}

    # Create parent directories if needed
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "success": True,
        "result": {"path": path, "bytes_written": len(content.encode("utf-8"))},
    }


async def _edit_file(params: dict, base_dir: str | None) -> dict:
    """Edit file by replacing a string."""
    path = params["path"]
    old_string = params["old_string"]
    new_string = params["new_string"]

    if base_dir and not os.path.isabs(path):
        path = os.path.join(base_dir, path)

    if not is_path_allowed(path):
        return {"success": False, "error": f"Access denied: {path}"}

    if not os.path.exists(path):
        return {"success": False, "error": f"File not found: {path}"}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    count = content.count(old_string)
    if count == 0:
        return {"success": False, "error": "String not found in file"}
    if count > 1:
        return {"success": False, "error": f"String found {count} times, must be unique"}

    new_content = content.replace(old_string, new_string, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "result": {"path": path, "replacements": 1},
    }


async def _list_directory(params: dict, base_dir: str | None) -> dict:
    """List directory contents."""
    path = params.get("path", base_dir or ".")
    pattern = params.get("pattern", "*")
    recursive = params.get("recursive", False)

    if base_dir and not os.path.isabs(path):
        path = os.path.join(base_dir, path)

    if not is_path_allowed(path):
        return {"success": False, "error": f"Access denied: {path}"}

    if not os.path.exists(path):
        return {"success": False, "error": f"Directory not found: {path}"}

    results = []
    # Directories to skip for performance
    skip_dirs = {"node_modules", "__pycache__", "venv", ".git", ".venv", "dist", "build", ".next", ".nuxt"}

    if recursive:
        for root, dirs, files in os.walk(path):
            # Filter out hidden and common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in skip_dirs]
            for name in files + dirs:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, path)
                if fnmatch.fnmatch(name, pattern):
                    is_dir = os.path.isdir(full_path)
                    results.append({
                        "path": rel_path,
                        "type": "directory" if is_dir else "file",
                    })
            if len(results) > 1000:
                break
    else:
        # Use scandir for better performance (avoids extra stat calls)
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if fnmatch.fnmatch(entry.name, pattern):
                        results.append({
                            "path": entry.name,
                            "type": "directory" if entry.is_dir() else "file",
                        })
        except PermissionError:
            return {"success": False, "error": f"Permission denied: {path}"}

    return {
        "success": True,
        "result": {"path": path, "entries": results[:500]},
    }


async def _search_files(params: dict, base_dir: str | None) -> dict:
    """Search for pattern in files."""
    pattern = params["pattern"]
    path = params.get("path", base_dir or ".")
    file_pattern = params.get("file_pattern", "*")
    context_lines = params.get("context_lines", 2)
    max_results = params.get("max_results", 50)

    if base_dir and not os.path.isabs(path):
        path = os.path.join(base_dir, path)

    if not is_path_allowed(path):
        return {"success": False, "error": f"Access denied: {path}"}

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return {"success": False, "error": f"Invalid regex: {e}"}

    results = []

    # Directories to skip for performance
    skip_dirs = {"node_modules", "__pycache__", "venv", ".git", ".venv", "dist", "build", ".next", ".nuxt"}

    for root, dirs, files in os.walk(path):
        # Filter directories in-place for efficiency
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in skip_dirs]

        for name in files:
            # Skip binary files for efficiency
            if is_binary_file(name):
                continue

            if not fnmatch.fnmatch(name, file_pattern):
                continue

            file_path = os.path.join(root, name)
            rel_path = os.path.relpath(file_path, path)

            # Skip large files
            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
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
            except Exception:
                continue

            if len(results) >= max_results:
                break

        if len(results) >= max_results:
            break

    return {
        "success": True,
        "result": {"matches": results, "total": len(results)},
    }


async def _run_command(params: dict, base_dir: str | None) -> dict:
    """Execute a shell command with security restrictions."""
    command = params["command"]
    working_dir = params.get("working_directory", base_dir or ".")
    timeout = min(params.get("timeout", 60), 300)  # Cap at 5 minutes

    if not is_command_safe(command):
        return {"success": False, "error": "Command blocked for security reasons"}

    if base_dir and not os.path.isabs(working_dir):
        working_dir = os.path.join(base_dir, working_dir)

    # Verify working directory exists
    if not os.path.isdir(working_dir):
        return {"success": False, "error": f"Working directory not found: {working_dir}"}

    # Create a sanitized environment (remove sensitive variables)
    env = os.environ.copy()
    sensitive_vars = [
        "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_AI_KEY",
        "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "DATABASE_URL",
        "SECRET_KEY", "JWT_SECRET", "PRIVATE_KEY",
    ]
    for var in sensitive_vars:
        env.pop(var, None)

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
            env=env,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )

        stdout_text = stdout.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]
        stderr_text = stderr.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]

        return {
            "success": True,
            "result": {
                "exit_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
            },
        }
    except asyncio.TimeoutError:
        # Try to kill the process
        try:
            process.kill()
        except Exception:
            pass
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _execute_tracertm_tool(
    tool_name: str,
    params: dict,
    db_session: Any,
) -> dict:
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

    elif tool_name == "tracertm_get_item":
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

    elif tool_name == "tracertm_get_links":
        from tracertm.repositories.link_repository import LinkRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        repo = LinkRepository(db_session)
        item_id = params["item_id"]
        direction = params.get("direction", "both")

        links = []
        if direction in ("outgoing", "both"):
            outgoing = await repo.get_by_source(item_id)
            links.extend([
                {"type": "outgoing", "target_id": str(l.target_item_id), "link_type": l.link_type}
                for l in outgoing
            ])
        if direction in ("incoming", "both"):
            incoming = await repo.get_by_target(item_id)
            links.extend([
                {"type": "incoming", "source_id": str(l.source_item_id), "link_type": l.link_type}
                for l in incoming
            ])

        return {
            "success": True,
            "result": {"item_id": item_id, "links": links},
        }

    elif tool_name == "tracertm_impact_analysis":
        from tracertm.services.impact_analysis_service import ImpactAnalysisService

        if not db_session:
            return {"success": False, "error": "Database session required"}

        service = ImpactAnalysisService(db_session)
        result = await service.analyze_impact(params["item_id"])

        return {
            "success": True,
            "result": {
                "root_item_id": result.root_item_id,
                "total_affected": result.total_affected,
                "max_depth": result.max_depth_reached,
                "affected_items": result.affected_items[:50],  # Limit results
            },
        }

    elif tool_name == "tracertm_search":
        # Simple search implementation
        from tracertm.repositories.item_repository import ItemRepository
        from sqlalchemy import text

        if not db_session:
            return {"success": False, "error": "Database session required"}

        query = params["query"]
        project_id = params.get("project_id")

        # Use LIKE for simple search
        sql = text("""
            SELECT id, title, view, status FROM items
            WHERE (title LIKE :query OR description LIKE :query)
            AND deleted_at IS NULL
            LIMIT 50
        """)

        result = await db_session.execute(sql, {"query": f"%{query}%"})
        rows = result.fetchall()

        return {
            "success": True,
            "result": {
                "query": query,
                "results": [
                    {"id": str(r.id), "title": r.title, "type": r.view, "status": r.status}
                    for r in rows
                ],
            },
        }

    elif tool_name == "tracertm_create_item":
        from tracertm.repositories.item_repository import ItemRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        repo = ItemRepository(db_session)
        item = await repo.create(
            project_id=params["project_id"],
            title=params["title"],
            view=params["type"].upper(),
            item_type=params["type"],
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

    elif tool_name == "tracertm_create_link":
        from tracertm.repositories.link_repository import LinkRepository

        if not db_session:
            return {"success": False, "error": "Database session required"}

        repo = LinkRepository(db_session)
        link = await repo.create(
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
