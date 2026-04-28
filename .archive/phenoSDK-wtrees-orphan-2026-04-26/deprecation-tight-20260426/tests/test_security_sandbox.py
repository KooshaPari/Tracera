"""
Tests for the security sandbox manager facade.
"""

from __future__ import annotations

from pathlib import Path

from pheno.security.sandbox import (
    PermissionResult,
    SandboxManager,
    SandboxSecuritySettings,
    secure_file_access,
    validate_path_security,
)


def _make_manager(tmp_path: Path) -> SandboxManager:
    settings = SandboxSecuritySettings(
        allowed_paths=[str(tmp_path)],
        blocked_paths=[str(tmp_path / "blocked")],
        allowed_extensions={".txt"},
        max_file_size=1024,
        require_confirmation=False,
    )
    return SandboxManager(settings=settings)


def test_validate_path_security_allows_files_inside_workspace(tmp_path: Path) -> None:
    manager = _make_manager(tmp_path)
    file_path = tmp_path / "notes.txt"
    file_path.write_text("hello")

    result = validate_path_security(file_path, sandbox_manager=manager)
    assert isinstance(result, PermissionResult)
    assert result.allowed
    assert result.reason is None


def test_validate_path_security_blocks_blocklisted_directory(tmp_path: Path) -> None:
    blocked_dir = tmp_path / "blocked"
    blocked_dir.mkdir()
    blocked_file = blocked_dir / "secret.txt"
    blocked_file.write_text("secret")

    manager = _make_manager(tmp_path)
    result = validate_path_security(blocked_file, sandbox_manager=manager)
    assert not result.allowed
    assert "blocked directory" in (result.reason or "")


def test_secure_file_access_context(tmp_path: Path) -> None:
    manager = _make_manager(tmp_path)
    target = tmp_path / "managed.txt"
    target.write_text("data")

    with secure_file_access(target, sandbox_manager=manager) as context:
        assert context.workspace == tmp_path.resolve()
        assert target.read_text() == "data"
