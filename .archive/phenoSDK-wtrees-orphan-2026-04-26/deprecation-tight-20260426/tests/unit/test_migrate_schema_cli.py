from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from migrate_schema import (  # type: ignore  # noqa: E402
    SchemaHealth,
    check_schema_health,
)


def test_check_schema_health_offline(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    health, diff = check_schema_health(tmp_path, offline=True)
    assert isinstance(health, SchemaHealth)
    assert diff is None
    assert health.status == "offline"
