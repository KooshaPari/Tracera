"""File-backed model registry with explicit version pinning."""

from __future__ import annotations

import json
import pickle  # noqa: S403
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_SAFE_PART = re.compile(r"^[A-Za-z0-9_.-]+$")
_INDEX_FILE = "registry.json"


class ModelRegistryError(ValueError):
    """Raised when registry operations cannot be completed."""


class ModelEntry(BaseModel):
    """Metadata for one saved model version."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    version: str
    artifact_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class _RegistryIndex(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    models: dict[str, dict[str, ModelEntry]] = Field(default_factory=dict)
    pins: dict[str, str] = Field(default_factory=dict)


class ModelRegistry:
    """Persist and resolve local model artifacts by name and version.

    A pinned version is used by load(name) when no version is provided.
    Explicit versions always win over pins.
    """

    def __init__(self, root: str | Path) -> None:
        """Create a registry rooted at the given directory."""
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / _INDEX_FILE

    def save(
        self,
        name: str,
        version: str,
        model: Any,
        metadata: dict[str, Any] | None = None,
        *,
        pin: bool = False,
        overwrite: bool = False,
    ) -> ModelEntry:
        """Save a model artifact and register its metadata."""
        self._validate_part(name, "name")
        self._validate_part(version, "version")

        index = self._read_index()
        versions = index.models.setdefault(name, {})
        if version in versions and not overwrite:
            raise ModelRegistryError(  # noqa: TRY003
                f"model {name!r} version {version!r} already exists"
            )

        model_dir = self.root / name
        model_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = model_dir / f"{version}.pkl"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        with artifact_path.open("wb") as handle:
            pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)

        entry = ModelEntry(
            name=name,
            version=version,
            artifact_path=str(artifact_path.relative_to(self.root)),
            metadata=metadata or {},
            created_at=datetime.now(UTC),
        )
        versions[version] = entry
        if pin:
            index.pins[name] = version
        self._write_index(index)
        return entry

    def load(self, name: str, version: str | None = None) -> Any:
        """Load a saved model, using the pinned or latest version by default."""
        entry = self.get(name, version)
        with (self.root / entry.artifact_path).open("rb") as handle:
            return pickle.load(handle)  # noqa: S301

    def get(self, name: str, version: str | None = None) -> ModelEntry:
        """Return metadata for a model version."""
        index = self._read_index()
        versions = index.models.get(name)
        if not versions:
            raise ModelRegistryError(f"model {name!r} is not registered")  # noqa: TRY003

        resolved_version = version or index.pins.get(name) or self._latest_version(versions)
        entry = versions.get(resolved_version)
        if entry is None:
            raise ModelRegistryError(  # noqa: TRY003
                f"model {name!r} version {resolved_version!r} is not registered"
            )
        return entry

    def list(self, name: str | None = None) -> list[ModelEntry]:
        """List registered model versions, newest first."""
        index = self._read_index()
        selected = {name: index.models.get(name, {})} if name else index.models
        entries = [entry for versions in selected.values() for entry in versions.values()]
        return sorted(entries, key=lambda entry: entry.created_at, reverse=True)

    def pin(self, name: str, version: str) -> ModelEntry:
        """Pin a model name to an existing version."""
        index = self._read_index()
        entry = self.get(name, version)
        index.pins[name] = version
        self._write_index(index)
        return entry

    def pinned_version(self, name: str) -> str | None:
        """Return the pinned version for a model, if one exists."""
        return self._read_index().pins.get(name)

    def _read_index(self) -> _RegistryIndex:
        if not self.index_path.exists():
            return _RegistryIndex()
        return _RegistryIndex.model_validate_json(self.index_path.read_text())

    def _write_index(self, index: _RegistryIndex) -> None:
        payload = index.model_dump(mode="json")
        self.index_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    @staticmethod
    def _latest_version(versions: dict[str, ModelEntry]) -> str:
        return max(versions.values(), key=lambda entry: entry.created_at).version

    @staticmethod
    def _validate_part(value: str, label: str) -> None:
        if not value or "/" in value or not _SAFE_PART.fullmatch(value):
            raise ModelRegistryError(f"invalid model {label}: {value!r}")  # noqa: TRY003
