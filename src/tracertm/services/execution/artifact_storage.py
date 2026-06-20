"""Local filesystem artifact storage for QA Integration (STORY-003).

Stores screenshots, videos, GIFs, logs under ~/.tracertm/artifacts/{project_id}/{execution_id}/.
"""

from __future__ import annotations

import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ArtifactStorageService:
    """Local filesystem storage for execution artifacts."""

    def __init__(
        self,
        base_path: str | Path | None = None,
    ) -> None:
        """Initialize artifact storage.

        Args:
            base_path: Root directory for artifacts. Defaults to
                TRACERTM_ARTIFACT_PATH or ~/.tracertm/artifacts.
        """
        if base_path is None:
            base_path = os.getenv("TRACERTM_ARTIFACT_PATH", "").strip()
            if not base_path:
                base_path = Path.home() / ".tracertm" / "artifacts"
        self._base = Path(base_path).expanduser().resolve()

    def _dir(self, project_id: str, execution_id: str) -> Path:
        """Return directory path for a project/execution."""
        return self._base / project_id / execution_id

    def ensure_dir(self, project_id: str, execution_id: str) -> Path:
        """Create and return artifact directory for an execution."""
        d = self._dir(project_id, execution_id)
        d.mkdir(parents=True, exist_ok=True)
        return d

    def store_file(
        self,
        project_id: str,
        execution_id: str,
        source_path: str | Path,
        _artifact_type: str,
        *,
        filename: str | None = None,
        subdir: str | None = None,
    ) -> tuple[Path, int]:
        """Copy a file into artifact storage for the given execution.

        Args:
            project_id: Project ID.
            execution_id: Execution ID.
            source_path: Path to the file to store.
            artifact_type: Type (screenshot, video, gif, log, trace, tape).
            filename: Optional filename; default is original name or uuid-based.
            subdir: Optional subdirectory under execution dir (e.g. 'videos').

        Returns:
            Tuple of (stored_file_path, file_size_bytes).
        """
        source = Path(source_path).resolve()
        if not source.is_file():
            msg = f"Artifact file not found: {source}"
            raise FileNotFoundError(msg)

        dest_dir = self._dir(project_id, execution_id)
        if subdir:
            dest_dir /= subdir
        dest_dir.mkdir(parents=True, exist_ok=True)

        name = filename or source.name
        dest_path = dest_dir / name
        shutil.copy2(source, dest_path)
        size = dest_path.stat().st_size
        return dest_path, size

    def get_path(self, project_id: str, execution_id: str, relative_path: str) -> Path:
        """Resolve a path relative to the execution artifact dir."""
        return (self._dir(project_id, execution_id) / relative_path).resolve()

    def list_artifacts(
        self,
        project_id: str,
        execution_id: str,
        *,
        artifact_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List stored files under an execution dir (by extension if artifact_type given).

        Returns list of dicts with keys: path, size, mtime, suggested_type.
        """
        d = self._dir(project_id, execution_id)
        if not d.is_dir():
            return []

        ext_map = {
            "screenshot": {".png", ".jpg", ".jpeg", ".webp"},
            "video": {".webm", ".mp4", ".mkv"},
            "gif": {".gif"},
            "log": {".log", ".txt"},
            "trace": {".zip", ".trace"},
            "tape": {".tape"},
        }
        allowed = ext_map.get(artifact_type) if artifact_type else None

        out: list[dict[str, Any]] = []
        for f in d.rglob("*"):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if allowed and ext not in allowed:
                continue
            out.append({
                "path": str(f),
                "relative_path": str(f.relative_to(d)),
                "size": f.stat().st_size,
                "mtime": datetime.fromtimestamp(f.stat().st_mtime, UTC),
                "suggested_type": artifact_type or self._suggest_type(ext),
            })
        return out

    def _suggest_type(self, ext: str) -> str:
        for kind, exts in {
            "screenshot": {".png", ".jpg", ".jpeg", ".webp"},
            "video": {".webm", ".mp4", ".mkv"},
            "gif": {".gif"},
            "log": {".log", ".txt"},
            "tape": {".tape"},
        }.items():
            if ext in exts:
                return kind
        return "other"

    def delete_execution_artifacts(self, project_id: str, execution_id: str) -> bool:
        """Remove all stored artifacts for an execution. Returns True if dir was removed."""
        d = self._dir(project_id, execution_id)
        if not d.is_dir():
            return True
        shutil.rmtree(d, ignore_errors=True)
        return True

    def delete_old_executions(
        self,
        project_id: str,
        retention_days: int,
        *,
        now: datetime | None = None,
    ) -> int:
        """Remove artifact dirs for executions older than retention_days. Returns count removed."""
        project_dir = self._base / project_id
        if not project_dir.is_dir():
            return 0
        now = now or datetime.now(UTC)
        removed = 0
        for execution_dir in project_dir.iterdir():
            if not execution_dir.is_dir():
                continue
            try:
                mtime = datetime.fromtimestamp(execution_dir.stat().st_mtime, UTC)
                if (now - mtime).days >= retention_days:
                    shutil.rmtree(execution_dir, ignore_errors=True)
                    removed += 1
            except OSError:
                continue
        return removed

    @property
    def base_path(self) -> Path:
        """Return the configured base path for artifacts."""
        return self._base
