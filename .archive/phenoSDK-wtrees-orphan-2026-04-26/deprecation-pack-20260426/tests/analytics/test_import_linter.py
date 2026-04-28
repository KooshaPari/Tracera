
import pytest

from pheno.analytics.code import import_linter as module
from pheno.analytics.code import wily_support
from pheno.analytics.exceptions import AnalyticsDependencyError


def test_run_import_linter_missing_dependency(monkeypatch, tmp_path):
    monkeypatch.setattr(module, "lint_imports", None, raising=False)
    with pytest.raises(AnalyticsDependencyError):
        module.run_import_linter(tmp_path / "importlinter.ini")


def test_run_import_linter_success(monkeypatch, tmp_path):
    called = {}

    def fake_lint_imports(config_filename: str):
        called["config"] = config_filename
        return True

    monkeypatch.setattr(module, "lint_imports", fake_lint_imports, raising=False)
    config = tmp_path / "i.ini"
    config.write_text("[importlinter]\nroot_package=my_pkg\n")
    result = module.run_import_linter(config)
    assert result["success"] is True
    assert called["config"] == str(config.resolve())


def test_inspect_direct_imports_missing(monkeypatch):
    monkeypatch.setattr(module, "direct_imports_of", None, raising=False)
    with pytest.raises(AnalyticsDependencyError):
        module.inspect_direct_imports("my_pkg.module")


def test_inspect_direct_imports(monkeypatch):
    monkeypatch.setattr(module, "direct_imports_of", lambda name: {"os", "sys"}, raising=False)
    imports = module.inspect_direct_imports("pkg.mod")
    assert imports == ["os", "sys"]


def test_run_wily_report_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(wily_support.shutil, "which", lambda name: None)
    with pytest.raises(AnalyticsDependencyError):
        wily_support.run_wily_report(tmp_path)
