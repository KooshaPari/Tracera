"""Storage, sync, backup, and file watch MCP tools."""

from __future__ import annotations

import gzip
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastmcp.exceptions import ToolError
from sqlalchemy import text

# Table names from sqlite_master or backup JSON; must be identifier-safe.
_TABLE_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _safe_table_name(name: str) -> str:
    if not _TABLE_NAME_RE.match(name):
        msg = f"Invalid table name: {name!r}"
        raise ToolError(msg)
    return name


try:
    from tracertm.mcp.core import mcp
except ImportError:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]

from tracertm.storage.file_watcher import TraceFileWatcher
from tracertm.storage.local_storage import LocalStorageManager

from .common import _WATCHERS, _build_sync_engine, _wrap


@mcp.tool(description="Unified sync operations")
async def sync_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified sync management tool.

    Actions:
    - status: Get sync status
    - sync: Synchronize changes (optional: force)
    - pull: Pull changes from remote
    """
    return await _sync_manage_impl(action, payload, ctx)


async def _sync_manage_impl(
    action: str,
    payload: dict[str, object] | None,
    ctx: object | None,
) -> dict[str, object]:
    """Implementation of sync management."""
    payload = payload or {}
    action = action.lower()
    sync_engine = _build_sync_engine()

    if action == "status":
        state = sync_engine.get_status()
        return _wrap(
            {
                "status": state.status.value,
                "last_sync": state.last_sync.isoformat() if state.last_sync else None,
                "pending_changes": state.pending_changes,
                "conflicts_count": state.conflicts_count,
                "last_error": state.last_error,
            },
            ctx,
            action,
        )
    if action == "sync":
        force = bool(payload.get("force", False))
        result = await sync_engine.sync(_force=force)
        return _wrap(
            {
                "success": result.success,
                "entities_synced": result.entities_synced,
                "conflicts": result.conflicts,
                "errors": result.errors,
                "duration_seconds": result.duration_seconds,
            },
            ctx,
            action,
        )
    if action == "pull":
        result = await sync_engine.pull_changes()
        return _wrap(
            {
                "success": result.success,
                "entities_synced": result.entities_synced,
                "conflicts": result.conflicts,
                "errors": result.errors,
                "duration_seconds": result.duration_seconds,
            },
            ctx,
            action,
        )

    msg = f"Unknown sync action: {action}"
    raise ToolError(msg)


@mcp.tool(description="Unified backup operations")
def backup_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified backup management tool.

    Actions:
    - backup: Create backup (optional: project_id, output, compress)
    - restore: Restore from backup (requires: path)
    """
    payload = payload or {}
    action = action.lower()

    storage = LocalStorageManager()

    if action == "backup":
        project_id_obj = payload.get("project_id")
        project_id = str(project_id_obj) if project_id_obj else None
        output = payload.get("output")
        compress = bool(payload.get("compress", True))

        if not output:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            suffix = ".json.gz" if compress else ".json"
            output = f"tracertm_backup_{timestamp}{suffix}"

        backup_data: dict[str, object] = {
            "version": "1.0",
            "timestamp": datetime.now(UTC).isoformat(),
            "project_id": project_id,
            "tables": {},
        }

        with storage.get_session() as session:
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            for table in tables:
                if table.startswith("alembic"):
                    continue
                safe_name = _safe_table_name(table)
                rows = session.execute(text(f"SELECT * FROM {safe_name}")).all()  # nosec B608
                records = [dict(row._mapping) for row in rows]
                for row in records:
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            row[key] = value.isoformat()
                backup_data["tables"][table] = records  # type: ignore[index]

        output_path = Path(output)  # type: ignore[arg-type]
        if compress:
            with gzip.open(output_path, "wt", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, default=str)
        else:
            output_path.write_text(json.dumps(backup_data, indent=2, default=str), encoding="utf-8")

        return _wrap({"output": str(output_path), "tables": len(backup_data["tables"])}, ctx, action)  # type: ignore[arg-type]

    if action == "restore":
        path_obj = payload.get("path")
        path = str(path_obj) if path_obj else None
        if not path:
            msg = "path is required for restore."
            raise ToolError(msg)
        backup_file = Path(path)
        if not backup_file.exists():
            msg = f"Backup file not found: {path}"
            raise ToolError(msg)
        if backup_file.suffix == ".gz":
            with gzip.open(backup_file, "rt", encoding="utf-8") as f:
                backup_data = json.load(f)
        else:
            backup_data = json.loads(backup_file.read_text(encoding="utf-8"))

        if not isinstance(backup_data, dict) or "tables" not in backup_data:
            msg = "Invalid backup format."
            raise ToolError(msg)

        with storage.get_session() as session:
            for table, rows in backup_data["tables"].items():  # type: ignore[attr-defined]
                safe_name = _safe_table_name(table)
                session.execute(text(f"DELETE FROM {safe_name}"))  # nosec B608
                for row in rows:
                    columns = ", ".join(row)
                    placeholders = ", ".join([f":{k}" for k in row])
                    session.execute(
                        text(f"INSERT INTO {safe_name} ({columns}) VALUES ({placeholders})"),  # nosec B608
                        row,
                    )
            session.commit()

        return _wrap({"restored": True, "tables": len(backup_data["tables"])}, ctx, action)  # type: ignore[arg-type]

    msg = f"Unknown backup action: {action}"
    raise ToolError(msg)


@mcp.tool(description="Unified file watch operations")
def file_watch_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified file watch management tool.

    Actions:
    - start: Start watching directory (optional: path, debounce, auto_sync, watch_id)
    - stop: Stop watching (requires: watch_id)
    - status: Get watch status (optional: watch_id for specific watcher, or all if omitted)
    """
    payload = payload or {}
    action = action.lower()

    if action == "start":
        path = Path(payload.get("path") or Path.cwd())  # type: ignore[arg-type]
        debounce = int(payload.get("debounce", 500))  # type: ignore[call-overload]
        auto_sync = bool(payload.get("auto_sync", False))
        storage = LocalStorageManager()
        watcher = TraceFileWatcher(
            project_path=path,
            storage=storage,
            debounce_ms=debounce,
            auto_sync=auto_sync,
        )
        watcher.start()
        watch_id = payload.get("watch_id") or f"watch-{len(_WATCHERS) + 1}"
        _WATCHERS[watch_id] = watcher  # type: ignore[index]
        return _wrap({"watch_id": watch_id, "path": str(path)}, ctx, action)

    if action == "stop":
        watch_id = payload.get("watch_id")
        if not watch_id or watch_id not in _WATCHERS:
            msg = "watch_id not found."
            raise ToolError(msg)
        watcher = _WATCHERS.pop(watch_id)  # type: ignore[call-overload]
        watcher.stop()
        return _wrap({"watch_id": watch_id, "stopped": True}, ctx, action)

    if action == "status":
        watch_id = payload.get("watch_id")
        if watch_id:
            target_watcher: object = _WATCHERS.get(watch_id)  # type: ignore[call-overload]
            if not target_watcher:
                msg = "watch_id not found."
                raise ToolError(msg)
            return _wrap({"watch_id": watch_id, "stats": target_watcher.get_stats()}, ctx, action)  # type: ignore[attr-defined]
        return _wrap({k: v.get_stats() for k, v in _WATCHERS.items()}, ctx, action)

    msg = f"Unknown watch action: {action}"
    raise ToolError(msg)
