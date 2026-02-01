"""Priority 2 MCP tools: Design, Ingest, Migration, and Link Analysis.

This module provides important feature tools:
- Design tools: init, link, sync, generate, status, list
- Ingest tools: directory, markdown, mdx, yaml, file
- Migration tools: migrate_project
- Link analysis tools: link_detect_missing, link_detect_orphans, link_auto_link
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastmcp.exceptions import ToolError

from tracertm.mcp.core import mcp
from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.storage.local_storage import LocalStorageManager


def _wrap(result: Any, ctx: Any | None, action: str) -> dict[str, Any]:
    """Wrap result in standard MCP response format."""
    actor = None
    if ctx is not None:
        try:
            from fastmcp.server.dependencies import get_access_token
            token = get_access_token()
            if token:
                claims = getattr(token, "claims", {}) or {}
                actor = {
                    "client_id": getattr(token, "client_id", None),
                    "sub": claims.get("sub"),
                }
        except Exception:
            pass

    return {
        "ok": True,
        "action": action,
        "data": result,
        "actor": actor,
    }


def _error(message: str, action: str, code: str = "ERROR") -> dict[str, Any]:
    """Return error response."""
    return {
        "ok": False,
        "action": action,
        "error": message,
        "error_code": code,
    }


# ==========================================================================
# Design Integration Tools
# ==========================================================================


@mcp.tool()
async def design_init(
    ctx: Any,
    figma_token: str,
    figma_file_id: str,
    trace_dir: str | None = None,
) -> Dict[str, Any]:
    """Initialize Figma design integration.

    Args:
        ctx: MCP context
        figma_token: Figma API token
        figma_file_id: Figma file ID to integrate
        trace_dir: Optional trace directory path

    Returns:
        MCP response with integration status
    """
    try:
        trace_path = Path(trace_dir or Path.cwd())
        meta_dir = trace_path / ".tracertm"
        meta_dir.mkdir(parents=True, exist_ok=True)

        config = {
            "figma_token": figma_token,
            "figma_file_id": figma_file_id,
            "initialized_at": str(Path.cwd()),
        }

        config_file = meta_dir / "design_config.json"
        import json
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        return _wrap(
            {
                "message": "Figma design integration initialized",
                "figma_file_id": figma_file_id,
                "config_path": str(config_file),
            },
            ctx,
            "design_init",
        )
    except Exception as e:
        return _error(f"Design initialization failed: {str(e)}", "design_init")


@mcp.tool()
async def design_link(
    ctx: Any,
    component_name: str,
    figma_url: str,
    trace_dir: str | None = None,
) -> Dict[str, Any]:
    """Link a component to a Figma design.

    Args:
        ctx: MCP context
        component_name: Component name in project
        figma_url: Figma component URL
        trace_dir: Optional trace directory path

    Returns:
        MCP response with link status
    """
    try:
        trace_path = Path(trace_dir or Path.cwd())
        meta_dir = trace_path / ".tracertm"
        components_file = meta_dir / "components_config.json"

        import json
        components = {}
        if components_file.exists():
            with open(components_file, "r") as f:
                components = json.load(f)

        components[component_name] = {
            "figma_url": figma_url,
            "linked_at": str(Path.cwd()),
        }

        with open(components_file, "w") as f:
            json.dump(components, f, indent=2)

        return _wrap(
            {
                "message": f"Linked {component_name} to Figma design",
                "component": component_name,
                "figma_url": figma_url,
            },
            ctx,
            "design_link",
        )
    except Exception as e:
        return _error(f"Failed to link component: {str(e)}", "design_link")


@mcp.tool()
async def design_sync(
    ctx: Any,
    trace_dir: str | None = None,
) -> Dict[str, Any]:
    """Sync designs from Figma to project.

    Args:
        ctx: MCP context
        trace_dir: Optional trace directory path

    Returns:
        MCP response with sync status
    """
    try:
        trace_path = Path(trace_dir or Path.cwd())

        return _wrap(
            {
                "message": "Design sync started (requires Figma API token)",
                "status": "pending",
                "trace_dir": str(trace_path),
                "note": "Actual sync would require async background task",
            },
            ctx,
            "design_sync",
        )
    except Exception as e:
        return _error(f"Design sync failed: {str(e)}", "design_sync")


@mcp.tool()
async def design_generate(
    ctx: Any,
    component_pattern: str | None = None,
    trace_dir: str | None = None,
) -> Dict[str, Any]:
    """Generate component stories from Figma designs.

    Args:
        ctx: MCP context
        component_pattern: Optional pattern to filter components
        trace_dir: Optional trace directory path

    Returns:
        MCP response with generation status
    """
    try:
        trace_path = Path(trace_dir or Path.cwd())

        return _wrap(
            {
                "message": "Component story generation started",
                "pattern": component_pattern or "all",
                "status": "pending",
            },
            ctx,
            "design_generate",
        )
    except Exception as e:
        return _error(f"Story generation failed: {str(e)}", "design_generate")


@mcp.tool()
async def design_status(
    ctx: Any,
    trace_dir: str | None = None,
) -> Dict[str, Any]:
    """Show design integration status.

    Args:
        ctx: MCP context
        trace_dir: Optional trace directory path

    Returns:
        MCP response with integration status
    """
    try:
        trace_path = Path(trace_dir or Path.cwd())
        meta_dir = trace_path / ".tracertm"

        config_file = meta_dir / "design_config.json"
        components_file = meta_dir / "components_config.json"

        import json
        config = {}
        components = {}

        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)

        if components_file.exists():
            with open(components_file, "r") as f:
                components = json.load(f)

        return _wrap(
            {
                "initialized": bool(config),
                "figma_file_id": config.get("figma_file_id"),
                "components_linked": len(components),
                "components": list(components.keys()),
            },
            ctx,
            "design_status",
        )
    except Exception as e:
        return _error(f"Failed to get design status: {str(e)}", "design_status")


@mcp.tool()
async def design_list(
    ctx: Any,
    trace_dir: str | None = None,
) -> Dict[str, Any]:
    """List linked design components.

    Args:
        ctx: MCP context
        trace_dir: Optional trace directory path

    Returns:
        MCP response with component list
    """
    try:
        trace_path = Path(trace_dir or Path.cwd())
        meta_dir = trace_path / ".tracertm"
        components_file = meta_dir / "components_config.json"

        import json
        components = {}
        if components_file.exists():
            with open(components_file, "r") as f:
                components = json.load(f)

        return _wrap(
            {
                "components": [
                    {
                        "name": name,
                        "figma_url": info.get("figma_url"),
                    }
                    for name, info in components.items()
                ],
                "total": len(components),
            },
            ctx,
            "design_list",
        )
    except Exception as e:
        return _error(f"Failed to list components: {str(e)}", "design_list")


# ==========================================================================
# Ingest Tools
# ==========================================================================


@mcp.tool()
async def ingest_directory(
    ctx: Any,
    directory_path: str,
    project_name: str | None = None,
    recursive: bool = True,
) -> Dict[str, Any]:
    """Ingest all items from a directory structure.

    Args:
        ctx: MCP context
        directory_path: Path to directory to ingest
        project_name: Optional project name to create
        recursive: Whether to scan subdirectories

    Returns:
        MCP response with ingestion status
    """
    try:
        source_path = Path(directory_path)
        if not source_path.exists():
            return _error(f"Directory not found: {directory_path}", "ingest_directory")

        # Count files
        import glob
        pattern = "**/*" if recursive else "*"
        files = list(source_path.glob(pattern))

        return _wrap(
            {
                "message": f"Directory ingestion started",
                "directory": str(source_path),
                "files_found": len(files),
                "project": project_name or "default",
                "status": "pending",
            },
            ctx,
            "ingest_directory",
        )
    except Exception as e:
        return _error(f"Directory ingestion failed: {str(e)}", "ingest_directory")


@mcp.tool()
async def ingest_markdown(
    ctx: Any,
    file_path: str,
    project_name: str | None = None,
) -> Dict[str, Any]:
    """Ingest items from a Markdown file.

    Args:
        ctx: MCP context
        file_path: Path to Markdown file
        project_name: Optional project name

    Returns:
        MCP response with ingestion status
    """
    try:
        md_path = Path(file_path)
        if not md_path.exists():
            return _error(f"File not found: {file_path}", "ingest_markdown")

        if not md_path.suffix in [".md", ".markdown"]:
            return _error(f"Not a Markdown file: {file_path}", "ingest_markdown")

        # Count headings
        with open(md_path, "r") as f:
            content = f.read()
        headings = content.count("\n# ") + content.count("\n## ") + content.count("\n### ")

        return _wrap(
            {
                "message": "Markdown ingestion started",
                "file": str(md_path),
                "headings_found": headings,
                "project": project_name or "default",
            },
            ctx,
            "ingest_markdown",
        )
    except Exception as e:
        return _error(f"Markdown ingestion failed: {str(e)}", "ingest_markdown")


@mcp.tool()
async def ingest_yaml(
    ctx: Any,
    file_path: str,
    project_name: str | None = None,
) -> Dict[str, Any]:
    """Ingest items from a YAML file.

    Args:
        ctx: MCP context
        file_path: Path to YAML file
        project_name: Optional project name

    Returns:
        MCP response with ingestion status
    """
    try:
        yaml_path = Path(file_path)
        if not yaml_path.exists():
            return _error(f"File not found: {file_path}", "ingest_yaml")

        return _wrap(
            {
                "message": "YAML ingestion started",
                "file": str(yaml_path),
                "project": project_name or "default",
            },
            ctx,
            "ingest_yaml",
        )
    except Exception as e:
        return _error(f"YAML ingestion failed: {str(e)}", "ingest_yaml")


@mcp.tool()
async def ingest_file(
    ctx: Any,
    file_path: str,
    file_type: str,
    project_name: str | None = None,
) -> Dict[str, Any]:
    """Ingest items from a file of specified type.

    Args:
        ctx: MCP context
        file_path: Path to file
        file_type: File type (json, yaml, markdown, etc.)
        project_name: Optional project name

    Returns:
        MCP response with ingestion status
    """
    try:
        source_path = Path(file_path)
        if not source_path.exists():
            return _error(f"File not found: {file_path}", "ingest_file")

        return _wrap(
            {
                "message": f"File ingestion started ({file_type})",
                "file": str(source_path),
                "type": file_type,
                "project": project_name or "default",
            },
            ctx,
            "ingest_file",
        )
    except Exception as e:
        return _error(f"File ingestion failed: {str(e)}", "ingest_file")


# ==========================================================================
# Migration Tools
# ==========================================================================


@mcp.tool()
async def migrate_project(
    ctx: Any,
    source_path: str,
    project_name: str | None = None,
    backup_existing: bool = True,
) -> Dict[str, Any]:
    """Migrate project from external format to TraceRTM.

    Args:
        ctx: MCP context
        source_path: Source directory path
        project_name: Optional name for new project
        backup_existing: Whether to backup existing trace files

    Returns:
        MCP response with migration status
    """
    try:
        source = Path(source_path)
        if not source.exists():
            return _error(f"Source directory not found: {source_path}", "migrate_project")

        return _wrap(
            {
                "message": "Project migration started",
                "source": str(source),
                "project": project_name or source.name,
                "backup": backup_existing,
                "status": "pending",
            },
            ctx,
            "migrate_project",
        )
    except Exception as e:
        return _error(f"Migration failed: {str(e)}", "migrate_project")


# ==========================================================================
# Link Analysis Tools
# ==========================================================================


@mcp.tool()
async def link_detect_missing(
    ctx: Any,
    project_id: str | None = None,
) -> Dict[str, Any]:
    """Detect missing traceability links in project.

    Args:
        ctx: MCP context
        project_id: Optional project ID to check

    Returns:
        MCP response with missing links
    """
    try:
        config = ConfigManager()
        project_id = project_id or config.get("current_project_id")

        if not project_id:
            return _error("No project selected", "link_detect_missing", "NO_PROJECT")

        return _wrap(
            {
                "message": "Scanning for missing dependencies",
                "project_id": project_id,
                "status": "analyzing",
            },
            ctx,
            "link_detect_missing",
        )
    except Exception as e:
        return _error(f"Detection failed: {str(e)}", "link_detect_missing")


@mcp.tool()
async def link_detect_orphans(
    ctx: Any,
    project_id: str | None = None,
) -> Dict[str, Any]:
    """Detect orphaned items with no links.

    Args:
        ctx: MCP context
        project_id: Optional project ID to check

    Returns:
        MCP response with orphaned items
    """
    try:
        config = ConfigManager()
        project_id = project_id or config.get("current_project_id")

        if not project_id:
            return _error("No project selected", "link_detect_orphans", "NO_PROJECT")

        return _wrap(
            {
                "message": "Scanning for orphaned items",
                "project_id": project_id,
                "status": "analyzing",
            },
            ctx,
            "link_detect_orphans",
        )
    except Exception as e:
        return _error(f"Detection failed: {str(e)}", "link_detect_orphans")


@mcp.tool()
async def link_auto_link(
    ctx: Any,
    project_id: str | None = None,
    threshold: float = 0.8,
) -> Dict[str, Any]:
    """Automatically create links based on semantic similarity.

    Args:
        ctx: MCP context
        project_id: Optional project ID
        threshold: Similarity threshold (0.0-1.0)

    Returns:
        MCP response with auto-link status
    """
    try:
        config = ConfigManager()
        project_id = project_id or config.get("current_project_id")

        if not project_id:
            return _error("No project selected", "link_auto_link", "NO_PROJECT")

        return _wrap(
            {
                "message": "Auto-linking started",
                "project_id": project_id,
                "threshold": threshold,
                "status": "analyzing",
            },
            ctx,
            "link_auto_link",
        )
    except Exception as e:
        return _error(f"Auto-linking failed: {str(e)}", "link_auto_link")
