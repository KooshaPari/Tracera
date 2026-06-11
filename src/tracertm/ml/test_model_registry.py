"""Tests for the ML model registry."""

# ruff: noqa: S101

from pathlib import Path

import pytest

from tracertm.ml import ModelRegistry, ModelRegistryError


@pytest.mark.unit
def test_save_list_and_load_latest(tmp_path: Path) -> None:
    """Save versions, list metadata, and load the latest version."""
    registry = ModelRegistry(tmp_path)

    registry.save("ranker", "1.0.0", {"weights": [1]}, metadata={"metric": 0.7})
    registry.save("ranker", "1.1.0", {"weights": [2]}, metadata={"metric": 0.9})

    entries = registry.list("ranker")

    assert [entry.version for entry in entries] == ["1.1.0", "1.0.0"]
    assert entries[0].metadata == {"metric": 0.9}
    assert registry.load("ranker") == {"weights": [2]}


@pytest.mark.unit
def test_pin_controls_default_load_without_blocking_explicit_versions(tmp_path: Path) -> None:
    """Pinned versions control default loads while explicit versions still work."""
    registry = ModelRegistry(tmp_path)

    registry.save("classifier", "1.0.0", {"version": "old"})
    registry.save("classifier", "1.1.0", {"version": "new"}, pin=True)
    registry.pin("classifier", "1.0.0")

    assert registry.pinned_version("classifier") == "1.0.0"
    assert registry.load("classifier") == {"version": "old"}
    assert registry.load("classifier", "1.1.0") == {"version": "new"}


@pytest.mark.unit
def test_save_requires_overwrite_for_existing_version(tmp_path: Path) -> None:
    """Existing model versions require explicit overwrite."""
    registry = ModelRegistry(tmp_path)
    registry.save("embedder", "1.0.0", "first")

    with pytest.raises(ModelRegistryError):
        registry.save("embedder", "1.0.0", "second")

    registry.save("embedder", "1.0.0", "second", overwrite=True)
    assert registry.load("embedder", "1.0.0") == "second"


@pytest.mark.unit
def test_rejects_unsafe_model_names(tmp_path: Path) -> None:
    """Unsafe names cannot escape the registry root."""
    registry = ModelRegistry(tmp_path)

    with pytest.raises(ModelRegistryError):
        registry.save("../escape", "v1", object())
