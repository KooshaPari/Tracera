from typing import Any

"""E2E-like CLI flows for export/import using fakes (no real DB/filesystem)."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

runner = CliRunner()


def _fake_storage_manager() -> None:
    class _FakeSession:
        def __init__(self) -> None:
            self._project = SimpleNamespace(
                id="proj-1",
                name="Project One",
                description="desc",
                created_at=None,
                updated_at=None,
            )
            self._items = [
                SimpleNamespace(
                    id="item-1",
                    title="Login",
                    description="",
                    view="FEATURE",
                    item_type="feature",
                    status="todo",
                    priority="P1",
                    owner="alice",
                    parent_id=None,
                    item_metadata={},
                    version=1,
                    created_at=None,
                    updated_at=None,
                ),
            ]
            self._links = [
                SimpleNamespace(
                    id="lnk-1",
                    source_item_id="item-1",
                    target_item_id="item-2",
                    link_type="implements",
                    link_metadata={},
                    created_at=None,
                ),
            ]

        # SQLAlchemy-like API shim
        def query(self, model: Any) -> None:
            self._model = model
            return self

        def filter(self, *_args: Any, **_kwargs: Any) -> None:
            return self

        def first(self) -> None:
            return self._project

        def all(self) -> None:
            if self._model.__name__ == "Item":
                return self._items
            return self._links

    class _Storage:
        def get_session(self) -> None:
            class _Ctx:
                def __enter__(self) -> None:
                    return _FakeSession()

                def __exit__(self, *_: Any) -> None:
                    return False

            return _Ctx()

    return _Storage()


@pytest.mark.e2e
def test_export_json_writes_output(tmp_path: Any) -> None:
    out_file = tmp_path / "export.json"

    with (
        patch("tracertm.cli.commands.export.ConfigManager") as cfg,
        patch("tracertm.cli.commands.export._get_storage_manager", return_value=_fake_storage_manager()),
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = "proj-1"
        cfg.return_value = cfg_inst

        result = runner.invoke(
            app,
            ["export", "--format", "json", "--output", str(out_file)],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["project"]["id"] == "proj-1"
    assert data["items"][0]["title"] == "Login"


@pytest.mark.e2e
def test_export_yaml_and_csv(tmp_path: Any) -> None:
    yaml_out = tmp_path / "export.yaml"
    csv_out = tmp_path / "export.csv"

    with (
        patch("tracertm.cli.commands.export.ConfigManager") as cfg,
        patch("tracertm.cli.commands.export._get_storage_manager", return_value=_fake_storage_manager()),
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = "proj-1"
        cfg.return_value = cfg_inst

        res_yaml = runner.invoke(app, ["export", "--format", "yaml", "--output", str(yaml_out)], catch_exceptions=False)
        res_csv = runner.invoke(app, ["export", "--format", "csv", "--output", str(csv_out)], catch_exceptions=False)

    assert res_yaml.exit_code == 0
    assert "project:" in yaml_out.read_text()
    assert res_csv.exit_code == 0
    assert "ID,Title,Description" in csv_out.read_text().splitlines()[0]


@pytest.mark.e2e
def test_export_unsupported_format_fails() -> None:
    with patch("tracertm.cli.commands.export.ConfigManager") as cfg:
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = "proj-1"
        cfg.return_value = cfg_inst

        result = runner.invoke(app, ["export", "--format", "pdf"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "Unsupported format" in result.stdout


@pytest.mark.e2e
def test_import_json_validate_only_passes(tmp_path: Any) -> None:
    payload = {
        "project": {"id": "proj-1", "name": "Project One"},
        "items": [],
        "links": [],
    }
    src = tmp_path / "backup.json"
    src.write_text(json.dumps(payload))

    with (
        patch("tracertm.cli.commands.import_cmd._validate_import_data", return_value=[]),
        patch("tracertm.cli.commands.import_cmd._import_data", return_value=None),
    ):
        result = runner.invoke(app, ["import", "json", str(src), "--validate-only"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Validation passed" in result.stdout


@pytest.mark.e2e
def test_import_json_missing_file_fails(tmp_path: Any) -> None:
    missing = tmp_path / "nope.json"
    result = runner.invoke(app, ["import", "json", str(missing)], catch_exceptions=False)
    assert result.exit_code != 0
    assert "File not found" in result.stdout


@pytest.mark.e2e
def test_import_json_validation_errors(tmp_path: Any) -> None:
    bad_payload = {"project": {}, "items": "not-a-list"}
    src = tmp_path / "bad.json"
    src.write_text(json.dumps(bad_payload))

    with patch("tracertm.cli.commands.import_cmd._validate_import_data", return_value=["items must be list"]):
        result = runner.invoke(app, ["import", "json", str(src)], catch_exceptions=False)

    assert result.exit_code != 0
    assert "Validation errors" in result.stdout


@pytest.mark.e2e
def test_import_yaml_success(tmp_path: Any) -> None:
    payload = """
project:
  id: proj-1
  name: Project One
items: []
links: []
"""
    src = tmp_path / "backup.yaml"
    src.write_text(payload)

    with (
        patch("tracertm.cli.commands.import_cmd._validate_import_data", return_value=[]),
        patch("tracertm.cli.commands.import_cmd._import_data", return_value=None),
    ):
        result = runner.invoke(app, ["import", "yaml", str(src), "--validate-only"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Validation passed" in result.stdout
