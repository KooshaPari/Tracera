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

    mcp = _StubMCP()  # type: ignore[assignment]

from tracertm.cli.commands import export as export_cmd
from tracertm.cli.commands import import_cmd as import_cmd_module
from tracertm.config.manager import ConfigManager
from tracertm.services.stateless_ingestion_service import StatelessIngestionService
from tracertm.storage.local_storage import LocalStorageManager

from .common import _wrap


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
        output_path = Path(output)
        output_path.write_text(content, encoding="utf-8")
        return _wrap(
            {"format": action, "output": str(output_path), "bytes": len(content)},
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

    def _load_data() -> dict[str, Any]:
        data = payload.get("data")
        if isinstance(data, dict[str, Any]):
            return data
        content = payload.get("content")
        path = payload.get("path")
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                result = yaml.safe_load(content)
                if result is None:
                    raise ToolError("Failed to parse YAML content")
                return result
        if path:
            file_path = Path(path)
            if not file_path.exists():
                raise ToolError(f"File not found: {path}")
            if file_path.suffix.lower() in {".yaml", ".yml"}:
                result = yaml.safe_load(file_path.read_text(encoding="utf-8"))
                if result is None:
                    raise ToolError(f"Failed to parse YAML file: {path}")
                return result
            return json.loads(file_path.read_text(encoding="utf-8"))
        raise ToolError("Provide data, content, or path for import.")

    if action == "validate":
        data = _load_data()
        errors, warnings = import_cmd_module._validate_import_data(data)
        return _wrap({"errors": errors, "warnings": warnings, "valid": len(errors) == 0}, ctx, action)

    data = _load_data()

    if action == "full":
        errors, _ = import_cmd_module._validate_import_data(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        if not data.get("project") or not isinstance(data.get("items"), list[Any]):
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

    if action == "json":
        errors, _ = import_cmd_module._validate_import_data(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        import_cmd_module._import_data(data, project_name, "json")
        return _wrap({"imported": True, "source": "json"}, ctx, action)

    if action == "yaml":
        errors, _ = import_cmd_module._validate_import_data(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        import_cmd_module._import_data(data, project_name, "yaml")
        return _wrap({"imported": True, "source": "yaml"}, ctx, action)

    if action == "jira":
        errors = import_cmd_module._validate_jira_format(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        import_cmd_module._import_jira_data(data, project_name)
        return _wrap({"imported": True, "source": "jira"}, ctx, action)

    if action == "github":
        errors = import_cmd_module._validate_github_format(data)
        if errors:
            return _wrap({"errors": errors, "valid": False}, ctx, action)
        import_cmd_module._import_github_data(data, project_name)
        return _wrap({"imported": True, "source": "github"}, ctx, action)

    raise ToolError(f"Unknown import action: {action}")


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

    storage = LocalStorageManager()
    with storage.get_session() as session:
        service = StatelessIngestionService(session)
        if action in {"markdown", "md"}:
            result = service.ingest_markdown(file_path, project_id, view, dry_run, validate)
        elif action == "mdx":
            result = service.ingest_mdx(file_path, project_id, view, dry_run, validate)
        elif action in {"yaml", "yml"}:
            result = service.ingest_yaml(file_path, project_id, view, dry_run, validate)
        elif action == "directory":
            directory = Path(file_path)
            if not directory.exists():
                raise ToolError(f"Directory not found: {file_path}")
            recursive = bool(payload.get("recursive", True))
            patterns = {".md", ".mdx", ".yaml", ".yml"}
            files = directory.rglob("*") if recursive else directory.iterdir()
            results = []
            for path in files:
                if path.is_file() and path.suffix.lower() in patterns:
                    if path.suffix.lower() in {".md", ".markdown"}:
                        res = service.ingest_markdown(str(path), project_id, view, dry_run, validate)
                    elif path.suffix.lower() == ".mdx":
                        res = service.ingest_mdx(str(path), project_id, view, dry_run, validate)
                    else:
                        res = service.ingest_yaml(str(path), project_id, view, dry_run, validate)
                    results.append({"path": str(path), "result": res})
            if not dry_run:
                session.commit()
            return _wrap({"count": len(results), "results": results}, ctx, action)
        else:
            raise ToolError(f"Unknown ingest action: {action}")

        if not dry_run:
            session.commit()

    return _wrap(result, ctx, action)
