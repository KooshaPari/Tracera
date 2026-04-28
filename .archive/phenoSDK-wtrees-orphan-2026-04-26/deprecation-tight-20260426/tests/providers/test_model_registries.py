from __future__ import annotations

import json
from pathlib import Path

from pheno.providers.registry import OpenAIModelCatalog


def write_catalog(tmp_dir: Path, filename: str, models: list[dict]) -> Path:
    path = tmp_dir / filename
    path.write_text(json.dumps({"models": models}, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_openai_registry_alias_resolution(tmp_path, monkeypatch):
    catalog = write_catalog(
        tmp_path,
        "openai_models.json",
        [
            {
                "model_name": "gpt-5",
                "aliases": ["gpt5", "o5"],
                "context_window": 200000,
                "max_output_tokens": 8000,
            },
        ],
    )

    monkeypatch.setenv("OPENAI_MODELS_CONFIG_PATH", str(catalog))

    reg = OpenAIModelCatalog()

    # list_models should include canonical name
    assert "gpt-5" in reg.list_models()

    # aliases should resolve to canonical
    caps = reg.resolve("gpt5")
    assert caps and caps.get("model_name") == "gpt-5"

    caps2 = reg.get_capabilities("o5")
    assert caps2 and caps2.get("friendly_name", "").startswith("OpenAI (")
