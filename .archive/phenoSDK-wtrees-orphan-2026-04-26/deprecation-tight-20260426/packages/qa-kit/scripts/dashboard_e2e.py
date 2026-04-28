#!/usr/bin/env python3
"""End-to-end test for the QA Dashboard using Playwright (Chromium).

What it does:
- Creates a temp QA DB
- Ingests a minimal JUnit XML run
- Starts the QA dashboard server on a free port
- Uses Playwright to load the UI and verify core elements render

Requirements:
- Python packages: fastapi, uvicorn, playwright (the script installs playwright browsers if needed)
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def ensure_playwright() -> None:
    try:
        import playwright  # noqa: F401
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    # Ensure browsers installed
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"], stdout=subprocess.DEVNULL)
    except Exception:
        # Retry without quiet in case of issues
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])


def wait_for_ready(url: str, timeout: float = 20.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.ok:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Service not ready: {url}")


@contextmanager
def qa_server(db_path: Path, port: int = 8899):
    env = os.environ.copy()
    env["QA_DB_PATH"] = str(db_path)
    cmd = [sys.executable, str(REPO / "dashboard" / "qa_dashboard.py"), "--host", "127.0.0.1", "--port", str(port)]
    proc = subprocess.Popen(cmd, cwd=str(REPO), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        wait_for_ready(f"http://127.0.0.1:{port}/api/qa/projects", timeout=30)
        yield proc
    finally:
        with contextlib.suppress(Exception):
            proc.terminate()
            proc.wait(timeout=5)


def ingest_minimal(db_path: Path, project: str) -> None:
    junit_content = """
    <testsuite name="e2e" tests="1" failures="0" errors="0" skipped="0" time="0.01">
      <testcase classname="e2e.sample" name="test_ok" time="0.01"/>
    </testsuite>
    """.strip()
    with tempfile.TemporaryDirectory() as td:
        junit_file = Path(td) / "e2e.xml"
        junit_file.write_text(junit_content)
        subprocess.check_call(
            [
                sys.executable,
                str(REPO / "scripts" / "qa_ingest.py"),
                "--project",
                project,
                "--framework",
                "pytest",
                "--input",
                str(junit_file),
                "--format",
                "junit",
                "--commit",
                "E2E",
                "--branch",
                "local",
                "--ci",
                "local",
                "--db",
                str(db_path),
            ]
        )


def run_playwright(url: str, project: str) -> None:
    from playwright.sync_api import sync_playwright
from src.shared.logging import get_logger

logger = get_logger(__name__)



    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda msg: logger.info(f"[browser] {msg.type.upper()}: {msg.text}"))
        page.on("pageerror", lambda exc: logger.info(f"[browser-error] {exc}"))
        page.goto(url, wait_until="networkidle")
        # Wait for project selector
        page.wait_for_selector("#projectSelect")
        # Ensure at least one option present
        opts = page.eval_on_selector_all("#projectSelect option", "els => els.map(e => e.value)")
        assert project in opts, f"Expected project option not found; options: {opts}"
        # Select project (in case not auto-selected)
        page.select_option("#projectSelect", project)
        # Wait for Summary card to render values
        try:
            page.wait_for_selector("#summary .pill", timeout=45000)
        except Exception:
            html = page.content()
            print("[debug] page content snippet:", html[:1200])
            raise
        # Basic sanity checks on panels
        assert page.locator("text=Summary (14d)").count() == 1
        assert page.locator("text=Recent Runs").count() == 1
        assert page.locator("text=Top Failures").count() == 1
        # Confirm pass rate text present
        assert page.locator("#summary").inner_text().lower().find("avg pass") != -1
        browser.close()


def main() -> int:
    ensure_playwright()
    project = "e2e-qa"
    db_path = REPO / "dashboard" / "qa_data" / "e2e_qa.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    ingest_minimal(db_path, project)
    try:
        with qa_server(db_path, port=8899) as proc:
            run_playwright("http://127.0.0.1:8899/", project)
    except Exception:
        try:
            if proc and proc.stdout:
                out = proc.stdout.read()
                print("[server logs]", out[-2000:] if out else "<no output>")
        except Exception:
            pass
        raise
    logger.info("QA Dashboard E2E: SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
