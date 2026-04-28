from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from pytest import MonkeyPatch

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from ingest_benchmarks import MANIFEST_ENV_KEY
from ingest_benchmarks import main as ingest_main  # type: ignore  # noqa: E402


def run_cli(tmp_path: Path, argv: list[str]) -> None:
    manifest = tmp_path / "manifest.json"
    with MonkeyPatch.context() as mp:
        mp.setenv(MANIFEST_ENV_KEY, str(manifest))
        ingest_main(argv)


def test_register_updates_manifest(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "datasets"
    run_cli(
        tmp_path,
        [
            "register",
            "--dataset",
            "swe-bench-lite",
            "--source",
            "https://example.com/swe-bench-lite",
            "--split",
            "train",
            "--samples",
            "300",
        ],
    )

    manifest_path = tmp_path / "manifest.json"
    with manifest_path.open() as handle:
        manifest = json.load(handle)

    assert "swe-bench-lite" in manifest
    assert manifest["swe-bench-lite"]["split"] == "train"


def test_list_handles_empty_manifest(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run_cli(tmp_path, ["list"])
    captured = capsys.readouterr()
    assert "No benchmark datasets registered" in captured.out
