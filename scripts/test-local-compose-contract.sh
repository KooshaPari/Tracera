#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import json
import re

compose = Path("docker-compose.yml").read_text(encoding="utf-8")
legacy_compose = Path("docker-compose.local.yml").read_text(encoding="utf-8")
dockerfile = Path("Dockerfile.rust").read_text(encoding="utf-8")
frontend_package = json.loads(Path("frontend/package.json").read_text(encoding="utf-8"))

package_manager = frontend_package["packageManager"]
package_manager_name, package_manager_version = package_manager.split("@", 1)
assert package_manager_name == "bun", "frontend packageManager must declare Bun"
assert package_manager_version == "1.3.11", (
    "frontend packageManager must use the supported Bun 1.3.11 toolchain"
)
bun_image = re.search(r"^FROM oven/bun:([^\s]+)-alpine AS frontend-build$", dockerfile, re.M)
assert bun_image, "frontend build stage must use an explicit Bun Alpine image"
assert bun_image.group(1) == package_manager_version, (
    "frontend build Bun image must match frontend/package.json packageManager"
)
install_command = "RUN bun install --frozen-lockfile --ignore-scripts"
postinstall_command = "RUN bun run postinstall"
assert install_command in dockerfile, "frontend install must defer lifecycle scripts"
assert postinstall_command in dockerfile, "frontend install must run the declared postinstall explicitly"
assert dockerfile.index(install_command) < dockerfile.index(postinstall_command), (
    "frontend install must precede the explicit postinstall"
)
if frontend_package.get("scripts", {}).get("postinstall", "").startswith("bash "):
    bash_install = re.search(r"^RUN apk add --no-cache .*\bbash\b", dockerfile, re.M)
    assert bash_install, "frontend postinstall requires Bash in the Alpine build stage"
    assert dockerfile.index(bash_install.group(0)) < dockerfile.index(postinstall_command), (
        "frontend build must install Bash before postinstall"
    )

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
