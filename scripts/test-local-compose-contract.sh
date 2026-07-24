#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import re

compose = Path("docker-compose.local.yml").read_text(encoding="utf-8")
dockerfile = Path("Dockerfile.rust").read_text(encoding="utf-8")

assert "HEALTHCHECK" in dockerfile, "Rust image must define a healthcheck"
assert "wget -q -O /dev/null http://127.0.0.1:8080/health" in dockerfile, (
    "Rust image healthcheck must probe loopback /health"
)
server = re.search(r"(?ms)^  tracera-server:\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)", compose)
frontend = re.search(r"(?ms)^  frontend:\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)", compose)
assert server and "healthcheck:" in server.group(1), "server service healthcheck missing"
assert frontend and "condition: service_healthy" in frontend.group(1), (
    "frontend must wait for a healthy server"
)
assert '"${TRACERA_LOCAL_BIND_ADDR:-127.0.0.1}:${TRACERA_LOCAL_PORT:-18081}:80"' in compose, (
    "frontend publication must default to loopback"
)
print("local Compose readiness contract: PASS")
PY
