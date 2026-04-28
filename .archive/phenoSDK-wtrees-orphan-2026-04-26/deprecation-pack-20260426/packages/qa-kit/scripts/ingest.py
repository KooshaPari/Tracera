#!/usr/bin/env python3
"""QA Results Ingestion CLI.

Ingest test results from multiple frameworks (pytest via JUnit XML,
Next.js/Jest/Vitest via JUnit XML or JSON) into a local SQLite database
for powering the QA dashboard.

Usage examples:

  - Pytest (JUnit XML):
      pytest --junitxml=reports/pytest-junit.xml
      scripts/qa_ingest.py \
        --project zen-mcp-server --framework pytest \
        --input reports/pytest-junit.xml --format junit \
        --commit $GIT_COMMIT --branch $GIT_BRANCH --ci github \
        --coverage-json ./.coverage/coverage-summary.json

  - Jest (JUnit):
      jest --reporters=default --reporters=jest-junit
      scripts/qa_ingest.py \
        --project frontend-app --framework jest \
        --input reports/junit.xml --format junit \
        --commit $GIT_COMMIT --branch $GIT_BRANCH --ci github

  - Vitest (JUnit):
      vitest --reporter=junit --outputFile=reports/vitest-junit.xml
      scripts/qa_ingest.py \
        --project frontend-admin --framework vitest \
        --input reports/vitest-junit.xml --format junit

  - Jest (JSON):
      jest --json --outputFile=reports/jest.json
      scripts/qa_ingest.py \
        --project frontend-app --framework jest \
        --input reports/jest.json --format jest-json

The database is created at qa_data/qa.db (or specify with --db)
"""

import argparse
import json
import os
import sqlite3
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

DEFAULT_DB_DIR = Path("qa_data")
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "qa.db"


def ensure_db(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """,
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            framework TEXT NOT NULL,
            commit_sha TEXT,
            branch TEXT,
            ci_provider TEXT,
            triggered_by TEXT,
            created_at TEXT NOT NULL,
            started_at TEXT,
            duration_ms INTEGER,
            total INTEGER,
            passed INTEGER,
            failed INTEGER,
            skipped INTEGER,
            errors INTEGER,
            coverage_lines REAL,
            coverage_branches REAL,
            meta_json TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );
        """,
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            file TEXT,
            suite TEXT,
            name TEXT,
            status TEXT,
            duration_ms INTEGER,
            error_message TEXT,
            retry_count INTEGER,
            extra_json TEXT,
            FOREIGN KEY(run_id) REFERENCES runs(id)
        );
        """,
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_runs_project_created ON runs(project_id, created_at);",
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cases_run_status ON test_cases(run_id, status);")
    conn.commit()


def upsert_project(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO projects(name) VALUES(?)", (name,))
    cur.execute("SELECT id FROM projects WHERE name=?", (name,))
    row = cur.fetchone()
    assert row, "Failed to upsert project"
    return int(row[0])


@dataclass
class RunSummary:
    total: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration_ms: int | None
    started_at: str | None


def insert_run(
    conn: sqlite3.Connection,
    project_id: int,
    framework: str,
    summary: RunSummary,
    commit_sha: str | None,
    branch: str | None,
    ci_provider: str | None,
    triggered_by: str | None,
    coverage_lines: float | None,
    coverage_branches: float | None,
    meta: dict[str, Any],
) -> int:
    cur = conn.cursor()
    created_at = datetime.now(UTC).isoformat()
    cur.execute(
        """
        INSERT INTO runs(
            project_id, framework, commit_sha, branch, ci_provider, triggered_by,
            created_at, started_at, duration_ms, total, passed, failed, skipped, errors,
            coverage_lines, coverage_branches, meta_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            framework,
            commit_sha,
            branch,
            ci_provider,
            triggered_by,
            created_at,
            summary.started_at,
            summary.duration_ms,
            summary.total,
            summary.passed,
            summary.failed,
            summary.skipped,
            summary.errors,
            coverage_lines,
            coverage_branches,
            json.dumps(meta) if meta else None,
        ),
    )
    run_id = cur.lastrowid
    conn.commit()
    return int(run_id)


def insert_cases(conn: sqlite3.Connection, run_id: int, cases: Iterable[dict[str, Any]]) -> None:
    cur = conn.cursor()
    rows = [
        (
            run_id,
            c.get("file"),
            c.get("suite"),
            c.get("name"),
            c.get("status"),
            c.get("duration_ms"),
            c.get("error_message"),
            c.get("retry_count"),
            json.dumps(c.get("extra")) if c.get("extra") else None,
        )
        for c in cases
    ]
    cur.executemany(
        """
        INSERT INTO test_cases(run_id, file, suite, name, status, duration_ms, error_message, retry_count, extra_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def parse_junit(path: Path) -> tuple[RunSummary, list[dict[str, Any]]]:
    tree = ET.parse(path)
    root = tree.getroot()
    total = passed = failed = skipped = errors = 0
    duration_ms = 0
    started_at: str | None = None
    cases: list[dict[str, Any]] = []

    # JUnit can be <testsuites> or <testsuite>
    suites = []
    if root.tag.endswith("testsuites"):
        suites = root.findall(".//testsuite")
    elif root.tag.endswith("testsuite"):
        suites = [root]
    else:
        raise ValueError(f"Unsupported JUnit root tag: {root.tag}")

    for suite in suites:
        # Attributes vary; be defensive
        t = int(suite.attrib.get("tests", 0) or 0)
        f = int(suite.attrib.get("failures", 0) or 0)
        e = int(suite.attrib.get("errors", 0) or 0)
        s = int(suite.attrib.get("skipped", suite.attrib.get("disabled", 0)) or 0)
        time_s = float(suite.attrib.get("time", 0.0) or 0.0)
        total += t
        failed += f
        errors += e
        skipped += s
        # Duration may be per suite; sum them
        duration_ms += int(time_s * 1000)

        for case in suite.findall("testcase"):
            name = case.attrib.get("name")
            classname = case.attrib.get("classname")
            file = case.attrib.get("file") or (classname.replace(".", "/") if classname else None)
            time_case = float(case.attrib.get("time", 0.0) or 0.0)
            status = "passed"
            err_msg = None
            if case.find("failure") is not None:
                status = "failed"
                failure = case.find("failure")
                if failure is not None:
                    err_msg = (failure.attrib.get("message") or failure.text or "").strip()[:4096]
            elif case.find("error") is not None:
                status = "error"
                error_el = case.find("error")
                if error_el is not None:
                    err_msg = (error_el.attrib.get("message") or error_el.text or "").strip()[:4096]
            elif case.find("skipped") is not None:
                status = "skipped"

            cases.append(
                {
                    "file": file,
                    "suite": classname,
                    "name": name,
                    "status": status,
                    "duration_ms": int(time_case * 1000),
                    "error_message": err_msg,
                    "retry_count": None,
                    "extra": None,
                },
            )

    # Some JUnit emitters set totals at the <testsuites> level; if our total is 0, compute from cases
    if total == 0 and cases:
        total = len(cases)
        passed = sum(1 for c in cases if c["status"] == "passed")
        failed = sum(1 for c in cases if c["status"] == "failed")
        skipped = sum(1 for c in cases if c["status"] == "skipped")
        errors = sum(1 for c in cases if c["status"] == "error")

    summary = RunSummary(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        duration_ms=duration_ms or None,
        started_at=started_at,
    )
    return summary, cases


def parse_jest_json(path: Path) -> tuple[RunSummary, list[dict[str, Any]]]:
    data = json.loads(path.read_text())
    # Jest JSON format can vary; handle common fields
    total = int(data.get("numTotalTests") or data.get("numTotalTestSuites") or 0)
    passed = int(data.get("numPassedTests") or 0)
    failed = int(data.get("numFailedTests") or 0)
    skipped = int(data.get("numPendingTests") or 0)
    errors = int(data.get("numRuntimeErrorTestSuites") or 0)
    start_time = data.get("startTime")
    duration_ms = int(data.get("testResultsProcessor", 0) or data.get("duration", 0) or 0)

    if not duration_ms and start_time and data.get("success") is not None:
        # Fall back to per-suite durations
        duration_ms = sum(
            int(tr.get("perfStats", {}).get("runtime", 0) or 0)
            for tr in data.get("testResults", [])
        )

    cases: list[dict[str, Any]] = []
    for tr in data.get("testResults", []):
        file_path = tr.get("name") or tr.get("testFilePath")
        for ar in tr.get("assertionResults", []):
            status = ar.get("status")
            mapped = {
                "passed": "passed",
                "failed": "failed",
                "pending": "skipped",
                "todo": "skipped",
                "skipped": "skipped",
            }.get(status, status or "unknown")
            title = ar.get("title")
            full_name = ar.get("fullName") or title
            duration = ar.get("duration")
            # Jest stores failure messages under "failureMessages"
            failure_messages = ar.get("failureMessages") or []
            err_msg = None
            if failure_messages:
                err_msg = "\n".join(failure_messages)
                if len(err_msg) > 4096:
                    err_msg = err_msg[:4096]
            cases.append(
                {
                    "file": file_path,
                    "suite": tr.get("testResults"),
                    "name": full_name,
                    "status": mapped,
                    "duration_ms": int(duration) if duration else None,
                    "error_message": err_msg,
                    "retry_count": None,
                    "extra": {"ancestorTitles": ar.get("ancestorTitles")},
                },
            )

    if total == 0 and cases:
        total = len(cases)
        passed = sum(1 for c in cases if c["status"] == "passed")
        failed = sum(1 for c in cases if c["status"] == "failed")
        skipped = sum(1 for c in cases if c["status"] == "skipped")

    summary = RunSummary(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        duration_ms=duration_ms or None,
        started_at=(
            datetime.fromtimestamp(start_time / 1000, tz=UTC).isoformat()
            if isinstance(start_time, int | float)
            else None
        ),
    )
    return summary, cases


def parse_vitest_json(path: Path) -> tuple[RunSummary, list[dict[str, Any]]]:
    # Vitest JSON reporters vary; support a common structure
    data = json.loads(path.read_text())
    stats = data.get("stats") or {}
    total = int(stats.get("tests") or 0)
    passed = int(stats.get("passes") or 0)
    failed = int(stats.get("failures") or 0)
    skipped = int(stats.get("pending") or stats.get("skips") or 0)
    errors = 0
    duration_ms = int(stats.get("duration") or 0)
    started_at = None
    cases: list[dict[str, Any]] = []

    for t in data.get("tests") or []:
        name = t.get("name") or t.get("fullName")
        status = t.get("state") or t.get("status")
        mapped = {
            "pass": "passed",
            "passed": "passed",
            "fail": "failed",
            "failed": "failed",
            "skip": "skipped",
            "skipped": "skipped",
            "todo": "skipped",
        }.get(status, status)
        err_msg = None
        if t.get("err"):
            em = t["err"].get("message") or t["err"].get("stack")
            if em:
                err_msg = em[:4096]
        cases.append(
            {
                "file": t.get("file") or t.get("filepath"),
                "suite": t.get("suite"),
                "name": name,
                "status": mapped,
                "duration_ms": int(t.get("duration") or 0),
                "error_message": err_msg,
                "retry_count": t.get("retryCount"),
                "extra": None,
            },
        )

    if total == 0 and cases:
        total = len(cases)
        passed = sum(1 for c in cases if c["status"] == "passed")
        failed = sum(1 for c in cases if c["status"] == "failed")
        skipped = sum(1 for c in cases if c["status"] == "skipped")

    summary = RunSummary(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        duration_ms=duration_ms or None,
        started_at=started_at,
    )
    return summary, cases


def maybe_parse_coverage_json(path: Path | None) -> tuple[float | None, float | None]:
    if not path or not path.exists():
        return None, None
    try:
        data = json.loads(path.read_text())
        # Try Jest coverage-summary.json shape
        total = data.get("total") or {}
        lines_pct = total.get("lines", {}).get("pct")
        branches_pct = total.get("branches", {}).get("pct")
        if lines_pct is not None or branches_pct is not None:
            return (
                float(lines_pct) if lines_pct is not None else None,
                float(branches_pct) if branches_pct is not None else None,
            )
        # Try coverage.py JSON summary-like shapes
        if isinstance(data, dict) and "totals" in data:
            t = data["totals"]
            lines_pct = t.get("percent_covered") or t.get("covered_percent")
            return (float(lines_pct) if lines_pct is not None else None, None)
    except Exception:
        return None, None
    return None, None


def maybe_parse_coverage_xml(path: Path | None) -> tuple[float | None, float | None]:
    """Parse coverage.py Cobertura XML for line/branch coverage.

    Returns (lines_pct, branches_pct) as floats 0-100 when available.
    """
    if not path or not path.exists():
        return None, None
    try:
        root = ET.parse(path).getroot()
        if root.tag.endswith("coverage"):
            line_rate = root.attrib.get("line-rate")
            branch_rate = root.attrib.get("branch-rate")
            lines_pct = float(line_rate) * 100 if line_rate is not None else None
            branches_pct = float(branch_rate) * 100 if branch_rate is not None else None
            if (
                lines_pct is None
                and root.attrib.get("lines-valid")
                and root.attrib.get("lines-covered")
            ):
                lv = float(root.attrib.get("lines-valid"))
                lc = float(root.attrib.get("lines-covered"))
                lines_pct = (lc / lv * 100) if lv else None
            return lines_pct, branches_pct
    except Exception:
        return None, None
    return None, None


def detect_format(path: Path) -> str:
    if path.suffix.lower() in {".xml"}:
        # Attempt to verify if it's JUnit
        try:
            root = ET.parse(path).getroot()
            if root.tag.endswith("testsuite") or root.tag.endswith("testsuites"):
                return "junit"
        except Exception:
            pass
        return "xml"
    if path.suffix.lower() in {".json"}:
        # Best effort: detect jest/vitest/playwright/lhci
        try:
            data = json.loads(path.read_text())
            if "numTotalTests" in data or "testResults" in data:
                return "jest-json"
            if "stats" in data or "tests" in data:
                return "vitest-json"
            if "suites" in data or ("config" in data and "version" in data):
                return "playwright-json"
            if "lighthouseVersion" in data or ("categories" in data and "audits" in data):
                return "lhci-json"
        except Exception:
            pass
        return "json"
    return "unknown"


def parse_playwright_json(path: Path) -> tuple[RunSummary, list[dict[str, Any]]]:
    data = json.loads(path.read_text())
    cases: list[dict[str, Any]] = []

    def walk(node: Any):
        if isinstance(node, dict):
            if node.get("title") and (node.get("outcome") or node.get("status")):
                outcome = node.get("outcome") or node.get("status")
                status = {
                    "expected": "passed",
                    "skipped": "skipped",
                    "unexpected": "failed",
                    "flaky": "failed",
                    "passed": "passed",
                    "failed": "failed",
                }.get(outcome, outcome or "unknown")
                loc = node.get("location") or {}
                file_path = loc.get("file") if isinstance(loc, dict) else None
                duration = node.get("duration") or node.get("durationMs")
                cases.append(
                    {
                        "file": file_path,
                        "suite": None,
                        "name": node.get("title"),
                        "status": status,
                        "duration_ms": int(duration) if duration else None,
                        "error_message": None,
                        "retry_count": None,
                        "extra": None,
                    },
                )
            for k, v in node.items():
                if k in ("suites", "specs", "tests", "entries", "children") and isinstance(v, list):
                    for it in v:
                        walk(it)
        elif isinstance(node, list):
            for it in node:
                walk(it)

    walk(data)
    total = len(cases)
    passed = sum(1 for c in cases if c["status"] == "passed")
    failed = sum(1 for c in cases if c["status"] == "failed")
    skipped = sum(1 for c in cases if c["status"] == "skipped")
    summary = RunSummary(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=0,
        duration_ms=None,
        started_at=None,
    )
    return summary, cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest test results into QA dashboard DB")
    parser.add_argument(
        "--project", required=True, help="Project name (e.g., zen-mcp-server, frontend-web)",
    )
    parser.add_argument("--db", dest="db_path", help="Override DB path (default: qa_data/qa.db)")
    parser.add_argument("--framework", required=True, help="Framework (pytest|jest|vitest|other)")
    parser.add_argument(
        "--input", required=True, nargs="+", help="Input file(s): JUnit XML or JSON",
    )
    parser.add_argument(
        "--format",
        default="auto",
        help="Input format: auto|junit|jest-json|vitest-json|playwright-json|lhci-json",
    )
    parser.add_argument("--commit", help="Commit SHA")
    parser.add_argument("--branch", help="Branch name")
    parser.add_argument(
        "--ci", dest="ci_provider", help="CI provider (github|gitlab|jenkins|local)",
    )
    parser.add_argument("--triggered-by", help="Triggered by (user, schedule)")
    parser.add_argument(
        "--coverage-json", type=str, help="Path to coverage summary JSON (optional)",
    )
    parser.add_argument(
        "--coverage-xml", type=str, help="Path to coverage XML (Cobertura) (optional)",
    )
    parser.add_argument(
        "--meta", type=str, help='Additional metadata JSON string (e.g., "{"node":"20.x"}")',
    )

    args = parser.parse_args(argv)
    inputs: list[Path] = [Path(p) for p in args.input]
    for p in inputs:
        if not p.exists():
            print(f"ERROR: input not found: {p}", file=sys.stderr)
            return 2

    cov_lines, cov_branches = maybe_parse_coverage_json(
        Path(args.coverage_json) if args.coverage_json else None,
    )
    if cov_lines is None and args.coverage_xml:
        xml_lines, xml_branches = maybe_parse_coverage_xml(Path(args.coverage_xml))
        cov_lines = cov_lines if cov_lines is not None else xml_lines
        cov_branches = cov_branches if cov_branches is not None else xml_branches
    meta: dict[str, Any] = {}
    if args.meta:
        try:
            meta = json.loads(args.meta)
        except json.JSONDecodeError as e:
            print(f"WARNING: --meta is not valid JSON: {e}", file=sys.stderr)

    db_path = (
        Path(args.db_path)
        if args.db_path
        else (Path(os.environ.get("QA_DB_PATH")) if os.environ.get("QA_DB_PATH") else None)
    )
    conn = ensure_db(db_path=db_path)
    # Apply QA_PROJECT_ALIASES mapping at ingestion time to canonicalize project name
    canonical_project = args.project
    try:
        aliases = json.loads(os.environ.get("QA_PROJECT_ALIASES", "{}"))
        if canonical_project in aliases:
            canonical_project = aliases[canonical_project]
    except Exception:
        pass
    project_id = upsert_project(conn, canonical_project)

    all_cases: list[dict[str, Any]] = []
    agg_total = agg_passed = agg_failed = agg_skipped = agg_errors = 0
    agg_duration_ms: int = 0
    run_started_at: str | None = None

    for input_path in inputs:
        fmt = args.format
        if fmt == "auto":
            fmt = detect_format(input_path)
        if fmt == "junit":
            summary, cases = parse_junit(input_path)
        elif fmt == "jest-json":
            summary, cases = parse_jest_json(input_path)
        elif fmt == "vitest-json":
            summary, cases = parse_vitest_json(input_path)
        elif fmt == "playwright-json":
            summary, cases = parse_playwright_json(input_path)
        elif fmt == "lhci-json":
            # LHCI handled by a separate ingestion tool; skip here
            continue
        else:
            print(f"ERROR: unsupported or unknown format for {input_path}: {fmt}", file=sys.stderr)
            return 3

        all_cases.extend(cases)
        agg_total += summary.total
        agg_passed += summary.passed
        agg_failed += summary.failed
        agg_skipped += summary.skipped
        agg_errors += summary.errors
        if summary.duration_ms:
            agg_duration_ms += summary.duration_ms
        if summary.started_at and not run_started_at:
            run_started_at = summary.started_at

    run_summary = RunSummary(
        total=agg_total or len(all_cases),
        passed=agg_passed or sum(1 for c in all_cases if c["status"] == "passed"),
        failed=agg_failed or sum(1 for c in all_cases if c["status"] == "failed"),
        skipped=agg_skipped or sum(1 for c in all_cases if c["status"] == "skipped"),
        errors=agg_errors,
        duration_ms=agg_duration_ms or None,
        started_at=run_started_at,
    )

    run_id = insert_run(
        conn,
        project_id=project_id,
        framework=args.framework,
        summary=run_summary,
        commit_sha=args.commit,
        branch=args.branch,
        ci_provider=args.ci_provider,
        triggered_by=args.triggered_by,
        coverage_lines=cov_lines,
        coverage_branches=cov_branches,
        meta=meta,
    )
    insert_cases(conn, run_id, all_cases)

    print(
        json.dumps(
            {
                "status": "ok",
                "run_id": run_id,
                "project": canonical_project,
                "framework": args.framework,
                "totals": {
                    "total": run_summary.total,
                    "passed": run_summary.passed,
                    "failed": run_summary.failed,
                    "skipped": run_summary.skipped,
                    "errors": run_summary.errors,
                },
                "coverage": {"lines": cov_lines, "branches": cov_branches},
            },
            indent=2,
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
