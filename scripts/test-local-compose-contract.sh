#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import re

compose = Path("docker-compose.yml").read_text(encoding="utf-8")
legacy_compose = Path("docker-compose.local.yml").read_text(encoding="utf-8")
dockerfile = Path("Dockerfile.rust").read_text(encoding="utf-8")

assert "HEALTHCHECK" in dockerfile, "Rust image must define a healthcheck"
assert "wget -q -O /dev/null http://127.0.0.1:8080/health" in dockerfile, (
    "Rust image healthcheck must probe loopback /health"
)
assert "TRACERA_FRONTEND_DIST=/opt/tracera/frontend/dist" in dockerfile, (
    "Rust image must serve the approved rich dashboard"
)
assert "COPY --from=frontend-build /workspace/frontend/dist /opt/tracera/frontend/dist" in dockerfile, (
    "Rust image must contain the built rich dashboard"
)
server = re.search(r"(?ms)^  tracera-server:\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)", compose)
assert server and "depends_on:" in server.group(1), "server database dependency missing"
assert '"127.0.0.1:${TRACERA_LOCAL_PORT:-18000}:8080"' in server.group(1), (
    "rich dashboard gateway must be hard-bound to loopback :18000"
)
assert 'TRACERA_PUBLIC_BIND_MODE: "loopback-published"' in server.group(1), (
    "canonical gateway must declare its loopback-published deployment boundary"
)
assert "TRACERA_LOCAL_BIND_ADDR" not in server.group(1), (
    "canonical gateway must not allow an environment override to expose its host port"
)
assert "\n  frontend:" not in compose, "canonical stack must not publish a split frontend"
legacy_frontend = re.search(r"(?ms)^  frontend:\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)", legacy_compose)
assert legacy_frontend and "condition: service_healthy" in legacy_frontend.group(1), (
    "explicit legacy frontend must wait for a healthy server"
)
assert '"127.0.0.1:${TRACERA_LOCAL_PORT:-18081}:80"' in legacy_compose, (
    "legacy frontend publication must be hard-bound to loopback :18081"
)
assert 'TRACERA_PUBLIC_BIND_MODE: "private-network"' in legacy_compose, (
    "legacy backend must declare its private-network deployment boundary"
)
print("local Compose readiness contract: PASS")
PY
