#!/usr/bin/env bash
set -euo pipefail

# Secret-free deployment gate.  CI runs the private mode; operators should run
# `--mode public` before attaching a public DNS name or tunnel.
mode="private"
if [[ "${1:-}" == "--mode" ]]; then
  mode="${2:?usage: $0 [--mode private|public]}"
fi
if [[ "$mode" != "private" && "$mode" != "public" ]]; then
  echo "error: mode must be private or public" >&2
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose="$root/deploy/selfhost/docker-compose.selfhost.yml"
caddy="$root/deploy/selfhost/Caddyfile"

fail() { echo "DEPLOYMENT SECURITY FAIL: $*" >&2; exit 1; }
grep -qE '^      TRACERA_BIND_ADDR: 0\.0\.0\.0:8080$' "$compose" \
  || fail "self-host server must bind only to the internal compose network"
if grep -qE '^      - "?[0-9]+:8080' "$compose"; then
  fail "tracera-server must not publish port 8080 directly"
fi
grep -qE '^\s*reverse_proxy tracera-server:8080$' "$caddy" \
  || fail "Caddy must be the only ingress to tracera-server"
grep -qE '^\s*header \{' "$caddy" \
  || fail "Caddy security headers block is missing"

# Public TLS must be reachable at the ingress boundary.  Keep this check
# independent of secrets so it can run in CI and before a tunnel is attached.
grep -qE '^      - "443:443"$' "$compose" \
  || fail "Caddy must publish HTTPS port 443 at the ingress boundary"

if [[ "$mode" == "public" ]]; then
  # A commented forward_auth example is not a control. Require an active
  # auth directive and TLS listener before public exposure is considered safe.
  grep -qE '^\s*(forward_auth|basic_auth|jwt)' "$caddy" \
    || fail "public mode requires an active Caddy auth directive (forward_auth/basic_auth/jwt)"
  grep -qE '^\S+\s*\{' "$caddy" \
    || fail "public mode requires an explicit Caddy site listener"
  grep -qE '^https://' "$caddy" || grep -qE '^\{\$[A-Z0-9_]+\}\s*\{' "$caddy" \
    || fail "public mode requires HTTPS (Caddy automatic TLS)"
fi

echo "deployment security gate passed (mode=$mode)"
