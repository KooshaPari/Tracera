from __future__ import annotations

import json
from pathlib import Path

from clink.registry import CONFIG_ENV_VAR, ClinkRegistry


def write_client(tmp_dir: Path, name: str) -> Path:
    cfg_dir = tmp_dir
    cfg_dir.mkdir(parents=True, exist_ok=True)
    path = cfg_dir / f"{name}.json"
    data = {
        "name": name,
        "command": name,
        "additional_args": [],
        "env": {},
        "roles": {"default": {"prompt_path": "systemprompts/clink/default.txt", "role_args": []}},
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_clink_registry_reads_env_override(tmp_path, monkeypatch):
    cfg_path = tmp_path
    write_client(cfg_path, "gemini")

    # Provide the default prompt path referenced by the JSON
    prompt_file = cfg_path / "systemprompts" / "clink" / "default.txt"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text("Default prompt", encoding="utf-8")

    monkeypatch.setenv(CONFIG_ENV_VAR, str(cfg_path))

    reg = ClinkRegistry()
    names = reg.list_clients()
    assert "gemini" in names
    roles = reg.list_roles("gemini")
    assert "default" in roles
