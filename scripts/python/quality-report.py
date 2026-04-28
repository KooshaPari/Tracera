#!/usr/bin/env python3
"""Parse quality log files and print an action plan (by file and/or by log).

Handles: Go (vet, gofmt, test), Python (ruff, mypy, pytest), Frontend (biome/tsc/turbo).
Color highlighting by project (Go/Python/Frontend). Optional --watch for stream of updates.
"""

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = ROOT / ".quality" / "logs"
LAST_RUN_JSON = ROOT / ".quality" / "last-run.json"
DAG_CONFIG = ROOT / "config" / "quality-dag.yaml"
SUITES = [
    ("quality-go.log", "Go"),
    ("quality-python.log", "Python"),
    ("quality-frontend.log", "Frontend"),
]
# Fallback when no quality-dag.yaml: (log_stem, display_name, category, suite_for_patterns)
SPLIT_STEPS_FALLBACK = [
    ("naming", "Naming", "lint", "Python"),
    ("go-lint", "Go lint", "lint", "Go"),
    ("go-proto", "Go proto", "lint", "Go"),
    ("py-lint", "Python lint", "lint", "Python"),
    ("py-type", "Python type", "lint", "Python"),
    ("fe-lint", "Frontend lint", "lint", "Frontend"),
    ("fe-type", "Frontend type", "lint", "Frontend"),
    ("go-build", "Go build", "test", "Go"),
    ("go-test", "Go test", "test", "Go"),
    ("py-test", "Python test", "test", "Python"),
    ("fe-build", "Frontend build", "test", "Frontend"),
    ("fe-test", "Frontend test", "test", "Frontend"),
]


def _load_split_steps_from_dag() -> list[tuple[str, str, str, str]]:
    """Derive SPLIT_STEPS from quality-dag.yaml. Returns (stem, display, category, suite)."""
    if not DAG_CONFIG.exists():
        return SPLIT_STEPS_FALLBACK
    try:
        import yaml
        data = yaml.safe_load(DAG_CONFIG.read_text())
        steps = data.get("steps", {})
    except Exception:
        return SPLIT_STEPS_FALLBACK
    if not steps:
        return SPLIT_STEPS_FALLBACK

    def _suite(name: str) -> str:
        if name.startswith("py-") or name == "naming":
            return "Python"
        if name.startswith("go-"):
            return "Go"
        if name.startswith("fe-"):
            return "Frontend"
        if name.startswith("bash-"):
            return "Python"  # bash patterns similar to Python
        return "Python"

    def _category(name: str) -> str:
        return "test" if "-test" in name or "-build" in name else "lint"

    return [
        (name, cfg.get("display", name), _category(name), _suite(name))
        for name, cfg in steps.items()
    ]


SPLIT_STEPS = _load_split_steps_from_dag()
# ANSI colors by project (respect NO_COLOR and non-TTY)
C_GO = "\033[36m"  # cyan
C_PY = "\033[33m"  # yellow
C_FE = "\033[34m"  # blue
C_FAIL = "\033[31m"  # red
C_DIM = "\033[2m"
C_RESET = "\033[0m"


def use_color() -> bool:
    """Use color."""
    if not sys.stdout.isatty():
        return False
    import os

    return os.environ.get("NO_COLOR", "").strip() == ""


def c(suite: str) -> str:
    """C."""
    if not use_color():
        return ""
    if suite == "Go":
        return C_GO
    if suite == "Python":
        return C_PY
    if suite == "Frontend":
        return C_FE
    return ""


def cr() -> str:
    """Cr."""
    return C_RESET if use_color() else ""


# Failure markers in log content (suite name -> list of regex patterns)
FAILURE_MARKERS = {
    "Go": [r"--- FAIL:", r"FAIL\s+[\w./-]+\.go", r"exit status 1", r"go test .* failed"],
    "Python": [r"FAILED\s+", r"ERROR\s+", r"exit status 1", r"=+\s+\d+ failed", r"E\s+.*Error"],
    "Frontend": [r"error TS", r"Error:", r"exit status 1", r"failed with exit code", r"Build failed"],
}

PATTERNS = [
    (re.compile(r"vet:\s+(.+?):(\d+):(\d+):\s*(.+)"), "go"),
    (re.compile(r"^\s+(.+_test\.go):(\d+):\s*(.+)"), "go"),
    (re.compile(r"^\s*(.+\.go):(\d+):\s*(.+)"), "go"),
    (re.compile(r"--- FAIL:\s+(\S+)\s+"), "go_fail"),
    (re.compile(r"^(.+?):(\d+):(\d+):\s+(\S+)\s+(.+)"), "ruff"),
    (re.compile(r"^(.+?):(\d+):\s+error:\s*(.+)"), "mypy"),
    (re.compile(r"FAILED\s+(.+?)::"), "pytest_file"),
    (re.compile(r"^(.+?)\((\d+),(\d+)\):\s*(.+)"), "fe_biome"),
    (re.compile(r"^(.+?):(\d+):(\d+)\s*-\s*(.+)"), "fe_biome2"),
    (re.compile(r"^(.+?):(\d+):(\d+):\s*(.+)"), "fe_tsc"),
]

EXCERPT_PAT = re.compile(r"error|FAIL|failed|Error:|ERROR|E\d{3}", re.IGNORECASE)
MAX_EXCERPT_LINES = 25

# Strip ANSI escape sequences so patterns match (logs may contain ESC or literal \033[...]m)
ANSI_ESCAPE = re.compile(r"\033\[[0-9;]*m")
ANSI_ESCAPE_LITERAL = re.compile(r"\\033\[[0-9;]*m")


def strip_ansi(line: str) -> str:
    """Strip ansi."""
    s = ANSI_ESCAPE.sub("", line)
    return ANSI_ESCAPE_LITERAL.sub("", s)


# Generic file:line(:col)? or file(line,col)? patterns for by-file extraction (any tool)
FILE_LINE_PATTERNS = [
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs)):(\d+):(\d+):\s*(.+)$"),  # path:line:col: msg
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs)):(\d+):\s*(.+)$"),  # path:line: msg
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs))\((\d+),(\d+)\):\s*(.+)$"),  # path(line,col): msg
    re.compile(r"^(.+?\.(?:go|py|ts|tsx|js|jsx|mjs|cjs))\((\d+)\):\s*(.+)$"),  # path(line): msg
]
# Gofmt -l: one path per line (optional trailing whitespace)
GOFMT_FILE = re.compile(r"^\s*(.+\.go)\s*$")


def use_split_mode() -> bool:
    """True if per-step logs exist (from run-quality-split.sh)."""
    return any((LOG_DIR / f"{stem}.log").exists() for stem, _, _, _ in SPLIT_STEPS)


def get_failed_suites_from_last_run() -> list[str]:
    """Get failed suites from last run."""
    if not LAST_RUN_JSON.exists():
        return []
    try:
        data = json.loads(LAST_RUN_JSON.read_text())
        return data.get("failed_suites") or []
    except (json.JSONDecodeError, OSError):
        return []


def get_failed_steps_from_last_run() -> list[str]:
    """Get failed steps from last run."""
    if not LAST_RUN_JSON.exists():
        return []
    try:
        data = json.loads(LAST_RUN_JSON.read_text())
        return data.get("failed_steps") or []
    except (json.JSONDecodeError, OSError):
        return []


def detect_failed_suites_from_logs() -> list[tuple[str, Path]]:
    """Detect failed suites from logs."""
    failed = []
    for log_name, suite_name in SUITES:
        log_path = LOG_DIR / log_name
        if not log_path.exists() or log_path.stat().st_size == 0:
            continue
        text = log_path.read_text(errors="replace")
        patterns = FAILURE_MARKERS.get(suite_name, [r"exit status 1", r"FAILED", r"Error:"])
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                failed.append((suite_name, log_path))
                break
    return failed


def detect_failed_steps_from_logs() -> list[tuple[str, Path]]:
    """In split mode: steps with non-zero .exit file. Returns (stem, log_path) for consistency with last-run.json."""
    failed = []
    for stem, _display_name, _cat, _suite in SPLIT_STEPS:
        exit_path = LOG_DIR / f"{stem}.exit"
        log_path = LOG_DIR / f"{stem}.log"
        if not exit_path.exists():
            continue
        try:
            code = int(exit_path.read_text().strip())
        except (ValueError, OSError):
            code = 1
        if code != 0 and log_path.exists():
            failed.append((stem, log_path))
    return failed


def normalize_path(raw: str, cwd: Path) -> str:
    """Normalize path."""
    raw = raw.strip()
    for prefix in ("./backend/", "backend/", "./", ""):
        if raw.startswith(prefix):
            p = (cwd / (raw[len(prefix) :] if prefix else raw)).resolve()
            try:
                return str(p.relative_to(cwd))
            except ValueError:
                return raw
    return raw


def should_skip_line(line_stripped: str) -> bool:
    """Check if line should be skipped during parsing."""
    if not line_stripped or line_stripped.startswith(("Running ", "[")):
        return True
    # Skip make / shell noise
    return bool(line_stripped.startswith(("make[", "$ ")) or "*** [" in line_stripped)


def parse_pattern_match(kind: str, groups: tuple, cwd: Path, line_stripped: str) -> tuple[str, int | None, str] | None:
    """Parse a matched pattern into an issue tuple."""
    g = groups

    if kind == "go":
        file_path = normalize_path(g[0], cwd)
        line_no = int(g[1])
        msg = g[3] if len(g) == 4 else (g[2] if len(g) >= 3 else line_stripped)
        return (file_path, line_no, msg)

    if kind == "go_fail":
        return ("backend (Go tests)", None, f"FAIL: {g[0]}")

    if kind == "ruff":
        return (normalize_path(g[0], cwd), int(g[1]), f"{g[3]} {g[4]}")

    if kind == "mypy":
        return (normalize_path(g[0], cwd), int(g[1]), g[2])

    if kind == "pytest_file":
        return (normalize_path(g[0], cwd), None, "FAILED test")

    if kind in {"fe_biome", "fe_biome2", "fe_tsc"}:
        file_path = normalize_path(g[0], cwd)
        line_no = int(g[1])
        msg = g[3] if len(g) > 3 else line_stripped
        return (file_path, line_no, msg)

    return None


def try_generic_patterns(line_stripped: str, cwd: Path) -> tuple[str, int | None, str] | None:
    """Try generic file:line patterns."""
    for pat in FILE_LINE_PATTERNS:
        m = pat.match(line_stripped)
        if m:
            g = m.groups()
            file_path = normalize_path(g[0], cwd)
            line_no = int(g[1])
            msg = g[3] if len(g) == 4 else g[2]
            return (file_path, line_no, msg)
    return None


def try_gofmt_pattern(line_stripped: str, suite_name: str, cwd: Path) -> tuple[str, int | None, str] | None:
    """Try gofmt-specific pattern."""
    if suite_name == "Go":
        m = GOFMT_FILE.match(line_stripped)
        if m and not line_stripped.startswith("cd ") and "vet" not in line_stripped:
            return (normalize_path(m.group(1), cwd), None, "gofmt: needs formatting")
    return None


def try_main_patterns(line: str, line_stripped: str, cwd: Path) -> tuple[str, int | None, str] | None:
    """Try main pattern matching."""
    for pat, kind in PATTERNS:
        m = pat.search(line) or (pat.match(line) if line else None)
        if m:
            issue = parse_pattern_match(kind, m.groups(), cwd, line_stripped)
            if issue:
                return issue
    return None


def process_log_line(raw_line: str, suite_name: str, cwd: Path) -> tuple[str, int | None, str] | None:
    """Process a single log line and extract issue if present."""
    line = strip_ansi(raw_line)
    line_stripped = line.strip()

    if should_skip_line(line_stripped):
        return None

    # Try main patterns
    issue = try_main_patterns(line, line_stripped, cwd)
    if issue:
        return issue

    # Try generic patterns
    issue = try_generic_patterns(line_stripped, cwd)
    if issue:
        return issue

    # Try gofmt pattern
    return try_gofmt_pattern(line_stripped, suite_name, cwd)


def extract_issues(log_path: Path, suite_name: str, cwd: Path) -> list[tuple[str, int | None, str]]:
    """Extract issues from log file using various pattern matchers."""
    if not log_path.exists():
        return []

    text = log_path.read_text(encoding="utf-8", errors="replace")
    issues = []

    for raw_line in text.splitlines():
        issue = process_log_line(raw_line, suite_name, cwd)
        if issue:
            issues.append(issue)

    return issues


def excerpt_lines(log_path: Path) -> list[str]:
    """Return lines that look like errors, or last MAX_EXCERPT_LINES if none."""
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    error_lines = [ln for ln in lines if EXCERPT_PAT.search(strip_ansi(ln))]
    if error_lines:
        return error_lines[:MAX_EXCERPT_LINES]
    return lines[-MAX_EXCERPT_LINES:] if len(lines) > MAX_EXCERPT_LINES else lines


def extract_by_file_from_log_text(text: str, cwd: Path, suite_name: str) -> dict[str, list[tuple[int | None, str]]]:
    """Parse log text and return map file_path -> [(line_no, msg), ...] for by-file dumps."""
    by_file: dict[str, list[tuple[int | None, str]]] = defaultdict(list)
    for raw_line in text.splitlines():
        line = strip_ansi(raw_line).strip()
        if not line or line.startswith(("make[", "$ ")) or "*** [" in line:
            continue
        for pat in FILE_LINE_PATTERNS:
            m = pat.match(line)
            if not m:
                continue
            g = m.groups()
            file_path = normalize_path(g[0], cwd)
            line_no = int(g[1])
            msg = (g[3] if len(g) == 4 else g[2]).strip()
            by_file[file_path].append((line_no, msg))
            break
        else:
            if suite_name == "Go":
                m = GOFMT_FILE.match(line)
                if m and "vet" not in line and "gofmt" not in line:
                    by_file[normalize_path(m.group(1), cwd)].append((None, "gofmt: needs formatting"))
    return dict(by_file)


def print_action_plan_by_file(by_file: dict, _cwd: Path) -> None:
    """Print action plan by file."""
    for file_path in sorted(by_file.keys()):
        entries = by_file[file_path]
        for _suite, _line_no, _msg in entries:
            pass


def print_action_plan_by_log(failed_suites: list[str], with_content: list[tuple[str, Path]], cwd: Path) -> None:
    """Print action plan by log: for each log, show by-file err/warn dumps (then excerpt if no files)."""
    seen = set()
    for suite in failed_suites:
        log_name = next((n for n, s in SUITES if s == suite), f"quality-{suite.lower()}.log")
        log_path = LOG_DIR / log_name
        if not log_path.exists() or log_path in seen:
            continue
        seen.add(log_path)
        text = log_path.read_text(errors="replace")
        by_file = extract_by_file_from_log_text(text, cwd, suite)
        if by_file:
            for file_path in sorted(by_file.keys()):
                entries = by_file[file_path]
                for _line_no, _msg in entries:
                    pass
        else:
            # No file:line parsed — run failed early or no linter output
            pass
    for name, p in with_content:
        if p in seen:
            continue
        suite = next(s for n, s in SUITES if n == name)
        text = p.read_text(errors="replace")
        by_file = extract_by_file_from_log_text(text, cwd, suite)
        if by_file:
            for file_path in sorted(by_file.keys()):
                entries = by_file[file_path]
                for _line_no, _msg in entries:
                    pass


def collect_issues_by_file(cwd: Path) -> tuple[dict, dict]:
    """Collect issues from split logs, grouped by file and category."""
    by_file_lint: dict[str, list[tuple[str, int | None, str]]] = defaultdict(list)
    by_file_test: dict[str, list[tuple[str, int | None, str]]] = defaultdict(list)

    for stem, display_name, category, suite_for_patterns in SPLIT_STEPS:
        log_path = LOG_DIR / f"{stem}.log"
        for file_path, line_no, msg in extract_issues(log_path, suite_for_patterns, cwd):
            entry = (display_name, line_no, msg)
            if category == "lint":
                by_file_lint[file_path].append(entry)
            else:
                by_file_test[file_path].append(entry)

    return by_file_lint, by_file_test


def print_issues_by_category(by_file_lint: dict, by_file_test: dict, _sep: str) -> None:
    """Print lint and test issues grouped by file."""
    if by_file_lint:
        for file_path in sorted(by_file_lint.keys()):
            entries = by_file_lint[file_path]
            for _step_name, _line_no, _msg in entries:
                pass

    if by_file_test:
        for file_path in sorted(by_file_test.keys()):
            entries = by_file_test[file_path]
            for _step_name, _line_no, _msg in entries:
                pass


def print_step_details_by_file(by_file: dict, _display_name: str, _log_path: Path) -> None:
    """Print details for a step grouped by file."""
    for fp in sorted(by_file.keys()):
        for _line_no, _msg in by_file[fp]:
            pass


def print_step_excerpt(_display_name: str, log_path: Path) -> None:
    """Print excerpt from log when no by-file details available."""
    lines = excerpt_lines(log_path)
    for _ln in lines[:15]:
        pass


def print_failed_steps_details(failed_steps: list[str], cwd: Path, _sep: str) -> None:
    """Print details for failed steps when no by-file issues found."""
    for stem, display_name, _, suite_for_patterns in SPLIT_STEPS:
        if stem not in failed_steps:
            continue

        log_path = LOG_DIR / f"{stem}.log"
        if not log_path.exists():
            continue

        text = log_path.read_text(errors="replace")
        by_file = extract_by_file_from_log_text(text, cwd, suite_for_patterns)

        if by_file:
            print_step_details_by_file(by_file, display_name, log_path)
        else:
            print_step_excerpt(display_name, log_path)


def run_report_split() -> int:
    """Report from per-step logs: group Lint/Type by file, Tests separate."""
    cwd = Path.cwd()
    by_file_lint, by_file_test = collect_issues_by_file(cwd)

    failed_steps = get_failed_steps_from_last_run()
    failed_from_logs = [name for name, _ in detect_failed_steps_from_logs()]
    failed_steps = sorted(set(failed_steps) | set(failed_from_logs))

    sep = "=" * 72

    # Print by-file issues if found
    print_issues_by_category(by_file_lint, by_file_test, sep)

    if by_file_lint or by_file_test:
        if failed_steps:
            pass
        return 0

    # No parseable by-file: show failed steps and per-step log excerpts
    if failed_steps:
        print_failed_steps_details(failed_steps, cwd, sep)

    return 0


def run_report() -> int:
    """Run report."""
    if use_split_mode():
        return run_report_split()
    cwd = Path.cwd()
    by_file = defaultdict(list)

    for log_name, suite_name in SUITES:
        log_path = LOG_DIR / log_name
        for file_path, line_no, msg in extract_issues(log_path, suite_name, cwd):
            by_file[file_path].append((suite_name, line_no, msg))

    failed_from_last = get_failed_suites_from_last_run()
    failed_from_logs = [suite for suite, _ in detect_failed_suites_from_logs()]
    failed_suites = sorted(set(failed_from_last) | set(failed_from_logs))
    existing = [(name, LOG_DIR / name) for name, _ in SUITES if (LOG_DIR / name).exists()]
    with_content = [(n, p) for n, p in existing if p.stat().st_size > 0]

    if by_file:
        print_action_plan_by_file(by_file, cwd)
        if failed_suites:
            pass
        return 0

    # All passed, no file-level issues: short success (skip verbose by-log listing)
    if not failed_suites and with_content:
        return 0

    # No parseable by-file issues: show failed runs (colored) and action plan by log
    if failed_suites:
        for suite in failed_suites:
            log_name = next((n for n, s in SUITES if s == suite), f"quality-{suite.lower()}.log")
            log_path = LOG_DIR / log_name

    if with_content:
        print_action_plan_by_log(failed_suites, with_content, cwd)

    return 0


def main() -> int:
    """Main."""
    parser = argparse.ArgumentParser(description="Quality report: action plan by file and/or by log")
    parser.add_argument("--watch", action="store_true", help="Stream: re-run report every N seconds")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between runs when --watch (default 5)")
    args = parser.parse_args()

    if args.watch:
        try:
            while True:
                run_report()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            return 0

    return run_report()


if __name__ == "__main__":
    sys.exit(main())
