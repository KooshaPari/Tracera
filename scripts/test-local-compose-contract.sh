#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import re

compose = Path("docker-compose.local.yml").read_text(encoding="utf-8")
dockerfile = Path("Dockerfile.rust").read_text(encoding="utf-8")
frontend_dockerfile = Path("frontend/Dockerfile.local").read_text(encoding="utf-8")
nginx = Path("frontend/deploy/nginx.local.conf").read_text(encoding="utf-8")
api_origin = Path("frontend/apps/web/src/config/api-origin.ts").read_text(encoding="utf-8")

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
assert "ENV VITE_API_URL=" in frontend_dockerfile, (
    "local frontend build must opt into the browser's same-origin API path"
)
assert "VITE_API_BASE" not in frontend_dockerfile, (
    "local frontend build must not set the unused VITE_API_BASE variable"
)
assert "window.location.origin" in api_origin, (
    "empty VITE_API_URL must resolve to the browser's current origin"
)
assert "proxy_pass http://tracera-server:8080" in nginx, (
    "local nginx must proxy API requests to the private Rust backend"
)

source_root = Path("frontend/apps/web/src")
loopback_fallbacks = []
for path in source_root.rglob("*"):
    if (
        path.suffix not in {".ts", ".tsx", ".js", ".jsx"}
        or "__tests__" in path.parts
        or "mocks" in path.parts
        or ".test." in path.name
    ):
        continue
    text = path.read_text(encoding="utf-8")
    if "127.0.0.1:18000" in text or "localhost:4000" in text or ":18000" in text:
        loopback_fallbacks.append(str(path))
assert not loopback_fallbacks, (
    "browser client must not fall back to an unpublished loopback backend: "
    + ", ".join(loopback_fallbacks)
)
print("local Compose readiness contract: PASS")
PY
