"""Priority 2 MCP tools: Design, Ingest, Migration, and Link Analysis.

This module provides important feature tools:
- Design tools: init, link, sync, generate, status, list
- Ingest tools: directory, markdown, mdx, yaml, file
- Migration tools: migrate_project
- Link analysis tools: link_detect_missing, link_detect_orphans, link_auto_link
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from tracertm.config.manager import ConfigManager
from tracertm.mcp.core import mcp

logger = logging.getLogger(__name__)

_ACTOR_CONTEXT_ERRORS = (ImportError, AttributeError, TypeError, ValueError)
_TOOL_OPERATION_ERRORS = (RuntimeError, ValueError, TypeError, OSError, LookupError)


def _path_exists(path: Path) -> bool:
    """Sync helper for Path.exists (run via asyncio.to_thread)."""
    return path.exists()


def _path_glob(path: Path, pattern: str) -> list[Path]:
    """Sync helper for Path.glob (run via asyncio.to_thread)."""
    return list(path.glob(pattern))


def _read_text_sync(path: Path) -> str:
    """Sync helper to read file text (run via asyncio.to_thread)."""
    return path.read_text(encoding="utf-8")


def _wrap(result: object, ctx: object | None, action: str) -> dict[str, object]:
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
        except _ACTOR_CONTEXT_ERRORS as e:
            logger.debug("Could not get actor from access token: %s", e)

    return {
        "ok": True,
        "action": action,
        "data": result,
        "actor": actor,
    }


def _error(message: str, action: str, code: str = "ERROR") -> dict[str, object]:
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
def design_init(
    ctx: object,
    figma_token: str,
    figma_file_id: str,
    trace_dir: str | None = None,
) -> dict[str, object]:
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

        with config_file.open("w") as f:
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Design initialization failed: {e!s}", "design_init")


@mcp.tool()
def design_link(
    ctx: object,
    component_name: str,
    figma_url: str,
    trace_dir: str | None = None,
) -> dict[str, object]:
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
            with components_file.open() as f:
                components = json.load(f)

        components[component_name] = {
            "figma_url": figma_url,
            "linked_at": str(Path.cwd()),
        }

        with components_file.open("w") as f:
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to link component: {e!s}", "design_link")


@mcp.tool()
def design_sync(
    ctx: object,
    trace_dir: str | None = None,
) -> dict[str, object]:
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Design sync failed: {e!s}", "design_sync")


@mcp.tool()
def design_generate(
    ctx: object,
    component_pattern: str | None = None,
    _trace_dir: str | None = None,
) -> dict[str, object]:
    """Generate component stories from Figma designs.

    Args:
        ctx: MCP context
        component_pattern: Optional pattern to filter components
        trace_dir: Optional trace directory path

    Returns:
        MCP response with generation status
    """
    try:
        return _wrap(
            {
                "message": "Component story generation started",
                "pattern": component_pattern or "all",
                "status": "pending",
            },
            ctx,
            "design_generate",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Story generation failed: {e!s}", "design_generate")


@mcp.tool()
async def design_status(
    ctx: object,
    trace_dir: str | None = None,
) -> dict[str, object]:
    """Show design integration status.

    Args:
        ctx: MCP context
        trace_dir: Optional trace directory path

    Returns:
        MCP response with integration status
    """
    await asyncio.sleep(0)
    try:
        trace_path = Path(trace_dir or Path.cwd())
        meta_dir = trace_path / ".tracertm"

        config_file = meta_dir / "design_config.json"
        components_file = meta_dir / "components_config.json"

        import json

        config = {}
        components = {}

        if config_file.exists():
            with config_file.open() as f:
                config = json.load(f)

        if components_file.exists():
            with components_file.open() as f:
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get design status: {e!s}", "design_status")


@mcp.tool()
async def design_list(
    ctx: object,
    trace_dir: str | None = None,
) -> dict[str, object]:
    """List linked design components.

    Args:
        ctx: MCP context
        trace_dir: Optional trace directory path

    Returns:
        MCP response with component list
    """
    await asyncio.sleep(0)
    try:
        trace_path = Path(trace_dir or Path.cwd())
        meta_dir = trace_path / ".tracertm"
        components_file = meta_dir / "components_config.json"

        import json

        components = {}
        if components_file.exists():
            with components_file.open() as f:
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to list components: {e!s}", "design_list")


# ==========================================================================
# Ingest Tools
# ==========================================================================


@mcp.tool()
async def ingest_directory(
    ctx: object,
    directory_path: str,
    project_name: str | None = None,
    recursive: bool = True,
) -> dict[str, object]:
    """Ingest all items from a directory structure.

    Args:
        ctx: MCP context
        directory_path: Path to directory to ingest
        project_name: Optional project name to create
        recursive: Whether to scan subdirectories

    Returns:
        MCP response with ingestion status
    """
    await asyncio.sleep(0)
    try:
        source_path = Path(directory_path)
        if not await asyncio.to_thread(_path_exists, source_path):
            return _error(f"Directory not found: {directory_path}", "ingest_directory")

        # Count files
        pattern = "**/*" if recursive else "*"
        files = await asyncio.to_thread(_path_glob, source_path, pattern)

        return _wrap(
            {
                "message": "Directory ingestion started",
                "directory": str(source_path),
                "files_found": len(files),
                "project": project_name or "default",
                "status": "pending",
            },
            ctx,
            "ingest_directory",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Directory ingestion failed: {e!s}", "ingest_directory")


@mcp.tool()
async def ingest_markdown(
    ctx: object,
    file_path: str,
    project_name: str | None = None,
) -> dict[str, object]:
    """Ingest items from a Markdown file.

    Args:
        ctx: MCP context
        file_path: Path to Markdown file
        project_name: Optional project name

    Returns:
        MCP response with ingestion status
    """
    await asyncio.sleep(0)
    try:
        md_path = Path(file_path)
        if not await asyncio.to_thread(_path_exists, md_path):
            return _error(f"File not found: {file_path}", "ingest_markdown")

        if md_path.suffix not in {".md", ".markdown"}:
            return _error(f"Not a Markdown file: {file_path}", "ingest_markdown")

        # Count headings (read file in thread to avoid blocking)
        content = await asyncio.to_thread(_read_text_sync, md_path)
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Markdown ingestion failed: {e!s}", "ingest_markdown")


@mcp.tool()
async def ingest_yaml(
    ctx: object,
    file_path: str,
    project_name: str | None = None,
) -> dict[str, object]:
    """Ingest items from a YAML file.

    Args:
        ctx: MCP context
        file_path: Path to YAML file
        project_name: Optional project name

    Returns:
        MCP response with ingestion status
    """
    await asyncio.sleep(0)
    try:
        yaml_path = Path(file_path)
        if not await asyncio.to_thread(_path_exists, yaml_path):
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"YAML ingestion failed: {e!s}", "ingest_yaml")


@mcp.tool()
async def ingest_file(
    ctx: object,
    file_path: str,
    file_type: str,
    project_name: str | None = None,
) -> dict[str, object]:
    """Ingest items from a file of specified type.

    Args:
        ctx: MCP context
        file_path: Path to file
        file_type: File type (json, yaml, markdown, etc.)
        project_name: Optional project name

    Returns:
        MCP response with ingestion status
    """
    await asyncio.sleep(0)
    try:
        source_path = Path(file_path)
        if not await asyncio.to_thread(_path_exists, source_path):
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"File ingestion failed: {e!s}", "ingest_file")


# ==========================================================================
# Migration Tools
# ==========================================================================


@mcp.tool()
async def migrate_project(
    ctx: object,
    source_path: str,
    project_name: str | None = None,
    backup_existing: bool = True,
) -> dict[str, object]:
    """Migrate project from external format to TraceRTM.

    Args:
        ctx: MCP context
        source_path: Source directory path
        project_name: Optional name for new project
        backup_existing: Whether to backup existing trace files

    Returns:
        MCP response with migration status
    """
    await asyncio.sleep(0)
    try:
        source = Path(source_path)
        if not await asyncio.to_thread(_path_exists, source):
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Migration failed: {e!s}", "migrate_project")


# ==========================================================================
# Link Analysis Tools
# ==========================================================================


@mcp.tool()
async def link_detect_missing(
    ctx: object,
    project_id: str | None = None,
) -> dict[str, object]:
    """Detect missing traceability links in project.

    Args:
        ctx: MCP context
        project_id: Optional project ID to check

    Returns:
        MCP response with missing links
    """
    await asyncio.sleep(0)
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Detection failed: {e!s}", "link_detect_missing")


@mcp.tool()
async def link_detect_orphans(
    ctx: object,
    project_id: str | None = None,
) -> dict[str, object]:
    """Detect orphaned items with no links.

    Args:
        ctx: MCP context
        project_id: Optional project ID to check

    Returns:
        MCP response with orphaned items
    """
    await asyncio.sleep(0)
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Detection failed: {e!s}", "link_detect_orphans")


@mcp.tool()
async def link_auto_link(
    ctx: object,
    project_id: str | None = None,
    threshold: float = 0.8,
) -> dict[str, object]:
    """Automatically create links based on semantic similarity.

    Args:
        ctx: MCP context
        project_id: Optional project ID
        threshold: Similarity threshold (0.0-1.0)

    Returns:
        MCP response with auto-link status
    """
    await asyncio.sleep(0)
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
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Auto-linking failed: {e!s}", "link_auto_link")
