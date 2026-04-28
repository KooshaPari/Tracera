# Dev Port Clearing for rtm dev start Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ensure `rtm dev start` clears occupied ports for go-backend, python-backend, frontend (5173), docs (3001), and storybook (6006) before each service starts, while all other services keep existing “hold if already running” behavior.

**Architecture:** Add an optional per-service port-clear pre-hook inside `scripts/shell/with-lifecycle.sh`, driven by environment variables defined per service in `config/process-compose.yaml`. Only services that opt-in will clear ports; all others remain unchanged.

**Tech Stack:** Bash (process-compose wrapper), YAML config, pytest for CLI-focused integration test.

---

## Phased WBS + DAG

### Phase 1 — Discovery / Constraints
- **T1**: Confirm target services, ports, and config location (done by plan author).

### Phase 2 — Test Design (TDD)
- **T2**: Add failing test that proves `with-lifecycle.sh` clears a listening port when configured.
- **T3**: Run the test and verify it fails before implementation.

### Phase 3 — Build
- **T4**: Implement optional port-clearing logic in `scripts/shell/with-lifecycle.sh`.
- **T5**: Configure per-service port-clear env in `config/process-compose.yaml` for go-backend, python-backend, frontend, docs, storybook.

### Phase 4 — Verification
- **T6**: Run the new test and confirm it passes.
- **T7**: Manual smoke: start `rtm dev start`, verify ports clear and services come up without “address already in use”.

**DAG (Dependencies):**
- T2 → T3 → T4 → T5 → T6 → T7

---

### Task 2: Add failing test for port clearing

**Files:**
- Create: `tests/cli/test_dev_port_clear.py`

**Step 1: Write the failing test**

```python
import os
import shutil
import socket
import subprocess
import sys
import time

import pytest


def _wait_for_port(port: int, timeout: float = 2.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.05)
    return False


def test_with_lifecycle_clears_listening_port():
    if os.name == "nt":
        pytest.skip("with-lifecycle.sh is POSIX-only")
    if shutil.which("lsof") is None:
        pytest.skip("lsof not available")

    # Find a free port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        assert _wait_for_port(port), "server did not start"

        env = os.environ.copy()
        env["PORT_CLEAR_MODE"] = "kill"
        env["PORT_CLEAR_PORTS"] = str(port)

        result = subprocess.run(
            ["bash", "scripts/shell/with-lifecycle.sh", "test-service", "true"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0
        assert not _wait_for_port(port, timeout=1.0), "port still listening"
        assert server.poll() is not None, "server process still alive"
    finally:
        server.terminate()
        try:
            server.wait(timeout=2)
        except Exception:
            server.kill()
```

**Step 2: Run test to verify it fails**

Run:
```
pytest tests/cli/test_dev_port_clear.py::test_with_lifecycle_clears_listening_port -v
```
Expected: FAIL (port still listening / server still alive)

**Step 3: Commit**

SKIP — user requested no git actions.

---

### Task 4: Implement optional port-clearing in with-lifecycle wrapper

**Files:**
- Modify: `scripts/shell/with-lifecycle.sh`

**Step 1: Write minimal implementation**

Add after `SERVICE_NAME` assignment and before the `echo "[LIFECYCLE] START ..."` line:

```bash
PORT_CLEAR_MODE="${PORT_CLEAR_MODE:-}"
PORT_CLEAR_PORTS="${PORT_CLEAR_PORTS:-}"

if [[ -n "$PORT_CLEAR_MODE" ]]; then
  if [[ "$PORT_CLEAR_MODE" != "kill" ]]; then
    echo "[LIFECYCLE] PORT-CLEAR error: unsupported PORT_CLEAR_MODE='$PORT_CLEAR_MODE' for $SERVICE_NAME" >&2
    exit 1
  fi
  if [[ -z "$PORT_CLEAR_PORTS" ]]; then
    echo "[LIFECYCLE] PORT-CLEAR error: PORT_CLEAR_PORTS is required for $SERVICE_NAME" >&2
    exit 1
  fi
  if ! command -v lsof >/dev/null 2>&1; then
    echo "[LIFECYCLE] PORT-CLEAR error: lsof not found (required) for $SERVICE_NAME" >&2
    exit 1
  fi

  IFS=',' read -ra _ports <<< "$PORT_CLEAR_PORTS"
  for _port in "${_ports[@]}"; do
    _port="${_port//[[:space:]]/}"
    if ! [[ "$_port" =~ ^[0-9]+$ ]]; then
      echo "[LIFECYCLE] PORT-CLEAR error: invalid port '$_port' for $SERVICE_NAME" >&2
      exit 1
    fi

    _pids=$(lsof -Pi :"$_port" -sTCP:LISTEN -t 2>/dev/null || true)
    if [[ -n "$_pids" ]]; then
      echo "[LIFECYCLE] PORT-CLEAR $SERVICE_NAME port=$_port pids=$_pids"
      kill -TERM $_pids 2>/dev/null || true
      sleep 0.3
      _still=$(lsof -Pi :"$_port" -sTCP:LISTEN -t 2>/dev/null || true)
      if [[ -n "$_still" ]]; then
        kill -KILL $_still 2>/dev/null || true
        sleep 0.2
      fi
      _still=$(lsof -Pi :"$_port" -sTCP:LISTEN -t 2>/dev/null || true)
      if [[ -n "$_still" ]]; then
        echo "[LIFECYCLE] PORT-CLEAR error: port $_port still in use for $SERVICE_NAME (pids=$_still)" >&2
        exit 1
      fi
    fi
  done
fi
```

**Step 2: Commit**

SKIP — user requested no git actions.

---

### Task 5: Configure per-service port clearing in process-compose.yaml

**Files:**
- Modify: `config/process-compose.yaml`

**Step 1: Update environment blocks**

Add the following to each service’s `environment:` list:

- `go-backend` (port 8080)
  - `PORT_CLEAR_MODE=kill`
  - `PORT_CLEAR_PORTS=8080`

- `python-backend` (port 8000)
  - `PORT_CLEAR_MODE=kill`
  - `PORT_CLEAR_PORTS=8000`

- `frontend` (Vite, port 5173)
  - `PORT_CLEAR_MODE=kill`
  - `PORT_CLEAR_PORTS=5173`

- `docs` (Next.js docs, port 3001)
  - `PORT_CLEAR_MODE=kill`
  - `PORT_CLEAR_PORTS=3001`

- `storybook` (port 6006)
  - `PORT_CLEAR_MODE=kill`
  - `PORT_CLEAR_PORTS=6006`

**Step 2: Commit**

SKIP — user requested no git actions.

---

### Task 6: Verify

**Files:**
- Test: `tests/cli/test_dev_port_clear.py`

**Step 1: Run targeted test**

Run:
```
pytest tests/cli/test_dev_port_clear.py::test_with_lifecycle_clears_listening_port -v
```
Expected: PASS

**Step 2: Manual smoke (optional if you’re not running services now)**

Run:
```
rtm dev start
```
Expected: If a previous instance is bound to 5173/8000/8080/3001/6006, the wrapper logs a PORT-CLEAR line and starts cleanly (no “address already in use” errors).

**Step 3: Commit**

SKIP — user requested no git actions.
