"""Tests for content-addressed model registry behavior."""


from pathlib import Path

import pytest

from tracertm.ml.registry import ModelRegistry, ModelRegistryError


@pytest.mark.unit
def test_save_load_and_list_pickle_model(tmp_path: Path) -> None:
    registry = ModelRegistry(tmp_path)

    first = registry.save("ranker", "1.0.0", {"weights": [1]}, metadata={"auc": 0.7})
    second = registry.save("ranker", "1.1.0", {"weights": [2]}, metadata={"auc": 0.9})

    assert first.artifact_path.startswith("models/ranker/1.0.0/blobs/")
    assert second.sha256 != first.sha256
    assert [entry.version for entry in registry.list("ranker")] == ["1.1.0", "1.0.0"]
    assert registry.load("ranker") == {"weights": [2]}


@pytest.mark.unit
def test_pin_records_semver_and_sha_for_default_load(tmp_path: Path) -> None:
    registry = ModelRegistry(tmp_path)
    registry.save("classifier", "1.0.0", {"version": "old"})
    registry.save("classifier", "1.1.0", {"version": "new"})

    pinned = registry.pin("classifier", "1.0.0")

    assert registry.pinned_version("classifier") == "1.0.0"
    assert registry.get("classifier").sha256 == pinned.sha256
    assert registry.load("classifier") == {"version": "old"}
    assert registry.load("classifier", "1.1.0") == {"version": "new"}


@pytest.mark.unit
def test_onnx_adapter_stores_content_addressed_blob(tmp_path: Path) -> None:
    registry = ModelRegistry(tmp_path)
    payload = b"onnx-model-bytes"

    entry = registry.save("detector", "2.0.0", payload, format="onnx")

    assert entry.format == "onnx"
    assert entry.artifact_path.endswith(f"{entry.sha256}.onnx")
    assert (tmp_path / entry.artifact_path).read_bytes() == payload
    assert registry.load("detector", "2.0.0") == payload


@pytest.mark.unit
def test_rejects_non_semver_and_duplicate_versions(tmp_path: Path) -> None:
    registry = ModelRegistry(tmp_path)

    with pytest.raises(ModelRegistryError):
        registry.save("embedder", "v1", object())

    registry.save("embedder", "1.0.0", "first")
    with pytest.raises(ModelRegistryError):
        registry.save("embedder", "1.0.0", "second")
