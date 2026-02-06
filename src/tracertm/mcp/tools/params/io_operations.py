"""Import/Export/Ingestion MCP tools."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import yaml
from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except Exception:  # pragma: no cover

    class _StubMCP:
        def tool(self, *args: Any, **kwargs: Any):
            def decorator(fn):
                return fn

            return decorator

    mcp = _StubMCP()

from tracertm.cli.commands import export as export_cmd
from tracertm.cli.commands import import_cmd as import_cmd_module
from tracertm.config.manager import ConfigManager
from tracertm.services.stateless_ingestion_service import StatelessIngestionService
from tracertm.storage.local_storage import LocalStorageManager

from .common import _wrap


def _path_write_text(path_str: str, content: str, encoding: str = "utf-8") -> None:
    """Sync helper: write text to path (run via asyncio.to_thread)."""
    Path(path_str).write_text(content, encoding=encoding)


def _load_data_from_path(path: str) -> Any:
    """Sync helper: load import data from file path (run via asyncio.to_thread)."""
    p = Path(path)
    if not p.exists():
        raise ToolError(f"File not found: {path}")
    if p.suffix.lower() in {".yaml", ".yml"}:
        result = yaml.safe_load(p.read_text(encoding="utf-8"))
        if result is None:
            raise ToolError(f"Failed to parse YAML file: {path}")
        return result
    return json.loads(p.read_text(encoding="utf-8"))


def _load_data_from_payload(payload: dict[str, Any]) -> Any:
    """Load import data from payload (data/content)."""
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    content = payload.get("content")
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            result = yaml.safe_load(content)
            if result is None:
                raise ToolError("Failed to parse YAML content")
            return result
    raise ToolError("Provide data, content, or path for import.")


async def _get_import_data(payload: dict[str, Any]) -> Any:
    """Load import data, handling file paths when provided."""
    path = payload.get("path")
    if path:
        return await asyncio.to_thread(_load_data_from_path, path)
    return _load_data_from_payload(payload)


def _wrap_validation(
    errors: list[str],
    warnings: list[str] | None,
    ctx: Any | None,
    action: str,
) -> dict[str, Any]:
    """Wrap validation results."""
    return _wrap(
        {"errors": errors, "warnings": warnings or [], "valid": len(errors) == 0},
        ctx,
        action,
    )


def _validate_import_or_wrap(data: Any, ctx: Any | None, action: str) -> dict[str, Any] | None:
    """Validate import data and return wrapped errors if invalid."""
    errors, warnings = import_cmd_module._validate_import_data(data)
    if errors:
        return _wrap_validation(errors, warnings, ctx, action)
    return None


def _handle_import_full(
    data: Any,
    ctx: Any | None,
    action: str,
) -> dict[str, Any]:
    invalid = _validate_import_or_wrap(data, ctx, action)
    if invalid is not None:
        return invalid
    if not data.get("project") or not isinstance(data.get("items"), list):
        return _wrap({"errors": ["Canonical format requires project and items"], "valid": False}, ctx, action)
    import_cmd_module._import_data(data, None, "full")
    return _wrap(
        {
            "imported": True,
            "source": "full",
            "project": data.get("project", {}).get("name"),
            "items": len(data.get("items", [])),
            "links": len(data.get("links", [])),
        },
        ctx,
        action,
    )


def _handle_import_standard(
    data: Any,
    project_name: str | None,
    ctx: Any | None,
    action: str,
) -> dict[str, Any]:
    invalid = _validate_import_or_wrap(data, ctx, action)
    if invalid is not None:
        return invalid
    import_cmd_module._import_data(data, project_name, action)
    return _wrap({"imported": True, "source": action}, ctx, action)


def _handle_import_jira(
    data: Any,
    project_name: str | None,
    ctx: Any | None,
    action: str,
) -> dict[str, Any]:
    errors = import_cmd_module._validate_jira_format(data)
    if errors:
        return _wrap({"errors": errors, "valid": False}, ctx, action)
    import_cmd_module._import_jira_data(data, project_name)
    return _wrap({"imported": True, "source": "jira"}, ctx, action)


def _handle_import_github(
    data: Any,
    project_name: str | None,
    ctx: Any | None,
    action: str,
) -> dict[str, Any]:
    errors = import_cmd_module._validate_github_format(data)
    if errors:
        return _wrap({"errors": errors, "valid": False}, ctx, action)
    import_cmd_module._import_github_data(data, project_name)
    return _wrap({"imported": True, "source": "github"}, ctx, action)


@mcp.tool(description="Unified export operations")
async def export_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified export management tool.

    Actions (formats):
    - json: Export as JSON (items + project metadata)
    - full: Export canonical JSON (project + items + links) for import/round-trip
    - yaml: Export as YAML
    - csv: Export as CSV
    - markdown: Export as Markdown

    Requires: project_id (from payload or config)
    Optional: output (file path to write to)
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    if action == "full":
        action = "json"  # full uses same canonical output as json
    format_map = {
        "json": export_cmd.export_to_json,
        "yaml": export_cmd.export_to_yaml,
        "csv": export_cmd.export_to_csv,
        "markdown": export_cmd.export_to_markdown,
    }
    if action not in format_map:
        raise ToolError("Unsupported export format. Use json|full|yaml|csv|markdown.")

    config = ConfigManager()
    project_id = payload.get("project_id") or config.get("current_project_id")
    if not project_id:
        raise ToolError("project_id is required for export.")

    storage = LocalStorageManager()
    with storage.get_session() as session:
        content = format_map[action](session, project_id)

    output = payload.get("output")
    if output:
        await asyncio.to_thread(_path_write_text, output, content)
        return _wrap(
            {"format": action, "output": str(output), "bytes": len(content)},
            ctx,
            action,
        )

    return _wrap({"format": action, "content": content}, ctx, action)


@mcp.tool(description="Unified import operations")
async def import_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified import management tool.

    Actions:
    - validate: Validate import data
    - json: Import from JSON (into existing project or create from canonical)
    - full: Import canonical JSON as new project (project + items + links)
    - yaml: Import from YAML
    - jira: Import from Jira format
    - github: Import from GitHub format

    Data sources (provide one):
    - data: Direct dict
    - content: String content (JSON or YAML)
    - path: File path

    Optional: project_name (for json/yaml; omit for full to create new project)
    """
    await asyncio.sleep(0)
    payload = payload or {}
    action = action.lower()
    project_name = payload.get("project_name")
    data = await _get_import_data(payload)

    handlers = {
        "validate": lambda: _wrap_validation(*import_cmd_module._validate_import_data(data), ctx, action),
        "full": lambda: _handle_import_full(data, ctx, action),
        "json": lambda: _handle_import_standard(data, project_name, ctx, action),
        "yaml": lambda: _handle_import_standard(data, project_name, ctx, action),
        "jira": lambda: _handle_import_jira(data, project_name, ctx, action),
        "github": lambda: _handle_import_github(data, project_name, ctx, action),
    }
    handler = handlers.get(action)
    if handler is None:
        raise ToolError(f"Unknown import action: {action}")
    return handler()


@mcp.tool(description="Unified ingestion operations")
def ingestion_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified ingestion management tool.

    Actions:
    - markdown/md: Ingest Markdown file
    - mdx: Ingest MDX file
    - yaml/yml: Ingest YAML file
    - directory: Ingest all files in directory

    Requires: path
    Optional: project_id, view, dry_run, validate, recursive (for directory)
    """
    payload = payload or {}
    action = action.lower()
    file_path = payload.get("path")
    if not file_path:
        raise ToolError("path is required for ingestion.")

    project_id = payload.get("project_id")
    view = payload.get("view", "FEATURE")
    dry_run = bool(payload.get("dry_run", False))
    validate = bool(payload.get("validate", True))

    def _ingest_single(service: StatelessIngestionService) -> dict[str, Any]:
        handlers = {
            "markdown": service.ingest_markdown,
            "md": service.ingest_markdown,
            "mdx": service.ingest_mdx,
            "yaml": service.ingest_yaml,
            "yml": service.ingest_yaml,
        }
        handler = handlers.get(action)
        if handler is None:
            raise ToolError(f"Unknown ingest action: {action}")
        return handler(file_path, project_id, view, dry_run, validate)

    def _ingest_directory(service: StatelessIngestionService) -> dict[str, Any]:
        directory = Path(file_path)
        if not directory.exists():
            raise ToolError(f"Directory not found: {file_path}")
        recursive = bool(payload.get("recursive", True))
        patterns = {".md", ".mdx", ".yaml", ".yml"}
        files = directory.rglob("*") if recursive else directory.iterdir()
        results = []
        for path in files:
            if not path.is_file() or path.suffix.lower() not in patterns:
                continue
            suffix = path.suffix.lower()
            if suffix in {".md", ".markdown"}:
                res = service.ingest_markdown(str(path), project_id, view, dry_run, validate)
            elif suffix == ".mdx":
                res = service.ingest_mdx(str(path), project_id, view, dry_run, validate)
            else:
                res = service.ingest_yaml(str(path), project_id, view, dry_run, validate)
            results.append({"path": str(path), "result": res})
        return {"count": len(results), "results": results}

    storage = LocalStorageManager()
    with storage.get_session() as session:
        service = StatelessIngestionService(session)
        result = _ingest_directory(service) if action == "directory" else _ingest_single(service)
        if not dry_run:
            session.commit()

    return _wrap(result, ctx, action)
