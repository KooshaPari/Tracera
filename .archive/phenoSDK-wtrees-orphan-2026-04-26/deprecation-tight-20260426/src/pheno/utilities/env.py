"""
Environment file loading utilities.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

logger = get_logger("pheno.env")


class EnvLoadError(RuntimeError):
    """
    Raised when environment loading fails.
    """


@dataclass
class EnvConfig:
    """
    Configuration for environment loading.
    """

    base_dir: Path = field(default_factory=Path.cwd)
    env_files: Iterable[str] = field(default_factory=lambda: (".env", ".env.local"))
    override_existing: bool = False
    required_vars: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.base_dir.exists():
            raise EnvLoadError(f"Base directory does not exist: {self.base_dir}")


def parse_env_file(file_path: Path) -> Iterator[tuple[str, str]]:
    """
    Parse environment file and yield key-value pairs.
    """
    if not file_path.exists():
        return

    try:
        with open(file_path, encoding="utf-8") as handle:
            for line_num, line in enumerate(handle, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    logger.warning("Invalid line %s in %s: %s", line_num, file_path, stripped)
                    continue
                key, _, value = stripped.partition("=")
                key = key.strip()
                value = value.strip()
                if value and value[0] in {'"', "'"} and value[-1] == value[0]:
                    value = value[1:-1]
                if key:
                    yield key, value
    except Exception as exc:
        raise EnvLoadError(f"Failed to parse {file_path}: {exc}") from exc


def load_env_files(config: EnvConfig | None = None) -> dict[str, str]:
    """
    Load environment variables from configured .env files.
    """
    config = config or EnvConfig()

    try:  # pragma: no cover - optional dependency
        from dotenv import dotenv_values  # type: ignore

        use_dotenv = True
    except ImportError:
        use_dotenv = False
        if any((config.base_dir / name).exists() for name in config.env_files):
            logger.info(
                "python-dotenv not installed; falling back to built-in parser. "
                "Install python-dotenv for improved .env support.",
            )

    merged: dict[str, str] = {}
    for env_file in config.env_files:
        path = config.base_dir / env_file
        if not path.exists():
            logger.debug("Env file not found: %s", path)
            continue
        try:
            if use_dotenv:
                values = dotenv_values(path)  # type: ignore
                if values:
                    merged.update({k: v for k, v in values.items() if v is not None})
                    logger.info("Loaded %s variables from %s", len(values), env_file)
            else:
                values = dict(parse_env_file(path))
                merged.update(values)
                logger.info("Loaded %s variables from %s", len(values), env_file)
        except Exception as exc:
            logger.warning("Failed loading %s: %s", env_file, exc)

    applied = 0
    for key, value in merged.items():
        if config.override_existing or key not in os.environ:
            os.environ[key] = value
            applied += 1
    logger.info("Applied %s environment variables", applied)

    missing = config.required_vars - set(os.environ.keys())
    if missing:
        raise EnvLoadError(f"Missing required environment variables: {', '.join(sorted(missing))}")

    return merged


@contextmanager
def temporary_env(**overrides: str) -> Iterator[None]:
    """
    Temporarily set environment variables within the context.
    """
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            os.environ[key] = str(value)
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def get_env_var(key: str, default: str | None = None, *, required: bool = False) -> str | None:
    """
    Return environment variable value with optional default and validation.
    """
    value = os.environ.get(key, default)
    if required and value is None:
        raise EnvLoadError(f"Required environment variable not set: {key}")
    return value


def collect_env(prefix: str) -> dict[str, str]:
    """
    Collect environment variables that start with the given prefix (case-insensitive).
    """
    prefix_upper = prefix.upper()
    return {key: value for key, value in os.environ.items() if key.upper().startswith(prefix_upper)}


__all__ = [
    "EnvConfig",
    "EnvLoadError",
    "collect_env",
    "get_env_var",
    "load_env_files",
    "parse_env_file",
    "temporary_env",
]
