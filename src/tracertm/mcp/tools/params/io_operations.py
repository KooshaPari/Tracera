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
except ImportError:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]

from tracertm.cli.commands import export as export_cmd
from tracertm.cli.commands import import_cmd as import_cmd_module
from tracertm.config.manager import ConfigManager
from tracertm.services.stateless_ingestion_service import StatelessIngestionService
from tracertm.storage.local_storage import LocalStorageManager

from .common import _wrap


def _path_write_text(path_str: str, content: str, encoding: str = "utf-8") -> None:
    """Sync helper: write text to path (run via asyncio.to_thread)."""
    Path(path_str).write_text(content, encoding=encoding)


def _load_data_from_path(path: str) -> object:
    """Sync helper: load import data from file path (run via asyncio.to_thread)."""
    p = Path(path)
    if not p.exists():
        msg = f"File not found: {path}"
        raise ToolError(msg)
    if p.suffix.lower() in {".yaml", ".yml"}:
        result = yaml.safe_load(p.read_text(encoding="utf-8"))
        if result is None:
            msg = f"Failed to parse YAML file: {path}"
            raise ToolError(msg)
        return result
    return json.loads(p.read_text(encoding="utf-8"))


def _load_data_from_payload(payload: dict[str, object]) -> object:
    """Load import data from payload (data/content)."""
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    content = payload.get("content")
    if content:
        try:
            return json.loads(content)  # type: ignore[arg-type]
        except json.JSONDecodeError as err:
            result = yaml.safe_load(content)  # type: ignore[arg-type]
            if result is None:
                msg = "Failed to parse YAML content"
                raise ToolError(msg) from err
            return result
    msg = "Provide data, content, or path for import."
    raise ToolError(msg)


async def _get_import_data(payload: dict[str, object]) -> object:
    """Load import data, handling file paths when provided."""
    path_obj = payload.get("path")
    path = str(path_obj) if path_obj else None
    if path:
        return await asyncio.to_thread(_load_data_from_path, path)
    return _load_data_from_payload(payload)


def _wrap_validation(
    errors: list[str],
    warnings: list[str] | None,
    ctx: object | None,
    action: str,
) -> dict[str, object]:
    """Wrap validation results."""
    return _wrap(
        {"errors": errors, "warnings": warnings or [], "valid": len(errors) == 0},
        ctx,
        action,
    )


def _validate_import_or_wrap(data: object, ctx: object | None, action: str) -> dict[str, object] | None:
    """Validate import data and return wrapped errors if invalid."""
    errors, warnings = import_cmd_module._validate_import_data(data)
    if errors:
        return _wrap_validation(errors, warnings, ctx, action)
    return None


def _handle_import_full(
    data: object,
    ctx: object | None,
    action: str,
) -> dict[str, object]:
    invalid = _validate_import_or_wrap(data, ctx, action)
    if invalid is not None:
        return invalid
    if not data.get("project") or not isinstance(data.get("items"), list):  # type: ignore[attr-defined]
        return _wrap({"errors": ["Canonical format requires project and items"], "valid": False}, ctx, action)
    import_cmd_module._import_data(data, None, "full")
    return _wrap(
        {
            "imported": True,
            "source": "full",
            "project": data.get("project", {}).get("name"),  # type: ignore[attr-defined]
            "items": len(data.get("items", [])),  # type: ignore[attr-defined]
            "links": len(data.get("links", [])),  # type: ignore[attr-defined]
        },
        ctx,
        action,
    )


def _handle_import_standard(
    data: object,
    project_name: str | None,
    ctx: object | None,
    action: str,
) -> dict[str, object]:
    invalid = _validate_import_or_wrap(data, ctx, action)
    if invalid is not None:
        return invalid
    import_cmd_module._import_data(data, project_name, action)
    return _wrap({"imported": True, "source": action}, ctx, action)


def _handle_import_jira(
    data: object,
    project_name: str | None,
    ctx: object | None,
    action: str,
) -> dict[str, object]:
    errors = import_cmd_module._validate_jira_format(data)
    if errors:
        return _wrap({"errors": errors, "valid": False}, ctx, action)
    import_cmd_module._import_jira_data(data, project_name)
    return _wrap({"imported": True, "source": "jira"}, ctx, action)


def _handle_import_github(
    data: object,
    project_name: str | None,
    ctx: object | None,
    action: str,
) -> dict[str, object]:
    errors = import_cmd_module._validate_github_format(data)
    if errors:
        return _wrap({"errors": errors, "valid": False}, ctx, action)
    import_cmd_module._import_github_data(data, project_name)
    return _wrap({"imported": True, "source": "github"}, ctx, action)


@mcp.tool(description="Unified export operations")
async def export_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified export management tool.

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
        msg = "Unsupported export format. Use json|full|yaml|csv|markdown."
        raise ToolError(msg)

    config = ConfigManager()
    project_id_obj = payload.get("project_id")
    project_id = str(project_id_obj) if project_id_obj else None or config.get("current_project_id")
    if not project_id:
        msg = "project_id is required for export."
        raise ToolError(msg)

    storage = LocalStorageManager()
    with storage.get_session() as session:
        content = format_map[action](session, project_id)

    output = payload.get("output")
    if output:
        await asyncio.to_thread(_path_write_text, output, content)  # type: ignore[arg-type]
        return _wrap(
            {"format": action, "output": str(output), "bytes": len(content)},
            ctx,
            action,
        )

    return _wrap({"format": action, "content": content}, ctx, action)


@mcp.tool(description="Unified import operations")
async def import_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified import management tool.

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
        "validate": lambda: _wrap_validation(*import_cmd_module._validate_import_data(data), ctx, action),  # type: ignore[call-arg]
        "full": lambda: _handle_import_full(data, ctx, action),
        "json": lambda: _handle_import_standard(data, project_name, ctx, action),  # type: ignore[arg-type]
        "yaml": lambda: _handle_import_standard(data, project_name, ctx, action),  # type: ignore[arg-type]
        "jira": lambda: _handle_import_jira(data, project_name, ctx, action),  # type: ignore[arg-type]
        "github": lambda: _handle_import_github(data, project_name, ctx, action),  # type: ignore[arg-type]
    }
    handler = handlers.get(action)
    if handler is None:
        msg = f"Unknown import action: {action}"
        raise ToolError(msg)
    return handler()


@mcp.tool(description="Unified ingestion operations")
def ingestion_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified ingestion management tool.

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
    payload.get("path")
    str(path_obj) if path_obj else None  # type: ignore[name-defined]
    if not file_path:  # type: ignore[name-defined]
        msg = "path is required for ingestion."
        raise ToolError(msg)

    project_id_obj = payload.get("project_id")
    project_id = str(project_id_obj) if project_id_obj else None
    view = str(payload.get("view", "FEATURE"))
    dry_run = bool(payload.get("dry_run", False))
    validate = bool(payload.get("validate", True))

    def _ingest_single(service: StatelessIngestionService) -> dict[str, object]:
        handlers = {
            "markdown": service.ingest_markdown,
            "md": service.ingest_markdown,
            "mdx": service.ingest_mdx,
            "yaml": service.ingest_yaml,
            "yml": service.ingest_yaml,
        }
        handler = handlers.get(action)
        if handler is None:
            msg = f"Unknown ingest action: {action}"
            raise ToolError(msg)
        return handler(file_path, project_id, view, dry_run, validate)  # type: ignore[name-defined]

    def _ingest_directory(service: StatelessIngestionService) -> dict[str, object]:
        directory = Path(file_path)  # type: ignore[name-defined]
        if not directory.exists():
            msg = f"Directory not found: {file_path}"  # type: ignore[name-defined]
            raise ToolError(msg)
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
