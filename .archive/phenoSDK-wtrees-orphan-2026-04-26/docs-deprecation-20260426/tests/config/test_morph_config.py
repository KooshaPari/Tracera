from pheno.config.core import MorphConfig


def test_morph_config_defaults():
    cfg = MorphConfig()
    assert cfg.enable_structlog is True
    assert cfg.security_profile == "strict"
    assert "semantic_search" in cfg.subsystem_timeouts


def test_morph_config_env_override(monkeypatch):
    monkeypatch.setenv("MORPH_ENABLE_PRESIDIO", "true")
    data = MorphConfig.from_env(prefix="morph_").model_dump()
    assert data.get("enable_presidio") is True
