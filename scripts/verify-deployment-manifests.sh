#!/usr/bin/env bash
set -euo pipefail

# Static, secret-free deployment consistency gate. This intentionally does not
# contact registries or expand credentials; it catches drift before deployment.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() { printf 'deployment manifest check failed: %s\n' "$1" >&2; exit 1; }

command -v rg >/dev/null 2>&1 \
  || fail "ripgrep (rg) is required for secret scanning"

[[ -f Dockerfile.rust ]] || fail "Dockerfile.rust is missing"
grep -q 'dockerfile: Dockerfile.rust' docker-compose.yml \
  || fail "docker-compose.yml must build the Rust server from Dockerfile.rust"
! grep -qE '^[[:space:]]*-[[:space:]]*"?8080:8080' docker-compose.yml \
  || fail "backend port 8080 must remain internal"
! grep -qE '^[[:space:]]*-[[:space:]]*"?5432:5432' docker-compose.yml \
  || fail "postgres port 5432 must remain internal"

grep -q -- '--token' deploy/selfhost/docker-compose.selfhost.yml \
  || fail "self-host tunnel must pass a token to cloudflared"
grep -q 'CF_TUNNEL_TOKEN:?CF_TUNNEL_TOKEN is required' deploy/selfhost/docker-compose.selfhost.yml \
  || fail "self-host tunnel token must be required"
! grep -qE '^[[:space:]]*-[[:space:]]*"?8080:' deploy/selfhost/docker-compose.selfhost.yml \
  || fail "self-host backend port 8080 must not be published"

grep -q 'path: /ready' deploy/kubernetes/templates/tracera.yaml \
  || fail "Helm readiness probe must use the canonical /ready endpoint"
grep -q 'path: /health' deploy/kubernetes/templates/tracera.yaml \
  || fail "Helm liveness probe must use the canonical /health endpoint"

# Never allow a concrete database password in checked-in deployment material.
! rg -n 'POSTGRES_PASSWORD:[[:space:]]+tracera|postgres://[^:]+:tracera@' \
  docker-compose.yml deploy Dockerfile.rust >/dev/null \
  || fail "possible concrete database credential in deployment material"

# Keep the Helm chart's pod security invariants in the same pre-deploy gate.
"$ROOT_DIR/scripts/verify-kubernetes-security.sh" \
  || fail "Kubernetes security policy gate failed"

printf 'deployment manifest checks passed (secret-free static mode)\n'
