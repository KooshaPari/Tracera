#!/usr/bin/env python3
"""Naming explosion guard shared across Go/Python/Frontend.

This consolidates patterns into a single ruleset to keep behavior consistent
and reduce drift between language-specific scripts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config/naming-guard.json"

DEFAULT_FORBIDDEN_WORDS = [
    "new",
    "improved",
    "enhanced",
    "updated",
    "fixed",
    "refactored",
    "modified",
    "revised",
    "copy",
    "backup",
    "old",
    "draft",
    "final",
    "latest",
    "temp",
    "tmp",
    "wip",
    "legacy",
    "deprecated",
    "duplicate",
    "alternate",
    "iteration",
    "replacement",
    "variant",
]

DEFAULT_CONFIG = {
    "forbidden_words": DEFAULT_FORBIDDEN_WORDS,
    "check_identifiers": True,
    "check_directories": True,
    "max_filename_length": 80,
    "max_dirname_length": 80,
    "max_identifier_length": 60,
    "max_path_depth": 12,
    "search": {
        "go": ["backend"],
        "python": ["src/tracertm", "tests"],
        "frontend": ["frontend/apps", "frontend/packages"],
    },
    "exclude_path_patterns": {
        "common": [
            "node_modules",
            "ARCHIVE",
            "__pycache__",
            "migrations",
            "dist",
            "coverage",
            "storybook-static",
            "docs",
            "CONFIG",
            "test-results",
            "openapi",
            "proto",
            ".git",
        ],
        "go": ["vendor", "temporal", "template"],
        "frontend": ["temporal", "/template", "TEMPLATE"],
    },
    "domain_exceptions": {
        "go": ["backup", "benchmark"],
        "python": [
            "backup",
            "benchmark",
            "test_final_(gap_|edge_)?coverage\\.py$",
            "test_.*_(batch|part)[0-9]+\\.py$",
        ],
        "frontend": ["benchmark"],
    },
    "identifier_exceptions": {
        "go": ["backup", "benchmark"],
        "python": ["backup", "benchmark"],
        "frontend": ["backup", "benchmark"],
    },
    "extensions": {
        "go": [".go"],
        "python": [".py"],
        "frontend": [".ts", ".tsx", ".js", ".jsx"],
    },
    "identifier_exclude_path_patterns": {
        "common": ["tests", "/tests/"],
        "go": [],
        "python": [],
        "frontend": [],
    },
}


def load_config() -> dict:
    """Load config."""
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return DEFAULT_CONFIG


def iter_files(roots: Iterable[Path], extensions: set[str], exclude_parts: list[str]) -> Iterable[Path]:
    """Iter files."""
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in extensions:
                continue
            path_str = str(path)
            if any(part in path_str for part in exclude_parts):
                continue
            yield path


def iter_directories(roots: Iterable[Path], exclude_parts: list[str]) -> Iterable[Path]:
    """Iter directories."""
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_dir():
                continue
            path_str = str(path)
            if any(part in path_str for part in exclude_parts):
                continue
            yield path


def compile_word_patterns(words: list[str]) -> dict[str, re.Pattern]:
    """Compile word patterns."""
    joined = "|".join(words)
    return {
        "suffix": re.compile(rf"_({joined})\\.", re.IGNORECASE),
        "prefix": re.compile(rf"^({joined})_[A-Za-z0-9_]+", re.IGNORECASE),
        "middle": re.compile(rf"_({joined})(_|\\.)", re.IGNORECASE),
        "kebab": re.compile(rf"-({joined})(\\.|_)", re.IGNORECASE),
    }


def split_identifier_tokens(name: str) -> list[str]:
    """Split identifier tokens."""
    base = re.sub(r"[_.-]+", " ", name)
    base = re.sub(r"([a-z0-9])([A-Z])", r"\\1 \\2", base)
    base = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\\1 \\2", base)
    return [token.lower() for token in base.split() if token]


def matches_domain_exception(path: Path, exceptions: list[str]) -> bool:
    """Matches domain exception."""
    path_str = str(path)
    return any(re.search(pattern, path_str) for pattern in exceptions)


def has_stutter(name: str) -> bool:
    """Has stutter."""
    base = re.sub(r"\.[A-Za-z0-9]+$", "", name)
    tokens = [token for token in split_identifier_tokens(base) if len(token) > 1]
    return any(tokens[i] == tokens[i + 1] for i in range(len(tokens) - 1))


def is_violation(
    path: Path,
    lang: str,
    patterns: dict[str, re.Pattern],
    exceptions: list[str],
    max_filename_length: int,
    max_dirname_length: int,
    max_path_depth: int,
) -> bool:
    """Is violation."""
    if matches_domain_exception(path, exceptions):
        return False

    name = path.name
    if path.is_file() and len(name) > max_filename_length:
        return True
    if path.is_dir() and len(name) > max_dirname_length:
        return True
    if len(path.parts) > max_path_depth:
        return True
    if has_stutter(name):
        return True

    versioned = re.search(r"(_v|V|v|version|ver|rev|iter)[-_]?[0-9]+", name, re.IGNORECASE)
    if versioned:
        return True

    name_digits = re.search(r"[A-Za-z]{2,}[0-9]+\\.", name)
    if name_digits:
        return True

    numbered = re.search(r"_[0-9]+\\.", name)
    if numbered:
        return True

    phase = re.search(r"phase[-_]?[0-9]+", name, re.IGNORECASE)
    if phase:
        return True

    if patterns["suffix"].search(name):
        return True
    if patterns["prefix"].search(name):
        return True
    if patterns["middle"].search(name):
        return True
    if patterns["kebab"].search(name):
        return True

    if lang in {"go", "frontend"}:
        pascal_prefix = re.search(
            r"^(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised|Copy|Backup|Old|Draft|Final|Latest|Temp|Tmp|Wip|Legacy|Deprecated|Duplicate|Alternate)[A-Z]",
            name,
            re.IGNORECASE,
        )
        if pascal_prefix:
            return True
        pascal_suffix = re.search(
            r"(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised|Final|Latest)\\.", name, re.IGNORECASE
        )
        if pascal_suffix:
            return True

    return False


def matches_identifier_exception(name: str, exceptions: list[str]) -> bool:
    """Matches identifier exception."""
    return any(re.search(pattern, name, re.IGNORECASE) for pattern in exceptions)


def is_identifier_violation(
    name: str,
    _lang: str,
    _patterns: dict[str, re.Pattern],
    forbidden_identifier_words: list[str],
    exceptions: list[str],
    max_identifier_length: int,
) -> bool:
    """Is identifier violation."""
    if matches_identifier_exception(name, exceptions):
        return False

    if name.startswith("__") and name.endswith("__"):
        return False
    if len(name) > max_identifier_length:
        return True
    if has_stutter(name):
        return True

    versioned = re.search(r"(_v|V|v|version|ver|rev|iter)[-_]?[0-9]+", name, re.IGNORECASE)
    if versioned:
        return True

    name_digits = re.search(r"[A-Za-z]{2,}[0-9]+$", name)
    if name_digits:
        return True

    numbered = re.search(r"_[0-9]+$", name)
    if numbered:
        return True

    phase = re.search(r"phase[-_]?[0-9]+", name, re.IGNORECASE)
    if phase:
        return True

    tokens = split_identifier_tokens(name)
    return bool(any(token in forbidden_identifier_words for token in tokens))


def strip_ts_comments(source: str) -> str:
    """Strip ts comments."""
    source = re.sub(r"/\\*.*?\\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//.*", "", source)


def iter_ts_identifiers(source: str) -> Iterable[str]:
    """Iter ts identifiers."""
    source = strip_ts_comments(source)
    patterns = [
        r"\\bclass\\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\\binterface\\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\\btype\\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\\benum\\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\\bfunction\\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\\b(?:const|let|var)\\s+([A-Za-z_][A-Za-z0-9_]*)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, source):
            yield match.group(1)


def iter_go_identifiers(source: str) -> Iterable[str]:
    """Iter go identifiers."""
    patterns = [
        r"^\\s*func\\s+(?:\\([^)]*\\)\\s*)?([A-Za-z_][A-Za-z0-9_]*)",
        r"^\\s*type\\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"^\\s*(?:var|const)\\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"^\\s*([A-Za-z_][A-Za-z0-9_]*)\\s+(?:struct|interface)\\b",
    ]
    for line in source.splitlines():
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                yield match.group(1)


def iter_python_identifiers(path: Path) -> Iterable[str]:
    """Iter python identifiers."""
    import ast

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield node.name
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    yield target.id


def iter_identifier_names(path: Path, lang: str) -> Iterable[str]:
    """Iter identifier names."""
    if lang == "python":
        return iter_python_identifiers(path)
    source = path.read_text(encoding="utf-8")
    if lang == "go":
        return iter_go_identifiers(source)
    return iter_ts_identifiers(source)


def main() -> int:
    """Main."""
    parser = argparse.ArgumentParser(description="Naming explosion guard")
    parser.add_argument("--lang", choices=["go", "python", "frontend"], required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    config = load_config()
    forbidden_words = config.get("forbidden_words", DEFAULT_FORBIDDEN_WORDS)
    forbidden_identifier_words = config.get("forbidden_identifier_words", forbidden_words)
    check_identifiers = config.get("check_identifiers", True)
    check_directories = config.get("check_directories", True)
    max_filename_length = int(config.get("max_filename_length", 80))
    max_dirname_length = int(config.get("max_dirname_length", 80))
    max_identifier_length = int(config.get("max_identifier_length", 60))
    max_path_depth = int(config.get("max_path_depth", 12))
    search_dirs = config.get("search", {}).get(args.lang, [])
    extensions = set(config.get("extensions", {}).get(args.lang, []))
    exclude_parts = config.get("exclude_path_patterns", {}).get("common", [])
    exclude_parts += config.get("exclude_path_patterns", {}).get(args.lang, [])
    exceptions = config.get("domain_exceptions", {}).get(args.lang, [])
    identifier_exceptions = config.get("identifier_exceptions", {}).get(args.lang, [])
    identifier_exclude = config.get("identifier_exclude_path_patterns", {}).get("common", [])
    identifier_exclude += config.get("identifier_exclude_path_patterns", {}).get(args.lang, [])

    root = Path(args.root)
    roots = [root / Path(dir_path) for dir_path in search_dirs]

    patterns = compile_word_patterns(forbidden_words)

    violations: list[Path] = []
    directory_violations: list[Path] = []
    identifier_violations: dict[Path, list[str]] = {}
    if check_directories:
        directory_violations.extend(
            path
            for path in iter_directories(roots, exclude_parts)
            if is_violation(
                path,
                args.lang,
                patterns,
                exceptions,
                max_filename_length,
                max_dirname_length,
                max_path_depth,
            )
        )
    for path in iter_files(roots, extensions, exclude_parts):
        if args.lang == "go" and (path.name.endswith("_test.go") or path.name.endswith(".pb.go")):
            continue
        if args.lang == "python" and path.name.endswith("_pb2_grpc.py"):
            continue
        if args.lang == "python" and path.name.endswith("_pb2.py"):
            continue
        if is_violation(
            path,
            args.lang,
            patterns,
            exceptions,
            max_filename_length,
            max_dirname_length,
            max_path_depth,
        ):
            violations.append(path)
        if check_identifiers and not any(part in str(path) for part in identifier_exclude):
            names = [
                name
                for name in iter_identifier_names(path, args.lang)
                if is_identifier_violation(
                    name,
                    args.lang,
                    patterns,
                    forbidden_identifier_words,
                    identifier_exceptions,
                    max_identifier_length,
                )
            ]
            if names:
                identifier_violations[path] = sorted(set(names))

    if violations or directory_violations or identifier_violations:
        if directory_violations:
            for _path in sorted(set(directory_violations)):
                pass
        if violations:
            for _path in sorted(set(violations)):
                pass
        if identifier_violations:
            for path in sorted(identifier_violations):
                for _name in identifier_violations[path]:
                    pass
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
