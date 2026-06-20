#!/usr/bin/env python3
"""Unified terminal for rtm dev start --quick.

Runs backend-go, backend-py, and frontend in one terminal. Output is intercepted
in full phrases (blurbs), not line-by-line. Phrases from the same service are
debounced (within 1s) and bundled into one block. Uses ANSI coloring so colors
persist in any terminal; filters out phrases that are only HTTP 200 noise.
"""

import logging
import os
import re
import signal
import sys
import threading
import time
from pathlib import Path
from queue import Empty, Queue
from subprocess import PIPE, STDOUT, Popen

logger = logging.getLogger(__name__)

# Debounce: bundle phrases from the same tag if they arrive within this many seconds
DEBOUNCE_SEC = 1.0

# Tags for the three services (match rtm dev status names)
TAG_GO = "backend-go"
TAG_PY = "backend-py"
TAG_FRONTEND = "frontend"

# ANSI escape codes (our own system so colors persist everywhere)
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_RED = "\033[31m"
ANSI_BRIGHT_RED = "\033[1;31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BRIGHT_YELLOW = "\033[1;33m"
ANSI_MAGENTA = "\033[35m"
ANSI_CYAN = "\033[36m"
ANSI_BRIGHT_CYAN = "\033[1;36m"

# Tag colors (ANSI): backend-go=cyan, backend-py=green, frontend=magenta
TAG_ANSI = {
    TAG_GO: ANSI_BRIGHT_CYAN,
    TAG_PY: ANSI_GREEN,
    TAG_FRONTEND: ANSI_MAGENTA,
}
# Line-level colors: error=red, warn=yellow, info=dim cyan
ANSI_ERROR = ANSI_BRIGHT_RED
ANSI_WARN = ANSI_YELLOW
ANSI_INFO = ANSI_DIM + ANSI_CYAN

# Phrase boundary: new log entry often starts with date, level, or method (optional leading whitespace)
LOG_START_PATTERN = re.compile(
    r"^\s*(\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|INFO|ERROR|WARN|WARNING|DEBUG|GET\s|POST\s|PUT\s|DELETE\s|PATCH\s|\[\s*\]|File\s+)",
)
# Filter: skip phrase that is only HTTP 200 success
FILTER_200 = re.compile(r"^\s*(GET|POST|PUT|DELETE|PATCH)\s+.*\s+200\s*$", re.MULTILINE)
FILTER_200_INLINE = re.compile(r"\s200\s+OK\s*$|\s200\s*$")


def project_root() -> Path:
    """Project root."""
    return Path(__file__).resolve().parent.parent


def _is_only_200_noise(phrase: str) -> bool:
    """True if phrase is only HTTP 200 success lines (safe to hide)."""
    stripped = phrase.strip()
    if not stripped:
        return True
    # Single line that looks like "GET /path 200"
    if FILTER_200.match(stripped):
        return True
    # All lines are 200-like
    lines = [ln.strip() for ln in phrase.splitlines() if ln.strip()]
    if not lines:
        return True
    return all(FILTER_200_INLINE.search(ln) or FILTER_200.match(ln) for ln in lines)


def _is_new_log_start(line: str) -> bool:
    """True if this line looks like the start of a new log entry (so previous buffer should flush)."""
    return bool(LOG_START_PATTERN.match(line.strip()))


def _line_style_ansi(line: str) -> str:
    """Return ANSI prefix for this line (error=red, warn=yellow, info=dim cyan, 5xx/4xx=red, else empty)."""
    s = line.strip().upper()
    if not s:
        return ""
    if "ERROR" in s or "FATAL" in s or "EXCEPTION" in s:
        return ANSI_ERROR
    if "WARN" in s or "WARNING" in s:
        return ANSI_WARN
    if " 500 " in s or "500 INTERNAL" in s or "INTERNAL SERVER ERROR" in s:
        return ANSI_ERROR
    if " 401 " in s or " 403 " in s or " 404 " in s or "UNAUTHORIZED" in s or "FORBIDDEN" in s:
        return ANSI_WARN
    if "FAILED" in s or "FAIL" in s or "NOT AVAILABLE" in s:
        return ANSI_ERROR
    if "INFO" in s and not s.startswith("#"):
        return ANSI_INFO
    return ""


def _format_phrase_ansi(tag: str, phrase: str) -> str:
    """Format one phrase with our ANSI coloring: [tag] line + content with line-level colors."""
    tag_ansi = TAG_ANSI.get(tag, ANSI_RESET)
    out = ["\n", tag_ansi, "[", tag, "]", ANSI_RESET, "\n"]
    for line in phrase.rstrip().splitlines(keepends=True):
        prefix = _line_style_ansi(line)
        if prefix:
            out.extend((prefix, line.rstrip("\n"), ANSI_RESET, "\n"))
        else:
            out.append(line)
    out.append("\n")
    return "".join(out)


def _run_service(
    tag: str,
    cwd: Path,
    argv: list[str],
    env: dict[str, str],
    phrase_queue: Queue[tuple[str, str]],
    processes: list[Popen],
    max_lines_per_phrase: int = 80,
) -> None:
    """Run one process; buffer stdout/stderr into phrases; push (tag, phrase) to queue."""
    try:
        p = Popen(
            argv,
            cwd=cwd,
            env=env,
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            bufsize=1,
        )
        processes.append(p)
    except Exception as e:
        phrase_queue.put((tag, f"[process failed to start: {e}]\n"))
        return

    buf: list[str] = []

    def flush() -> None:
        if buf:
            phrase = "".join(buf)
            buf.clear()
            if phrase.strip() and not _is_only_200_noise(phrase):
                phrase_queue.put((tag, phrase))

    try:
        for line in iter(p.stdout.readline, ""):
            if not line.strip():
                # Blank line: end of phrase, don't add to buffer
                if buf:
                    flush()
                continue
            if _is_new_log_start(line) and buf:
                flush()
            buf.append(line)
            if len(buf) >= max_lines_per_phrase:
                flush()
        flush()
    except (BrokenPipeError, OSError):
        pass
    finally:
        try:
            p.wait(timeout=1)
        except Exception:
            p.kill()


def _printer(phrase_queue: Queue[tuple[str, str]], stop: threading.Event) -> None:
    """Consume (tag, phrase); debounce per-tag (bundle phrases within DEBOUNCE_SEC), then print with ANSI."""
    buffer: dict[str, list[str]] = {}  # tag -> list of phrases to bundle
    flush_due: dict[str, float] = {}  # tag -> monotonic time when to flush

    def flush_tag(tag: str) -> None:
        if tag not in buffer or not buffer[tag]:
            return
        bundled = "\n".join(buffer[tag])
        buffer[tag] = []
        flush_due.pop(tag, None)
        s = _format_phrase_ansi(tag, bundled)
        sys.stdout.write(s)
        sys.stdout.flush()

    def flush_all_due(now: float) -> None:
        for tag in list(flush_due.keys()):
            if flush_due[tag] <= now:
                flush_tag(tag)

    while not stop.is_set():
        now = time.monotonic()
        flush_all_due(now)
        # Wait until next phrase or until next flush is due
        next_due = min(flush_due.values()) if flush_due else None
        timeout = 0.25
        if next_due is not None:
            timeout = min(0.25, max(0.0, next_due - now))
        try:
            tag, phrase = phrase_queue.get(timeout=timeout)
        except Empty:
            continue
        if not phrase.strip():
            continue
        buffer.setdefault(tag, []).append(phrase.strip())
        flush_due[tag] = now + DEBOUNCE_SEC

    # Flush all buffered (no wait)
    for tag in list(buffer.keys()):
        flush_tag(tag)
    # Drain queue and flush immediately (no more debounce)
    while True:
        try:
            tag, phrase = phrase_queue.get_nowait()
            if not phrase.strip():
                continue
            s = _format_phrase_ansi(tag, phrase)
            sys.stdout.write(s)
            sys.stdout.flush()
        except Empty:
            break


def main() -> int:
    """Main."""
    root = project_root()
    env = os.environ.copy()
    path_add = os.pathsep.join(["/opt/homebrew/bin", "/usr/local/bin"])
    env["PATH"] = path_add + os.pathsep + env.get("PATH", "")
    env.setdefault("PYTHONWARNINGS", "ignore:remove second argument of ws_handler:DeprecationWarning")

    phrase_queue: Queue[tuple[str, str]] = Queue()
    stop = threading.Event()
    threads: list[threading.Thread] = []
    processes: list[Popen] = []

    # Start printer (ANSI coloring; thread-safe)
    printer_thread = threading.Thread(
        target=_printer,
        args=(phrase_queue, stop),
        daemon=True,
    )
    printer_thread.start()

    def run_go() -> None:
        _run_service(TAG_GO, root / "backend", ["air", "-c", ".air.toml"], env, phrase_queue, processes)

    def run_py() -> None:
        _run_service(
            TAG_PY,
            root,
            [
                str(root / ".venv" / "bin" / "python"),
                "-m",
                "uvicorn",
                "src.tracertm.api.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload-exclude",
                "ARCHIVE",
                "--reload-exclude",
                "CONFIG",
            ],
            env,
            phrase_queue,
            processes,
        )

    def run_frontend() -> None:
        _run_service(
            TAG_FRONTEND,
            root / "frontend" / "apps" / "web",
            ["bun", "run", "dev", "--host", "0.0.0.0"],
            env,
            phrase_queue,
            processes,
        )

    # Strict deps order: go -> py -> frontend so preflights pass
    t_go = threading.Thread(target=run_go, daemon=True)
    t_go.start()
    threads.append(t_go)
    time.sleep(2)
    t_py = threading.Thread(target=run_py, daemon=True)
    t_py.start()
    threads.append(t_py)
    time.sleep(2)
    t_fe = threading.Thread(target=run_frontend, daemon=True)
    t_fe.start()
    threads.append(t_fe)

    def on_sig(_signum: int, _frame: object) -> None:
        stop.set()
        for p in processes:
            try:
                p.terminate()
            except Exception as e:
                logger.debug("Terminate: %s", e)
        sys.exit(0)

    signal.signal(signal.SIGINT, on_sig)
    signal.signal(signal.SIGTERM, on_sig)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        for p in processes:
            try:
                p.terminate()
                p.wait(timeout=2)
            except Exception as e:
                logger.debug("Terminate/wait: %s", e)
        printer_thread.join(timeout=1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
